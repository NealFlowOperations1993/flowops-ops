# FlowOps — Cold Email

This project is the FlowOperations cold email engine: lead sourcing, tool generation,
Smartlead sending, reply handling and reporting. Read `docs/FlowOps_Cold_Email_Infrastructure.pdf`
for the full picture before making changes.

## Before running anything

```bash
set -a; source ~/.config/n8n-creds/flowops-core.env; set +a
```

Every script reads credentials from the environment: `SMARTLEAD_API_KEY`, `ANTHROPIC_API_KEY`,
`OPENROUTER_API_KEY`, `APIFY_TOKEN`, and `SUPABASE_SERVICE_KEY` (used by `bulk_import.py` and
`core/signal_enricher.py`). Without this they raise `KeyError` — intended, so a stale
key is never used silently. **Never hardcode a key**; 29 were removed from source on 2026-10-20.

## Current state (2026-10-23)

- **All four contractor campaigns are stopped.** Nothing sent since Oct 5.
- Cause is **lead starvation, not breakage** — 38 untouched leads vs 315/day capacity.
- All 13 n8n workflows are active and healthy; the machine runs on an empty track.
- Lifetime: 6,173 sent, **7 human replies (0.11%)**, 2 positive, **0 calls booked**.
- 10 inboxes, 2 domains, all 100% warmup reputation. **Never pause warmup.**

## The core problem

0.11% reply rate is ~20x below the industry floor (2–3% average). This is a **copy problem**,
not a delivery problem. Do not scale volume before reply rate clears 2%.

At top-quartile conversion (1.5% booked), 300 emails/day — what the 10 inboxes already
support — produces ~4.5 meetings/day, which hits the 3–5 calls/day goal. **The target does
not require 5,000/day.**

## Open work, in order

1. **Reply to Ben** at `ben@codexconstruction.com` — asked "Ballpark?" on Sep 19, unanswered.
2. ~~Wire the contractor notification.~~ **Done and verified (Nov 23).** The current tool site
   (Lovable Tool Studio, `brandable-toolbox-studio.lovable.app/t/...`) posts each submission to n8n
   `fo-toolstudio-lead` (workflow aR4U1sCh1HAuCxta, live since Nov 4), which emails the business's
   `owner_email` via Gmail with the homeowner's details (bcc raine@). Routing check passed Nov 23.
   No real homeowner submission yet. (The old `fo-tool-lead` note applied to the retired Vercel pages.)
3. **Rebuild the copy as ONE new campaign** — compliant subjects, no orphaned lines, no
   monthly-payment promise, plus a pre-send coherence check.
4. Refill the lead list (~$8.60/day of Google Maps scraping).
5. Restart at 150–200/day. Hold until reply rate clears 2%.

## Hard-won rules — do not relearn these

- **Never write to a live Smartlead sequence.** It recreates every variant even when IDs are
  passed back, re-queueing contacted leads into duplicate sends. Ship copy changes as a *new*
  campaign. Per-lead `custom_fields` are the only safe in-place edit.
- **Smartlead's reply webhook inverts fields:** `from_email` is OUR mailbox, `to_email` /
  `sl_lead_email` is the prospect.
- **Open rate is not real.** Raw ~48% is mostly security scanners — median time-to-open is 24
  seconds and there are 0 clicks on 1,610 opens. True rate is 14–18%. Judge on replies.
- **A reply under 6 minutes is a machine**, not a human.
- **Never assert an absence** ("you have no booking page") from one page of evidence. Criticism
  openers produced most of our hostile replies.
- **A signal that becomes a factual claim needs real evidence**, never a keyword match.
- **Deletion filters must be allow-list narrow** — a cleanup once deleted 177 real leads because
  real contractors are named Joe.
- **Never guess email addresses** (e.g. firstname@company.com). Use only addresses published on
  the company's own site, licence record or listing. Guessed addresses came back 13% Reoon-safe
  vs 77–83% for published ones (Nov 18), wasting credits.
- **Owner-only filter removed (Neal, Nov 19).** 5 of the 7 positives replied from a generic
  inbox (e.g. tndeckworks@gmail.com). Any inbox the company publishes itself is allowed,
  including info@ and office@; prefer a named person's when one is published. Every lead still
  records `owner_evidence` (blank is fine), `source`, `source_url` and its score.
- **Google Maps leads only (Neal, Nov 19).** No YellowPages, licence lists or manufacturer
  locators. Tag every lead `source=google_maps` with its placeId. Fresh scraping is Apify
  `compass~crawler-google-places` (~$0.004/place; server-side filters +$0.001 each; $200/cycle cap,
  cycle Nov 20–Dec 19 — do NOT ask to raise it).
