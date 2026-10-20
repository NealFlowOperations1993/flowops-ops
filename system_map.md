# FlowOperations n8n System Map — exaltisgroup instance

Generated 2026-08-23. 112 workflows total, 38 active. Credentials: `~/.config/n8n-creds/flowops-n8n.env`.

Legend: 🟢 = active, ⚪ = inactive. Workflows marked **[DO NOT TOUCH]** are read-only (`modifiable: false`) — copy patterns out of them, never edit them in place.

## COLD EMAIL (Brutus / FlowOps lead engine)

### 🟢 B30 Reply Pipeline
- **id:** `TH6uS1Phh8jZCmTG`
- **trigger:** webhook /brutus-reply
- **services:** smartlead.ai, anthropic, supabase, apify, slack
- **purpose:** Smartlead EMAIL_REPLY webhook: parses reply, Claude classifies intent (POSITIVE_HIGH..SPAM, JSON with confidence + suggested reply), inserts reply row and handles unsubscribe suppression in Supabase (brutus schema), auto-sends Smartlead reply only if POSITIVE_HIGH & confidence>=0.90 & thread_position>=2, scrapes company site/news signals (Apify rag-web-browser + direct fetch), posts rich Slack card and stores thread ref back to Smartlead lead. Note: hardcoded Anthropic, Smartlead, Apify, and Supabase service-role keys live in code nodes.

### 🟢 Cold Email Lead Generation Pipeline
- **id:** `0qkPeKHq1siM4yh5`
- **trigger:** /apify-lead-pipeline (webhook, fired by Apify run-completed)
- **services:** apify.com, smartlead.ai, supabase.co, openrouter, slack
- **purpose:** On Apify run completion, fetches the dataset, filters leads against ICP and detects niche, checks Supabase suppression, generates OpenRouter personalization, mirrors leads to Supabase and pushes to Smartlead campaigns, then Slack-notifies.

### 🟢 Qualification Call Booked — Slack Notification + Research
- **id:** `WNE56YhjuWqmjfAO`
- **trigger:** /qualification-call-booked
- **services:** slack, smartlead.ai
- **purpose:** GHL appointment webhook → extracts lead/appointment data, looks up the lead's Smartlead custom fields (slack_message_ts/slack_channel) to find the original reply thread, and posts a Block Kit call card into that Slack thread (fallback channel C0AMW0J3X6X).

### 🟢 Smartlead → Slack: New Lead Notification
- **id:** `c6g1Sjv2yab4OFKD`
- **trigger:** webhook /a5b4c001-1f84-4f37-8167-01d9fb93c3af (Smartlead webhook)
- **services:** smartlead.ai (inbound webhook), slack
- **purpose:** Receives a Smartlead event via webhook and posts a new-lead notification to Slack. Two nodes: Webhook → Slack.

### ⚪ Apify Rotation Dispatcher - 400 Leads/Day
- **id:** `v4qtQEozBVJ7wkFc`
- **trigger:** cron 0 11 * * * (daily 6AM ET)
- **services:** smartlead.ai, apify, exaltisgroup n8n webhook (apify-lead-pipeline)
- **purpose:** Daily gate: checks Smartlead for >=5 ACTIVE-warmup mailboxes, then deterministically rotates 4 niche/city pairs (10 niches x 10 cities, day-of-year offset) and fires Apify google-maps-with-contact-details runs (100 places each) with ACTOR.RUN.SUCCEEDED/FAILED webhooks pointed at /apify-lead-pipeline.

### ⚪ B01 — Hiring Ops Signal Scraper
- **id:** `ZgoPlGB1dlkheTlL`
- **trigger:** 0 6 * * *
- **services:** apify.com, supabase.co, slack
- **purpose:** Daily runs Apify Indeed scraper (misceres~indeed-scraper) across 5 ops-role queries with async start→poll→dataset-fetch, parses/filters postings for ops-hiring signals, dedupes and inserts into Supabase signals table, posts a Slack daily report.

### ⚪ B11 — Enrichment + Suppression
- **id:** `fPkU2gxayKtHLfdF`
- **trigger:** webhook /brutus-enrich (POST) + hourly cron 0 * * * *
- **services:** supabase.co (brutus schema signal_events), findymail/apollo/anymailfinder/hunter/millionverifier (waterfall — keys are PASTE_ placeholders, not wired), slack, n8n webhook forward to /brutus-push (B22)
- **purpose:** Brutus pipeline stage: pulls pending signal_events from Supabase, marks them enriching, runs an email-enrichment waterfall (Findymail→Apollo→Anymailfinder→Hunter→MillionVerifier), persists results with suppression/no-email filtering, forwards ready contacts to B22 via /brutus-push, and posts a Slack report. Waterfall API keys are unfilled placeholders.

### ⚪ B22 — Smartlead Push
- **id:** `aIXwzranxRF3krQn`
- **trigger:** /brutus-push
- **services:** smartlead.ai, supabase.co, slack
- **purpose:** Brutus push webhook (responds 202 immediately) → validates contacts require smartlead_campaign_id/sequence_id, checks Supabase is_suppressed RPC per contact, groups allowed leads by campaign in batches of 100, POSTs to Smartlead campaigns/{id}/leads, writes send events + marks signals sent in Supabase, logs suppressed, Slack batch report.

### ⚪ B22 — Smartlead Push
- **id:** `xXlxFQFF86lX2Ykj`
- **trigger:** webhook /brutus-push
- **services:** smartlead.ai, supabase, slack
- **purpose:** Receives lead batches (responds 202 immediately), validates/expands, runs Supabase RPC is_suppressed per lead, pushes allowed leads to Smartlead campaign /leads endpoint in batches of 100, writes send_events, marks signal events sent, logs suppressed leads, Slack summary.

### ⚪ Cold Email Lead Generation Pipeline
- **id:** `ZU82mBlxlxS0rLRv`
- **trigger:** /apify-lead-pipeline
- **services:** apify.com, smartlead.ai (payload built, push node not connected)
- **purpose:** Apify run-finished webhook → fetches the run's dataset, filters leads by ICP (decision-maker titles, blocks role emails, company_size<200), normalizes fields into Smartlead lead schema, batches, builds Smartlead payload — final push node intentionally not connected ('Create a Smartlead campaign then connect the Push node').

### ⚪ Cold Email Lead Intake Pipeline
- **id:** `NvQC9GvwVJXtxefG`
- **trigger:** webhook /leads-intake
- **services:** google sheets
- **purpose:** Receives a leads array via webhook, responds 200 immediately, splits, dedupes, normalizes fields in a code node, filters to has-email, and appendOrUpdates rows into a Google Sheet (doc 1c3nAyqgji..., tab Leads).

### ⚪ Daily Apify Niche Scrapes (FlowOps)
- **id:** `QVMajRvX1TKB7r0d`
- **trigger:** cron daily at hour 11 UTC (6 AM ET)
- **services:** apify.com
- **purpose:** Daily schedule fires a code node that kicks off Apify niche scrape runs (lead sourcing for FlowOps).

### ⚪ FlowOps Backfill Personalization
- **id:** `IKbHDsYF7ifcXVbT`
- **trigger:** cron */10 * * * *
- **services:** smartlead.ai, anthropic
- **purpose:** V1 monolith of the personalization backfill: single code node with hardcoded Smartlead + Anthropic API keys, 10 campaign IDs, niche labels, and the founder-tone 9-key personalization system prompt; fetches, personalizes, and updates leads inline. Superseded by V2. NOTE: live API keys are hardcoded in the code node.

### ⚪ FlowOps Backfill Personalization V2
- **id:** `I9knmvWukp2PKlCF`
- **trigger:** cron */10 * * * *
- **services:** smartlead.ai, anthropic, slack
- **purpose:** Every 10 min, loops Smartlead campaigns, fetches leads with cursor persistence, calls Anthropic (tool-use) to generate 9 personalization variables per lead, validates keys, PATCHes the lead back into Smartlead, and Slack-alerts on failures.

### ⚪ FlowOps · Phase 0 — Lead Generation (Apify → Smartlead + Reply→Slack)
- **id:** `61ZkxnoZBrYOGfZK`
- **trigger:** cron: every 6 hours (sourcing branch) + /smartlead-reply (webhook, reply branch)
- **services:** apify.com, smartlead.ai, slack
- **purpose:** Earlier-gen lead engine: loops configured niches, scrapes each via Apify run-sync, maps to Smartlead lead schema, POSTs to campaign; separate branch receives Smartlead reply webhooks and posts to Slack.

