#!/usr/bin/env python3
"""
Daily metrics digest. Pulls 24h numbers across all campaigns and writes a
clean status report. Run at 7am via cron / launchd or Slack /command.

Usage:
  python3 daily_digest.py                  # print to stdout
  python3 daily_digest.py --slack          # also post to Slack via BRUTUS_BOT_TOKEN
  python3 daily_digest.py --json           # machine-readable output

Schedule via macOS launchd (one-time setup by Neal):
  # ~/Library/LaunchAgents/com.flowops.daily-digest.plist
  # Wake at 7am every day, run this script
"""
import argparse
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

API_KEY = os.environ["SMARTLEAD_API_KEY"]
BASE = "https://server.smartlead.ai/api/v1"
UA = "Mozilla/5.0"

# Correct campaign-ID map (re-verified 2026-05-11)
CIDS = {
    "MCA":          3263732,
    "WEALTH":       3263730,
    "COMMLOAN":     3263731,
    "FINANCIAL":    3191292,
    "MORTGAGE":     3191290,
    "INSURANCE":    3191291,
    "RECRUITER":    3191293,
    "AGENCY":       3191288,
    "COACH_FIT":    3191285,
    "TAX_RES":      3292969,
    "IT_MSP":       3292970,
}


def _get(path: str) -> dict | list:
    url = f"{BASE}{path}?api_key={API_KEY}"
    r = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(r, timeout=30) as resp:
        return json.loads(resp.read().decode())


def _to_int(v) -> int:
    try:
        return int(v) if v not in (None, "") else 0
    except Exception:
        return 0


def collect_metrics() -> dict:
    """Pull per-campaign analytics + aggregate."""
    rows = []
    totals = {"sends": 0, "opens": 0, "replies": 0, "bounces": 0}
    for niche, cid in CIDS.items():
        try:
            a = _get(f"/campaigns/{cid}/analytics")
        except Exception as e:
            rows.append({"niche": niche, "cid": cid, "err": str(e)})
            continue
        s = _to_int(a.get("sent_count"))
        o = _to_int(a.get("unique_open_count"))
        r = _to_int(a.get("reply_count"))
        b = _to_int(a.get("bounce_count"))
        rows.append({
            "niche":   niche,
            "cid":     cid,
            "status":  a.get("status", "?"),
            "sends":   s,
            "opens":   o,
            "replies": r,
            "bounces": b,
            "open_rate":   round(o / s * 100, 1) if s else 0,
            "reply_rate":  round(r / s * 100, 2) if s else 0,
            "bounce_rate": round(b / s * 100, 2) if s else 0,
        })
        totals["sends"]   += s
        totals["opens"]   += o
        totals["replies"] += r
        totals["bounces"] += b

    totals["open_rate"]   = round(totals["opens"]   / totals["sends"] * 100, 1) if totals["sends"] else 0
    totals["reply_rate"]  = round(totals["replies"] / totals["sends"] * 100, 2) if totals["sends"] else 0
    totals["bounce_rate"] = round(totals["bounces"] / totals["sends"] * 100, 2) if totals["sends"] else 0

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "campaigns":    rows,
        "totals":       totals,
    }


def render_text(metrics: dict) -> str:
    rows = metrics["campaigns"]
    t    = metrics["totals"]

    # Sort: ACTIVE first, then by replies desc, then by sends desc
    def sort_key(row):
        return (
            0 if row.get("status") == "ACTIVE" else 1,
            -row.get("replies", 0),
            -row.get("sends", 0),
        )
    rows = sorted([r for r in rows if not r.get("err")], key=sort_key)

    lines = []
    lines.append("=" * 70)
    lines.append(f"DAILY DIGEST  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"{'NICHE':<13}{'STAT':<10}{'SENDS':>7}{'OPN%':>7}{'REP':>5}{'REP%':>7}{'BNC%':>7}")
    lines.append("-" * 70)
    for r in rows:
        lines.append(f"{r['niche']:<13}{r['status'][:9]:<10}{r['sends']:>7}"
                     f"{r['open_rate']:>6.1f}%{r['replies']:>5}"
                     f"{r['reply_rate']:>6.2f}%{r['bounce_rate']:>6.2f}%")
    lines.append("-" * 70)
    lines.append(f"{'TOTAL':<13}{'':<10}{t['sends']:>7}"
                 f"{t['open_rate']:>6.1f}%{t['replies']:>5}"
                 f"{t['reply_rate']:>6.2f}%{t['bounce_rate']:>6.2f}%")
    lines.append("")

    # Health flags
    lines.append("HEALTH FLAGS:")
    flagged = False
    for r in rows:
        if r["sends"] < 5:
            continue
        if r["bounce_rate"] > 5.0:
            lines.append(f"  RED   {r['niche']} bounce rate {r['bounce_rate']}% — list quality issue, pause + rebuild")
            flagged = True
        if r["open_rate"] < 25.0 and r["sends"] >= 30:
            lines.append(f"  YEL   {r['niche']} open rate {r['open_rate']}% — subject lines need swap")
            flagged = True
        if r["status"] == "ACTIVE" and r["sends"] == 0:
            lines.append(f"  YEL   {r['niche']} ACTIVE but 0 sends — leads + sequence loaded?")
            flagged = True
    if not flagged:
        lines.append("  none — all campaigns within thresholds.")
    lines.append("")

    # Goal math
    target_calls = 3
    expected_calls = round(t["sends"] * t["reply_rate"] / 100 * 0.40 * 0.65, 2)
    lines.append(f"GOAL: {target_calls} booked calls/day")
    lines.append(f"  Current trajectory at {t['sends']} sends and {t['reply_rate']}% reply:")
    lines.append(f"  expected booked = {expected_calls}/day  ({'ON TRACK' if expected_calls >= target_calls else 'GAP'})")
    lines.append("")
    return "\n".join(lines)


def post_slack(text: str) -> bool:
    """Push the digest to Slack (#1-new-lead) via Brutus token."""
    import os
    token = os.environ.get("BRUTUS_BOT_TOKEN", "")
    channel = os.environ.get("SLACK_REPLY_CHANNEL", "#1-new-lead")
    if not token:
        print("[slack-skip] no BRUTUS_BOT_TOKEN")
        return False
    body = json.dumps({
        "channel": channel,
        "text":    f"```\n{text}\n```",
        "unfurl_links": False,
    }).encode()
    req = urllib.request.Request(
        "https://slack.com/api/chat.postMessage",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type":  "application/json; charset=utf-8",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            resp = json.loads(r.read().decode())
            return bool(resp.get("ok"))
    except Exception as e:
        print(f"[slack-error] {e}")
        return False


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--slack", action="store_true", help="also post to Slack")
    p.add_argument("--json", action="store_true", help="print JSON only")
    args = p.parse_args()

    metrics = collect_metrics()

    if args.json:
        print(json.dumps(metrics, indent=2))
        return

    text = render_text(metrics)
    print(text)

    if args.slack:
        ok = post_slack(text)
        print(f"\n[slack] posted: {ok}")


if __name__ == "__main__":
    main()
