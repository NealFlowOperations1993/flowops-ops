#!/usr/bin/env python3
"""V3: SEQUENTIAL personalization. ~17 min for 1,000 leads. Survives Anthropic rate limits."""
import json, time, urllib.request, urllib.error
import os

API_KEY = os.environ["SMARTLEAD_API_KEY"]
ANTHROPIC_KEY = os.environ["ANTHROPIC_API_KEY"]
SL_BASE = "https://server.smartlead.ai/api/v1"
UA = "Mozilla/5.0"

NICHE_MAGNETS = {
    'FINANCIAL': {'name':'Local Google Search Audit','offer':'A 1-page PDF showing the 7 advisors who appear before them when someone Googles "financial advisor" in their city, plus 3 specific fixes to move into the top 5 results. 24h.'},
    'WEALTH':    {'name':'HNW Trigger-Event Watchlist','offer':'A ranked list of 25 people in their 50-mile radius who recently became liquid (M&A exits, IPO, real estate sales, executive departures). 24h.'},
    'MORTGAGE':  {'name':'Refi-Ready Database Reactivation','offer':'They send their dead-lead list. We return 50 borrowers who would save $400+/mo refinancing right now, with personalized SMS scripts. 24h.'},
    'COMMERCIAL_LOAN':{'name':'SBA-Ready Prospect Scoring','offer':'A 1-page PDF of 100 businesses in their state with new filings + UCC liens + DBA changes, scored by SBA-fundability. 24h.'},
    'MCA':       {'name':'Clean-Sheet Merchant Pipeline','offer':'75 first-position-only merchants in their state who funded in the last 30 days (no stacks). 24h.'},
}
QUOTA = [("FINANCIAL",3191292,600),("MORTGAGE",3191290,300),("MCA",3263732,65),("WEALTH",3263730,22),("COMMERCIAL_LOAN",3263731,10)]

SYS = """You write personalized cold email variables for Neal Thakkar at FlowOperations.
Generate 9 vars (3 emails x opener/pain/cta) that REINFORCE the niche_magnet_offer in the user message. Never invent a different deliverable.
TONE: Raw, founder-to-founder. Short sentences. NO em-dashes. NO emojis. NO marketing jargon (SERP, schema, conversion rate, funnel, ICP, LTV, optimize, leverage, scalable). NO "hope this finds you well", "I came across", "I'd love to", "circle back".
FORBIDDEN: "no pitch after"/"no follow-up"/"no strings"/"I won't email again" — never write them.
FORBIDDEN: inventing THEIR specific traffic numbers, dollar amounts, competitor names, cities you don't have data on.
OK: industry-wide stats, niche patterns, real lead context.
OUTPUT: ONLY a JSON object: email1_opener, email1_pain, email1_cta, email2_opener, email2_pain, email2_cta, email3_opener, email3_pain, email3_cta. 1-2 sentences each."""

def http(url):
    r = urllib.request.Request(url, headers={"User-Agent":UA,"Accept":"application/json"})
    with urllib.request.urlopen(r, timeout=30) as resp: return json.loads(resp.read().decode())

def call_anthropic(body, retries=4):
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
                wait = 5 + (10 * attempt)
                time.sleep(wait)
                continue
            return None
        except Exception:
            time.sleep(2)
    return None

def patch(lead_id, cf):
    url = f"{SL_BASE}/leads/{lead_id}?api_key={API_KEY}"
    r = urllib.request.Request(url, data=json.dumps({"lead_input":{"custom_fields":cf}}).encode(),
        headers={"Content-Type":"application/json","User-Agent":UA}, method="POST")
    try:
        with urllib.request.urlopen(r, timeout=30) as resp: return resp.status
    except urllib.error.HTTPError as e: return e.code

def get_unpers(cid, limit):
    leads, off = [], 0
    while len(leads) < limit:
        d = http(f"{SL_BASE}/campaigns/{cid}/leads?api_key={API_KEY}&limit=100&offset={off}")
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
                "lead_id": inner.get("id") or l.get("id"), "email": em,
                "first_name": inner.get("first_name") or "", "last_name": inner.get("last_name") or "",
                "company_name": inner.get("company_name") or "",
                "city": cf.get("city","") or (loc.split(",")[0].strip() if "," in loc else ""),
                "state": cf.get("state","") or (loc.split(",")[-1].strip() if "," in loc else ""),
                "website": inner.get("website") or "", "existing_cf": cf,
            })
            if len(leads) >= limit: break
        if len(items) < 100: break
        off += 100
    return leads

print("Pulling unpersonalized leads...")
all_jobs = []
for niche, cid, q in QUOTA:
    leads = get_unpers(cid, q)
    print(f"  {niche}: {len(leads)}")
    for lead in leads: all_jobs.append((lead, niche))
print(f"\nTotal: {len(all_jobs)} leads. ETA: ~{len(all_jobs) * 1.5 / 60:.0f} min sequential\n")

ok = fail = 0
start = time.time()
for i, (lead, niche) in enumerate(all_jobs, 1):
    magnet = NICHE_MAGNETS[niche]
    body = {"model":"claude-haiku-4-5-20251001","max_tokens":1500,"temperature":0.7,
        "system":[{"type":"text","text":SYS,"cache_control":{"type":"ephemeral"}}],
        "messages":[{"role":"user","content":json.dumps({**lead,"niche":niche,"niche_magnet_name":magnet["name"],"niche_magnet_offer":magnet["offer"]})}]}
    resp = call_anthropic(body)
    if not resp:
        fail += 1
        if i % 25 == 0:
            elapsed = (time.time()-start)/60
            print(f"  {i}/{len(all_jobs)}  ok={ok}  fail={fail}  {elapsed:.1f}min")
        time.sleep(0.5)
        continue
    text = resp["content"][0]["text"].strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"): text = text[4:]
        text = text.split("```")[0]
    try:
        p = json.loads(text.strip())
    except:
        fail += 1
        continue
    new_cf = dict(lead["existing_cf"])
    new_cf.update({
        "personalized_opener":p.get("email1_opener",""),"personalized_pain":p.get("email1_pain",""),"personalized_cta":p.get("email1_cta",""),
        "personalized_opener_2":p.get("email2_opener",""),"personalized_pain_2":p.get("email2_pain",""),"personalized_cta_2":p.get("email2_cta",""),
        "personalized_opener_3":p.get("email3_opener",""),"personalized_pain_3":p.get("email3_pain",""),"personalized_cta_3":p.get("email3_cta",""),
    })
    new_cf.setdefault("niche", niche)
    new_cf.setdefault("source", "single_pass_seq_2026-05-07")
    s = patch(lead["lead_id"], new_cf)
    if s in (200, 204): ok += 1
    else: fail += 1
    if i % 25 == 0:
        elapsed = (time.time()-start)/60
        eta = (len(all_jobs)-i) * (elapsed/i)
        print(f"  {i}/{len(all_jobs)}  ok={ok}  fail={fail}  elapsed={elapsed:.1f}min  ETA={eta:.1f}min")
    time.sleep(1.0)  # 1 req/sec → 60/min, safe under most rate limits

print(f"\n══ DONE  {ok}/{len(all_jobs)} personalized in {(time.time()-start)/60:.1f}min ══")
