#!/usr/bin/env python3
"""
FastAPI metrics server. Powers the Lovable dashboard.

Endpoints (all return JSON, CORS enabled):
  GET /                       — health check
  GET /metrics/today          — today's sends/opens/replies/clicks per niche
  GET /metrics/7d             — 7-day rolling baseline per niche + verdict
  GET /metrics/niche/{niche}  — single-niche detail
  GET /variants/performance   — A/B variant breakdown
  GET /leads/recent?limit=50  — last N replies/clicks across all campaigns
  GET /spend                  — OpenRouter + Apify usage today/week/month
  GET /campaigns              — all campaigns + lead counts

Run:
  cd ~/Desktop/council
  .venv-server/bin/uvicorn metrics_api:app --host 0.0.0.0 --port 8788

Expose via Cloudflare Tunnel or Vercel for Lovable dashboard to consume.
"""
import json
import os
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta
from collections import defaultdict

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

KEY = os.environ["SMARTLEAD_API_KEY"]
BASE = "https://server.smartlead.ai/api/v1"
UA = "Mozilla/5.0"
OR_KEY = os.environ["OPENROUTER_API_KEY"]
APIFY_TOK = os.environ["APIFY_TOKEN"]

CAMPAIGNS = {
    "MCA":       3263732,
    "WEALTH":    3263730,
    "COMMLOAN":  3263731,
    "FINANCIAL": 3191292,
    "MORTGAGE":  3191290,
    "INSURANCE": 3191291,
    "AGENCY":    3191288,
    "RECRUITER": 3191293,
    "COACH_BIZ": 3191287,
    "COACH_FIT": 3191285,
    "TAX_RES":   3292969,
    "IT_MSP":    3292970,
    "PI_LAW":    3327115,
    "MEDSPA":    3191285,
}

