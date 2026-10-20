import { SectionHeader } from "../SectionHeader";
import { DataTable } from "../DataTable";
import { CopyBlock } from "@/components/trident/CopyBlock";

export const PipelineSection = () => (
  <div>
    <SectionHeader label="03 — PIPELINE" title="8-Stage Lead Flow Architecture" />
    <DataTable
      headers={["STAGE", "ACTION", "TOOL", "PASS RATE", "OUTPUT"]}
      rows={[
        [{ text: "1 — SCRAPE", color: "#93C5FD" }, "Bots collect raw leads from 4 sources", "Apify", "100%", "~100K raw/mo at scale"],
        [{ text: "2 — FILTER", color: "#93C5FD" }, "ICP scoring: title, size, email quality", "n8n Code Node", "40-60%", "ICP-matched leads"],
        [{ text: "3 — DEDUPE", color: "#93C5FD" }, "Remove leads already in campaigns", "n8n + Smartlead API", "95%+", "No duplicate sends"],
        [{ text: "4 — PERSONALIZE", color: "#93C5FD" }, "AI writes custom opener per lead", "Claude API (Haiku)", "100%", "Personalized objects"],
        [{ text: "5 — VERIFY", color: "#93C5FD" }, "SMTP handshake on every email", "Debounce API", "70-80%", "~25-40K verified/mo"],
        [{ text: "6 — PUSH", color: "#93C5FD" }, "Load into Smartlead campaign via API", "n8n + Smartlead API", "100%", "Live in sequences"],
        [{ text: "7 — SEND", color: "#93C5FD" }, "Sequences fire across warmed inboxes", "Smartlead", "50%+ open rate", "Emails delivered"],
        [{ text: "8 — ROUTE", color: "#93C5FD" }, "Positive replies → GHL opportunities", "n8n + GHL", "1-5% reply rate", "Pipeline opportunities"],
      ]}
    />
    <div className="mt-5">
      <h3 className="text-foreground font-bold mb-2">n8n Flow Architecture</h3>
      <CopyBlock label="N8N PIPELINE" content={`Apify Dataset Webhook (POST trigger)
        ↓
[Node 1] Fetch Dataset Items (HTTP GET → Apify API)
        ↓
[Node 2] ICP Filter (Code: title, size, email validation)
        ↓
[Node 3] Deduplicate vs Smartlead existing leads
        ↓
[Node 4] AI Personalization (Claude API → custom opener)
        ↓
[Node 5] Email Verification (Debounce API)
        ↓
[Node 6] Drop invalid emails (Filter node)
        ↓
[Node 7] Push to Smartlead Campaign (HTTP POST)
        ↓
[Node 8] Slack Notification (Pipeline complete summary)`} />
    </div>
  </div>
);
