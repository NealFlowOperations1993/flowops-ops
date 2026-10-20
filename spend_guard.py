"""
Universal $50/day spend cap enforcement.

Usage at the top of any cost-incurring script:

    from spend_guard import check_spend_or_die
    check_spend_or_die(estimated_cost_usd=5.00)  # blocks if today's total + this would exceed $50

Posts a RED ALERT to Slack DM (Neal) when:
  - Total daily spend approaching $40 (warning at 80%)
  - Total daily spend approaching $50 (red alert at 100%)
  - Any single script tries to spend that would push past $50

Source of truth for daily spend:
  - OpenRouter today's usage (live)
  - Apify today's usage (live, derived from monthlyUsage / days elapsed)
  - Smartlead amortized ($97/mo / 30 = $3.23/day)
  - n8n amortized ($20/mo / 30 = $0.67/day)
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

DAILY_CAP_USD = 50.0
WARNING_THRESHOLD_USD = 40.0   # 80% of cap

OR_KEY = os.environ["OPENROUTER_API_KEY"]
APIFY_TOKEN = os.environ["APIFY_TOKEN"]

SMARTLEAD_DAILY = 97.0 / 30   # ~$3.23
N8N_DAILY = 20.0 / 30          # ~$0.67


def get_openrouter_today() -> float:
    try:
        r = urllib.request.Request("https://openrouter.ai/api/v1/auth/key",
            headers={"Authorization": f"Bearer {OR_KEY}"})
        d = json.loads(urllib.request.urlopen(r, timeout=10).read()).get("data", {})
        return float(d.get("usage_daily", 0))
    except Exception:
        return 0.0


def get_apify_daily_burn() -> float:
    """Apify reports monthly usage. Estimate today's burn = monthly / days elapsed."""
    try:
        r = urllib.request.Request(
            f"https://api.apify.com/v2/users/me/limits?token={APIFY_TOKEN}",
            headers={"User-Agent": "Mozilla/5.0"})
        d = json.loads(urllib.request.urlopen(r, timeout=10).read()).get("data", {})
        usage = d.get("current", {}).get("monthlyUsageUsd", 0)
        cycle = d.get("monthlyUsageCycle", {})
        start = cycle.get("startAt", "")
        if not start: return 0.0
        s = datetime.fromisoformat(start.replace("Z", "+00:00"))
        days = max(1, (datetime.now(timezone.utc) - s).days)
        return float(usage) / days
    except Exception:
        return 0.0


def get_today_total() -> dict:
    or_today = get_openrouter_today()
    apify_today = get_apify_daily_burn()
    total = or_today + apify_today + SMARTLEAD_DAILY + N8N_DAILY
    return {
        "openrouter": or_today,
        "apify":      apify_today,
        "smartlead":  SMARTLEAD_DAILY,
        "n8n":        N8N_DAILY,
        "total":      total,
        "cap":        DAILY_CAP_USD,
        "headroom":   DAILY_CAP_USD - total,
    }


def slack_red_alert(message: str):
    """Post red alert to Neal DM. Best effort — don't block on failure."""
    SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
    if not SLACK_BOT_TOKEN:
        return  # silent fail
    try:
        body = json.dumps({
            "channel": "U0AFMPD5CPM",   # Neal DM
            "text": f"🚨 *SPEND ALERT* 🚨\n{message}",
        }).encode()
        req = urllib.request.Request(
            "https://slack.com/api/chat.postMessage",
            data=body,
            headers={
                "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        urllib.request.urlopen(req, timeout=8).read()
    except Exception:
        pass


def check_spend_or_die(estimated_cost_usd: float = 0.0, script_name: str = ""):
    """
    Block execution if today's total + estimated_cost would exceed $50/day cap.
    Send Slack red alert if blocked.
    """
    spend = get_today_total()
    projected = spend["total"] + estimated_cost_usd
    name = script_name or sys.argv[0]

    print(f"[SPEND GUARD] today: ${spend['total']:.2f} | this run: ${estimated_cost_usd:.2f} | projected: ${projected:.2f} | cap: ${DAILY_CAP_USD}")

    if projected > DAILY_CAP_USD:
        msg = (f"BLOCKED `{name}` — would push spend over the $50/day cap.\n"
               f"Today so far: ${spend['total']:.2f}\n"
               f"This script estimated: ${estimated_cost_usd:.2f}\n"
               f"Projected total: ${projected:.2f}\n"
               f"Headroom: ${spend['headroom']:.2f}")
        print(f"\n🚨 {msg}\n")
        slack_red_alert(msg)
        sys.exit(1)

    if projected > WARNING_THRESHOLD_USD:
        msg = (f"⚠️ `{name}` will push today's spend to ${projected:.2f} (warning >${WARNING_THRESHOLD_USD}).")
        print(f"\n{msg}\n")
        slack_red_alert(msg)


if __name__ == "__main__":
    s = get_today_total()
    print(json.dumps(s, indent=2))
