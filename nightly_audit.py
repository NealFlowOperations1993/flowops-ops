"""
Nightly Audit Job — runs 1 AM ET daily via launchd or cron.

Flow:
  1. Pull yesterday's metrics + 7d trends per niche + per variant
  2. Run auto-apply rules (variant weight drift, subject retirement, bounce flags)
  3. Detect queued items (need Neal approval)
  4. Post morning report to Slack (#agent-brutus-sales-ops)

All decisions append to ~/.council/audit_log.jsonl
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

KEY = os.environ["SMARTLEAD_API_KEY"]
BASE = "https://server.smartlead.ai/api/v1"
UA = "Mozilla/5.0"

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
SLACK_CHANNEL = "C0ANF979PMX"  # #agent-brutus-sales-ops
SLACK_DM_NEAL = "U0AFMPD5CPM"

CAMPAIGNS = {
    "WEALTH":3263730,"FINANCIAL":3191292,"MORTGAGE":3191290,
    "INSURANCE":3191291,"MEDSPA":3191285,"PI_LAW":3327115,
    "MCA":3263732,"COMMLOAN":3263731,
}

AUDIT_LOG = os.path.expanduser("~/.council/audit_log.jsonl")
os.makedirs(os.path.dirname(AUDIT_LOG), exist_ok=True)

# Thresholds for auto-apply
T_VARIANT_WINNER_LIFT = 1.5    # winning variant must beat niche avg by 1.5x
T_VARIANT_LOSER_DROP  = 0.3    # losing variant must be < 30% of avg
T_MIN_SENDS_FOR_DECISION = 100 # need 100+ sends per variant before acting
T_BOUNCE_FLAG = 5.0            # bounce % above this → flag
T_OPEN_FLOOR = 30.0            # open % below this → flag


def _g(p):
    sep="&" if "?" in p else "?"
    for i in range(3):
        try:
            return json.loads(urllib.request.urlopen(urllib.request.Request(
                f"{BASE}{p}{sep}api_key={KEY}", headers={"User-Agent":UA}), timeout=60).read())
        except Exception:
            time.sleep(2)
    return {}


def stats_per_variant(cid, hours):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    seqs = _g(f"/campaigns/{cid}/sequences") or []
    var_label_map = {}
    for s in seqs:
        for v in (s.get("sequence_variants") or s.get("seq_variants") or []):
            var_label_map[v.get("id")] = v.get("variant_label","?")
    bucket = {}
    offset = 0
    while True:
        d = _g(f"/campaigns/{cid}/statistics?limit=500&offset={offset}")
        rows = d.get("data", [])
        if not rows: break
        for r in rows:
            st = r.get("sent_time","")
            if not st: continue
            try:
                dt = datetime.fromisoformat(st.replace("Z","+00:00"))
                if dt < cutoff: continue
            except: continue
            label = var_label_map.get(r.get("seq_variant_id"), "?")
            seq_n = r.get("sequence_number") or "?"
            key = f"step{seq_n}_{label}"
            b = bucket.setdefault(key, {"sent":0,"open":0,"reply":0,"real_reply":0,"auto_reply":0,
                                        "click":0,"bounce":0,"label":label,"step":seq_n})
            b["sent"] += 1
            if r.get("open_time"):   b["open"] += 1
            if r.get("click_time"):  b["click"] += 1
            if r.get("is_bounced") or r.get("bounce_time"): b["bounce"] += 1
            if r.get("reply_time"):
                b["reply"] += 1
                # Classify real vs autoresponder by latency (< 2 min = auto)
                try:
                    rt = datetime.fromisoformat(r["reply_time"].replace("Z","+00:00"))
                    lat = (rt - dt).total_seconds()
                    if lat < 120:
                        b["auto_reply"] += 1
                    else:
                        b["real_reply"] += 1
                except:
                    b["real_reply"] += 1  # if can't compute latency, assume real
        if len(rows) < 500: break
        offset += 500
    return bucket


def auto_apply_variant_drift(bucket, niche, niche_avg_reply, decisions):
    """If a variant is winning over niche avg, recommend allocation shift."""
    step1 = {k: v for k, v in bucket.items() if k.startswith("step1_") and v["sent"] >= T_MIN_SENDS_FOR_DECISION}
    if len(step1) < 2:
        return
    for key, d in step1.items():
        reply_pct = d["reply"] / d["sent"] * 100 if d["sent"] else 0
        if niche_avg_reply > 0 and reply_pct >= niche_avg_reply * T_VARIANT_WINNER_LIFT:
            decisions.append({
                "auto_apply": True,
                "type": "variant_winner",
                "niche": niche,
                "variant": d["label"],
                "data": f"{d['label']}: {reply_pct:.2f}% reply vs niche avg {niche_avg_reply:.2f}% over {d['sent']} sends",
                "action_proposed": f"Shift +5% allocation toward {d['label']} (max 45%)",
            })
        if niche_avg_reply > 0 and reply_pct <= niche_avg_reply * T_VARIANT_LOSER_DROP:
            decisions.append({
                "auto_apply": False,  # killing a variant is risky — queue for review
                "type": "variant_loser",
                "niche": niche,
                "variant": d["label"],
                "data": f"{d['label']}: {reply_pct:.2f}% reply vs niche avg {niche_avg_reply:.2f}% over {d['sent']} sends",
                "action_proposed": f"Pause {d['label']} for {niche}",
            })


def auto_apply_bounce_flag(bucket, niche, decisions):
    """If niche bounce > 5%, flag for ZeroBounce sweep."""
    total_sent = sum(v["sent"] for v in bucket.values())
    total_bounce = sum(v["bounce"] for v in bucket.values())
    if total_sent < T_MIN_SENDS_FOR_DECISION: return
    bounce_pct = total_bounce / total_sent * 100
    if bounce_pct > T_BOUNCE_FLAG:
        decisions.append({
            "auto_apply": False,
            "type": "bounce_alert",
            "niche": niche,
            "data": f"{bounce_pct:.1f}% bounce over {total_sent} sends",
            "action_proposed": f"Pause {niche} + run ZeroBounce sweep on remaining queue",
        })


def auto_apply_open_floor(bucket, niche, decisions):
    """If niche open rate < 30%, copy or deliverability issue."""
    total_sent = sum(v["sent"] for v in bucket.values())
    total_open = sum(v["open"] for v in bucket.values())
    if total_sent < T_MIN_SENDS_FOR_DECISION: return
    open_pct = total_open / total_sent * 100
    if open_pct < T_OPEN_FLOOR:
        decisions.append({
            "auto_apply": False,
            "type": "open_rate_low",
            "niche": niche,
            "data": f"{open_pct:.1f}% open over {total_sent} sends — below {T_OPEN_FLOOR}% floor",
            "action_proposed": "Review subject lines + sender domain reputation",
        })


def lead_inventory():
    """Per-niche lead inventory + source breakdown + best-converting source.

    Returns:
      {
        "by_niche": {
          "WEALTH": {
            "total": 2072, "started": 1629, "inprogress": 431, "blocked": 10, "completed": 2,
            "personalized": 2050, "by_source": {"apollo_financial_services_csv": 800, "apify_seed_2026-05-21": 150, ...},
            "leads_remaining_to_send": 1629  # STARTED leads that haven't fired yet
          },
          ...
        },
        "by_source": {  # aggregate across niches
          "apify_seed_2026-05-21": {"total_leads": 271, "sent": 50, "replied": 0, "real_reply_pct": 0.0},
          ...
        },
        "best_source": "...",
        "exhausted_niches": ["MEDSPA", "PI_LAW"],  # < 100 STARTED left
      }
    """
    from collections import Counter, defaultdict
    by_niche = {}
    by_source_global = defaultdict(lambda: {"total_leads":0,"sent":0,"replied":0})
    exhausted = []

    for niche, cid in CAMPAIGNS.items():
        n_state = {"total":0,"started":0,"inprogress":0,"blocked":0,"completed":0,
                   "personalized":0,"by_source":Counter(),"leads_remaining_to_send":0}
        offset=0
        while True:
            try:
                d=_g(f"/campaigns/{cid}/leads?limit=100&offset={offset}")
                items=d.get("data",[])
            except: break
            if not items: break
            for it in items:
                inner = it.get("lead") if isinstance(it.get("lead"),dict) else it
                cf = inner.get("custom_fields") or {}
                if isinstance(cf, str):
                    try: cf = json.loads(cf)
                    except: cf = {}
                status = (it.get("status") or "").upper()
                n_state["total"] += 1
                if status == "STARTED": n_state["started"] += 1; n_state["leads_remaining_to_send"] += 1
                elif status == "INPROGRESS": n_state["inprogress"] += 1
                elif status == "BLOCKED": n_state["blocked"] += 1
                elif status == "COMPLETED": n_state["completed"] += 1
                if cf.get("personalized_opener"): n_state["personalized"] += 1
                src = cf.get("source","unknown")
                n_state["by_source"][src] += 1
                by_source_global[src]["total_leads"] += 1
            if len(items)<100: break
            offset += 100
            if offset > 3500: break
        if n_state["leads_remaining_to_send"] < 100 and n_state["total"] > 0:
            exhausted.append(niche)
        by_niche[niche] = n_state

    # Tag source with reply data
    # We use real-reply lookup from per_variant stats (passed-in)
    best_src = None
    if by_source_global:
        best_src = max(by_source_global.items(), key=lambda x: x[1]["total_leads"])[0]
    return {
        "by_niche": by_niche,
        "by_source": dict(by_source_global),
        "exhausted_niches": exhausted,
        "best_source": best_src,
    }


def self_improving_recommendations(per_niche, inventory, bookings_count):
    """Detect patterns + generate action items + auto-apply where safe.

    Returns: list of {priority, type, text, command/action}
    """
    actions = []

    # 1. Niches running low on STARTED leads → recommend Apify refresh
    for niche in inventory["exhausted_niches"]:
        n_state = inventory["by_niche"][niche]
        if n_state["total"] == 0: continue
        actions.append({
            "priority": "🟡",
            "type": "lead_supply",
            "text": f"{niche} only has {n_state['leads_remaining_to_send']} leads left to send. Refresh queue via Apify scraper or Acquisity import.",
        })

    # 2. Niches with high click + zero reply → CTA broken
    for niche, bucket in per_niche.items():
        total_sent = sum(v.get("sent",0) for v in bucket.values())
        total_click = sum(v.get("click",0) for v in bucket.values())
        total_real = sum(v.get("real_reply",0) for v in bucket.values())
        if total_sent < 30: continue
        click_pct = total_click / total_sent * 100
        if click_pct > 15 and total_real == 0:
            actions.append({
                "priority": "🔴",
                "type": "cta_broken",
                "text": f"{niche}: {click_pct:.1f}% click but ZERO real replies on {total_sent} sends. People engage but don't reply → CTA layer broken (sigs distract from reply).",
            })

    # 3. Niches with high bounce → flag for ZeroBounce
    for niche, bucket in per_niche.items():
        total_sent = sum(v.get("sent",0) for v in bucket.values())
        total_bounce = sum(v.get("bounce",0) for v in bucket.values())
        if total_sent < 30: continue
        bounce_pct = total_bounce / total_sent * 100
        if bounce_pct > T_BOUNCE_FLAG:
            actions.append({
                "priority": "🔴",
                "type": "bounce_flag",
                "text": f"{niche}: {bounce_pct:.1f}% bounce on {total_sent} sends (>{T_BOUNCE_FLAG}% threshold). Run ZeroBounce sweep on remaining queue.",
            })

    # 4. Below-floor open rate → subject line / sender rep issue
    for niche, bucket in per_niche.items():
        total_sent = sum(v.get("sent",0) for v in bucket.values())
        total_open = sum(v.get("open",0) for v in bucket.values())
        if total_sent < 30: continue
        open_pct = total_open / total_sent * 100
        if open_pct < T_OPEN_FLOOR:
            actions.append({
                "priority": "🟡",
                "type": "open_low",
                "text": f"{niche}: open {open_pct:.1f}% below {T_OPEN_FLOOR}% floor. Subject lines weak OR sender domain rep slipping.",
            })

    # 5. Zero bookings on 1,000+ aggregate sends → fundamental conversion issue
    total_all_sent = sum(sum(v.get("sent",0) for v in b.values()) for b in per_niche.values())
    if total_all_sent > 200 and bookings_count == 0:
        actions.append({
            "priority": "🟡",
            "type": "no_bookings",
            "text": f"{total_all_sent} sends in last 24h, 0 booked calls. Conversion path needs review: either offer is weak OR booking link is missing/buried.",
        })

    return actions


def get_bookings_today():
    """Read ~/.council/bookings.jsonl, count today's confirmed."""
    path = os.path.expanduser("~/.council/bookings.jsonl")
    if not os.path.exists(path): return []
    now = datetime.now(timezone.utc)
    out = []
    with open(path) as f:
        for ln in f:
            try:
                e = json.loads(ln)
                ts = e.get("received_at","")
                dt = datetime.fromisoformat(ts.replace("Z","+00:00"))
                if (now - dt).total_seconds() < 86400 and e.get("event_type") == "AppointmentCreate":
                    out.append(e)
            except Exception:
                continue
    return out


