#!/usr/bin/env python3
"""V5 — Finish the 4 niches that bulk_v4 didn't reach. Smaller scope: ~397 leads."""
import json, time, urllib.request, urllib.error, sys
import os

API_KEY = os.environ["SMARTLEAD_API_KEY"]
ANTHROPIC_KEY = os.environ["ANTHROPIC_API_KEY"]
SL_BASE = "https://server.smartlead.ai/api/v1"
UA = "Mozilla/5.0"

NICHE_MAGNETS = {
    'WEALTH':   {'name':'HNW Trigger-Event Watchlist','offer':'A ranked list of 25 people in their 50-mile radius who recently became liquid (M&A exits, IPO, real estate sales). 24h.'},
    'MORTGAGE': {'name':'Refi-Ready Database Reactivation','offer':'They send their dead-lead list. We return 50 borrowers who would save $400+/mo refinancing. 24h.'},
    'COMMERCIAL_LOAN':{'name':'SBA-Ready Prospect Scoring','offer':'A 1-page PDF of 100 businesses scored by SBA-fundability. 24h.'},
    'MCA':      {'name':'Clean-Sheet Merchant Pipeline','offer':'75 first-position-only merchants who funded recently (no stacks). 24h.'},
}
QUOTA = [("MORTGAGE",3191290,300),("MCA",3263732,65),("WEALTH",3263730,22),("COMMERCIAL_LOAN",3263731,10)]

SYS = """You write personalized cold email variables for Neal Thakkar at FlowOperations.
Generate 9 vars (3 emails x opener/pain/cta) that REINFORCE the niche_magnet_offer.
TONE: Raw, founder-to-founder. Short sentences. NO em-dashes. NO emojis. NO marketing jargon.
NO "hope this finds you well", "I came across", "I'd love to", "circle back".
FORBIDDEN: "no pitch after"/"no follow-up"/"no strings"/"I won't email again".
FORBIDDEN: inventing THEIR specific traffic, dollar amounts, competitor names, cities.
OK: industry-wide stats, niche patterns.
OUTPUT: ONLY a JSON object: email1_opener, email1_pain, email1_cta, email2_opener, email2_pain, email2_cta, email3_opener, email3_pain, email3_cta. 1-2 sentences each."""

def http_get(url, retries=3):
    for i in range(retries):
        try:
            r = urllib.request.Request(url, headers={"User-Agent":UA,"Accept":"application/json"})
            with urllib.request.urlopen(r, timeout=45) as resp: return json.loads(resp.read().decode())
        except Exception:
            time.sleep(3); 
    return None

def call_anthropic(body, retries=3):
    for i in range(retries):
        try:
            r = urllib.request.Request("https://api.anthropic.com/v1/messages",
                data=json.dumps(body).encode(),
                headers={"x-api-key":ANTHROPIC_KEY,"anthropic-version":"2023-06-01","content-type":"application/json"},
                method="POST")
            with urllib.request.urlopen(r, timeout=60) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(8 * (i+1))
            else: time.sleep(3)
        except Exception:
            time.sleep(3)
    return None

def patch_lead(cid, lead_id, email, cf, retries=3):
    url = f"{SL_BASE}/campaigns/{cid}/leads/{lead_id}?api_key={API_KEY}"
    body = {"email": email, "custom_fields": cf}
    for i in range(retries):
        try:
            r = urllib.request.Request(url, data=json.dumps(body).encode(),
                headers={"Content-Type":"application/json","User-Agent":UA}, method="POST")
            with urllib.request.urlopen(r, timeout=30) as resp: return resp.status
        except urllib.error.HTTPError as e: return e.code
        except Exception:
            time.sleep(3)
    return 0

def get_unpers(cid, limit):
    leads, off = [], 0
    while len(leads) < limit:
        d = http_get(f"{SL_BASE}/campaigns/{cid}/leads?api_key={API_KEY}&limit=100&offset={off}")
        if not d: break
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
            leads.append({"lead_id": inner.get("id") or l.get("id"), "email": em,
                "first_name": inner.get("first_name") or "",
                "company_name": inner.get("company_name") or "",
                "city": cf.get("city","") or (loc.split(",")[0].strip() if "," in loc else ""),
                "state": cf.get("state","") or (loc.split(",")[-1].strip() if "," in loc else ""),
                "existing_cf": cf})
            if len(leads) >= limit: break
        if len(items) < 100: break
        off += 100
        time.sleep(0.5)
    return leads

print("Pulling unpersonalized leads from 4 niches...", flush=True)
all_jobs = []
for niche, cid, q in QUOTA:
    leads = get_unpers(cid, q)
    print(f"  {niche}: {len(leads)} pulled", flush=True)
    for lead in leads: all_jobs.append((lead, niche, cid))
print(f"\nTotal: {len(all_jobs)} leads. ETA: ~{len(all_jobs) * 5 / 60:.1f} min sequential.\n", flush=True)

ok = fail = 0
start = time.time()
for i, (lead, niche, cid) in enumerate(all_jobs, 1):
    magnet = NICHE_MAGNETS[niche]
    body = {"model":"claude-haiku-4-5-20251001","max_tokens":1500,"temperature":0.7,
        "system":[{"type":"text","text":SYS,"cache_control":{"type":"ephemeral"}}],
        "messages":[{"role":"user","content":json.dumps({**{k:v for k,v in lead.items() if k not in ('existing_cf','lead_id')}, "niche":niche,"niche_magnet_name":magnet["name"],"niche_magnet_offer":magnet["offer"]})}]}
    
    resp = call_anthropic(body)
    if not resp:
        fail += 1
        time.sleep(0.5)
        continue
    try:
        text = resp["content"][0]["text"].strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"): text = text[4:]
            text = text.split("```")[0]
        p = json.loads(text.strip())
    except Exception:
        fail += 1
        continue
    
    new_cf = dict(lead["existing_cf"])
    new_cf.update({
        "personalized_opener":p.get("email1_opener",""),"personalized_pain":p.get("email1_pain",""),"personalized_cta":p.get("email1_cta",""),
        "personalized_opener_2":p.get("email2_opener",""),"personalized_pain_2":p.get("email2_pain",""),"personalized_cta_2":p.get("email2_cta",""),
        "personalized_opener_3":p.get("email3_opener",""),"personalized_pain_3":p.get("email3_pain",""),"personalized_cta_3":p.get("email3_cta",""),
    })
    new_cf.setdefault("niche", niche)
    new_cf.setdefault("source", "single_pass_v5_2026-05-07")
    
    s = patch_lead(cid, lead["lead_id"], lead["email"], new_cf)
    if s in (200, 204): ok += 1
    else: fail += 1
    
    if i % 25 == 0 or i == len(all_jobs):
        elapsed = (time.time()-start)/60
        eta = (len(all_jobs)-i) * elapsed / max(i,1)
        print(f"  {i}/{len(all_jobs)}  ok={ok} fail={fail}  {elapsed:.1f}min  ETA={eta:.1f}min", flush=True)
    time.sleep(0.6)

print(f"\n══ DONE  {ok}/{len(all_jobs)} personalized in {(time.time()-start)/60:.1f}min ══", flush=True)
