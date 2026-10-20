"""
Variant comparison: rank A/B/C/D per niche by reply rate, click rate, open rate.

Usage:
  python3 compare_variants.py              # all niches, last 7d
  python3 compare_variants.py --niche WEALTH --hours 168
  python3 compare_variants.py --json       # machine-readable for nightly_audit

Output:
  Per-niche × variant table with sent / open% / click% / reply% / verdict
  Verdict: WINNING (reply > 1.5× niche avg) / LOSING (reply < 0.5× avg) / EVEN / NEED_MORE_DATA
"""
import argparse
import json
import sys
import urllib.request
import time
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import os

KEY = os.environ["SMARTLEAD_API_KEY"]
BASE = "https://server.smartlead.ai/api/v1"
UA = "Mozilla/5.0"

CAMPAIGNS = {
    "WEALTH":3263730,"FINANCIAL":3191292,"MORTGAGE":3191290,
    "INSURANCE":3191291,"MEDSPA":3191285,"PI_LAW":3327115,
    "MCA":3263732,"COMMLOAN":3263731,
}

MIN_SENDS_FOR_VERDICT = 50  # need at least 50 sends per variant for statistical signal


def G(p):
    sep="&" if "?" in p else "?"
    for i in range(3):
        try:
            return json.loads(urllib.request.urlopen(urllib.request.Request(
                f"{BASE}{p}{sep}api_key={KEY}", headers={"User-Agent":UA}), timeout=60).read())
        except Exception:
            time.sleep(2)
    return {}


def variant_label_for(seq_variant_id, sequences):
    """Resolve seq_variant_id → 'A'/'B'/'C'/'D' by looking at the sequence definition."""
    for s in sequences:
        for v in (s.get("sequence_variants") or s.get("seq_variants") or []):
            if v.get("id") == seq_variant_id:
                return v.get("variant_label", "?")
    return "?"


def stats_by_variant(cid, hours):
    """Pull all sends within window grouped by seq_variant_id."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    sequences = G(f"/campaigns/{cid}/sequences") or []

    by_variant = defaultdict(lambda: {"sent":0,"open":0,"reply":0,"click":0,"bounce":0})
    offset = 0
    while True:
        d = G(f"/campaigns/{cid}/statistics?limit=500&offset={offset}")
        rows = d.get("data", [])
        if not rows: break
        for r in rows:
            st = r.get("sent_time","")
            if not st: continue
            try:
                dt = datetime.fromisoformat(st.replace("Z","+00:00"))
                if dt < cutoff: continue
            except: continue
            vid = r.get("seq_variant_id") or "unknown"
            label = variant_label_for(vid, sequences)
            seq_no = r.get("sequence_number") or "?"
            key = f"step{seq_no}_{label}"
            by_variant[key]["sent"] += 1
            if r.get("open_time"):   by_variant[key]["open"] += 1
            if r.get("reply_time"):  by_variant[key]["reply"] += 1
            if r.get("click_time"):  by_variant[key]["click"] += 1
            if r.get("is_bounced") or r.get("bounce_time"): by_variant[key]["bounce"] += 1
        if len(rows) < 500: break
        offset += 500
    return dict(by_variant)


def verdict_for(reply_pct, niche_avg, sent):
    if sent < MIN_SENDS_FOR_VERDICT:
        return "NEED_MORE_DATA"
    if niche_avg == 0:
        return "EVEN" if reply_pct == 0 else "WINNING"
    if reply_pct >= niche_avg * 1.5:
        return "WINNING"
    if reply_pct <= niche_avg * 0.5:
        return "LOSING"
    return "EVEN"


def analyze(hours=168, niches=None):
    target = niches or list(CAMPAIGNS.keys())
    report = {}
    for niche in target:
        cid = CAMPAIGNS[niche]
        by_var = stats_by_variant(cid, hours)
        if not by_var: continue
        # Compute niche-wide reply % for verdict baseline
        total_sent = sum(d["sent"] for d in by_var.values())
        total_reply = sum(d["reply"] for d in by_var.values())
        niche_reply_avg = (total_reply / total_sent * 100) if total_sent else 0

        variants_out = []
        for key, d in sorted(by_var.items()):
            sent = d["sent"]
            if sent == 0: continue
            reply_pct = d["reply"] / sent * 100
            variants_out.append({
                "variant":     key,
                "sent":        sent,
                "open_pct":    round(d["open"] / sent * 100, 1),
                "click_pct":   round(d["click"] / sent * 100, 1),
                "reply_pct":   round(reply_pct, 2),
                "bounce_pct":  round(d["bounce"] / sent * 100, 1),
                "verdict":     verdict_for(reply_pct, niche_reply_avg, sent),
            })
        report[niche] = {
            "window_hours":      hours,
            "niche_avg_reply":   round(niche_reply_avg, 2),
            "total_sent":        total_sent,
            "variants":          variants_out,
        }
    return report


def print_text(report):
    for niche, d in report.items():
        print(f"\n=== {niche} (last {d['window_hours']}h | total sent {d['total_sent']} | avg reply {d['niche_avg_reply']}%) ===")
        print(f"  {'VARIANT':<14} {'SENT':>5} {'OPEN%':>7} {'CLICK%':>7} {'REPLY%':>7} {'BOUNCE%':>8} {'VERDICT':<16}")
        for v in d["variants"]:
            print(f"  {v['variant']:<14} {v['sent']:>5} {v['open_pct']:>6.1f}% {v['click_pct']:>6.1f}% "
                  f"{v['reply_pct']:>6.2f}% {v['bounce_pct']:>7.1f}% {v['verdict']:<16}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--hours", type=int, default=168)
    p.add_argument("--niche", action="append", help="Filter to specific niche(s)")
    p.add_argument("--json",  action="store_true", help="JSON output")
    args = p.parse_args()

    report = analyze(hours=args.hours, niches=args.niche)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_text(report)


if __name__ == "__main__":
    main()
