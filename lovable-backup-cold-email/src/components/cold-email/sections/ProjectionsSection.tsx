import { SectionHeader } from "../SectionHeader";
import { DataTable } from "../DataTable";
import { Highlight } from "../Highlight";

export const ProjectionsSection = () => (
  <div>
    <SectionHeader label="10 — PROJECTIONS" title="Realistic Revenue Projections" subtitle="Honest numbers only. No hype." />
    <DataTable
      headers={["MONTH", "EMAILS", "POS. REPLIES", "CALLS", "CLOSES", "CONSERVATIVE", "REALISTIC"]}
      rows={[
        ["April", "1,000", "3-8", "1-3", "0-1", "$0-10K", { text: "$0-10K", color: "#F59E0B" }],
        ["May", "12,000", "36-96", "14-38", "3-10", "$30K", { text: "$60-100K", color: "#10B981" }],
        ["June", "24,000", "72-192", "29-77", "6-19", "$60K", { text: "$90-190K", color: "#10B981" }],
        ["July", "36,000", "108-288", "43-115", "9-29", "$90K", { text: "$150-290K", color: "#10B981" }],
        ["August", "48,000", "144-384", "58-154", "12-38", "$120K", { text: "$200-380K", color: "#10B981" }],
        ["December", "96,000", "288-768", "115-307", "23-77", "$230K", { text: "$577K+", color: "#10B981" }],
      ]}
    />
    <div className="grid grid-cols-2 gap-4 mt-5">
      <Highlight color="hsl(var(--red))">
        🚧 DELIVERY CONSTRAINT: At 10 closes/month you have 10 builds to deliver. Use Claude Code + vertical templates. Budget 15-20 days of build time or hire a developer on retainer by May.
      </Highlight>
      <Highlight color="hsl(var(--amber))">
        🚧 COPY TAKES TIME: April is market research. Week-1 copy will not be your best copy. Expect 2-3 weeks to find what converts for your ICP.
      </Highlight>
    </div>
    <div className="mt-4 bg-background rounded-xl border border-primary/25 p-5 text-center">
      <div className="text-[13px] text-foreground-tertiary mb-1.5">December — At Full Scale</div>
      <div className="text-4xl font-black text-green">$577,500/month</div>
      <div className="text-[13px] text-foreground-tertiary mt-1">in pipeline from a $49/month infrastructure</div>
    </div>
  </div>
);
