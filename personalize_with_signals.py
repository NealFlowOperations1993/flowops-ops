#!/usr/bin/env python3
"""
Signal-Led Personalization — Day 5 wiring.

Per lead:
  1. signal_enricher.enrich() → public-records signals (Form D, news, tech stack, LinkedIn)
  2. Council Mini best_opener(lead_ctx + signals) → 3 persona candidates → judge picks winner
  3. Write winning opener + signal data to Smartlead custom_fields

Cost per lead: ~$0.0016 (3 Gemini Flash + 1 Sonnet judge) + ~$0.001 Apify (if news fires)
Total at 400/day: ~$1/day. Within $50/day cap easily.

Use this for NEW leads only — existing leads keep their single-shot openers
to preserve variant comparison data.
"""
import json
import os
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set up paths
sys.path.insert(0, os.path.dirname(__file__))

from spend_guard import check_spend_or_die
from council_mini import best_opener
from core.signal_enricher import enrich

SL_KEY = os.environ["SMARTLEAD_API_KEY"]
SL = "https://server.smartlead.ai/api/v1"
UA = "Mozilla/5.0"

# Niche → label map for cleaner prompts to Council
NICHE_LABELS = {
    "WEALTH": "wealth management firm",
    "FINANCIAL": "financial advisor",
    "MORTGAGE": "mortgage broker",
    "INSURANCE": "insurance agency",
    "MEDSPA": "med spa",
    "PI_LAW": "personal injury law firm",
    "MCA": "merchant cash advance broker",
    "COMMLOAN": "commercial loan broker",
}

CAMPAIGNS = {v: k for k, v in {
    "WEALTH":3263730,"FINANCIAL":3191292,"MORTGAGE":3191290,
    "INSURANCE":3191291,"MEDSPA":3191285,"PI_LAW":3327115,
    "MCA":3263732,"COMMLOAN":3263731}.items()}


def get_new_leads(cid, limit=50):
    """Pull leads that have NO personalized_opener AND no signal_enriched_at."""
    leads = []
    offset = 0
    while len(leads) < limit:
        url = f"{SL}/campaigns/{cid}/leads?limit=100&offset={offset}&api_key={SL_KEY}"
        try:
            r = urllib.request.Request(url, headers={"User-Agent":UA})
            d = json.loads(urllib.request.urlopen(r, timeout=30).read())
        except Exception:
            break
        items = d.get("data", [])
        if not items: break
        for it in items:
            inner = it.get("lead") if isinstance(it.get("lead"), dict) else it
            cf = inner.get("custom_fields") or {}
            if isinstance(cf, str):
                try: cf = json.loads(cf)
                except: cf = {}
            # Skip already-personalized leads
            if cf.get("signal_enriched_at"): continue
            if cf.get("personalized_opener") and cf.get("personalized_opener_2"):
                continue
            email = (inner.get("email") or "").lower()
            if not email or "@" not in email: continue
            leads.append({
                "lead_id":   inner.get("id") or it.get("id"),
                "email":     email,
                "first_name": inner.get("first_name") or "",
                "last_name":  inner.get("last_name") or "",
                "company":   inner.get("company_name") or "",
                "website":   inner.get("website") or "",
                "city":      cf.get("city",""),
                "state":     cf.get("state",""),
                "existing_cf": cf,
            })
            if len(leads) >= limit: break
        if len(items) < 100: break
        offset += 100
    return leads


def patch_lead(cid, lead_id, email, custom_fields):
    url = f"{SL}/campaigns/{cid}/leads/{lead_id}?api_key={SL_KEY}"
    body = {"email": email, "custom_fields": custom_fields}
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
        headers={"Content-Type":"application/json","User-Agent":UA}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status
    except Exception:
        return 0


def process(lead, niche):
    # Step 1: enrich with public signals
    signals = enrich({
        "first_name": lead["first_name"],
        "company_name": lead["company"],
        "website": lead["website"],
        "city": lead["city"],
        "state": lead["state"],
        "niche": niche,
    })

    # Step 2: feed lead context + signals into Council Mini
    lead_ctx = {
        "first_name": lead["first_name"],
        "company": lead["company"],
        "city": lead["city"],
        "state": lead["state"],
        "niche": NICHE_LABELS.get(niche, niche.lower()),
        "signals": signals,
    }
    council = best_opener(lead_ctx)
    opener = council.get("opener","")
    if not opener:
        return {"ok": False, "email": lead["email"], "err": "council_failed"}

    # Step 3: write back to Smartlead with signal metadata
    new_cf = dict(lead["existing_cf"])
    new_cf["personalized_opener"]   = opener
    new_cf["opener_persona_winner"] = council.get("winner_id","")
    new_cf["signal_enriched_at"]    = __import__("datetime").datetime.now().isoformat()
    new_cf["signals_summary"]       = " | ".join(f"{k}: {v[:80]}" for k,v in signals.items())[:500]

    status = patch_lead(CAMPAIGNS_BY_NAME.get(niche, 0), lead["lead_id"], lead["email"], new_cf)
    return {"ok": status in (200,204), "email": lead["email"], "status": status,
            "winner": council.get("winner_id"), "signals_count": len(signals)}


CAMPAIGNS_BY_NAME = {
    "WEALTH":3263730,"FINANCIAL":3191292,"MORTGAGE":3191290,
    "INSURANCE":3191291,"MEDSPA":3191285,"PI_LAW":3327115,
    "MCA":3263732,"COMMLOAN":3263731,
}


def main():
    # Spend guard — estimate $0.002/lead × max 100 = $0.20 per niche × 8 niches = $1.60
    check_spend_or_die(estimated_cost_usd=2.00, script_name="personalize_with_signals.py")

    jobs = []
    for niche, cid in CAMPAIGNS_BY_NAME.items():
        leads = get_new_leads(cid, limit=50)
        if leads:
            print(f"[{niche}] {len(leads)} new leads to enrich+personalize", flush=True)
            for l in leads:
                jobs.append((l, niche))

    if not jobs:
        print("No new leads to process (all already have signal-enriched openers).")
        return

    print(f"\nTotal: {len(jobs)} leads (4 parallel workers)\n", flush=True)

    ok = err = 0
    persona_wins = {"ANALYST":0,"FOUNDER_PEER":0,"DIRECT":0,"NONE":0}
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(process, l, n): (l,n) for l,n in jobs}
        for i, fut in enumerate(as_completed(futs), 1):
            r = fut.result()
            if r["ok"]:
                ok += 1
                persona_wins[r.get("winner","NONE")] = persona_wins.get(r.get("winner","NONE"),0) + 1
            else:
                err += 1
            if i % 10 == 0 or i == len(jobs):
                print(f"  [{i}/{len(jobs)}] ok={ok} err={err}", flush=True)

    print(f"\nDONE ok={ok} err={err}")
    print(f"PERSONA WINS: {persona_wins}")


if __name__ == "__main__":
    main()