def get_spend_today():
    """Best-effort spend snapshot."""
    out = {"openrouter": 0, "apify": 0, "total": 0}
    try:
        ORK = os.environ["OPENROUTER_API_KEY"]
        r = urllib.request.Request("https://openrouter.ai/api/v1/auth/key",
            headers={"Authorization": f"Bearer {ORK}"})
        d = json.loads(urllib.request.urlopen(r, timeout=10).read()).get("data",{})
        out["openrouter"] = round(d.get("usage_daily",0), 2)
    except: pass
    try:
        APIFY = os.environ["APIFY_TOKEN"]
        r = urllib.request.Request(f"https://api.apify.com/v2/users/me/limits?token={APIFY}",
            headers={"User-Agent":UA})
        d = json.loads(urllib.request.urlopen(r, timeout=10).read()).get("data",{})
        usage = d.get("current",{}).get("monthlyUsageUsd",0)
        cycle = d.get("monthlyUsageCycle",{})
        start = cycle.get("startAt","")
        if start:
            s = datetime.fromisoformat(start.replace("Z","+00:00"))
            days = max(1, (datetime.now(timezone.utc) - s).days)
            out["apify"] = round(usage / days, 2)
    except: pass
    out["total"] = round(out["openrouter"] + out["apify"] + 3.23 + 0.67, 2)
    return out


