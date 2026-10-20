# EXTRACTION.md — Cold Email Lovable Tabs → Consolidated Rebuild
Generated 2026-08-25 from /Users/nealthakkar/Desktop/council/lovable-backup-cold-email
Backup status: 27 files present. MISSING: `src/data/coldEmailAugust2026.ts` (holds ALL 22-stage content for the August-2026 page — CATEGORIES, STAGES, FEEDBACK_LOOPS). Back it up before destroying the Lovable project or that content is gone.

Live-engine baseline used for comparison: Smartlead campaigns 3842105 (hardscaping/estimator) + 3845617 (deck/booking page); 500/day, 50/inbox, 10 inboxes on flowoperations.org + flowopsleadgen.com; 3-email seq day 0/3/7; 10-variant split (5 subjects x give/ask); n8n B30 reply pipeline (Claude classifier + call push), Budget Guard $20/day, VOC Miner (5000-datapoint gate; deck_builder 7142 met, hardscaping 583), Lead Engine v1 (OnlineJobs/Skool/EDGAR), 6pm Slack digest, tool-lead capture webhook, qual-call threading; Apify datasets fo-replies/fo-voc-datapoints/fo-suppression-log/fo-leads-scored + KV ledger; tools = patio estimator + booking page on flowops-assets.vercel.app/tools/; deterministic 7-finding site-scan openers (no LLM).

---

## 1. FULL CONTENT LEDGER

### TAB A — "War Machine" Cold Email Playbook (/cold-email, built Apr 2026)
Shell: ColdEmailPage.tsx (router, 960px content) + ColdEmailSidebar.tsx (16 sections, "FLOWOPERATIONS / War Machine / Cold Email Playbook", "BUILT APR 2026").

**01 Overview (OverviewSection.tsx)** — "8 stages. Fully automated. $49/month." SCRAPE (Apify: LinkedIn/Apollo/Google Maps/Crunchbase 24/7, founder name/email/company/title) → FILTER (n8n ICP scoring: title/size/email format) → VERIFY (SMTP handshake, "zero bounces") → PERSONALIZE (Claude Haiku custom first line) → LOAD (n8n→Smartlead API, "no manual imports ever") → SEND (20+ warmed inboxes, 70-100/day/inbox, rotating domains) → REPLY (intent-keyword classification → GHL opportunities) → CLOSE (call → software demo → close). "It feeds you leads forever."

**02 Tech Stack (StackSection.tsx)** — 9-layer table: Apify $49/mo NEED; n8n self-hosted $0 HAVE; Debounce/Millionverifier $10/5K NEED; Smartlead HAVE; Aerosend $120+/mo PHASE 3; GoHighLevel HAVE; Claude API Haiku ~$5/10K NEED; Namecheap domains $1-2/yr BUY NOW ("NEVER your primary domain"); n8n+Slack monitoring $0 BUILD. Budgets: April $49; May $70-100; June+ $170-220.

**03 Pipeline (PipelineSection.tsx)** — 8-stage table w/ pass rates: SCRAPE 100% (~100K raw/mo at scale); FILTER 40-60% (n8n code node); DEDUPE 95%+ (vs Smartlead); PERSONALIZE 100% (Claude Haiku); VERIFY 70-80% Debounce (~25-40K verified/mo); PUSH 100%; SEND 50%+ open; ROUTE 1-5% reply → GHL. Plus ASCII n8n diagram: Apify Dataset Webhook → Fetch Dataset Items → ICP Filter → Dedupe → AI Personalization → Debounce Verify → Drop invalid → Push to Smartlead → Slack notify.

**04 Phases (PhasesSection.tsx)** — P1 "Test Fire" (Apr): 1,000 emails, 3 domains, 6 inboxes, ~45/day, $49, KPI = 1 close. P2 "Engine On" (May): 12,000, 6 domains, 12 inboxes, ~545/day, $100-200, KPI cost/booked-call <$5, add Aerosend if burning, 3-5 closes. P3 "Compound" (Jun-Sep): 24-60K, 10-22 domains, 20-44 inboxes, 1-2.7K/day, KPI reply-to-close >15%, Aerosend private infra, hire setter, 10-20 closes/mo. P4 "War Machine" (Oct-Dec): 72-96K, 26-34 domains, 52-68 inboxes, 3-4.3K/day, KPI "$577K/mo pipeline from $49 infra", SDR team, 40-77 closes/mo. (ONLY record of these projections.)

