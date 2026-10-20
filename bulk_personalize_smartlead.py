#!/usr/bin/env python3
"""
Single-pass personalization for existing Smartlead leads.
Pulls leads with empty personalized_opener, runs Haiku per lead with niche-magnet
context, PATCHes custom_fields back to Smartlead.

Cost: ~$0.001/lead. 1,000 leads = ~$1.
Time: ~3-5 min parallelized.
"""
import json
import sys
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import os

API_KEY = os.environ["SMARTLEAD_API_KEY"]
ANTHROPIC_KEY = os.environ["ANTHROPIC_API_KEY"]
SL_BASE = "https://server.smartlead.ai/api/v1"
UA = "Mozilla/5.0"

# Same map as Pipeline (must stay in sync)
NICHE_MAGNETS = {
    'FINANCIAL': {
        'name': 'Local Google Search Audit',
        'offer': 'A 1-page PDF showing the 7 advisors who appear before them when someone Googles "financial advisor" in their city, plus 3 specific fixes to move into the top 5 results. 24h turnaround.'
    },
    'WEALTH': {
        'name': 'HNW Trigger-Event Watchlist',
        'offer': 'A ranked list of 25 people in their 50-mile radius who recently became liquid (M&A exits, IPO, real estate sales, executive departures), with 1 connection paths to their firm. 24h.'
    },
    'MORTGAGE': {
        'name': 'Refi-Ready Database Reactivation',
        'offer': 'They send their 24-month dead-lead list. We run it against today rates and return the 50 borrowers who would save $400+/mo refinancing right now, with personalized SMS scripts. 24h.'
    },
    'COMMERCIAL_LOAN': {
        'name': 'SBA-Ready Prospect Scoring',
        'offer': 'A 1-page PDF of 100 businesses in their state with new filings + UCC liens + DBA changes, scored by SBA-fundability and ranked by funding hook. 24h.'
    },
    'MCA': {
        'name': 'Clean-Sheet Merchant Pipeline',
        'offer': '75 first-position-only merchants in their state who funded in the last 30 days (no stacks), cross-referenced to their target industries, with predicted renewal-window timing. 24h.'
    },
}

# Distribution: 1,000 leads total, weighted by volume
QUOTA_PER_NICHE = {
    "FINANCIAL":       (3191292, 600),
    "MORTGAGE":        (3191290, 300),
    "MCA":             (3263732, 65),
    "WEALTH":          (3263730, 22),
    "COMMERCIAL_LOAN": (3263731, 10),
    "PI_LAW":          (3327115, 200),
    "MEDSPA":          (3191285, 200),
    "INSURANCE":       (3191291, 100),
}

SYS_PROMPT = """You write personalized cold email variables for Neal Thakkar at FlowOperations.

CONTEXT: This recipient is being sent a sequence with a SPECIFIC reverse-lead-magnet offer for their niche.
Your job: generate 9 vars (3 emails x 3 fields) that REINFORCE that specific offer. Never invent a different deliverable.

The user message will include `niche_magnet_offer` — the EXACT free deliverable we're promising them.
Your personalized_cta MUST point to THAT deliverable (not an AI audit, not a discovery call, not a generic offer).

TONE RULES (NON-NEGOTIABLE):
- Raw, founder-to-founder. Short sentences.
- No "hope this finds you well", "I came across", "I'd love to", "circle back".
- No em-dashes. Use periods or commas.
- No marketing jargon (SERP, schema, conversion rate, funnel, ICP, LTV, CAC, optimize, leverage, scalable).
- No emojis.

FORBIDDEN PROMISES (these are lies, never write them):
- "no pitch after" / "no follow-up" / "no strings" / "I won't email again"

FORBIDDEN: FAKE-SPECIFIC CLAIMS (no inventing data we don't have):
- Don't invent THEIR traffic numbers, conversion rates, dollar amounts.
- Don't name specific competitors or cities you don't have data on.
- Don't claim "I saw you posted about X" unless you have signal data.
OK to use: industry-wide stats, niche patterns, real data from their lead context.

OUTPUT: Return ONLY a JSON object with these 9 keys (no markdown, no prose):
  email1_opener, email1_pain, email1_cta,
  email2_opener, email2_pain, email2_cta,
  email3_opener, email3_pain, email3_cta.
Each field 1-2 sentences max."""

def http_get(url):
    r = urllib.request.Request(url, headers={"User-Agent":UA, "Accept":"application/json"})
    with urllib.request.urlopen(r, timeout=30) as resp:
        return json.loads(resp.read().decode())

def http_post_anthropic(body):
    r = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode(),
        headers={"x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(r, timeout=60) as resp:
        return json.loads(resp.read().decode())

def smartlead_patch_lead(lead_id, custom_fields):
    """Update a lead's custom_fields in Smartlead."""
    url = f"{SL_BASE}/leads/{lead_id}?api_key={API_KEY}"
    body = {"lead_input": {"custom_fields": custom_fields}}
    r = urllib.request.Request(url, data=json.dumps(body).encode(),
        headers={"Content-Type":"application/json","User-Agent":UA}, method="POST")
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            return resp.status, resp.read().decode()[:120]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:200]