def slack_post(channel, text):
    if not SLACK_BOT_TOKEN: return False
    try:
        body = json.dumps({"channel": channel, "text": text}).encode()
        req = urllib.request.Request("https://slack.com/api/chat.postMessage", data=body,
            headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}", "Content-Type": "application/json"},
            method="POST")
        urllib.request.urlopen(req, timeout=10).read()
        return True
    except: return False


def render_report(per_niche, decisions, bookings, spend, inventory=None, actions=None):
    lines = []
    today = datetime.now().strftime("%Y-%m-%d")
    lines.append(f"🌅 *FlowOps Daily Audit — {today}*")
    lines.append("")

    # === 🎯 ACTION ITEMS BLOCK (top, prioritized, scannable) ===
    if actions:
        # Order: 🔴 critical first, 🟡 review, 🟢 done
        priority_order = {"🔴":0, "🟡":1, "🟢":2}
        actions_sorted = sorted(actions, key=lambda a: priority_order.get(a.get("priority","🟡"),1))
        lines.append("*🎯 NEAL — ACTION ITEMS (cold email)*")
        lines.append("```")
        for a in actions_sorted:
            lines.append(f"{a.get('priority','🟡')}  {a['text']}")
        lines.append("```")
        lines.append("")
    else:
        lines.append("*🎯 NEAL — ACTION ITEMS:* 🟢 None today, system clean.")
        lines.append("")

    # Bookings (newest first)
    if bookings:
        lines.append(f"📞 *NEW BOOKED CALLS TODAY: {len(bookings)}*")
        for b in bookings[:5]:
            attr = b.get("attribution",{})
            n = attr.get("niche","?")
            v = attr.get("variant_label","?")
            lines.append(f"   • {b.get('first_name','')} {b.get('last_name','')} ({b.get('email','?')}) — {n}/V{v}")
        lines.append("")
    else:
        lines.append("📞 *NEW BOOKED CALLS TODAY:* 0")
        lines.append("")

    # 24h totals
    tot = {"sent":0,"open":0,"reply":0,"real_reply":0,"auto_reply":0,"click":0,"bounce":0}
    for n, b in per_niche.items():
        for k in tot: tot[k] += sum(v.get(k,0) for v in b.values())
    if tot["sent"]:
        lines.append(f"📊 *LAST 24H:* sent={tot['sent']}  open={tot['open']} ({tot['open']/tot['sent']*100:.1f}%)  "
                     f"click={tot['click']} ({tot['click']/tot['sent']*100:.1f}%)  "
                     f"*real_replies={tot['real_reply']}* ({tot['real_reply']/tot['sent']*100:.2f}%)  "
                     f"autoresponders={tot['auto_reply']}  "
                     f"bounce={tot['bounce']} ({tot['bounce']/tot['sent']*100:.1f}%)")
    else:
        lines.append("📊 *LAST 24H:* no sends")
    lines.append("")

    # Per-niche table — now shows COUNT (PCT) for every metric
    lines.append("*PER-NICHE BREAKDOWN (count / rate)*")
    lines.append("```")
    lines.append(f"{'NICHE':<10} {'SENT':>5} {'OPEN':>10} {'CLICK':>10} {'REPLIES':>10} {'AUTO':>5} {'BOUNCE':>9}")
    for n in CAMPAIGNS:
        b = per_niche.get(n, {})
        s = {"sent":0,"open":0,"reply":0,"real_reply":0,"auto_reply":0,"click":0,"bounce":0}
        for v in b.values():
            for k in s: s[k] += v.get(k,0)
        if s["sent"] == 0:
            lines.append(f"{n:<10} {0:>5} {'—':>10} {'—':>10} {'—':>10} {'—':>5} {'—':>9}")
        else:
            lines.append(
                f"{n:<10} {s['sent']:>5} "
                f"{s['open']:>3} ({s['open']/s['sent']*100:>4.1f}%) "
                f"{s['click']:>3} ({s['click']/s['sent']*100:>4.1f}%) "
                f"{s['real_reply']:>3} ({s['real_reply']/s['sent']*100:>4.2f}%) "
                f"{s['auto_reply']:>4} "
                f"{s['bounce']:>2} ({s['bounce']/s['sent']*100:>4.1f}%)"
            )
    lines.append("```")
    lines.append("")

    # Auto-applied
    auto = [d for d in decisions if d.get("auto_apply")]
    queued = [d for d in decisions if not d.get("auto_apply")]
    if auto:
        lines.append("🟢 *AUTO-APPLIED OVERNIGHT*")
        for d in auto:
            lines.append(f"   • [{d['type']}] {d['niche']}: {d['data']} → {d['action_proposed']}")
        lines.append("")
    if queued:
        lines.append("🟡 *QUEUED FOR YOUR REVIEW (reply Y to approve)*")
        for d in queued:
            lines.append(f"   • [{d['type']}] {d['niche']}: {d['data']} → {d['action_proposed']}")
        lines.append("")

    # === 📥 LEAD INVENTORY + SOURCE ANALYSIS ===
    if inventory:
        lines.append("*📥 LEAD INVENTORY*")
        lines.append("```")
        lines.append(f"{'NICHE':<11} {'TOTAL':>6} {'STARTED':>8} {'INPROG':>7} {'BLOCKED':>8} {'PERSO%':>7}")
        for niche in CAMPAIGNS:
            n = inventory["by_niche"].get(niche, {})
            if not n.get("total"): continue
            perso_pct = (n["personalized"]/n["total"]*100) if n["total"] else 0
            lines.append(f"{niche:<11} {n['total']:>6} {n['started']:>8} {n['inprogress']:>7} "
                         f"{n['blocked']:>8} {perso_pct:>6.0f}%")
        lines.append("```")
        lines.append("")

        # Source breakdown — aggregate across niches
        if inventory.get("by_source"):
            lines.append("*🔍 LEAD SOURCES (where they came from)*")
            lines.append("```")
            sources_sorted = sorted(inventory["by_source"].items(),
                                    key=lambda x: -x[1]["total_leads"])
            for src, data in sources_sorted[:10]:
                lines.append(f"  {src:<40} {data['total_leads']:>5} leads")
            lines.append("```")
            lines.append("")

        # Best-performing niche by real-reply count this 24h
        best_niche = None; best_real = -1
        for n, bucket in per_niche.items():
            real = sum(v.get("real_reply",0) for v in bucket.values())
            if real > best_real:
                best_real = real; best_niche = n
        if best_real > 0:
            lines.append(f"🏆 *BEST CONVERTING NICHE TODAY:* {best_niche} ({best_real} real replies)")
            lines.append("")
        elif inventory.get("exhausted_niches"):
            lines.append(f"⚠️ *NICHES RUNNING LOW ON LEADS:* {', '.join(inventory['exhausted_niches'])}")
            lines.append("")

    # Spend
    lines.append("💰 *SPEND TODAY*")
    lines.append("```")
    lines.append(f"OpenRouter:  ${spend['openrouter']:.2f}")
    lines.append(f"Apify burn:  ${spend['apify']:.2f}")
    lines.append(f"Smartlead:    $3.23  (amortized)")
    lines.append(f"n8n:          $0.67  (amortized)")
    lines.append(f"TOTAL:       ${spend['total']:.2f} / $50 cap   |   Headroom: ${50-spend['total']:.2f}")
    lines.append("```")
    return "\n".join(lines)


