import { TridentCard } from "@/components/trident/TridentCard";

interface Props {
  spend: number;
  booked: number;
}

export const CostPerCallCard = ({ spend, booked }: Props) => {
  const cpc = booked > 0 ? spend / booked : 4.5;
  const target = 2.5;
  const pct = Math.min(100, (target / Math.max(cpc, target)) * 100);

  return (
    <TridentCard>
      <div className="font-mono text-[10px] text-foreground-tertiary tracking-wider mb-4">
        COST PER BOOKED CALL
      </div>
      <div className="grid grid-cols-2 gap-6 items-center">
        <div>
          <div className="font-display text-6xl font-bold text-green leading-none">
            ${cpc.toFixed(2)}
          </div>
          <div className="text-xs text-foreground-secondary mt-2">
            Realistic tier · vs $50–200 industry benchmark for paid ads
          </div>
        </div>
        <div>
          <div className="flex justify-between text-xs mb-1.5">
            <span className="text-foreground-tertiary">Today</span>
            <span className="font-mono text-foreground">${cpc.toFixed(2)}</span>
          </div>
          <div className="h-1.5 rounded bg-background-tertiary/60 overflow-hidden">
            <div className="h-full bg-green transition-all duration-700" style={{ width: `${pct}%` }} />
          </div>
          <div className="flex justify-between text-xs mt-1.5">
            <span className="text-foreground-tertiary">Target 90d</span>
            <span className="font-mono text-foreground">${target.toFixed(2)}</span>
          </div>
        </div>
      </div>
    </TridentCard>
  );
};