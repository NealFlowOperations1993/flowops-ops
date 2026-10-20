# Strategy: 3 Booked Calls/Day

**Date:** 2026-05-11
**Goal:** 3 booked Trident qualification calls/day, sustainably, by end of May.
**Operating constraint:** Neal's attention is the bottleneck. The system books calls without him in the loop.

---

## The funnel math

Working backward from 3 booked/day:

| Stage | Rate | Volume needed |
|---|---|---|
| Booked calls/day | — | **3** |
| Positive replies/day | 60% → book (auto-system + speed) | 5 |
| Total replies/day | 40% positive | 13 |
| Sends/day | 1.5% reply rate (Council + magnets) | **870/day** |

So the system target is **~850-900 sends/day** with a reply rate of 1.5%+ and a 60% positive→book conversion (which the auto-reply system + GHL booking link makes achievable).

If reply rate drops to 1.0% baseline, sends need to climb to **~1,250/day**.

## Current state (2026-05-11)

| Niche | Status | Sends to date | Reply rate | Notes |
|---|---|---|---|---|
| MCA | ACTIVE | 125 | 0.80% | Ralph replied |
| WEALTH | ACTIVE | 45 | **2.22%** | Jon replied today — best converter |
| COMMLOAN | ACTIVE | 21 | 0.00% | Too early |
| FINANCIAL | PAUSED | 61 | 0.00% | Subject line dead, 9.8% open |
| MORTGAGE | PAUSED | 61 | 1.64% | 11.5% bounce — list quality |
| INSURANCE | PAUSED | 1 | — | Functional, not launched |
| AGENCY | COMPLETED | 1 | — | Old run, dormant |
| TAX_RES | DRAFTED | 0 | — | No inboxes, no leads |
| IT_MSP | DRAFTED | 0 | — | No inboxes, no leads |
| Total | — | **320** | **0.94%** | |

**Current send capacity:** 10 inboxes × 15/day = **150/day max**, ~60/day actual.

**Gap to goal:** Need ~6x send capacity AND need to keep reply rate at 1.5%+. The capacity gap is the binding constraint.

---

## The 4 levers, in priority order

### Lever 1 — Speed-to-lead via auto-reply (DONE, awaiting deploy)

The single biggest multiplier on what you already have.

- Built: `webhook_server.py` + `core/reply_orchestrator.py`
- Latency: ~4 sec from inbound webhook to outbound reply
- Cost: ~$0.005 per inbound
- Coverage: All POSITIVE replies (confidence ≥ 0.75) auto-respond with contextual draft + GHL booking link
- NEUTRAL/NEGATIVE/OOO/UNSUB → Slack alert to Neal, no auto-action
- Voice rules baked in (no em-dashes, no fault admission, no jargon)

**Expected lift:** 35% book rate (current, when Neal sees replies same-day) → 65-75% book rate (auto-reply within seconds). Roughly **2x book conversion** on existing reply volume.

**To deploy:** see `DEPLOY_REPLY_SYSTEM.md`. Ngrok or Cloudflare Tunnel + Smartlead webhook config = 30 min Neal's time.

### Lever 2 — More inboxes (capacity expansion)

Current: 10 inboxes × 15/day = 150/day ceiling. Need ~6x.