## NUCLEUS — W-SERIES [READ-ONLY]

### 🟢 W02 — Live Call Ingest **[DO NOT TOUCH]**
- **id:** `7IELdwez8oHe1v13`
- **trigger:** /live-call-ingest (webhook)
- **services:** supabase.co, slack, n8n webhook chain (icp-synthesis)
- **purpose:** Ingests live-call transcripts: validates payload, saves to Supabase live_call_transcripts, updates client lifecycle row, triggers W03 ICP synthesis, Slack-notifies Neal.

### 🟢 W03 — ICP Synthesis (Claude Opus) **[DO NOT TOUCH]**
- **id:** `Xyx8OPuQEvB34ZPK`
- **trigger:** /icp-synthesis
- **services:** supabase.co, anthropic, slack
- **purpose:** Pulls client record, form submissions and call transcript from Supabase, builds an ICP-synthesis prompt, calls Claude, validates output, saves icp_docs row, updates client lifecycle, Slack-notifies Neal (missing fields or ready).

### 🟢 W12 - Hook Framework Tagger **[DO NOT TOUCH]**
- **id:** `uwWkVbjaFv5EL03E`
- **trigger:** webhook /hook-tagger
- **services:** anthropic, supabase, slack
- **purpose:** Webhook-triggered: builds a Claude prompt to tag raw corpus entries against the hook framework, parses tags, writes to corpus_entries_tagged, updates raw entry status, notifies Slack.

### 🟢 W13 - Weekly Corpus Synthesis **[DO NOT TOUCH]**
- **id:** `q4lFP1ccv9m4T6HE`
- **trigger:** schedule: weekly Monday 06:00 UTC
- **services:** supabase, anthropic, slack
- **purpose:** For each active niche in Supabase, pulls the week's tagged corpus entries, calls Claude to synthesize a weekly snapshot, saves to corpus_weekly_snapshots, reports to Slack.

### 🟢 W14 — Engine 1 Content Batch (Weekly) **[DO NOT TOUCH]**
- **id:** `wOnPobJNkux2t58X`
- **trigger:** schedule: weekly Monday 08:00 UTC
- **services:** supabase, anthropic, slack, n8n webhook (W20 output-delivery)
- **purpose:** Weekly: loops active content clients from Supabase, merges signed-off ICP doc + corpus snapshot, runs Claude Pass 1 strategy (with validation gate), Pass 2 drafting in batches of 5, Pass 3 validation, saves outputs and triggers W20 delivery; Slack alerts on completion/failure.

### 🟢 W15 — Engine 2 Cold Email Batch **[DO NOT TOUCH]**
- **id:** `Xzh21ax4GJ0y0GFG`
- **trigger:** /cold-email-batch
- **services:** supabase.co, anthropic
- **purpose:** For a client with cold_email engine active: fetches ICP doc + weekly corpus snapshot from Supabase, runs a 3-pass Claude chain (architecture → drafts → validate), assembles a cold-email sequence, saves to outputs table, then triggers W20 output-delivery webhook.

### 🟢 W16 — Engine 3 Ads Batch (Weekly) **[DO NOT TOUCH]**
- **id:** `4ayRollLDqc2i0Iy`
- **trigger:** cron: weekly Monday 08:00 UTC (plus manual webhook /ads-batch)
- **services:** supabase.co, anthropic, n8n webhook chain (output-delivery)
- **purpose:** Weekly per-client ad batch generation: pulls active paid-ads clients + ICP/corpus snapshot from Supabase, runs a 3-pass Claude chain (strategy → draft → validate), saves outputs to Supabase, triggers W20 delivery.

### 🟢 W17 - Landing Page Generator **[DO NOT TOUCH]**
- **id:** `s7amPRr1dbRP7FVW`
- **trigger:** webhook /landing-page-generator
- **services:** supabase, anthropic, slack
- **purpose:** On webhook, fetches client + ICP docs and latest corpus snapshot from Supabase, runs a 3-pass Claude chain (architecture, full copy, validation), saves the landing page to outputs and notifies Slack.

### 🟢 W20 — Output Delivery **[DO NOT TOUCH]**
- **id:** `tqalhKlrlE9Njyvq`
- **trigger:** webhook /output-delivery
- **services:** slack, supabase
- **purpose:** Receives a batch delivery request, routes by engine, posts deliverables to the client's Slack channel, marks outputs delivered and updates client first-batch timestamp in Supabase, notifies Neal.

### ⚪ Nucleus - Client Asset Transcription & Intelligence Extraction **[DO NOT TOUCH]**
- **id:** `Rmogbcmjui394rFm`
- **trigger:** NONE
- **services:** assemblyai, anthropic, google drive, google docs, google sheets, slack
- **purpose:** n8n form intake of client media assets; downloads from Drive, transcribes via AssemblyAI polling loop, runs Claude (Opus) structured extraction into a Nucleus doc, writes Google Doc + JSON to Shared Drive, appends registry row to Sheets, notifies Slack; error trigger posts to Slack.

### ⚪ Nucleus — Client vs Competitor Multi-Source Scrape **[DO NOT TOUCH]**
- **id:** `CS3hNOZCbXNBv4fk`
- **trigger:** webhook /nucleus-scrape
- **services:** apify.com, anthropic, supabase.co, slack, google drive
- **purpose:** Shared-secret-verified webhook takes client+competitor entities, uses an Anthropic agent to detect social platforms from each site, builds per-platform Apify scrape jobs (Reddit/IG/FB/Twitter with Reddit fallback actor), dedupes/filters, archives to Drive, ingests into Supabase nucleus-ingest edge fn, and posts a Slack digest.

### ⚪ W05 — Reddit Scraper **[DO NOT TOUCH]**
- **id:** `qbhw3TyP8A7Z89eV`
- **trigger:** webhook /scraper-reddit
- **services:** apify, supabase, slack
- **purpose:** Webhook-triggered: builds an Apify actor input, kicks off an Apify Reddit scrape run, records the pending run in Supabase scraper_runs, notifies Slack.

### ⚪ W06 — Review Sites Scraper **[DO NOT TOUCH]**
- **id:** `tSkTh2PdsFH2yFYq`
- **trigger:** webhook /scraper-reviews
- **services:** apify, supabase, slack
- **purpose:** Webhook-triggered: builds Apify request for review-site scraping, starts the run, saves pending run to Supabase scraper_runs, notifies Slack.

### ⚪ W07 — YouTube Scraper **[DO NOT TOUCH]**
- **id:** `2YaQs0YAz5AmDP0Z`
- **trigger:** /scraper-youtube (webhook)
- **services:** apify.com, supabase.co, slack, n8n webhook chain (hook-tagger)
- **purpose:** Runs Apify streamers~youtube-scraper via run-sync-get-dataset-items, parses results, saves to Supabase corpus_entries_raw, chains to the hook-tagger webhook, Slack notify. Content-engine corpus ingestion.

### ⚪ W09 — Ad Libraries Scraper **[DO NOT TOUCH]**
- **id:** `dRq9YbrOcHJnoGXr`
- **trigger:** webhook /scraper-ad-library (POST)
- **services:** apify (facebook-ads-scraper actor), supabase.co (scraper_runs table), slack
- **purpose:** Kicks off an Apify facebook-ads-scraper run for configured competitors, records the run in Supabase scraper_runs, notifies Slack. Part of the W-series content engine.

### ⚪ W10 — Competitor Landing Pages Scraper **[DO NOT TOUCH]**
- **id:** `nxTAfAmGN97szqOA`
- **trigger:** webhook /scraper-competitor-lps (POST)
- **services:** apify (website-content-crawler actor), supabase.co (scraper_runs), slack
- **purpose:** Kicks off an Apify website-content-crawler run against competitor landing pages, logs the run to Supabase scraper_runs, notifies Slack. W-series content engine.

### ⚪ W11 — Job Board Scraper **[DO NOT TOUCH]**
- **id:** `PMimK77BQxk0p6l8`
- **trigger:** webhook /scraper-job-board
- **services:** apify.com (misceres~indeed-scraper), supabase.co, slack
- **purpose:** Webhook-triggered: builds an Indeed search, kicks off the Apify Indeed scraper actor run, records the run in Supabase scraper_runs table, and notifies Slack. W-prefixed Nucleus infrastructure — read-only.

### ⚪ W17 — Landing Page Generator (older variant) **[DO NOT TOUCH]**
- **id:** `z9l9iL5u7cvFPYq1`
- **trigger:** webhook /landing-page-generator (same path as active s7amPRr1dbRP7FVW — inactive duplicate)
- **services:** supabase, anthropic, n8n webhook (W20 output-delivery)
- **purpose:** Older/inactive duplicate of W17: fetch client+ICP and corpus_snapshots from Supabase, 3-pass Claude LP generation, save to outputs and trigger W20 delivery.

