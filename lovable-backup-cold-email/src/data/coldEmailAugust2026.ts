export type CategoryId =
  | "strategy"
  | "lead-data"
  | "infrastructure"
  | "campaigns"
  | "replies-sales"
  | "optimization";

export interface Category {
  id: CategoryId;
  label: string;
  token: string; // css var name for accent
}

export const CATEGORIES: Category[] = [
  { id: "strategy", label: "Strategy", token: "--cyan" },
  { id: "lead-data", label: "Lead Data", token: "--blue" },
  { id: "infrastructure", label: "Infrastructure", token: "--purple" },
  { id: "campaigns", label: "Campaigns", token: "--amber" },
  { id: "replies-sales", label: "Replies + Sales", token: "--green" },
  { id: "optimization", label: "Optimization", token: "--red" },
];

export interface Stage {
  num: string;
  id: string;
  title: string;
  category: CategoryId;
  summary: string;
  subprocess: string[];
  gates: string[];
  kpis: { label: string; hint: string }[];
}

export const STAGES: Stage[] = [
  {
    num: "01",
    id: "pick-niche",
    title: "Pick Niche",
    category: "strategy",
    summary:
      "Choose the market where urgent pain, economics, reachable TAM, identifiable decision makers, listability, timing triggers and manageable saturation all overlap.",
    subprocess: [
      "Map candidate niches against urgency of pain and willingness to pay",
      "Size reachable TAM (not total TAM) — how many can actually be listed and emailed",
      "Confirm decision makers are identifiable by title and reachable by email",
      "Test listability: can accounts be enumerated from at least two independent sources",
      "Identify timing triggers (funding, hiring, tech change, growth, seasonality)",
      "Score saturation: how many competitors already run cold outbound here",
      "Check economics: deal value must support acquisition cost with margin",
    ],
    gates: [
      "Adequate reachable TAM",
      "Pain is expensive enough to pay for",
      "Buyer is reachable by email",
      "There is a reason to act now",
    ],
    kpis: [
      { label: "TAM", hint: "Reachable accounts in niche" },
      { label: "Avg deal value", hint: "Expected ACV per closed account" },
      { label: "Reachable ICP %", hint: "Share of TAM that is listable + emailable" },
    ],
  },
  {
    num: "02",
    id: "create-offer",
    title: "Create Offer",
    category: "strategy",
    summary:
      "Quantify the pain and cost of inaction, then package a believable mechanism into a scoped, priced, risk-reversed offer with a low-friction CTA.",
    subprocess: [
      "Quantify current pain and cost of inaction in the buyer's own units",
      "State the desired outcome concretely and measurably",
      "Define the mechanism — why this works and why now",
      "Scope deliverables, exclusions and time-to-value",
      "Set pricing, payment terms and viable unit economics",
      "Add risk reversal (guarantee, pilot, staged commitment)",
      "Attach proof: results, named references, artefacts",
      "Pre-answer the top objections inside the offer itself",
      "Pick the lowest-friction CTA that still qualifies",
      "Create subsegment variants where the pain differs materially",
    ],
    gates: [
      "Concrete, measurable outcome",
      "Believable mechanism",
      "CTA is easy to say yes to",
      "Unit economics are viable",
    ],
    kpis: [
      { label: "ACV", hint: "Average contract value" },
      { label: "Gross margin", hint: "Margin after delivery cost" },
      { label: "Payback", hint: "Months to recover acquisition cost" },
    ],
  },
  {
    num: "03",
    id: "define-icp",
    title: "Define ICP + Segments",
    category: "strategy",
    summary:
      "Encode the ideal customer as queryable rules — firmographics, signals, titles, exclusions — and tier segments 1/2/3 by expected return.",
    subprocess: [
      "Encode company size, revenue band and industry",
      "Set geography and language constraints",
      "Capture technology and platform requirements",
      "Define hiring, funding and growth signals that indicate readiness",
      "List target titles, departments and seniority levels",
      "Write explicit exclusions (wrong size, wrong model, competitors, existing customers)",
      "Assign Tier 1 / Tier 2 / Tier 3 with a distinct reason-to-buy per tier",
      "Translate every rule into a query a data pipeline can execute",
    ],
    gates: [
      "Rules are queryable, not descriptive",
      "Each segment has a reason to buy",
      "Exclusions are explicit",
    ],
    kpis: [
      { label: "Segment count", hint: "Active, distinctly addressable segments" },
      { label: "ICP match rate", hint: "Share of sourced records passing ICP rules" },
      { label: "Tier-1 count", hint: "Accounts in highest-priority tier" },
    ],
  },
  {
    num: "04",
    id: "lead-sources",
    title: "Find Lead Sources",
    category: "lead-data",
    summary:
      "Build a prioritized portfolio of sources — databases, social, directories, registries, lawful intent signals — ranked by accuracy, freshness and cost.",
    subprocess: [
      "Inventory paid databases and their coverage per segment",
      "Add LinkedIn / Sales Navigator style search surfaces",
      "Add industry directories and association member lists",
      "Add maps and local listing data for geo-bound niches",
      "Mine job boards for hiring signals and stack disclosures",
      "Layer technology and funding datasets",
      "Pull review sites, event attendee and speaker lists",
      "Use public registries where lawful and relevant",
      "Add competitor and customer ecosystem signals, plus lawful intent data",
      "Score every source on accuracy, freshness and cost per usable record",
    ],
    gates: [
      "At least two independent sources per segment",
      "Source terms permit the intended use",
      "Cost per usable record within budget",
    ],
    kpis: [
      { label: "Cost / lead", hint: "Blended cost per usable record" },
      { label: "Coverage", hint: "Share of segment reachable via source mix" },
      { label: "Freshness", hint: "Median record age" },
    ],
  },
  {
    num: "05",
    id: "scrape-acquire",
    title: "Scrape / Acquire Leads",
    category: "lead-data",
    summary:
      "Capture raw account and contact records with full provenance into staging — never straight into production.",
    subprocess: [
      "Capture account fields: legal name, domain, location, firmographics",
      "Normalize the domain at capture time",
      "Record source URL and capture timestamp on every row",
      "Attach trigger evidence where the source provided it",
      "Capture contact name, title, department and profile URL",
      "Persist immutable source IDs for future re-sync",
      "Write everything to staging records, duplicates allowed",
      "Log per-source error and failure rates",
    ],
    gates: [
      "Provenance present on every row",
      "Domain normalized",
      "Duplicates confined to staging",
    ],
    kpis: [
      { label: "Raw leads / day", hint: "Acquisition throughput" },
      { label: "Source errors", hint: "Failed or malformed extractions" },
      { label: "Cost / raw record", hint: "Acquisition cost before enrichment" },
    ],
  },
  {
    num: "06",
    id: "normalize-dedupe",
    title: "Normalize + Deduplicate",
    category: "lead-data",
    summary:
      "Collapse staging noise into canonical accounts and contacts with stable IDs.",
    subprocess: [
      "Normalize domains, company names, titles, locations and phone formats",
      "Merge duplicate companies across sources",
      "Merge duplicate contacts within a company",
      "Remove malformed records and free-mail domains where unsuitable",
      "Drop inactive companies and obvious test records",
      "Assign canonical account and contact IDs",
      "Preserve the merge trail for auditability",
    ],
    gates: [
      "Canonical IDs assigned",
      "Duplicate rate below threshold",
      "Merge trail retained",
    ],
    kpis: [
      { label: "Duplicate rate", hint: "Share of staging rows merged away" },
      { label: "Invalid-domain rate", hint: "Malformed or unusable domains" },
      { label: "Retained %", hint: "Staging rows promoted to canonical" },
    ],
  },
  {
    num: "07",
    id: "enrich",
    title: "Enrich Leads",
    category: "lead-data",
    summary:
      "Add the variables messaging and scoring depend on, then compute ICP score and tier.",
    subprocess: [
      "Verify website and generate email candidates",
      "Fill firmographics: size, revenue band, category, description",
      "Detect technology stack and platform signals",
      "Attach social URLs and company locations",
      "Add funding, hiring, news and advertising activity",
      "Capture contact seniority and tenure",
      "Attach trigger evidence with source and date",
      "Compute ICP score and assign tier",
    ],
    gates: [
      "All required message variables present",
      "Score meets threshold",
      "Geographic and economic fit confirmed",
    ],
    kpis: [
      { label: "Fill rate", hint: "Required variables populated" },
      { label: "Cost / enriched lead", hint: "Enrichment spend per record" },
      { label: "ICP pass rate", hint: "Enriched records above score threshold" },
    ],
  },
  {
    num: "08",
    id: "verify-suppress",
    title: "Verify Email + Suppress",
    category: "lead-data",
    summary:
      "Validate deliverability and enforce every suppression rule before a record can ever be enrolled.",
    subprocess: [
      "Run syntax, MX and mailbox-level checks",
      "Flag catch-all, disposable, role and high-risk addresses",
      "Suppress prior hard bounces permanently",
      "Suppress unsubscribes, opt-outs and DNC entries",
      "Suppress existing customers, open opportunities, competitors and internal domains",
      "Apply jurisdiction-specific consent rules",
      "Store a confidence score per address",
    ],
    gates: [
      "Bounce risk under threshold",
      "All suppression lists applied",
      "Jurisdiction compliance confirmed",
    ],
    kpis: [
      { label: "Verified %", hint: "Addresses passing verification" },
      { label: "Risky %", hint: "Catch-all, role or high-risk share" },
      { label: "Expected bounce %", hint: "Modelled bounce before send" },
    ],
  },
  {
    num: "09",
    id: "personalize",
    title: "Personalize + Research",
    category: "lead-data",
    summary:
      "Produce factual, relevant, non-creepy relevance lines that map a real trigger to the offer — with a safe fallback for every record.",
    subprocess: [
      "Collect account-level and person-level observations",
      "Identify pain and trigger signals with evidence links",
      "Map each trigger to the relevant offer angle",
      "Write a concise relevance line — one idea, no flattery",
      "Attach segment-level problem, proof and CTA",
      "Run factuality and evidence checks on every claim",
      "Score confidence and generate a safe fallback variant",
    ],
    gates: [
      "Factually supported",
      "Relevant to the offer",
      "Not creepy or over-familiar",
      "Fallback present",
    ],
    kpis: [
      { label: "Coverage", hint: "Records with usable personalization" },
      { label: "Confidence", hint: "Mean personalization confidence" },
      { label: "Review-failure %", hint: "Lines rejected at QA" },
    ],
  },
  {
    num: "10",
    id: "domain-architecture",
    title: "Domain Architecture",
    category: "infrastructure",
    summary:
      "Run branded adjacent sending domains in pools with volume caps, retirement rules and reputation monitoring — never impersonation, never the primary domain.",
    subprocess: [
      "Register branded adjacent domains, no deceptive impersonation",
      "Maintain a domain inventory with renewal dates and owners",
      "Group domains into campaign pools",
      "Set sensible redirects to the primary web property",
      "Define per-domain volume caps",
      "Write replacement and retirement rules",
      "Monitor reputation and blocklists per domain",
      "Isolate the primary corporate domain from outbound entirely",
    ],
    gates: [
      "Primary domain isolated",
      "No impersonation of other brands",
      "Caps and retirement rules defined",
    ],
    kpis: [
      { label: "Active domains", hint: "Domains in rotation" },
      { label: "Leads / domain / day", hint: "Load per sending domain" },
      { label: "Domain health", hint: "Reputation and blocklist status" },
    ],
  },
  {
    num: "11",
    id: "dns-inbox",
    title: "DNS + Inbox Setup",
    category: "infrastructure",
    summary:
      "Stand up authenticated mailboxes with correct SPF, DKIM, DMARC and MX, real signatures, tested inbound routing and secured credentials.",
    subprocess: [
      "Standardize mailbox and display naming",
      "Configure SPF, DKIM, DMARC and MX per domain",
      "Decide tracking domain strategy carefully (or omit tracking)",
      "Build signatures that match a real, findable entity",
      "Define reply behaviour and inbound test coverage",
      "Assign routing and ownership for every inbox",
      "Secure credentials with MFA and documented recovery",
    ],
    gates: [
      "Authentication passes on all domains",
      "Inbound tests received and routed",
      "MFA enabled and recovery documented",
    ],
    kpis: [
      { label: "Auth pass rate", hint: "SPF/DKIM/DMARC pass share" },
      { label: "Inbox count", hint: "Live sending mailboxes" },
      { label: "Setup failures", hint: "Mailboxes failing validation" },
    ],
  },
  {
    num: "12",
    id: "warmup",
    title: "Warm-up + Reputation",
    category: "infrastructure",
    summary:
      "Ramp volume gradually with legitimate patterns, monitor placement, and pause, quarantine or retire inboxes on signal degradation.",
    subprocess: [
      "Ramp volume gradually with legitimate sending patterns",
      "Hold volume consistent day to day",
      "Keep bounces and complaints low by construction",
      "Monitor blocks, provider-level behaviour and inbox placement",
      "Define pause, quarantine and retire thresholds",
      "Run seed-list placement tests on a schedule",
    ],
    gates: [
      "Bounce rate under threshold",
      "Complaint rate under threshold",
      "Placement verified by seed tests",
    ],
    kpis: [
      { label: "Bounce rate", hint: "Hard + soft bounce share" },
      { label: "Complaint rate", hint: "Spam complaints per delivered" },
      { label: "Inbox placement", hint: "Seed-test inbox rate" },
    ],
  },
  {
    num: "13",
    id: "messaging",
    title: "Build Messaging",
    category: "campaigns",
    summary:
      "Compose modular emails — subject, opener, relevance, problem, mechanism, proof, CTA — into tested variants with follow-ups that close the loop.",
    subprocess: [
      "Write modular blocks: subject, opener, relevance, problem, mechanism, proof, CTA",
      "Build variant families: short, proof-heavy, trigger-led, direct",
      "Write follow-ups that add new information, not reminders",
      "Write a close-the-loop final message",
      "Strip fluff, flattery and fake familiarity",
      "Check mobile rendering and length",
      "Verify every claim is supported by real proof",
    ],
    gates: [
      "One idea per email",
      "CTA is easy",
      "Proof is relevant",
      "All claims supported",
    ],
    kpis: [
      { label: "Positive reply rate", hint: "Positives per delivered" },
      { label: "Reply rate", hint: "All replies per delivered" },
      { label: "Words / email", hint: "Length discipline" },
    ],
  },
  {
    num: "14",
    id: "assembly-qa",
    title: "Campaign Assembly + QA",
    category: "campaigns",
    summary:
      "Map segment to offer to inbox, set schedule and caps, wire stop rules, then pass a hard QA checklist before launch approval.",
    subprocess: [
      "Map segment → offer → inbox pool",
      "Wire variables with fallbacks for every field",
      "Set timezone, sending days, caps, spacing and follow-up timing",
      "Configure stop-on-reply and unsubscribe handling",
      "Configure reply and out-of-office handling",
      "Re-apply suppression at enrollment time",
      "Add seed addresses to every campaign",
      "Render previews across clients",
      "Check formatting, links, sender identity and duplicates",
      "Obtain explicit launch approval",
    ],
    gates: [
      "Zero QA errors outstanding",
      "Suppression re-applied at enrollment",
      "Launch approved by an owner",
    ],
    kpis: [
      { label: "QA errors", hint: "Defects found pre-launch" },
      { label: "Enrolled leads", hint: "Contacts entering sequences" },
      { label: "Daily capacity", hint: "Sendable volume per day" },
    ],
  },
  {
    num: "15",
    id: "launch-send",
    title: "Launch + Sending Engine",
    category: "campaigns",
    summary:
      "Release in small batches, watch bounce/block/reply signals, scale only while healthy, and keep suppression synchronized continuously.",
    subprocess: [
      "Release a small first batch and hold",
      "Monitor bounces, blocks and reply mix in real time",
      "Scale volume only while health signals hold",
      "Balance load across inboxes and domains",
      "Enforce caps; never send in bursts",
      "Pause on bad source or bad copy signals",
      "Quarantine unhealthy inboxes immediately",
      "Keep suppression synchronized continuously with sending",
    ],
    gates: [
      "Health signals within limits before each scale step",
      "No burst sending",
      "Suppression sync verified",
    ],
    kpis: [
      { label: "Sends", hint: "Volume dispatched" },
      { label: "Delivery", hint: "Delivered share of sends" },
      { label: "Bounce rate", hint: "Live bounce share" },
    ],
  },
  {
    num: "16",
    id: "reply-classification",
    title: "Reply Classification",
    category: "replies-sales",
    summary:
      "Ingest every reply, link it to its thread and lead, classify intent with confidence, escalate ambiguity to a human, suppress opt-outs immediately.",
    subprocess: [
      "Ingest replies and link to thread, campaign and lead",
      "Classify: positive, referral, question, objection, later, not interested",
      "Classify: unsubscribe, out-of-office, wrong person, hostile",
      "Score classification confidence",
      "Escalate low-confidence and hostile replies to a human",
      "Suppress opt-outs immediately and irreversibly",
    ],
    gates: [
      "Opt-outs suppressed immediately",
      "Low-confidence replies human-reviewed",
      "Every reply linked to a lead",
    ],
    kpis: [
      { label: "Positives", hint: "Positive replies per period" },
      { label: "Accuracy", hint: "Classification accuracy vs audit" },
      { label: "SLA", hint: "Time to classification" },
    ],
  },
  {
    num: "17",
    id: "qualification",
    title: "Qualification + Response",
    category: "replies-sales",
    summary:
      "Respond fast and in context, confirm fit, problem, authority, timing and commercial fit, then offer booking with minimal friction.",
    subprocess: [
      "Respond quickly, in the thread, in context",
      "Answer the question actually asked",
      "Confirm fit, problem, authority, timing and commercial fit",
      "Send the minimum information needed to progress",
      "Offer concrete booking options",
      "Route valuable and referral replies to the right owner",
      "Create the opportunity record on qualification",
    ],
    gates: [
      "Response within SLA",
      "Qualification criteria captured",
      "Opportunity created for qualified replies",
    ],
    kpis: [
      { label: "Reply-to-meeting", hint: "Meetings per positive reply" },
      { label: "Response time", hint: "Median first-response latency" },
      { label: "Qualified %", hint: "Replies passing qualification" },
    ],
  },
  {
    num: "18",
    id: "booking",
    title: "Booking + Show-Up Engine",
    category: "replies-sales",
    summary:
      "Convert intent into held meetings with correct timezones, pre-call context, reminders and explicit no-show recovery.",
    subprocess: [
      "Handle calendar availability and timezone correctly",
      "Send immediate confirmation",
      "Send pre-call context and proof",
      "Send reminder sequence before the call",
      "Make rescheduling one click",
      "Detect cancellations and no-shows automatically",
      "Run a no-show recovery sequence",
      "Log the final meeting outcome",
    ],
    gates: [
      "Confirmation and reminders sent",
      "No-shows detected and routed to recovery",
      "Outcome logged for every booking",
    ],
    kpis: [
      { label: "Booking rate", hint: "Bookings per positive reply" },
      { label: "Show rate", hint: "Held meetings per booked" },
      { label: "No-show recovery", hint: "Recovered share of no-shows" },
    ],
  },
  {
    num: "19",
    id: "crm-handoff",
    title: "CRM + Sales Handoff",
    category: "replies-sales",
    summary:
      "Upsert account, contact and opportunity with the full outbound evidence trail so downstream revenue can be attributed backwards.",
    subprocess: [
      "Upsert account, contact and opportunity records",
      "Attach source, segment and trigger evidence",
      "Attach thread, copy variant and offer used",
      "Set owner, stage, value and next action",
      "Log meeting outcome and objections raised",
      "Log lost reason, win and realized revenue",
    ],
    gates: [
      "Evidence trail attached",
      "Owner and next action set",
      "Outcome fields completed",
    ],
    kpis: [
      { label: "Meetings→opportunities", hint: "Conversion into pipeline" },
      { label: "Close rate", hint: "Won share of opportunities" },
      { label: "Revenue / meeting", hint: "Realized revenue per held meeting" },
    ],
  },
  {
    num: "20",
    id: "analytics",
    title: "Analytics + Attribution",
    category: "optimization",
    summary:
      "Track the full chain from sourced to revenue and attribute outcomes to source, segment, campaign, copy and inbox pool — with consistent definitions.",
    subprocess: [
      "Track sourced → verified → sent → delivered",
      "Track replies, positive replies and unsubscribes",
      "Track booked → held → opportunity → won → revenue",
      "Attribute outcomes to source, segment, campaign, copy variant and inbox pool",
      "Attach costs and compute CAC",
      "Compute revenue per 1,000 delivered",
      "Analyse by cohort, not blended averages",
      "Exclude bots and automated noise",
    ],
    gates: [
      "Revenue attributable to source and segment",
      "Metric definitions consistent across reports",
      "Bot and noise traffic excluded",
    ],
    kpis: [
      { label: "Positive reply %", hint: "Positives per delivered" },
      { label: "Meeting %", hint: "Held meetings per delivered" },
      { label: "CAC", hint: "Cost per acquired customer" },
    ],
  },
  {
    num: "21",
    id: "optimization-loops",
    title: "Optimization Loops",
    category: "optimization",
    summary:
      "Compare controlled variables against downstream revenue truth, promote winners, pause losers, and keep a disciplined test backlog.",
    subprocess: [
      "Compare segments, sources and offers on revenue outcomes",
      "Compare copy, triggers, titles, company size and geography",
      "Analyse objections and lost reasons for patterns",
      "Promote winners and pause losers explicitly",
      "Revise hooks, proof and CTAs based on findings",
      "Revise qualification, enrichment, scoring and suppression rules",
      "Refresh stale leads on a schedule",
      "Maintain a controlled, prioritized test backlog",
    ],
    gates: [
      "Decisions tied to downstream outcomes",
      "One controlled variable per test",
      "Backlog prioritized by expected value",
    ],
    kpis: [
      { label: "Lift per test", hint: "Measured improvement per experiment" },
      { label: "Time-to-learning", hint: "Days from launch to decision" },
      { label: "Revenue per lead", hint: "Realized revenue per sourced lead" },
    ],
  },
  {
    num: "22",
    id: "governance",
    title: "Governance + Maintenance",
    category: "optimization",
    summary:
      "Assign owners, keep consent and security current, refresh data on schedule, and review the full funnel with documentation that stays true.",
    subprocess: [
      "Define system owners and maintain a change log",
      "Review consent and compliance by jurisdiction",
      "Enforce data retention and minimization",
      "Audit security and access regularly",
      "Review vendors and costs",
      "Run scheduled data refreshes",
      "Audit sending infrastructure periodically",
      "Define incident and complaint escalation paths",
      "Own SLAs and keep runbooks current",
      "Run periodic full-funnel review and update documentation",
    ],
    gates: [
      "Owners assigned for every subsystem",
      "Opt-outs immutable",
      "Access reviewed on schedule",
      "Runbooks current",
    ],
    kpis: [
      { label: "Compliance exceptions", hint: "Open compliance issues" },
      { label: "Stale-data %", hint: "Records past refresh window" },
      { label: "Incident resolution", hint: "Median time to resolve" },
    ],
  },
];

