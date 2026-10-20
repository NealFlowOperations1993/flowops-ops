import { TridentCard } from "@/components/trident/TridentCard";

interface Variant {
  id: string;
  letter: string;
  name: string;
  status: "LIVE" | "WIRING" | "FRI";
  sent: number;
  reply: number;
  click: number;
  booked: number;
  spark: number[];
  winner?: boolean;
}

const VARIANTS: Variant[] = [
  { id: "a", letter: "A", name: "IntakeBot", status: "LIVE", sent: 0, reply: 0, click: 0, booked: 0, spark: [1,2,2,3,4,3,5,6,7,8,9,8,10] },
  { id: "b", letter: "B", name: "FlowScore", status: "WIRING", sent: 0, reply: 0, click: 0, booked: 0, spark: [0,0,1,1,2,2,3,3,4,5,5,6,6] },
  { id: "c", letter: "C", name: "Mockup", status: "LIVE", sent: 0, reply: 0, click: 0, booked: 0, spark: [2,3,3,4,5,5,6,7,7,8,9,10,11], winner: true },
  { id: "d", letter: "D", name: "Direct Audit", status: "FRI", sent: 0, reply: 0, click: 0, booked: 0, spark: [0,0,0,0,0,1,1,1,2,2,3,3,4] },
];

const STATUS_COLOR: Record<Variant["status"], string> = {
  LIVE: "hsl(var(--green))",
  WIRING: "hsl(var(--cyan))",
  FRI: "hsl(var(--amber))",
};

export const VariantPerformanceGrid = () => (
  <div>
    <div className="font-mono text-[10px] text-foreground-tertiary tracking-wider mb-3">VARIANT PERFORMANCE</div>
    <div className="grid grid-cols-4 gap-3">
      {VARIANTS.map(v => (
        <TridentCard
          key={v.id}
          className="relative"
          accentColor={v.winner ? "#F472B6" : undefined}
        >
          {v.winner && (
            <div className="absolute top-2 right-2 font-mono text-[9px] px-1.5 py-0.5 rounded"
              style={{ background: "#F472B620", color: "#F472B6" }}>WINNING</div>
          )}
          <div className="font-display text-base font-bold text-foreground">
            {v.letter} · <span className="text-foreground-secondary">{v.name}</span>
          </div>
          <div className="grid grid-cols-2 gap-2 mt-3 text-xs">
            <Stat label="Sent" value={v.sent} />
            <Stat label="Reply" value={`${v.reply}%`} />
            <Stat label="Click" value={`${v.click}%`} />
            <Stat label="Booked" value={v.booked} />
          </div>
          <div className="mt-3">
            <Spark values={v.spark} color={v.winner ? "#F472B6" : "hsl(var(--cyan))"} />
          </div>
          <div className="flex justify-end mt-2">
            <span className="font-mono text-[9px] px-1.5 py-0.5 rounded font-bold"
              style={{ background: STATUS_COLOR[v.status] + "20", color: STATUS_COLOR[v.status] }}>
              {v.status}
            </span>
          </div>
        </TridentCard>
      ))}
    </div>
  </div>
);

const Stat = ({ label, value }: { label: string; value: string | number }) => (
  <div>
    <div className="font-mono text-[9px] text-foreground-tertiary tracking-wider">{label.toUpperCase()}</div>
    <div className="font-mono text-sm text-foreground">{value}</div>
  </div>
);

const Spark = ({ values, color }: { values: number[]; color: string }) => {
  const max = Math.max(...values, 1);
  const pts = values.map((v, i) => `${(i / (values.length - 1)) * 100},${24 - (v / max) * 24}`).join(" ");
  return (
    <svg viewBox="0 0 100 24" preserveAspectRatio="none" style={{ width: "100%", height: 24 }}>
      <polyline fill="none" stroke={color} strokeWidth="1.5" points={pts} />
    </svg>
  );
};