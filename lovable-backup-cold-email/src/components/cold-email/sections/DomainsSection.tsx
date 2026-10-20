import { SectionHeader } from "../SectionHeader";
import { DataTable } from "../DataTable";
import { Highlight } from "../Highlight";
import { TridentBadge } from "@/components/trident/TridentBadge";

export const DomainsSection = () => (
  <div>
    <SectionHeader label="05 — DOMAINS" title="Domain & Inbox Infrastructure" />
    <Highlight color="hsl(var(--red))">CRITICAL: Never send cold email from your primary domain. Ever. Buy dedicated sending domains.</Highlight>
    <h3 className="text-foreground font-bold mt-5 mb-2.5">Domain Naming Strategy</h3>
    <DataTable
      headers={["PATTERN", "EXAMPLE", "WHY IT WORKS"]}
      rows={[
        ["[word]+[word].com", "growthsync.co, flowops.io", "Sounds like a real brand"],
        ["[brand]-[word].com", "flowops-hq.com", "Related but distinct from primary"],
        ["[industry]+[word].com", "agencytools.co", "Niche-relevant for ICP trust"],
        ["[action]+[word].com", "getresults.io, buildsystems.co", "Action-oriented, memorable"],
      ]}
    />
    <h3 className="text-foreground font-bold mt-5 mb-2.5">DNS Records (Copy These Exact Values)</h3>
    <DataTable
      headers={["RECORD TYPE", "NAME/HOST", "VALUE", "TTL"]}
      rows={[
        [{ text: "TXT (SPF)", color: "#93C5FD" }, "@", "v=spf1 include:_spf.smartlead.ai ~all", "3600"],
        [{ text: "TXT (DKIM)", color: "#93C5FD" }, "smartlead._domainkey", "[Get from Smartlead → Inbox Settings]", "3600"],
        [{ text: "TXT (DMARC)", color: "#93C5FD" }, "_dmarc", "v=DMARC1; p=none; rua=mailto:dmarc@yourdomain.com", "3600"],
      ]}
    />
    <p className="text-foreground-tertiary text-[13px] mt-3">✓ Verify records at: mxtoolbox.com/spf and mail-tester.com</p>
  </div>
);
