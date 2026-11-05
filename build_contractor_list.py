"""
Build a list of hardscape/patio contractors with a NAMED owner email.

Pipeline (per metro):
  1. Google Maps scrape via Apify (compass~google-maps-extractor, ~$0.004/place),
     websites only, hard-capped by --max-usd.
  2. Layer-2 qualification from each contractor's own site (same gates as the
     infrastructure guide): 15+ reviews and 4.0+ rating, hardscape vocabulary
     present, maintenance terms do not dominate, a portfolio/gallery page exists.
  3. Email discovery from home + /about + /team + /contact pages. Role inboxes
     (info@, office@, sales@ ...) are dropped. Only named addresses survive.
  4. Owner first name only with evidence:
       owner_confirmed — the site names an owner/founder/president AND the
                         email's local part matches that person
       named_contact   — a named address whose first name appears on the
                         site, but nobody is labelled owner
     Nothing is guessed from an email local part alone.
  5. Optional MillionVerifier check (--verify). Keeps "ok" only.

Output CSV columns:
  business_name, owner_first_name, website, owner_email, city, state,
  match, evidence, reviews, rating
The main file holds owner_confirmed rows; named_contact rows go to a second
file so you can decide whether to use them.

Usage:
  set -a; source ~/.config/n8n-creds/flowops-core.env; set +a
  python3 build_contractor_list.py \\
      --metro "Atlanta, GA" --metro "Charlotte, NC" --metro "Columbus, OH" \\
      --target 300 --max-usd 25 --exclude contacted.csv --out ~/Desktop/hardscape_300.csv

  --exclude takes any CSV with an "email" and/or "website"/"domain" column
  (e.g. an export of the master lead list) so nobody already contacted is
  listed again.

Output is a CSV outside the repo (*.csv is gitignored). Never commit lead data.
"""
import argparse
import csv
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
ACTOR = "compass~google-maps-extractor"
COST_PER_PLACE = 0.004
SEARCH_TERMS = ["hardscaping contractor", "paver patio contractor", "retaining wall contractor"]
SUBPAGES = ["", "/about", "/about-us", "/our-team", "/team", "/contact", "/contact-us"]

HARDSCAPE = ["paver", "retaining wall", "seat wall", "outdoor kitchen", "hardscap", "patio", "fire pit",
             "flagstone", "natural stone", "belgard", "unilock", "techo-bloc", "ep henry"]
MAINTENANCE = ["mowing", "lawn mowing", "fertiliz", "aeration", "snow removal", "leaf removal",
               "weekly maintenance", "lawn care"]
PORTFOLIO = re.compile(r'href="[^"]*(gallery|portfolio|projects|our-work|photos)[^"]*"', re.I)

ROLE_LOCALS = {
    "info", "office", "sales", "contact", "contactus", "admin", "hello", "hi", "support", "service",
    "services", "estimates", "estimate", "quotes", "quote", "team", "mail", "email", "jobs", "careers",
    "billing", "accounts", "accounting", "marketing", "help", "inquiries", "inquiry", "enquiries",
    "booking", "bookings", "schedule", "scheduling", "design", "designs", "noreply", "no-reply",
    "webmaster", "customerservice", "reception", "frontdesk", "hr", "projects", "general", "orders",
    "landscaping", "hardscaping", "outdoor", "web", "website", "media", "press", "warranty", "ap", "ar",
}
JUNK_EMAIL = re.compile(r"\.(png|jpe?g|gif|webp|avif|svg)$|example\.|yourdomain|mysite|domain\.com|"
                        r"sentry|wixpress|godaddy|latofonts|impallari|@company\.com|you@", re.I)
FREE_MAIL = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "aol.com", "icloud.com", "comcast.net"}
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
TITLE = r"(?i:co-?owner|owner|co-?founder|founder|president|ceo|principal)"
NAME = r"([A-Z][a-z]{2,})(?:\s+[A-Z]\.)?\s+([A-Z][a-zA-Z'\-]{1,})"
OWNER_PATTERNS = [
    re.compile(NAME + r",?\s+(?:is\s+)?(?i:the\s+|our\s+|a\s+)?(?:[A-Za-z&]+\s+)?" + TITLE),
    re.compile(TITLE + r"s?(?:\s*(?:/|&|and)\s*\w+)?\s*[:\-\u2013,]?\s*" + NAME),
]
# capitalised words that start sentences, menus and buttons, never a first name
NOT_FIRST_NAMES = {"the", "our", "about", "contact", "call", "meet", "home", "projects", "project", "gallery",
                   "services", "service", "free", "get", "request", "read", "learn", "view", "see", "book",
                   "schedule", "quality", "custom", "outdoor", "your", "we", "with", "and", "for", "from", "why",
                   "what", "how", "best", "top", "new", "privacy", "terms", "copyright", "all", "rights",
                   "reserved", "north", "south", "east", "west", "county", "city", "lake", "mount", "saint",
                   "owner", "founder", "president", "manager", "office", "team", "staff", "email", "phone"}
