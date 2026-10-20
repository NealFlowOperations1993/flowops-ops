import { useState, useMemo } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { CopyBlock } from "@/components/trident/CopyBlock";
import { Printer, ChevronDown, ChevronRight, ExternalLink } from "lucide-react";

/* =========================================================
   FlowOps Cold Email — Interactive SOP Visualizer
   Self-contained page. Hardcoded content for v1.
   Scoped color palette via inline styles (no token pollution).
   ========================================================= */

const C = {
  bg: "hsl(222 47% 4%)",
  surface: "hsl(222 47% 7%)",
  surface2: "hsl(222 40% 10%)",
  border: "hsl(222 30% 18%)",
  text: "#EDF4FF",
  muted: "#8FA0BD",
  blue: "#3B82F6",
  cyan: "#22D3EE",
  violet: "#A855F7",
  pink: "#F472B6",
  green: "#22C55E",
  amber: "#F59E0B",
  red: "#EF4444",
};

type Status = "LIVE" | "FRIDAY" | "WIRING" | "BUILDING" | "READY";
const statusColor: Record<Status, string> = {
  LIVE: C.green,
  FRIDAY: C.amber,
  WIRING: C.cyan,
  BUILDING: C.violet,
  READY: C.blue,
};

interface Stage {
  id: string;
  num: string;
  emoji: string;
  title: string;
  subtitle: string;
  accent: string;
  bullets: string[];
  status: Status;
  tools: string;
  cost: string;
  overview: string;
  tech: string;
  runbook: string;
}

