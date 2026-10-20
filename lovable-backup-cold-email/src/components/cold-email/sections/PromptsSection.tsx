import { useState } from "react";
import { TridentCard } from "@/components/trident/TridentCard";
import { CopyBlock } from "@/components/trident/CopyBlock";
import { SectionHeader } from "../SectionHeader";

const prompts = [
  { num: "01", title: "n8n Core Pipeline", est: "25 min", color: "hsl(var(--blue))",
    desc: "Builds the complete n8n workflow JSON — Apify webhook trigger → ICP filter → dedupe → personalization → verification → Smartlead push → Slack notification.",
    prompt: `Build me a complete n8n workflow JSON file for a cold email lead generation pipeline.

WORKFLOW NODES:
1. Apify Webhook Trigger (POST) — receives dataset ID when scraping completes
2. Fetch Apify Dataset — HTTP GET to Apify API with Bearer auth
3. ICP Filter (Code Node) — filter by title (founder/owner/CEO), company_size <200, valid email
4. Deduplicate — check against existing Smartlead campaign leads
5. Normalize Fields — map to: email, first_name, last_name, company_name, linkedin_url, custom fields
6. Batch for Verification — split into 100-lead batches
7. Debounce Verification — POST to Debounce API, keep only valid emails (code 5/6)
8. Push to Smartlead — POST to Smartlead campaign API
9. Slack Notification — summary of pipeline results
10. Error Handler — catch all errors, send alert

ENV VARS: APIFY_API_TOKEN, SMARTLEAD_API_KEY, SMARTLEAD_CAMPAIGN_ID, DEBOUNCE_API_KEY, NOTIFY_WEBHOOK_URL` },
  { num: "02", title: "Apify Scraper Configs", est: "20 min", color: "hsl(var(--purple))",
    desc: "Creates Apify actor configuration files for LinkedIn, Apollo, Google Maps, and Crunchbase, plus a Node.js manager script.",
    prompt: `Build me complete Apify actor configuration files for my cold email pipeline.

ICP: Founders/owners/CEOs of 1-50 employee businesses in: marketing agencies, med spas, real estate, business coaches, e-commerce

CREATE:
1. apify-configs/linkedin-people-scraper.json
2. apify-configs/apollo-scraper.json
3. apify-configs/google-maps-scraper.json
4. apify-configs/crunchbase-scraper.json
5. scraper-manager.js — Node.js script using Apify SDK to run all scrapers
6. vertical-search-queries.json` },
  { num: "03", title: "Smartlead + Email Copy", est: "25 min", color: "hsl(var(--green))",
    desc: "Generates full Smartlead campaign setup guide, 3-email sequences for 2 verticals, and reply templates.",
    prompt: `Build me a complete Smartlead campaign setup package.

OFFER: I build custom AI-powered software using Claude Code. Deliver in days not months.

TOP 2 VERTICALS: Marketing agencies and Med spas

CREATE:
1. smartlead-campaign-setup.md
2. email-sequences/marketing-agency-sequence.json
3. email-sequences/med-spa-sequence.json
4. email-sequences/follow-up-templates.json
5. smartlead-api-integration.js
6. inbox-setup-checklist.md` },
  { num: "04", title: "GHL Reply Routing", est: "20 min", color: "hsl(var(--amber))",
    desc: "Builds n8n → GHL integration: classifies reply intent, creates contacts, assigns pipeline stages.",
    prompt: `Build me a complete GHL automation system for routing cold email replies.

GOAL: Positive replies → GHL opportunities automatically

CREATE:
1. ghl-pipeline-setup.md
2. n8n-to-ghl-webhook.js — intent classification + GHL routing
3. ghl-api-integration.js
4. smartlead-reply-webhook.md
5. ghl-automations.json
6. full-integration-test.js` },
  { num: "05", title: "AI Personalization Engine", est: "15 min", color: "hsl(var(--red))",
    desc: "Builds a Claude-powered personalization engine that writes custom first lines for every lead at scale.",
    prompt: `Build me an AI personalization engine for cold email at scale.

INPUT: Array of leads with firstName, companyName, title, industry
OUTPUT: Same array + personalizedOpener field

CREATE:
1. personalization-engine.js — Claude API (Haiku), batch of 10
2. n8n-personalization-node.js
3. test-personalization.js
4. integration-with-pipeline.md

TARGET COST: under $5 per 10,000 leads` },
  { num: "06", title: "Dashboard + Monitoring", est: "15 min", color: "#EC4899",
    desc: "Builds monitoring dashboard plus automated daily briefing and health checker scripts.",
    prompt: `Build me a monitoring dashboard and master control system.

CREATE:
1. dashboard/index.html — dark theme, pipeline health, alerts
2. daily-briefing.js — runs 8am daily via cron
3. health-checker.js — runs every 4 hours
4. cron-setup.md
5. master-runbook.md — complete operations manual` },
];

export const PromptsSection = () => {
  const [activePrompt, setActivePrompt] = useState(0);
  const pr = prompts[activePrompt];

  return (
    <div>
      <SectionHeader label="14 — CLAUDE CODE" title="Build Prompts" subtitle="Paste these into Claude Code in order. Complete build in ~2 hours." />
      <div className="rounded-lg p-2.5 mb-5 text-[13px]" style={{ background: "hsl(var(--red) / 0.08)", border: "1px solid hsl(var(--red) / 0.2)", color: "hsl(var(--red))" }}>
        ⚠️ <strong>Pre-Build Checklist:</strong> Buy 3 domains on Namecheap ($3-6) • Sign up for Apify ($49/mo) • Have Smartlead + GHL credentials ready • Have n8n running
      </div>
      <div className="flex gap-2 mb-5 flex-wrap">
        {prompts.map((p, i) => (
          <button
            key={i}
            onClick={() => setActivePrompt(i)}
            className="rounded-lg px-3.5 py-2 cursor-pointer transition-all"
            style={{
              background: activePrompt === i ? p.color + "25" : "hsl(var(--background-secondary))",
              border: `1px solid ${activePrompt === i ? p.color : "hsl(var(--border))"}`,
            }}
          >
            <span className="font-mono text-[11px] font-bold" style={{ color: p.color }}>{p.num}</span>
            <span className={`text-xs ml-1.5 ${activePrompt === i ? "text-foreground" : "text-foreground-tertiary"}`}>{p.title}</span>
            <span className="text-foreground-tertiary text-[10px] ml-1.5">~{p.est}</span>
          </button>
        ))}
      </div>
      <TridentCard accentColor={pr.color}>
        <div className="flex justify-between items-start mb-3">
          <div>
            <span className="font-mono text-[11px] font-bold px-2.5 py-0.5 rounded" style={{ background: pr.color + "22", border: `1px solid ${pr.color}55`, color: pr.color }}>PROMPT {pr.num} OF 06</span>
            <h3 className="text-lg font-bold text-foreground mt-2 mb-1">{pr.title}</h3>
            <p className="text-foreground-tertiary text-[13px]">{pr.desc}</p>
          </div>
          <span className="font-mono text-[11px] px-2.5 py-0.5 rounded text-foreground-tertiary" style={{ background: "hsl(var(--background-tertiary))", border: "1px solid hsl(var(--border))" }}>~{pr.est}</span>
        </div>
        <CopyBlock label="COPY → PASTE INTO CLAUDE CODE" content={pr.prompt} />
      </TridentCard>
    </div>
  );
};
