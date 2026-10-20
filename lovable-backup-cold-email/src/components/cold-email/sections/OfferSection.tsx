import { TridentCard } from "@/components/trident/TridentCard";
import { SectionHeader } from "../SectionHeader";
import { DataTable } from "../DataTable";

export const OfferSection = () => (
  <div>
    <SectionHeader label="09 — THE OFFER" title="Custom Software via Claude Code" subtitle="You're not pitching a service. You're showing up with a product." />
    <div className="grid grid-cols-2 gap-4 mb-5">
      <TridentCard accentColor="hsl(var(--red))">
        <div className="font-mono text-xs text-red tracking-[2px] mb-2.5">TRADITIONAL AGENCY</div>
        {['"We run your ads"', '"We do automation"', "Perceived as: commodity", "Price ceiling: $2K-$5K", "Build cost: high (team required)", "Delivery: weeks/months"].map(t => (
          <div key={t} className="text-foreground-tertiary text-[13px] py-1 border-b border-border/20">{t}</div>
        ))}
      </TridentCard>
      <TridentCard accentColor="hsl(var(--green))">
        <div className="font-mono text-xs text-green tracking-[2px] mb-2.5">YOUR PLAY</div>
        {['"We build your custom software"', '"Here\'s the system, built for your vertical"', "Perceived as: builder/partner", "Price floor: $10K-$50K+", "Build cost: low (Claude Code + your time)", "Delivery: days"].map(t => (
          <div key={t} className="text-foreground-secondary text-[13px] font-semibold py-1 border-b border-border/20">{t}</div>
        ))}
      </TridentCard>
    </div>
    <h3 className="text-foreground font-bold mb-2.5">Vertical Templates</h3>
    <DataTable
      headers={["VERTICAL", "SOFTWARE NAME", "PAIN POINT", "PROOF OF VALUE"]}
      rows={[
        ["Marketing Agencies", { text: "AgencyOS", color: "#F59E0B" }, "Client reporting, onboarding, churn", "40% less churn, 2hrs/week saved"],
        ["Med Spas", { text: "MedSpa Suite", color: "#F59E0B" }, "No-shows, reactivation, booking", "Cut no-shows 50%"],
        ["Real Estate", { text: "AgentFlow", color: "#F59E0B" }, "Lead follow-up, deal tracking", "3x faster pipeline"],
        ["Coaches/Consultants", { text: "CoachOS", color: "#F59E0B" }, "Client delivery, onboarding", "10hrs/week back"],
        ["E-commerce", { text: "StoreEngine", color: "#F59E0B" }, "Abandoned cart, retention, LTV", "+23% LTV"],
      ]}
    />
  </div>
);
