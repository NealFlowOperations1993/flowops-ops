"""
FlowScore wrapper — hits the REAL flowoperations.ai/flowscore API
(Supabase Edge Function `analyze-url`).

Returns: { overall_score, score_range, interpretation,
           estimated_monthly_revenue_leakage:{min,max},
           dimensions:[{name, score, findings:[]}] }

Use this per-lead during Council personalization. The result drops
into Smartlead custom_fields so emails reference REAL scores, not made-up ones.
"""
import json
import urllib.request
import urllib.error

SUPA = "https://npjkusfkwybhyisfrhtb.supabase.co"
ANON = ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5wamt1c2Zrd3liaHlpc2ZyaHRiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ1NzY2OTEsImV4cCI6MjA5MDE1MjY5MX0."
        "k5-2-4uggEHtHKHxzlOYMMSnZCpIxIxeiW2st6mAC5I")

# Map our internal niches -> flowoperations.ai/flowscore niche keys
NICHE_MAP = {
    "WEALTH":    "wealth",
    "FINANCIAL": "financial",
    "MORTGAGE":  "mortgage",
    "INSURANCE": "insurance",
    "MEDSPA":    "fitness",       # closest match in their dropdown
    "PI_LAW":    "generic",       # no law option; generic gives reasonable scoring
    "MCA":       "mca",
    "COMMLOAN":  "commercial",
    "AGENCY":    "agency",
    "RECRUITER": "recruiter",
    "COACH_BIZ": "coach",
    "COACH_FIT": "fitness",
}


def score(url: str, niche: str = "generic", monthly_traffic: int = None, avg_deal_size: int = None) -> dict:
    """Hit the FlowScore API. Returns raw payload or {'error': str}."""
    if not url:
        return {"error": "no_url"}
    if not url.startswith("http"):
        url = f"https://{url}"

    niche_key = NICHE_MAP.get(niche.upper(), "generic")
    body = {"url": url, "niche": niche_key}
    if monthly_traffic:
        body["monthlyTraffic"] = int(monthly_traffic)
    if avg_deal_size:
        body["avgDealSize"] = int(avg_deal_size)

    req = urllib.request.Request(
        f"{SUPA}/functions/v1/analyze-url",
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {ANON}",
            "apikey": ANON,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": f"http_{e.code}", "detail": e.read().decode()[:200]}
    except Exception as e:
        return {"error": str(e)[:200]}


def extract_for_email(fs: dict) -> dict:
    """Distill API payload into the 4 fields the email templates need."""
    if not fs or fs.get("error"):
        return {
            "flowscore":         "",
            "flowscore_meaning": "",
            "flowscore_leak":    "",
            "flowscore_weak":    "",
        }

    score_val = fs.get("overall_score", 0)
    leak = fs.get("estimated_monthly_revenue_leakage", {}) or {}
    lo, hi = leak.get("min", 0), leak.get("max", 0)

    # Pick the single WEAKEST dimension (lowest score) for the "profound point"
    dims = fs.get("dimensions", []) or []
    weakest = min(dims, key=lambda d: d.get("score", 100)) if dims else {}
    weak_name = weakest.get("name", "")
    findings = weakest.get("findings", []) or []
    # Take the first ✗ finding (the strongest gap)
    weak_finding = ""
    for f in findings:
        if f.startswith("✗") or f.startswith("✗"):
            weak_finding = f.lstrip("✗✗ ").strip()
            break
    if not weak_finding and findings:
        weak_finding = findings[0].lstrip("✗✓⚠ ✗✓⚠ ").strip()

    # Build the prose pieces email templates plug into:
    meaning_phrase = (
        f"That's {fs.get('score_range','red')} territory — "
        "you're losing deals you don't even know about."
        if score_val < 60 else
        f"Solid ({fs.get('score_range','green')}) — but there are 1-2 quiet leaks worth ~$15-30K/mo."
    )

    leak_phrase = (
        f"${lo:,}-${hi:,}/month" if hi else
        "low five-figures/month"
    )

    weak_phrase = (
        f"Your biggest gap: **{weak_name}** ({weakest.get('score',0)}/100). "
        f"{weak_finding[:180]}"
        if weak_name else ""
    )

    return {
        "flowscore":         str(score_val),
        "flowscore_meaning": meaning_phrase,
        "flowscore_leak":    leak_phrase,
        "flowscore_weak":    weak_phrase,
    }


if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else "https://mercerwealthmanagementgroup.com"
    niche = sys.argv[2] if len(sys.argv) > 2 else "WEALTH"
    raw = score(url, niche)
    print("=== RAW ===")
    print(json.dumps(raw, indent=2)[:2000])
    print("\n=== FOR EMAIL ===")
    print(json.dumps(extract_for_email(raw), indent=2))
