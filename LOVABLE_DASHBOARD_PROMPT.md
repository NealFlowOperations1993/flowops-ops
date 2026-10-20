# Lovable Build Prompt — FlowOps Live Dashboard

Paste this into your "Flow Operations Architect" Lovable project. It'll build the dashboard in one pass.

---

## THE PROMPT (paste verbatim into Lovable)

```
Build me a single-page dark-mode operations dashboard for FlowOperations.ai cold email pipeline.

DESIGN SYSTEM:
- Background: hsl(222 47% 4%)
- Primary: #3B82F6, secondary glow accents #22D3EE + #A855F7
- Display font: Space Grotesk
- Mono font: Fira Code
- Vibe: Bloomberg terminal meets Linear. Sharp 4-6px border radii max.
- Big numbers, tight tables, live-feeling counters that update every 30 sec.

DATA SOURCE:
All data comes from a single REST API. Set the base URL as a placeholder I can fill in:
  const API_BASE = "https://REPLACE-WITH-TUNNEL-URL.trycloudflare.com";

Endpoints to fetch:
  GET ${API_BASE}/dashboard/summary   — one-shot, returns everything below
  GET ${API_BASE}/metrics/today
  GET ${API_BASE}/metrics/7d
  GET ${API_BASE}/campaigns
  GET ${API_BASE}/spend
  GET ${API_BASE}/leads/recent
  GET ${API_BASE}/metrics/niche/{niche}

Poll /dashboard/summary every 30 seconds. Show a subtle pulse animation on the
"Live" indicator each refresh.

LAYOUT (top-to-bottom):

1. HEADER ROW (60px tall):
   - Left: "FlowOps" logo + "Live Dashboard" title
   - Right: live pulse dot + "Last updated: <relative time>" + "Refresh" button

2. KPI ROW (4 big number tiles in a single row):
   - Sends today    (large number, today's totals.sent)
   - Replies today  (totals.reply)
   - Calls booked   (calculate from clicks * 0.7 as proxy until GHL webhook live)
   - Spend today    ($ from spend.openrouter.today + spend.apify.month_usage/30)
   Each tile: muted background, big number, tiny label, % vs yesterday in green/red.

3. 7-DAY METRICS TABLE (full width):
   columns: NICHE | STATUS | SENT | OPEN% | REPLY% | CLICK% | BOUNCE% | VERDICT
   Sort by reply % desc. Color verdict badges:
     HEALTHY = green chip
     ITERATE = yellow chip
     WAIT_FOR_DATA = grey chip
   Click a row → expands to /metrics/niche/{niche} detail panel below.

4. CAMPAIGN STATUS GRID (cards):
   For each niche from /campaigns: card with
     - Niche label, big
     - Status (ACTIVE/PAUSED) as a colored chip
     - Lead count (big monospace number)
     - Sparkline of last 7d sends (small SVG)

5. RECENT ACTIVITY FEED (right side, sticky):
   Last 20 from /leads/recent
   Each row: niche tag, lead name, action (replied/clicked), relative time
   Highlight any reply with subtle blue glow.

6. SPEND SECTION (footer band):
   3 columns: OpenRouter (today/week/month), Apify (today/month/limit), Smartlead (subscription note).
   Tiny bar chart for OpenRouter monthly trend.

INTERACTIVITY:
- Hovering a metrics row: subtle highlight
- Clicking a niche row: opens detail panel showing today/7d/30d comparison
- Recent activity feed: clicking a lead opens a Slack-style sidebar with that lead's full data

MOBILE:
- Stack everything vertically below 768px
- KPI tiles become 2x2 grid

DO NOT use chart libraries. Use simple SVG sparklines + native CSS for bars. No D3, no Chart.js.

DO NOT include authentication. API has no auth, dashboard is for internal use only.

Generate the full project with Next.js 15 + Tailwind v4 + TypeScript.
```

---

## Steps to deploy

1. Open Lovable → "Flow Operations Architect" project
2. Paste the prompt above into a new chat
3. Wait ~2 min for Lovable to build
4. Once built, click the chat-bubble icon → ask: "Replace API_BASE with https://<my-tunnel-url>"
5. Click "Connect Domain" → optional: link to dashboard.flowoperations.ai
6. Done

## Getting the API URL (Cloudflare Tunnel — 5 min setup)

The metrics API runs locally at `http://127.0.0.1:8788`. To expose it publicly for Lovable:

```bash
# Install once
brew install cloudflared

# One-time auth
cloudflared tunnel login

# Persistent tunnel (recommended for long-term)
cloudflared tunnel create flowops-metrics
cloudflared tunnel route dns flowops-metrics metrics.flowoperations.ai
cloudflared tunnel run --url http://127.0.0.1:8788 flowops-metrics
```

You get `https://metrics.flowoperations.ai` permanently pointing at the local API.

**OR** for instant ephemeral testing (no auth):
```bash
cloudflared tunnel --url http://127.0.0.1:8788
```
Spits out a random `https://xxx-yyy-zzz.trycloudflare.com` URL — paste into Lovable.

## Operational notes

- API runs on the Mac as a uvicorn process. To make persistent:
  ```bash
  cd ~/Desktop/council
  nohup .venv-server/bin/uvicorn metrics_api:app --host 0.0.0.0 --port 8788 > ~/.council/metrics_api.log 2>&1 &
  ```
- To restart after Mac reboot, add to crontab `@reboot`
- To deploy to Vercel instead (more reliable long-term), wrap the FastAPI in Vercel's serverless adapter (~30 min migration)

## Apify daily cron (live)

n8n workflow `Daily Apify Niche Scrapes (FlowOps)` is now active. Fires daily at 6 AM ET, rotates 3 niches per day across the 12-niche queue:

| Day | Niches scraped |
|---|---|
| Sun / Thu | MCA · MEDSPA · PI_LAW |
| Mon / Fri | WEALTH · MORTGAGE · INSURANCE |
| Tue / Sat | COMMLOAN · AGENCY · TAX_RES |
| Wed | RECRUITER · IT_MSP · FINANCIAL |

Each scrape: 5 cities × 50 leads = 250 per niche per day. **~750 fresh leads/day total** for ~$2-3/day Apify spend.
