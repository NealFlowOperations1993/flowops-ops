#!/usr/bin/env python3
"""
Bypass n8n. Personalize locally via Council (Gemini Flash) + push direct to Smartlead.

Usage:
  python3 direct_ingest.py --csv "/path/to/leads.csv" --niche WEALTH --campaign-id 3263730 --limit 2063
"""
import argparse
import csv
import json
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from core import council, llm, signal_enricher
import os

SL_KEY = os.environ["SMARTLEAD_API_KEY"]
SL_BASE = "https://server.smartlead.ai/api/v1"
UA = "Mozilla/5.0"


def smartlead_add_lead(cid: int, lead_data: dict) -> tuple[bool, str]:
    """POST a single lead with custom fields populated."""
    url = f"{SL_BASE}/campaigns/{cid}/leads?api_key={SL_KEY}"
    body = json.dumps({"lead_list": [lead_data]}).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/json",
        "User-Agent":   UA,
        "Accept":       "application/json",
    }, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return True, r.read().decode()[:200]
    except Exception as e:
        try:
            err = e.read().decode()[:200]
        except Exception:
            err = str(e)
        return False, err


def process_lead(lead: dict, niche: str, cid: int, niche_context: dict | None = None) -> dict:
    """Council personalize + push to Smartlead. Returns log dict."""
    t0 = time.time()
    try:
        result = council.generate(lead, niche_context, debug=False)
        final = result.get("final", {})
    except Exception as e:
        return {"email": lead.get("email"), "_error": f"council_fail: {e}"}

    # Build Smartlead lead payload with custom_fields populated
    # CRITICAL: Map Council's email1_* keys to the Smartlead template's personalized_* keys
    # Also escape $ to &#36; (HTML entity) to avoid Smartlead's SQL parameter-binding bug
    def esc(s):
        return (s or "").replace("$", "&#36;")
    cf = {
        "city":  lead.get("city",""),
        "state": lead.get("state",""),
        "title": lead.get("category","") or lead.get("title",""),
        "niche": niche,
        "source": "direct_ingest_2026-05-12",
        # Map Council 9-key output → Smartlead template variables (with $ escaped)
        "personalized_opener":   esc(final.get("email1_opener", "")),
        "personalized_pain":     esc(final.get("email1_pain", "")),
        "personalized_cta":      esc(final.get("email1_cta", "")),
        "personalized_opener_2": esc(final.get("email2_opener", "")),
        "personalized_pain_2":   esc(final.get("email2_pain", "")),
        "personalized_cta_2":    esc(final.get("email2_cta", "")),
        "personalized_opener_3": esc(final.get("email3_opener", "")),
        "personalized_pain_3":   esc(final.get("email3_pain", "")),
        "personalized_cta_3":    esc(final.get("email3_cta", "")),
    }

    sl_payload = {
        "first_name":    lead.get("first_name",""),
        "last_name":     lead.get("last_name",""),
        "email":         lead.get("email",""),
        "company_name":  lead.get("company_name",""),
        "website":       lead.get("website",""),
        "phone_number":  lead.get("phone_number",""),
        "location":      f"{lead.get('city','')}, {lead.get('state','')}".strip(", "),
        "custom_fields": cf,
    }

    ok, msg = smartlead_add_lead(cid, sl_payload)
    elapsed = time.time() - t0
    return {
        "email":   lead.get("email"),
        "ok":      ok,
        "msg":     msg,
        "cost":    result.get("cost_usd", 0),
        "latency": round(elapsed, 1),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True)
    p.add_argument("--niche", required=True)
    p.add_argument("--campaign-id", type=int, required=True)
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--workers", type=int, default=10)
    p.add_argument("--offset", type=int, default=0, help="skip first N rows")
    args = p.parse_args()

    # Apollo-style column names from the CSV
    # Convert each CSV row to council's expected lead dict shape
    leads = []
    with open(args.csv) as f:
        reader = csv.DictReader(f)
        for i, r in enumerate(reader):
            if args.offset and i < args.offset:
                continue
            email = (r.get("Email") or r.get("email") or "").strip().lower()
            if not email or "@" not in email:
                continue
            leads.append({
                "first_name":   r.get("First Name","") or r.get("first_name",""),
                "last_name":    r.get("Last Name","")  or r.get("last_name",""),
                "email":        email,
                "company_name": r.get("Company","")    or r.get("company_name",""),
                "website":      r.get("Website","")   or r.get("website",""),
                "city":         (r.get("Location","") or r.get("city","")).split(",")[0].strip(),
                "state":        r.get("State","")    or r.get("state",""),
                "category":     r.get("Title","")    or r.get("title",""),
                "phone_number": r.get("Phone","")    or r.get("phone_number",""),
                "niche":        args.niche,
                "linkedin":     r.get("LinkedIn URL","") or r.get("linkedin",""),
            })
            if args.limit and len(leads) >= args.limit:
                break

    print(f"Processing {len(leads)} leads → {args.niche} (campaign {args.campaign_id})")
    print(f"Workers: {args.workers} · Model: Gemini Flash · ETA: ~{len(leads)//args.workers}s")
    print()

    t0 = time.time()
    ok = 0
    err = 0
    total_cost = 0.0

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(process_lead, l, args.niche, args.campaign_id): l for l in leads}
        for i, fut in enumerate(as_completed(futs)):
            r = fut.result()
            total_cost += r.get("cost", 0)
            if r.get("ok"):
                ok += 1
            else:
                err += 1
                if err < 5:
                    print(f"  [err {err}] {r.get('email')}: {r.get('msg', r.get('_error',''))[:100]}")
            if (i + 1) % 50 == 0:
                elapsed = time.time() - t0
                rate = (i+1) / elapsed
                eta_remain = (len(leads) - i - 1) / rate if rate else 0
                print(f"  [{i+1}/{len(leads)}] ok={ok} err={err} cost=${total_cost:.2f} rate={rate:.1f}/s eta={eta_remain:.0f}s")

    elapsed = time.time() - t0
    print()
    print(f"DONE in {elapsed:.0f}s")
    print(f"  Pushed: {ok}/{len(leads)}")
    print(f"  Errors: {err}")
    print(f"  Total cost: ${total_cost:.3f}")


if __name__ == "__main__":
    main()