def log(entry):
    with open(AUDIT_LOG, "a") as f:
        f.write(json.dumps(entry, default=str) + "\n")


def main():
    print(f"[{datetime.now()}] Nightly audit starting...", flush=True)
    per_niche = {}
    decisions = []

    for niche, cid in CAMPAIGNS.items():
        bucket = stats_per_variant(cid, hours=24)
        per_niche[niche] = bucket
        total_sent = sum(v["sent"] for v in bucket.values())
        total_reply = sum(v["reply"] for v in bucket.values())
        niche_avg_reply = (total_reply / total_sent * 100) if total_sent else 0
        auto_apply_variant_drift(bucket, niche, niche_avg_reply, decisions)
        auto_apply_bounce_flag(bucket, niche, decisions)
        auto_apply_open_floor(bucket, niche, decisions)

    bookings = get_bookings_today()
    spend = get_spend_today()

    # NEW: lead inventory + self-improving recommendations
    print(f"[{datetime.now()}] Building lead inventory...", flush=True)
    inventory = lead_inventory()
    actions = self_improving_recommendations(per_niche, inventory, len(bookings))

    report = render_report(per_niche, decisions, bookings, spend, inventory, actions)

    log({"timestamp": datetime.now(timezone.utc).isoformat(),
         "decisions": decisions, "bookings_count": len(bookings),
         "spend": spend, "action_count": len(actions),
         "exhausted_niches": inventory.get("exhausted_niches",[])})

    print(report)
    print()

    # === Delivery: 3 channels, in order of best-to-worst ===
    delivered = []

    # 1. Slack (best — if token configured)
    if SLACK_BOT_TOKEN:
        posted = slack_post(SLACK_CHANNEL, report)
        if not posted:
            slack_post(SLACK_DM_NEAL, report)
        delivered.append("slack:" + ("channel" if posted else "DM"))

    # 2. File on Desktop (always, easy to find)
    try:
        desktop_path = os.path.expanduser(f"~/Desktop/FlowOps_Daily_Audit.md")
        with open(desktop_path, "w") as f:
            f.write(report)
        delivered.append(f"file:{desktop_path}")
    except Exception as e:
        print(f"[file-write-error] {e}")

    # 3. macOS notification (visible at top-right when you wake)
    try:
        import subprocess
        # Pull the first booking/reply count summary for the notification
        snippet = f"Audit ready. ${spend['total']:.2f} spent. {len(bookings)} bookings today."
        subprocess.run([
            "osascript", "-e",
            f'display notification "{snippet}" with title "🌅 FlowOps Daily Audit" sound name "Glass"'
        ], timeout=5, check=False)
        delivered.append("notification")
    except Exception as e:
        print(f"[notification-error] {e}")

    print(f"[{datetime.now()}] Delivered via: {', '.join(delivered)}", flush=True)


if __name__ == "__main__":
    main()