### ⚪ W18 — Performance Ingest **[DO NOT TOUCH]**
- **id:** `DPFhUvwCvgWjYs4f`
- **trigger:** cron daily 02:00 UTC
- **services:** supabase.co, smartlead.ai, slack
- **purpose:** Daily pulls active clients from Supabase, for clients with the cold-email engine fetches Smartlead campaign stats (code node), saves performance_events rows to Supabase, and posts a Slack daily report.

## CONTENT ENGINE [READ-ONLY]

### 🟢 FlowOps - Slack Interactive Callback Handler **[DO NOT TOUCH]**
- **id:** `IbdX6AoHDqqb0czz`
- **trigger:** webhook /slack-interactive
- **services:** slack, heygen, leadconnectorhq/GHL
- **purpose:** Receives Slack interactive button callbacks, routes by callback type (video/carousel/animated approvals), on approval fetches the Slack thread, extracts the script, fires HeyGen video generation, and queues social posts via GHL social-media-posting accounts; posts acks/rejects back to Slack.

### 🟢 W01 - Async Form Handler **[DO NOT TOUCH]**
- **id:** `SF1vMrGgWpHCOKv2`
- **trigger:** webhook /async-form-handler
- **services:** supabase, slack
- **purpose:** Receives client async form submissions, upserts client record and saves submission to Supabase (uuhnhybmdsyzppiuhlvk), notifies Neal on Slack.

### 🟢 W04 - Niche Corpus Bootstrap **[DO NOT TOUCH]**
- **id:** `SY7yayRHbj4EZ06K`
- **trigger:** webhook /corpus-bootstrap
- **services:** supabase, n8n webhooks (reddit/youtube scrapers), slack
- **purpose:** Checks if a niche exists in Supabase; if new, creates the niche record and fans out to the Reddit and YouTube scraper workflows via internal webhooks, updates status, Slack-notifies; skips if existing.

### 🟢 W19 — ICP Refinement Review **[DO NOT TOUCH]**
- **id:** `TRaCvLxrTlVRYD9C`
- **trigger:** cron weekly Friday 09:00 UTC
- **services:** supabase, anthropic, slack
- **purpose:** Weekly loop over active signed-off clients: pulls 30-day performance_events and latest icp_docs from Supabase, has Claude propose ICP refinements, saves to icp_refinements, posts Neal a Friday briefing to Slack.

### ⚪ FlowOps - Daily X Auto-Publisher **[DO NOT TOUCH]**
- **id:** `MPljcl3qhizRKYch`
- **trigger:** webhook /x-auto-publish
- **services:** x/twitter (api.x.com), slack
- **purpose:** Webhook receives a batch of tweets, splits them, posts each to X via api.x.com/2/tweets, and confirms each in Slack.

### ⚪ FlowOps - Sunday X Scheduler 2026-04-19 **[DO NOT TOUCH]**
- **id:** `ayQkrol5VsAwW4nd`
- **trigger:** 10 one-shot crons (Apr 19-20, past — effectively dead)
- **services:** x/twitter api, slack
- **purpose:** One-off scheduler: 10 hardcoded date-specific cron triggers each post a tweet via api.x.com/2/tweets and confirm to Slack. Dates are past; effectively dead.

### ⚪ FlowOps Daily Content Pipeline **[DO NOT TOUCH]**
- **id:** `Z0XjGAnK7nbXvXc9`
- **trigger:** 0 7 * * *
- **services:** youtube data api, openai, slack
- **purpose:** Daily pulls YouTube trending videos, has OpenAI generate video scripts from them, posts to Slack. Early FlowOps content pipeline, inactive.

### ⚪ My workflow 5 **[DO NOT TOUCH]**
- **id:** `iJ8xFAcDxmmsUGIK`
- **trigger:** webhook /nucleus-submission
- **services:** notion
- **purpose:** Stub: webhook named 'Nucleus' → boilerplate code node (adds myNewField=1) → Notion database page update. Appears to be an unfinished Nucleus submission intake.

### ⚪ W08 — Short Video Scraper (TikTok) **[DO NOT TOUCH]**
- **id:** `SDajKtPcJmDYQkMz`
- **trigger:** webhook /scraper-short-video
- **services:** apify, supabase, slack
- **purpose:** Kicks off an Apify TikTok scraper actor run and records the pending run in Supabase scraper_runs table, then notifies Slack; async — a downstream workflow presumably harvests results.

### ⚪ W14 - Engine 1 Content Batch **[DO NOT TOUCH]**
- **id:** `ETqj4m7RnxG45QOu`
- **trigger:** cron Mondays 08:00 UTC (plus manual webhook /content-batch)
- **services:** supabase.co, anthropic
- **purpose:** Weekly per-client content batch: reads clients+ICP docs and corpus snapshot from Supabase, two-pass Claude generation (strategy then draft), saves outputs to Supabase and triggers W20 delivery webhook.

### ⚪ 🤖Content Creator Agent **[DO NOT TOUCH]**
- **id:** `6PBptEpybhdJh6eH`
- **trigger:** NONE (executeWorkflowTrigger — called by another workflow)
- **services:** openai, tavily
- **purpose:** Sub-workflow LangChain agent: GPT-4o agent with Tavily search tool that produces content when invoked by a parent workflow.

## CLIENT ONBOARDING (FlowOps internal)

### 🟢 1. Workflow B — PandaDoc Signed → Client Onboarding **[DO NOT TOUCH]**
- **id:** `2x7L7Y1LUJJ9NhV0`
- **trigger:** /pandadoc-signed (webhook)
- **services:** pandadoc (inbound webhook), slack, google drive, gmail
- **purpose:** On PandaDoc contract signed: creates client + internal Slack channels, invites client as guest and team members, builds a 4-subfolder Google Drive structure, sends Gmail welcome, posts welcome/notification messages; error branch to Slack.

### 🟢 2. Create Notion Database **[DO NOT TOUCH]**
- **id:** `dt5MJFlNERwybyXP`
- **trigger:** webhook /notion-database (POST); also errorTrigger → Slack
- **services:** notion, slack
- **purpose:** Numbered onboarding step: on webhook, reads a Notion database and creates a page via the Notion API; error trigger posts failures to Slack.

### 🟢 3. Client Onboarding: Trustpilot Competitor Watch **[DO NOT TOUCH]**
- **id:** `aa8bUwBHFAUlM3oz`
- **trigger:** /web-scraper
- **services:** apify.com, anthropic, google drive, slack
- **purpose:** GHL onboarding webhook with competitors → Apify run-sync scrapes Trustpilot, Google Reviews, Reddit; dedupes seen reviews, groups by competitor, Claude writes digest, saves summary doc to Google Drive, Slack-notifies; errorTrigger→Slack.

### 🟢 4. Brand Book Generator **[DO NOT TOUCH]**
- **id:** `YJIcdJIHijHjhbht`
- **trigger:** /brand-book-generator
- **services:** anthropic, google drive, slack, convertapi
- **purpose:** Onboarding webhook with client assets → downloads/converts assets (ConvertAPI PDF/SVG→PNG), Claude analyzes brand, composes brand-book HTML → PDF, saves to client Google Drive folder, Slack notifies; error trigger to Slack.

### 🟢 5. Fathom Meeting Transcript Reporter **[DO NOT TOUCH]**
- **id:** `U6PMw4v7vFFRDoUW`
- **trigger:** webhook /fathom-meeting (+ /fathom-action-complete for Slack interactivity)
- **services:** fathom (inbound), google drive, slack
- **purpose:** Fathom meeting webhook: resolves client, dedupes against Drive, creates transcript + summary Google Docs, posts meeting report to Slack with interactive action buttons whose callbacks update the Slack message; errors alert Slack.

### 🟢 Fathom → Notion Call Processing **[DO NOT TOUCH]**
- **id:** `8jTHkSHGGaCSiJln`
- **trigger:** webhook /d584dab4-df9d-4d51-944b-7459645cb767
- **services:** notion, slack, openai
- **purpose:** Receives Fathom call webhooks, runs an OpenAI agent to analyze the call, upserts a Notion call page (search→update or create), and posts onboarding calls to Slack #onboarding-call-notes.

