#!/usr/bin/env python3
"""V2: rate-limited + retries on 429. Captures first 12 for display."""
import json, sys, time, urllib.request, urllib.error, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

API_KEY = os.environ["SMARTLEAD_API_KEY"]
ANTHROPIC_KEY = os.environ["ANTHROPIC_API_KEY"]
SL_BASE = "https://server.smartlead.ai/api/v1"
UA = "Mozilla/5.0"

NICHE_MAGNETS = {
    'FINANCIAL': {'name': 'Local Google Search Audit', 'offer': 'A 1-page PDF showing the 7 advisors who appear before them when someone Googles "financial advisor" in their city, plus 3 specific fixes to move into the top 5 results. 24h turnaround.'},
    'WEALTH':    {'name': 'HNW Trigger-Event Watchlist', 'offer': 'A ranked list of 25 people in their 50-mile radius who recently became liquid (M&A exits, IPO, real estate sales, executive departures), with 1 connection paths to their firm. 24h.'},
    'MORTGAGE':  {'name': 'Refi-Ready Database Reactivation', 'offer': 'They send their 24-month dead-lead list. We run it against today rates and return the 50 borrowers who would save $400+/mo refinancing right now, with personalized SMS scripts. 24h.'},
    'COMMERCIAL_LOAN': {'name': 'SBA-Ready Prospect Scoring', 'offer': 'A 1-page PDF of 100 businesses in their state with new filings + UCC liens + DBA changes, scored by SBA-fundability. 24h.'},
    'MCA':       {'name': 'Clean-Sheet Merchant Pipeline', 'offer': '75 first-position-only merchants in their state who funded in the last 30 days (no stacks), with predicted renewal-window timing. 24h.'},
}

QUOTA = [("FINANCIAL",3191292,600),("MORTGAGE",3191290,300),("MCA",3263732,65),("WEALTH",3263730,22),("COMMERCIAL_LOAN",3263731,10)]

SYS_PROMPT = """You write personalized cold email variables for Neal Thakkar at FlowOperations.
Generate 9 vars (3 emails x opener/pain/cta) that REINFORCE the niche_magnet_offer in the user message. Never invent a different deliverable.
TONE: Raw, founder-to-founder. Short sentences. NO em-dashes. NO emojis. NO marketing jargon (SERP, schema, conversion rate, funnel, ICP, LTV, optimize, leverage, scalable). NO "hope this finds you well", "I came across", "I'd love to", "circle back".
FORBIDDEN: "no pitch after", "no follow-up", "no strings", "I won't email again" — these are lies, never write them.
FORBIDDEN: inventing THEIR specific traffic numbers, dollar amounts, competitor names, cities you don't have data on.
OK: industry-wide stats, niche patterns, real data from lead context.
OUTPUT: ONLY a JSON object with these 9 keys (no markdown):
  email1_opener, email1_pain, email1_cta, email2_opener, email2_pain, email2_cta, email3_opener, email3_pain, email3_cta. 1-2 sentences each."""

def http_get(url):
    r = urllib.request.Request(url, headers={"User-Agent":UA, "Accept":"application/json"})
    with urllib.request.urlopen(r, timeout=30) as resp: return json.loads(resp.read().decode())

def http_post_anthropic(body, retries=3):
    for attempt in range(retries):
        try:
            r = urllib.request.Request("https://api.anthropic.com/v1/messages",
                data=json.dumps(body).encode(),
                headers={"x-api-key":ANTHROPIC_KEY,"anthropic-version":"2023-06-01","content-type":"application/json"},
                method="POST")
            with urllib.request.urlopen(r, timeout=60) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 5 * (2 ** attempt)
                time.sleep(wait)
                continue
            raise
    return {"_error": "rate_limit_exhausted"}

def smartlead_patch(lead_id, cf):
    url = f"{SL_BASE}/leads/{lead_id}?api_key={API_KEY}"
    body = {"lead_input": {"custom_fields": cf}}
    r = urllib.request.Request(url, data=json.dumps(body).encode(),
        headers={"Content-Type":"application/json","User-Agent":UA}, method="POST")
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code