export interface FeedbackLoop {
  from: string;
  to: string;
  detail: string;
  targets: string[]; // stage nums
}

export const FEEDBACK_LOOPS: FeedbackLoop[] = [
  {
    from: "Replies, objections, lost reasons",
    to: "Offer + copy",
    detail:
      "Every objection and lost reason is a defect report on the offer or the message. Patterns rewrite the mechanism, proof and CTA — not just the subject line.",
    targets: ["02", "13"],
  },
  {
    from: "Meetings, opportunities, revenue",
    to: "ICP scoring, segments, sources",
    detail:
      "Revenue truth re-weights ICP scoring and re-prioritizes which segments and which data sources get budget next cycle.",
    targets: ["03", "04", "07"],
  },
  {
    from: "Bounce, complaint, inbox placement",
    to: "Verification, sources, infrastructure",
    detail:
      "Deliverability degradation traces back to a data source or an inbox. Fix verification thresholds, retire the source, adjust domain health and lower volume caps.",
    targets: ["08", "10", "12", "15"],
  },
  {
    from: "Personalization review failures",
    to: "Research rules + fallbacks",
    detail:
      "Failed QA lines tighten research rules, raise evidence requirements and improve the safe fallback so coverage never depends on invention.",
    targets: ["09"],
  },
  {
    from: "Test results",
    to: "Experiment backlog → controlled relaunch",
    detail:
      "Results feed a prioritized backlog. Winners are promoted with one variable changed at a time; losers are documented, not silently retried.",
    targets: ["21", "14"],
  },
];
