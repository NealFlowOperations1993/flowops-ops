import { useState, useEffect } from "react";
import { TridentCard } from "@/components/trident/TridentCard";
import { SectionHeader } from "../SectionHeader";

const ops = [
  { period: "DAILY — 5 minutes", color: "hsl(var(--blue))", tasks: [
    "Check daily briefing (Slack notification from n8n)",
    "Respond to positive replies in GHL master inbox",
    "Review health alerts — bounce rate, paused campaigns",
    "Confirm inboxes are sending in Smartlead dashboard",
    "Check pipeline throughput — are leads flowing end-to-end?",
  ]},
  { period: "WEEKLY — 30 minutes", color: "hsl(var(--purple))", tasks: [
    "Review open/reply rates per campaign and per subject line",
    "Pause underperforming subject line variants",
    "Check domain health scores in Smartlead",
    "Review ICP filter accuracy — are replies from the right people?",
    "Check Apify run results — did scrapes complete successfully?",
    "Add new leads to pipeline if running low (under 2 weeks runway)",
  ]},
  { period: "MONTHLY — 2 hours", color: "hsl(var(--green))", tasks: [
    "Full pipeline audit: scrape → send → reply → close conversion rates",
    "Buy and start warming new domains for next month's scale target",
    "Review and refresh email copy — copy decays over time",
    "Update ICP criteria based on who actually closed",
    "Plan next month's verticals and campaign structure",
    "Calculate true CAC and optimize the highest-impact lever",
  ]},
];

const getStorageKey = () => {
  const today = new Date().toISOString().slice(0, 10);
  return `ops-checklist-${today}`;
};

export const OpsSection = () => {
  const [checked, setChecked] = useState<Record<string, boolean>>(() => {
    try {
      const saved = localStorage.getItem(getStorageKey());
      return saved ? JSON.parse(saved) : {};
    } catch { return {}; }
  });

  useEffect(() => {
    localStorage.setItem(getStorageKey(), JSON.stringify(checked));
  }, [checked]);

  const toggle = (key: string) => setChecked(prev => ({ ...prev, [key]: !prev[key] }));

  return (
    <div>
      <SectionHeader label="12 — OPERATIONS" title="Daily Operating Protocol" subtitle="Interactive — checkboxes reset daily." />
      <div className="flex flex-col gap-4">
        {ops.map((op, gi) => {
          const completed = op.tasks.filter((_, ti) => checked[`${gi}-${ti}`]).length;
          const pct = Math.round((completed / op.tasks.length) * 100);
          return (
            <TridentCard key={op.period} accentColor={op.color}>
              <div className="flex justify-between items-center mb-3">
                <div className="font-mono text-xs font-bold tracking-[2px]" style={{ color: op.color }}>{op.period}</div>
                <div className="flex items-center gap-2">
                  <div className="w-20 h-1.5 rounded-full bg-background">
                    <div className="h-full rounded-full transition-all" style={{ width: `${pct}%`, background: op.color }} />
                  </div>
                  <span className="font-mono text-[10px] text-foreground-tertiary">{completed}/{op.tasks.length}</span>
                </div>
              </div>
              {op.tasks.map((t, ti) => {
                const key = `${gi}-${ti}`;
                const done = !!checked[key];
                return (
                  <label
                    key={key}
                    className="flex items-center gap-3 py-2 px-2 rounded-md cursor-pointer transition-colors hover:bg-background/50 group"
                  >
                    <div
                      className="w-4 h-4 rounded border flex items-center justify-center shrink-0 transition-all"
                      style={{
                        borderColor: done ? op.color : "hsl(var(--border))",
                        background: done ? op.color : "transparent",
                      }}
                    >
                      {done && <span className="text-[10px] text-background font-bold">✓</span>}
                    </div>
                    <input type="checkbox" checked={done} onChange={() => toggle(key)} className="sr-only" />
                    <span className={`text-xs transition-all ${done ? "text-foreground-tertiary line-through" : "text-foreground-secondary"}`}>{t}</span>
                  </label>
                );
              })}
            </TridentCard>
          );
        })}
      </div>
    </div>
  );
};
