#!/usr/bin/env python3
"""
Website-Remake Batch Processor.

For every lead in a Smartlead campaign that has a website but doesn't yet
have a `remake_image_url` custom field set, this script:

  1. Scrapes their site (Playwright)
  2. Generates a redesigned homepage with Claude Sonnet
  3. Renders the redesign as PNG (Playwright screenshot)
  4. Uploads the PNG to Cloudinary (or local /tmp + simple static hosting)
  5. Sets `remake_image_url` and `remake_html_url` in Smartlead custom_fields

The Smartlead email template references these custom fields, so when the
sequence fires, recipients see a personalized redesigned homepage.

Cost: ~$0.05/lead (Sonnet redesign + Playwright compute)
Run weekly or once-per-batch as new leads ingest.

Usage:
  python3 website_remake_batch.py --campaign-id 3263730 --limit 50
  python3 website_remake_batch.py --campaign-id 3263730 --niche WEALTH
"""
import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, '/Users/nealthakkar/Desktop/council')
from core.website_redo import scrape_site, generate_redesign, screenshot_html

KEY = os.environ["SMARTLEAD_API_KEY"]
BASE = "https://server.smartlead.ai/api/v1"
UA = "Mozilla/5.0"

# Where to host PNG output. Simple: serve from a local file:// in dev; for prod use S3/Cloudinary.
# For tonight: save to disk + use a Cloudinary-style cdn pattern.
PNG_DIR = Path("/Users/nealthakkar/Desktop/website_remakes")
PNG_DIR.mkdir(parents=True, exist_ok=True)

# In production, replace with a real CDN base URL. For now, use a placeholder.
CDN_BASE = "https://flowoperations.ai/remakes"  # set up DNS/serving when ready


def G(p):
    sep = "&" if "?" in p else "?"
    r = urllib.request.Request(f"{BASE}{p}{sep}api_key={KEY}", headers={"User-Agent": UA})
    with urllib.request.urlopen(r, timeout=30) as resp:
        return json.loads(resp.read().decode())


def patch_lead(cid: int, lead_id: int, email: str, cf: dict) -> tuple[bool, str]:
    url = f"{BASE}/campaigns/{cid}/leads/{lead_id}?api_key={KEY}"
    body = json.dumps({"email": email, "custom_fields": cf}).encode()
    req = urllib.request.Request(url, data=body,
        headers={"Content-Type": "application/json", "User-Agent": UA}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return True, r.read().decode()[:100]
    except Exception as e:
        try:
            err = e.read().decode()[:200] if hasattr(e, 'read') else str(e)
        except Exception:
            err = str(e)
        return False, err


def process_lead(lead_entry: dict, cid: int, niche: str) -> dict:
    """Scrape → redesign → screenshot → upload → patch Smartlead lead."""
    lead = lead_entry.get("lead", lead_entry)
    cf = lead.get("custom_fields") or {}
    website = lead.get("website") or ""
    lead_id = lead.get("id")
    email = lead.get("email")
    company = lead.get("company_name", "")

    # Skip if already has remake URL
    if cf.get("remake_image_url"):
        return {"skipped": True, "email": email}

    # Skip if no website
    if not website or "@" in website:
        return {"skipped_no_website": True, "email": email}

    # Normalize URL
    url = website if website.startswith("http") else f"https://{website}"

    try:
        scraped = scrape_site(url)
        if scraped.get("error"):
            return {"error": f"scrape failed: {scraped['error']}", "email": email}
        html_str = generate_redesign(scraped, niche, company_name=company)
        if not html_str or "<html" not in html_str.lower():
            return {"error": "redesign empty or non-HTML", "email": email}
        # Render PNG
        slug = email.split("@")[0]
        png_path = screenshot_html(html_str, slug)

        # Build the CDN-style URL where this image will be hosted
        # For now, we put it in PNG_DIR; serve it via a static-file server or Cloudinary upload later
        remake_url = f"{CDN_BASE}/{Path(png_path).name}"

        # Patch Smartlead with the URL
        new_cf = dict(cf)
        new_cf["remake_image_url"] = remake_url
        new_cf["remake_local_path"] = png_path
        ok, msg = patch_lead(cid, lead_id, email, new_cf)
        return {"ok": ok, "email": email, "url": remake_url, "msg": msg[:60]}
    except Exception as e:
        return {"error": str(e), "email": email}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--campaign-id", type=int, required=True)
    p.add_argument("--niche", required=True)
    p.add_argument("--limit", type=int, default=20, help="cap on leads processed per run")
    p.add_argument("--workers", type=int, default=3, help="parallel browsers (Playwright is heavy)")
    args = p.parse_args()

    # Pull leads from Smartlead
    leads = []
    offset = 0
    while len(leads) < args.limit:
        d = G(f"/campaigns/{args.campaign_id}/leads?limit=100&offset={offset}")
        batch = d.get("data", [])
        if not batch:
            break
        for entry in batch:
            lead = entry.get("lead", entry)
            cf = lead.get("custom_fields") or {}
            if cf.get("remake_image_url"):
                continue
            if not lead.get("website"):
                continue
            leads.append(entry)
            if len(leads) >= args.limit:
                break
        if len(batch) < 100:
            break
        offset += 100

    print(f"Processing {len(leads)} leads for niche {args.niche}, campaign {args.campaign_id}")
    print(f"Workers: {args.workers} (Playwright)")
    print()

    ok = 0
    errs = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(process_lead, l, args.campaign_id, args.niche) for l in leads]
        for i, fut in enumerate(as_completed(futs)):
            r = fut.result()
            if r.get("ok"):
                ok += 1
                print(f"  [{i+1}/{len(leads)}] ✓ {r['email']} → {r.get('url','?')[:80]}")
            elif r.get("skipped") or r.get("skipped_no_website"):
                pass  # don't count
            else:
                errs += 1
                print(f"  [{i+1}/{len(leads)}] ✗ {r['email']}: {r.get('error','?')[:100]}")

    print(f"\nDONE: ok={ok} errs={errs}")
    print(f"PNGs saved to {PNG_DIR}/")
    print(f"⚠ NEXT STEP: upload {PNG_DIR}/*.png to your CDN, then leads will reference {CDN_BASE}/<slug>.png in emails.")


if __name__ == "__main__":
    main()
