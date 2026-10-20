import { useState } from "react";
import { ColdEmailSidebar, SectionId } from "@/components/cold-email/ColdEmailSidebar";
import { OverviewSection } from "@/components/cold-email/sections/OverviewSection";
import { LiveMetricsSection } from "@/components/cold-email/sections/LiveMetricsSection";
import { GrowthChartSection } from "@/components/cold-email/sections/GrowthChartSection";
import { StackSection } from "@/components/cold-email/sections/StackSection";
import { PipelineSection } from "@/components/cold-email/sections/PipelineSection";
import { PhasesSection } from "@/components/cold-email/sections/PhasesSection";
import { DomainsSection } from "@/components/cold-email/sections/DomainsSection";
import { WarmupSection } from "@/components/cold-email/sections/WarmupSection";
import { ICPSection } from "@/components/cold-email/sections/ICPSection";
import { CopySection } from "@/components/cold-email/sections/CopySection";
import { OfferSection } from "@/components/cold-email/sections/OfferSection";
import { ProjectionsSection } from "@/components/cold-email/sections/ProjectionsSection";
import { DeliverabilitySection } from "@/components/cold-email/sections/DeliverabilitySection";
import { OpsSection } from "@/components/cold-email/sections/OpsSection";
import { ScalingSection } from "@/components/cold-email/sections/ScalingSection";
import { PromptsSection } from "@/components/cold-email/sections/PromptsSection";

const SECTION_COMPONENTS: Record<SectionId, React.FC> = {
  overview: OverviewSection,
  metrics: LiveMetricsSection,
  growth: GrowthChartSection,
  stack: StackSection,
  pipeline: PipelineSection,
  phases: PhasesSection,
  domains: DomainsSection,
  warmup: WarmupSection,
  icp: ICPSection,
  copy: CopySection,
  offer: OfferSection,
  projections: ProjectionsSection,
  deliverability: DeliverabilitySection,
  ops: OpsSection,
  scaling: ScalingSection,
  prompts: PromptsSection,
};

const ColdEmailPage = () => {
  const [active, setActive] = useState<SectionId>("overview");
  const ActiveSection = SECTION_COMPONENTS[active];

  return (
    <div className="flex -m-6 -mt-6 min-h-[calc(100vh-0px)]">
      <ColdEmailSidebar active={active} onSelect={setActive} />
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-[960px] mx-auto p-8 pb-20">
          <ActiveSection />
        </div>
      </div>
    </div>
  );
};

export default ColdEmailPage;
