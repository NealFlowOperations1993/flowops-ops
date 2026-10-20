# Mailbox Expansion Plan

**Goal:** Get from 150/day capacity (10 inboxes × 15/day) to 900/day capacity (30 inboxes × 30/day) by end of May.

## Current state

| Domain | Inboxes | Per-inbox daily | Daily capacity |
|---|---|---|---|
| flowoperations.org | 5 (lilly, priya, ryan, ashley, nealt) | 15 | 75 |
| flowopsleadgen.com | 5 (roddy, mason, john, carly, neal) | 15 | 75 |
| **Total** | **10** | — | **150** |

Both domains are warmed and sending without bounce issues. Safe to bump per-inbox.

## Target state by end of May

| Domain | Inboxes | Per-inbox daily | Daily capacity |
|---|---|---|---|
| flowoperations.org (existing) | 5 | 30 | 150 |
| flowopsleadgen.com (existing) | 5 | 30 | 150 |
| Domain 3 (new) | 5 | 30 | 150 |
| Domain 4 (new) | 5 | 30 | 150 |
| Domain 5 (new) | 5 | 30 | 150 |
| Domain 6 (new) | 5 | 30 | 150 |
| **Total** | **30** | — | **900** |

## Domain buy-list (Neal, this weekend)

Buy 4 new domains. Pick names that look like real ops/sales domains, NOT lookalikes of the main brand (to avoid Google flagging when they connect inbox patterns).

Recommended pattern: short, generic, no hyphens, .com or .co:

| Suggested name | Available? | Notes |
|---|---|---|
| flowopsoutbound.com | check Zapmail | clear ops naming |
| flowops-direct.com | avoid (hyphen) | — |
| getflowops.com | check | "get" prefix is fine for sales |
| operationsflow.com | check | mirror image |
| flowopssolutions.com | check | descriptive |
| flowopsteam.com | check | sounds like internal ops |
| flowops.partners | check | .partners TLD reads well for B2B |
| trident-ops.com | avoid (Trident brand exposure) | — |

**Pick 4. Total cost: ~$48-60 ($12-15 each via Zapmail or Namecheap).**

## Inbox naming convention (consistent across domains)

Use real-sounding US first names. Vary across domains so the pattern isn't obvious.

Example per new domain (just an example set — Zapmail picks the actual ones):

```
Domain 3:  emma@, jacob@, olivia@, michael@, sophia@
Domain 4:  liam@, ava@, noah@, isabella@, ethan@
Domain 5:  mia@, lucas@, charlotte@, mason@, amelia@
Domain 6:  oliver@, harper@, elijah@, evelyn@, james@
```

Don't repeat names across domains (Smartlead correlates patterns).

## Warmup timeline

1. **Day 0-1 (this weekend):** Buy domains via Zapmail. Zapmail auto-creates inboxes + sets up SPF/DKIM/DMARC + connects to Smartlead automatically.
2. **Day 1-14:** Smartlead's warmup runs daily on each inbox. Volume scales from 2/day → 10/day → 15/day automatically.
3. **Day 14-21:** Manual cap bump per inbox: 15 → 25/day. Monitor bounce + spam rates.
4. **Day 21-28:** Final bump: 25 → 30/day. At this point all 30 inboxes are at full capacity.

## Per-inbox daily cap bumps for existing 10 inboxes

Existing 10 inboxes are warm enough to bump TODAY. Smartlead UI:

```
Email Accounts → Bulk Edit → Daily Sending Limit → 30
```

Apply to all 10 existing inboxes. Effective tomorrow. **This alone doubles your capacity from 150 → 300/day.**

## Smartlead account budget check

- Subscription tier: confirm you're on the Pro plan (supports 30+ inboxes) — should be fine
- API rate limits: 60 requests/sec — we're nowhere near that
- Warmup: included free, no per-inbox add-on cost

## Monitoring during scale-up

Watch these metrics weekly. If any go red, pause new inboxes and investigate before adding more.

| Metric | Green | Yellow | Red |
|---|---|---|---|
| Bounce rate (rolling 7d) | <3% | 3-5% | >5% |
| Spam complaint rate | <0.1% | 0.1-0.3% | >0.3% |
| Open rate per domain | >35% | 25-35% | <25% |
| Warmup reply rate | >80% | 60-80% | <60% |

## Total weekend cost summary

| Item | Cost |
|---|---|
| 4 new domains | $48-60 |
| 20 new Zapmail inboxes | usually bundled with domain on Zapmail |
| Apify monthly cap raise | $54 (to lift current cap) |
| **Total cash outlay** | **~$110** |

## What this unlocks (math)

```
Today:           150/day × 1.5% reply × 40% positive × 65% book = 0.6 calls/day
End of week:     300/day (bumped existing) × 1.5% × 40% × 65%   = 1.2 calls/day
End of May:      900/day (full warmup)   × 1.5% × 40% × 65%     = 3.5 calls/day  ✓
```

The 30-inbox plan is what gets you to 3 calls/day. Everything else (auto-reply, magnets, landing pages) is multiplier on top.