# words that make "First Last" a business name rather than a person
BIZ_WORDS = {"hardscapes", "hardscaping", "hardscape", "landscaping", "landscapes", "landscape", "construction",
             "pavers", "paving", "outdoor", "outdoors", "stone", "stoneworks", "masonry", "design", "designs",
             "services", "service", "company", "co", "llc", "inc", "group", "decks", "contracting", "builders",
             "patios", "concrete", "lawn", "gardens", "enterprises", "home", "homes", "living", "solutions"}

def http_get(url: str, timeout: int = 12) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(1_500_000).decode("utf-8", errors="replace")


def page_text(raw: str) -> str:
    raw = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", raw)
    # block-level tags become hard breaks so a name never spans two page elements
    raw = re.sub(r"(?i)</?(p|div|li|ul|ol|h[1-6]|br|td|tr|th|table|section|header|footer|nav|a|button|label|option)\b[^>]*>", " | ", raw)
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", raw)))


def domain_of(url: str) -> str:
    host = urllib.parse.urlparse(url if "//" in url else "http://" + url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def extract_emails(raw: str, site_domain: str) -> set[str]:
    found = set(re.findall(r'mailto:([^"\'?>\s]+)', raw, re.I)) | set(EMAIL_RE.findall(page_text(raw)))
    keep = set()
    for e in found:
        e = urllib.parse.unquote(e).strip().strip(".").lower()
        if not EMAIL_RE.fullmatch(e) or JUNK_EMAIL.search(e):
            continue
        dom = e.split("@", 1)[1]
        if dom == site_domain or dom.endswith("." + site_domain) or dom in FREE_MAIL:
            keep.add(e)
    return keep


def is_named(email: str) -> bool:
    local = re.sub(r"\d+$", "", email.split("@", 1)[0])
    parts = [p for p in re.split(r"[._\-+]", local) if p]
    if not parts or local in ROLE_LOCALS or parts[0] in ROLE_LOCALS:
        return False
    return parts[0].isalpha() and len(parts[0]) >= 2


def person_names(text: str, business: str = "") -> list[tuple[str, str]]:
    """Every "First Last" on the page that is not part of a business name."""
    biz = {w.lower() for w in re.findall(r"[A-Za-z]+", business)}
    out = []
    for m in re.finditer(r"(?=\b" + NAME + ")", text):
        first, last = m.group(1), m.group(2)
        if (last.lower() in BIZ_WORDS or first.lower() in BIZ_WORDS or first.lower() in NOT_FIRST_NAMES
                or first.lower() in biz or last.lower() in NOT_FIRST_NAMES):
            continue
        out.append((first, last))
    return list(dict.fromkeys(out))


def owner_names(text: str, business: str = "") -> list[tuple[str, str]]:
    names = []
    for pat in OWNER_PATTERNS:
        names += [(m.group(1), m.group(2)) for m in pat.finditer(text)]
    people = set(person_names(text, business))
    return [n for n in dict.fromkeys(names) if n in people]


def local_matches(email: str, first: str, last: str = "") -> bool:
    local = re.sub(r"\d+$", "", email.split("@", 1)[0].lower())
    f, l = first.lower(), last.lower()
    forms = {f, f + l, f + "." + l, f + "_" + l, f + "-" + l, f[:1] + l, f[:1] + "." + l} if l else {f}
    return local in forms


def first_name_on_site(email: str, text: str, business: str = "") -> str | None:
    """The first name of a named address, only if that person appears by full name on the site."""
    for first, last in person_names(text, business):
        if local_matches(email, first, last):
            return first
    return None

def qualify(place: dict, text: str, raw_all: str) -> str | None:
    """Return a rejection reason, or None if the contractor passes every gate."""
    if (place.get("reviewsCount") or 0) < 15 or (place.get("totalScore") or 0) < 4.0:
        return "maps_quality"
    low = text.lower()
    hard = sum(low.count(w) for w in HARDSCAPE)
    maint = sum(low.count(w) for w in MAINTENANCE)
    if hard == 0:
        return "no_hardscape_vocab"
    if maint > hard:
        return "maintenance_dominant"
    if not PORTFOLIO.search(raw_all):
        return "no_portfolio"
    return None


def process(place: dict) -> dict:
    site = place.get("website") or ""
    base = site.split("?")[0].rstrip("/")
    dom = domain_of(base)
    out = {"place": place, "domain": dom, "reject": None, "rows": [], "site": base}
    if (place.get("reviewsCount") or 0) < 15 or (place.get("totalScore") or 0) < 4.0:
        out["reject"] = "maps_quality"
        return out
    raws = []
    for sub in SUBPAGES:
        try:
            raws.append(http_get(base + sub))
        except (urllib.error.URLError, TimeoutError, ValueError, ConnectionError, OSError):
            if sub == "":
                out["reject"] = "site_unreachable"
                return out
    raw_all = "\n".join(raws)
    text = page_text(raw_all)
    out["reject"] = qualify(place, text, raw_all)
    if out["reject"]:
        return out
    named = sorted(e for e in extract_emails(raw_all, dom) if is_named(e))
    if not named:
        out["reject"] = "no_named_email"
        return out
    biz = place.get("title", "")
    owners = owner_names(text, biz)
    for e in named:
        owner = next((o for o in owners if local_matches(e, *o)), None)
        if owner:
            out["rows"].append({"email": e, "first": owner[0], "match": "owner_confirmed",
                                "evidence": f"site names {owner[0]} {owner[1]} as owner/founder/president"})
            continue
        seen = first_name_on_site(e, text, biz)
        if seen:
            out["rows"].append({"email": e, "first": seen, "match": "named_contact",
                                "evidence": f"{seen} appears by full name on site; not labelled owner"})
    if not out["rows"]:
        out["reject"] = "name_not_evidenced"
    return out


def apify_scrape(metro: str, per_term: int, max_usd: float) -> list[dict]:
    token = os.environ["APIFY_TOKEN"]
    body = {"searchStringsArray": SEARCH_TERMS, "locationQuery": metro, "maxCrawledPlacesPerSearch": per_term,
            "language": "en", "website": "withWebsite", "skipClosedPlaces": True}
    qs = urllib.parse.urlencode({"token": token, "maxTotalChargeUsd": f"{max_usd:.2f}", "timeout": 900})
    url = f"https://api.apify.com/v2/acts/{ACTOR}/run-sync-get-dataset-items?{qs}"
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json", "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=960) as r:
        return json.loads(r.read().decode())


