#!/usr/bin/env python3
"""
Morning launch QA. Run this when you wake up to see what's ready to fire.

Usage:
  cd ~/Desktop/council && python3 morning_check.py
"""
import json
import urllib.request
from collections import defaultdict
import os

KEY = os.environ["SMARTLEAD_API_KEY"]
BASE = "https://server.smartlead.ai/api/v1"
UA = "Mozilla/5.0"
GHL = "https://api.leadconnectorhq.com/widget/bookings/flowqualificationcall"

CAMPAIGNS = {
    "MCA":          3263732,
    "WEALTH":       3263730,
    "COMMLOAN":     3263731,
    "FINANCIAL":    3191292,
    "MORTGAGE":     3191290,
    "INSURANCE":    3191291,
    "AGENCY":       3191288,
    "RECRUITER":    3191293,
    "COACH_BIZ":    3191287,
    "COACH_FIT":    3191285,
    "TAX_RES":      3292969,
    "IT_MSP":       3292970,
}


def G(p):
    sep = "&" if "?" in p else "?"
    r = urllib.request.Request(f"{BASE}{p}{sep}api_key={KEY}", headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(r, timeout=30) as resp:
        return json.loads(resp.read().decode())


def main():
    print("\n=== MORNING LAUNCH CHECK ===\n")

    rows = []
    for niche, cid in CAMPAIGNS.items():
        try:
            a = G(f"/campaigns/{cid}/analytics")
            status = a.get("status", "?")
        except Exception:
            status = "ERR"
        try:
            L = G(f"/campaigns/{cid}/leads?limit=3&offset=0")
            t = L.get("total_leads", 0)
            total = int(t) if str(t).isdigit() else 0
            leads_sample = L.get("data", [])
        except Exception:
            total = 0
            leads_sample = []
        try:
            S = G(f"/campaigns/{cid}/sequences")
            has_link = False
            personalized_in_template = False
            for s in S:
                for v in (s.get("sequence_variants") or []):
                    body = v.get("email_body", "") or ""
                    if "leadconnectorhq" in body:
                        has_link = True
                    if "personalized_opener" in body:
                        personalized_in_template = True
        except Exception:
            has_link = False
            personalized_in_template = False

        # Check personalization quality on one lead
        has_perso = False
        if leads_sample:
            cf = (leads_sample[0].get("lead", leads_sample[0]).get("custom_fields") or {})
            has_perso = bool(cf.get("personalized_opener"))

        rows.append({
            "niche": niche,
            "status": status,
            "total_leads": total,
            "has_link": has_link,
            "has_personalized_template": personalized_in_template,
            "first_lead_has_perso": has_perso,
        })

    # Print table
    print(f"{'NICHE':<12}{'STATUS':<10}{'LEADS':>7}{'LINK':>6}{'TEMPL':>7}{'PERSO':>7}  READY?")
    print("-" * 70)
    for r in rows:
        ready = "✓" if (r["status"] == "ACTIVE" and r["total_leads"] > 0 and r["has_link"] and r["has_personalized_template"]) else "—"
        if r["status"] == "ACTIVE" and r["total_leads"] > 0 and not r["first_lead_has_perso"]:
            ready = "⚠ NO PERSO"
        print(f"{r['niche']:<12}{r['status'][:8]:<10}{r['total_leads']:>7}{'✓' if r['has_link'] else 'X':>6}{'✓' if r['has_personalized_template'] else 'X':>7}{'✓' if r['first_lead_has_perso'] else '—':>7}  {ready}")

    # Recommendations
    print("\nNEXT ACTIONS:")
    for r in rows:
        if r["status"] == "PAUSED" and r["total_leads"] >= 50 and r["has_link"]:
            print(f"  • {r['niche']}: PAUSED with {r['total_leads']} leads + booking link ready. Unpause to add ~{min(r['total_leads'], 300)}/day sending capacity.")
        if r["status"] == "ACTIVE" and r["total_leads"] > 0 and not r["first_lead_has_perso"]:
            print(f"  • {r['niche']}: ⚠️ {r['total_leads']} leads have empty personalized_opener. Run repair_keys.py before unpausing.")

    print("\nNote: ⚠ NO PERSO means leads exist but custom_fields.personalized_opener is empty.")
    print("      Run /tmp/repair_keys.py to fix (copies email1_* → personalized_* with $-escape).\n")


if __name__ == "__main__":
    main()