const STAGES: Stage[] = [
  {
    id: "discovery", num: "STAGE 1", emoji: "🔍", title: "Discovery",
    subtitle: "Lead sourcing across surfaces", accent: C.cyan,
    bullets: ["Apify scrapers across 9 niches", "150+ raw leads / day", "Reddit + Twitter + Meta (next)", "Dedup against Master DB"],
    status: "LIVE", tools: "Apify · n8n", cost: "$60–90/mo",
    overview: "Sources fresh prospects daily across niche-specific surfaces. Feeds the rest of the pipeline.",
    tech: "Apify actors orchestrated by n8n. Output normalized to leads.raw in Supabase.",
    runbook: "Restart: n8n → 'discovery-master' workflow → Re-run last hour. Scale: add new actor + niche row in icp_niches table.",
  },
  {
    id: "icp", num: "STAGE 2", emoji: "🎯", title: "ICP Filter",
    subtitle: "Niche fit + signal floor", accent: C.cyan,
    bullets: ["9 active niches → 25+ planned", "Hard filters: revenue, headcount, geo", "Soft scoring: stack, hiring signals", "Drops ~60% of raw leads"],
    status: "LIVE", tools: "Postgres · OpenRouter", cost: "incl.",
    overview: "Cuts the raw firehose down to fit-shaped leads before any expensive enrichment runs.",
    tech: "SQL hard filters → LLM soft scorer (gpt-5-mini) → leads.qualified.",
    runbook: "Tune thresholds in /sql/icp_thresholds.sql. Add niche: insert into icp_niches with filter JSON.",
  },
  {
    id: "signal", num: "STAGE 3", emoji: "📡", title: "Signal Enrichment",
    subtitle: "Cara dossier per lead", accent: C.cyan,
    bullets: ["Site crawl + about/team pages", "Tech stack + ad presence", "Recent posts / podcasts", "Outputs: dossier.md per lead"],
    status: "LIVE", tools: "OpenRouter · Apify", cost: "$30–80/mo",
    overview: "Builds a multi-source dossier on each qualified lead — feeds Council and personalizer.",
    tech: "Cara enrichment chain (Gemini 2.5 Flash + GPT-5 mini) → leads.dossier JSONB.",
    runbook: "Re-enrich a lead: POST /api/cara/refresh {lead_id}. Migration to n8n is in NEXT.",
  },
  {
    id: "council", num: "STAGE 3.0", emoji: "🏛️", title: "Strategy Council",
    subtitle: "Picks magnet variant per lead", accent: C.violet,
    bullets: ["Roman-frame agents (Leonidas / Marcus / Brutus)", "Reads dossier + reply history", "Selects A/B/C/D + reasoning", "Logs vote → metrics loop"],
    status: "LIVE", tools: "OpenRouter (gpt-5)", cost: "incl.",
    overview: "Per-lead strategy meeting that picks which magnet variant to deploy and why.",
    tech: "Council agent chain w/ structured JSON output. Vote stored in council_votes.",
    runbook: "Force a variant: POST /api/council/override {lead_id, variant}. Weights tuned nightly (LATER).",
  },
  {
    id: "magnet", num: "STAGE 3.5", emoji: "🧲", title: "Magnet Generation",
    subtitle: "4 variants in parallel", accent: C.violet,
    bullets: ["A · IntakeBot live demo URL", "B · FlowScore real API call", "C · Mockup (Gemini 3 Pro image)", "D · Direct audit offer"],
    status: "WIRING", tools: "Gemini 3 Pro · Custom APIs", cost: "$0.06/lead",
    overview: "Generates the personalized hook asset that the email links to. Council picks which to send.",
    tech: "Per-variant edge functions; mockups pre-gen 77 at $4.62 batch cost.",
    runbook: "Variant D rollout Friday (A/B/C/D 25/25/25/25). Per-variant logs in magnet_runs.",
  },
  {
    id: "copy", num: "STAGE 4", emoji: "✍️", title: "Copy Generation",
    subtitle: "Personalized first-touch + follow-ups", accent: C.violet,
    bullets: ["Pulls dossier + magnet payload", "3-step sequence per lead", "Persona-locked voice", "QA pass before queue"],
    status: "LIVE", tools: "OpenRouter (gpt-5)", cost: "incl.",
    overview: "Writes the actual email sequence wrapped around the chosen magnet.",
    tech: "Prompt template versioned in /prompts/copy_v3.md. Output → emails.queued.",
    runbook: "Rewrite a lead: POST /api/copy/regen {lead_id}. Persona swap via personas.active.",
  },
  {
    id: "send", num: "STAGE 5", emoji: "📤", title: "Send",
    subtitle: "Smartlead delivery", accent: C.blue,
    bullets: ["80–300/day → 400/day target", "Multi-domain warm rotation", "4 AM ET daily push", "Bounce + spam guard"],
    status: "LIVE", tools: "Smartlead", cost: "$97/mo",
    overview: "Hands the queued sequence to Smartlead with persona signatures and rotation rules.",
    tech: "Smartlead API; persona signatures in /assets/personas/. Webhooks → /api/smartlead/event.",
    runbook: "Pause campaign: Smartlead UI → Campaigns → Toggle. Add domain: warmup table + DNS.",
  },
  {
    id: "reply", num: "STAGE 6", emoji: "🤖", title: "Auto-Reply",
    subtitle: "Classify + respond", accent: C.blue,
    bullets: ["Classifier: positive / nurture / no", "Drafts reply + books call", "Human-in-loop on high-confidence", "Auto-send threshold (LATER)"],
    status: "LIVE", tools: "OpenRouter · Cal.com", cost: "incl.",
    overview: "Reads inbound, classifies, drafts reply, and offers calendar slots when warranted.",
    tech: "Reply agent → reply_drafts. Cal.com link injected for booking-intent classes.",
    runbook: "Override draft: /internal/replies → Edit → Send. Flip auto-send via FEATURE_AUTO_SEND env.",
  },
  {
    id: "booked", num: "STAGE 7", emoji: "📅", title: "Booked Call",
    subtitle: "Pre-call brief + handoff", accent: C.green,
    bullets: ["Cal.com webhook → CRM", "Pre-call brief auto-gen (NEXT)", "Slack ping to closer", "Outcome logged → loop"],
    status: "LIVE", tools: "Cal.com · Slack", cost: "incl.",
    overview: "Booked meetings flow into the CRM with a dossier-based brief for the closer.",
    tech: "Cal webhook → Supabase booked_calls → Slack edge function notifier.",
    runbook: "Missed brief: POST /api/brief/regen {booking_id}. Outcome form in /internal/calls.",
  },
  {
    id: "metrics", num: "STAGE 8", emoji: "📊", title: "Metrics Loop",
    subtitle: "Nightly weight tuning", accent: C.amber,
    bullets: ["Per-variant reply / book rates", "Council vote weights re-tuned", "Dashboard refresh 5 min", "Feeds back to Stage 3.0"],
    status: "BUILDING", tools: "n8n · Postgres", cost: "$20/mo",
    overview: "Closes the loop: outcomes from Stage 7 re-weight Council voting nightly.",
    tech: "Nightly n8n job aggregates events → council_weights. Realtime via Supabase channel.",
    runbook: "Force re-tune: n8n → 'metrics-loop' → Run now. Inspect /internal/metrics.",
  },
];

