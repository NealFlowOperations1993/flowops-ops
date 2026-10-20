import { useMemo, useState } from "react";
import { cn } from "@/lib/utils";
import { PageHeader } from "@/components/trident/PageHeader";
import {
  CATEGORIES,
  STAGES,
  FEEDBACK_LOOPS,
  type CategoryId,
  type Stage,
} from "@/data/coldEmailAugust2026";
import { ArrowRight, CheckCircle2, ShieldCheck, Gauge, RefreshCw, ChevronRight } from "lucide-react";

type FilterId = "all" | CategoryId;

const accentOf = (id: CategoryId) =>
  `hsl(var(${CATEGORIES.find((c) => c.id === id)!.token}))`;

const labelOf = (id: CategoryId) => CATEGORIES.find((c) => c.id === id)!.label;

const ColdEmailAugust2026Page = () => {
  const [filter, setFilter] = useState<FilterId>("all");
  const [selectedId, setSelectedId] = useState<string>(STAGES[0].id);

  const visible = useMemo(
    () => (filter === "all" ? STAGES : STAGES.filter((s) => s.category === filter)),
    [filter],
  );

  const selected: Stage =
    visible.find((s) => s.id === selectedId) ?? visible[0] ?? STAGES[0];

  const pills: { id: FilterId; label: string }[] = [
    { id: "all", label: "Entire System" },
    ...CATEGORIES.map((c) => ({ id: c.id as FilterId, label: c.label })),
  ];

  const totalGates = STAGES.reduce((n, s) => n + s.gates.length, 0);
  const totalKpis = STAGES.reduce((n, s) => n + s.kpis.length, 0);

  return (
    <div className="pb-20">
      <PageHeader
        badge="// SYSTEM MAP"
        title="Cold Email: August 2026"
        subtitle="The complete cold-email operating system in 22 stages — from market selection and offer construction, through lead data, sending infrastructure, campaigns and reply handling, to revenue attribution, optimization loops and governance."
      />

      {/* Summary strip */}
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        {[
          { icon: ChevronRight, label: "Stages", value: "22" },
          { icon: ShieldCheck, label: "Quality gates", value: String(totalGates) },
          { icon: Gauge, label: "Tracked KPIs", value: String(totalKpis) },
          { icon: RefreshCw, label: "Feedback loops", value: String(FEEDBACK_LOOPS.length) },
        ].map((k) => (
          <div
            key={k.label}
            className="bg-background-secondary border border-border rounded-lg p-4 flex items-center gap-3"
          >
            <k.icon className="w-4 h-4 text-cyan shrink-0" />
            <div>
              <div className="font-mono text-[10px] tracking-[0.18em] uppercase text-foreground-tertiary">
                {k.label}
              </div>
              <div className="font-display text-2xl text-foreground leading-tight">{k.value}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Filter pills */}
      <div
        className="flex flex-wrap gap-2 mb-6"
        role="group"
        aria-label="Filter stages by category"
      >
        {pills.map((p) => {
          const active = filter === p.id;
          const accent = p.id === "all" ? "hsl(var(--cyan))" : accentOf(p.id as CategoryId);
          return (
            <button
              key={p.id}
              type="button"
              aria-pressed={active}
              onClick={() => setFilter(p.id)}
              className={cn(
                "px-3.5 py-1.5 rounded-full text-xs transition-colors border focus:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                active
                  ? "text-foreground"
                  : "text-foreground-secondary border-border hover:text-foreground hover:bg-background-secondary",
              )}
              style={
                active
                  ? { borderColor: accent, background: `color-mix(in srgb, ${accent} 14%, transparent)` }
                  : undefined
              }
            >
              {p.label}
            </button>
          );
        })}
      </div>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_400px] items-start">
        {/* System map */}
        <div>
          <div className="font-mono text-[10px] tracking-[0.2em] uppercase text-foreground-tertiary mb-3">
            Flow sequence — left to right, top to bottom
          </div>
          <ul className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {visible.map((s, i) => {
              const accent = accentOf(s.category);
              const active = s.id === selected.id;
              return (
                <li key={s.id} className="relative">
                  <button
                    type="button"
                    onClick={() => setSelectedId(s.id)}
                    aria-current={active}
                    className={cn(
                      "w-full h-full text-left rounded-lg p-4 border transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                      active
                        ? "bg-background-tertiary"
                        : "bg-background-secondary border-border hover:bg-background-tertiary/60 hover:-translate-y-0.5",
                    )}
                    style={active ? { borderColor: accent } : undefined}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span
                        className="font-mono text-[11px] tracking-[0.14em]"
                        style={{ color: accent }}
                      >
                        {s.num}
                      </span>
                      <span className="font-mono text-[9px] tracking-[0.14em] uppercase text-foreground-tertiary">
                        {labelOf(s.category)}
                      </span>
                    </div>
                    <div className="text-sm font-medium text-foreground mb-1.5">{s.title}</div>
                    <p className="text-xs text-foreground-secondary line-clamp-3">{s.summary}</p>
                    <div
                      className="mt-3 h-px w-full"
                      style={{ background: `linear-gradient(90deg, ${accent}, transparent)` }}
                    />
                  </button>
                  {i < visible.length - 1 && (
                    <ArrowRight
                      aria-hidden
                      className="hidden xl:block absolute -right-2.5 top-1/2 -translate-y-1/2 w-3 h-3 text-foreground-tertiary/50"
                    />
                  )}
                </li>
              );
            })}
          </ul>
        </div>

        {/* Drill-down */}
        <aside className="lg:sticky lg:top-6">
          <div
            className="bg-background-secondary border rounded-lg p-5"
            style={{ borderColor: accentOf(selected.category) }}
            aria-live="polite"
          >
            <div className="flex items-center gap-2 mb-1">
              <span
                className="font-mono text-xs tracking-[0.16em]"
                style={{ color: accentOf(selected.category) }}
              >
                STAGE {selected.num}
              </span>
              <span className="font-mono text-[9px] tracking-[0.14em] uppercase text-foreground-tertiary">
                {labelOf(selected.category)}
              </span>
            </div>
            <h2 className="font-display text-2xl text-foreground mb-2">{selected.title}</h2>
            <p className="text-sm text-foreground-secondary mb-5">{selected.summary}</p>

            <div className="font-mono text-[10px] tracking-[0.2em] uppercase text-foreground-tertiary mb-2">
              Subprocess checklist
            </div>
            <ul className="space-y-1.5 mb-5">
              {selected.subprocess.map((step) => (
                <li key={step} className="flex gap-2 text-xs text-foreground-secondary">
                  <CheckCircle2
                    className="w-3.5 h-3.5 mt-0.5 shrink-0"
                    style={{ color: accentOf(selected.category) }}
                  />
                  <span>{step}</span>
                </li>
              ))}
            </ul>

            <div className="font-mono text-[10px] tracking-[0.2em] uppercase text-foreground-tertiary mb-2">
              Quality gates
            </div>
            <div className="flex flex-wrap gap-1.5 mb-5">
              {selected.gates.map((g) => (
                <span
                  key={g}
                  className="text-[11px] px-2 py-1 rounded-md border border-border bg-background-tertiary text-foreground-secondary"
                >
                  {g}
                </span>
              ))}
            </div>

            <div className="font-mono text-[10px] tracking-[0.2em] uppercase text-foreground-tertiary mb-2">
              KPIs
            </div>
            <div className="grid gap-2 sm:grid-cols-3">
              {selected.kpis.map((k) => (
                <div
                  key={k.label}
                  className="bg-background-tertiary border border-border rounded-md p-3"
                >
                  <div className="text-xs text-foreground font-medium mb-1">{k.label}</div>
                  <div className="text-[11px] text-foreground-tertiary leading-snug">{k.hint}</div>
                </div>
              ))}
            </div>
          </div>
        </aside>
      </div>

      {/* Feedback loops */}
      <section className="mt-12">
        <h2 className="font-display text-2xl text-foreground mb-1">Feedback loops</h2>
        <p className="text-sm text-foreground-secondary mb-5 max-w-3xl">
          The system is not a funnel, it is a circuit. Sales outcomes travel back upstream and rewrite
          ICP, source selection, offer, personalization, messaging and infrastructure decisions.
          Optimization is driven by downstream revenue truth — never by vanity opens.
        </p>
        <div className="grid gap-3 lg:grid-cols-2">
          {FEEDBACK_LOOPS.map((l) => (
            <div key={l.from} className="bg-background-secondary border border-border rounded-lg p-4">
              <div className="flex flex-wrap items-center gap-2 mb-2">
                <span className="text-xs text-foreground font-medium">{l.from}</span>
                <ArrowRight aria-hidden className="w-3.5 h-3.5 text-cyan shrink-0" />
                <span className="text-xs text-cyan">{l.to}</span>
              </div>
              <p className="text-xs text-foreground-secondary mb-3">{l.detail}</p>
              <div className="flex flex-wrap gap-1.5">
                {l.targets.map((num) => {
                  const st = STAGES.find((s) => s.num === num)!;
                  return (
                    <button
                      key={num}
                      type="button"
                      onClick={() => {
                        setFilter("all");
                        setSelectedId(st.id);
                      }}
                      className="font-mono text-[10px] px-2 py-1 rounded border border-border text-foreground-tertiary hover:text-foreground hover:border-border-emphasized transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    >
                      {num} {st.title}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Gates + KPI overview */}
      <section className="mt-12 grid gap-6 lg:grid-cols-2">
        <div>
          <h2 className="font-display text-xl text-foreground mb-3">Quality-gate overview</h2>
          <div className="bg-background-secondary border border-border rounded-lg divide-y divide-border">
            {STAGES.map((s) => (
              <div key={s.id} className="p-3 flex gap-3">
                <span className="font-mono text-[11px] text-foreground-tertiary w-6 shrink-0 pt-0.5">
                  {s.num}
                </span>
                <div className="min-w-0">
                  <div className="text-xs text-foreground mb-1">{s.title}</div>
                  <div className="text-[11px] text-foreground-secondary">
                    {s.gates.join(" · ")}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div>
          <h2 className="font-display text-xl text-foreground mb-3">KPI legend</h2>
          <div className="bg-background-secondary border border-border rounded-lg divide-y divide-border">
            {CATEGORIES.map((c) => (
              <div key={c.id} className="p-3">
                <div
                  className="font-mono text-[10px] tracking-[0.18em] uppercase mb-2"
                  style={{ color: `hsl(var(${c.token}))` }}
                >
                  {c.label}
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {STAGES.filter((s) => s.category === c.id)
                    .flatMap((s) => s.kpis.map((k) => k.label))
                    .map((label, i) => (
                      <span
                        key={`${label}-${i}`}
                        className="text-[11px] px-2 py-1 rounded-md bg-background-tertiary border border-border text-foreground-secondary"
                      >
                        {label}
                      </span>
                    ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default ColdEmailAugust2026Page;
