# FlowOps — Cold Email

This project is the FlowOperations cold email engine: lead sourcing, tool generation,
Smartlead sending, reply handling and reporting. Read `docs/FlowOps_Cold_Email_Infrastructure.pdf`
for the full picture before making changes.

## Before running anything

```bash
set -a; source ~/.config/n8n-creds/flowops-core.env; set +a
```

Every script reads credentials from the environment: `SMARTLEAD_API_KEY`, `ANTHROPIC_API_KEY`,
`OPENROUTER_API_KEY`, `APIFY_TOKEN`. Without this they raise `KeyError` — intended, so a stale
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
2. **Wire the contractor notification.** Tool submissions hit n8n `fo-tool-lead`, get logged and
   Slacked to us, but **never reach the contractor** — while the email promises they do.
   Affects all 2,558 live tool pages.
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