**This weekend (Neal's task, ~$50-100 total):**
- Buy 4 more sender domains via Zapmail (use the same name patterns as flowoperations.org + flowopsleadgen.com)
  - Suggestion: `flowopsoutbound.com`, `flowops-direct.com`, `flowoperationsai.com`, `getflowops.com`
- Each domain: 5 inboxes with the same `lilly@`, `priya@`, `ryan@`, `ashley@`, etc. naming
- Spool up Smartlead warmup on all 20 new inboxes (Zapmail auto-onboards to Smartlead)
- Once warm (10 days): bump cap from 15 → 30/day per inbox

**Final state after warmup completes (late May):**
- 6 domains × 5 inboxes × 30/day = **900/day capacity** — right at goal.

### Lever 3 — Reply rate uplift (Council + niche magnets + landing pages)

Current avg 0.94%. WEALTH already at 2.22%. Target: 1.5% overall.

Three things move it:
1. **Niche-specific magnets** — already redesigned for 5 hard niches (`lead_magnets_v2.md`). Wire into sequences.
2. **Lovable landing pages** — drafted in `lovable_prompts.md`. When deployed, swap email CTAs from "reply 'send'" to landing-page URL. Captures FB pixel + lets prospects self-serve the magnet without replying.
3. **Subject line spintax** — Financial died at 9.8% open because of one bad subject. All campaigns should ship 3-5 subject variants per niche with spintax `{{a|b|c}}` syntax.

**Expected lift:** 0.94% → 1.5% over 30 days. Conservative.

### Lever 4 — Lead supply (Acquisity + Apify cron)

At 900 sends/day, you burn **27K leads/month**. Apify daily cron at $0.50/day budget produces maybe 50-100/day = 1,500-3,000/month. Not enough.

**Acquisity is the supply unlock:**
- Bulk-import via `bulk_import.py` (already built, handles 12 niche tags)
- Target: 5K-10K leads per pull, per niche, every 2 weeks
- Dedupes against Brutus contacts table automatically
- Smoke test: 200 leads through end-to-end Sun (waiting on your CSV export)

Apify continues as a freshness layer — daily small drops of recently-active businesses.

---

## The week's execution plan

### Tonight / overnight (autonomous)
- [x] Auto-reply pipeline built, tested, dry-run on Ralph + Jon
- [x] Webhook server + deployment doc written
- [x] Real campaign state mapped (corrected IDs)
- [x] Jon's reply queued as a draft for Neal to fire
- [ ] Strategy doc (this one)
- [ ] Acquisity ingest pipeline prep + synthetic-data smoke test
- [ ] Mailbox expansion plan + buy list
- [ ] Financial subject line rewrites (5 variants, spintax format)

### Monday (Neal + me)
- Neal: buy the 4 domains, kick off warmup
- Neal: deploy webhook server (Cloudflare Tunnel recommended)
- Neal: wire Smartlead EMAIL_REPLY webhook → tunnel URL
- Neal: drop BRUTUS_BOT_TOKEN env so Slack alerts fire
- Neal: hit "send" on the Jon draft once approved
- Me: relaunch FINANCIAL with new subject variants
- Me: attach inboxes + load leads into TAX_RES, IT_MSP, INSURANCE
- Me: 7am digest of Sunday's metrics

### Tuesday-Friday
- Run live with auto-reply system
- Daily metrics check, tune subject lines per niche
- 20 new inboxes finish warmup ~end of next week → bump caps to 30/day
- Acquisity pulls 5K leads into the 3 highest-converting niches

### End of May
- 6 domains, 30 inboxes, ~900 sends/day
- 1.5% reply, 40% positive, 65% auto-book = **3.5 calls/day**

---

## What kills this plan

1. **Bounce rate creeps above 5%** → Smartlead pauses domains, sending drops. Mitigation: every Acquisity import goes through ZeroBounce or MillionVerifier first.
2. **GHL booking link goes 404** or routing changes. Mitigation: link checked on every auto-reply (already coded).
3. **Council draft hallucinates fake deliverables** in auto-replies. Mitigation: voice rules + per-niche offer summary fed to the drafter (already coded).
4. **Domain reputation drops on a sender** (spam complaints, replies marked junk). Mitigation: warmup must keep running on all inboxes, monitor via Smartlead's domain reputation dashboard.

---

## The KPI dashboard (auto-updated daily at 7am via Monday digest)

```
DAILY METRICS — 2026-05-XX
─────────────────────────────────────────────
Sends (24h):         872 / 900 target
Inbox utilization:   97%
Reply rate (24h):    1.54%  ✓ above 1.5% target
Positive %:          43%    ✓ above 40% target
Bounces (24h):       2.1%   ✓ below 5% threshold

REPLIES PROCESSED (24h):
  Auto-replied:       8
  Flagged to Neal:    5  (NEUTRAL: 3, NEGATIVE: 2)
  Unsubscribed:       2
  Out-of-office:      1

CALLS BOOKED (24h):   3  ✓ goal met
Calls scheduled (next 48h):  7
─────────────────────────────────────────────
```
