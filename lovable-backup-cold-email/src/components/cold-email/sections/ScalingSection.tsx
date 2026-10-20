import { SectionHeader } from "../SectionHeader";
import { DataTable } from "../DataTable";
import { Highlight } from "../Highlight";

export const ScalingSection = () => (
  <div>
    <SectionHeader label="13 — SCALING" title="The Scaling Playbook" subtitle="Scale is earned. Follow this sequence exactly." />
    <DataTable
      headers={["STEP", "ACTION", "TIMING", "CONDITION TO PROCEED"]}
      rows={[
        [{ text: "1", color: "#3B82F6" }, "Validate copy", "April", "Open rate >35% AND reply rate >1.5% on 200+ sends"],
        [{ text: "2", color: "#3B82F6" }, "Validate ICP", "April-May", "Positive replies are actually in your target vertical with budget"],
        [{ text: "3", color: "#3B82F6" }, "Validate offer", "May", "At least 1 closed deal from cold email — machine is proven"],
        [{ text: "4", color: "#3B82F6" }, "Scale inboxes", "May-June", "Add 3 domains per 12K additional emails/month target"],
        [{ text: "5", color: "#3B82F6" }, "Add Aerosend", "June", "When domains start burning OR hitting 30K+/month"],
        [{ text: "6", color: "#3B82F6" }, "Add AI personalization", "June", "After copy validated — personalization amplifies what's working"],
        [{ text: "7", color: "#3B82F6" }, "Hire setter", "June-July", "When positive reply volume exceeds your personal bandwidth"],
        [{ text: "8", color: "#3B82F6" }, "Add verticals", "July+", "Launch new vertical every 4-6 weeks with proven template"],
      ]}
    />
    <Highlight color="hsl(var(--green))">
      The machine is simple. The discipline is hard. Execute the protocol every day and the math does the rest.
    </Highlight>
  </div>
);
