#!/usr/bin/env python3
"""
Build the FlowOps SOP as a designer-quality 40-50 page PDF.
HTML + print CSS → Playwright → PDF.
"""
import base64
import re
import time
from pathlib import Path

OUT_DIR = Path("/Users/nealthakkar/Desktop/council/sop_pdf")
OUT_PDF = Path("/Users/nealthakkar/Desktop/FlowOps_SOP_v1.pdf")

# Embed Mercer mockup as base64 for inline use
mercer = Path("/Users/nealthakkar/Desktop/intakebot/public/mockups/tmercer.png").read_bytes()
mercer_b64 = base64.b64encode(mercer).decode()
MERCER_IMG = f"data:image/png;base64,{mercer_b64}"

# CSS
CSS = """
@page {
  size: Letter;
  margin: 0.5in 0.6in 0.6in 0.6in;
  background: #0a0d14;
  @bottom-center {
    content: "FlowOps Cold Email Pipeline · SOP v1 · " counter(page) " / " counter(pages);
    font-family: Inter, -apple-system, sans-serif;
    font-size: 9pt;
    color: #4a5568;
  }
  @top-right {
    content: "CONFIDENTIAL · FLOW OPERATIONS";
    font-family: Inter, sans-serif;
    font-size: 8pt;
    letter-spacing: 0.15em;
    color: #3b82f6;
  }
}
@page :first {
  margin: 0;
  @top-right { content: ""; }
  @bottom-center { content: ""; }
}
@page section-divider {
  margin: 0;
  @top-right { content: ""; }
  @bottom-center { content: ""; }
}

* { margin: 0; padding: 0; box-sizing: border-box; }
html, body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  background: #0a0d14;
  color: #e2e8f0;
  font-size: 11pt;
  line-height: 1.55;
  -webkit-font-smoothing: antialiased;
}

/* === COVER === */
.cover {
  page: cover;
  page-break-after: always;
  height: 100vh;
  width: 100%;
  background:
    radial-gradient(ellipse at 20% 20%, rgba(59,130,246,0.35), transparent 50%),
    radial-gradient(ellipse at 80% 80%, rgba(168,85,247,0.30), transparent 50%),
    radial-gradient(ellipse at 50% 100%, rgba(34,211,238,0.20), transparent 50%),
    linear-gradient(180deg, #0a0d14 0%, #050811 100%);
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 0.9in 0.8in;
  color: #fff;
}
.cover .logo-mark {
  font-size: 18pt;
  font-weight: 700;
  letter-spacing: 0.3em;
  color: #3b82f6;
}
.cover .hero {
  display: flex; flex-direction: column; gap: 24px;
  margin-top: 60px;
}
.cover .badge {
  display: inline-block;
  padding: 6px 14px;
  background: rgba(59,130,246,0.15);
  border: 1px solid #3b82f6;
  color: #93c5fd;
  font-size: 9pt;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  border-radius: 4px;
  width: max-content;
}
.cover h1 {
  font-family: 'Space Grotesk', 'Inter', sans-serif;
  font-size: 64pt;
  font-weight: 700;
  line-height: 1.0;
  background: linear-gradient(135deg, #fff 0%, #93c5fd 60%, #c4b5fd 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  letter-spacing: -0.03em;
}
.cover h2 {
  font-size: 22pt;
  font-weight: 400;
  color: #cbd5e1;
  line-height: 1.3;
  max-width: 80%;
}
.cover .meta-grid {
  display: grid; grid-template-columns: 1fr 1fr 1fr 1fr;
  gap: 24px;
  padding-top: 36px;
  border-top: 1px solid rgba(255,255,255,0.1);
}
.cover .meta-label {
  font-size: 8pt;
  letter-spacing: 0.2em;
  color: #64748b;
  text-transform: uppercase;
  margin-bottom: 6px;
}
.cover .meta-val {
  font-size: 14pt;
  color: #fff;
  font-weight: 500;
}
.cover .footer {
  display: flex; justify-content: space-between;
  font-size: 10pt;
  color: #64748b;
}

/* === SECTION DIVIDER === */
.divider {
  page: section-divider;
  page-break-before: always;
  page-break-after: always;
  height: 100vh;
  width: 100%;
  background: linear-gradient(135deg, #0a0d14 0%, #0f1525 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 0 1.2in;
  position: relative;
}
.divider::before {
  content: '';
  position: absolute;
  top: 0; left: 0;
  width: 8px; height: 100%;
  background: linear-gradient(180deg, var(--accent, #3b82f6), transparent);
}
.divider .num {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 240pt;
  font-weight: 700;
  line-height: 0.9;
  color: rgba(59,130,246,0.12);
  letter-spacing: -0.05em;
}
.divider .label {
  font-size: 10pt;
  letter-spacing: 0.3em;
  color: var(--accent, #3b82f6);
  text-transform: uppercase;
  margin-bottom: 12px;
}
.divider .title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 56pt;
  font-weight: 700;
  color: #fff;
  letter-spacing: -0.02em;
  line-height: 1.05;
  margin-bottom: 20px;
}
.divider .blurb {
  font-size: 16pt;
  color: #94a3b8;
  max-width: 600px;
  line-height: 1.4;
}

/* === CONTENT === */
.page-block {
  page-break-after: always;
  padding-top: 12pt;
}
.page-block:last-child { page-break-after: auto; }

h3.section-h {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 26pt;
  font-weight: 700;
  color: #fff;
  letter-spacing: -0.02em;
  margin-bottom: 6pt;
  line-height: 1.1;
}
h3.section-h .num {
  color: var(--accent, #3b82f6);
  margin-right: 12pt;
  font-weight: 700;
}
.subtitle {
  font-size: 11pt;
  color: var(--accent, #3b82f6);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-bottom: 18pt;
  font-weight: 600;
}

h4 {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 14pt;
  font-weight: 600;
  color: #fff;
  margin-top: 18pt;
  margin-bottom: 8pt;
  letter-spacing: -0.01em;
}
h4::before {
  content: '';
  display: inline-block;
  width: 4px; height: 16px;
  background: var(--accent, #3b82f6);
  margin-right: 10px;
  vertical-align: -3px;
  border-radius: 2px;
}

p { color: #cbd5e1; margin-bottom: 8pt; line-height: 1.6; }
strong { color: #fff; font-weight: 600; }
em { color: #94a3b8; font-style: italic; }

ul, ol { margin-left: 18pt; margin-bottom: 12pt; }
li { color: #cbd5e1; margin-bottom: 4pt; line-height: 1.55; }
li::marker { color: var(--accent, #3b82f6); }

a { color: #93c5fd; text-decoration: none; }

/* Inline code */
code {
  font-family: 'JetBrains Mono', monospace;
  font-size: 9.5pt;
  background: rgba(148,163,184,0.1);
  padding: 1px 5px;
  border-radius: 3px;
  color: #c4b5fd;
  border: 1px solid rgba(168,85,247,0.2);
}

/* Code blocks */
pre {
  background: #0f1729;
  border: 1px solid #1e293b;
  border-left: 3px solid var(--accent, #3b82f6);
  border-radius: 4px;
  padding: 12pt 14pt;
  font-family: 'JetBrains Mono', monospace;
  font-size: 9pt;
  color: #cbd5e1;
  line-height: 1.5;
  overflow-x: hidden;
  margin: 12pt 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}

/* Tables */
table {
  width: 100%;
  border-collapse: collapse;
  margin: 12pt 0;
  font-size: 9.5pt;
  border-radius: 6px;
  overflow: hidden;
}
thead {
  background: rgba(59,130,246,0.15);
}
thead th {
  text-align: left;
  padding: 8pt 10pt;
  color: #93c5fd;
  font-weight: 600;
  font-size: 9pt;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  border-bottom: 1px solid rgba(59,130,246,0.3);
}
tbody td {
  padding: 7pt 10pt;
  border-bottom: 1px solid rgba(148,163,184,0.1);
  color: #cbd5e1;
}
tbody tr:nth-child(even) td { background: rgba(15,23,41,0.4); }

/* Callouts */
.callout {
  background: linear-gradient(135deg, rgba(59,130,246,0.08), rgba(168,85,247,0.05));
  border: 1px solid rgba(59,130,246,0.25);
  border-left: 4px solid var(--accent, #3b82f6);
  border-radius: 6px;
  padding: 14pt 16pt;
  margin: 14pt 0;
}
.callout .label {
  font-size: 8pt;
  letter-spacing: 0.2em;
  color: var(--accent, #3b82f6);
  text-transform: uppercase;
  margin-bottom: 6pt;
  font-weight: 600;
}
.callout .body { color: #e2e8f0; font-size: 10.5pt; }

.kpi-row {
  display: grid; grid-template-columns: 1fr 1fr 1fr 1fr;
  gap: 10pt;
  margin: 14pt 0;
}
.kpi-row .kpi {
  background: rgba(15,23,41,0.7);
  border: 1px solid #1e293b;
  border-radius: 6px;
  padding: 10pt;
  text-align: left;
}
.kpi .icon { font-size: 18pt; }
.kpi .label {
  font-size: 7.5pt;
  letter-spacing: 0.15em;
  color: #64748b;
  text-transform: uppercase;
  margin-top: 4pt;
}
.kpi .val {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 22pt;
  font-weight: 700;
  color: #fff;
  margin-top: 4pt;
  line-height: 1.0;
}
.kpi .delta {
  font-size: 8pt;
  color: #22c55e;
  margin-top: 3pt;
}

/* Two-column layout */
.cols2 {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 18pt;
  margin: 10pt 0;
}

/* Image embed */
.figure {
  margin: 14pt 0;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #1e293b;
  background: #0f1729;
}
.figure img { width: 100%; display: block; }
.figure .caption {
  padding: 8pt 12pt;
  font-size: 9pt;
  color: #94a3b8;
  border-top: 1px solid #1e293b;
  background: #0a0e18;
}

/* Status pill */
.pill {
  display: inline-block;
  padding: 2pt 8pt;
  font-size: 8pt;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  border-radius: 3px;
  margin-right: 6pt;
}
.pill-green  { background: rgba(34,197,94,0.15);  color: #4ade80; border: 1px solid #22c55e; }
.pill-amber  { background: rgba(245,158,11,0.15); color: #fbbf24; border: 1px solid #f59e0b; }
.pill-violet { background: rgba(168,85,247,0.15); color: #c4b5fd; border: 1px solid #a855f7; }
.pill-cyan   { background: rgba(34,211,238,0.15); color: #67e8f9; border: 1px solid #22d3ee; }
.pill-grey   { background: rgba(148,163,184,0.15);color: #cbd5e1; border: 1px solid #64748b; }

/* TOC */
.toc { padding: 12pt 0; }
.toc-item {
  display: flex;
  justify-content: space-between;
  padding: 8pt 0;
  border-bottom: 1px dashed #1e293b;
  font-size: 11pt;
}
.toc-item .name { color: #e2e8f0; }
.toc-item .num { color: #3b82f6; font-family: 'JetBrains Mono', monospace; }

/* Architecture stack visual */
.stack {
  display: grid;
  gap: 8pt;
  margin: 14pt 0;
}
.stack-layer {
  background: rgba(15,23,41,0.7);
  border: 1px solid #1e293b;
  border-left: 4px solid var(--layer-color, #3b82f6);
  border-radius: 4px;
  padding: 10pt 14pt;
}
.stack-layer .layer-name {
  font-size: 8pt;
  letter-spacing: 0.2em;
  color: var(--layer-color, #3b82f6);
  text-transform: uppercase;
  font-weight: 600;
  margin-bottom: 4pt;
}
.stack-layer .layer-content { color: #cbd5e1; font-size: 10pt; }
"""

