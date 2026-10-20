import { useState } from "react";
import { TridentCard } from "@/components/trident/TridentCard";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";

interface Row {
  key: string;
  label: string;
  current: number;
  target: number;
  format: (v: number) => string;
  color: string;
  trend: number[]; // last 30d hardcoded sample for v1
}

interface Props {
  dailyLeads: number;
  dailySends: number;
  replyRate: number;
  bookedMonth: number;
  revenueMonth: number;
}

const fmtNum = (v: number) => v.toLocaleString();
const fmtPct = (v: number) => `${v.toFixed(1)}%`;
const fmtUsd = (v: number) => `$${Math.round(v).toLocaleString()}`;

const sampleTrend = (peak: number) =>
  Array.from({ length: 30 }, (_, i) => Math.round((peak * (i + 1)) / 30 * (0.7 + Math.random() * 0.6)));

export const TargetMetricsBand = ({ dailyLeads, dailySends, replyRate, bookedMonth, revenueMonth }: Props) => {
  const [open, setOpen] = useState<Row | null>(null);

  const rows: Row[] = [
    { key: "leads", label: "Daily new leads", current: dailyLeads, target: 600, format: fmtNum, color: "hsl(var(--cyan))", trend: sampleTrend(dailyLeads || 150) },
    { key: "sends", label: "Daily sends", current: dailySends, target: 1100, format: fmtNum, color: "hsl(var(--blue))", trend: sampleTrend(dailySends || 120) },
    { key: "reply", label: "Reply rate", current: replyRate, target: 3.0, format: fmtPct, color: "#A855F7", trend: sampleTrend(replyRate || 1) },
    { key: "booked", label: "Booked calls / month", current: bookedMonth, target: 250, format: fmtNum, color: "hsl(var(--green))", trend: sampleTrend(bookedMonth || 5) },
    { key: "revenue", label: "Monthly outbound revenue", current: revenueMonth, target: 1_000_000, format: fmtUsd, color: "#22C55E", trend: sampleTrend(revenueMonth || 1000) },
  ];

  return (
    <>
      <TridentCard>
        <div className="font-mono text-[10px] text-foreground-tertiary tracking-wider mb-4">
          TARGET METRICS — 90 DAY PROGRESS
        </div>
        <div className="space-y-3">
          {rows.map(r => {
            const pct = Math.min(100, r.target > 0 ? (r.current / r.target) * 100 : 0);
            return (
              <button
                key={r.key}
                onClick={() => setOpen(r)}
                className="w-full text-left p-3 rounded hover:bg-background-tertiary/40 transition-colors"
              >
                <div className="flex items-baseline justify-between mb-1.5">
                  <span className="text-xs text-foreground">{r.label}</span>
                  <span className="font-mono text-[11px] text-foreground-secondary">
                    <span className="text-foreground" style={{ color: r.color }}>{r.format(r.current)}</span>
                    <span className="text-foreground-tertiary"> / target {r.format(r.target)}</span>
                    <span className="ml-2 text-foreground-tertiary">{pct.toFixed(0)}%</span>
                    {r.current === 0 && <span className="ml-2 text-amber">(early)</span>}
                  </span>
                </div>
                <div className="h-1.5 rounded bg-background-tertiary/60 overflow-hidden">
                  <div
                    className="h-full transition-all duration-700"
                    style={{ width: `${pct}%`, background: r.color }}
                  />
                </div>
              </button>
            );
          })}
        </div>
      </TridentCard>

      <Dialog open={!!open} onOpenChange={o => !o && setOpen(null)}>
        <DialogContent className="max-w-xl">
          {open && (
            <>
              <DialogHeader>
                <DialogTitle>{open.label} · last 30d</DialogTitle>
              </DialogHeader>
              <Sparkline values={open.trend} color={open.color} height={120} />
              <div className="font-mono text-[11px] text-foreground-tertiary mt-3">
                Current {open.format(open.current)} · 90-day target {open.format(open.target)}
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
};

const Sparkline = ({ values, color, height = 32 }: { values: number[]; color: string; height?: number }) => {
  const max = Math.max(...values, 1);
  const w = 100;
  const pts = values.map((v, i) => `${(i / (values.length - 1)) * w},${height - (v / max) * height}`).join(" ");
  return (
    <svg viewBox={`0 0 ${w} ${height}`} preserveAspectRatio="none" style={{ width: "100%", height }}>
      <polyline fill="none" stroke={color} strokeWidth="1.5" points={pts} />
    </svg>
  );
};