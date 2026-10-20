import { SectionHeader } from "../SectionHeader";
import { TridentCard } from "@/components/trident/TridentCard";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const chartData = [
  { month: "Apr", emails: 1000 },
  { month: "May", emails: 12000 },
  { month: "Jun", emails: 24000 },
  { month: "Jul", emails: 36000 },
  { month: "Aug", emails: 48000 },
  { month: "Sep", emails: 60000 },
  { month: "Oct", emails: 72000 },
  { month: "Nov", emails: 84000 },
  { month: "Dec", emails: 96000 },
];

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg px-3 py-2" style={{ background: "hsl(222,55%,6%)", border: "1px solid hsl(217,60%,20%,0.5)" }}>
      <div className="font-mono text-[10px] text-foreground-tertiary">{label} 2026</div>
      <div className="font-mono text-sm font-bold text-cyan">{payload[0].value.toLocaleString()} emails</div>
    </div>
  );
};

export const GrowthChartSection = () => (
  <div>
    <SectionHeader label="GROWTH TRAJECTORY" title="Monthly Email Volume — 2026" subtitle="From 1,000 test emails to 96,000/month war machine." />
    <TridentCard>
      <div className="font-mono text-[10px] tracking-[2px] text-foreground-tertiary mb-4">PROJECTED EMAIL VOLUME (APR → DEC)</div>
      <ResponsiveContainer width="100%" height={320}>
        <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="emailGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="hsl(190,90%,50%)" stopOpacity={0.3} />
              <stop offset="95%" stopColor="hsl(190,90%,50%)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(217,28%,12%)" />
          <XAxis dataKey="month" tick={{ fill: "hsl(215,20%,50%)", fontSize: 11, fontFamily: "Fira Code" }} axisLine={{ stroke: "hsl(217,28%,12%)" }} tickLine={false} />
          <YAxis tick={{ fill: "hsl(215,20%,50%)", fontSize: 11, fontFamily: "Fira Code" }} axisLine={false} tickLine={false} tickFormatter={(v) => `${v / 1000}K`} />
          <Tooltip content={<CustomTooltip />} />
          <Area type="monotone" dataKey="emails" stroke="hsl(190,90%,50%)" strokeWidth={2} fill="url(#emailGradient)" />
        </AreaChart>
      </ResponsiveContainer>
    </TridentCard>

    <div className="grid grid-cols-3 gap-3 mt-4">
      {[
        ["Phase 1", "1K", "Apr", "hsl(var(--blue))"],
        ["Phase 2", "12K", "May", "hsl(var(--purple))"],
        ["Full Scale", "96K", "Dec", "hsl(var(--green))"],
      ].map(([phase, vol, month, color]) => (
        <TridentCard key={phase as string} accentColor={color as string}>
          <div className="font-mono text-[9px] tracking-[2px] text-foreground-tertiary mb-1">{phase}</div>
          <div className="text-2xl font-black" style={{ color: color as string }}>{vol}</div>
          <div className="text-[11px] text-foreground-tertiary">{month} 2026</div>
        </TridentCard>
      ))}
    </div>
  </div>
);
