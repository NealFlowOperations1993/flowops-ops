#!/usr/bin/env python3
"""
Personalize PI_LAW + MEDSPA + INSURANCE leads via OpenRouter Gemini Flash (cheap).
~$0.0001 / lead. Targeted at the fresh seed batch.

Uses OpenRouter (~13x cheaper than Anthropic direct):
- Gemini 2.0 Flash:  $0.075 / M input, $0.30 / M output
- Anthropic Haiku:    $1.00 / M input, $5.00 / M output
"""
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

SL_KEY = os.environ["SMARTLEAD_API_KEY"]
SL = "https://server.smartlead.ai/api/v1"
UA = "Mozilla/5.0"

OR_KEY = os.environ["OPENROUTER_API_KEY"]
OR_URL = "https://openrouter.ai/api/v1/chat/completions"

TARGETS = {
    "PI_LAW":     {"cid": 3327115, "label": "personal injury law firm",
                   "magnet": "free 20-min AI Audit + custom implementation plan"},
    "MEDSPA":     {"cid": 3191285, "label": "med spa",
                   "magnet": "free 20-min AI Audit + custom implementation plan"},
    "INSURANCE":  {"cid": 3191291, "label": "insurance agency",
                   "magnet": "free 20-min AI Audit + custom implementation plan"},
    "FINANCIAL":  {"cid": 3191292, "label": "financial advisor",
                   "magnet": "free 20-min AI Audit + custom implementation plan"},
    "MCA":        {"cid": 3263732, "label": "MCA broker",
                   "magnet": "free 20-min AI Audit + custom implementation plan"},
    "COMMLOAN":   {"cid": 3263731, "label": "commercial loan broker",
                   "magnet": "free 20-min AI Audit + custom implementation plan"},
    "MORTGAGE":   {"cid": 3191290, "label": "mortgage broker",
                   "magnet": "free 20-min AI Audit + custom implementation plan"},
}

SYS = """You write personalized cold email VARIABLES for Neal Thakkar at FlowOperations.

Output JSON ONLY with exactly these 9 keys (no extras, no commentary):
{
  "email1_opener": "string (1-2 sentences, signal-led, NO 'I hope this email finds you well')",
  "email1_pain":   "string (1 sentence, niche-specific pain)",
  "email1_cta":    "string (1 sentence soft reply ask)",
  "email2_opener": "string",
  "email2_pain":   "string",
  "email2_cta":    "string",
  "email3_opener": "string",
  "email3_pain":   "string",
  "email3_cta":    "string"
}

VOICE RULES:
- Direct, founder-to-founder. No filler.
- Cite something specific about the prospect's business when possible (city, name shape).
- Never invent data. If you don't know the prospect, lead with their city or niche.
- Length: openers under 25 words. Pain under 20. CTA under 15.
- No em-dashes. No marketing words ("synergy", "leverage", "circle back").
- Don't promise generic things — the CTA must invite a REPLY, not a click."""


def http_post(url, body, headers, timeout=45):
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
        headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {"_error": True, "code": e.code, "body": e.read().decode()[:300]}
    except Exception as e:
        return {"_error": True, "msg": str(e)[:300]}


def call_or(system, user, retries=2):
    body = {
        "model": "google/gemini-2.5-flash-lite",
        "max_tokens": 600,
        "temperature": 0.7,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
    }
    headers = {
        "Authorization": f"Bearer {OR_KEY}",
        "Content-Type":  "application/json",
    }
    for attempt in range(retries + 1):
        r = http_post(OR_URL, body, headers, timeout=60)
        if r.get("_error"):
            time.sleep(1.5 ** attempt)
            continue
        try:
            return r["choices"][0]["message"]["content"]
        except Exception:
            time.sleep(1.5 ** attempt)
    return None


def parse_json(text):
    if not text: return None
    t = text.strip()
    # strip code fences
    t = re.sub(r"^```(?:json)?\s*", "", t)
    t = re.sub(r"\s*```\s*$", "", t)
    try:
        return json.loads(t)
    except Exception:
        # Sometimes there's prose before/after. Find first {...}
        m = re.search(r"\{[\s\S]*\}", t)
        if m:
            try: return json.loads(m.group(0))
            except: return None
        return None


