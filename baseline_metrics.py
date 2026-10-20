#!/usr/bin/env python3
"""
Nightly baseline metrics evaluator.

Runs against each active campaign on a 7-day rolling window. If any metric
below threshold, flags for auto-iteration.

Usage:
  python3 baseline_metrics.py              # human report
  python3 baseline_metrics.py --json       # machine output for digest
  python3 baseline_metrics.py --trigger    # also fire auto-iteration on failed niches
"""
import argparse
import json
import urllib.request
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import os

KEY = os.environ["SMARTLEAD_API_KEY"]
BASE = "https://server.smartlead.ai/api/v1"
UA = "Mozilla/5.0"

# Thresholds (per Neal's spec)
THRESHOLDS = {
    "min_open_rate":      25.0,   # %
    "min_reply_rate":     0.8,    # %
    "min_positive_pct":   30.0,   # % of replies (we'll proxy via reply count for now)
    "min_booked_ratio":   1/400,  # 1 call per 400 sent
    "max_bounce_rate":    5.0,    # %
    "min_sends_to_eval":  100,    # don't evaluate until at least 100 sends
}

CAMPAIGNS = {
    "MCA":       3263732,
    "WEALTH":    3263730,
    "COMMLOAN":  3263731,
    "FINANCIAL": 3191292,
    "MORTGAGE":  3191290,
    "INSURANCE": 3191291,
    "AGENCY":    3191288,
    "RECRUITER": 3191293,
    "TAX_RES":   3292969,
    "IT_MSP":    3292970,
}


def G(p):
    sep = "&" if "?" in p else "?"
    r = urllib.request.Request(f"{BASE}{p}{sep}api_key={KEY}", headers={"User-Agent": UA})
    with urllib.request.urlopen(r, timeout=30) as resp:
        return json.loads(resp.read().decode())


def evaluate_niche(niche: str, cid: int, window_days: int = 7) -> dict:
    """Pull 7d window stats per niche."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)
    stats = {"sent": 0, "open": 0, "reply": 0, "bnc": 0, "click": 0}

    offset = 0
    while True:
        try:
            d = G(f"/campaigns/{cid}/statistics?limit=500&offset={offset}")
            rows = d.get("data", [])
        except Exception:
            break
        if not rows:
            break
        for r in rows:
            st = r.get("sent_time", "")
            if not st:
                continue
            try:
                dt = datetime.fromisoformat(st.replace("Z", "+00:00"))
                if dt < cutoff:
                    continue
            except Exception:
                continue
            stats["sent"] += 1
            if r.get("open_time"):
                stats["open"] += 1
            if r.get("reply_time"):
                stats["reply"] += 1
            if r.get("is_bounced") or r.get("bounce_time"):
                stats["bnc"] += 1
            if r.get("click_time"):
                stats["click"] += 1
        if len(rows) < 500:
            break
        offset += 500

    s = stats["sent"]
    open_rate = stats["open"] / s * 100 if s else 0
    reply_rate = stats["reply"] / s * 100 if s else 0
    bnc_rate = stats["bnc"] / s * 100 if s else 0
    click_rate = stats["click"] / s * 100 if s else 0

    # Compute health flags
    flags = []
    iteration_actions = []
    if s < THRESHOLDS["min_sends_to_eval"]:
        flags.append(f"INSUFFICIENT_DATA ({s} sends, need {THRESHOLDS['min_sends_to_eval']})")
    else:
        if open_rate < THRESHOLDS["min_open_rate"]:
            flags.append(f"LOW_OPEN_RATE ({open_rate:.1f}% < {THRESHOLDS['min_open_rate']}%)")
            iteration_actions.append("rewrite_subject_lines")
        if reply_rate < THRESHOLDS["min_reply_rate"]:
            flags.append(f"LOW_REPLY_RATE ({reply_rate:.2f}% < {THRESHOLDS['min_reply_rate']}%)")
            iteration_actions.append("regenerate_council_with_new_magnet_angle")
        if bnc_rate > THRESHOLDS["max_bounce_rate"]:
            flags.append(f"HIGH_BOUNCE_RATE ({bnc_rate:.1f}% > {THRESHOLDS['max_bounce_rate']}%)")
            iteration_actions.append("pause_and_reverify_list")

    return {
        "niche": niche,
        "campaign_id": cid,
        "window_days": window_days,
        "stats": stats,
        "open_rate":   round(open_rate, 1),
        "reply_rate":  round(reply_rate, 2),
        "click_rate":  round(click_rate, 2),
        "bounce_rate": round(bnc_rate, 2),
        "flags": flags,
        "iteration_actions": iteration_actions,
        "verdict": "ITERATE" if iteration_actions else ("INSUFFICIENT_DATA" if flags else "HEALTHY"),
    }


def render_text(results: list[dict]) -> str:
    lines = []
    lines.append("=" * 80)
    lines.append(f"BASELINE METRICS — 7-day rolling | Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"{'NICHE':<11}{'SENT':>6}{'OPEN%':>7}{'REPLY%':>8}{'CLICK%':>8}{'BNC%':>7}  VERDICT")
    lines.append("-" * 80)
    for r in results:
        s = r["stats"]
        verdict_icon = {"HEALTHY": "✓ HEALTHY", "ITERATE": "⚠ ITERATE", "INSUFFICIENT_DATA": "— wait"}.get(r["verdict"], "?")
        lines.append(f"{r['niche']:<11}{s['sent']:>6}{r['open_rate']:>6.1f}%{r['reply_rate']:>7.2f}%{r['click_rate']:>7.2f}%{r['bounce_rate']:>6.2f}%  {verdict_icon}")
    lines.append("")

    iterates = [r for r in results if r["verdict"] == "ITERATE"]
    if iterates:
        lines.append("ITERATIONS RECOMMENDED:")
        for r in iterates:
            lines.append(f"  • {r['niche']}: {', '.join(r['iteration_actions'])}")
            for f in r["flags"]:
                lines.append(f"      - {f}")
        lines.append("")
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    p.add_argument("--trigger", action="store_true", help="auto-trigger iterations on failed niches")
    p.add_argument("--window", type=int, default=7, help="rolling window in days")
    args = p.parse_args()

    results = []
    for niche, cid in CAMPAIGNS.items():
        results.append(evaluate_niche(niche, cid, window_days=args.window))

    if args.json:
        print(json.dumps(results, indent=2))
        return

    print(render_text(results))

    if args.trigger:
        for r in results:
            if r["verdict"] == "ITERATE":
                print(f"\n[TRIGGER] {r['niche']}: would auto-run {', '.join(r['iteration_actions'])}")
                # auto_iterate.py would be invoked here per action
                # not running automatically tonight — write that next


if __name__ == "__main__":
    main()
