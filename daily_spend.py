#!/usr/bin/env python3
"""
Pulls daily/monthly spend across all API providers.
Output formatted for the daily digest.

Sources:
  - OpenRouter: /auth/key endpoint returns usage totals
  - Anthropic: messages API doesn't expose usage, but we can estimate from local logs
  - Apify: /v2/users/me endpoint
  - Smartlead: subscription (flat, not API-tracked)
  - Supabase: hard to track per-day, approximate from row counts
"""
import argparse
import json
import os
import urllib.request

OR_KEY = os.environ["OPENROUTER_API_KEY"]
APIFY_TOK = os.environ["APIFY_TOKEN"]


def openrouter_spend() -> dict:
    """Pull cumulative + period spend from OpenRouter."""
    r = urllib.request.Request("https://openrouter.ai/api/v1/auth/key",
                               headers={"Authorization": f"Bearer {OR_KEY}"})
    try:
        with urllib.request.urlopen(r, timeout=15) as resp:
            d = json.loads(resp.read().decode()).get("data", {})
        return {
            "total_usage":   round(d.get("usage", 0), 2),
            "usage_today":   round(d.get("usage_daily", 0), 2),
            "usage_weekly":  round(d.get("usage_weekly", 0), 2),
            "usage_monthly": round(d.get("usage_monthly", 0), 2),
            "credit_limit":  d.get("limit"),
        }
    except Exception as e:
        return {"error": str(e)}


def apify_spend() -> dict:
    """Pull Apify usage."""
    r = urllib.request.Request(f"https://api.apify.com/v2/users/me?token={APIFY_TOK}")
    try:
        with urllib.request.urlopen(r, timeout=15) as resp:
            d = json.loads(resp.read().decode()).get("data", {})
        usage = d.get("monthlyUsage", {}) or d.get("usageCycle", {})
        plan = d.get("plan", {})
        return {
            "plan":            plan.get("id", "?"),
            "monthly_usage":   round(float(usage.get("platformUsageUsd", 0)), 2),
            "monthly_limit":   d.get("limits", {}).get("monthlyServiceUsageUsd"),
        }
    except Exception as e:
        return {"error": str(e)}


def anthropic_spend() -> dict:
    """Anthropic doesn't expose usage via API. Estimate from local config or skip."""
    # If we want real tracking, we'd need to instrument every API call locally
    # For now, report "manual review required"
    return {"note": "Anthropic doesn't expose usage via API; check console.anthropic.com manually"}


def smartlead_spend() -> dict:
    """Smartlead subscription is flat — no per-action tracking via API."""
    return {"note": "Smartlead subscription is flat-rate (no per-action cost)"}


def render(spend: dict) -> str:
    lines = []
    lines.append("=" * 65)
    lines.append("DAILY SPEND REPORT")
    lines.append("=" * 65)
    lines.append("")
    o = spend["openrouter"]
    if "error" not in o:
        lines.append(f"OPENROUTER (Council + signals + auto-reply):")
        lines.append(f"  Today:     ${o['usage_today']}")
        lines.append(f"  This week: ${o['usage_weekly']}")
        lines.append(f"  Monthly:   ${o['usage_monthly']}")
        lines.append(f"  Total ever: ${o['total_usage']}")
    else:
        lines.append(f"OPENROUTER: error — {o['error']}")
    lines.append("")
    a = spend["apify"]
    if "error" not in a:
        lines.append(f"APIFY (lead scraping):")
        lines.append(f"  Plan:           {a['plan']}")
        lines.append(f"  Monthly usage:  ${a['monthly_usage']}")
        lines.append(f"  Monthly limit:  ${a.get('monthly_limit', 'unlimited')}")
    else:
        lines.append(f"APIFY: error — {a['error']}")
    lines.append("")
    lines.append(f"ANTHROPIC: {spend['anthropic'].get('note','')}")
    lines.append(f"SMARTLEAD: {spend['smartlead'].get('note','')}")
    lines.append("")

    total_today_api = o.get("usage_today", 0)
    lines.append(f"TODAY'S API SPEND TOTAL (OpenRouter): ${total_today_api}")
    lines.append("MONTHLY API SPEND ALL-IN: ${:.2f} (OpenRouter) + ${:.2f} (Apify) = ${:.2f}".format(
        o.get("usage_monthly", 0), a.get("monthly_usage", 0),
        o.get("usage_monthly", 0) + a.get("monthly_usage", 0)
    ))
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    spend = {
        "openrouter": openrouter_spend(),
        "apify":      apify_spend(),
        "anthropic":  anthropic_spend(),
        "smartlead":  smartlead_spend(),
    }

    if args.json:
        print(json.dumps(spend, indent=2))
    else:
        print(render(spend))


if __name__ == "__main__":
    main()