const KPIS = [
  { emoji: "🔍", label: "DAILY LEADS", value: "150+", color: C.cyan, detail: "Raw scraped across 9 niches before ICP filter." },
  { emoji: "📤", label: "DAILY SENDS", value: "80–300 → 400", color: C.blue, detail: "Current daily volume; ramping to 400 with new domains." },
  { emoji: "🎯", label: "ACTIVE NICHES", value: "9", color: C.violet, detail: "Filtered ICPs in production. 25+ planned in NEXT." },
  { emoji: "🧲", label: "MAGNET VARIANTS", value: "4 (A/B/C/D)", color: C.pink, detail: "IntakeBot · FlowScore · Mockup · Direct Audit." },
  { emoji: "🎨", label: "MOCKUPS PRE-GEN", value: "77 ($4.62)", color: C.amber, detail: "Batch generated via Gemini 3 Pro image preview." },
  { emoji: "🤖", label: "AUTO-REPLY", value: "LIVE", color: C.green, detail: "Classifier + drafter shipping replies daily." },
];

const TIMELINE = [
  { row: "Daily new leads", values: [150, 250, 400, 600] },
  { row: "Daily sends", values: [200, 400, 700, 1000] },
  { row: "Reply rate %", values: [3, 5, 7, 9] },
  { row: "Positive reply %", values: [0.8, 1.5, 2.5, 3.5] },
  { row: "Booked calls / day", values: [1, 3, 6, 10] },
  { row: "Booked calls / month", values: [22, 66, 132, 220] },
  { row: "Monthly revenue ($k)", values: [15, 50, 110, 200] },
];

const KANBAN: Record<"NOW" | "NEXT" | "LATER", string[]> = {
  NOW: [
    "Wire FlowScore into personalizer",
    "Variant B 3-split tests (B1/B2/B3)",
    "Variant D Friday rollout (A/B/C/D 25/25/25/25)",
    "Persistent Cloudflare tunnel for webhooks",
  ],
  NEXT: [
    "Expand ICP filter to 25+ niches",
    "Reddit + Twitter + Meta signal sources",
    "Persona signature photos in emails",
    "Pre-call brief auto-gen (Cara dossier + replies)",
    "Acquisity full integration (CSV → live)",
  ],
  LATER: [
    "n8n migration of Cara enrichment chain",
    "assets.flowoperations.ai custom domain",
    "Auto-send threshold for high-confidence replies",
    "Per-variant Council weight tuning (nightly)",
    "Multi-tenant: spin up first 3 client campaigns",
  ],
};

const COSTS = [
  ["Smartlead", "$97"], ["OpenRouter", "$30–80"], ["Apify", "$60–90"],
  ["Mockups (Gemini)", "$40–200"], ["Vercel", "$0"], ["n8n", "$20"],
];

/* ---------- Atoms ---------- */

const Pill = ({ status }: { status: Status }) => (
  <span style={{
    fontSize: 10, fontWeight: 700, letterSpacing: 0.8, padding: "3px 8px",
    borderRadius: 4, color: statusColor[status], background: `${statusColor[status]}1A`,
    border: `1px solid ${statusColor[status]}40`,
  }}>{status}</span>
);