**05 Domains (DomainsSection.tsx)** — "Never send cold email from your primary domain. Ever." 4 naming patterns w/ examples (growthsync.co, flowops-hq.com, agencytools.co, getresults.io — illustrative, not owned). Exact DNS values (TTL 3600): SPF `v=spf1 include:_spf.smartlead.ai ~all`; DKIM host `smartlead._domainkey`; DMARC `_dmarc` `v=DMARC1; p=none; rua=mailto:dmarc@yourdomain.com`. Verify via mxtoolbox.com/spf + mail-tester.com.

**06 Warmup (WarmupSection.tsx)** — 5-phase ramp: D1-7 0 real/5-20 warmup; D7-14 5-10 real; D14-21 15-25; D21-28 40-60; D28+ 70-100 real + 20 warmup. Plus dated April launch timeline (buy 3 domains day 1 … full sends day 28+).

**07 ICP & Scraping (ICPSection.tsx)** — ICP: Founder/Owner/CEO/Co-Founder/President; 1-50 employees (exclude 51+); $30K-500K/mo revenue signal; US-first; work email only (drop gmail/yahoo/hotmail); verticals Agencies/SaaS/E-comm/Med Spa, one vertical per campaign. Source table: LinkedIn scraper 200-500/run 4★; Apollo 500-1000/run 5★ "best emails+firmographics"; Google Maps 500-2000/run 3★; Crunchbase 100-300/run 4★.

**08 Email Copy (CopySection.tsx)** — 3-email framework w/ full copy: E1 Hook (Day 1, 3 subject variants: "quick question about {companyName}" / "built something for {industry}" / "{firstName} — 2 min?"; body w/ {personalizedOpener} + "Worth a 5-minute look?"); E2 Follow-up (Day 3-4, "re:" subject, [Client X] proof); E3 Breakup (Day 7, "closing the loop", "looks like you're building something real"). 8 rules: NEVER "AI" in subject / >3 emails / >1 CTA / >5 lines; ALWAYS first name in E1 / mention company+vertical / peer-not-vendor tone / test 3+ subjects.

**09 The Offer (OfferSection.tsx)** — Agency vs Builder positioning ($2-5K ceiling vs $10-50K+ floor, days-not-months via Claude Code). 5 vertical products: AgencyOS, MedSpa Suite, AgentFlow, CoachOS, StoreEngine — w/ aspirational proof claims (40% less churn, 50% fewer no-shows, +23% LTV — placeholders, not real data).

**10 Projections (ProjectionsSection.tsx)** — Apr-Dec table: Apr 1,000 emails/$0-10K … Aug 48,000/$200-380K … Dec 96,000 emails / 23-77 closes / $577K+ realistic. Hero: "$577,500/month from a $49/month infrastructure." Callouts: DELIVERY CONSTRAINT (10 closes = 10 builds; Claude Code + vertical templates; dev retainer by May); COPY TAKES TIME (2-3 weeks to find converting copy).

**Growth Chart (GrowthChartSection.tsx)** — AreaChart Apr 1K → Dec 96K (+12K/mo linear); phase cards 1K/12K/96K. Only record of Sep-Nov intermediates (60/72/84K).

**11 Deliverability (DeliverabilitySection.tsx)** — Traffic-light thresholds w/ red-zone actions: Bounce <2%/2-4%/>4% (pause domain); Spam <0.1%/0.1-0.3%/>0.3% (stop, audit copy); Open >40%/25-40%/<25% (test subjects); Reply >2%/1-2%/<1% (rewrite copy, refine ICP); Unsub <0.5%/0.5-1%/>1%. 10 deliverability killers (primary-domain sending, skipped verification, >2x/week volume jumps, spam words "guaranteed/free offer/act now", blast-then-silence, no SPF/DKIM/DMARC, 500+/day on one inbox, high image ratio, links in Email 1, purchased leads).

