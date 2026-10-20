#!/usr/bin/env python3
"""
Pre-generate Gemini 3 Pro Image mockups for leads scheduled to receive Variant C tomorrow.

Logic:
- Pull top 30 leads per active niche (likely to send tomorrow)
- For each lead with a website + no existing mockup, generate via Gemini Image
- Save PNG to ~/Desktop/intakebot/public/mockups/<slug>.png
- Patch Smartlead custom_field remake_image_url

Run:
  python3 mockup_batch_run.py
"""
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, '/Users/nealthakkar/Desktop/council')
from core.website_redo import scrape_site, generate_redesign_image

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
MOCKUP_DIR = Path.home() / "Desktop" / "intakebot" / "public" / "mockups"
MOCKUP_DIR.mkdir(parents=True, exist_ok=True)
CDN_BASE = "https://flowops-assets.vercel.app/mockups"
PER_NICHE = 20  # 6 niches × 20 = 120 mockups max — only the NEXT-DAY queue
# Cost @ Gemini 3.1 Flash Image: ~$0.005-0.01 per mockup → ~$0.60-1.20/night max
# Spend guard enforced at top of main()


def G(p):
    sep = "&" if "?" in p else "?"
    r = urllib.request.Request(f"{BASE}{p}{sep}api_key={KEY}", headers={"User-Agent": UA})
    with urllib.request.urlopen(r, timeout=30) as resp:
        return json.loads(resp.read().decode())


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


def process(lead_entry, cid, niche):
    lead = lead_entry.get("lead", lead_entry)
    cf = lead.get("custom_fields") or {}
    website = lead.get("website", "") or ""
    company = lead.get("company_name", "")
    email = lead.get("email")
    lead_id = lead.get("id")

    # Skip if no website or already has mockup
    if not website or "@" in website:
        return {"skipped": "no_website", "email": email}
    if cf.get("remake_image_url") and not cf.get("remake_image_url","").endswith("/.png"):
        return {"skipped": "exists", "email": email}

    url = website if website.startswith("http") else f"https://{website}"
    try:
        scraped = scrape_site(url)
        if scraped.get("error"):
            return {"error": f"scrape: {scraped['error']}", "email": email}
        slug = re.sub(r"[^a-z0-9]+", "_", email.split("@")[0].lower())[:40]
        out_path = str(MOCKUP_DIR / f"{slug}.png")
        png = generate_redesign_image(scraped, niche, company_name=company, out_path=out_path)
        if not png:
            return {"error": "gemini empty", "email": email}
        cdn_url = f"{CDN_BASE}/{slug}.png"
        # Patch Smartlead
        new_cf = dict(cf)
        new_cf["remake_image_url"] = cdn_url
        ok = patch_lead(cid, lead_id, email, new_cf)
        return {"ok": ok, "email": email, "url": cdn_url, "png": png}
    except Exception as e:
        return {"error": str(e), "email": email}


def main():
    # Spend guard FIRST — block if today's spend + this run would exceed $50/day cap
    from spend_guard import check_spend_or_die
    estimated = 6 * PER_NICHE * 0.01   # max ~120 mockups @ $0.01 each = $1.20
    check_spend_or_die(estimated_cost_usd=estimated, script_name="mockup_batch_run.py")
    print(f"Pre-generating Variant C mockups for tomorrow's queue\n")
    all_leads = []
    for niche, cid in CAMPAIGNS.items():
        try:
            d = G(f"/campaigns/{cid}/leads?limit={PER_NICHE}&offset=0")
            batch = d.get("data", [])
        except Exception as e:
            print(f"  {niche}: skip (fetch err)")
            continue
        for entry in batch[:PER_NICHE]:
            all_leads.append((entry, cid, niche))
        print(f"  Queued {min(len(batch), PER_NICHE)} leads from {niche}")
    print(f"\nTotal queue: {len(all_leads)} mockups")
    print(f"Estimated cost: ${len(all_leads) * 0.06:.2f}  Estimated time: ~{len(all_leads) * 25 / 3 / 60:.1f}min with 3 workers\n")

    ok = err = skip = 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = [ex.submit(process, *args) for args in all_leads]
        for i, fut in enumerate(as_completed(futs)):
            r = fut.result()
            if r.get("ok"):
                ok += 1
                print(f"  [{i+1}/{len(all_leads)}] ✓ {r['email']} → {r['url'][:80]}")
            elif r.get("skipped"):
                skip += 1
            else:
                err += 1
                print(f"  [{i+1}/{len(all_leads)}] ✗ {r['email']}: {r.get('error','')[:80]}")
    print(f"\nDONE in {time.time()-t0:.0f}s | ok={ok} err={err} skip={skip}")
    print(f"Mockups in: {MOCKUP_DIR}/")
    print(f"⚠ Push intakebot/public/mockups to Vercel to make URLs live")


if __name__ == "__main__":
    main()