const StageCard = ({ s, onClick, wide = false }: { s: Stage; onClick: () => void; wide?: boolean }) => (
  <button onClick={onClick}
    className="text-left transition-all duration-200 hover:-translate-y-0.5 group"
    style={{
      width: wide ? "100%" : 340, minHeight: 280, background: C.surface,
      border: `1px solid ${C.border}`, borderLeft: `3px solid ${s.accent}`,
      borderRadius: 8, padding: 18, color: C.text, display: "flex", flexDirection: "column",
      boxShadow: "0 1px 0 rgba(255,255,255,0.02)",
    }}
    onMouseEnter={e => (e.currentTarget.style.boxShadow = `0 12px 32px -12px ${s.accent}55, 0 0 0 1px ${s.accent}40`)}
    onMouseLeave={e => (e.currentTarget.style.boxShadow = "0 1px 0 rgba(255,255,255,0.02)")}
  >
    <div className="flex items-start justify-between mb-3">
      <span style={{ fontSize: 26 }}>{s.emoji}</span>
      <span style={{ fontSize: 10, color: C.muted, letterSpacing: 1, fontFamily: "JetBrains Mono, monospace" }}>{s.num}</span>
    </div>
    <h3 style={{ fontFamily: "Space Grotesk, sans-serif", fontWeight: 700, fontSize: 20, lineHeight: 1.15 }}>{s.title}</h3>
    <div style={{ color: s.accent, fontSize: 12, fontWeight: 600, marginTop: 2, marginBottom: 12 }}>{s.subtitle}</div>
    <ul style={{ flex: 1, fontSize: 12, color: "#C8D3E6", lineHeight: 1.65 }}>
      {s.bullets.map(b => <li key={b} style={{ paddingLeft: 12, position: "relative" }}>
        <span style={{ position: "absolute", left: 0, top: 8, width: 4, height: 4, background: s.accent, borderRadius: 99 }} />{b}
      </li>)}
    </ul>
    <div className="flex items-center justify-between mt-4 pt-3" style={{ borderTop: `1px solid ${C.border}` }}>
      <Pill status={s.status} />
      <span style={{ fontSize: 10, color: C.muted, fontFamily: "JetBrains Mono, monospace" }}>{s.tools} · {s.cost}</span>
    </div>
    <span className="opacity-0 group-hover:opacity-100 transition-opacity"
      style={{ fontSize: 11, color: s.accent, marginTop: 8, display: "inline-flex", alignItems: "center", gap: 4 }}>
      Learn more <ExternalLink className="w-3 h-3" />
    </span>
  </button>
);

const Arrow = ({ color = C.cyan, dashed = false, label }: { color?: string; dashed?: boolean; label?: string }) => (
  <div className="flex items-center gap-2 px-2" style={{ minWidth: 60 }}>
    <svg width="100%" height="14" style={{ flex: 1, minWidth: 36 }}>
      <line x1="0" y1="7" x2="100%" y2="7" stroke={color} strokeWidth="1.5" strokeDasharray={dashed ? "4 4" : "0"} />
      <polygon points="100,0 100,14 110,7" fill={color} transform="translate(-10,0)" />
    </svg>
    {label && <span style={{ fontSize: 9, color: C.muted, whiteSpace: "nowrap" }}>{label}</span>}
  </div>
);

/* ---------- Page ---------- */