# Section divider builder
def divider(num, title, blurb, accent="#3b82f6"):
    return f"""
<div class="divider" style="--accent: {accent};">
  <div class="num">{num}</div>
  <div>
    <div class="label">Section {num}</div>
    <div class="title">{title}</div>
    <div class="blurb">{blurb}</div>
  </div>
</div>
"""

# Content page builder
def section_content(num, title, accent, body):
    return f"""
<div class="page-block" style="--accent: {accent};">
  {body}
</div>
"""

# Build the full HTML
def build_html():
    parts = [
"""<!doctype html><html><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>""" + CSS + """</style>
</head><body>""",

# ============ COVER ============
"""
<div class="cover">
  <div class="logo-mark">FLOW OPERATIONS</div>
  <div class="hero">
    <div class="badge">Standard Operating Procedure · v1</div>
    <h1>Cold Email Pipeline</h1>
    <h2>End-to-end SOP. Discovery → personalization → magnet → send → reply → booked call.</h2>
  </div>
  <div>
    <div class="meta-grid">
      <div><div class="meta-label">Owner</div><div class="meta-val">Neal Thakkar</div></div>
      <div><div class="meta-label">Status</div><div class="meta-val">LIVE</div></div>
      <div><div class="meta-label">Variants</div><div class="meta-val">A · B · C · D</div></div>
      <div><div class="meta-label">Capacity</div><div class="meta-val">800/day</div></div>
    </div>
    <div style="height:20px;"></div>
    <div class="footer">
      <span>Confidential · FlowOperations.ai</span>
      <span>2026-05-13 · Edition 1.0</span>
    </div>
  </div>
</div>
""",

# ============ TOC ============
"""
<div class="page-block">
  <h3 class="section-h" style="--accent:#3b82f6;">Table of Contents</h3>
  <div class="subtitle">14 sections · ~45 pages</div>
  <div class="toc">
""" + "".join(f"""<div class="toc-item"><span class="name">{t}</span><span class="num">§{n}</span></div>""" for n,t in [
("01","Vision & Target Metrics"),
("02","Stage 1 — Discovery (Lead Supply)"),
("03","Stage 2 — ICP Filter"),
("04","Stage 3 — Signal Enrichment (Cara Barone)"),
("05","Stage 3.0 — Strategy Council (Magnet Picker)"),
("06","Stage 3.5 — Magnet Generation (4 Variants)"),
("07","Stage 4 — Copy Generation"),
("08","Stage 5 — Send (Smartlead)"),
("09","Stage 6 — Auto-Reply"),
("10","Stage 7 — Booked Call"),
("11","Stage 8 — Metrics Loop"),
("12","Tech Stack Overview"),
("13","Cost Model"),
("14","Runbooks & Glossary"),
]) + """
  </div>
</div>
""",

# ============ SECTION 1 ============
divider("01", "Vision & Target Metrics", "Build the highest-quality outbound system in service businesses — real research, real magnets, real personalization at scale.", "#3b82f6"),

"""
<div class="page-block" style="--accent:#3b82f6;">
  <div class="subtitle">Section 01 · The Mission</div>
  <h3 class="section-h"><span class="num">01</span>Vision &amp; Target Metrics</h3>
  <p style="font-size:13pt; color:#e2e8f0; max-width:90%; margin: 16pt 0;">
    We are building the most personalized, highest-quality outbound system in service businesses. The thesis is simple: when every email contains a real magnet (live AI demo, real ops score, or a custom website redesign) and references specific public signals about the lead, reply rates 3-5x industry averages — and the cost-per-call collapses by 10-40x relative to paid advertising.
  </p>
  <h4>Four pillars</h4>
  <ul>
    <li><strong>Cara Barone</strong> — an AI research agent persona (hello@carabarone.com) who pulls public dossiers on each lead before any email is sent. Reads as a real internal handoff, not as marketing copy.</li>
    <li><strong>Council</strong> — a 12-persona, 5-judge LLM ensemble that writes every email. Each lead's email is reviewed by the judges before send. Bad drafts die in committee.</li>
    <li><strong>4-variant split testing</strong> — A (IntakeBot URL), B (FlowScore quiz), C (Website mockup), D (Direct AI Audit pilot). Each variant is fundamentally different in psychology and friction.</li>
    <li><strong>Auto-reply at scale</strong> — every reply is classified by an LLM and a draft response is generated within 90 seconds. Neal reviews + sends.</li>
  </ul>

  <div class="callout">
    <div class="label">Why this works</div>
    <div class="body">Cold email loses when every email is templated. The system above produces emails that look hand-written for 800 leads per day. That asymmetry is the moat.</div>
  </div>
</div>

<div class="page-block" style="--accent:#3b82f6;">
  <h4>90-Day target metrics</h4>
  <table>
    <thead><tr><th>KPI</th><th>Today</th><th>30 days</th><th>60 days</th><th>90 days</th></tr></thead>
    <tbody>
      <tr><td>Daily new leads</td><td>150</td><td>250</td><td>400</td><td>600</td></tr>
      <tr><td>Daily sends (new + followups)</td><td>80-150</td><td>300-450</td><td>600-800</td><td>1,000-1,200</td></tr>
      <tr><td>Reply rate</td><td>—</td><td>2.0%</td><td>2.5%</td><td>3.0%</td></tr>
      <tr><td>Positive reply rate</td><td>—</td><td>0.9%</td><td>1.2%</td><td>1.5%</td></tr>
      <tr><td>Booked calls / day</td><td>0</td><td>2-3</td><td>4-6</td><td>7-10</td></tr>
      <tr><td>Booked calls / month</td><td>0</td><td>60-90</td><td>120-180</td><td>200-300</td></tr>
      <tr><td>Avg deal value</td><td>—</td><td>$5K</td><td>$8K</td><td>$12K</td></tr>
      <tr><td><strong>Monthly outbound revenue</strong></td><td>$0</td><td><strong>$90-180K</strong></td><td><strong>$250-500K</strong></td><td><strong>$1M+</strong></td></tr>
    </tbody>
  </table>

  <h4>What "winning" looks like at day 90</h4>
  <p>
    A consistent <strong>5-7 qualified founder calls per day on Neal's calendar</strong> at a cost of <strong>~$6 per call</strong>. Revenue is held back not by lead supply but by Neal's personal call capacity — which is the right bottleneck to have. From there, the next move is hiring a discovery-call SDR or building a Loom-screening layer.
  </p>

  <div class="cols2" style="margin-top: 16pt;">
    <div class="callout">
      <div class="label">Industry benchmark</div>
      <div class="body"><strong>$50-200</strong> per qualified call via paid advertising.</div>
    </div>
    <div class="callout">
      <div class="label">FlowOps benchmark</div>
      <div class="body"><strong>~$4.50</strong> per qualified call at realistic 90-day tier.</div>
    </div>
  </div>
</div>
""",

# ============ SECTION 2 ============
divider("02", "Discovery", "150+ fresh deliverable leads per day, rotating across 12 niches. Apify + Acquisity + manual.", "#22d3ee"),

"""
<div class="page-block" style="--accent:#22d3ee;">
  <div class="subtitle">Section 02 · Stage 1 · Lead Supply</div>
  <h3 class="section-h"><span class="num">02</span>Discovery</h3>

  <p><strong>Goal:</strong> 150+ fresh, deliverable leads per day, distributed across 12 active niches.</p>

  <h4>Three sources</h4>
  <table>
    <thead><tr><th>Source</th><th>Mechanism</th><th>Daily volume</th><th>Cost</th></tr></thead>
    <tbody>
      <tr><td><strong>Apify Google Maps</strong></td><td>n8n daily cron 6 AM ET, rotates 3 niches/day across 12-niche queue</td><td>~150</td><td>$60-90/mo</td></tr>
      <tr><td><strong>Acquisity CSV imports</strong></td><td>Manual export, <code>bulk_import.py</code> runs end-to-end ingest</td><td>Variable</td><td>Per Acquisity contract</td></tr>
      <tr><td><strong>Manual seeding</strong></td><td>ABM-style hand-selection for Fortune 500 / strategic targets</td><td>~5</td><td>$0</td></tr>
    </tbody>
  </table>

  <h4>n8n cron rotation</h4>
  <p>Workflow ID <code>QVMajRvX1TKB7r0d</code> ("Daily Apify Niche Scrapes (FlowOps)") fires every morning at 6 AM ET. Rotates three niches per day across a twelve-niche queue:</p>
  <table>
    <thead><tr><th>Day</th><th>Niches scraped</th></tr></thead>
    <tbody>
      <tr><td>Sun / Thu</td><td>MCA · MEDSPA · PI_LAW</td></tr>
      <tr><td>Mon / Fri</td><td>WEALTH · MORTGAGE · INSURANCE</td></tr>
      <tr><td>Tue / Sat</td><td>COMMLOAN · AGENCY · TAX_RES</td></tr>
      <tr><td>Wed</td><td>RECRUITER · IT_MSP · FINANCIAL</td></tr>
    </tbody>
  </table>

  <p>Each scrape: 10 leads × 5 cities × 3 niches = <strong>150 leads / day</strong>. Cost capped at ~$3/day Apify spend.</p>

  <div class="callout">
    <div class="label">Apify configuration</div>
    <div class="body">Actor: <code>compass~crawler-google-places</code>. maxCrawledPlacesPerSearch=10 (was 50, reduced for cost). includeWebResults=true to capture website + reviews.</div>
  </div>
</div>

<div class="page-block" style="--accent:#22d3ee;">
  <h4>Acquisity integration</h4>
  <p>Acquisity provides purchased, intent-graded B2B lead lists at scale. The integration flow:</p>
  <ol>
    <li>Neal exports CSV from Acquisity dashboard (any niche, 200-2,000 leads)</li>
    <li>Drop CSV in <code>~/Downloads/</code></li>
    <li>Run <code>python3 bulk_import.py ~/Downloads/file.csv --niche RECRUITER</code></li>
    <li>Script: dedups in-CSV, dedups against Smartlead universe, validates emails, routes to target campaign</li>
    <li>Webhook fires to n8n → Council personalizes each lead → writes back to Smartlead</li>
  </ol>

  <h4>Manual seeding workflow</h4>
  <p>Reserved for high-LTV targets. Neal hand-picks 5-10 names per day from LinkedIn or news. Drops them into a Notion intake table. Same Council enrichment runs but with manual quality review before Smartlead push.</p>

  <h4>Quality gates at Discovery</h4>
  <ul>
    <li>Email must exist and be deliverable (regex + MX record check)</li>
    <li>Website must resolve (HTTP 200 within 5 seconds)</li>
    <li>Lead must not exist in any Smartlead campaign (dedup against universe)</li>
    <li>Domain age &gt; 30 days (avoid honeypots and disposables)</li>
  </ul>

  <h4>What lives where</h4>
  <pre>
~/.council/lead_cache/      # Local CSV cache of all imports
~/.council/dedup_index.db   # SQLite index of email + domain dedup keys
n8n workflow: QVMajRvX1TKB7r0d
Apify token: stored in ~/.config/n8n-creds/apify.env</pre>
</div>
""",

# ============ SECTION 3 ============
divider("03", "ICP Filter", "70% pass rate. Niche classifier, deliverability check, hygiene rejects.", "#22d3ee"),

"""
<div class="page-block" style="--accent:#22d3ee;">
  <div class="subtitle">Section 03 · Stage 2 · Quality Gates</div>
  <h3 class="section-h"><span class="num">03</span>ICP Filter</h3>

  <p><strong>Goal:</strong> Pass only deliverable, in-ICP leads to enrichment. Achieve ~70% pass rate from raw scrape.</p>

  <h4>The 25+ niche classifier</h4>
  <p>Each lead's company name, website meta description, and Google Maps category are run through a Gemini Flash classifier that picks one of 25+ niche labels:</p>
  <div class="cols2">
    <div>
      <ul>
        <li><strong>WEALTH</strong> — wealth management, RIA, family office</li>
        <li><strong>FINANCIAL</strong> — financial advisor, CFP</li>
        <li><strong>MORTGAGE</strong> — broker, lender, mortgage origination</li>
        <li><strong>INSURANCE</strong> — agency, captive, broker</li>
        <li><strong>MEDSPA</strong> — aesthetic medicine, med spa</li>
        <li><strong>PI_LAW</strong> — personal injury law</li>
        <li><strong>MCA</strong> — merchant cash advance</li>
        <li><strong>COMMLOAN</strong> — commercial lending</li>
      </ul>
    </div>
    <div>
      <ul>
        <li><strong>AGENCY</strong> — marketing / SMMA</li>
        <li><strong>RECRUITER</strong> — staffing, executive search</li>
        <li><strong>COACH_BIZ</strong> — business coach</li>
        <li><strong>COACH_FIT</strong> — fitness coach, gym</li>
        <li><strong>IT_MSP</strong> — managed IT services</li>
        <li><strong>TAX_RES</strong> — tax resolution</li>
        <li><strong>DENTAL</strong> — dental practice</li>
        <li><strong>ROOFER</strong> — residential roofing</li>
      </ul>
    </div>
  </div>

  <h4>Hygiene rejects</h4>
  <p>Leads are dropped if any of the following is true:</p>
  <ul>
    <li>No website OR no email → drop silently</li>
    <li>Email domain is personal (<code>gmail.com</code>, <code>yahoo.com</code>, etc.) with no business domain → flag for manual review</li>
    <li>Domain age &lt; 30 days → flag (likely fresh disposable)</li>
    <li>Already in any Smartlead campaign (active, paused, or completed) → dedup drop</li>
    <li>MX record fails → drop</li>
  </ul>

  <h4>Optional ZeroBounce verification</h4>
  <p>For historically high-bounce niches (MORTGAGE shows 11.5% bounce rate without verification), an optional ZeroBounce sweep runs on the filtered list before push. Costs $0.007/email. Drops bounce to under 2%.</p>

  <div class="callout">
    <div class="label">Why this matters</div>
    <div class="body">Smartlead's deliverability score is partially based on bounce rate. Bounces above 4% trigger inbox-provider throttling. The ICP filter is a deliverability investment, not just a quality filter.</div>
  </div>

  <h4>Output schema</h4>
  <pre>{
  "email": "robert@ufc4wealth.com",
  "first_name": "Robert",
  "last_name": "Mendez",
  "company_name": "UFC 4 Wealth",
  "website": "ufc4wealth.com",
  "niche": "WEALTH",
  "city": "Austin", "state": "TX",
  "campaign_id": 3263730,
  "source": "apify_google_maps",
  "verified_at": "2026-05-13T03:14:22Z"
}</pre>
</div>
""",

# ============ SECTION 4 ============
divider("04", "Signal Enrichment", "Cara Barone — the AI research agent. Public dossier per lead.", "#22d3ee"),

"""
<div class="page-block" style="--accent:#22d3ee;">
  <div class="subtitle">Section 04 · Stage 3 · Cara Barone</div>
  <h3 class="section-h"><span class="num">04</span>Signal Enrichment</h3>

  <p><strong>Goal:</strong> Build a 3-5 line public-records dossier on each lead. Used in the email body either as a personalized opener OR as a forwarded "Cara research" block.</p>

  <h4>Cara Barone — the persona</h4>
  <div class="callout">
    <div class="label">Identity</div>
    <div class="body"><strong>Email:</strong> hello@carabarone.com<br>
    <strong>Voice:</strong> Internal-comms, short, fact-dense, no salesy language<br>
    <strong>Role:</strong> AI research analyst at FlowOps. Pulls public dossiers and forwards them to Neal for cold-outreach decisions.<br>
    <strong>Format:</strong> Renders as a real forwarded email inside the cold email body, like a Slack handoff that accidentally went outbound.</div>
  </div>

  <h4>Signal sources (live)</h4>
  <table>
    <thead><tr><th>Source</th><th>Signal type</th><th>API / method</th></tr></thead>
    <tbody>
      <tr><td>LinkedIn</td><td>Job changes, recent posts, hires</td><td>Internal scraper</td></tr>
      <tr><td>Company website</td><td>Tech stack, services, tagline, social proof</td><td>Playwright + Wappalyzer rules</td></tr>
      <tr><td>SEC EDGAR</td><td>Form D filings (wealth liquidity signal)</td><td>api.sec.gov</td></tr>
      <tr><td>Google Business Profile</td><td>Reviews, hours, photos</td><td>Apify scraper</td></tr>
      <tr><td>News API</td><td>Recent press, funding announcements</td><td>NewsAPI / Apify</td></tr>
      <tr><td>Tech stack sniffer</td><td>HubSpot, GHL, Calendly, ConvertKit etc. detected</td><td>Custom Playwright sniffer</td></tr>
    </tbody>
  </table>

  <h4>Signal sources (planned next 2 weeks)</h4>
  <ul>
    <li>Reddit — brand mentions, complaint threads</li>
    <li>Twitter / X — recent posts, follower count growth</li>
    <li>Meta Ads Library — active ad creatives</li>
    <li>YouTube — recent videos, subscriber growth</li>
    <li>G2 / Trustpilot — review velocity, NPS signals</li>
  </ul>
</div>

<div class="page-block" style="--accent:#22d3ee;">
  <h4>Output schema</h4>
  <pre>{
  "leadId": "abc123",
  "signals": {
    "linkedin_job_change_days": 14,
    "tech_stack": ["GHL", "Calendly", "ConvertKit"],
    "recent_news": "Featured in Forbes Wealth, May 2026",
    "form_d_count_metro_60d": 34,
    "gbp_reviews": 127,
    "gbp_avg_rating": 4.8
  }
}</pre>

  <h4>Cara block — sample output</h4>
  <pre>---------- Forwarded ----------
From: Cara Barone &lt;hello@carabarone.com&gt;
Subject: Reach out to Robert - Quick Start fit
To: Neal

Wrapped research on UFC 4 Wealth.

- Site running GHL + FB Pixel - already comfortable with marketing tech
- 34 Form D filings in Austin metro last 60 days (SEC EDGAR) - local liquidity wave
- Robert listed as founder/CEO, joined Sept 2024 - recent enough to still be building
- GBP shows 47 reviews, 4.9 avg - real client base, not just SEO bait

Strong fit, recommend reach-out. 9/10.

- Cara</pre>

  <h4>How Cara plugs into emails</h4>
  <p>The Council uses Cara's output in two ways:</p>
  <ol>
    <li><strong>As the personalized opener line.</strong> The Council pulls the strongest signal and rewrites it in Neal's voice as the first sentence of the email.</li>
    <li><strong>As a forwarded block inside the email.</strong> Used in Acquisity variants V1 and V6. The cold email body literally contains a forwarded Cara research note — feels like an internal Slack handoff that slipped to the lead.</li>
  </ol>

  <h4>Code paths</h4>
  <pre>core/signal_enricher.py       # Source aggregator
core/cara_research.py         # Cara block generator
core/llm.py                   # OpenRouter wrapper, models: gemini-2.0-flash-001</pre>
</div>
""",

# ============ SECTION 5 ============
divider("05", "Strategy Council", "Magnet picker. Decides A/B/C/D per lead based on signal strength + past metrics.", "#a855f7"),

"""
<div class="page-block" style="--accent:#a855f7;">
  <div class="subtitle">Section 05 · Stage 3.0 · The Brain</div>
  <h3 class="section-h"><span class="num">05</span>Strategy Council</h3>

  <p><strong>Goal:</strong> Decide which magnet variant — A, B, C, or D — best fits THIS lead given their signal profile and past niche performance.</p>

  <h4>The decision</h4>
  <p>Every lead enters Stage 3.0 with a signal dossier (from Cara) and a niche tag. The Strategy Council picks one of four magnet variants and sets the pain angle + CTA shape. The decision is written to the lead's <code>custom_fields.variant_assigned</code> in Smartlead.</p>

  <h4>Decision matrix</h4>
  <table>
    <thead><tr><th>Lead profile</th><th>Best variant</th><th>Why</th></tr></thead>
    <tbody>
      <tr><td>High-traffic site, weak conversion infrastructure</td><td><strong>C — Mockup</strong></td><td>Visual proof of upside</td></tr>
      <tr><td>Strong tech stack, modern website</td><td><strong>B — FlowScore</strong></td><td>They appreciate data, will engage with a quiz</td></tr>
      <tr><td>Low signal but in-ICP</td><td><strong>D — Direct Audit</strong></td><td>Lowest friction, offer-led not value-led</td></tr>
      <tr><td>Highly personalized signal hit (job change, recent news)</td><td><strong>A — IntakeBot</strong></td><td>Engagement-led, the URL is novelty enough</td></tr>
    </tbody>
  </table>

  <h4>Current allocation</h4>
  <div class="cols2">
    <div class="callout">
      <div class="label">Wednesday + Thursday</div>
      <div class="body">A / B / C @ <strong>33 / 33 / 34</strong> three-way baseline</div>
    </div>
    <div class="callout">
      <div class="label">Friday onwards</div>
      <div class="body">A / B / C / D @ <strong>25 / 25 / 25 / 25</strong> full four-way split</div>
    </div>
  </div>
</div>

<div class="page-block" style="--accent:#a855f7;">
  <h4>Architecture — the 12-persona, 5-judge ensemble</h4>
  <p>The Council is built as 12 writer personas with distinct voices plus 5 judges that rank outputs. Each draft is reviewed before it lands in Smartlead.</p>

  <h4>The 12 writer personas</h4>
  <table>
    <thead><tr><th>Persona</th><th>Voice notes</th></tr></thead>
    <tbody>
      <tr><td><strong>Hormozi-blunt</strong></td><td>Short sentences, dollar amounts, no metaphors</td></tr>
      <tr><td><strong>Ogilvy-classy</strong></td><td>Long-form, story-first, sophisticated cadence</td></tr>
      <tr><td><strong>NPR-warm</strong></td><td>Conversational, hedged, friendly</td></tr>
      <tr><td><strong>Founder-confidant</strong></td><td>Peer-to-peer tone, low status games</td></tr>
      <tr><td><strong>Local-specialist</strong></td><td>Mentions city, regional details, neighbor-of vibes</td></tr>
      <tr><td><strong>Data-nerd</strong></td><td>Leads with numbers, hard claims, no fluff</td></tr>
      <tr><td><strong>Curiosity-gap</strong></td><td>Opens with a question, withholds offer until line 4</td></tr>
      <tr><td><strong>Brutus-forwarded</strong></td><td>Email body IS the forwarded Cara research</td></tr>
      <tr><td><strong>Negative-frame</strong></td><td>Leads with what they're losing</td></tr>
      <tr><td><strong>Peer-signal</strong></td><td>References competitor / peer firm activity</td></tr>
      <tr><td><strong>Pilot-pitch</strong></td><td>Frames as "rolling out to 8 firms this month"</td></tr>
      <tr><td><strong>One-question-short</strong></td><td>Five lines max, single yes/no ask</td></tr>
    </tbody>
  </table>

  <h4>The 5 judges</h4>
  <p>Each draft passes 5 judges scoring on different axes:</p>
  <ol>
    <li><strong>Clarity</strong> — would a busy founder read this without skimming?</li>
    <li><strong>Specificity</strong> — is the personalization real or generic?</li>
    <li><strong>No-template-feel</strong> — does it read like a human wrote it for them?</li>
    <li><strong>CTA strength</strong> — is the ask clear and low-friction?</li>
    <li><strong>Brand fit</strong> — does it match Neal's voice and FlowOps positioning?</li>
  </ol>

  <p>Each judge scores 0-10. The draft with the highest composite score wins and is written to Smartlead. Below a composite threshold of 35/50, the lead is flagged for manual review instead of auto-send.</p>
</div>
""",

# ============ SECTION 6 ============
divider("06", "Magnet Generation", "The 4 variants. A IntakeBot. B FlowScore. C Mockup. D Direct Audit.", "#a855f7"),

"""
<div class="page-block" style="--accent:#a855f7;">
  <div class="subtitle">Section 06 · Stage 3.5 · The Magnets</div>
  <h3 class="section-h"><span class="num">06</span>Magnet Generation — 4 Variants</h3>

  <p>Each variant is psychologically distinct. They differ on what the lead must DO (click vs read vs quiz vs reply) and what we're testing (engagement vs data appetite vs visual proof vs raw offer).</p>

  <h4>Variant A — IntakeBot URL</h4>
  <div class="callout" style="--accent:#22d3ee;">
    <div class="label">Concept</div>
    <div class="body">Send the lead to a live demo of an AI receptionist customized to their niche.</div>
  </div>
  <table>
    <tbody>
      <tr><td><strong>URL</strong></td><td><code>intakebot.vercel.app/for/{niche}</code></td></tr>
      <tr><td><strong>Cost</strong></td><td>$0 (static demo, Vercel free tier)</td></tr>
      <tr><td><strong>Magnet asset</strong></td><td>N/A (link only)</td></tr>
      <tr><td><strong>Status</strong></td><td><span class="pill pill-green">Live</span></td></tr>
      <tr><td><strong>What we measure</strong></td><td>Click-through rate. Engaged users → high-intent segment.</td></tr>
    </tbody>
  </table>

  <h4>Variant B — FlowScore</h4>
  <div class="callout" style="--accent:#a855f7;">
    <div class="label">Concept</div>
    <div class="body">Run their site through the REAL FlowScore API and email them their actual score, biggest gap, and dollar leak.</div>
  </div>
  <table>
    <tbody>
      <tr><td><strong>API</strong></td><td>Supabase Edge Function behind <code>flowoperations.ai/flowscore</code></td></tr>
      <tr><td><strong>Returns</strong></td><td>overall_score (0-100), score_range (red/amber/green), interpretation, estimated_monthly_revenue_leakage, 8 dimension sub-scores</td></tr>
      <tr><td><strong>Cost</strong></td><td>$0 (Neal's existing product)</td></tr>
      <tr><td><strong>Status</strong></td><td><span class="pill pill-amber">Wiring</span></td></tr>
    </tbody>
  </table>
  <p>Three sub-splits within Variant B:</p>
  <ul>
    <li><strong>B1 Call-first:</strong> "Your FlowScore is X/100. Here's your biggest gap. 15 min?"</li>
    <li><strong>B2 Report-or-call:</strong> "Reply REPORT for the 8-page PDF, REPLY CALL for 15 min"</li>
    <li><strong>B3 PDF-then-call:</strong> Email 1 = score teaser. Email 2 = the PDF + "now that you've seen it, 15 min?"</li>
  </ul>
</div>

<div class="page-block" style="--accent:#a855f7;">
  <h4>Variant C — Website Mockup</h4>
  <div class="callout" style="--accent:#f472b6;">
    <div class="label">Concept</div>
    <div class="body">Redesign their actual homepage with Gemini 3 Pro Image. Single tall vertical screenshot, top-to-bottom. Send inline.</div>
  </div>
  <table>
    <tbody>
      <tr><td><strong>Tool</strong></td><td><code>google/gemini-3-pro-image-preview</code> via OpenRouter</td></tr>
      <tr><td><strong>Layout</strong></td><td>Single tall vertical screenshot (portrait 1440×3200), continuous column</td></tr>
      <tr><td><strong>Niche design language</strong></td><td>navy+gold (wealth), rose+cream (medspa), black+gold (PI_law), warm-amber (mortgage), navy+blue (financial), sky+white (insurance)</td></tr>
      <tr><td><strong>Hosting</strong></td><td><code>flowops-assets.vercel.app/mockups/&lt;slug&gt;.png</code> · CORS enabled · 1yr cache</td></tr>
      <tr><td><strong>Cost</strong></td><td><strong>$0.06 / mockup</strong> · ~$40-200/mo at production volume</td></tr>
      <tr><td><strong>Status</strong></td><td><span class="pill pill-green">Live · 77 mockups pre-generated</span></td></tr>
    </tbody>
  </table>

  <div class="figure">
    <img src="""" + MERCER_IMG + """" alt="Mercer Wealth mockup">
    <div class="caption">Sample Variant C output — Mercer Wealth Management, vertical screenshot. Hero, services grid, testimonial, founder section, CTA, footer.</div>
  </div>
</div>

<div class="page-block" style="--accent:#a855f7;">
  <h4>Variant D — Direct AI Audit Pilot</h4>
  <div class="callout" style="--accent:#f59e0b;">
    <div class="label">Concept</div>
    <div class="body">No magnet asset. Pure offer-led framing: "Free 20-min AI Audit. We want the case study. Want it?"</div>
  </div>
  <table>
    <tbody>
      <tr><td><strong>Magnet asset</strong></td><td>None — offer-led, not value-led</td></tr>
      <tr><td><strong>Cost to generate</strong></td><td>$0 (consumes Neal's call time on conversion)</td></tr>
      <tr><td><strong>Status</strong></td><td><span class="pill pill-amber">Friday rollout</span></td></tr>
      <tr><td><strong>Predicted performance</strong></td><td>Highest reply rate, lowest click rate, similar book rate to B+C. Removes all friction.</td></tr>
    </tbody>
  </table>

  <h4>Variant D copy (truncated)</h4>
  <pre>Subject: free AI audit for {{company_name}}?

Hey {{first_name}},

Quick one. Running a pilot this month - building free
20-min AI Audits for 8 {{niche_label}} founders. We're
looking for case studies.

The audit:
- Map your current ops top to bottom
- Find the 3-5 places AI saves 10+ hours a week
- Walk you through the dollar impact ({{leak_range}}/mo)
- Hand you the implementation plan to keep

Plan is yours to keep. Free. No catch - we want the case
study + permission to use {{company_name}} as reference.

{{company_name}} looks like a fit. 20 min next week?

Neal</pre>

  <h4>Variant economics — full comparison</h4>
  <table>
    <thead><tr><th>Variant</th><th>What lead must do</th><th>Friction</th><th>Cost</th><th>Predicted reply rate</th></tr></thead>
    <tbody>
      <tr><td>A · IntakeBot</td><td>Click + explore demo</td><td>Medium</td><td>$0</td><td>2.0%</td></tr>
      <tr><td>B · FlowScore</td><td>Take a 60-sec quiz</td><td>High</td><td>$0</td><td>1.5%</td></tr>
      <tr><td>C · Mockup</td><td>Look at an image</td><td>Low</td><td>$0.06</td><td>2.5%</td></tr>
      <tr><td>D · Direct Audit</td><td>Just reply "yes"</td><td>Lowest</td><td>$0</td><td>3.5%</td></tr>
    </tbody>
  </table>
</div>
""",

# ============ SECTION 7 ============
divider("07", "Copy Generation", "The Council writes the 4-step sequence. Cara signal opener, niche pain, variant pitch, CTA.", "#a855f7"),

"""
<div class="page-block" style="--accent:#a855f7;">
  <div class="subtitle">Section 07 · Stage 4 · The Words</div>
  <h3 class="section-h"><span class="num">07</span>Copy Generation</h3>

  <p>The Council writes the full 4-step sequence per lead. Each email follows a consistent structural template but reads as unique copy because every field is rewritten from real signals.</p>

  <h4>Per-email structure</h4>
  <ol>
    <li><strong>Personalized opener</strong> — derived from Cara signal (job change, news, peer activity, tech stack)</li>
    <li><strong>Role-specific pain</strong> — niche-aware, sometimes persona-aware (CEO vs ops lead)</li>
    <li><strong>Magnet pitch</strong> — varies by variant A/B/C/D</li>
    <li><strong>CTA</strong> — also varies by variant (call / quiz / look / reply)</li>
    <li><strong>Cara forwarded research</strong> — only in V1 and V6 of Acquisity variants, optional elsewhere</li>
    <li><strong>Signature</strong> — persona name from the sender inbox + Neal's calendar link in footer</li>
  </ol>

  <h4>Followup cadence (same across all variants)</h4>
  <table>
    <thead><tr><th>Step</th><th>Day</th><th>Subject</th><th>Angle</th></tr></thead>
    <tbody>
      <tr><td>1</td><td>0</td><td>Variant-specific</td><td>Main pitch + magnet</td></tr>
      <tr><td>2</td><td>+3</td><td><code>re: the $X/mo leak</code></td><td>Quick follow-up, different angle</td></tr>
      <tr><td>3</td><td>+5</td><td><code>worth 15 min or not?</code></td><td>Close the loop, either answer fine</td></tr>
      <tr><td>4</td><td>+7</td><td><code>last note, {first_name}</code></td><td>Breakup, calendar link in footer</td></tr>
    </tbody>
  </table>

  <h4>Model usage</h4>
  <table>
    <thead><tr><th>Use case</th><th>Model</th><th>Why</th></tr></thead>
    <tbody>
      <tr><td>Per-lead drafts (80% of generations)</td><td>Gemini 2.0 Flash</td><td>Cheap, fast, good enough for personalization</td></tr>
      <tr><td>High-value leads, hard niches</td><td>Sonnet 4.5</td><td>Better at subtle voice + judgment</td></tr>
      <tr><td>Judge consensus (Council)</td><td>Sonnet 4.5</td><td>Score consistency across the 5 axes</td></tr>
      <tr><td>Variant C mockups</td><td>Gemini 3 Pro Image</td><td>Best image gen for site mockups</td></tr>
      <tr><td>Reply classification</td><td>Sonnet 4.5</td><td>Nuance on positive vs negative replies</td></tr>
    </tbody>
  </table>

  <div class="callout">
    <div class="label">Universal rule</div>
    <div class="body">All LLM calls in every FlowOps project MUST route through OpenRouter when the model is available there. Hardcoded across every codebase. No direct calls to Anthropic, Google, or OpenAI APIs.</div>
  </div>
</div>
""",

# ============ SECTION 8 ============
divider("08", "Send", "Smartlead. 10 persona inboxes. 4am-12pm ET window. 400/day capacity.", "#3b82f6"),

"""
<div class="page-block" style="--accent:#3b82f6;">
  <div class="subtitle">Section 08 · Stage 5 · The Send</div>
  <h3 class="section-h"><span class="num">08</span>Send · Smartlead</h3>

  <p>Smartlead is the sequence engine. 10 warmed persona inboxes spread across 2 domains. Each inbox capped at 40 sends/day = <strong>400/day total capacity</strong>.</p>

  <h4>10 persona inboxes</h4>
  <table>
    <thead><tr><th>Persona</th><th>Email</th><th>Domain</th><th>Daily cap</th></tr></thead>
    <tbody>
      <tr><td>Lilly Smith</td><td>lilly@flowoperations.org</td><td>flowoperations.org</td><td>40</td></tr>
      <tr><td>Priya Iyer</td><td>priya@flowoperations.org</td><td>flowoperations.org</td><td>40</td></tr>
      <tr><td>Ryan Mitchell</td><td>ryan@flowoperations.org</td><td>flowoperations.org</td><td>40</td></tr>
      <tr><td>Ashley Cole</td><td>ashley@flowoperations.org</td><td>flowoperations.org</td><td>40</td></tr>
      <tr><td>Neal Thakkar</td><td>nealt@flowoperations.org</td><td>flowoperations.org</td><td>40</td></tr>
      <tr><td>Roddy Greene</td><td>roddy@flowopsleadgen.com</td><td>flowopsleadgen.com</td><td>40</td></tr>
      <tr><td>Mason Park</td><td>mason@flowopsleadgen.com</td><td>flowopsleadgen.com</td><td>40</td></tr>
      <tr><td>John Davis</td><td>john@flowopsleadgen.com</td><td>flowopsleadgen.com</td><td>40</td></tr>
      <tr><td>Carly Bennett</td><td>carly@flowopsleadgen.com</td><td>flowopsleadgen.com</td><td>40</td></tr>
      <tr><td>Neal (alt)</td><td>neal@flowopsleadgen.com</td><td>flowopsleadgen.com</td><td>40</td></tr>
    </tbody>
  </table>

  <h4>Send window + safety</h4>
  <ul>
    <li><strong>Time:</strong> 4 AM – 12 PM ET (8-hour window)</li>
    <li><strong>Days:</strong> 7 days/week</li>
    <li><strong>Min time between emails per inbox:</strong> 5 min</li>
    <li><strong>From-name:</strong> Persona (Lilly Smith, etc.) — body signs off as Neal</li>
    <li><strong>BCC:</strong> neal@flowoperations.ai gets a copy of every outbound</li>
    <li><strong>Stop-trigger:</strong> reply to ANY email pauses the whole sequence for that lead</li>
  </ul>
</div>

<div class="page-block" style="--accent:#3b82f6;">
  <h4>Active campaigns</h4>
  <table>
    <thead><tr><th>Niche</th><th>Campaign ID</th><th>Status</th><th>Leads in queue</th></tr></thead>
    <tbody>
      <tr><td>WEALTH</td><td><code>3263730</code></td><td><span class="pill pill-green">Active</span></td><td>2,072</td></tr>
      <tr><td>FINANCIAL</td><td><code>3191292</code></td><td><span class="pill pill-green">Active</span></td><td>2,894</td></tr>
      <tr><td>MORTGAGE</td><td><code>3191290</code></td><td><span class="pill pill-green">Active</span></td><td>1,768</td></tr>
      <tr><td>INSURANCE</td><td><code>3191291</code></td><td><span class="pill pill-green">Active</span></td><td>86</td></tr>
      <tr><td>MCA</td><td><code>3263732</code></td><td><span class="pill pill-green">Active</span></td><td>legacy</td></tr>
      <tr><td>COMMLOAN</td><td><code>3263731</code></td><td><span class="pill pill-green">Active</span></td><td>legacy</td></tr>
      <tr><td>MEDSPA</td><td><code>3191285</code></td><td><span class="pill pill-amber">Paused</span></td><td>1</td></tr>
      <tr><td>PI_LAW</td><td><code>3327115</code></td><td><span class="pill pill-grey">Drafted</span></td><td>0</td></tr>
      <tr><td>RECRUITER</td><td><code>3191293</code></td><td><span class="pill pill-amber">Paused</span></td><td>0</td></tr>
    </tbody>
  </table>

  <h4>Deliverability watch</h4>
  <p>Smartlead reports per-inbox health daily. The 5-7 day deliverability window after raising per-inbox cap from 30 → 40 is the highest-risk period. Triggers for rollback to 35/day:</p>
  <ul>
    <li>Bounce rate &gt; 2.5% on any 24-hour window</li>
    <li>Any inbox flagged "warming" status returning to "fresh"</li>
    <li>Reply rate dropping by &gt; 30% week-over-week (likely spam folder)</li>
  </ul>

  <div class="callout">
    <div class="label">Acquisity parallel pipeline</div>
    <div class="body">Acquisity sends through their own infrastructure (not Smartlead's inboxes). At 400/day Acquisity + 400/day Smartlead, the system runs two isolated pipelines — no deliverability overlap, combined 800/day capacity with full domain reputation isolation.</div>
  </div>
</div>
""",

# ============ SECTION 9 ============
divider("09", "Auto-Reply", "Webhook + LLM classifier. 90-second SLA from inbound to drafted response.", "#3b82f6"),

"""
<div class="page-block" style="--accent:#3b82f6;">
  <div class="subtitle">Section 09 · Stage 6 · The Response Layer</div>
  <h3 class="section-h"><span class="num">09</span>Auto-Reply</h3>

  <p><strong>Goal:</strong> Reply to inbound emails within 90 seconds. Classify, draft a response, route to Neal's inbox for review.</p>

  <h4>The flow</h4>
  <ol>
    <li>Lead replies → Smartlead receives</li>
    <li>Smartlead webhook fires <code>EMAIL_REPLY</code> event</li>
    <li>Cloudflare Tunnel forwards to local FastAPI service on port 8787</li>
    <li>LLM classifier (Sonnet 4.5) categorizes the reply</li>
    <li>Based on category, a draft response is generated</li>
    <li>Draft lands in Neal's Smartlead inbox as a DRAFT (not auto-sent)</li>
    <li>Neal reviews + sends</li>
  </ol>

  <h4>Reply categories + handler logic</h4>
  <table>
    <thead><tr><th>Category</th><th>Trigger</th><th>Draft action</th></tr></thead>
    <tbody>
      <tr><td><strong>INTERESTED</strong></td><td>"yes", "tell me more", "send the report", "let's chat"</td><td>Drafts response with GHL booking link inline</td></tr>
      <tr><td><strong>NOT_INTERESTED</strong></td><td>"not interested", "remove me", "wrong fit"</td><td>Drafts polite close, marks lead as do-not-contact</td></tr>
      <tr><td><strong>OUT_OF_OFFICE</strong></td><td>OOO auto-reply detected</td><td>Flags lead for re-send when they're back</td></tr>
      <tr><td><strong>WRONG_PERSON</strong></td><td>"not the right contact"</td><td>Drafts referral ask</td></tr>
      <tr><td><strong>QUESTION</strong></td><td>Specific question about offering</td><td>Drafts answer + maintains conversation</td></tr>
    </tbody>
  </table>

  <h4>Status</h4>
  <ul>
    <li><span class="pill pill-green">Live</span> Webhook registered on 9 campaigns</li>
    <li><span class="pill pill-amber">Tunnel ephemeral</span> Currently <code>additional-accessibility-marker-ada.trycloudflare.com</code> — needs persistent named tunnel for prod</li>
  </ul>

  <h4>Persistent tunnel upgrade path</h4>
  <pre># One-time
brew install cloudflared
cloudflared tunnel login
cloudflared tunnel create flowops-reply

# DNS — point a subdomain at the tunnel
cloudflared tunnel route dns flowops-reply reply.flowoperations.ai

# Run as a service (LaunchDaemon on macOS)
cloudflared tunnel run --url http://127.0.0.1:8787 flowops-reply</pre>
</div>
""",

# ============ SECTION 10 ============
divider("10", "Booked Call", "GHL widget. Slack notification. Pre-call brief. Outcome tracking.", "#22c55e"),

"""
<div class="page-block" style="--accent:#22c55e;">
  <div class="subtitle">Section 10 · Stage 7 · Revenue</div>
  <h3 class="section-h"><span class="num">10</span>Booked Call</h3>

  <p><strong>Goal:</strong> Convert positive replies into 15-20 minute discovery calls on Neal's calendar.</p>

  <h4>The flow</h4>
  <ol>
    <li>Auto-reply drops GHL booking link in response</li>
    <li>Lead clicks → GHL widget renders</li>
    <li>Lead picks slot → GHL creates calendar event on Neal's Google Calendar</li>
    <li>Slack notification fires to <code>#booked-calls</code> channel with lead summary</li>
    <li>Pre-call brief auto-generated (Cara dossier + reply history + suggested talking points)</li>
    <li>Call happens, outcome logged to CRM (Notion + GHL)</li>
  </ol>

  <h4>Pre-call brief auto-generation</h4>
  <p>Triggered when a calendar event is created. Composes a 1-page brief delivered to Neal via Slack DM 30 minutes before the call:</p>
  <pre>===========================================
PRE-CALL BRIEF — Robert Mendez (UFC 4 Wealth)
Scheduled: 2026-05-14 10:00 AM ET (15 min)
===========================================

WHO THEY ARE
Founder/CEO at UFC 4 Wealth, Austin TX
Wealth management, RIA, $50M AUM (LinkedIn)
Joined company Sept 2024

WHY THEY REPLIED
Engaged with Variant C (Mockup) on 2026-05-13
Reply: "this is impressive. tell me more about the audit"

WHAT TO PUSH
- Free 20-min audit pitch (resonates given his reply)
- Lead with the FlowScore breakdown (we have his data)
- Specific gap: CRM &amp; Booking Integration scored 20/100

POSSIBLE OBJECTIONS
- "We already use Wealthbox" - acknowledge, audit covers integration
- "Send a proposal first" - offer Loom walkthrough as middle ground

REFERENCES TO CITE
- Lion's Share Wealth (similar AUM, similar Form D activity)
- ClearPath Advisors (Austin-based, same metro)</pre>
</div>
""",

# ============ SECTION 11 ============
divider("11", "Metrics Loop", "Surface what works. Kill what doesn't. Feed back into Strategy Council.", "#f59e0b"),

"""
<div class="page-block" style="--accent:#f59e0b;">
  <div class="subtitle">Section 11 · Stage 8 · The Brain Feeds Itself</div>
  <h3 class="section-h"><span class="num">11</span>Metrics Loop</h3>

  <p><strong>Goal:</strong> Aggregate daily and 7-day performance per niche × variant. Surface winners, kill losers, feed back into Stage 3.0 (Strategy Council) so tomorrow's variant assignments are smarter than yesterday's.</p>

  <h4>What we track</h4>
  <table>
    <thead><tr><th>Metric</th><th>Source</th><th>Cadence</th></tr></thead>
    <tbody>
      <tr><td>Sends</td><td>Smartlead /statistics</td><td>real-time</td></tr>
      <tr><td>Opens</td><td>Smartlead</td><td>real-time</td></tr>
      <tr><td>Clicks</td><td>Smartlead</td><td>real-time</td></tr>
      <tr><td>Replies</td><td>Smartlead</td><td>real-time</td></tr>
      <tr><td>Reply category</td><td>Reply classifier output</td><td>~90 sec from reply</td></tr>
      <tr><td>Bounces</td><td>Smartlead</td><td>real-time</td></tr>
      <tr><td>Booked calls</td><td>GHL → Slack webhook</td><td>real-time</td></tr>
      <tr><td>Cost per booked call</td><td>spend ÷ calls</td><td>daily rollup</td></tr>
    </tbody>
  </table>

  <h4>Verdict labels</h4>
  <ul>
    <li><span class="pill pill-green">HEALTHY</span> reply &gt; 0.8%, bounce &lt; 5%, sent &gt; 100</li>
    <li><span class="pill pill-amber">ITERATE</span> outside thresholds, needs copy review</li>
    <li><span class="pill pill-grey">WAIT_FOR_DATA</span> &lt; 100 sends, no verdict yet</li>
  </ul>

  <h4>Dashboard architecture</h4>
  <ul>
    <li><strong>Frontend:</strong> Lovable single-page app (dark mode, Bloomberg-meets-Linear vibe)</li>
    <li><strong>Backend:</strong> FastAPI (<code>metrics_api.py</code>) on port 8788</li>
    <li><strong>Tunnel:</strong> Cloudflare Tunnel (ephemeral or persistent)</li>
    <li><strong>Refresh:</strong> every 30 seconds via polling</li>
  </ul>

  <h4>Endpoints</h4>
  <pre>GET /dashboard/summary    one-shot, returns everything below
GET /metrics/today        per-niche stats for last 24h
GET /metrics/7d           7-day rolling + verdict per niche
GET /metrics/niche/{n}    detail per niche (today / 7d / 30d)
GET /variants/performance A/B/C/D breakdown across all campaigns
GET /leads/recent         last N replies + clicks
GET /spend                OpenRouter + Apify usage
GET /campaigns            all campaigns + lead counts</pre>

  <h4>Nightly Council review</h4>
  <p>Runs at 1 AM ET. Aggregates the day's metrics. The Council picks winning variants per niche. Adjusts weights in Stage 3.0 strategy decisions — slightly downweights losers, upweights winners. All decisions logged to <code>/tmp/council/decisions/&lt;date&gt;.json</code> for auditability.</p>
</div>
""",

# ============ SECTION 12 ============
divider("12", "Tech Stack", "Discovery. Enrichment. Storage. Hosting. Automation. Everything routes through OpenRouter.", "#3b82f6"),

"""
<div class="page-block" style="--accent:#3b82f6;">
  <div class="subtitle">Section 12 · The Toolchain</div>
  <h3 class="section-h"><span class="num">12</span>Tech Stack</h3>

  <p>End-to-end stack, layered from data sources at the bottom to the user-facing dashboard at the top.</p>

  <div class="stack">
    <div class="stack-layer" style="--layer-color:#22d3ee;">
      <div class="layer-name">Layer 1 — Discovery</div>
      <div class="layer-content">Apify (Google Maps scraper) · n8n (cron orchestration) · Acquisity (purchased lists) · Manual seeding (Notion intake)</div>
    </div>
    <div class="stack-layer" style="--layer-color:#a855f7;">
      <div class="layer-name">Layer 2 — AI &amp; Enrichment</div>
      <div class="layer-content"><strong>OpenRouter (universal gateway)</strong> · Gemini 2.0 Flash (Council writes, Cara research) · Sonnet 4.5 (judges, classifiers) · Gemini 3 Pro Image (mockups) · Playwright (site scraping + tech stack sniffer)</div>
    </div>
    <div class="stack-layer" style="--layer-color:#3b82f6;">
      <div class="layer-name">Layer 3 — Storage &amp; State</div>
      <div class="layer-content">Smartlead (lead DB + sequence engine) · Smartlead custom_fields (personalization vars) · Local ~/.council/ (decisions, cache, logs) · SQLite (dedup index)</div>
    </div>
    <div class="stack-layer" style="--layer-color:#f472b6;">
      <div class="layer-name">Layer 4 — Hosting</div>
      <div class="layer-content">intakebot.vercel.app (Variant A magnet) · flowops-assets.vercel.app (Variant C mockups + team photos) · flowoperations.ai/flowscore (Variant B magnet) · Lovable (dashboard + SOP visualizer)</div>
    </div>
    <div class="stack-layer" style="--layer-color:#22c55e;">
      <div class="layer-name">Layer 5 — Automation &amp; Integrations</div>
      <div class="layer-content">Smartlead webhooks (EMAIL_REPLY) · Cloudflare Tunnel (expose local FastAPI services) · n8n (Apify cron + Cara enrichment chains) · GoHighLevel (booking + CRM) · Slack (notifications)</div>
    </div>
    <div class="stack-layer" style="--layer-color:#f59e0b;">
      <div class="layer-name">Layer 6 — Observability</div>
      <div class="layer-content">FastAPI metrics_api.py · Lovable dashboard · Notion ops log · Slack #booked-calls channel · Local /tmp/council/decisions/ JSON audit trail</div>
    </div>
  </div>

  <h4>Universal rule</h4>
  <div class="callout">
    <div class="label">Hardcoded across every project</div>
    <div class="body"><strong>All LLM calls in every FlowOperations project MUST route through OpenRouter when the model is available there.</strong> No direct calls to Anthropic, Google, or OpenAI APIs. This is non-negotiable — applies to all future builds.</div>
  </div>
</div>
""",

# ============ SECTION 13 ============
divider("13", "Cost Model", "$250-500/mo total. $4.50 per booked call at realistic tier. 10-40x cheaper than paid.", "#22c55e"),

"""
<div class="page-block" style="--accent:#22c55e;">
  <div class="subtitle">Section 13 · The Numbers</div>
  <h3 class="section-h"><span class="num">13</span>Cost Model</h3>

  <h4>Monthly recurring (current state, 400 Smartlead sends/day)</h4>
  <table>
    <thead><tr><th>Item</th><th>Cost</th><th>Notes</th></tr></thead>
    <tbody>
      <tr><td>Smartlead Pro</td><td>$97/mo</td><td>10 inboxes</td></tr>
      <tr><td>OpenRouter (Gemini Flash + Sonnet)</td><td>$30-80/mo</td><td>Variable</td></tr>
      <tr><td>Apify</td><td>$60-90/mo</td><td>150 leads/day</td></tr>
      <tr><td>Variant C mockups</td><td>$40-200/mo</td><td>$0.06 × Variant C sends</td></tr>
      <tr><td>Vercel</td><td>$0</td><td>Free tier for static</td></tr>
      <tr><td>n8n</td><td>$20/mo</td><td>Starter</td></tr>
      <tr><td>GHL</td><td>—</td><td>Reused, Neal's existing</td></tr>
      <tr><td><strong>Total</strong></td><td><strong>~$250-500/mo</strong></td><td>At 400 sends/day</td></tr>
    </tbody>
  </table>

  <h4>Cost per booked call (realistic tier @ 90 days)</h4>
  <p><strong>$400/mo total cost ÷ 90 calls/mo = $4.45 per booked call.</strong></p>
  <p>Industry benchmark for qualified calls via paid advertising: $50-200 per call. <strong>FlowOps is 11-45x cheaper per call.</strong> This is the moat.</p>

  <h4>Cost-to-revenue ratio at realistic tier</h4>
  <table>
    <tbody>
      <tr><td>Monthly cost</td><td>$400</td></tr>
      <tr><td>Monthly revenue (180 calls × 30% close × $8K avg deal)</td><td>$432,000</td></tr>
      <tr><td><strong>Cost ratio</strong></td><td><strong>0.09%</strong></td></tr>
    </tbody>
  </table>

  <h4>800/day projections (after Acquisity online)</h4>
  <table>
    <thead><tr><th>Tier</th><th>Calls/day</th><th>Calls/mo</th><th>Mo revenue @ $8K</th><th>Cost ratio</th></tr></thead>
    <tbody>
      <tr><td>Conservative</td><td>2-4</td><td>60-120</td><td>$144K-$288K</td><td>~0.5%</td></tr>
      <tr><td>Realistic</td><td>5-7</td><td>150-210</td><td>$360K-$504K</td><td>~0.3%</td></tr>
      <tr><td>Optimistic</td><td>12-15</td><td>350-450</td><td>$840K-$1.08M</td><td>~0.2%</td></tr>
    </tbody>
  </table>

  <div class="callout">
    <div class="label">Where the constraint moves at 800/day</div>
    <div class="body">At realistic tier (~6 calls/day), Neal's personal call capacity becomes the bottleneck. The right next move is building a discovery-call scoring rubric, taking only the top 50% of bookings, and routing the rest to a Loom + email-only flow.</div>
  </div>
</div>
""",

# ============ SECTION 14 ============
divider("14", "Runbooks", "How to start it. How to stop it. How to fix it.", "#3b82f6"),

"""
<div class="page-block" style="--accent:#3b82f6;">
  <div class="subtitle">Section 14 · Operations</div>
  <h3 class="section-h"><span class="num">14</span>Runbooks &amp; Glossary</h3>

  <h4>Morning check (every day 8 AM ET)</h4>
  <pre>cd ~/Desktop/council
python3 morning_check.py</pre>
  <p>Outputs: lead counts per campaign, % with empty personalization, send window status.</p>

  <h4>Pre-generate mockups for tomorrow's Variant C</h4>
  <pre>cd ~/Desktop/council
.venv-server/bin/python mockup_batch_run.py</pre>
  <p>~$5 cost, ~15 min runtime, populates 80-120 mockups.</p>

  <h4>Run an Acquisity import</h4>
  <pre>cd ~/Desktop/council
python3 bulk_import.py ~/Downloads/&lt;acquisity_file&gt;.csv \\
  --niche RECRUITER</pre>

  <h4>Restart auto-reply tunnel + server</h4>
  <pre>pkill -f cloudflared
nohup .venv-server/bin/uvicorn webhook_server:app \\
  --port 8787 &gt; ~/.council/webhook.log 2&gt;&amp;1 &amp;
nohup cloudflared tunnel \\
  --url http://127.0.0.1:8787 \\
  &gt; ~/.council/tunnel.log 2&gt;&amp;1 &amp;

# Get the new public URL
grep -oE "https://[a-z0-9-]+\\.trycloudflare\\.com" \\
  ~/.council/tunnel.log | tail -1</pre>

  <h4>Restart metrics API for Lovable</h4>
  <pre>nohup .venv-server/bin/uvicorn metrics_api:app \\
  --port 8788 &gt; ~/.council/metrics_api.log 2&gt;&amp;1 &amp;
nohup cloudflared tunnel \\
  --url http://127.0.0.1:8788 \\
  &gt; ~/.council/metrics_tunnel.log 2&gt;&amp;1 &amp;</pre>

  <h4>Pause a misbehaving campaign</h4>
  <pre>POST https://server.smartlead.ai/api/v1/campaigns/{cid}/status?api_key={KEY}
Body: {"status":"PAUSED"}</pre>
</div>

<div class="page-block" style="--accent:#3b82f6;">
  <h4>Glossary</h4>
  <table>
    <thead><tr><th>Term</th><th>Meaning</th></tr></thead>
    <tbody>
      <tr><td><strong>Variant</strong></td><td>One of 4 magnet types (A IntakeBot / B FlowScore / C Mockup / D Direct Audit)</td></tr>
      <tr><td><strong>Niche</strong></td><td>A vertical / ICP segment (WEALTH, FINANCIAL, MORTGAGE, etc.)</td></tr>
      <tr><td><strong>Persona inbox</strong></td><td>One of 10 Smartlead sender inboxes (each is a real Gmail account on a warmed domain)</td></tr>
      <tr><td><strong>Cara</strong></td><td>AI research agent persona (hello@carabarone.com) used in forwarded-research email format</td></tr>
      <tr><td><strong>Council</strong></td><td>12-persona + 5-judge LLM ensemble that writes per-lead copy</td></tr>
      <tr><td><strong>FlowScore</strong></td><td>0-100 ops audit score from flowoperations.ai/flowscore (Supabase Edge Fn)</td></tr>
      <tr><td><strong>OpenRouter</strong></td><td>Universal LLM gateway. All FlowOps LLM calls route through here. Hardcoded.</td></tr>
      <tr><td><strong>IntakeBot</strong></td><td>AI receptionist product, served at intakebot.vercel.app, used as Variant A magnet</td></tr>
      <tr><td><strong>Acquisity</strong></td><td>Third-party purchased lead provider, run through parallel sending pipeline</td></tr>
      <tr><td><strong>FigJam SOP</strong></td><td>Living diagram at figma.com/board/kkhkStGCh5VgxA0uV8Untv</td></tr>
    </tbody>
  </table>

  <h4>Document version</h4>
  <table>
    <tbody>
      <tr><td><strong>Edition</strong></td><td>1.0</td></tr>
      <tr><td><strong>Generated</strong></td><td>2026-05-13</td></tr>
      <tr><td><strong>Owner</strong></td><td>Neal Thakkar · neal@flowoperations.ai</td></tr>
      <tr><td><strong>Source markdown</strong></td><td><code>~/Desktop/council/FLOWOPS_SOP_DETAILED.md</code></td></tr>
      <tr><td><strong>Source FigJam</strong></td><td><code>figma.com/board/kkhkStGCh5VgxA0uV8Untv</code></td></tr>
      <tr><td><strong>Classification</strong></td><td>Confidential — Internal use only</td></tr>
    </tbody>
  </table>

  <div style="margin-top: 28pt; padding-top: 14pt; border-top: 1px solid #1e293b; text-align:center; color:#64748b; font-size:9pt;">
    <strong style="color:#3b82f6; letter-spacing:0.2em;">FLOW OPERATIONS</strong> · Cold Email Pipeline · End of document
  </div>
</div>
""",

"</body></html>"
    ]
    return "\n".join(parts)


def render():
    from playwright.sync_api import sync_playwright

    html = build_html()
    html_path = OUT_DIR / "sop.html"
    html_path.write_text(html)
    print(f"HTML: {html_path} ({len(html):,} bytes)")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1100, "height": 1500})
        page = ctx.new_page()
        page.goto(f"file://{html_path}", wait_until="networkidle")
        # wait for fonts
        time.sleep(2)
        page.pdf(
            path=str(OUT_PDF),
            format="Letter",
            print_background=True,
            margin={"top":"0in","right":"0in","bottom":"0in","left":"0in"},
            prefer_css_page_size=True,
        )
        ctx.close()
        browser.close()

    size_mb = OUT_PDF.stat().st_size / 1024 / 1024
    print(f"\n✅ PDF: {OUT_PDF}")
    print(f"   Size: {size_mb:.1f} MB")


if __name__ == "__main__":
    render()