### 🟢 Workflow B — GHL Onboarding Booked → Slack + Notion **[DO NOT TOUCH]**
- **id:** `7y0oWO7q5azteZtp`
- **trigger:** /ghl-onboarding-booked (webhook)
- **services:** leadconnectorhq/GHL (inbound webhook), slack, notion
- **purpose:** On GHL onboarding-call booking: invites team to client Slack channel, posts welcome, sets topic, creates a Notion client progress page.

### 🟢 Workflow C — Onboarding Form Submitted **[DO NOT TOUCH]**
- **id:** `2AEQUUpF7DOrsoOk`
- **trigger:** /onboarding-form (webhook)
- **services:** leadconnectorhq/GHL, slack
- **purpose:** Receives onboarding form submissions, derives intelligence-layer fields in code, PUTs the data onto the GHL contact, and posts summaries to the client Slack channel and internal team.

### ⚪ Client Onboarding - Slack Connect + Delegation Guide **[DO NOT TOUCH]**
- **id:** `cfRtWW5bHziZkAW2`
- **trigger:** NONE (n8n form trigger)
- **services:** slack
- **purpose:** On form submit: creates a Slack channel, sends a Slack Connect invite to the client, posts a welcome message and threaded tool-guide messages.

### ⚪ GHL Contract Tag — PandaDoc Draft Generator **[DO NOT TOUCH]**
- **id:** `vfOxPah68kHn0T0a`
- **trigger:** webhook /ghl-contract-trigger
- **services:** leadconnectorhq/GHL (inbound), pandadoc, slack
- **purpose:** GHL contract tag fires webhook; validates contact data, checks PandaDoc for an existing draft (dedupe), creates a PandaDoc draft if none, then posts contract link to #new-contracts in Slack.

### ⚪ Onboarding Workflow **[DO NOT TOUCH]**
- **id:** `Nm6LaCzIkqG7Nx3K`
- **trigger:** NONE (n8n form trigger)
- **services:** gmail, slack, openai, clickup, google drive
- **purpose:** Client onboarding on form submit: sends welcome email (Gmail), creates a company Slack channel + posts, extracts tasks from an uploaded PDF via a GPT-4o-mini agent with structured output, creates ClickUp folder/list/tasks, and creates a Google Drive client folder.

### ⚪ Onboarding — Stage 1: Trigger & Parse **[DO NOT TOUCH]**
- **id:** `n53aeRXo9ZEhbDeU`
- **trigger:** webhook /ghl-new-hire (POST)
- **services:** leadconnectorhq/GHL (inbound webhook), pandadoc, slack
- **purpose:** New-hire intake from GHL: validates/maps payload, creates a PandaDoc document from template, waits for processing, sends it for signature; Slack alerts on validation failure or doc-not-ready.

### ⚪ Onboarding — Stage 2: Signed Gate (webhook) **[DO NOT TOUCH]**
- **id:** `nM69a2OHKraAlbe0`
- **trigger:** webhook /pandadoc-completed (POST)
- **services:** pandadoc (inbound webhook), gmail, slack, google admin directory, leadconnectorhq/GHL, n8n user API (placeholder URL)
- **purpose:** On PandaDoc completion: verifies signature, sends Calendly link, Slack human-approval gate, then provisions the hire — creates Google Workspace user, emails credentials, invites to GHL and n8n, updates GHL contact status; logs rejects/ignored events to Slack.

### ⚪ Onboarding — Stage 2B: Unsigned Gate (webhook) **[DO NOT TOUCH]**
- **id:** `efjCOJiZaczbmJUX`
- **trigger:** cron 0 9 * * * (despite 'webhook' in name)
- **services:** pandadoc, gmail, slack
- **purpose:** Daily 9am sweep: lists PandaDoc docs in document.sent status, computes age, and for docs unsigned 2+ days sends a Gmail follow-up to HR and logs to Slack ops.

### ⚪ PandaDoc → Slack: New Contract Drafted **[DO NOT TOUCH]**
- **id:** `u4OkvNu3ZqxpIbuX`
- **trigger:** webhook /pandadoc-doc-created
- **services:** pandadoc (inbound webhook), slack
- **purpose:** Receives PandaDoc document_created events, filters to draft/uploaded docs, builds a Slack Block payload and posts to #new-contracts via chat.postMessage, verifying the response.

### ⚪ Paused: GHL->Webhook->Slack->GDrive->Password Vault Invite **[DO NOT TOUCH]**
- **id:** `8F1Tn4vEhB0ccedA`
- **trigger:** /8a80564c-e161-4208-8352-fddb7fcb794c (webhook, GHL-sourced)
- **services:** slack, google drive, gmail
- **purpose:** Older paused onboarding chain: webhook → parse company to channel name → create Slack channel + Drive folder → invite user → Gmail welcome → Slack Connect inviteShared. Superseded by Workflow B (2x7L7Y1LUJJ9NhV0).

### ⚪ Workflow A — GHL Contract Tag → PandaDoc Draft **[DO NOT TOUCH]**
- **id:** `6gIkvVNHbR16vMp2`
- **trigger:** /ghl-contract-tag (webhook)
- **services:** pandadoc, slack, leadconnectorhq/GHL (inbound webhook)
- **purpose:** On GHL contract tag: creates a PandaDoc document from template, waits for processing, sends for signature, Slack-notifies.

### ⚪ Workflow B — GHL Onboarding Booked → Slack Channel (NEW) **[DO NOT TOUCH]**
- **id:** `LsVRzEkpWfW912Qw`
- **trigger:** NONE
- **services:** none
- **purpose:** Empty shell — zero nodes in the dump; intended (per name) to create a Slack channel when a GHL onboarding call is booked, but nothing built.

### ⚪ Workflow B — PandaDoc Signed → Client Onboarding V2 **[DO NOT TOUCH]**
- **id:** `Zxu0n17m8j3L7u5I`
- **trigger:** /1b1a9d34-17f3-49ad-8630-303cb2dce45c (PandaDoc webhook)
- **services:** pandadoc (inbound), gmail, slack, google drive
- **purpose:** PandaDoc document.completed → sends welcome email, creates client Slack channel, invites client as guest, posts welcome message, creates client Drive folder with 4 subfolders, notifies #new-agreements.

### ⚪ Zoom Onboarding Call to Client Flowchart and Task Assignment **[DO NOT TOUCH]**
- **id:** `FX7WHqAqhtcV4hdr`
- **trigger:** webhook /fathom-transcript (plus Figma file-update trigger)
- **services:** notion, openai, figma, gmail
- **purpose:** Fathom transcript webhook → OpenAI agent extracts action items + diagram data → creates FigJam diagram via Figma API, creates Notion client page and action-item tasks, emails diagram via Gmail; separate Figma-update branch syncs changes to Notion and notifies team.

## CLIENT: BYLDA (Logan Fields / App Guys)

### 🟢 BYLDA n8n WF7 - Build Pack Progress **[DO NOT TOUCH]**
- **id:** `AmO3QaRxwBmHptzf`
- **trigger:** webhook /bylda-lead-progress
- **services:** leadconnectorhq/GHL, slack
- **purpose:** On lead-progress webhook, upserts GHL contact + custom fields, then composes/updates a 'Build Pack' progress note on the contact (get notes → update or create) and Slack-notifies conditionally.

### ⚪ BYLDA n8n WF1 - Lead Intake Slack Ping **[DO NOT TOUCH]**
- **id:** `80iIDmAKtBnCCUGz`
- **trigger:** /bylda-lead-created (webhook)
- **services:** slack
- **purpose:** BYLDA client lead-intake: normalizes GHL LEAD_CREATED webhook payload, responds 200, pings Slack.

### ⚪ BYLDA n8n WF2 - Prototype Engine **[DO NOT TOUCH]**
- **id:** `KYHGmsrax1QjsQuE`
- **trigger:** webhook /bylda-qualified-booked
- **services:** anthropic, supabase.co, hcti.io, leadconnectorhq/GHL, slack (incoming webhook)
- **purpose:** On qualified-booked webhook: Claude generates an HTML wireframe, uploads it to Supabase storage, screenshots via hcti.io, writes prototype URLs to the GHL contact, waits until T-30m before the booked slot, then sends a pre-call SMS via GHL conversations. Guard branches respond 422/502 and Slack-alert on failure.

### ⚪ BYLDA n8n WF3 - Branch Notifier **[DO NOT TOUCH]**
- **id:** `VqQrVZJ4VoBGyjiT`
- **trigger:** webhooks /bylda-lead-exploring and /bylda-lead-dq
- **services:** leadconnectorhq/GHL, slack (incoming webhook)
- **purpose:** Two webhooks tag a lead as exploring or DQ, upsert the contact+tag into GHL, and ping Slack via incoming webhook.

