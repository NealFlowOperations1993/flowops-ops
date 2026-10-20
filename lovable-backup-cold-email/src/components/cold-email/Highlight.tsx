interface Props {
  color?: string;
  children: React.ReactNode;
}

export const Highlight = ({ color = "hsl(var(--blue))", children }: Props) => (
  <div
    className="rounded-lg p-3 my-3 font-bold text-[13px]"
    style={{ background: color + "15", border: `1px solid ${color}40`, color }}
  >
    {children}
  </div>
);

export const Bullet = ({ children, color = "hsl(var(--green))" }: Props) => (
  <div className="flex gap-2.5 mb-1.5">
    <span className="shrink-0 mt-0.5" style={{ color }}>→</span>
    <span className="text-foreground-secondary text-[13px] leading-relaxed">{children}</span>
  </div>
);