- **SCRAPING PAUSED (Neal, Nov 23).** After the Nov 23 deck scrape, launch NO Apify runs until
  Neal says to resume. Apify cycle was ~$165 of $200 (98% our Google Maps actor). Leads are sized to
  last to Nov 30: deck 75/day, W1-B hardscape 15/day, W2 mortgage 20/day. If deck runs short, lower
  its daily cap rather than scrape. Next scrape needs a cheaper method (half of each search was
  already-scraped places).
- **The winning recipe (Nov 4–14, all positives). Restored Nov 21 — do not drift. No filter may
  be added that did not exist then without Neal's say-so.**
  - **Leads:** Google Maps "deck builder" + "deck contractor" in affluent counties. Rating ≥ 4.3,
    20+ reviews (Claude's filter, Nov 19 — ~18% of the winning pool was below it; all positives
    above), real site, no chain/supplier/franchise. **Do not require "deck" in the homepage
    title, and do not restrict Apify to the "deck builder" category** — the winning deck pool was
    only ~60% Google "Deck builder"; ~40% were general contractors, construction and fence
    companies that build decks (positives G&J General Contractors, MAC Home Pros). Rule: category
    "Deck builder" passes; other contractor categories pass if their own site mentions decks ≥2×;
    drop painters, pressure washers, handymen, siding/roofing-first, stain/repair-only shops.
  - **Email 1 is a MIX, not one email.** Deck Nov 4–14 positives per sends: "price shoppers"
    2/281, "quick question" 1/35, "two homeowners" 1/17, "I'm just wondering" 1/~15. New deck
    leads get 40% price shoppers + 20% each of the other three, word for word
    (`scripts/pipeline/build_w.py`, variants J/Q/W/T; W uses the deck-project-planner tool).
  - **Email 2:** "Bumping this up. Want me to send the deck designer over? It takes about a
    minute to try." No link. The Nov 13 rewrite that put the link in Email 2 killed replies.
  - **Email 3:** the breakup with the link.
  - **Deck campaign 4336994:** 150 new leads/day (Neal, Nov 21), send window 8 AM–1 PM Central.
- **Branding is ALWAYS on (Neal, Nov 23).** Every new tool_prospects row now queues a branding job
  automatically (DB trigger `tool_prospects_always_enrich`), however it's inserted. Root cause of
  the Nov 9–23 gap: our uploads inserted rows with raw SQL, which skipped the import API's job queue,
  so ~2,700 pages had no logo/colors. Worker: cron `tool-branding-enrichment` every minute →
  `/api/public/enrich`, now 20 per run. Never remove the trigger.
- **Per-company offer + price range (Neal, Nov 23):** each tool must show that company's own services/
  materials and a price range for that company — published prices from their site when they exist,
  otherwise a local-market estimate labelled as such. Never present an estimate as their own prices.
- **Mix follows positives.** Deck gets the biggest share of new leads; HVAC the smallest.
- **Dedupe by company name and phone too**, not just email/domain — a different address at a
  company we already emailed is still a repeat.
- **Reoon keep rule:** safe + catch_all + role_account; drop unknown, invalid, disabled.
- **Scan every lead after an upload**, never a sample. A 25-lead sample once passed while 1,275
  were broken.
- **Model calls go in n8n HTTP nodes**, not Code nodes — 60s limit kills them silently.
- **Check `campaign_lead_stats.notStarted` before judging performance.** A dry list looks
  identical to a paused campaign in reports.

## Where things live

| Resource | Location |
|---|---|
| Tool pages (live) | `flowops-assets.vercel.app/tools/{slug}` |
| Tool page source | `github.com/NealFlowOperations1993/flowops-assets` |
| This repo | `github.com/NealFlowOperations1993/flowops-ops` |
| Master leads (33,132) | Apify dataset `cMhQiJNz6imqqTNOb` |
| Automations | `exaltisgroup.app.n8n.cloud` — 13 workflows |
| Reporting | Slack `#cold-email` (`C0BRH7PBC14`) |
| Post to Slack | `POST n8n /webhook/fo-brutus-report {"text":"..."}` |
| Send a file to Slack | `POST n8n /webhook/slack-send-file-v2-6d2e9f` (multipart) |

## Campaigns

| ID | Name | Status |
|---|---|---|
| 3842105 | Hardscaping | COMPLETED |
| 3845617 | Deck Builders | PAUSED (356 leads left) |
| 3863467 | Hardscape v2 | PAUSED (37 leads left) |
| 3848711 | Outdoor Living | COMPLETED |

## Deploying tool pages

```bash
cd ~/Desktop/flowops-assets && npx vercel@latest deploy --prod --yes
```

Vercel auto-deploy on push is **not yet wired** — the Vercel account has no GitHub Login
Connection (add at vercel.com/account/login-connections). Project is owned by the team
`flow-operations`, not the personal account.