### ⚪ BYLDA n8n WF4 - Build Pack PDF Generator **[DO NOT TOUCH]**
- **id:** `VnoGpWeqRAB9nU7L`
- **trigger:** webhook /bylda-buildpack-pdf
- **services:** hcti.io, leadconnectorhq/GHL
- **purpose:** Renders a Build Pack HTML template to an image/PDF via hcti.io and writes the asset URL onto the GHL contact custom field; responds 200/502 based on render success.

### ⚪ BYLDA n8n WF5 - DQ Gift, The DIY Route **[DO NOT TOUCH]**
- **id:** `ZN6omtZkFjvUsLQ7`
- **trigger:** /bylda-dq-gift
- **services:** anthropic, hcti.io, leadconnectorhq/GHL, slack
- **purpose:** For disqualified BYLDA leads: Claude writes a personalized 'DIY Route' gift as HTML, hcti.io renders it to an image, writes the result to the GHL contact record; Slack webhook alert + 502 on render failure.

### ⚪ BYLDA n8n WF6 - Meta Conversions API **[DO NOT TOUCH]**
- **id:** `QuZfRRgIrxgVlXWP`
- **trigger:** webhook /bylda-capi-event
- **services:** facebook graph (Meta CAPI)
- **purpose:** Webhook receives an event, normalizes, SHA-256 hashes user data in a code node, and POSTs it to Meta Conversions API (graph.facebook.com pixel events), then responds 200.

## CLIENT: COST LEDGER (GHL ↔ Sheets)

### 🟢 Cost Ledger — A — Jobs Sync (GHL to Sheets) **[DO NOT TOUCH]**
- **id:** `EXamxKhW9peUouuO`
- **trigger:** webhook /ghl-jobs-sync
- **services:** leadconnectorhq/GHL, google sheets
- **purpose:** GHL opportunity webhook → maps payload to a Jobs row → upserts into Google Sheets ledger.

### 🟢 Cost Ledger — B — Cost Intake (Form to Ledger) **[DO NOT TOUCH]**
- **id:** `mmi69ErtebtgDUiN`
- **trigger:** webhook /ledger-cost (POST)
- **services:** google sheets
- **purpose:** Receives a cost form submission, reads the Jobs sheet to map the cost to a job, and appends a row to the Ledger sheet.

### 🟢 Cost Ledger — C — On-demand Excel Export **[DO NOT TOUCH]**
- **id:** `HRDZZViZHucBjHR1`
- **trigger:** webhook /ledger-export
- **services:** google sheets
- **purpose:** On webhook, reads Ledger + Jobs sheets, filters and totals in code, converts to XLSX, and responds to the webhook with the file.

### ⚪ Cost Ledger — C — Cost Intake (Form to Ledger) **[DO NOT TOUCH]**
- **id:** `TsSptE6ULGpxsgJg`
- **trigger:** webhook /ledger-cost
- **services:** google sheets
- **purpose:** Receives cost form submissions, maps to a ledger row, appends to the Cost Ledger Google Sheet.

## JARVIS / MISC INTERNAL OPS

### 🟢 FlowOps Daily Diagnostic → #diagnostics
- **id:** `S1xs37O9JZMAX8ZI`
- **trigger:** cron 0 15 * * * (10am EST) + webhook /flowops-diagnostic-now
- **services:** pandadoc, leadconnectorhq/GHL, make.com, n8n cloud, slack
- **purpose:** Daily health check code node pings PandaDoc templates/webhooks, GHL location+workflows, Make scenarios/connections, and n8n itself, then posts a status Block Kit report to Slack #diagnostics and verifies the post.

### 🟢 JARVIS
- **id:** `otWfDhWuIoPbmGtQ`
- **trigger:** webhook /jarvis-n8n
- **services:** openai, tavily, slack (via sub-workflows)
- **purpose:** LangChain agent (GPT-4o + buffer memory) behind a webhook, routing to Email/Contact/Content Creator/Calendar tool sub-workflows plus Tavily search and a calculator; a personal assistant hub.

### 🟢 Neal Autopilot — Selective (Client Channels)
- **id:** `3qyTRxFWDYthPrHn`
- **trigger:** /neal-autopilot (webhook, Slack events)
- **services:** slack, anthropic
- **purpose:** Slack event listener: filters to client channels, classifies inbound messages with Claude, auto-replies as Neal when classified safe, otherwise DMs a draft to Neal for approval and sends on approval.

### 🟢 🤖Calendar Agent
- **id:** `gIg2J8fa0SP0pggy`
- **trigger:** NONE (executeWorkflowTrigger sub-workflow)
- **services:** openai (gpt-4o via langchain), google calendar
- **purpose:** LangChain agent sub-workflow exposing Google Calendar tools (create/get/update/delete events, with attendees) to a parent JARVIS-style orchestrator.

### 🟢 🤖Contact Agent
- **id:** `dB3TqhbKNDV2pTeL`
- **trigger:** NONE (executeWorkflowTrigger — called by another workflow, JARVIS-style sub-agent)
- **services:** openai (gpt-4o via langchain), airtable, google sheets
- **purpose:** LangChain agent sub-workflow that gets/adds/updates contacts in Airtable and Google Sheets on behalf of a parent orchestrator agent.

### 🟢 🤖Email Agent
- **id:** `PWLbRw3pfFqnXuK0`
- **trigger:** NONE (executeWorkflowTrigger — called by another workflow)
- **services:** gmail, openai
- **purpose:** Sub-workflow LangChain agent (GPT-4o) with a full Gmail toolbelt: send, reply, draft, getAll, labels, mark unread — an email-operations agent invoked by a parent workflow (Jarvis-style).

### ⚪ Brain Dump to Notion Task Organizer
- **id:** `7LutbMORPmfu0nep`
- **trigger:** /brain-dump (webhook)
- **services:** openai, notion
- **purpose:** Receives brain-dump text, uses a GPT LangChain agent with structured output parser to organize it into tasks, creates Notion database entries.

### ⚪ Brand Book Generator
- **id:** `W9iOf0nz1UWwe28z`
- **trigger:** webhook /brandbook-intake
- **services:** anthropic, google drive, slack, leadconnectorhq/GHL, custom render service
- **purpose:** Brand intake webhook: two-stage Claude calls (strategy then design tokens), validates and composes a brand book, renders PDF via external render service, uploads to Drive, Slack human-approval Wait gate, then attaches note to GHL contact and notifies delivered/revision.

### ⚪ Client Ticket Submission
- **id:** `Ymp1TxefF8daZDTu`
- **trigger:** NONE (n8n form trigger)
- **services:** notion
- **purpose:** n8n-hosted form submission creates a Notion database page (client ticket). Two nodes only.

### ⚪ Fathom to Notion Call Sync + Action Items
- **id:** `NXJ92TP29LkWuowA`
- **trigger:** webhook /fathom-call-received
- **services:** notion
- **purpose:** Fathom call webhook → parses summary/action items → creates a Notion call record, then splits action items into individual Notion task pages.

### ⚪ FlowOperations - Error Notifier
- **id:** `A0g5KMYYCxSNrgXW`
- **trigger:** NONE (n8n Error Trigger)
- **services:** slack
- **purpose:** Global n8n error trigger that posts workflow failures to Slack via chat.postMessage.

### ⚪ FlowOps Slack Video Approval
- **id:** `VRBpRIg51CfTWiwX`
- **trigger:** webhook /video-ready (+ /slack-callback)
- **services:** slack, youtube (placeholder), tiktok (placeholder), instagram/facebook graph (placeholder), linkedin (placeholder)
- **purpose:** Video-ready webhook posts a Slack approve/reject card; on approval routes to four social upload nodes that are explicitly placeholders (YOUR_IG_USER_ID etc.), on reject posts a reject message.

### ⚪ X Auto Poster
- **id:** `Dwaj9g3r4XPKwphB`
- **trigger:** NONE (Slack message trigger on channel C0AG731FPMF, Brutus token)
- **services:** slack, twitter/X
- **purpose:** Posts any Slack message from channel C0AG731FPMF to X as a tweet.

### ⚪ Zoom Transcript → Notion (Blocks) → Ready to Process
- **id:** `Vlq8LWWuHZN7Vaf8`
- **trigger:** webhook /fathom/recording-completed
- **services:** notion, openai
- **purpose:** Fathom recording-completed webhook: downloads transcript, chunks it into Notion blocks appended in batches, then an OpenAI-backed agent extracts structured meeting info formatted for Notion.