def get_unpersonalized(cid, limit=1500):
    leads = []
    offset = 0
    while len(leads) < limit:
        url = f"{SL}/campaigns/{cid}/leads?limit=100&offset={offset}&api_key={SL_KEY}"
        try:
            r = urllib.request.Request(url, headers={"User-Agent": UA})
            d = json.loads(urllib.request.urlopen(r, timeout=20).read())
        except Exception as e:
            print(f"  fetch err {e}", flush=True)
            break
        items = d.get("data", [])
        if not items: break
        for it in items:
            inner = it.get("lead") if isinstance(it.get("lead"), dict) else it
            cf = inner.get("custom_fields") or {}
            if isinstance(cf, str):
                try: cf = json.loads(cf)
                except: cf = {}
            if cf.get("personalized_opener"): continue
            email = (inner.get("email") or "").lower()
            if not email or "@" not in email: continue
            leads.append({
                "lead_id":    inner.get("id") or it.get("id"),
                "email":      email,
                "first_name": inner.get("first_name") or "",
                "company":    inner.get("company_name") or "",
                "city":       cf.get("city","") or "",
                "website":    inner.get("website") or "",
                "existing_cf": cf,
            })
            if len(leads) >= limit: break
        if len(items) < 100: break
        offset += 100
    return leads


def patch_lead(cid, lead_id, email, custom_fields):
    """Smartlead requires campaign-scoped lead updates."""
    url = f"{SL}/campaigns/{cid}/leads/{lead_id}?api_key={SL_KEY}"
    body = {"email": email, "custom_fields": custom_fields}
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
        headers={"Content-Type":"application/json","User-Agent":UA}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0


def process(lead, niche):
    cfg = TARGETS[niche]
    user = json.dumps({
        "first_name":  lead["first_name"],
        "company":     lead["company"],
        "city":        lead["city"],
        "niche":       cfg["label"],
        "magnet":      cfg["magnet"],
    })
    raw = call_or(SYS, user)
    parsed = parse_json(raw)
    if not parsed:
        return {"ok": False, "email": lead["email"], "err": "parse_fail"}
    new_cf = dict(lead["existing_cf"])
    new_cf.update({
        "personalized_opener":   parsed.get("email1_opener",""),
        "personalized_pain":     parsed.get("email1_pain",""),
        "personalized_cta":      parsed.get("email1_cta",""),
        "personalized_opener_2": parsed.get("email2_opener",""),
        "personalized_pain_2":   parsed.get("email2_pain",""),
        "personalized_cta_2":    parsed.get("email2_cta",""),
        "personalized_opener_3": parsed.get("email3_opener",""),
        "personalized_pain_3":   parsed.get("email3_pain",""),
        "personalized_cta_3":    parsed.get("email3_cta",""),
        "niche": niche,
    })
    status = patch_lead(TARGETS[niche]["cid"], lead["lead_id"], lead["email"], new_cf)
    return {"ok": status in (200, 204), "email": lead["email"], "status": status}


def main():
    from spend_guard import check_spend_or_die
    # Estimate: ~400 leads × ~$0.0002 = ~$0.08
    check_spend_or_die(estimated_cost_usd=0.50, script_name="personalize_new_niches.py")

    jobs = []
    for niche, cfg in TARGETS.items():
        print(f"[{niche}] fetching unpersonalized leads...", flush=True)
        leads = get_unpersonalized(cfg["cid"], limit=1500)
        print(f"  got {len(leads)}", flush=True)
        for l in leads:
            jobs.append((l, niche))

    if not jobs:
        print("Nothing to personalize.", flush=True)
        return

    print(f"\nTotal to personalize: {len(jobs)} (parallel x 10)\n", flush=True)

    ok = err = 0
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(process, l, n): (l, n) for l, n in jobs}
        for i, fut in enumerate(as_completed(futs), 1):
            r = fut.result()
            if r["ok"]:
                ok += 1
                if i % 25 == 0 or i == len(jobs):
                    print(f"  [{i}/{len(jobs)}] ok={ok} err={err}", flush=True)
            else:
                err += 1
                if err <= 5:
                    print(f"  ✗ {r['email']}: {r.get('err') or r.get('status')}", flush=True)

    print(f"\nDONE  ok={ok}  err={err}", flush=True)


if __name__ == "__main__":
    main()