app = FastAPI(title="FlowOps Metrics API", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten to your Lovable origin in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def G(p):
    sep = "&" if "?" in p else "?"
    url = f"{BASE}{p}{sep}api_key={KEY}"
    r = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(r, timeout=30) as resp:
        return json.loads(resp.read().decode())


def stats_for_window(cid, hours_back):
    """Pull send stats for one campaign over a rolling window."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours_back)
    stats = {"sent": 0, "open": 0, "reply": 0, "click": 0, "bounce": 0}
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
            if r.get("click_time"):
                stats["click"] += 1
            if r.get("is_bounced") or r.get("bounce_time"):
                stats["bounce"] += 1
        if len(rows) < 500:
            break
        offset += 500
    return stats


def rates(s):
    n = s["sent"] or 1
    return {
        **s,
        "open_pct":   round(s["open"]   / n * 100, 1),
        "reply_pct":  round(s["reply"]  / n * 100, 2),
        "click_pct":  round(s["click"]  / n * 100, 2),
        "bounce_pct": round(s["bounce"] / n * 100, 2),
    }


@app.get("/")
def health():
    return {"ok": True, "service": "FlowOps Metrics API", "ts": datetime.now(timezone.utc).isoformat()}


@app.get("/metrics/today")
def metrics_today():
    """Today's stats per niche (last 24h rolling)."""
    out = []
    for niche, cid in CAMPAIGNS.items():
        s = stats_for_window(cid, 24)
        out.append({"niche": niche, "campaign_id": cid, **rates(s)})
    totals = {k: sum(r.get(k, 0) for r in out) for k in ["sent", "open", "reply", "click", "bounce"]}
    return {"generated_at": datetime.now(timezone.utc).isoformat(),
            "window": "last 24h", "niches": out, "totals": rates(totals)}


@app.get("/metrics/7d")
def metrics_7d():
    """7-day rolling stats + verdict per niche."""
    THRESHOLDS = {"open": 25, "reply": 0.8, "bounce_max": 5.0, "min_sends": 100}
    out = []
    for niche, cid in CAMPAIGNS.items():
        s = stats_for_window(cid, 168)
        r = rates(s)
        flags = []
        if s["sent"] >= THRESHOLDS["min_sends"]:
            if r["open_pct"] < THRESHOLDS["open"]:
                flags.append("LOW_OPEN")
            if r["reply_pct"] < THRESHOLDS["reply"]:
                flags.append("LOW_REPLY")
            if r["bounce_pct"] > THRESHOLDS["bounce_max"]:
                flags.append("HIGH_BOUNCE")
        verdict = "ITERATE" if flags else ("HEALTHY" if s["sent"] >= THRESHOLDS["min_sends"] else "WAIT_FOR_DATA")
        out.append({"niche": niche, "campaign_id": cid, **r, "flags": flags, "verdict": verdict})
    return {"generated_at": datetime.now(timezone.utc).isoformat(),
            "window": "last 7 days", "niches": out}


@app.get("/metrics/niche/{niche}")
def metrics_niche(niche: str):
    """Detail for one niche over multiple windows."""
    niche = niche.upper()
    if niche not in CAMPAIGNS:
        return {"error": f"unknown niche: {niche}", "available": list(CAMPAIGNS.keys())}
    cid = CAMPAIGNS[niche]
    return {
        "niche": niche, "campaign_id": cid,
        "today":      rates(stats_for_window(cid, 24)),
        "last_7d":    rates(stats_for_window(cid, 168)),
        "last_30d":   rates(stats_for_window(cid, 720)),
    }


@app.get("/variants/performance")
def variants_performance():
    """A/B variant breakdown across all campaigns. Looks at custom_fields.ab_variant_id."""
    out = []
    for niche, cid in CAMPAIGNS.items():
        try:
            seqs = G(f"/campaigns/{cid}/sequences")
        except Exception:
            continue
        for s in seqs:
            n_var = s.get("seq_number")
            for v in (s.get("sequence_variants") or []):
                out.append({
                    "niche": niche,
                    "campaign_id": cid,
                    "step": n_var,
                    "variant_label": v.get("variant_label"),
                    "subject": (v.get("subject") or "")[:80],
                    "distribution_pct": v.get("variant_distribution_percentage"),
                })
    return {"variants": out, "count": len(out)}


@app.get("/leads/recent")
def leads_recent(limit: int = Query(50, le=200)):
    """Most recent leads with activity (replies, clicks)."""
    activity = []
    for niche, cid in CAMPAIGNS.items():
        try:
            d = G(f"/campaigns/{cid}/statistics?limit=100&offset=0")
            rows = d.get("data", [])
        except Exception:
            continue
        for r in rows:
            if r.get("reply_time") or r.get("click_time"):
                activity.append({
                    "niche":       niche,
                    "lead_email":  r.get("lead_email"),
                    "lead_name":   r.get("lead_name"),
                    "sent_time":   r.get("sent_time"),
                    "reply_time":  r.get("reply_time"),
                    "click_time":  r.get("click_time"),
                    "open_count":  r.get("open_count", 0),
                    "subject":     r.get("email_subject"),
                })
    activity.sort(key=lambda x: x.get("reply_time") or x.get("click_time") or "", reverse=True)
    return {"count": min(len(activity), limit), "leads": activity[:limit]}


@app.get("/spend")
def spend():
    """API spend rollup across OpenRouter + Apify."""
    out = {"openrouter": None, "apify": None, "smartlead_note": "flat subscription"}
    # OpenRouter
    try:
        r = urllib.request.Request("https://openrouter.ai/api/v1/auth/key",
                                   headers={"Authorization": f"Bearer {OR_KEY}"})
        with urllib.request.urlopen(r, timeout=15) as resp:
            d = json.loads(resp.read().decode()).get("data", {})
        out["openrouter"] = {
            "today":   round(d.get("usage_daily", 0), 2),
            "week":    round(d.get("usage_weekly", 0), 2),
            "month":   round(d.get("usage_monthly", 0), 2),
            "total":   round(d.get("usage", 0), 2),
        }
    except Exception as e:
        out["openrouter"] = {"error": str(e)}
    # Apify
    try:
        r = urllib.request.Request(f"https://api.apify.com/v2/users/me?token={APIFY_TOK}")
        with urllib.request.urlopen(r, timeout=15) as resp:
            d = json.loads(resp.read().decode()).get("data", {})
        out["apify"] = {
            "plan":          d.get("plan", {}).get("id", "?"),
            "month_usage":   round(float(d.get("usageCycle", {}).get("platformUsageUsd", 0)), 2),
            "month_limit":   d.get("limits", {}).get("monthlyServiceUsageUsd"),
        }
    except Exception as e:
        out["apify"] = {"error": str(e)}
    out["generated_at"] = datetime.now(timezone.utc).isoformat()
    return out


@app.get("/campaigns")
def campaigns():
    """All campaigns + lead counts + status."""
    out = []
    for niche, cid in CAMPAIGNS.items():
        try:
            a = G(f"/campaigns/{cid}/analytics")
            status = a.get("status", "?")
        except Exception:
            status = "ERR"
        try:
            L = G(f"/campaigns/{cid}/leads?limit=1&offset=0")
            total = L.get("total_leads", 0) if isinstance(L, dict) else 0
            total = int(str(total)) if str(total).isdigit() else 0
        except Exception:
            total = 0
        out.append({
            "niche": niche,
            "campaign_id": cid,
            "status": status,
            "total_leads": total,
        })
    return {"campaigns": out, "generated_at": datetime.now(timezone.utc).isoformat()}


@app.get("/bookings")
def bookings(limit: int = Query(50, le=200)):
    """Booked calls (sourced from GHL webhook events logged by webhook_server)."""
    import os as _os
    path = _os.path.expanduser("~/.council/bookings.jsonl")
    if not _os.path.exists(path):
        return {"count": 0, "today": 0, "week": 0, "month": 0, "bookings": []}
    with open(path) as f:
        lines = f.readlines()
    out = []
    for ln in lines[-limit:]:
        try:
            e = json.loads(ln)
            e.pop("raw", None)
            out.append(e)
        except Exception:
            continue
    # Tally by recency
    now = datetime.now(timezone.utc)
    def _is_recent(e, hours):
        ts = e.get("received_at","")
        try:
            dt = datetime.fromisoformat(ts.replace("Z","+00:00"))
            return (now - dt).total_seconds() < hours * 3600
        except:
            return False
    confirmed = [e for e in out if (e.get("event_type") == "AppointmentCreate")
                 and (e.get("status") or "").lower() not in ("cancelled","canceled","noshow")]
    return {
        "count":     len(confirmed),
        "today":     sum(1 for e in confirmed if _is_recent(e, 24)),
        "week":      sum(1 for e in confirmed if _is_recent(e, 168)),
        "month":     sum(1 for e in confirmed if _is_recent(e, 720)),
        "bookings":  list(reversed(confirmed)),
    }


@app.get("/dashboard/summary")
def dashboard_summary():
    """One-shot endpoint with everything needed for the Lovable dashboard."""
    return {
        "today":     metrics_today(),
        "last_7d":   metrics_7d(),
        "campaigns": campaigns(),
        "spend":     spend(),
        "leads":     leads_recent(limit=20),
        "bookings":  bookings(limit=20),
    }
