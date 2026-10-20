import { useState } from "react";
import { TridentCard } from "@/components/trident/TridentCard";
import { SectionHeader } from "../SectionHeader";
import { Highlight, Bullet } from "../Highlight";

const phases = [
  { num: "P1", name: "Test Fire", period: "APRIL", color: "hsl(var(--blue))", target: "1,000 emails", domains: "3", inboxes: "6", daily: "~45/day", budget: "~$49", kpi: "ONE close in April = machine validated",
    goals: ["Validate email copy and subject lines", "Test ICP targeting accuracy", "Establish warmup baseline", "Build and test the full pipeline", "Target: 1 closed deal = WIN"] },
  { num: "P2", name: "Engine On", period: "MAY", color: "hsl(var(--purple))", target: "12,000 emails", domains: "6", inboxes: "12", daily: "~545/day", budget: "~$100-200", kpi: "Cost per booked call under $5",
    goals: ["Scale proven April copy", "Add Aerosend if domains burning", "Optimize reply → GHL routing", "First real revenue pipeline", "Target: 3-5 closes"] },
  { num: "P3", name: "Compound", period: "JUNE–SEPT", color: "hsl(var(--green))", target: "24K–60K emails", domains: "10–22", inboxes: "20–44", daily: "1K–2.7K/day", budget: "Budget unlocked", kpi: "Reply-to-close rate above 15%",
    goals: ["Add Aerosend private infra", "A/B test sequences systematically", "Add AI personalization layer", "Hire setter to work replies", "Target: 10-20 closes/month"] },
  { num: "P4", name: "War Machine", period: "OCT–DEC", color: "hsl(var(--amber))", target: "72K–96K emails", domains: "26–34", inboxes: "52–68", daily: "3K–4.3K/day", budget: "ROI-driven", kpi: "$577K/month pipeline from $49 infra",
    goals: ["Full fleet automation", "Multi-niche campaigns in parallel", "Dedicated SDR team", "You only close", "Target: 40-77 closes/month"] },
];

export const PhasesSection = () => {
  const [active, setActive] = useState(0);
  const p = phases[active];

  return (
    <div>
      <SectionHeader label="04 — PHASES" title="Month-by-Month Roadmap" />
      <div className="flex gap-2.5 mb-5">
        {phases.map((ph, i) => (
          <button
            key={i}
            onClick={() => setActive(i)}
            className="flex-1 rounded-lg p-3 cursor-pointer transition-all"
            style={{
              background: active === i ? ph.color + "20" : "hsl(var(--background-secondary))",
              border: `1px solid ${active === i ? ph.color : "hsl(var(--border))"}`,
            }}
          >
            <div className="font-mono text-[10px] font-bold tracking-wider" style={{ color: ph.color }}>{ph.num}</div>
            <div className="text-[13px] font-bold text-foreground mt-0.5">{ph.name}</div>
            <div className="text-[11px] text-foreground-tertiary mt-0.5">{ph.period}</div>
          </button>
        ))}
      </div>
      <TridentCard accentColor={p.color}>
        <div className="grid grid-cols-5 gap-3 mb-5">
          {([["TARGET", p.target], ["DOMAINS", p.domains], ["INBOXES", p.inboxes], ["DAILY SENDS", p.daily], ["BUDGET", p.budget]] as [string, string][]).map(([k, v]) => (
            <div key={k} className="bg-background rounded-lg p-2.5 text-center">
              <div className="font-mono text-[10px] text-foreground-tertiary mb-1">{k}</div>
              <div className="text-sm font-extrabold text-foreground">{v}</div>
            </div>
          ))}
        </div>
        <div className="font-mono text-[11px] tracking-[2px] mb-2.5" style={{ color: p.color }}>OBJECTIVES</div>
        {p.goals.map(g => <Bullet key={g} color={p.color}>{g}</Bullet>)}
        <Highlight color={p.color}>KPI: {p.kpi}</Highlight>
      </TridentCard>
    </div>
  );
};
