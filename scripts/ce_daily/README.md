# Cold Email dashboard — daily update

Updates every tab of `flowoperations.org/cold-email-system` (Lovable project `d3ba2f70…`) once a day.
Scheduled task: **Cold email dashboard daily update**, 7:23 AM Central, every day.

## Data flow
1. Smartlead via n8n gateway `vLADM6PiJ14ItZsv` ("SL Request"): campaign analytics, per-email statistics, email accounts.
2. `metrics.py <saved_execution.json> <YYYY-MM-DD> <out.json>` computes per-campaign leads/emails, human opens
   (first open ≥120 s after send), replies, bounces, and the E1 subject leaderboard.
3. Replies: B30 pipeline (`TH6uS1Phh8jZCmTG`) + reply dataset; only human replies count (no auto-replies/OOO/tickets).
4. `tabs_template_*.py` shows the structure written to `ce_tab_updates` (one row per tab: headline, kpis, body_md, tables),
   plus `ce_status` keys `headline`, `leads_ready`, `last_reviewed`, `open_items`, `campaigns` (drives `engine-live`).

## Alert checks (every run)
- 9 sending inboxes `message_per_day == 35` (dropped to 5 on 2026-11-12; restored)
- warmup reputation ≥ 98%, no warmup block, SPF/DKIM/DMARC verified
- campaigns ACTIVE, notStarted runway ≥ 1 day
- Apify token valid (401 on 2026-11-12)
