import { SectionHeader } from "../SectionHeader";
import { DataTable } from "../DataTable";
import { TridentBadge } from "@/components/trident/TridentBadge";

export const WarmupSection = () => (
  <div>
    <SectionHeader label="06 — WARMUP" title="Warmup Protocol" subtitle="Warming by tomorrow. Sending real emails by Day 7." />
    <DataTable
      headers={["PERIOD", "REAL SENDS/DAY", "WARMUP AUTO", "RISK", "FOCUS"]}
      rows={[
        ["Days 1–7", "0", "5–20", { text: "NONE", color: "#10B981" }, "Let Smartlead warmup run automatically"],
        ["Days 7–14", "5–10", "15–20", { text: "VERY LOW", color: "#10B981" }, "Test copy on best ICP leads only"],
        ["Days 14–21", "15–25", "20", { text: "LOW", color: "#22C55E" }, "Iterate on open rates"],
        ["Days 21–28", "40–60", "20", { text: "LOW-MED", color: "#F59E0B" }, "Ramp volume cautiously"],
        ["Day 28+", "70–100", "20", { text: "NORMAL", color: "#3B82F6" }, "Full operations"],
      ]}
    />
    <h3 className="text-foreground font-bold mt-5 mb-2.5">Your April Launch Timeline</h3>
    <div className="space-y-2.5">
      {[
        ["Day 1 (TODAY)", "hsl(var(--blue))", "Buy 3 domains, connect to Smartlead, enable warmup immediately"],
        ["Days 1-7", "hsl(var(--purple))", "Build lead lists with Apify, build the full n8n pipeline"],
        ["Day 7", "hsl(var(--green))", "First real sends — 5-10/inbox/day, low risk"],
        ["Day 14", "hsl(var(--amber))", "Ramp to 25/inbox/day. Buy 3 more domains for May."],
        ["Day 21", "#F97316", "Ramp to 50/inbox/day"],
        ["Day 28+", "hsl(var(--red))", "Full 70-100/inbox/day — real operation running"],
      ].map(([time, color, action]) => (
        <div key={time as string} className="flex gap-3 items-start">
          <span className="font-mono text-[11px] font-bold px-2.5 py-0.5 rounded shrink-0" style={{ background: (color as string) + "22", border: `1px solid ${color}55`, color: color as string }}>{time}</span>
          <span className="text-foreground-secondary text-[13px] pt-0.5">{action}</span>
        </div>
      ))}
    </div>
  </div>
);
