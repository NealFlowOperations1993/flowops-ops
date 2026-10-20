interface Props {
  label: string;
  title: string;
  subtitle?: string;
}

export const SectionHeader = ({ label, title, subtitle }: Props) => (
  <div className="mb-6">
    <div className="font-mono text-[10px] tracking-[3px] text-foreground-tertiary mb-1.5">{label}</div>
    <h2 className="text-[28px] font-black text-foreground tracking-tight">{title}</h2>
    {subtitle && <p className="text-sm text-foreground-tertiary mt-1.5">{subtitle}</p>}
    <div className="h-px mt-4" style={{ background: "linear-gradient(90deg, hsl(var(--blue) / 0.33), transparent)" }} />
  </div>
);