## OTHER (client creative, stubs, one-offs)

### 🟢 FlowOps Lead Nurture Engine
- **id:** `uGsGEAla4W4sLhTq`
- **trigger:** webhook /flowops-lead-nurture
- **services:** leadconnectorhq/GHL, anthropic
- **purpose:** GHL form opt-in triggers an AI SMS nurture sequence: Claude generates an opener sent via GHL conversations API, then wait 30min/24h/48h with reply checks (conversations/search); each no-reply branch generates and sends a Claude follow-up, ending in a soft close.

### 🟢 Olive Branch — Manual Image Gen (Lovable Webhook) V2
- **id:** `Dmqw1pmqlOsRg5QS`
- **trigger:** webhook /cf3a46a4-7ffb-4bed-a99a-0d1a9b66d8c8
- **services:** shopify, openai, slack
- **purpose:** Lovable form webhook → fetch Shopify product, GPT creative-director brief, generate ad image via OpenAI images/edits, upload result to Slack via external-upload 3-step flow.

### 🟢 Shopify Product Image - Auto BG Detection (Pixian.ai) **[DO NOT TOUCH]**
- **id:** `Ow3moIAHQAzhXJEI`
- **trigger:** cron 0 8 * * * (daily 8am MST)
- **services:** shopify, openai (images/edits, responses, GPT vision), pixian.ai, slack
- **purpose:** Daily Olive Branch ad generator: pulls Shopify products, picks 5, GPT-5.5 creative-director brief, GPT-Vision classifies whether background removal is needed, removes BG via Pixian.ai, composites/generates final ads via OpenAI image edits, uploads results to Slack (olive-branch channel) with error-trigger Slack alerts. Client (Laura/Olive Branch) creative pipeline.

### ⚪ BoldSign 403 isolation test
- **id:** `yHwQ4gTTSMFOrjpE`
- **trigger:** webhook /endurance-os (plus manual chain)
- **services:** boldsign, w3.org (test PDF)
- **purpose:** Debug scaffold: fetches a dummy PDF, attempts BoldSign document send/properties/list calls to isolate a 403 error; also has an /endurance-os webhook node.

### ⚪ Daily Shopify Ad Generator (LAURA) **[DO NOT TOUCH]**
- **id:** `RGxqcGU9MSI5I3MI`
- **trigger:** cron 0 7 * * * (daily 7am MST)
- **services:** shopify, openai (gpt-4o, gpt-image-1, images/edits), slack, microsoft onedrive
- **purpose:** Earlier version of the Laura/Olive Branch daily ad pipeline: pick 5 Shopify products, GPT-4o writes creative brief, gpt-image-1 generates scene, composites logo, uploads to Slack and OneDrive. Client work.

### ⚪ Daily Shopify Ad Generator (LAURA) **[DO NOT TOUCH]**
- **id:** `bWlQ2T8PAttaSIpL`
- **trigger:** daily at 07:00 (scheduleTrigger)
- **services:** shopify, anthropic, openai, onedrive, microsoft teams
- **purpose:** V1 of Laura/Olive Branch ad generator: Shopify products → Claude ad strategy → OpenAI image gen → OneDrive upload → Teams approval message. Superseded by V2/V3, client-owned.

### ⚪ Daily Shopify Ad Generator V2 **[DO NOT TOUCH]**
- **id:** `bibamR9yfIoiN0p3`
- **trigger:** 0 8 * * *
- **services:** shopify, openai, slack, google sheets
- **purpose:** V2 of the Laura/Olive Branch ad pipeline: 5 Shopify products daily, OpenAI background removal + GPT-4o brief + image-edit final ad, logo stamping via editImage, Slack file upload of final+original, Sheets dedupe log; errorTrigger→Slack. Client work, superseded by V3.

### ⚪ Daily Shopify Ad Generator V3 **[DO NOT TOUCH]**
- **id:** `XemFdZMTT96hePEX`
- **trigger:** 0 7 * * *
- **services:** shopify, openai, slack, google sheets
- **purpose:** Daily picks 5 Shopify products, removes background via OpenAI image edit, GPT-4o writes creative brief, generates final ad image, composites/stamps logo, uploads final+original to Slack, logs to Google Sheets. Client (Laura/Olive Branch) creative pipeline.

### ⚪ Daily Shopify Ad Generator V3 - Without Logo **[DO NOT TOUCH]**
- **id:** `Reyp6S8V65JFxD18`
- **trigger:** cron 0 8 * * * (daily 8am MST)
- **services:** shopify, openai (GPT-5.5 responses, images/edits), slack
- **purpose:** V3 of the Laura/Olive Branch daily ad pipeline without logo compositing: 5 products, GPT-5.5 brief, OpenAI edits for BG removal + final ad, Slack upload to fmg-graphics with error-trigger alerting. Client work.

### ⚪ HR-focused automation pipeline with AI
- **id:** `ASY6Bq7Ml4CwCYkl`
- **trigger:** NONE (n8n form trigger)
- **services:** openai, google sheets, google drive
- **purpose:** Template-style CV screening pipeline: form upload → extract text from CV → OpenAI extracts qualifications/personal data + summarization → writes evaluation to Google Sheets and uploads CV to Drive.

### ⚪ My workflow
- **id:** `kRd8vrBzLtvRdIVU`
- **trigger:** NONE
- **services:** none
- **purpose:** Completely empty workflow — zero nodes. Safe-to-delete placeholder.

### ⚪ My workflow 2
- **id:** `Gf5yzIWqE0JPUDLX`
- **trigger:** cron (empty default schedule trigger, no rule configured)
- **services:** none
- **purpose:** Empty stub: a single schedule trigger with no other nodes. Does nothing.

### ⚪ My workflow 3
- **id:** `3kvsQBqzMIjRYXSZ`
- **trigger:** /ba51f593-8e26-41d2-9540-6b0f77feb892 (webhook)
- **services:** none
- **purpose:** Empty stub — single webhook node, no downstream logic.

### ⚪ My workflow 4
- **id:** `OZo0L1VBWpgQhWd8`
- **trigger:** NONE
- **services:** none
- **purpose:** Empty — zero nodes in the dump.

### ⚪ Olive Branch Daily Creative (v3.4 - faithful product) **[DO NOT TOUCH]**
- **id:** `d5MaXZjyuMHU84xQ`
- **trigger:** cron 0 7 * * *
- **services:** shopify, openai (images/edits, chat/completions, images/generations), slack (external file upload)
- **purpose:** Daily Olive Branch client creative pipeline: pulls Shopify products, removes background via OpenAI image edit, GPT-4o writes a creative brief, generates final ad image, composites logo/product with editImage nodes, uploads to Slack.

### ⚪ Olive Branch — Manual AI Image Gen (Full AI + Pixian ref)
- **id:** `GV8Kbm24UVOXdDLV`
- **trigger:** webhook /olive-branch-image-request
- **services:** shopify, openai, pixian.ai, slack
- **purpose:** Lovable form webhook → Shopify product image → Pixian background removal → GPT creative brief → OpenAI images/edits full-AI ad → logo composite → Slack external-upload share; fans out N versions in a batch loop.

### ⚪ Olive Branch — Manual Image Gen (Lovable Webhook) **[DO NOT TOUCH]**
- **id:** `7ovuU3lbuyMjTvGJ`
- **trigger:** /olive-branch-image-request (webhook)
- **services:** shopify, openai, slack
- **purpose:** Client (Laura/Olive Branch) image pipeline: form webhook → Shopify product fetch → GPT-4o creative brief → gpt-image-1 generation loop → Slack post. Client-owned.

### ⚪ PandaDoc → Slack: New Contract Drafted
- **id:** `dsIRoZ7IbfF6Ylxa`
- **trigger:** webhook /pandadoc-doc-created (POST)
- **services:** pandadoc (inbound webhook), slack
- **purpose:** Receives PandaDoc document.created events, filters to draft/uploaded status, posts a formatted Block Kit message to #new-contracts via chat.postMessage and verifies the Slack response.

### ⚪ Slack to X Auto-Poster
- **id:** `oUDjAxVPOQ31Bgdv`
- **trigger:** NONE (Slack trigger: new post in final-social-media-posts)
- **services:** slack, twitter/X
- **purpose:** Listens for new messages in the final-social-media-posts Slack channel, parses X post text out of the message via a code node, and posts to X/Twitter.

