"""
Signal Enricher — pulls per-lead intel before Council personalization.

Sources (all free or via existing Apify subscription):
  - LinkedIn activity:  Apify Profile Scraper actor
  - Recent news:        Apify Google Search actor (one query per lead)
  - Tech stack:         direct HTTP GET on homepage + regex
  - Form D filings:     SEC EDGAR JSON API (WEALTH only)
  - UCC filings:        deferred to v2 (Playwright state SOS — too slow for cold path)

Cache: per-company domain in Supabase `signals_cache` (7-day TTL).

Public API:
  enrich(lead: dict) -> dict[str, str]   # signals keyed by signal name
  enrich_batch(leads: list) -> list      # processed in parallel where possible
"""
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone

APIFY_TOKEN = os.environ["APIFY_TOKEN"]
SUPABASE_URL = "https://uuhnhybmdsyzppiuhlvk.supabase.co"
SUPABASE_JWT = os.environ["SUPABASE_SERVICE_KEY"]
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15"

CACHE_TTL_DAYS = 7


# ─── HTTP helpers ──────────────────────────────────────────────────────────

def _get(url: str, headers: dict | None = None, timeout: int = 20) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="ignore")


def _post(url: str, body: dict, headers: dict | None = None, timeout: int = 60) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "User-Agent": UA, **(headers or {})},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


# ─── Supabase cache ────────────────────────────────────────────────────────

CACHE_PATH = os.path.expanduser("~/.council/signals_cache.json")
os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)


def _cache_load() -> dict:
    if not os.path.exists(CACHE_PATH):
        return {}
    try:
        with open(CACHE_PATH) as f:
            return json.load(f)
    except Exception:
        return {}


def _cache_save(cache: dict) -> None:
    try:
        with open(CACHE_PATH, "w") as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        print(f"  [cache-warn] save: {e}")


def _cache_get(company_domain: str) -> dict | None:
    """Look up cached signals for a company. Returns None if missing or expired."""
    domain = company_domain.lower().strip()
    cache = _cache_load()
    if domain not in cache:
        return None
    row = cache[domain]
    try:
        cached_at = datetime.fromisoformat(row["cached_at"].replace("Z", "+00:00"))
        if (datetime.now(timezone.utc) - cached_at).days > CACHE_TTL_DAYS:
            return None
        return row.get("signals") or {}
    except Exception:
        return None


def _cache_put(company_domain: str, signals: dict) -> None:
    """Upsert signals into local JSON cache."""
    domain = company_domain.lower().strip()
    cache = _cache_load()
    cache[domain] = {
        "signals":   signals,
        "cached_at": datetime.now(timezone.utc).isoformat(),
    }
    _cache_save(cache)


# ─── Signal pulls ──────────────────────────────────────────────────────────

def signal_tech_stack(domain: str) -> str:
    """Detect a few common stack signals from the homepage HTML."""
    if not domain:
        return ""
    url = domain if domain.startswith("http") else f"https://{domain}"
    try:
        html = _get(url, timeout=15)
    except Exception:
        return ""
    found = []
    patterns = {
        "GHL / HighLevel":  r"(highlevel|gohighlevel|leadconnector)",
        "WordPress":        r"wp-content|wp-includes|wp-json",
        "Wix":              r"static\.wixstatic\.com|wix-code",
        "Squarespace":      r"squarespace\.com|squarespace-cdn",
        "Webflow":          r"webflow\.com|wf-domain",
        "ClickFunnels":     r"clickfunnels|cfvars",
        "Calendly":         r"calendly\.com",
        "Cal.com":          r"cal\.com",
        "Intercom":         r"widget\.intercom\.io",
        "HubSpot":          r"hs-scripts\.com|hsforms",
        "Facebook Pixel":   r"facebook\.com/tr\?id=|fbevents\.js",
        "Google Tag Mgr":   r"googletagmanager\.com/gtm\.js",
    }
    for name, pat in patterns.items():
        if re.search(pat, html, re.IGNORECASE):
            found.append(name)
    if not found:
        return ""
    return f"Their site is running: {', '.join(found[:5])}."


