#!/usr/bin/env python3
"""
Bulk-import leads from Acquisity (or any CSV source) into the FlowOps cold email pipeline.

Usage:
  python3 bulk_import.py path/to/leads.csv --niche FINANCIAL
  python3 bulk_import.py ~/Desktop/acquisity_dump_2026-05-06.csv --niche MORTGAGE --dry-run

What it does:
  1. Reads the CSV (auto-detects common column names: email, first_name, etc.)
  2. Normalizes to the pipeline's expected schema
  3. Dedupes against Brutus contacts table (skips already-imported emails)
  4. Posts to the Lead Gen Pipeline webhook in batches of 100
  5. Reports: imported / deduped / errors

Niches available:
  FINANCIAL, WEALTH, MORTGAGE, COMMERCIAL_LOAN, FUNDING, MCA,
  AGENCY, MEDSPA, PI_LAW, BIZ_LAW
"""
import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

WEBHOOK = "https://exaltisgroup.app.n8n.cloud/webhook/apify-lead-pipeline"
SUPABASE_URL = "https://uuhnhybmdsyzppiuhlvk.supabase.co"
SUPABASE_JWT = os.environ["SUPABASE_SERVICE_KEY"]
UA = "Mozilla/5.0"

VALID_NICHES = {
    "FINANCIAL", "WEALTH", "MORTGAGE", "COMMERCIAL_LOAN", "FUNDING", "MCA",
    "AGENCY", "MEDSPA", "PI_LAW", "BIZ_LAW",
}

# Common column-name variants we'll auto-map
EMAIL_FIELDS       = ["email", "Email", "EMAIL", "email_address", "EmailAddress", "primary_email", "work_email"]
FIRST_NAME_FIELDS  = ["first_name", "First Name", "firstName", "FirstName", "fname", "given_name"]
LAST_NAME_FIELDS   = ["last_name", "Last Name", "lastName", "LastName", "lname", "family_name", "surname"]
COMPANY_FIELDS     = ["company_name", "Company", "company", "CompanyName", "organization", "business_name", "Business"]
WEBSITE_FIELDS     = ["website", "Website", "domain", "Domain", "url", "URL", "website_url"]
PHONE_FIELDS       = ["phone", "Phone", "phone_number", "PhoneNumber", "mobile", "telephone", "Phone Number"]
CITY_FIELDS        = ["city", "City", "CITY", "town"]
STATE_FIELDS       = ["state", "State", "STATE", "region", "province"]
TITLE_FIELDS       = ["title", "Title", "job_title", "JobTitle", "position", "role"]
LINKEDIN_FIELDS    = ["linkedin", "LinkedIn", "linkedin_url", "LinkedInUrl", "linkedin_profile"]


def first_match(row: dict, candidates: list[str]) -> str:
    for c in candidates:
        if c in row and (row[c] or "").strip():
            return row[c].strip()
    return ""


def normalize_row(row: dict, niche: str) -> dict | None:
    email = first_match(row, EMAIL_FIELDS).lower()
    if not email or "@" not in email:
        return None
    return {
        "email":         email,
        "first_name":    first_match(row, FIRST_NAME_FIELDS),
        "last_name":     first_match(row, LAST_NAME_FIELDS),
        "company_name":  first_match(row, COMPANY_FIELDS),
        "website":       first_match(row, WEBSITE_FIELDS),
        "phone_number":  first_match(row, PHONE_FIELDS),
        "city":          first_match(row, CITY_FIELDS),
        "state":         first_match(row, STATE_FIELDS),
        "category":      first_match(row, TITLE_FIELDS) or "",
        "linkedin":      first_match(row, LINKEDIN_FIELDS),
        "niche":         niche,
        "source":        "acquisity_bulk_import",
    }


def get_existing_brutus_emails() -> set[str]:
    """Pull all email_normalized values from Brutus contacts. Used for dedup."""
    print("Fetching existing Brutus contacts for dedup...")
    existing = set()
    offset = 0
    page_size = 1000
    while True:
        url = f"{SUPABASE_URL}/rest/v1/contacts?select=email_normalized&offset={offset}&limit={page_size}"
        req = urllib.request.Request(url, headers={
            "apikey": SUPABASE_JWT,
            "Authorization": f"Bearer {SUPABASE_JWT}",
            "Accept-Profile": "brutus",
            "Accept": "application/json",
            "User-Agent": UA,
        })
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                rows = json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            print(f"  Brutus contacts fetch HTTP {e.code}: {e.read().decode()[:200]}")
            break
        if not rows:
            break
        for row in rows:
            em = (row.get("email_normalized") or "").lower().strip()
            if em:
                existing.add(em)
        if len(rows) < page_size:
            break
        offset += page_size
        time.sleep(0.2)
    print(f"  Found {len(existing)} existing emails in Brutus")
    return existing


