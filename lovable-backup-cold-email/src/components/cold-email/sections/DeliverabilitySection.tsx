import { SectionHeader } from "../SectionHeader";
import { DataTable } from "../DataTable";

export const DeliverabilitySection = () => (
  <div>
    <SectionHeader label="11 — DELIVERABILITY" title="The Deliverability Bible" />
    <h3 className="text-foreground font-bold mb-2.5">Key Metrics Dashboard</h3>
    <DataTable
      headers={["METRIC", "GREEN ✓", "YELLOW ⚠️", "RED ✕ — ACTION"]}
      rows={[
        ["Bounce Rate", "<2%", "2-4%", { text: ">4% — Pause domain, check verification", color: "#EF4444" }],
        ["Spam Rate", "<0.1%", "0.1-0.3%", { text: ">0.3% — Stop sending, audit copy immediately", color: "#EF4444" }],
        ["Open Rate", ">40%", "25-40%", { text: "<25% — Test subjects, check spam folder placement", color: "#EF4444" }],
        ["Reply Rate", ">2%", "1-2%", { text: "<1% — Rewrite copy, refine ICP targeting", color: "#EF4444" }],
        ["Unsubscribe", "<0.5%", "0.5-1%", { text: ">1% — Audit targeting, soften tone", color: "#EF4444" }],
      ]}
    />
    <h3 className="text-foreground font-bold mt-5 mb-2.5">Deliverability Killers</h3>
    <div className="grid grid-cols-2 gap-2">
      {[
        "Sending from your primary domain",
        "Skipping email verification (even 5% bad = damage)",
        "Jumping volume more than 2x per week",
        "Spam words: 'guaranteed', 'free offer', 'act now'",
        "Inconsistent sending — blast then silence pattern",
        "No SPF/DKIM/DMARC set before first send",
        "One inbox sending 500+/day (max 70-100)",
        "High image ratio — plain text delivers better",
        "Links in Email 1 to unknown/cold domains",
        "Purchasing leads vs scraping (quality is garbage)",
      ].map(k => (
        <div key={k} className="flex gap-2 items-center px-2.5 py-1.5 rounded-md" style={{ background: "hsl(var(--red) / 0.06)", border: "1px solid hsl(var(--red) / 0.2)" }}>
          <span className="text-red shrink-0">✕</span>
          <span className="text-foreground-secondary text-xs">{k}</span>
        </div>
      ))}
    </div>
  </div>
);