def signal_recent_news(company_name: str, city: str = "") -> str:
    """DuckDuckGo HTML scrape. Free, no auth, no rate limits."""
    if not company_name:
        return ""
    q = f'"{company_name}"'
    if city:
        q += f" {city}"
    try:
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(q)}"
        html = _get(url, timeout=15)
        # DDG HTML: results are in <a class="result__a">...</a> with <a class="result__snippet">
        title_re = re.compile(r'<a[^>]+class="result__a"[^>]*>(.*?)</a>', re.DOTALL)
        snip_re  = re.compile(r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>', re.DOTALL)
        titles = [re.sub(r"<[^>]+>", "", t).strip() for t in title_re.findall(html)][:5]
        snips  = [re.sub(r"<[^>]+>", "", s).strip() for s in snip_re.findall(html)][:5]
        relevant = []
        key = company_name.lower()[:15]
        for t, s in zip(titles, snips):
            combined = (t + " " + s).lower()
            if key in combined:
                relevant.append(f"{t}: {s[:150]}")
            if len(relevant) >= 2:
                break
        if relevant:
            return f"Recent web mentions: {' || '.join(relevant)}"
        return ""
    except Exception as e:
        print(f"  [news-warn] {e}")
        return ""


def signal_linkedin_activity(linkedin_url: str) -> str:
    """Apify LinkedIn Profile Scraper. Returns recent activity summary."""
    if not linkedin_url:
        return ""
    if "linkedin.com/in/" not in linkedin_url.lower():
        # might be just the slug
        if not linkedin_url.startswith("http"):
            linkedin_url = f"https://linkedin.com/in/{linkedin_url.strip('/')}"
    try:
        url = f"https://api.apify.com/v2/acts/apimaestro~linkedin-profile-detail/run-sync-get-dataset-items?token={APIFY_TOKEN}"
        body = {"profileUrls": [linkedin_url]}
        resp = _post(url, body, timeout=60)
        if isinstance(resp, list) and resp:
            p = resp[0]
            bits = []
            if p.get("headline"):
                bits.append(f"Headline: {p['headline'][:120]}")
            if p.get("about"):
                bits.append(f"About snippet: {p['about'][:200]}")
            posts = p.get("posts") or []
            if posts:
                latest = posts[0]
                bits.append(f"Latest post: {(latest.get('text') or '')[:200]}")
            return " | ".join(bits) if bits else ""
        return ""
    except Exception as e:
        print(f"  [linkedin-warn] {e}")
        return ""


def signal_form_d_filings(city: str, state: str) -> str:
    """SEC EDGAR full-text search for recent Form D filings in metro."""
    if not city and not state:
        return ""
    try:
        q = urllib.parse.quote(f'"{city}"' if city else state)
        url = f"https://efts.sec.gov/LATEST/search-index?q={q}&forms=D&dateRange=custom&startdt=2026-04-01&enddt=2026-05-31"
        html = _get(url, timeout=10)
        # Form D filings list is in JSON inside the page
        try:
            data = json.loads(html)
            hits = (data.get("hits") or {}).get("total", {}).get("value", 0)
            if hits > 0:
                return f"{hits} Form D filings near {city or state} in last 60 days (SEC EDGAR)."
        except Exception:
            pass
        return ""
    except Exception as e:
        print(f"  [edgar-warn] {e}")
        return ""


# ─── Main enrichment ───────────────────────────────────────────────────────

def enrich(lead: dict) -> dict:
    """
    Pull all signals for a lead. Returns a dict of signal_name -> human string.
    Caches by company domain.
    """
    company = lead.get("company") or lead.get("company_name") or ""
    website = lead.get("website") or ""
    city    = lead.get("city") or ""
    state   = lead.get("state") or ""
    niche   = (lead.get("niche") or "").upper()
    linkedin = lead.get("linkedin") or ""

    # Domain for cache key
    domain = ""
    if website:
        m = re.search(r"(?:https?://)?(?:www\.)?([^/]+)", website)
        if m:
            domain = m.group(1).lower()
    if not domain and "@" in lead.get("email", ""):
        domain = lead["email"].split("@")[1].lower()
    if not domain:
        domain = company.lower().replace(" ", "")

    # Cache check
    cached = _cache_get(domain)
    if cached:
        return cached

    signals = {}

    # Fire signal pulls in parallel
    # Note: DDG news search disabled for batch runs (unreliable timing).
    # Enable with enable_news=True via lead dict for single-lead enrichment.
    enable_news = bool(lead.get("_enable_news"))
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {}
        futs[ex.submit(signal_tech_stack, domain)] = "tech_stack"
        if enable_news:
            futs[ex.submit(signal_recent_news, company, city)] = "recent_news"
        if linkedin:
            futs[ex.submit(signal_linkedin_activity, linkedin)] = "linkedin_activity"
        if niche == "WEALTH":
            futs[ex.submit(signal_form_d_filings, city, state)] = "form_d_local"

        for fut in as_completed(futs):
            name = futs[fut]
            try:
                v = fut.result(timeout=30)
                if v:
                    signals[name] = v
            except Exception as e:
                print(f"  [enrich-warn] {name}: {e}")

    # Cache (even empty results, to avoid re-pulling for a week)
    _cache_put(domain, signals)

    return signals


def enrich_batch(leads: list[dict], max_workers: int = 5) -> list[dict]:
    """Enrich a list of leads in parallel."""
    results = [None] * len(leads)

    def _do(idx_lead):
        idx, lead = idx_lead
        try:
            return idx, enrich(lead)
        except Exception as e:
            return idx, {"_error": str(e)}

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futs = [pool.submit(_do, (i, l)) for i, l in enumerate(leads)]
        for fut in as_completed(futs):
            idx, sig = fut.result()
            results[idx] = sig
    return results


def format_signals_for_council(signals: dict) -> str:
    """Render signals as a clean block to inject into Council persona context."""
    if not signals:
        return "(no specific signals available for this lead)"
    lines = ["SIGNALS WE KNOW ABOUT THIS LEAD (use ONLY if they ring true, never make up specifics):"]
    for name, val in signals.items():
        if val:
            lines.append(f"  - {name}: {val}")
    return "\n".join(lines)


if __name__ == "__main__":
    # Smoke test on 3 leads
    test_leads = [
        {
            "email": "palmer@lionssharewealth.com",
            "company": "Lion's Share Wealth",
            "website": "lionssharewealth.com",
            "city":    "Phoenix",
            "state":   "Arizona",
            "niche":   "WEALTH",
            "linkedin": "",
        },
        {
            "email": "jarroed@purpletreefunding.com",
            "company": "Purple Tree Funding",
            "website": "purpletreefunding.com",
            "city":    "Brooklyn",
            "state":   "NY",
            "niche":   "MCA",
            "linkedin": "",
        },
        {
            "email": "calvin.james@grandiosecapital.com",
            "company": "Grandiose Capital",
            "website": "grandiosecapital.com",
            "city":    "Miami",
            "state":   "Florida",
            "niche":   "MCA",
            "linkedin": "",
        },
    ]
    t0 = time.time()
    for i, lead in enumerate(test_leads, 1):
        print(f"\n{'='*70}\n[{i}] {lead['company']} ({lead['niche']})\n{'='*70}")
        s = enrich(lead)
        for k, v in s.items():
            print(f"\n  {k.upper()}:")
            print(f"    {v[:300]}")
        if not s:
            print("  (no signals captured)")
    print(f"\n--- elapsed: {time.time()-t0:.1f}s ---")