### ⚪ Slack → X Auto-Poster
- **id:** `SxKGrvHWbxiFeoR4`
- **trigger:** Slack trigger (new message in #final-social-media-posts)
- **services:** slack, twitter/x
- **purpose:** Watches #final-social-media-posts, parses X post text from the Slack message via code node, posts to X/Twitter.

### ⚪ ZZ - Anthropic Credential Setup (delete after use)
- **id:** `TCNZWVDmhjsSz1uk`
- **trigger:** NONE (manual trigger)
- **services:** httpbin.org
- **purpose:** One-off scaffold to register an Anthropic credential in n8n (HTTP node points at httpbin.org placeholder). Marked delete-after-use.

### ⚪ ZZ - Credential Setup (delete after use)
- **id:** `IY5NuPzdt9RCp5cq`
- **trigger:** NONE
- **services:** none
- **purpose:** Manual-trigger stub (Manual Trigger + NoOp only) used to attach/test credentials; self-labeled delete-after-use.

## REUSE MATRIX — building blocks for the new cold-email lead engine

| # | Component | Source workflow (id) | What it does | How to reuse |
|---|-----------|----------------------|--------------|--------------|
| 1 | Full Apify→Smartlead reference pipeline | Cold Email Lead Generation Pipeline (`0qkPeKHq1siM4yh5`, ACTIVE) | Apify run-completed webhook → dataset fetch → ICP filter + niche detect → Supabase suppression → OpenRouter personalization → Supabase mirror → Smartlead push → Slack | The canonical live implementation. Clone as the base of the new engine; it is modifiable and already OpenRouter-compliant. |
| 2 | Daily sourcing dispatcher | Apify Rotation Dispatcher — 400 Leads/Day (`v4qtQEozBVJ7wkFc`) | Smartlead mailbox-health gate (>=5 active-warmup inboxes), deterministic 10x10 niche/city rotation, fires Apify google-maps runs with completion webhooks aimed at /apify-lead-pipeline | Reactivate/adapt as the front of the loop; the mailbox gate prevents sending-capacity overruns. |
| 3 | Personalization backfill engine | FlowOps Backfill Personalization V2 (`I9knmvWukp2PKlCF`) | Every 10 min: Smartlead lead fetch with cursor persistence, Anthropic tool-use generating 9 personalization variables, key validation, PATCH back to Smartlead, Slack failure alerts | Use as-is for the personalization stage; swap Anthropic call to OpenRouter per universal rule. |
| 4 | 9-key personalization prompt + campaign/niche map | FlowOps Backfill Personalization V1 (`IKbHDsYF7ifcXVbT`) | Founder-tone system prompt (tone rules, niche labels, city/state pain references) and the campaign-ID→niche mapping | Lift the prompt and mapping into the new engine. WARNING: live Smartlead + Anthropic keys are hardcoded in its code node — move to n8n credentials and rotate. |
| 5 | Reply intent engine | B30 Reply Pipeline (`TH6uS1Phh8jZCmTG`, ACTIVE) | Claude JSON intent classifier (POSITIVE_HIGH..SPAM with confidence), auto-send guardrail (POSITIVE_HIGH & conf>=0.90 & thread_position>=2), Supabase suppression, Apify rag-web-browser signal enrichment, Slack Block Kit reply card | Keep as the reply arm. WARNING: hardcoded Anthropic/Smartlead/Apify/Supabase service-role keys in code nodes — migrate to credentials. |
| 6 | Smartlead push stage | B22 — Smartlead Push (`xXlxFQFF86lX2Ykj` / `aIXwzranxRF3krQn`) | Async 202-then-process webhook, per-lead Supabase is_suppressed RPC, campaign-grouped batches of 100 to /campaigns/{id}/leads, send_events audit ledger, suppressed-lead logging, Slack batch report | This IS the push stage — pick one variant (they are near-duplicates), delete the other, and wire it downstream of enrichment. |
| 7 | Enrichment waterfall + state machine | B11 — Enrichment + Suppression (`fPkU2gxayKtHLfdF`) | signal_events state machine (pending→enriching→done/failed), Findymail→Apollo→Anymailfinder→Hunter→MillionVerifier waterfall, suppression filter, forward-to-/brutus-push handoff, webhook + hourly-sweep dual trigger | Fill the PASTE_ placeholder API keys (cheapest-first ordering per cost rule), then it is the ready enrichment stage. |
| 8 | Hiring-signal sourcing | B01 — Hiring Ops Signal Scraper (`ZgoPlGB1dlkheTlL`) | Daily Apify Indeed scrape across 5 ops-role queries with start→poll→fetch, keyword filter, Supabase dedupe-then-insert signals, Slack daily report | Alternative/additional signal source feeding B11; inline Apify token should move to credentials. |
| 9 | Lead intake front door | Cold Email Lead Intake Pipeline (`NvQC9GvwVJXtxefG`) | Webhook leads-array intake → 200-immediately → splitOut → removeDuplicates → normalize → has-email gate → Sheets appendOrUpdate | Ready-made manual/CSV ingestion path for one-off lists alongside the Apify loop. |
| 10 | Reply-thread continuity | Qualification Call Booked (`WNE56YhjuWqmjfAO`, ACTIVE) | Stores slack_message_ts/slack_channel in Smartlead custom fields; on GHL booking, posts the call card back into the original Slack reply thread | Adopt the custom-field convention engine-wide so every lead's Slack thread survives from first reply to booked call. |
| 11 | Classify-then-gate reply drafting | Neal Autopilot — Selective (`3qyTRxFWDYthPrHn`, ACTIVE) | Claude classifies inbound Slack messages safe/unsafe; safe → auto-reply as Neal, unsafe → DM draft for approval | Reuse the gate + draft-approval loop for medium-confidence cold-email replies that B30 won't auto-send. |
| 12 | Smartlead event → Slack notify tail | Smartlead → Slack New Lead Notification (`c6g1Sjv2yab4OFKD`, ACTIVE) | Two-node Smartlead webhook → Slack post | Point additional Smartlead event types at it or clone per event category. |
| 13 | Failure alerting | FlowOperations — Error Notifier (`A0g5KMYYCxSNrgXW`) | Global n8n Error Trigger → Slack chat.postMessage | Activate and attach as the error handler on every new engine workflow. |
| 14 | Apify run-sync invocation (no polling) | W07 YouTube Scraper (`2YaQs0YAz5AmDP0Z`) / Nucleus Multi-Source Scrape (`CS3hNOZCbXNBv4fk`) [READ-ONLY] | run-sync-get-dataset-items synchronous actor call; shared-secret webhook verification; actor routing with fallback | Copy the HTTP node config into new workflows — never edit the W-series originals. |
| 15 | Apify fire-and-track shell | W05/W06/W09/W10/W11 scraper shells (`qbhw3TyP8A7Z89eV` etc.) [READ-ONLY] | POST /v2/acts/{actor}/runs kickoff + Supabase scraper_runs tracking row + Slack notify | Copy the shell for any new async lead-source scraper. |
| 16 | Smartlead stats ingest | W18 — Performance Ingest (`DPFhUvwCvgWjYs4f`) [READ-ONLY] | Daily Smartlead campaign-stats fetch → Supabase performance_events → Slack daily report | Copy the stats-fetch code node to power engine reporting/ICP iteration. |
| 17 | ICP refinement loop | W19 — ICP Refinement Review (`TRaCvLxrTlVRYD9C`, ACTIVE) [READ-ONLY] | Weekly: 30-day performance_events + icp_docs → Claude refinement proposals → Slack Friday briefing | Copy the loop shape to iterate the cold-email ICP from reply data. |
| 18 | Niche-loop sourcing + reply branch | Phase 0 Lead Generation (`61ZkxnoZBrYOGfZK`) | splitInBatches niche-config loop, Apify→Smartlead field mapping, Smartlead reply-webhook → Slack branch | Salvage the field-mapping code and reply branch; the rest is superseded by #1/#2. |
| 19 | ICP filter skeleton | Cold Email Lead Generation Pipeline v0 (`ZU82mBlxlxS0rLRv`) | Decision-maker title filter, role-email block, company_size<200, Smartlead lead_list normalization with dont_email_unsubscribed_leads | Superseded by the active `0qkPeKHq1siM4yh5` but its filter code is the cleanest standalone copy. |
| 20 | Slack human-approval gate | Onboarding Stage 2 (`nM69a2OHKraAlbe0`) [READ-ONLY] / Slack Video Approval (`VRBpRIg51CfTWiwX`) | Slack message → wait → IF-approved routing | Copy as the campaign-launch approval gate before any new campaign goes live. |

Key wiring insight: the Brutus chain is already a coherent engine — B01 (signals) → B11 (enrich, /brutus-enrich) → B22 (push, /brutus-push) → Smartlead → B30 (replies, /brutus-reply) → WNE booking card — but B01/B11/B22 are all inactive and B11's waterfall keys are unfilled. The active `0qkPeKHq1siM4yh5` + `v4qtQEozBVJ7wkFc` pair is the volume path (Google-Maps niche rotation). The new engine should merge the two: rotation dispatcher for volume, Brutus chain for signal-based precision, one shared suppression layer in Supabase.


## DO-NOT-TOUCH LIST (modifiable = false)

These workflows must never be edited in place — clone or copy patterns only:

**NUCLEUS — W-SERIES [READ-ONLY]**
- `2YaQs0YAz5AmDP0Z` — W07 — YouTube Scraper (off)
- `4ayRollLDqc2i0Iy` — W16 — Engine 3 Ads Batch (Weekly) (ACTIVE)
- `7IELdwez8oHe1v13` — W02 — Live Call Ingest (ACTIVE)
- `CS3hNOZCbXNBv4fk` — Nucleus — Client vs Competitor Multi-Source Scrape (off)
- `DPFhUvwCvgWjYs4f` — W18 — Performance Ingest (off)
- `PMimK77BQxk0p6l8` — W11 — Job Board Scraper (off)
- `Rmogbcmjui394rFm` — Nucleus - Client Asset Transcription & Intelligence Extraction (off)
- `Xyx8OPuQEvB34ZPK` — W03 — ICP Synthesis (Claude Opus) (ACTIVE)
- `Xzh21ax4GJ0y0GFG` — W15 — Engine 2 Cold Email Batch (ACTIVE)
- `dRq9YbrOcHJnoGXr` — W09 — Ad Libraries Scraper (off)
- `nxTAfAmGN97szqOA` — W10 — Competitor Landing Pages Scraper (off)
- `q4lFP1ccv9m4T6HE` — W13 - Weekly Corpus Synthesis (ACTIVE)
- `qbhw3TyP8A7Z89eV` — W05 — Reddit Scraper (off)
- `s7amPRr1dbRP7FVW` — W17 - Landing Page Generator (ACTIVE)
- `tSkTh2PdsFH2yFYq` — W06 — Review Sites Scraper (off)
- `tqalhKlrlE9Njyvq` — W20 — Output Delivery (ACTIVE)
- `uwWkVbjaFv5EL03E` — W12 - Hook Framework Tagger (ACTIVE)
- `wOnPobJNkux2t58X` — W14 — Engine 1 Content Batch (Weekly) (ACTIVE)
- `z9l9iL5u7cvFPYq1` — W17 — Landing Page Generator (older variant) (off)

**CONTENT ENGINE [READ-ONLY]**
- `6PBptEpybhdJh6eH` — 🤖Content Creator Agent (off)
- `ETqj4m7RnxG45QOu` — W14 - Engine 1 Content Batch (off)
- `IbdX6AoHDqqb0czz` — FlowOps - Slack Interactive Callback Handler (ACTIVE)
- `MPljcl3qhizRKYch` — FlowOps - Daily X Auto-Publisher (off)
- `SDajKtPcJmDYQkMz` — W08 — Short Video Scraper (TikTok) (off)
- `SF1vMrGgWpHCOKv2` — W01 - Async Form Handler (ACTIVE)
- `SY7yayRHbj4EZ06K` — W04 - Niche Corpus Bootstrap (ACTIVE)
- `TRaCvLxrTlVRYD9C` — W19 — ICP Refinement Review (ACTIVE)
- `Z0XjGAnK7nbXvXc9` — FlowOps Daily Content Pipeline (off)
- `ayQkrol5VsAwW4nd` — FlowOps - Sunday X Scheduler 2026-04-19 (off)
- `iJ8xFAcDxmmsUGIK` — My workflow 5 (off)

**CLIENT ONBOARDING (FlowOps internal)**
- `2AEQUUpF7DOrsoOk` — Workflow C — Onboarding Form Submitted (ACTIVE)
- `2x7L7Y1LUJJ9NhV0` — 1. Workflow B — PandaDoc Signed → Client Onboarding (ACTIVE)
- `6gIkvVNHbR16vMp2` — Workflow A — GHL Contract Tag → PandaDoc Draft (off)
- `7y0oWO7q5azteZtp` — Workflow B — GHL Onboarding Booked → Slack + Notion (ACTIVE)
- `8F1Tn4vEhB0ccedA` — Paused: GHL->Webhook->Slack->GDrive->Password Vault Invite (off)
- `8jTHkSHGGaCSiJln` — Fathom → Notion Call Processing (ACTIVE)
- `FX7WHqAqhtcV4hdr` — Zoom Onboarding Call to Client Flowchart and Task Assignment (off)
- `LsVRzEkpWfW912Qw` — Workflow B — GHL Onboarding Booked → Slack Channel (NEW) (off)
- `Nm6LaCzIkqG7Nx3K` — Onboarding Workflow (off)
- `U6PMw4v7vFFRDoUW` — 5. Fathom Meeting Transcript Reporter (ACTIVE)
- `YJIcdJIHijHjhbht` — 4. Brand Book Generator (ACTIVE)
- `Zxu0n17m8j3L7u5I` — Workflow B — PandaDoc Signed → Client Onboarding V2 (off)
- `aa8bUwBHFAUlM3oz` — 3. Client Onboarding: Trustpilot Competitor Watch (ACTIVE)
- `cfRtWW5bHziZkAW2` — Client Onboarding - Slack Connect + Delegation Guide (off)
- `dt5MJFlNERwybyXP` — 2. Create Notion Database (ACTIVE)
- `efjCOJiZaczbmJUX` — Onboarding — Stage 2B: Unsigned Gate (webhook) (off)
- `n53aeRXo9ZEhbDeU` — Onboarding — Stage 1: Trigger & Parse (off)
- `nM69a2OHKraAlbe0` — Onboarding — Stage 2: Signed Gate (webhook) (off)
- `u4OkvNu3ZqxpIbuX` — PandaDoc → Slack: New Contract Drafted (off)
- `vfOxPah68kHn0T0a` — GHL Contract Tag — PandaDoc Draft Generator (off)

**CLIENT: BYLDA (Logan Fields / App Guys)**
- `80iIDmAKtBnCCUGz` — BYLDA n8n WF1 - Lead Intake Slack Ping (off)
- `AmO3QaRxwBmHptzf` — BYLDA n8n WF7 - Build Pack Progress (ACTIVE)
- `KYHGmsrax1QjsQuE` — BYLDA n8n WF2 - Prototype Engine (off)
- `QuZfRRgIrxgVlXWP` — BYLDA n8n WF6 - Meta Conversions API (off)
- `VnoGpWeqRAB9nU7L` — BYLDA n8n WF4 - Build Pack PDF Generator (off)
- `VqQrVZJ4VoBGyjiT` — BYLDA n8n WF3 - Branch Notifier (off)
- `ZN6omtZkFjvUsLQ7` — BYLDA n8n WF5 - DQ Gift, The DIY Route (off)

**CLIENT: COST LEDGER (GHL ↔ Sheets)**
- `EXamxKhW9peUouuO` — Cost Ledger — A — Jobs Sync (GHL to Sheets) (ACTIVE)
- `HRDZZViZHucBjHR1` — Cost Ledger — C — On-demand Excel Export (ACTIVE)
- `TsSptE6ULGpxsgJg` — Cost Ledger — C — Cost Intake (Form to Ledger) (off)
- `mmi69ErtebtgDUiN` — Cost Ledger — B — Cost Intake (Form to Ledger) (ACTIVE)

**OTHER (client creative, stubs, one-offs)**
- `7ovuU3lbuyMjTvGJ` — Olive Branch — Manual Image Gen (Lovable Webhook) (off)
- `Ow3moIAHQAzhXJEI` — Shopify Product Image - Auto BG Detection (Pixian.ai) (ACTIVE)
- `RGxqcGU9MSI5I3MI` — Daily Shopify Ad Generator (LAURA) (off)
- `Reyp6S8V65JFxD18` — Daily Shopify Ad Generator V3 - Without Logo (off)
- `XemFdZMTT96hePEX` — Daily Shopify Ad Generator V3 (off)
- `bWlQ2T8PAttaSIpL` — Daily Shopify Ad Generator (LAURA) (off)
- `bibamR9yfIoiN0p3` — Daily Shopify Ad Generator V2 (off)
- `d5MaXZjyuMHU84xQ` — Olive Branch Daily Creative (v3.4 - faithful product) (off)
