"""Tier-1 personal event signals: their own site's recent content + company news search.
Permanent home (was /tmp, which gets cleared). Used by personalize/regen chains.
"""
import json, re, urllib.request, urllib.error
import os

APIFY = os.environ["APIFY_TOKEN"]
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15"


def _get(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="ignore")


def site_recent_content(website):
    if not website:
        return None
    url = website if website.startswith("http") else f"https://{website}"
    try:
        html = _get(url)
    except Exception:
        return None
    links = re.findall(r'href="([^"]*(?:blog|news|insights|press|articles|updates)[^"]*)"', html, re.I)
    m = re.match(r"(https?://[^/]+)", url)
    if not m:
        return None
    base = m.group(1)
    seen = set()
    candidates = []
    for l in links[:5]:
        full = l if l.startswith("http") else base + ("/" + l.lstrip("/"))
        if full in seen or base not in full:
            continue
        seen.add(full)
        candidates.append(full)
    titles = []
    for c in candidates[:2]:
        try:
            sub = _get(c)
        except Exception:
            continue
        for mt in re.findall(r"<h[23][^>]*>\s*(?:<a[^>]*>)?([^<]{15,110})<", sub)[:6]:
            t = re.sub(r"\s+", " ", mt).strip()
            if t and not any(x in t.lower() for x in ("cookie", "privacy", "subscribe", "contact us")):
                titles.append(t)
    if titles:
        return "Recent posts/articles on their own site: " + " | ".join(titles[:4])
    return None


def company_news(company, city=""):
    if not company or len(company) < 4:
        return None
    q = f'"{company}" {city} news 2026'
    body = json.dumps({"query": q, "maxResults": 3, "outputFormats": ["markdown"],
                       "scrapingTool": "raw-http", "htmlTransformer": "none"}).encode()
    try:
        req = urllib.request.Request(
            f"https://api.apify.com/v2/acts/apify~rag-web-browser/run-sync-get-dataset-items?token={APIFY}&timeout=60",
            data=body, headers={"Content-Type": "application/json"}, method="POST")
        items = json.loads(urllib.request.urlopen(req, timeout=90).read())
    except Exception:
        return None
    out = []
    for it in items[:3]:
        meta = it.get("searchResult", {}) or {}
        title = meta.get("title", "")
        desc = meta.get("description", "")
        if title and company.split()[0].lower() in (title + desc).lower():
            out.append(f"{title} — {desc[:140]}")
    if out:
        return "Recent news/search results about THIS company: " + " || ".join(out[:2])
    return None


def personal_event_signals(company, city, website):
    sig = {}
    s1 = site_recent_content(website)
    if s1:
        sig["own_site_recent_content"] = s1
    s2 = company_news(company, city)
    if s2:
        sig["company_specific_news"] = s2
    tier = 1 if sig else 3
    return sig, tier
