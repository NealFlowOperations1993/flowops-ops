import { TridentCard } from "@/components/trident/TridentCard";
import { CopyBlock } from "@/components/trident/CopyBlock";
import { SectionHeader } from "../SectionHeader";

export const CopySection = () => (
  <div>
    <SectionHeader label="08 — EMAIL COPY" title="The 3-Email Sequence Framework" subtitle="One job: get a curious click. The funnel sells." />
    <div className="grid grid-cols-3 gap-4">
      {[
        { label: "EMAIL 1 — THE HOOK", day: "Day 1", color: "hsl(var(--blue))", code: `Subject A: quick question about {companyName}\nSubject B: built something for {industry}\nSubject C: {firstName} — 2 min?\n\n---\n\nHey {firstName},\n\n{personalizedOpener}\n\nBuilt a custom system for {industry} owners\nthat eliminates {specific pain}.\nAlready running for 2 others.\n\nWorth a 5-minute look? [LINK]\n\n[Your name]` },
        { label: "EMAIL 2 — FOLLOW UP", day: "Day 3-4", color: "hsl(var(--purple))", code: `Subject: re: quick question about {companyName}\n\n---\n\nHey {firstName},\n\nDidn't want this to get buried —\n[Client X] in {industry} used this\nto [specific result].\n\nFigured it might be relevant too.\n\nStill happy to show you: [LINK]\n\n[Your name]` },
        { label: "EMAIL 3 — BREAKUP", day: "Day 7", color: "hsl(var(--green))", code: `Subject: closing the loop\n\n---\n\nHey {firstName},\n\nGoing to assume the timing\nisn't right — no worries at all.\n\nIf that changes: [LINK]\n\nGood luck with {companyName} —\nlooks like you're building\nsomething real.\n\n[Your name]` },
      ].map(e => (
        <CopyBlock key={e.label} label={`${e.label} (${e.day})`} content={e.code} />
      ))}
    </div>
    <h3 className="text-foreground font-bold mt-5 mb-2.5">Non-Negotiable Rules</h3>
    <div className="grid grid-cols-2 gap-1.5">
      {[
        ["NEVER", "Use the word 'AI' in a subject line", "hsl(var(--red))"],
        ["NEVER", "Send more than 3 emails in a sequence", "hsl(var(--red))"],
        ["NEVER", "Have more than one CTA per email", "hsl(var(--red))"],
        ["NEVER", "Write more than 5 lines total", "hsl(var(--red))"],
        ["ALWAYS", "Use their first name in Email 1", "hsl(var(--green))"],
        ["ALWAYS", "Mention their company or vertical specifically", "hsl(var(--green))"],
        ["ALWAYS", "Sound like a peer — not a vendor", "hsl(var(--green))"],
        ["ALWAYS", "Test 3 subject line variants minimum", "hsl(var(--green))"],
      ].map(([type, rule, color]) => (
        <div key={rule as string} className="flex gap-2 items-start py-1.5">
          <span className="font-mono text-[11px] font-bold px-2.5 py-0.5 rounded shrink-0" style={{ background: (color as string) + "22", border: `1px solid ${color}55`, color: color as string }}>{type}</span>
          <span className="text-foreground-secondary text-xs pt-0.5">{rule}</span>
        </div>
      ))}
    </div>
  </div>
);