export default function ColdEmailSOPPage() {
  const [open, setOpen] = useState<Stage | null>(null);
  const [kpiOpen, setKpiOpen] = useState<typeof KPIS[number] | null>(null);
  const [showLanes, setShowLanes] = useState(true);
  const [archOpen, setArchOpen] = useState(false);

  const byId = useMemo(() => Object.fromEntries(STAGES.map(s => [s.id, s])), []);
  const magnet = byId["magnet"];

  return (
    <div style={{ background: C.bg, color: C.text, minHeight: "100vh", fontFamily: "Inter, sans-serif" }}>
      {/* HERO */}
      <section style={{
        position: "relative", height: 240, overflow: "hidden",
        background: `linear-gradient(120deg, ${C.blue} 0%, ${C.violet} 50%, ${C.cyan} 100%)`,
        backgroundSize: "200% 200%", animation: "sopGradient 18s ease infinite",
      }}>
        <style>{`
          @keyframes sopGradient { 0%,100%{background-position:0% 50%} 50%{background-position:100% 50%} }
          @keyframes sopPulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.4;transform:scale(1.4)} }
          @keyframes sopBar { from{transform:scaleX(0)} to{transform:scaleX(1)} }
        `}</style>
        <div style={{ position: "absolute", inset: 0, background: "rgba(2,8,20,0.45)" }} />
        <div style={{ position: "relative", padding: "40px 48px", height: "100%", display: "flex", flexDirection: "column", justifyContent: "center" }}>
          <h1 style={{ fontFamily: "Space Grotesk, sans-serif", fontWeight: 700, fontSize: 60, lineHeight: 1.05, letterSpacing: -1 }}>
            ⚡ FlowOps Cold Email Pipeline
          </h1>
          <p style={{ marginTop: 8, fontSize: 16, color: "#E8EEFC", maxWidth: 900 }}>
            End-to-end SOP — discovery → personalization → magnet → send → reply → booked call
          </p>
        </div>
        <div style={{
          position: "absolute", top: 20, right: 20, display: "flex", alignItems: "center", gap: 8,
          padding: "8px 14px", background: "rgba(2,8,20,0.6)", border: `1px solid ${C.green}55`,
          borderRadius: 99, fontSize: 12, fontWeight: 600,
        }}>
          <span style={{ width: 8, height: 8, borderRadius: 99, background: C.green, animation: "sopPulse 1.6s infinite" }} />
          LIVE — sending tomorrow 4 AM ET
        </div>
      </section>

      {/* KPI STRIP */}
      <section style={{
        position: "sticky", top: 0, zIndex: 30, background: `${C.bg}EE`, backdropFilter: "blur(8px)",
        borderBottom: `1px solid ${C.border}`, padding: "14px 24px",
      }}>
        <div className="grid gap-3" style={{ gridTemplateColumns: "repeat(6, minmax(0,1fr))" }}>
          {KPIS.map(k => (
            <button key={k.label} onClick={() => setKpiOpen(k)}
              className="text-left transition-transform hover:-translate-y-0.5"
              style={{
                background: C.surface, border: `1px solid ${C.border}`, borderTop: `2px solid ${k.color}`,
                borderRadius: 6, padding: "10px 12px",
              }}>
              <div style={{ fontSize: 18 }}>{k.emoji}</div>
              <div style={{ fontSize: 9, color: C.muted, letterSpacing: 1, marginTop: 2 }}>{k.label}</div>
              <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: 18, fontWeight: 700, color: k.color, marginTop: 2 }}>
                {k.value}
              </div>
            </button>
          ))}
        </div>
      </section>

      {/* TOOLBAR */}
      <div style={{ display: "flex", justifyContent: "flex-end", gap: 10, padding: "14px 24px 0" }}>
        <button onClick={() => setShowLanes(s => !s)} style={toolBtn}>
          {showLanes ? "Hide" : "Show"} swim lanes
        </button>
        <button onClick={() => window.print()} style={toolBtn}>
          <Printer className="w-3.5 h-3.5" /> Print SOP
        </button>
      </div>

      {/* PIPELINE */}
      <section style={{ padding: "24px" }}>
        {/* Row 1 — Discovery */}
        <Lane label="DISCOVERY + ENRICHMENT" color={C.cyan} show={showLanes}>
          <StageCard s={byId.discovery} onClick={() => setOpen(byId.discovery)} />
          <Arrow color={C.cyan} />
          <StageCard s={byId.icp} onClick={() => setOpen(byId.icp)} />
          <Arrow color={C.cyan} />
          <StageCard s={byId.signal} onClick={() => setOpen(byId.signal)} />
        </Lane>

        {/* Row 2 — Strategy + Magnet */}
        <Lane label="STRATEGY + MAGNET" color={C.violet} show={showLanes}>
          <StageCard s={byId.council} onClick={() => setOpen(byId.council)} />
          <Arrow color={C.violet} label="selects A/B/C/D" />
          <div style={{ flex: 1, minWidth: 880 }}>
            <StageCard s={magnet} onClick={() => setOpen(magnet)} wide />
            <div className="grid gap-2 mt-2" style={{ gridTemplateColumns: "repeat(4, minmax(0,1fr))" }}>
              {[
                ["A · IntakeBot", "Live demo URL · click=engagement", "$0", "LIVE"],
                ["B · FlowScore", "Real API call · score+leak+gap", "$0", "WIRING"],
                ["C · Mockup", "Gemini 3 Pro · vertical image", "$0.06", "READY"],
                ["D · Direct Audit", "\"Free 20-min audit\" · low friction", "$0", "FRIDAY"],
              ].map(([t, sub, cost, st]) => (
                <div key={t} style={{
                  background: C.surface2, border: `1px solid ${C.border}`, borderRadius: 6, padding: 10,
                }}>
                  <div style={{ fontWeight: 700, fontSize: 12 }}>{t}</div>
                  <div style={{ fontSize: 11, color: C.muted, marginTop: 2 }}>{sub}</div>
                  <div className="flex items-center justify-between mt-2">
                    <span style={{ fontFamily: "JetBrains Mono, monospace", fontSize: 11, color: C.text }}>{cost}</span>
                    <Pill status={st as Status} />
                  </div>
                </div>
              ))}
            </div>
          </div>
          <Arrow color={C.violet} />
          <StageCard s={byId.copy} onClick={() => setOpen(byId.copy)} />
        </Lane>

        {/* Row 3 — Send */}
        <Lane label="SEND + REVENUE" color={C.blue} show={showLanes}>
          <StageCard s={byId.send} onClick={() => setOpen(byId.send)} />
          <Arrow color={C.blue} />
          <StageCard s={byId.reply} onClick={() => setOpen(byId.reply)} />
          <Arrow color={C.blue} />
          <StageCard s={byId.booked} onClick={() => setOpen(byId.booked)} />
        </Lane>

        {/* Row 4 — Loop */}
        <Lane label="FEEDBACK LOOP" color={C.amber} show={showLanes}>
          <StageCard s={byId.metrics} onClick={() => setOpen(byId.metrics)} />
          <Arrow color={C.amber} dashed label="re-weights Council" />
          <div style={{ alignSelf: "center", color: C.amber, fontSize: 11, fontFamily: "JetBrains Mono, monospace" }}>
            ⤴ loops back to STAGE 3.0
          </div>
        </Lane>
      </section>

      {/* TIMELINE */}
      <section style={{ padding: "32px 24px", borderTop: `1px solid ${C.border}` }}>
        <h2 style={h2}>Target Metrics — 90 Day Ramp</h2>
        <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 8, padding: 18 }}>
          <div className="grid items-center gap-3" style={{ gridTemplateColumns: "200px repeat(4, 1fr)" }}>
            <div />
            {["Today", "30 days", "60 days", "90 days"].map(h => (
              <div key={h} style={{ fontSize: 11, color: C.muted, letterSpacing: 1 }}>{h.toUpperCase()}</div>
            ))}
            {TIMELINE.map(row => {
              const max = Math.max(...row.values);
              return (
                <RowFragment key={row.row} row={row} max={max} />
              );
            })}
          </div>
        </div>
      </section>

      {/* COST */}
      <section style={{ padding: "32px 24px", borderTop: `1px solid ${C.border}` }}>
        <h2 style={h2}>Cost Model</h2>
        <div className="grid gap-4" style={{ gridTemplateColumns: "1fr 1fr 1fr" }}>
          <div style={panel}>
            <div style={panelLabel}>MONTHLY RECURRING</div>
            <table style={{ width: "100%", marginTop: 10, fontSize: 13 }}>
              <tbody>
                {COSTS.map(([k, v]) => (
                  <tr key={k} style={{ borderBottom: `1px solid ${C.border}` }}>
                    <td style={{ padding: "8px 0", color: C.muted }}>{k}</td>
                    <td style={{ padding: "8px 0", textAlign: "right", fontFamily: "JetBrains Mono, monospace", fontWeight: 600 }}>{v}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div style={{ ...panel, textAlign: "center" }}>
            <div style={panelLabel}>COST PER BOOKED CALL</div>
            <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: 64, fontWeight: 700, color: C.green, marginTop: 18 }}>$4.50</div>
            <div style={{ color: C.muted, fontSize: 12, marginTop: 6 }}>vs $50–200 industry benchmark for paid ads</div>
          </div>
          <div style={{ ...panel, textAlign: "center" }}>
            <div style={panelLabel}>COST-TO-REVENUE RATIO</div>
            <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: 64, fontWeight: 700, color: C.cyan, marginTop: 18 }}>0.15–0.30%</div>
            <div style={{ color: C.muted, fontSize: 12, marginTop: 6 }}>of monthly revenue spent on the engine</div>
          </div>
        </div>
      </section>

      {/* KANBAN */}
      <section style={{ padding: "32px 24px", borderTop: `1px solid ${C.border}` }}>
        <h2 style={h2}>Roadmap</h2>
        <div className="grid gap-4" style={{ gridTemplateColumns: "1fr 1fr 1fr" }}>
          {(["NOW", "NEXT", "LATER"] as const).map((col, i) => (
            <div key={col} style={panel}>
              <div style={{ ...panelLabel, color: [C.green, C.amber, C.violet][i] }}>{col}</div>
              <ul style={{ marginTop: 12, display: "flex", flexDirection: "column", gap: 8 }}>
                {KANBAN[col].map(item => (
                  <li key={item} style={{
                    fontSize: 13, padding: "10px 12px", background: C.surface2,
                    border: `1px solid ${C.border}`, borderRadius: 6, lineHeight: 1.4,
                  }}>{item}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      {/* ARCHITECTURE */}
      <section style={{ padding: "24px", borderTop: `1px solid ${C.border}` }}>
        <button onClick={() => setArchOpen(o => !o)} style={{
          display: "flex", alignItems: "center", gap: 8, color: C.text, fontWeight: 600, fontSize: 14,
        }}>
          {archOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
          Architecture diagram
        </button>
        {archOpen && (
          <div className="grid gap-3 mt-4" style={{ gridTemplateColumns: "repeat(5, 1fr)" }}>
            {[
              ["Discovery", "Apify · custom scrapers", C.cyan],
              ["Enrichment", "OpenRouter · Cara chain", C.cyan],
              ["Storage", "Supabase Postgres", C.blue],
              ["Hosting", "Vercel · Cloudflare", C.blue],
              ["Automation", "n8n · Smartlead", C.violet],
            ].map(([t, sub, c]) => (
              <div key={t as string} style={{
                background: C.surface, border: `1px solid ${C.border}`, borderTop: `3px solid ${c as string}`,
                borderRadius: 8, padding: 16,
              }}>
                <div style={{ fontWeight: 700, fontSize: 14 }}>{t}</div>
                <div style={{ color: C.muted, fontSize: 12, marginTop: 4 }}>{sub}</div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* STAGE DETAIL */}
      <Dialog open={!!open} onOpenChange={o => !o && setOpen(null)}>
        <DialogContent className="max-w-2xl" style={{ background: C.surface, borderColor: C.border, color: C.text }}>
          {open && (
            <>
              <DialogHeader>
                <DialogTitle style={{ fontFamily: "Space Grotesk, sans-serif", fontSize: 24 }}>
                  <span style={{ marginRight: 8 }}>{open.emoji}</span>{open.title}
                </DialogTitle>
                <div style={{ color: open.accent, fontSize: 12, fontWeight: 600 }}>{open.num} · {open.subtitle}</div>
              </DialogHeader>
              <Tabs defaultValue="overview" className="mt-2">
                <TabsList className="grid grid-cols-3" style={{ background: C.surface2 }}>
                  <TabsTrigger value="overview">Overview</TabsTrigger>
                  <TabsTrigger value="tech">Tech</TabsTrigger>
                  <TabsTrigger value="runbook">Runbook</TabsTrigger>
                </TabsList>
                <TabsContent value="overview" className="text-sm leading-relaxed mt-4">
                  <p style={{ color: "#D6E0F2" }}>{open.overview}</p>
                  <ul className="mt-4 space-y-1.5">
                    {open.bullets.map(b => <li key={b} style={{ color: "#C8D3E6", fontSize: 13 }}>• {b}</li>)}
                  </ul>
                  <div className="mt-4"><Pill status={open.status} /></div>
                </TabsContent>
                <TabsContent value="tech" className="text-sm mt-4">
                  <p style={{ color: "#D6E0F2", fontSize: 13, marginBottom: 12 }}>{open.tech}</p>
                  <CopyBlock label={`${open.tools} · ${open.cost}`} content={open.tech} />
                </TabsContent>
                <TabsContent value="runbook" className="text-sm mt-4">
                  <p style={{ color: "#D6E0F2", fontSize: 13, marginBottom: 12 }}>{open.runbook}</p>
                  <CopyBlock label="RUNBOOK" content={open.runbook} />
                </TabsContent>
              </Tabs>
              <div className="flex items-center justify-end gap-3 mt-4 pt-3" style={{ borderTop: `1px solid ${C.border}`, color: C.muted, fontSize: 12 }}>
                Was this helpful? <button style={feedbackBtn}>👍</button><button style={feedbackBtn}>👎</button>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>

      {/* KPI MODAL */}
      <Dialog open={!!kpiOpen} onOpenChange={o => !o && setKpiOpen(null)}>
        <DialogContent style={{ background: C.surface, borderColor: C.border, color: C.text }}>
          {kpiOpen && (
            <>
              <DialogHeader>
                <DialogTitle style={{ fontFamily: "Space Grotesk, sans-serif" }}>
                  {kpiOpen.emoji} {kpiOpen.label}
                </DialogTitle>
              </DialogHeader>
              <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: 36, fontWeight: 700, color: kpiOpen.color }}>
                {kpiOpen.value}
              </div>
              <p style={{ color: "#D6E0F2", fontSize: 13 }}>{kpiOpen.detail}</p>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}

/* ---------- helpers ---------- */

const toolBtn: React.CSSProperties = {
  display: "inline-flex", alignItems: "center", gap: 6, fontSize: 11, color: C.muted,
  background: C.surface, border: `1px solid ${C.border}`, padding: "6px 12px", borderRadius: 6,
};
const h2: React.CSSProperties = {
  fontFamily: "Space Grotesk, sans-serif", fontWeight: 700, fontSize: 24, marginBottom: 16,
};
const panel: React.CSSProperties = {
  background: C.surface, border: `1px solid ${C.border}`, borderRadius: 8, padding: 18,
};
const panelLabel: React.CSSProperties = {
  fontSize: 11, color: C.muted, letterSpacing: 1.2, fontWeight: 600,
};
const feedbackBtn: React.CSSProperties = {
  background: C.surface2, border: `1px solid ${C.border}`, borderRadius: 6, padding: "4px 10px",
};

function Lane({ label, color, children, show }: { label: string; color: string; children: React.ReactNode; show: boolean }) {
  return (
    <div style={{ marginBottom: 28 }}>
      {show && (
        <div style={{
          fontSize: 10, color, letterSpacing: 1.6, fontWeight: 700, marginBottom: 10,
          fontFamily: "JetBrains Mono, monospace",
        }}>— {label} —</div>
      )}
      <div style={{
        display: "flex", alignItems: "stretch", gap: 4, overflowX: "auto", paddingBottom: 8,
        ...(show ? { borderLeft: `2px solid ${color}33`, paddingLeft: 16 } : {}),
      }}>
        {children}
      </div>
    </div>
  );
}

function RowFragment({ row, max }: { row: { row: string; values: number[] }; max: number }) {
  return (
    <>
      <div style={{ fontSize: 13, color: C.text, padding: "10px 0" }}>{row.row}</div>
      {row.values.map((v, i) => (
        <div key={i} style={{ padding: "10px 0" }}>
          <div style={{
            height: 8, background: C.surface2, borderRadius: 4, overflow: "hidden",
            border: `1px solid ${C.border}`,
          }}>
            <div style={{
              width: `${(v / max) * 100}%`, height: "100%",
              background: `linear-gradient(90deg, ${C.blue}, ${C.cyan})`,
              transformOrigin: "left", animation: `sopBar 0.9s ${i * 0.1}s ease-out both`,
            }} />
          </div>
          <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: 11, color: C.muted, marginTop: 4 }}>{v}</div>
        </div>
      ))}
    </>
  );
}