**12 Daily Ops (OpsSection.tsx)** — Interactive checklists w/ date-keyed localStorage: DAILY 5min/5 tasks (Slack briefing, positive replies, health alerts, inbox check, throughput); WEEKLY 30min/6 (rates per campaign/subject, pause losers, domain health, ICP accuracy, Apify runs, 2-week lead runway); MONTHLY 2hr/6 (full audit, buy+warm next month's domains, refresh copy, update ICP from closes, plan verticals, true CAC).

**13 Scaling (ScalingSection.tsx)** — 8 gated steps w/ numeric conditions: validate copy (open >35% AND reply >1.5% on 200+ sends) → validate ICP → validate offer (1 close) → scale inboxes (+3 domains per 12K emails/mo) → Aerosend (domains burn OR 30K+/mo) → AI personalization → hire setter → new vertical every 4-6 weeks. Closer: "The machine is simple. The discipline is hard."

**14 Claude Code Prompts (PromptsSection.tsx)** — 6 verbatim build prompts (~2hr total): (1) n8n core pipeline 10-node spec w/ env vars APIFY_API_TOKEN/SMARTLEAD_API_KEY/SMARTLEAD_CAMPAIGN_ID/DEBOUNCE_API_KEY/NOTIFY_WEBHOOK_URL; (2) Apify scraper configs — 6 JSON deliverables incl. vertical-search-queries.json; (3) Smartlead + copy — 3-email sequences per vertical + inbox-setup-checklist; (4) GHL reply routing; (5) AI personalization engine (Haiku, batches of 10, <$5/10K); (6) Dashboard + monitoring (daily-briefing.js 8am cron, health-checker.js 4h, master-runbook.md). Pre-build checklist: 3 Namecheap domains $3-6, Apify $49, Smartlead+GHL creds, n8n.

**Live Metrics (LiveMetricsSection.tsx)** — "Pipeline Command Center", usePipelineMetrics hook w/ mock fallback, claims 5-min Smartlead/GHL/Apify polling. Hardcoded thresholds: bounce green <2%/amber <4%; spam <0.1%/<0.3%; open >40%/>25%; cost/call green <$15. Tiles: today (leads/sent/opens/replies/pos.) + month (emails/calls/revenue pipe/cost/cost-per-call). "All systems nominal" empty state.

**Aux components** — VariantPerformanceGrid: A IntakeBot LIVE / B FlowScore WIRING / C Mockup LIVE+WINNER / D Direct Audit FRI, all zeros, decorative sparklines. CostPerCallCard: fallback $4.50, 90-day target $2.50, "vs $50-200 paid-ads benchmark". TargetMetricsBand: 90-day targets 600 leads/day, 1,100 sends/day, 3.0% reply, 250 calls/mo, $1M/mo revenue — trend data is Math.random FAKE. ProjectsBoard: Now/Next/Later kanban (FlowScore wiring, Variant B/D, Cloudflare tunnel; 25+ niches, Reddit/Twitter/Meta signals, persona photos, pre-call briefs, Acquisity; Cara n8n migration, assets.flowoperations.ai, auto-send, Council weight tuning, multi-tenant) — localStorage may hold user edits not in this source backup. Primitives: DataTable, SectionHeader, Highlight/Bullet (no data).

### TAB B — SOP Visualizer (/cold-email-sop, ColdEmailSOPPage.tsx, fully self-contained)
Describes the Supabase+OpenRouter+Council architecture (older/aspirational). 10 stages w/ overview/tech/runbook each:
- S1 Discovery LIVE — Apify+n8n $60-90/mo, 9 niches, 150+ raw leads/day, dedup vs Master DB, n8n "discovery-master", icp_niches table, leads.raw (Supabase).
- S2 ICP Filter LIVE — hard filters (revenue/headcount/geo) + soft LLM scorer gpt-5-mini, drops ~60%, /sql/icp_thresholds.sql, leads.qualified.
- S3 Signal Enrichment LIVE — Cara dossier chain (Gemini 2.5 Flash + GPT-5 mini), site crawl/tech stack/ad presence, dossier.md per lead, leads.dossier JSONB, POST /api/cara/refresh.
- S3.0 Strategy Council LIVE — gpt-5 agents Leonidas/Marcus/Brutus vote magnet variant A/B/C/D, council_votes table, POST /api/council/override.
- S3.5 Magnet Generation WIRING — Gemini 3 Pro $0.06/lead; variants A IntakeBot demo URL / B FlowScore API / C Mockup image / D direct audit; 77 mockups pre-gen $4.62; Variant D Friday rollout 25/25/25/25; magnet_runs table.
- S4 Copy Generation LIVE — gpt-5, 3-step sequence, persona-locked voice, QA pass, /prompts/copy_v3.md, emails.queued, POST /api/copy/regen.
- S5 Send LIVE — Smartlead $97/mo, 80-300/day ramping to 400, 4 AM ET push, persona signatures, webhook /api/smartlead/event.
- S6 Auto-Reply LIVE — classifier positive/nurture/no, drafts + books Cal.com, human-in-loop, FEATURE_AUTO_SEND env, reply_drafts, /internal/replies.
- S7 Booked Call LIVE — Cal.com webhook → booked_calls, pre-call brief auto-gen NEXT, /internal/calls.
- S8 Metrics Loop BUILDING — n8n+Postgres $20/mo, nightly council_weights re-tune, 5-min dashboard refresh.
KPIs: 150+ leads/day, 9 niches (25+ planned), 4 magnet variants, 77 mockups $4.62. 90-day ramp: leads 150/250/400/600; sends 200/400/700/1000; reply 3/5/7/9%; positive 0.8/1.5/2.5/3.5%; calls/day 1/3/6/10; calls/mo 22/66/132/220; revenue $15K/50K/110K/200K. Kanban NOW/NEXT/LATER (mirrors ProjectsBoard). Costs/mo: Smartlead $97, OpenRouter $30-80, Apify $60-90, Gemini mockups $40-200, Vercel $0, n8n $20; cost/booked-call $4.50 vs $50-200 benchmark; cost-to-revenue 0.15-0.30%. Architecture grid: Apify discovery / OpenRouter+Cara enrichment / Supabase storage / Vercel+Cloudflare hosting / n8n+Smartlead automation. Hero badge "LIVE — sending tomorrow 4 AM ET".

### TAB C — August-2026 System Map (/cold-email-august-2026, ColdEmailAugust2026Page.tsx)
Presentation shell only. In-file: title "Cold Email: August 2026", subtitle "complete cold-email operating system in 22 stages — from market selection and offer construction, through lead data, sending infrastructure, campaigns and reply handling, to revenue attribution, optimization loops and governance"; "Stages: 22" summary; philosophy: "The system is not a funnel, it is a circuit. Sales outcomes travel back upstream and rewrite ICP, source selection, offer, personalization, messaging and infrastructure decisions. Optimization is driven by downstream revenue truth — never by vanity opens." ALL stage/gate/KPI/loop content lives in the MISSING src/data/coldEmailAugust2026.ts.

---

## 2. EXTRACT LIST (worth adding to consolidated rebuild; slotted into 6-tab structure)

Target tabs: 1 Map+scores · 2 Metrics&Projections · 3 Leads · 4 VOC · 5 Workflows&Diagnostics · 6 Templates&Copy

**→ Tab 1 (Map + scores)**
- 22-stage circuit philosophy + quality-gate/KPI-per-stage framing (ColdEmailAugust2026Page.tsx + missing data file) — "revenue truth, not vanity opens" doctrine as the map's organizing principle. RECOVER the data file first.
- Swim-lane pipeline w/ clickable stage cards + Overview/Tech/Runbook tabs per stage (ColdEmailSOPPage.tsx) — best-in-batch pattern for the live-engine map; repopulate with REAL stages (Lead Engine v1 → scoring → Smartlead → B30 → call).
- Gated scaling sequence pattern w/ numeric proceed-conditions (ScalingSection.tsx) — re-derive gates from live reality (e.g. VOC 5000-datapoint gate as gate #1; hardscaping 583/5000 as a live score).

**→ Tab 2 (Metrics & Projections)**
- Deliverability traffic-light thresholds + red-zone actions (DeliverabilitySection.tsx) — bounce/spam/open/reply bands are industry-sane; adopt as-is, corrected to the live 50/inbox cap.
- Live metrics dashboard patterns (LiveMetricsSection.tsx): live/mock status bar, threshold-colored health cards, severity alerts — rewire to Smartlead API + Apify KV ledger (not GHL); keep bounce/spam/open thresholds.
- Rebased projection model (ProjectionsSection.tsx / PhasesSection.tsx structure only) — the volume→reply→call→close waterfall table format is right; rebuild rows from live 500/day and actual campaign stats, not the $577K fantasy.
- Cost-per-booked-call as a KPI (CostPerCallCard.tsx) — worth actually tracking once calls exist; compute from Budget Guard spend / booked calls.
- Growth AreaChart + phase-milestone cards pattern (GrowthChartSection.tsx) — reuse for real send-volume history.

**→ Tab 3 (Leads)**
- One-vertical-per-campaign rule + work-email-only filter + founder-title filter (ICPSection.tsx) — codify as written lead-qualification rules for Lead Engine v1 output.
- 2-week lead-runway rule (OpsSection.tsx weekly item) — add as a Leads-tab warning metric (leads remaining ÷ daily send).
- Source-quality scorecard table pattern (ICPSection.tsx) — re-populate with OnlineJobs/Skool/EDGAR per-source yield+quality.

**→ Tab 4 (VOC)**
- Nothing directly (no tab had VOC content). Optional: "update ICP criteria from actual closes" monthly ritual (OpsSection.tsx) belongs here as the VOC→ICP feedback loop, matching the Aug-2026 circuit doctrine.

**→ Tab 5 (Workflows & Diagnostics)**
- Daily/weekly/monthly ops checklist component w/ localStorage daily reset (OpsSection.tsx) — most reusable component in the batch; rewrite tasks for the live engine (B30 health, Budget Guard, digest review, suppression log).
- Warmup ramp table as reusable SOP (WarmupSection.tsx) — generic 5-phase schedule + risk tiers, capped at 50/inbox, for any future domain/inbox expansion.
- Exact DNS records + verification tools (DomainsSection.tsx) — SPF/DKIM/DMARC values + mxtoolbox/mail-tester steps as the domain-onboarding runbook.
- 10 deliverability killers list (DeliverabilitySection.tsx) — keep 9 of 10 (drop "no links in Email 1", conflicts with live tool-link strategy; correct 70-100/inbox to 50).
- Deliverability incident actions (pause domain on >4% bounce etc.) — wire as documented responses next to the 6pm digest.
- ASCII/CopyBlock workflow-diagram pattern (PipelineSection.tsx) — document the REAL n8n workflows (B30, Budget Guard, VOC Miner, Lead Engine, digest) in this format.

**→ Tab 6 (Templates & Copy)**
- 8 NEVER/ALWAYS copy rules (CopySection.tsx) — codify; all 8 compatible with live copy.
- Breakup-email framing ("closing the loop", "looks like you're building something real") (CopySection.tsx) — candidate day-7 variant to test against live E3.
- Spam-word list ("guaranteed", "free offer", "act now") (DeliverabilitySection.tsx) — copy-QA checklist.
- Peer-not-vendor tone rule + subject-variant testing discipline (CopySection.tsx) — merge into variant-testing SOP for the 10-variant split.
- Claude Code build-prompts TAB PATTERN (PromptsSection.tsx) — keep the tabbed copy-paste-prompt UI, replace all 6 prompts with prompts that rebuild the LIVE engine components.

**UI patterns to carry (no data):** DataTable, SectionHeader, Highlight/Bullet, status Pill, sparkline Stat cards, KPI-strip w/ detail modals, drag-drop kanban w/ localStorage, checklist w/ progress bars, sidebar section registry (const-asserted SECTIONS + derived union type), scoped inline palette.

---

## 3. DISCARD LIST (stale/superseded — recorded here so nothing is lost silently)

**Architecture superseded by live engine**
- Entire Supabase/OpenRouter/Council stack (ColdEmailSOPPage.tsx): Supabase tables (leads.*, icp_niches, council_votes, magnet_runs, reply_drafts, booked_calls, council_weights), all /api/* and /internal/* endpoints, FEATURE_AUTO_SEND — live storage is Apify datasets + KV ledger.
- Strategy Council (Leonidas/Marcus/Brutus, gpt-5, nightly weight tuning) — no live counterpart.
- Cara dossier enrichment chain (Gemini 2.5 Flash + GPT-5 mini) + its n8n migration plan.
- 4-magnet variant system (IntakeBot, FlowScore, Mockup incl. 77 pre-gen batch $4.62, Direct Audit, 25/25/25/25 Friday rollout) — live = 2 real tools (patio estimator, booking page), 10-variant copy split.
- All LLM personalization/copy-gen: Claude Haiku openers, {personalizedOpener} merge field, gpt-5 copy_v3.md, personas, "AI personalization layer" scaling step — live is deliberately deterministic 7-finding site-scan, no LLM.
- GHL as reply/CRM destination (Overview, Pipeline, Prompts #4, Stack, Ops) — live = n8n B30 → call push.
- Cal.com booking + pre-call brief auto-gen — not in live stack.
- Debounce/Millionverifier verification layer — no verification vendor live.
- Apify as LinkedIn/Apollo/Google Maps/Crunchbase scraper (Overview, Pipeline, ICP sources, Prompts #2) — live Apify = storage; live sources = OnlineJobs/Skool/EDGAR.
- Aerosend private-IP infra (Stack, Phases, Scaling) — not in stack.
- Acquisity integration, assets.flowoperations.ai custom domain, persistent Cloudflare tunnel, persona signature photos, auto-send for high-confidence replies, multi-tenant client campaigns (ProjectsBoard/SOP kanban) — abandoned roadmap.

**Numbers superseded by live config**
- 70-100/inbox/day and 20+ inbox fleet (Overview, Warmup, Deliverability) — live cap is 50/inbox, 10 inboxes.
- 80-300→400/day, 4 AM ET push (SOP S5); 1,100 sends/day target (TargetMetricsBand) — live 500/day.
- 9→25+ niches, 150+ leads/day, ~100K raw/mo (SOP, Pipeline, ProjectsBoard) — live = 2 niches.
- Day 1/3-4/7 cadence + 3-subject-variant copy set (CopySection) — superseded by live day 0/3/7 + 10-variant split (framework rules extracted above; the specific copy is not the live copy).
- "No links in Email 1" rule — conflicts with live per-lead tool links.

**Pure fiction / dashboard theater**
- All zero-stat variant cards + decorative sparklines (VariantPerformanceGrid); Math.random 30-day trends (TargetMetricsBand); $4.50 fallback CPC + $2.50 target (CostPerCallCard); 5-min GHL polling claim (LiveMetricsSection).
- 90-day targets: 600 leads/day, 250 calls/mo, $1M/mo revenue (TargetMetricsBand); SOP ramp table to $200K/mo; War Machine Apr-Dec table to $577,500/mo, 96K emails/mo, 40-77 closes/mo, 26-34 domains, SDR team (Projections, Phases, GrowthChart) — aspirational, never validated; preserved in the ledger above, do not rebuild.
- Offer-section proof claims (40% churn, 50% no-shows, +23% LTV) + 5 named vertical products (AgencyOS etc.) — placeholder products, never built; live offer = free branded tools.
- "$49/month machine" cost framing; April/May/June budget lines (Stack) — stale.

**Stale timelines**
- April 2026 launch timeline (WarmupSection), all Apr-Jul month gates (ScalingSection), "sending tomorrow 4 AM ET" badge, "BUILT APR 2026" footer, ProjectsBoard ETAs ("tonight", "Fri 4am ET").

**Superseded validation gates**
- Copy/ICP/offer validation thresholds (open >35%, reply >1.5%, 1 close) — replaced by VOC Miner 5000-datapoint gate; kept in ledger as reference numbers only.
