import { TridentCard } from "@/components/trident/TridentCard";
import { SectionHeader } from "../SectionHeader";
import { DataTable } from "../DataTable";

export const StackSection = () => (
  <div>
    <SectionHeader label="02 — TECH STACK" title="Full Stack Breakdown" subtitle="Every tool, its role, what it costs." />
    <DataTable
      headers={["LAYER", "TOOL", "ROLE", "COST", "STATUS"]}
      rows={[
        ["Scraping", "Apify", "Runs scrapers on LinkedIn, Apollo, Maps, Crunchbase", "$49/mo", { text: "NEED", color: "#F59E0B" }],
        ["Pipeline", "n8n (self-hosted)", "Connects everything. Filters, transforms, routes all data", "$0", { text: "HAVE", color: "#10B981" }],
        ["Verification", "Debounce / Millionverifier", "Validates every email before touching Smartlead", "$10/5K", { text: "NEED", color: "#F59E0B" }],
        ["Sending", "Smartlead", "Sequences, warmup, inbox rotation, reply detection", "Have it", { text: "HAVE", color: "#10B981" }],
        ["Infra (Scale)", "Aerosend", "Private dedicated IPs for high-volume sending", "$120+/mo", { text: "PHASE 3", color: "#06B6D4" }],
        ["CRM", "GoHighLevel", "Receives replies, books calls, fires automations", "Have it", { text: "HAVE", color: "#10B981" }],
        ["AI Copy", "Claude API (Haiku)", "Writes personalized first lines per lead at scale", "~$5/10K", { text: "NEED", color: "#F59E0B" }],
        ["Domains", "Namecheap", "Sending domains — NEVER your primary domain", "$1-2/yr/ea", { text: "BUY NOW", color: "#EF4444" }],
        ["Monitoring", "n8n + Slack", "Daily briefings, health alerts, pipeline status", "$0", { text: "BUILD", color: "#8B5CF6" }],
      ]}
    />
    <div className="grid grid-cols-3 gap-3 mt-5">
      {[
        ["April", "$49", "Apify only"],
        ["May", "$70-100", "+ Debounce + Claude API"],
        ["June+", "$170-220", "+ Aerosend at scale"],
      ].map(([m, cost, note]) => (
        <TridentCard key={m as string}>
          <div className="font-mono text-[11px] text-foreground-tertiary mb-1">{m}</div>
          <div className="text-[28px] font-black text-green">{cost}</div>
          <div className="text-[11px] text-foreground-tertiary">{note}</div>
        </TridentCard>
      ))}
    </div>
  </div>
);