def push_batch(leads: list[dict]) -> tuple[bool, str]:
    body = json.dumps({"leads": leads}).encode()
    req = urllib.request.Request(WEBHOOK, data=body, headers={
        "Content-Type": "application/json",
        "User-Agent": UA,
    }, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status == 200, r.read().decode()[:200]
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}: {e.read().decode()[:200]}"
    except Exception as e:
        return False, str(e)[:200]


def main():
    p = argparse.ArgumentParser(description="Bulk-import leads from CSV into FlowOps pipeline.")
    p.add_argument("csv_path", help="Path to CSV file with leads")
    p.add_argument("--niche", required=True, choices=sorted(VALID_NICHES),
                   help="Niche tag for ALL leads in this CSV")
    p.add_argument("--dry-run", action="store_true",
                   help="Read + dedupe + count, but don't actually push")
    p.add_argument("--skip-dedup", action="store_true",
                   help="Skip Brutus dedup check (faster, allows duplicates)")
    p.add_argument("--batch-size", type=int, default=100,
                   help="Leads per batch POST (default 100)")
    p.add_argument("--limit", type=int, default=None,
                   help="Cap import at N leads (for testing)")
    args = p.parse_args()

    csv_path = Path(args.csv_path).expanduser()
    if not csv_path.exists():
        print(f"ERROR: file not found: {csv_path}")
        sys.exit(1)

    # Load + normalize
    print(f"\n═══ BULK IMPORT — {csv_path.name} ═══")
    print(f"Niche: {args.niche}")
    print(f"Webhook: {WEBHOOK}")
    print(f"Mode: {'DRY RUN (no push)' if args.dry_run else 'LIVE'}")
    print()

    # Detect delimiter
    delim = "\t" if csv_path.suffix.lower() == ".tsv" else ","
    with open(csv_path) as f:
        reader = csv.DictReader(f, delimiter=delim)
        rows = list(reader)
    print(f"Loaded {len(rows)} rows from CSV")

    # Normalize
    normalized = []
    skipped_no_email = 0
    for r in rows:
        norm = normalize_row(r, args.niche)
        if norm is None:
            skipped_no_email += 1
            continue
        normalized.append(norm)
    print(f"  {len(normalized)} valid (have email)")
    print(f"  {skipped_no_email} skipped (no email)")

    # In-CSV dedup (keep first occurrence per email)
    seen = set()
    before_local = len(normalized)
    deduped = []
    for n in normalized:
        if n["email"] in seen:
            continue
        seen.add(n["email"])
        deduped.append(n)
    normalized = deduped
    if before_local - len(normalized) > 0:
        print(f"  {before_local - len(normalized)} dedup'd within CSV (same email appeared twice)")

    # Dedup against Brutus
    if not args.skip_dedup:
        existing = get_existing_brutus_emails()
        before = len(normalized)
        normalized = [n for n in normalized if n["email"] not in existing]
        print(f"  {before - len(normalized)} dedup'd against Brutus (already imported)")

    # Limit
    if args.limit:
        normalized = normalized[:args.limit]
        print(f"  Capped at {args.limit} for testing")

    print(f"\nReady to import: {len(normalized)} leads")
    if not normalized:
        print("Nothing to import. Done.")
        return

    if args.dry_run:
        print("\n--dry-run set, not pushing. Sample of first 3 leads:")
        for n in normalized[:3]:
            print(f"  {json.dumps(n, indent=4)}")
        return

    # Push in batches
    print(f"\nPushing in batches of {args.batch_size}...")
    total_ok = 0
    total_err = 0
    for i in range(0, len(normalized), args.batch_size):
        chunk = normalized[i:i + args.batch_size]
        ok, body = push_batch(chunk)
        batch_num = i // args.batch_size + 1
        total_batches = (len(normalized) + args.batch_size - 1) // args.batch_size
        if ok:
            total_ok += len(chunk)
            print(f"  batch {batch_num}/{total_batches}: ✓ {len(chunk)} pushed")
        else:
            total_err += len(chunk)
            print(f"  batch {batch_num}/{total_batches}: ✗ {len(chunk)} FAILED — {body[:100]}")
        time.sleep(0.5)  # rate limit gentle

    print()
    print("═" * 60)
    print(f"DONE  Pushed: {total_ok}/{len(normalized)}  Errors: {total_err}")
    print(f"      Webhook will personalize + push to Smartlead in ~30 sec/batch")
    print(f"      Track progress in Slack #1-new-lead")


if __name__ == "__main__":
    main()