def budget_check(estimate: float) -> None:
    """Ask the n8n Budget Guard before spending, when its URL is configured."""
    url = os.environ.get("FO_BUDGET_GUARD_URL")
    if not url:
        print(f"  (FO_BUDGET_GUARD_URL not set; skipping Budget Guard for ${estimate:.2f})")
        return
    req = urllib.request.Request(url, method="POST", headers={"Content-Type": "application/json"},
                                 data=json.dumps({"action": "check_and_commit", "provider": "apify",
                                                  "est_cost_usd": round(estimate, 2),
                                                  "source": "build_contractor_list"}).encode())
    with urllib.request.urlopen(req, timeout=30) as r:
        res = json.loads(r.read().decode() or "{}")
    res = res[0] if isinstance(res, list) and res else res
    if res.get("allow") is not True:
        sys.exit(f"Budget Guard denied ${estimate:.2f}: remaining today ${res.get('remaining_usd')} of ${res.get('cap_usd')}")
    print(f"  Budget Guard: allowed ${estimate:.2f}, ${res.get('remaining_usd')} left today")


def verify(email: str) -> str:
    key = os.environ["MILLIONVERIFIER_API_KEY"]
    url = "https://api.millionverifier.com/api/v3/?" + urllib.parse.urlencode({"api": key, "email": email, "timeout": 10})
    try:
        return json.loads(http_get(url, timeout=20)).get("result", "unknown")
    except (urllib.error.URLError, ValueError, OSError):
        return "error"


