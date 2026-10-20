import { useState, useEffect, useCallback } from "react";
import { supabase } from "@/integrations/supabase/client";

const POLL_INTERVAL = 5 * 60 * 1000; // 5 minutes

const MOCK_DATA = {
  today: { leadsScraped: 347, emailsSent: 212, opens: 89, replies: 7, positiveReplies: 4 },
  health: { bounceRate: 1.8, spamRate: 0.04, openRate: 42 },
  month: { totalEmails: 6420, callsBooked: 14, revenuePipeline: 140000, cost: 149, costPerBookedCall: 10.64 },
  alerts: [
    { type: "warning", text: "Domain growthsync.co approaching 30-day rotation threshold" },
    { type: "info", text: "Campaign 'Med Spa V2' paused — reply rate below 0.5%" },
  ],
};

export interface PipelineMetrics {
  today: { leadsScraped: number; emailsSent: number; opens: number; replies: number; positiveReplies: number };
  health: { bounceRate: number; spamRate: number; openRate: number };
  month: { totalEmails: number; callsBooked: number; revenuePipeline: number; cost: number; costPerBookedCall: number };
  alerts: { type: string; text: string }[];
}

interface UsePipelineMetricsReturn {
  data: PipelineMetrics;
  isLoading: boolean;
  errors: string[];
  lastUpdated: Date | null;
  isLive: boolean;
  refresh: () => void;
}

export function usePipelineMetrics(): UsePipelineMetricsReturn {
  const [data, setData] = useState<PipelineMetrics>(MOCK_DATA);
  const [isLoading, setIsLoading] = useState(true);
  const [errors, setErrors] = useState<string[]>([]);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [isLive, setIsLive] = useState(false);

  const fetchMetrics = useCallback(async () => {
    setIsLoading(true);
    const newErrors: string[] = [];

    try {
      const { data: result, error } = await supabase.functions.invoke("pipeline-metrics");

      if (error) {
        newErrors.push(`Edge function error: ${error.message}`);
        setErrors(newErrors);
        setIsLoading(false);
        return; // keep existing data as fallback
      }

      const smartlead = result?.smartlead;
      const ghl = result?.ghl;
      const apify = result?.apify;

      // Collect per-source errors
      if (smartlead?.error) newErrors.push(smartlead.error);
      if (ghl?.error) newErrors.push(ghl.error);
      if (apify?.error) newErrors.push(apify.error);
      if (result?.configErrors) newErrors.push(...result.configErrors);

      // Build merged data — use live values where available, mock as fallback
      const hasSmartlead = smartlead && !smartlead.error;
      const hasGHL = ghl && !ghl.error;
      const hasApify = apify && !apify.error;

      const totalSent = hasSmartlead ? smartlead.emailsSent : MOCK_DATA.today.emailsSent;
      const monthCallsBooked = hasGHL ? ghl.callsBooked : MOCK_DATA.month.callsBooked;

      const merged: PipelineMetrics = {
        today: {
          leadsScraped: hasApify ? apify.leadsScraped : MOCK_DATA.today.leadsScraped,
          emailsSent: totalSent,
          opens: hasSmartlead ? smartlead.opens : MOCK_DATA.today.opens,
          replies: hasSmartlead ? smartlead.replies : MOCK_DATA.today.replies,
          positiveReplies: hasSmartlead ? smartlead.positiveReplies : MOCK_DATA.today.positiveReplies,
        },
        health: {
          bounceRate: hasSmartlead ? smartlead.bounceRate : MOCK_DATA.health.bounceRate,
          spamRate: MOCK_DATA.health.spamRate, // Not directly from Smartlead
          openRate: hasSmartlead ? smartlead.openRate : MOCK_DATA.health.openRate,
        },
        month: {
          totalEmails: totalSent,
          callsBooked: monthCallsBooked,
          revenuePipeline: hasGHL ? ghl.revenue : MOCK_DATA.month.revenuePipeline,
          cost: MOCK_DATA.month.cost, // Manual tracking
          costPerBookedCall: monthCallsBooked > 0 ? Math.round((MOCK_DATA.month.cost / monthCallsBooked) * 100) / 100 : MOCK_DATA.month.costPerBookedCall,
        },
        alerts: [
          ...(hasSmartlead && smartlead.alerts ? smartlead.alerts : []),
          ...(newErrors.length === 0 ? [] : [{ type: "warning" as const, text: `${newErrors.length} API source(s) returned errors` }]),
          ...(hasApify && apify.lastRunStatus !== "SUCCEEDED" ? [{ type: "warning", text: `Last Apify run status: ${apify.lastRunStatus}` }] : []),
        ],
      };

      // If at least one source returned real data, mark as live
      if (hasSmartlead || hasGHL || hasApify) {
        setIsLive(true);
      }

      // Only update data if we got at least something
      if (hasSmartlead || hasGHL || hasApify) {
        setData(merged);
      }

      setLastUpdated(new Date());
    } catch (e) {
      newErrors.push(e instanceof Error ? e.message : "Unknown fetch error");
    }

    setErrors(newErrors);
    setIsLoading(false);
  }, []);

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, POLL_INTERVAL);
    return () => clearInterval(interval);
  }, [fetchMetrics]);

  return { data, isLoading, errors, lastUpdated, isLive, refresh: fetchMetrics };
}
