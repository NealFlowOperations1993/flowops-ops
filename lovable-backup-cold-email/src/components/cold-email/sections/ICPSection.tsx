import { SectionHeader } from "../SectionHeader";
import { DataTable } from "../DataTable";

export const ICPSection = () => (
  <div>
    <SectionHeader label="07 — ICP & SCRAPING" title="Who to Target & How to Find Them" />
    <h3 className="text-foreground font-bold mb-2.5">ICP Definition</h3>
    <DataTable
      headers={["ATTRIBUTE", "TARGET VALUE", "FILTER RULE"]}
      rows={[
        ["Title", "Founder, Owner, CEO, Co-Founder, President", "Must contain at least one (case insensitive)"],
        ["Company Size", "1-50 employees", "Exclude 51+ — too corporate, long sales cycle"],
        ["Revenue Signal", "$30K-$500K/month", "Use funding data or traffic as proxy"],
        ["Geography", "United States", "US-first for Phase 1-2"],
        ["Email Format", "Work email only", "Drop gmail/yahoo/hotmail at filter stage"],
        ["Industry", "Agencies, SaaS, E-comm, Med Spa", "Define per campaign — one vertical per campaign"],
      ]}
    />
    <h3 className="text-foreground font-bold mt-5 mb-2.5">Scraping Sources</h3>
    <DataTable
      headers={["SOURCE", "APIFY ACTOR", "LEADS/RUN", "QUALITY", "BEST FOR"]}
      rows={[
        ["LinkedIn", "linkedin-profile-scraper", "200-500", { text: "★★★★", color: "#F59E0B" }, "Title-filtered, professional leads"],
        ["Apollo.io", "apollo-scraper", "500-1000", { text: "★★★★★", color: "#10B981" }, "Best emails + firmographics"],
        ["Google Maps", "google-maps-scraper", "500-2000", { text: "★★★", color: "#F59E0B" }, "Local businesses, med spas, agencies"],
        ["Crunchbase", "crunchbase-scraper", "100-300", { text: "★★★★", color: "#F59E0B" }, "Funded startups with growth signal"],
      ]}
    />
  </div>
);
