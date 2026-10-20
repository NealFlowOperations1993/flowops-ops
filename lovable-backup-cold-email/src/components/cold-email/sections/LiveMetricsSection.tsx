import { TridentCard } from "@/components/trident/TridentCard";
import { SectionHeader } from "../SectionHeader";
import { usePipelineMetrics } from "@/hooks/usePipelineMetrics";
import { RefreshCw, Loader2, Wifi, WifiOff } from "lucide-react";

const healthColor = (metric: string, value: number): string => {
  if (metric === "bounceRate") return value < 2 ? "hsl(var(--green))" : value < 4 ? "#F59E0B" : "hsl(var(--red))";
  if (metric === "spamRate") return value < 0.1 ? "hsl(var(--green))" : value < 0.3 ? "#F59E0B" : "hsl(var(--red))";
  if (metric === "openRate") return value > 40 ? "hsl(var(--green))" : value > 25 ? "#F59E0B" : "hsl(var(--red))";
  return "hsl(var(--foreground))";
};

export const LiveMetricsSection = () => {
  const { data: d, isLoading, errors, lastUpdated, isLive, refresh } = usePipelineMetrics();

  return (
    <div>
      <SectionHeader label="LIVE METRICS" title="Pipeline Command Center" subtitle="Pulls from Smartlead, GHL & Apify every 5 minutes." />

      {/* Status Bar */}
      <div className="flex items-center justify-between mb-4 px-1">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            {isLive ? (
              <>
                <Wifi className="w-3.5 h-3.5 text-green" />
                <span className="font-mono text-[10px] text-green">LIVE</span>
              </>
            ) : (
              <>
                <WifiOff className="w-3.5 h-3.5 text-foreground-tertiary" />
                <span className="font-mono text-[10px] text-foreground-tertiary">MOCK DATA</span>
              </>
            )}
          </div>
          {lastUpdated && (
            <span className="font-mono text-[10px] text-foreground-tertiary">
              Last updated: {lastUpdated.toLocaleTimeString()}
            </span>
          )}
        </div>
        <button
          onClick={refresh}
          disabled={isLoading}
          className="flex items-center gap-1.5 px-2.5 py-1 rounded text-[10px] font-mono text-foreground-tertiary hover:text-foreground transition-colors disabled:opacity-50"
          style={{ border: "1px solid hsl(var(--border))" }}
        >
          {isLoading ? <Loader2 className="w-3 h-3 animate-spin" /> : <RefreshCw className="w-3 h-3" />}
          REFRESH
        </button>
      </div>

      {/* Error Banner */}
      {errors.length > 0 && (
        <div className="rounded-lg px-4 py-2.5 mb-4" style={{ background: "hsl(var(--red) / 0.08)", border: "1px solid hsl(var(--red) / 0.3)" }}>
          <div className="font-mono text-[10px] text-red font-bold mb-1">API ERRORS</div>
          {errors.map((e, i) => (
            <div key={i} className="text-xs text-foreground-secondary">• {e}</div>
          ))}
        </div>
      )}

      {/* Today's Numbers */}
      <div className="font-mono text-[10px] tracking-[2px] text-foreground-tertiary mb-2">TODAY</div>
      <div className="grid grid-cols-5 gap-3 mb-5">
        {([
          ["LEADS SCRAPED", d.today.leadsScraped, "hsl(var(--blue))"],
          ["EMAILS SENT", d.today.emailsSent, "hsl(var(--cyan))"],
          ["OPENS", d.today.opens, "hsl(var(--green))"],
          ["REPLIES", d.today.replies, "hsl(var(--purple))"],
          ["POS. REPLIES", d.today.positiveReplies, "#EC4899"],
        ] as [string, number, string][]).map(([label, value, color]) => (
          <TridentCard key={label}>
            <div className="font-mono text-[9px] tracking-[2px] text-foreground-tertiary mb-1">{label}</div>
            <div className={`text-2xl font-black ${isLoading ? "animate-pulse" : ""}`} style={{ color }}>{isLoading ? "—" : value}</div>
          </TridentCard>
        ))}
      </div>

      {/* Pipeline Health */}
      <div className="font-mono text-[10px] tracking-[2px] text-foreground-tertiary mb-2">PIPELINE HEALTH</div>
      <div className="grid grid-cols-3 gap-3 mb-5">
        {([
          ["BOUNCE RATE", `${d.health.bounceRate}%`, "bounceRate", d.health.bounceRate],
          ["SPAM RATE", `${d.health.spamRate}%`, "spamRate", d.health.spamRate],
          ["OPEN RATE", `${d.health.openRate}%`, "openRate", d.health.openRate],
        ] as [string, string, string, number][]).map(([label, display, metric, value]) => {
          const color = healthColor(metric, value);
          return (
            <TridentCard key={label} accentColor={color}>
              <div className="font-mono text-[9px] tracking-[2px] text-foreground-tertiary mb-1">{label}</div>
              <div className={`text-3xl font-black ${isLoading ? "animate-pulse" : ""}`} style={{ color }}>{isLoading ? "—" : display}</div>
              <div className="mt-1 w-full h-1.5 rounded-full bg-background">
                <div className="h-full rounded-full transition-all" style={{ width: `${Math.min(value * (metric === "spamRate" ? 300 : metric === "bounceRate" ? 20 : 1), 100)}%`, background: color }} />
              </div>
            </TridentCard>
          );
        })}
      </div>

      {/* This Month */}
      <div className="font-mono text-[10px] tracking-[2px] text-foreground-tertiary mb-2">THIS MONTH</div>
      <div className="grid grid-cols-5 gap-3 mb-5">
        {([
          ["TOTAL EMAILS", d.month.totalEmails.toLocaleString(), "hsl(var(--blue))"],
          ["CALLS BOOKED", d.month.callsBooked.toString(), "hsl(var(--green))"],
          ["REVENUE PIPE", `$${(d.month.revenuePipeline / 1000).toFixed(0)}K`, "hsl(var(--green))"],
          ["TOTAL COST", `$${d.month.cost}`, "hsl(var(--amber))"],
          ["COST/CALL", `$${d.month.costPerBookedCall.toFixed(2)}`, d.month.costPerBookedCall < 15 ? "hsl(var(--green))" : "hsl(var(--amber))"],
        ] as [string, string, string][]).map(([label, value, color]) => (
          <TridentCard key={label}>
            <div className="font-mono text-[9px] tracking-[2px] text-foreground-tertiary mb-1">{label}</div>
            <div className={`text-xl font-black ${isLoading ? "animate-pulse" : ""}`} style={{ color }}>{isLoading ? "—" : value}</div>
          </TridentCard>
        ))}
      </div>

      {/* Alerts */}
      <div className="font-mono text-[10px] tracking-[2px] text-foreground-tertiary mb-2">ALERTS</div>
      <div className="flex flex-col gap-2">
        {d.alerts.length === 0 && !isLoading && (
          <div className="text-xs text-foreground-tertiary px-4 py-3 rounded-lg" style={{ background: "hsl(var(--green) / 0.06)", border: "1px solid hsl(var(--green) / 0.2)" }}>
            ✓ All systems nominal
          </div>
        )}
        {d.alerts.map((a, i) => (
          <div
            key={i}
            className="flex items-center gap-3 rounded-lg px-4 py-3"
            style={{
              background: a.type === "warning" ? "hsl(var(--amber) / 0.08)" : "hsl(var(--blue) / 0.08)",
              border: `1px solid ${a.type === "warning" ? "hsl(var(--amber) / 0.3)" : "hsl(var(--blue) / 0.3)"}`,
            }}
          >
            <span className="text-lg">{a.type === "warning" ? "⚠️" : "ℹ️"}</span>
            <span className="text-xs text-foreground-secondary">{a.text}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
