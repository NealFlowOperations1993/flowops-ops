# FlowOps Cold Email Pipeline — Detailed SOP

**Owner:** Neal Thakkar
**Last updated:** 2026-05-13
**Status:** LIVE — sending tomorrow at 4 AM ET

---

## Table of contents

1. [Vision & target metrics](#1-vision--target-metrics)
2. [Stage 1 — Discovery (Lead supply)](#2-stage-1--discovery-lead-supply)
3. [Stage 2 — ICP Filter](#3-stage-2--icp-filter)
4. [Stage 3 — Signal Enrichment (Cara Barone)](#4-stage-3--signal-enrichment-cara-barone)
5. [Stage 3.0 — Strategy Council (Magnet picker)](#5-stage-30--strategy-council-magnet-picker)
6. [Stage 3.5 — Magnet Generation (4 variants A/B/C/D)](#6-stage-35--magnet-generation-4-variants)
7. [Stage 4 — Copy Generation](#7-stage-4--copy-generation)
8. [Stage 5 — Send (Smartlead)](#8-stage-5--send-smartlead)
9. [Stage 6 — Auto-Reply (Webhook + LLM)](#9-stage-6--auto-reply)
10. [Stage 7 — Booked Call (GHL)](#10-stage-7--booked-call)
11. [Stage 8 — Metrics Loop](#11-stage-8--metrics-loop)
12. [Tech stack overview](#12-tech-stack-overview)
13. [Cost model](#13-cost-model)
14. [Runbooks](#14-runbooks)

---

## 1. Vision & target metrics

**Mission:** Build the highest-quality outbound system in service businesses — one that uses real research, real magnets, and real personalization at scale to fill Neal's calendar with qualified founder calls.

**Target metrics (90-day):**

| KPI | Today | 30 days | 60 days | 90 days |
|---|---|---|---|---|
| Daily new leads | 150 | 250 | 400 | 600 |
| Daily sends (new + followups) | 80-150 | 300-450 | 600-800 | 1,000-1,200 |
| Reply rate | unknown | 2.0% | 2.5% | 3.0% |
| Positive reply rate | unknown | 0.9% | 1.2% | 1.5% |
| Booked calls / day | 0 | 2-3 | 4-6 | 7-10 |
| Booked calls / month | 0 | 60-90 | 120-180 | 200-300 |
| Avg deal value (post-call) | n/a | $5K | $8K | $12K |
| Monthly revenue from outbound | $0 | $90-180K | $250-500K | $1M+ |

---

## 2. Stage 1 — Discovery (Lead supply)

**Goal:** Generate 150+ fresh, deliverable leads per day.

### Sources

1. **Apify Google Maps scraper** (`compass~crawler-google-places`)
   - Trigger: n8n cron, daily 6 AM ET
   - Workflow ID: `QVMajRvX1TKB7r0d` ("Daily Apify Niche Scrapes (FlowOps)")
   - Rotates 3 niches/day across 12-niche queue
   - Volume: 10 leads × 5 cities × 3 niches = 150 leads/day

2. **Acquisity CSV imports**
   - Manual: Neal exports CSV from Acquisity (purchased lists)
   - Workflow: `bulk_import.py ~/Downloads/file.csv --niche RECRUITER`
   - Includes in-CSV dedup + Smartlead-universe dedup
   - Volume: as available

3. **Manual seeding** (high-value targets)
   - Used for ABM list (Fortune 500, etc.)
   - Volume: ~5/day

### Niche rotation schedule

| Day | Niches scraped |
|---|---|
| Sun / Thu | MCA · MEDSPA · PI_LAW |
| Mon / Fri | WEALTH · MORTGAGE · INSURANCE |
| Tue / Sat | COMMLOAN · AGENCY · TAX_RES |
| Wed | RECRUITER · IT_MSP · FINANCIAL |

### Tools & cost

- **Apify:** ~$2-3/day → ~$60-90/mo
- **n8n:** flat subscription (exaltisgroup.app.n8n.cloud)
- **Storage:** local CSV cache at `~/.council/lead_cache/`

---

## 3. Stage 2 — ICP Filter

**Goal:** Pass only deliverable, in-ICP leads to enrichment.

### Filters

1. **Niche classifier** — 25+ categories (WEALTH, FINANCIAL, MORTGAGE, INSURANCE, MEDSPA, PI_LAW, MCA, COMMLOAN, AGENCY, RECRUITER, COACH_BIZ, COACH_FIT, IT_MSP, TAX_RES, etc.)
2. **Smartlead universe dedup** — if email exists in any campaign, skip
3. **Hygiene rejects:**
   - No website OR no email → drop
   - Personal-only email (gmail.com / hotmail.com / etc. with no business domain) → flag for manual review
   - Domain too new (<30 days) → flag
4. **Optional ZeroBounce mailbox verification** — for high-bounce niches (MORTGAGE history shows 11.5% bounce)

### Output

- ~70% pass rate → ~105 clean leads/day
- Each lead tagged with target campaign ID

### Code

- `core/icp_filter.py`
- `bulk_import.py` (Acquisity path)

---

## 4. Stage 3 — Signal Enrichment (Cara Barone)

**Goal:** Build a 3-5 line public-records dossier on each lead for use in personalization + forwarded-research format.

### Signal sources

| Source | What we look for | API |
|---|---|---|
| **LinkedIn** | Job changes, hires, posts | (scraped via internal) |
| **Company website** | Tech stack, services, tagline, social proof | scrape via Playwright |
| **SEC EDGAR** | Form D filings (wealth liquidity) | api.sec.gov |
| **Google Business Profile** | Reviews, hours, photos | Apify |
| **Reddit** | Brand mentions, complaints | (planned) |
| **Twitter/X** | Recent posts, follower count | (planned) |
| **Meta Ads Library** | Active ad creatives | (planned) |
| **YouTube** | Recent videos, subscriber growth | (planned) |
| **G2 / Trustpilot** | Reviews, NPS signals | (planned) |
| **News** | Recent press, fundings | NewsAPI/Apify |
| **Tech stack** | BuiltWith / Wappalyzer-style detect | (Playwright sniffer) |

### Output

```json
{
  "leadId": "abc123",
  "signals": {
    "linkedin_job_change_days": 14,
    "tech_stack": ["GHL", "Calendly", "ConvertKit"],
    "recent_news": "Featured in Forbes Wealth, May 2026",
    "form_d_count_metro_60d": 34,
    "gbp_reviews": 127,
    "gbp_avg_rating": 4.8
  }
}
```

### Cara Barone persona

This data flows into the "forwarded-from-Cara" email format. Cara is an AI research analyst persona, email `hello@carabarone.com`. The Council prompts her tone to feel like an internal Slack handoff: short, fact-dense, no salesy language.

### Code

- `core/signal_enricher.py`
- `core/cara_research.py` (was `brutus_research.py`, deprecated alias kept)
- Model: `google/gemini-2.0-flash-001` via OpenRouter

---

## 5. Stage 3.0 — Strategy Council (Magnet picker)

**Goal:** Decide which magnet variant (A / B / C / D) and angle to use for THIS lead, based on past metrics + signal strength.

### Decision matrix

| Lead profile | Best variant | Reason |
|---|---|---|
| High-traffic site, weak conversion | **C — Mockup** | Visual proof |
| Strong tech stack, modern site | **B — FlowScore** | They appreciate the data |
| Low signal but in-ICP | **D — Direct Audit** | Lowest friction |
| Highly personalized signal hit (job change, news) | **A — IntakeBot** | Engagement-led |

### Allocation (current default)

- Wed/Thu: A/B/C @ 33/33/34 (3-way baseline)
- **Fri onwards:** A/B/C/D @ 25/25/25/25

### Council architecture

- **12 personas** (different writer voices: Hormozi-blunt, NPR-warm, Ogilvy-classy, etc.)
- **5 judges** rank outputs on: clarity, specificity, no-template-feel, CTA strength, brand fit
- Top-scored variant wins → custom_fields populated → Smartlead picks it up

### Code

- `core/council.py`
- Model: Council uses Gemini Flash for drafts, Sonnet 4.5 for judge consensus

---

## 6. Stage 3.5 — Magnet Generation (4 variants)

### Variant A — IntakeBot URL (33% → 25% Fri)

**Concept:** Send the lead to a live demo of an AI receptionist customized to their niche.

- **URL:** `intakebot.vercel.app/for/{niche}`
- **Cost:** $0 (static demo, hosted on Vercel)
- **Status:** ✅ Live
- **Magnet asset:** N/A (link only)

### Variant B — FlowScore (33% → 25% Fri)

**Concept:** Run their site through the REAL FlowScore API and email them their actual score + biggest gap + dollar leak.

- **API:** `https://npjkusfkwybhyisfrhtb.supabase.co/functions/v1/analyze-url` (Supabase Edge Function behind flowoperations.ai/flowscore)
- **Returns:**
  - `overall_score` (0-100)
  - `score_range` (red/amber/green)
  - `interpretation` (paragraph)
  - `estimated_monthly_revenue_leakage` ({min, max})
  - `dimensions` (8 sub-scores with specific findings)
- **Cost:** $0 (Neal's existing FlowScore product)
- **Status:** 🟡 API wired (`core/flowscore.py`), wiring into personalizer

**3 split tests within Variant B:**
- **B1 — Call-first:** "Your FlowScore is X/100. Here's your biggest gap. 15 min to walk through fixes?"
- **B2 — Report-or-call:** "Reply REPORT for the 8-page PDF, REPLY CALL for 15 min"
- **B3 — PDF-then-call:** Email 1 = score teaser + "reply yes for the PDF". Email 2 = the PDF + "now that you've seen it, 15 min?"

### Variant C — Website Mockup (34% → 25% Fri)

**Concept:** Redesign their actual homepage with Gemini 3 Pro Image, send the mockup inline.

- **Tool:** Google Gemini 3 Pro Image (`google/gemini-3-pro-image-preview`) via OpenRouter
- **Layout:** Single tall vertical screenshot (portrait, 1440×3200), top-to-bottom continuous column
- **Niche-specific design language** per niche (luxury wealth navy+gold, medspa rose+cream, PI_law black+gold, etc.)
- **Hosted:** `flowops-assets.vercel.app/mockups/<slug>.png` (CORS-enabled, 1yr cache)
- **Pre-generation:** Run `mockup_batch_run.py` nightly for tomorrow's top 20 leads/niche
- **Cost:** $0.06/mockup → at 100/day = $180/mo
- **Status:** ✅ Live — 77 mockups pre-generated for tomorrow

### Variant D — Direct AI Audit Pilot (Friday rollout)

**Concept:** No consumable. Just pitch the pilot directly: "free 20-min AI Audit, we want the case study, want it?"

- **Magnet asset:** None — it's offer-led, not value-led
- **Cost:** $0 ($0 to generate, but consumes Neal's call time on conversion)
- **Status:** 🟡 Drafted, loads Thursday night, fires Friday 4 AM

**Predicted performance:** Highest reply rate, lowest click rate, similar book rate to B+C. Removes all friction.

---

## 7. Stage 4 — Copy Generation

**Goal:** Write the actual 4-step email sequence per lead.

### Per-email structure

```
[Personalized opener — uses Cara signal]
[Role-specific pain — niche + persona-aware]
[Magnet pitch — depends on variant A/B/C/D]
[CTA — depends on variant]
[Cara forwarded research — only V1/V6 of Acquisity, optional elsewhere]
[Signature — persona name + Neal's calendar link]
```

### Followup cadence

- **Step 1 (Day 0):** Main pitch + magnet
- **Step 2 (Day 3):** "Re: the $X/mo leak" — quick follow-up, different angle
- **Step 3 (Day 5):** "Worth 15 min or not?" — close the loop, either answer fine
- **Step 4 (Day 7):** "Last note" — breakup, calendar link in footer

### Model usage

- **Gemini Flash** — 80% of generations (cheap, fast, good enough)
- **Sonnet 4.5** — 20% for high-value leads / hard niches / Council judge consensus
- **All via OpenRouter** (UNIVERSAL RULE: all LLM calls route through OpenRouter)

### Code

- `core/council.py`
- `bulk_personalize_smartlead.py` (the per-lead runner)

---

## 8. Stage 5 — Send (Smartlead)

### Persona inboxes (10)

| Persona | Email | Domain | Cap |
|---|---|---|---|
| Lilly Smith | lilly@flowoperations.org | flowoperations.org | 40/day |
| Priya Iyer | priya@flowoperations.org | flowoperations.org | 40/day |
| Ryan Mitchell | ryan@flowoperations.org | flowoperations.org | 40/day |
| Ashley Cole | ashley@flowoperations.org | flowoperations.org | 40/day |
| Neal Thakkar | nealt@flowoperations.org | flowoperations.org | 40/day |
| Roddy Greene | roddy@flowopsleadgen.com | flowopsleadgen.com | 40/day |
| Mason Park | mason@flowopsleadgen.com | flowopsleadgen.com | 40/day |
| John Davis | john@flowopsleadgen.com | flowopsleadgen.com | 40/day |
| Carly Bennett | carly@flowopsleadgen.com | flowopsleadgen.com | 40/day |
| Neal (alt) | neal@flowopsleadgen.com | flowopsleadgen.com | 40/day |

**Total daily capacity: 400/day.**

### Send window

- **Time:** 4 AM – 12 PM ET (8-hour window)
- **Days:** 7 days/week
- **Min time between emails per inbox:** 5 min
- **From-name:** Persona (Lilly Smith, etc.) — body signs off as Neal

### Active campaigns

| Niche | Campaign ID | Status | Leads in queue |
|---|---|---|---|
| WEALTH | 3263730 | ACTIVE | 2,072 |
| FINANCIAL | 3191292 | ACTIVE | 2,894 |
| MORTGAGE | 3191290 | ACTIVE | 1,768 |
| INSURANCE | 3191291 | ACTIVE | 86 |
| MCA | 3263732 | ACTIVE | legacy |
| COMMLOAN | 3263731 | ACTIVE | legacy |
| MEDSPA | 3191285 | PAUSED | 1 |
| PI_LAW | 3327115 | DRAFTED | 0 |
| RECRUITER | 3191293 | PAUSED | 0 |

---

## 9. Stage 6 — Auto-Reply

**Goal:** Reply to inbound emails within 90 seconds, draft a response, route to Neal's inbox for review.

### Architecture

1. **Smartlead webhook** fires `EMAIL_REPLY` event
2. **Cloudflare Tunnel** forwards to local FastAPI service (`webhook_server.py` on port 8787)
3. **LLM classifier** (Sonnet 4.5 via OpenRouter) categorizes:
   - `INTERESTED` — drafts response with GHL booking link
   - `NOT_INTERESTED` — drafts polite close
   - `OUT_OF_OFFICE` — flags for re-send when they're back
   - `WRONG_PERSON` — asks for referral
   - `QUESTION` — drafts answer + maintains conversation
4. **Drafted response** lands in Neal's Smartlead inbox as a draft (not auto-sent)
5. **Neal reviews + sends** (or auto-send threshold can be added later)

### Status

- ✅ Webhook registered on 9 campaigns
- 🟡 Tunnel currently ephemeral (`additional-accessibility-marker-ada.trycloudflare.com`) — needs persistent named tunnel for production

---

## 10. Stage 7 — Booked Call

**Goal:** Convert positive replies into 15-20 min discovery calls on Neal's calendar.

### Flow

1. Auto-reply drops GHL booking link
2. Lead clicks → GHL widget (`api.leadconnectorhq.com/widget/bookings/flowqualificationcall`)
3. Lead picks slot → GHL creates calendar event on Neal's Google Cal
4. Slack notification fires to #booked-calls channel
5. **Pre-call brief auto-generated** (planned): Cara dossier + lead's reply history + suggested talking points
6. Call happens, outcome logged to CRM

### Tools

- GoHighLevel (booking + CRM)
- Slack (notifications)
- Google Calendar (calendar source-of-truth)
- Notion (post-call notes)

---

## 11. Stage 8 — Metrics Loop

**Goal:** Surface what's working, kill what isn't, feed insights back into Stage 3.0.

### Metrics tracked

| Per niche, per variant, per day | Source |
|---|---|
| Sends | Smartlead `/statistics` |
| Opens | Smartlead |
| Clicks | Smartlead |
| Replies | Smartlead + reply classifier |
| Bounces | Smartlead |
| Positive replies | Reply classifier |
| Booked calls | GHL + Slack |
| Cost per booked call | $$ spent / calls |

### Verdicts

- **HEALTHY** — reply > 0.8%, bounce < 5%, sent > 100
- **ITERATE** — outside thresholds
- **WAIT_FOR_DATA** — < 100 sends

### Dashboard

- **Lovable** front-end (dark mode, Bloomberg-meets-Linear vibe)
- **FastAPI** backend (`metrics_api.py` on port 8788)
- **Cloudflare Tunnel** for public exposure
- **Endpoints:** /dashboard/summary, /metrics/today, /metrics/7d, /metrics/niche/{niche}, /variants/performance, /leads/recent, /spend, /campaigns

### Nightly Council review

Runs at 1 AM ET. Aggregates day's metrics. Council picks winning variants per niche. Adjusts weight in Stage 3.0 strategy decisions (slightly downweights losers, upweights winners). All decisions logged to `/tmp/council/decisions/<date>.json`.

---

## 12. Tech stack overview

```
┌─────────────────────────────────────────────────────────┐
│  DISCOVERY                                              │
│  - Apify Google Maps Scraper (compass~crawler-google)   │
│  - n8n (Daily Apify Niche Scrapes workflow)             │
│  - Acquisity (manual CSV imports)                       │
├─────────────────────────────────────────────────────────┤
│  ENRICHMENT + AI                                        │
│  - OpenRouter (ALL LLM calls — UNIVERSAL RULE)          │
│    └ Gemini 2.0 Flash (Council writes, Cara research)   │
│    └ Sonnet 4.5 (judges, classifiers)                   │
│    └ Gemini 3 Pro Image (mockups)                       │
│  - Playwright (site scraping + tech stack detect)       │
├─────────────────────────────────────────────────────────┤
│  STORAGE + DB                                           │
│  - Smartlead (lead DB + sequence engine)                │
│  - Smartlead custom_fields (personalization vars)       │
│  - Local: ~/.council/ (logs, decisions, cache)          │
├─────────────────────────────────────────────────────────┤
│  HOSTING                                                │
│  - intakebot.vercel.app (Variant A magnet)              │
│  - flowops-assets.vercel.app (Variant C mockups + team) │
│  - flowoperations.ai/flowscore (Variant B magnet)       │
│  - Lovable (dashboard)                                  │
├─────────────────────────────────────────────────────────┤
│  AUTOMATION + INTEGRATIONS                              │
│  - Smartlead webhooks (EMAIL_REPLY)                     │
│  - Cloudflare Tunnel (expose local FastAPI)             │
│  - n8n (Apify cron, Cara enrichment chains)             │
│  - GoHighLevel (booking + CRM)                          │
│  - Slack (notifications)                                │
└─────────────────────────────────────────────────────────┘
```

---

## 13. Cost model

### Monthly recurring (current)

| Item | Cost | Notes |
|---|---|---|
| Smartlead | $97/mo | Pro plan, 10 inboxes |
| OpenRouter | $30-80/mo | Variable (Gemini Flash for most calls) |
| Apify | $60-90/mo | At 150 leads/day |
| Variant C mockups | $40-200/mo | Variable: $0.06 × Variant C sends |
| Vercel | $0 | Free tier for static hosting |
| n8n | $20/mo | Starter |
| GHL | (Neal's existing) | Reused |
| **Total** | **~$250-500/mo** | At 400 sends/day scale |

### Cost per booked call (realistic tier)

- $400/mo total cost ÷ 90 calls/mo = **~$4.50 per booked call**
- Industry benchmark: $50-200 per qualified call via paid ads
- **Outbound moat:** 10-40× cheaper per call than paid

### Cost-to-revenue ratio

- $400/mo cost vs $135-270K/mo revenue = **0.15-0.30% cost ratio**

---

## 14. Runbooks

### Morning check (every day, 8 AM ET)

```bash
cd ~/Desktop/council
python3 morning_check.py
```

Outputs: lead counts per campaign, % with empty personalization, send window status.

### Pre-gen mockups for tomorrow

```bash
cd ~/Desktop/council
.venv-server/bin/python mockup_batch_run.py
```

~$5 cost, ~15 min runtime, populates 80-120 mockups.

### Acquisity import

```bash
cd ~/Desktop/council
python3 bulk_import.py ~/Downloads/<acquisity_file>.csv --niche RECRUITER
```

### Restart auto-reply tunnel + server

```bash
# Kill old tunnel
pkill -f cloudflared

# Start fresh
nohup .venv-server/bin/uvicorn webhook_server:app --port 8787 > ~/.council/webhook.log 2>&1 &
nohup cloudflared tunnel --url http://127.0.0.1:8787 > ~/.council/tunnel.log 2>&1 &

# Get new URL
grep -oE "https://[a-z0-9-]+\.trycloudflare\.com" ~/.council/tunnel.log | tail -1
```

### Restart metrics API + tunnel for Lovable

```bash
nohup .venv-server/bin/uvicorn metrics_api:app --port 8788 > ~/.council/metrics_api.log 2>&1 &
nohup cloudflared tunnel --url http://127.0.0.1:8788 > ~/.council/metrics_tunnel.log 2>&1 &
```

### Pause a misbehaving campaign

```python
import urllib.request, json
KEY = "..."
cid = 3263730  # WEALTH
url = f"https://server.smartlead.ai/api/v1/campaigns/{cid}/status?api_key={KEY}"
req = urllib.request.Request(url, data=json.dumps({"status":"PAUSED"}).encode(),
    headers={"Content-Type":"application/json"}, method="POST")
urllib.request.urlopen(req).read()
```

---

## Glossary

- **Variant** — One of 4 magnet types (A/B/C/D) split-tested at Stage 3.5
- **Niche** — A vertical / ICP segment (WEALTH, FINANCIAL, etc.)
- **Persona inbox** — One of 10 Smartlead sender inboxes (each is a real Gmail account on a warmed domain)
- **Cara** — AI research agent persona (`hello@carabarone.com`) used in forwarded-research email format
- **Council** — The 12-persona + 5-judge LLM ensemble that writes per-lead copy
- **FlowScore** — 0-100 ops audit score from flowoperations.ai/flowscore (Supabase Edge Fn)
- **OpenRouter** — Universal LLM gateway. ALL FlowOps LLM calls route through here (hardcoded rule)