def load_exclusions(path: str | None) -> tuple[set[str], set[str]]:
    emails, domains = set(), set()
    if not path:
        return emails, domains
    with open(os.path.expanduser(path), newline="", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            low = {k.lower().strip(): (v or "").strip() for k, v in row.items() if k}
            if low.get("email"):
                emails.add(low["email"].lower())
                domains.add(low["email"].lower().split("@")[-1])
            for k in ("website", "domain"):
                if low.get(k):
                    domains.add(domain_of(low[k]))
    domains -= FREE_MAIL
    return emails, domains


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--metro", action="append", required=True, help='e.g. "Atlanta, GA" (repeat per metro)')
    ap.add_argument("--target", type=int, default=300, help="owner_confirmed rows wanted in total")
    ap.add_argument("--per-term", type=int, default=250, help="max Maps places per search term per metro")
    ap.add_argument("--max-usd", type=float, required=True, help="hard cap on total Apify spend")
    ap.add_argument("--exclude", help="CSV of already-contacted leads (email/website/domain columns)")
    ap.add_argument("--verify", action="store_true", help="MillionVerifier check (needs MILLIONVERIFIER_API_KEY)")
    ap.add_argument("--places-json", help="reuse a saved scrape instead of calling Apify (no spend)")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    per_metro_cap = args.max_usd / len(args.metro)
    estimate = len(args.metro) * len(SEARCH_TERMS) * args.per_term * COST_PER_PLACE
    if not args.places_json:
        if estimate > args.max_usd:
            sys.exit(f"Worst-case scrape cost ${estimate:.2f} exceeds --max-usd {args.max_usd}. Lower --per-term.")
        budget_check(estimate)

    ex_emails, ex_domains = load_exclusions(args.exclude)
    places: list[dict] = []
    if args.places_json:
        places = json.load(open(os.path.expanduser(args.places_json)))
    else:
        for metro in args.metro:
            print(f"Scraping {metro} (cap ${per_metro_cap:.2f})...")
            got = apify_scrape(metro, args.per_term, per_metro_cap)
            for p in got:
                p["_metro"] = metro
            places += got
            print(f"  {len(got)} places")
        snap = os.path.splitext(os.path.expanduser(args.out))[0] + "_places.json"
        json.dump(places, open(snap, "w"))
        print(f"Raw scrape saved to {snap} (re-run with --places-json to avoid paying again)")

    seen, todo = set(), []
    for p in places:
        dom = domain_of(p.get("website") or "")
        if dom and dom not in seen and dom not in ex_domains:
            seen.add(dom)
            todo.append(p)
    print(f"{len(places)} places → {len(todo)} unique new domains to check")

    confirmed, contacts, reasons = [], [], {}
    with ThreadPoolExecutor(max_workers=16) as pool:
        for fut in as_completed([pool.submit(process, p) for p in todo]):
            res = fut.result()
            if res["reject"]:
                reasons[res["reject"]] = reasons.get(res["reject"], 0) + 1
                continue
            p = res["place"]
            for r in res["rows"]:
                if r["email"] in ex_emails:
                    continue
                row = {"business_name": p.get("title", ""), "owner_first_name": r["first"],
                       "website": res["site"], "owner_email": r["email"],
                       "city": p.get("city", ""), "state": p.get("state", ""), "match": r["match"],
                       "evidence": r["evidence"], "reviews": p.get("reviewsCount", ""),
                       "rating": p.get("totalScore", ""), "metro": p.get("_metro", "")}
                (confirmed if r["match"] == "owner_confirmed" else contacts).append(row)

    # one owner row per business; keep the full contact list separately
    by_biz = {}
    for row in confirmed:
        by_biz.setdefault(domain_of(row["website"]), row)
    confirmed = list(by_biz.values())

    if args.verify:
        for rows in (confirmed, contacts):
            for row in rows:
                row["verify"] = verify(row["owner_email"])
        confirmed = [r for r in confirmed if r["verify"] == "ok"]
        contacts = [r for r in contacts if r["verify"] == "ok"]

    confirmed = confirmed[: args.target]
    cols = ["business_name", "owner_first_name", "website", "owner_email", "city", "state",
            "match", "evidence", "reviews", "rating", "metro"] + (["verify"] if args.verify else [])
    out = os.path.expanduser(args.out)
    for path, rows in ((out, confirmed), (os.path.splitext(out)[0] + "_named_contacts.csv", contacts)):
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)

    print(f"\nowner_confirmed: {len(confirmed)} → {out}")
    print(f"named_contact (not confirmed owner): {len(contacts)}")
    print("rejections:", json.dumps(dict(sorted(reasons.items(), key=lambda kv: -kv[1]))))
    if len(confirmed) < args.target:
        print(f"Short of {args.target}. Add a metro or raise --per-term; re-use the saved scrape with --places-json.")


if __name__ == "__main__":
    main()