def get_unpersonalized_leads(cid, limit):
    """Pull leads from a campaign with empty personalized_opener."""
    leads = []
    offset = 0
    while len(leads) < limit:
        d = http_get(f"{SL_BASE}/campaigns/{cid}/leads?api_key={API_KEY}&limit=100&offset={offset}")
        items = d.get("data") if isinstance(d, dict) else d
        if not items: break
        for l in items:
            inner = l.get("lead") if isinstance(l.get("lead"), dict) else l
            cf = inner.get("custom_fields") or {}
            if isinstance(cf, str):
                try: cf = json.loads(cf)
                except: cf = {}
            if cf.get("personalized_opener"):
                continue  # already personalized
            email = (inner.get("email") or "").lower()
            if "brutus_smoke" in email or email == "neal@flowoperations.ai":
                continue
            leads.append({
                "lead_id": inner.get("id") or l.get("id"),
                "email": email,
                "first_name": inner.get("first_name") or "",
                "last_name": inner.get("last_name") or "",
                "company_name": inner.get("company_name") or "",
                "city": cf.get("city","") or (inner.get("location","").split(",")[0].strip() if "," in (inner.get("location") or "") else ""),
                "state": cf.get("state","") or (inner.get("location","").split(",")[-1].strip() if "," in (inner.get("location") or "") else ""),
                "website": inner.get("website") or "",
                "existing_cf": cf,
            })
            if len(leads) >= limit: break
        if len(items) < 100: break
        offset += 100
        time.sleep(0.2)
    return leads

def personalize_one(lead, niche):
    magnet = NICHE_MAGNETS[niche]
    user = json.dumps({
        "company_name": lead["company_name"],
        "city": lead["city"],
        "state": lead["state"],
        "niche": niche,
        "website": lead["website"],
        "niche_magnet_name": magnet["name"],
        "niche_magnet_offer": magnet["offer"],
    })
    body = {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 1500,
        "temperature": 0.7,
        "system": [{"type":"text","text":SYS_PROMPT,"cache_control":{"type":"ephemeral"}}],
        "messages": [{"role":"user","content":user}]
    }
    try:
        resp = http_post_anthropic(body)
        text = resp["content"][0]["text"].strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"): text = text[4:]
            text = text.split("```")[0]
        text = text.strip()
        return json.loads(text)
    except Exception as e:
        return {"_error": str(e)[:120]}

def process_lead(lead, niche):
    pers = personalize_one(lead, niche)
    if pers.get("_error"):
        return {"lead": lead, "ok": False, "err": pers["_error"]}

    # NEW: also fetch FlowScore for this lead via the real API
    fs_fields = {"personalized_flowscore":"","flowscore_meaning":"","flowscore_leak":"","flowscore_weak":""}
    try:
        from core.flowscore import score as fs_score, extract_for_email
        website = lead.get("website") or lead["existing_cf"].get("website") or ""
        if website:
            raw = fs_score(website, niche)
            if not raw.get("error"):
                ext = extract_for_email(raw)
                fs_fields["personalized_flowscore"] = ext.get("flowscore","")
                fs_fields["flowscore_meaning"]     = ext.get("flowscore_meaning","")
                fs_fields["flowscore_leak"]        = ext.get("flowscore_leak","")
                fs_fields["flowscore_weak"]        = ext.get("flowscore_weak","")
    except Exception as e:
        pass  # FlowScore is best-effort — don't block personalization

    # Merge everything into custom_fields, preserving city/state/source/niche
    new_cf = dict(lead["existing_cf"])
    new_cf.update({
        "personalized_opener":   pers.get("email1_opener",""),
        "personalized_pain":     pers.get("email1_pain",""),
        "personalized_cta":      pers.get("email1_cta",""),
        "personalized_opener_2": pers.get("email2_opener",""),
        "personalized_pain_2":   pers.get("email2_pain",""),
        "personalized_cta_2":    pers.get("email2_cta",""),
        "personalized_opener_3": pers.get("email3_opener",""),
        "personalized_pain_3":   pers.get("email3_pain",""),
        "personalized_cta_3":    pers.get("email3_cta",""),
        **fs_fields,  # FlowScore fields
    })
    if not new_cf.get("niche"): new_cf["niche"] = niche
    if not new_cf.get("source"): new_cf["source"] = "single_pass_2026-05-07"
    status, resp = smartlead_patch_lead(lead["lead_id"], new_cf)
    return {"lead": lead, "ok": status in (200, 204), "status": status, "err": resp[:80] if status not in (200,204) else None}

# Main
print("═" * 70)
print("BULK PERSONALIZATION — single-pass Haiku, ~$1 total, ~5 min")
print("═" * 70)

all_jobs = []
for niche, (cid, quota) in QUOTA_PER_NICHE.items():
    print(f"\n[{niche} cid {cid}] pulling up to {quota} unpersonalized leads...")
    leads = get_unpersonalized_leads(cid, quota)
    print(f"  Got {len(leads)}")
    for lead in leads:
        all_jobs.append((lead, niche))

print(f"\n→ Total to personalize: {len(all_jobs)}")
if not all_jobs:
    print("Nothing to do.")
    sys.exit(0)

print("\nPersonalizing in parallel (max 10 concurrent)...")
ok_count = 0
fail_count = 0
sample_outputs = []
with ThreadPoolExecutor(max_workers=10) as pool:
    futures = [pool.submit(process_lead, lead, niche) for lead, niche in all_jobs]
    for i, fut in enumerate(as_completed(futures), 1):
        result = fut.result()
        if result["ok"]:
            ok_count += 1
        else:
            fail_count += 1
            if fail_count <= 5:
                print(f"  FAIL: {result['lead']['email']} — {result.get('err','?')[:100]}")
        if i % 50 == 0:
            print(f"  ...{i}/{len(all_jobs)} done ({ok_count} ok, {fail_count} fail)")

print()
print("═" * 70)
print(f"DONE. Personalized {ok_count}/{len(all_jobs)} leads")
print(f"      Failures: {fail_count}")
print("═" * 70)
