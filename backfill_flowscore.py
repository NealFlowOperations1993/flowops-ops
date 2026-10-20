#!/usr/bin/env python3
"""
import os
Backfill FlowScore fields on existing Smartlead leads.

Variant B can't fire correctly without these 4 custom_fields populated:
  - personalized_flowscore
  - flowscore_meaning
  - flowscore_leak
  - flowscore_weak

This script:
1. Pulls all leads from active campaigns
2. For each lead with a website + missing flowscore, hits the FlowScore API
3. Writes the 4 fields to Smartlead

Cost: $0 (FlowScore is your own product)
Time: ~3-5 sec per lead with 10 workers
Spend guard: enforced (estimated $0 since FlowScore API is free, OpenRouter not used)

Usage:
  python3 backfill_flowscore.py                # backfill ALL active campaigns, all leads
  python3 backfill_flowscore.py --niche WEALTH # one niche only
  python3 backfill_flowscore.py --limit 200    # cap per niche
"""
import argparse
import json
import sys
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, '/Users/nealthakkar/Desktop/council')
from core.flowscore import score, extract_for_email
from spend_guard import check_spend_or_die

KEY = os.environ["SMARTLEAD_API_KEY"]
BASE = "https://server.smartlead.ai/api/v1"
UA = "Mozilla/5.0"

CAMPAIGNS = {
    "WEALTH":    3263730,
    "FINANCIAL": 3191292,
    "MORTGAGE":  3191290,
    "INSURANCE": 3191291,
    "MEDSPA":    3191285,
    "PI_LAW":    3327115,
}


def G(p):
    sep = "&" if "?" in p else "?"
    r = urllib.request.Request(f"{BASE}{p}{sep}api_key={KEY}", headers={"User-Agent": UA})
    return json.loads(urllib.request.urlopen(r, timeout=30).read())


def patch_lead(cid, lead_id, email, cf):
    url = f"{BASE}/campaigns/{cid}/leads/{lead_id}?api_key={KEY}"
    body = json.dumps({"email": email, "custom_fields": cf}).encode()
    req = urllib.request.Request(url, data=body,
        headers={"Content-Type": "application/json", "User-Agent": UA}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return True
    except Exception:
        return False


def process_one(lead_entry, cid, niche):
    lead = lead_entry.get("lead", lead_entry)
    cf = lead.get("custom_fields") or {}
    website = lead.get("website", "") or ""
    email = lead.get("email")
    lead_id = lead.get("id")

    # Skip if no website
    if not website or "@" in website:
        return {"skipped": "no_website", "email": email}

    # Skip if already populated
    if cf.get("personalized_flowscore"):
        return {"skipped": "exists", "email": email}

    # Hit FlowScore API
    raw = score(website, niche)
    if raw.get("error"):
        return {"error": raw.get("error"), "email": email}

    extracted = extract_for_email(raw)
    if not extracted.get("flowscore"):
        return {"error": "empty_score", "email": email}

    # Patch Smartlead
    new_cf = dict(cf)
    new_cf.update({
        "personalized_flowscore": extracted["flowscore"],
        "flowscore_meaning":      extracted["flowscore_meaning"],
        "flowscore_leak":         extracted["flowscore_leak"],
        "flowscore_weak":         extracted["flowscore_weak"],
    })
    ok = patch_lead(cid, lead_id, email, new_cf)
    return {"ok": ok, "email": email, "score": extracted["flowscore"]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--niche", default=None, help="Single niche only")
    parser.add_argument("--limit", type=int, default=1000, help="Max leads per niche")
    parser.add_argument("--workers", type=int, default=10)
    args = parser.parse_args()

    # FlowScore is free, no OpenRouter spend — but still respect the cap
    check_spend_or_die(estimated_cost_usd=0.0, script_name="backfill_flowscore.py")

    niches = {args.niche: CAMPAIGNS[args.niche]} if args.niche else CAMPAIGNS

    all_jobs = []
    for niche, cid in niches.items():
        offset = 0
        count = 0
        while count < args.limit:
            try:
                d = G(f"/campaigns/{cid}/leads?limit=100&offset={offset}")
                rows = d.get("data", [])
            except Exception:
                break
            if not rows:
                break
            for entry in rows:
                if count >= args.limit: break
                all_jobs.append((entry, cid, niche))
                count += 1
            if len(rows) < 100: break
            offset += 100
        print(f"  Queued {count} from {niche}")

    print(f"\nTotal to process: {len(all_jobs)}")
    print(f"Estimated time @ {args.workers} workers: ~{len(all_jobs)*10/args.workers/60:.1f} min")
    print()

    ok = err = skip = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(process_one, *args_) for args_ in all_jobs]
        for i, fut in enumerate(as_completed(futs)):
            r = fut.result()
            if r.get("ok"):
                ok += 1
                if ok % 25 == 0:
                    print(f"  [{i+1}/{len(all_jobs)}] ok={ok} skip={skip} err={err}")
            elif r.get("skipped"):
                skip += 1
            else:
                err += 1
                if err <= 5:
                    print(f"  ✗ {r.get('email')}: {r.get('error','')[:80]}")

    print(f"\nDONE | ok={ok} skip={skip} err={err}")


if __name__ == "__main__":
    main()
