# Acquisity → Smartlead Workflow

End-to-end ingest pipeline for Acquisity-purchased lead lists.

## Steps

```
Acquisity CSV → bulk_import.py → n8n webhook → Council personalization → Smartlead campaign → daily send
```

## Pre-flight (one-time, Neal)

Confirm Acquisity export format includes at minimum:
- `email` (any case)
- `first_name`, `last_name` (or `name` + we split)
- `company_name` (or `Company`)
- `website` / `domain`
- `city` + `state`

Optional but improves personalization:
- `phone`, `title` (job title), `linkedin`, `revenue_band`, `employee_count`, `industry_naics`

The importer auto-maps every common column name variant. No CSV pre-processing needed.

## Usage

```bash
cd ~/Desktop/council

# Dry-run first to confirm parsing + see sample output
python3 bulk_import.py ~/Downloads/acquisity_wealth_2026-05-11.csv \
  --niche WEALTH --dry-run

# Live push to pipeline
python3 bulk_import.py ~/Downloads/acquisity_wealth_2026-05-11.csv \
  --niche WEALTH
```

Flags:
- `--niche`        — required. One of: FINANCIAL, WEALTH, MORTGAGE, COMMERCIAL_LOAN, FUNDING, MCA, AGENCY, MEDSPA, PI_LAW, BIZ_LAW
- `--dry-run`      — read + dedupe + show first 3 leads, don't push
- `--skip-dedup`   — bypass the Brutus dedup check (faster on huge imports, allows dupes)
- `--batch-size N` — leads per webhook POST (default 100, fine for most cases)
- `--limit N`      — cap to N leads (useful for testing)

## Built-in safeguards

1. **No-email rows** silently skipped (logged in summary)
2. **In-CSV dedup** — same email appearing twice gets collapsed to first occurrence
3. **Brutus dedup** — every email checked against existing contacts before push
4. **Batch size cap** — keeps the n8n webhook from timing out on huge imports

## After import, what happens automatically

1. n8n webhook receives the batch
2. Council personalization fires per lead (~$0.08/lead, 60 sec)
3. Personalized leads get the 9-key variable set written to Smartlead custom fields
4. Lead lands in the matching campaign, ready for next send window

## Recommended cadence

- **One niche per import.** Don't mix WEALTH + MORTGAGE in one CSV.
- **2000-5000 leads at a time.** Larger imports stress the n8n side; smaller are fine.
- **Run dry-run first.** Always. Catches bad CSV format before it pollutes Smartlead.
- **Schedule pulls every 2 weeks.** Lead freshness matters for cold reply rate.

## Cost per imported lead

| Step | Cost |
|---|---|
| Acquisity lead cost | (Neal's contract rate) |
| Council personalization | ~$0.08 |
| Smartlead send (per email) | included in subscription |
| Auto-reply if positive | ~$0.005 |
| **Total marginal cost per send** | **~$0.08-0.09** |

At 900/day → $72-81/day marginal LLM cost. Trident retainer is $5-15K/mo. Unit econ is fine.

## Tonight's synthetic smoke test results

Ran with `/tmp/acquisity_synthetic.csv` (11 rows):
- 10 valid (1 skipped: no email)
- 1 deduped within CSV (duplicate row)
- 9 final → ready to push

The fields normalize cleanly. Once you drop a real Acquisity CSV in `~/Downloads/`, the same command runs against it.

## Open question for Neal

What's the actual Acquisity export schema? If it has revenue/employee count or any signal data the importer should capture but currently ignores, send me the column header row and I'll extend the field mapper.