def get_unpersonalized(cid, limit):
    leads, off = [], 0
    while len(leads) < limit:
        d = http_get(f"{SL_BASE}/campaigns/{cid}/leads?api_key={API_KEY}&limit=100&offset={off}")
        items = d.get("data") if isinstance(d, dict) else d
        if not items: break
        for l in items:
            inner = l.get("lead") if isinstance(l.get("lead"), dict) else l
            cf = inner.get("custom_fields") or {}
            if isinstance(cf, str):
                try: cf = json.loads(cf)
                except: cf = {}
            if cf.get("personalized_opener"): continue
            em = (inner.get("email") or "").lower()
            if "brutus_smoke" in em or em == "neal@flowoperations.ai": continue
            loc = inner.get("location") or ""
            leads.append({
                "lead_id": inner.get("id") or l.get("id"),
                "email": em, "first_name": inner.get("first_name") or "",
                "last_name": inner.get("last_name") or "",
                "company_name": inner.get("company_name") or "",
                "city": cf.get("city","") or (loc.split(",")[0].strip() if "," in loc else ""),
                "state": cf.get("state","") or (loc.split(",")[-1].strip() if "," in loc else ""),
                "website": inner.get("website") or "", "existing_cf": cf,
            })
            if len(leads) >= limit: break
        if len(items) < 100: break
        off += 100
        time.sleep(0.3)
    return leads

def personalize(lead, niche):
    magnet = NICHE_MAGNETS[niche]
    body = {
        "model":"claude-haiku-4-5-20251001","max_tokens":1500,"temperature":0.7,
        "system":[{"type":"text","text":SYS_PROMPT,"cache_control":{"type":"ephemeral"}}],
        "messages":[{"role":"user","content":json.dumps({
            "company_name":lead["company_name"],"city":lead["city"],"state":lead["state"],
            "niche":niche,"website":lead["website"],
            "niche_magnet_name":magnet["name"],"niche_magnet_offer":magnet["offer"],
        })}]
    }
    resp = http_post_anthropic(body)
    if resp.get("_error"): return None
    text = resp["content"][0]["text"].strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"): text = text[4:]
        text = text.split("```")[0]
    try: return json.loads(text.strip())
    except: return None

samples_lock = threading.Lock()
samples = []

def process(lead, niche):
    p = personalize(lead, niche)
    if not p: return {"ok": False}
    new_cf = dict(lead["existing_cf"])
    new_cf.update({
        "personalized_opener":p.get("email1_opener",""),"personalized_pain":p.get("email1_pain",""),"personalized_cta":p.get("email1_cta",""),
        "personalized_opener_2":p.get("email2_opener",""),"personalized_pain_2":p.get("email2_pain",""),"personalized_cta_2":p.get("email2_cta",""),
        "personalized_opener_3":p.get("email3_opener",""),"personalized_pain_3":p.get("email3_pain",""),"personalized_cta_3":p.get("email3_cta",""),
    })
    new_cf.setdefault("niche", niche)
    new_cf.setdefault("source", "single_pass_2026-05-07")
    status = smartlead_patch(lead["lead_id"], new_cf)
    ok = status in (200, 204)
    if ok:
        with samples_lock:
            if len(samples) < 12 and lead["company_name"]:
                samples.append({"niche":niche,"lead":lead,"pers":p})
    return {"ok": ok, "status": status}

print("Pulling unpersonalized leads...")
all_jobs = []
for niche, cid, q in QUOTA:
    leads = get_unpersonalized(cid, q)
    print(f"  {niche}: {len(leads)}")
    for lead in leads: all_jobs.append((lead, niche))
print(f"\nTotal: {len(all_jobs)} leads to personalize\n")

print("Running with 4 workers + 429 retries...")
ok_count = fail_count = 0
with ThreadPoolExecutor(max_workers=4) as pool:
    futures = [pool.submit(process, lead, niche) for lead, niche in all_jobs]
    for i, fut in enumerate(as_completed(futures), 1):
        r = fut.result()
        if r["ok"]: ok_count += 1
        else: fail_count += 1
        if i % 50 == 0:
            print(f"  {i}/{len(all_jobs)}  ok={ok_count}  fail={fail_count}")

print(f"\n══ DONE  {ok_count}/{len(all_jobs)} personalized  ({fail_count} failed) ══")

# Save samples for display
import pathlib
pathlib.Path("/tmp/leads_recovery/12_samples.json").write_text(json.dumps(samples, indent=2))
print(f"\n12 samples saved to /tmp/leads_recovery/12_samples.json")
