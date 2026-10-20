import { cn } from "@/lib/utils";

export const SECTIONS = [
  { id: "overview", icon: "⚡", label: "Overview" },
  { id: "metrics", icon: "📊", label: "Live Metrics" },
  { id: "growth", icon: "📈", label: "Growth Chart" },
  { id: "stack", icon: "🛠️", label: "Tech Stack" },
  { id: "pipeline", icon: "⚙️", label: "Pipeline" },
  { id: "phases", icon: "🗺️", label: "Phases" },
  { id: "domains", icon: "🌐", label: "Domains" },
  { id: "warmup", icon: "🔥", label: "Warmup" },
  { id: "icp", icon: "🎯", label: "ICP & Scraping" },
  { id: "copy", icon: "✉️", label: "Email Copy" },
  { id: "offer", icon: "💡", label: "The Offer" },
  { id: "projections", icon: "📉", label: "Projections" },
  { id: "deliverability", icon: "📬", label: "Deliverability" },
  { id: "ops", icon: "📋", label: "Daily Ops" },
  { id: "scaling", icon: "🚀", label: "Scaling" },
  { id: "prompts", icon: "🤖", label: "Claude Code" },
] as const;

export type SectionId = typeof SECTIONS[number]["id"];

interface Props {
  active: SectionId;
  onSelect: (id: SectionId) => void;
}

export const ColdEmailSidebar = ({ active, onSelect }: Props) => (
  <div className="w-[220px] bg-background border-r border-border flex flex-col sticky top-0 h-screen overflow-y-auto shrink-0">
    <div className="p-4 border-b border-border">
      <div className="font-mono text-[9px] tracking-[3px] text-primary mb-1">FLOWOPERATIONS</div>
      <div className="text-sm font-extrabold text-foreground">War Machine</div>
      <div className="text-[11px] text-foreground-tertiary">Cold Email Playbook</div>
    </div>
    <nav className="flex-1 py-2">
      {SECTIONS.map(s => (
        <button
          key={s.id}
          onClick={() => onSelect(s.id)}
          className={cn(
            "w-full flex items-center gap-2.5 px-4 py-2.5 text-xs transition-all text-left border-l-2",
            active === s.id
              ? "bg-primary/10 border-primary text-foreground font-semibold"
              : "border-transparent text-foreground-tertiary hover:text-foreground-secondary"
          )}
        >
          <span>{s.icon}</span>
          <span>{s.label}</span>
        </button>
      ))}
    </nav>
    <div className="p-3 border-t border-border">
      <div className="font-mono text-[10px] text-foreground-tertiary/40">BUILT APR 2026</div>
    </div>
  </div>
);
