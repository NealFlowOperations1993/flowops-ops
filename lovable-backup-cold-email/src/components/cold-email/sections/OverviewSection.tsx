import { TridentCard } from "@/components/trident/TridentCard";
import { SectionHeader } from "../SectionHeader";
import { Highlight } from "../Highlight";

const stages = [
  { icon: "🕷️", label: "SCRAPE", title: "Data Acquisition", desc: "Apify bots crawl LinkedIn, Apollo, Google Maps, and Crunchbase 24/7, saving every matching founder's name, email, company, and title automatically. While you sleep.", color: "hsl(var(--blue))" },
  { icon: "🔬", label: "FILTER", title: "ICP Scoring & Cleaning", desc: "n8n reads every raw lead and asks: does this person match your ICP? Wrong title, wrong company size, bad email format — deleted instantly. Only the right people pass.", color: "hsl(var(--purple))" },
  { icon: "✅", label: "VERIFY", title: "Email Verification", desc: "Every address gets 'knocked on' via SMTP handshake before touching Smartlead. If the door doesn't exist, the lead is dropped. Zero bounces.", color: "hsl(var(--green))" },
  { icon: "🧠", label: "PERSONALIZE", title: "AI Personalization", desc: "Claude AI (Haiku model) writes a custom first line for every lead — referencing their company, role, or niche. Makes every email feel personally researched at scale.", color: "hsl(var(--amber))" },
  { icon: "📤", label: "LOAD", title: "Push to Smartlead", desc: "n8n pushes verified, personalized leads directly into Smartlead campaigns via API. No manual imports. Ever. Sequences auto-start.", color: "hsl(var(--red))" },
  { icon: "🔥", label: "SEND", title: "Sequence Execution", desc: "Smartlead sends across 20+ warmed inboxes, rotating domains, at human-like timing. Max 70-100/day per inbox so spam filters never see a blast.", color: "#F97316" },
  { icon: "💬", label: "REPLY", title: "Response Routing", desc: "Positive replies get classified by intent keywords and pushed into GHL as live opportunities automatically. Zero manual sorting.", color: "hsl(var(--cyan))" },
  { icon: "🏆", label: "CLOSE", title: "Funnel → Revenue", desc: "Interested leads hit your funnel, book a call, see the software demo, and you close them. The $49/month machine just fed you a real buyer.", color: "#EC4899" },
];

export const OverviewSection = () => (
  <div>
    <SectionHeader label="01 — OVERVIEW" title="The System: Simply Explained" subtitle="8 stages. Fully automated. $49/month." />
    <div className="grid grid-cols-2 gap-3">
      {stages.map(s => (
        <TridentCard key={s.label} accentColor={s.color}>
          <div className="flex gap-3 items-start">
            <div className="text-2xl shrink-0">{s.icon}</div>
            <div>
              <div className="font-mono text-[10px] tracking-[2px] mb-0.5" style={{ color: s.color }}>{s.label}</div>
              <div className="text-sm font-bold text-foreground mb-1.5">{s.title}</div>
              <div className="text-xs text-foreground-tertiary leading-relaxed">{s.desc}</div>
            </div>
          </div>
        </TridentCard>
      ))}
    </div>
    <Highlight color="hsl(var(--green))">
      The whole thing runs 24/7 with zero human input after setup. You set it up once. It feeds you leads forever.
    </Highlight>
  </div>
);
