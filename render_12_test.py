#!/usr/bin/env python3
"""Render 12 test emails for Neal — 2 per niche, Council-personalized, full Day 0 body."""
import sys, os, json, urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path.home() / "Desktop/council"))
from core import council

API_KEY = os.environ["SMARTLEAD_API_KEY"]
BASE = "https://server.smartlead.ai/api/v1"
UA = "Mozilla/5.0"

NICHE_TO_SEQ = {
    "FINANCIAL":       "v2_01_financial_advisor.json",
    "WEALTH":          "v2_02_wealth_manager.json",
    "MORTGAGE":        "v2_03_mortgage_broker.json",
    "COMMERCIAL_LOAN": "v2_05_commercial_loan_broker.json",
    "FUNDING":         "v2_04_funding_consultant.json",
    "MCA":             "v2_06_mca_broker.json",
}

NICHES_TO_PULL = [
    ("FINANCIAL", 3191292),
    ("WEALTH",    3263730),
    ("MORTGAGE",  3191290),
    ("COMMERCIAL_LOAN", 3263731),
    ("FUNDING",   3191291),
    ("MCA",       3263732),
]

def get(url):
    r = urllib.request.Request(url, headers={"User-Agent":UA, "Accept":"application/json"})
    with urllib.request.urlopen(r, timeout=30) as resp:
        return json.loads(resp.read().decode())

def get_leads(cid, n=2):
    """Pull first N real leads from campaign."""
    d = get(f"{BASE}/campaigns/{cid}/leads?api_key={API_KEY}&limit=20")
    items = d.get("data") if isinstance(d, dict) else d
    out = []
    for l in (items or []):
        inner = l.get("lead") if isinstance(l.get("lead"), dict) else l
        em = (inner.get("email") or "").lower()
        if "brutus_smoke" in em or em == "neal@flowoperations.ai": continue
        cf = inner.get("custom_fields") or {}
        if isinstance(cf, str):
            try: cf = json.loads(cf)
            except: cf = {}
        out.append({
            "company_name": inner.get("company_name") or "",
            "first_name": inner.get("first_name") or "",
            "last_name": inner.get("last_name") or "",
            "email": inner.get("email") or "",
            "phone_number": inner.get("phone_number") or "",
            "website": inner.get("website") or "",
            "city": cf.get("city","") or (inner.get("location","").split(",")[0].strip() if "," in (inner.get("location") or "") else ""),
            "state": cf.get("state","") or (inner.get("location","").split(",")[-1].strip() if "," in (inner.get("location") or "") else ""),
            "location": inner.get("location") or "",
        })
        if len(out) >= n: break
    return out

def render(seq_step, p, lead):
    body = seq_step["body"]
    body = body.replace("{{personalized_opener}}", p.get("email1_opener",""))
    body = body.replace("{{personalized_pain}}", p.get("email1_pain",""))
    body = body.replace("{{personalized_cta}}", p.get("email1_cta",""))
    body = body.replace("{{first_name}}", lead.get("first_name") or "there")
    body = body.replace("{{company_name}}", lead.get("company_name","your business"))
    body = body.replace("{{city}}", lead.get("city",""))
    body = body.replace("{{state}}", lead.get("state",""))
    subj = seq_step["subject"]
    for k,v in [("first_name", lead.get("first_name") or "there"),
                ("company_name", lead.get("company_name","your business")),
                ("city", lead.get("city","")),
                ("state", lead.get("state",""))]:
        subj = subj.replace("{{"+k+"}}", v)
    return subj, body

def process_lead(args):
    nc, lead = args
    lead["niche"] = nc
    seq = json.loads(Path(f"/tmp/leads_recovery/sequences/{NICHE_TO_SEQ[nc]}").read_text())
    nctx = {
        "reverse_magnet_name":  seq["reverse_lead_magnet"]["name"],
        "reverse_magnet_offer": seq["reverse_lead_magnet"]["deliverable"],
        "pain_anchor":          seq["stat_anchor"],
    }
    result = council.generate(lead, niche_context=nctx, debug=False)
    subj, body = render(seq["emails"][0], result["final"], lead)
    return {
        "niche": nc, "lead": lead, "subject": subj, "body": body,
        "voice_persona": result["winning_persona_for_voice"],
        "cost": result["cost_usd"],
        "magnet": seq["reverse_lead_magnet"]["name"],
    }

# Gather all leads
print("Pulling 2 leads per niche from Smartlead...")
all_jobs = []
for nc, cid in NICHES_TO_PULL:
    leads = get_leads(cid, n=2)
    for lead in leads:
        all_jobs.append((nc, lead))
print(f"Got {len(all_jobs)} leads to process\n")

# Run Council in parallel
print("Running Council on all 12 leads in parallel (max 6 concurrent)...")
with ThreadPoolExecutor(max_workers=6) as pool:
    futures = [pool.submit(process_lead, j) for j in all_jobs]
    results = []
    for i, fut in enumerate(as_completed(futures), 1):
        r = fut.result()
        results.append(r)
        print(f"  [{i}/{len(all_jobs)}] {r['niche']} — {r['lead']['email']} (${r['cost']})")

# Sort by niche for readability
results.sort(key=lambda r: r["niche"])

print("\n\n")
print("═" * 75)
print("12 RENDERED EMAILS — read each as if you're the recipient")
print("═" * 75)

for i, r in enumerate(results, 1):
    print(f"\n\n{'━'*75}")
    print(f"EMAIL {i}/12  —  NICHE: {r['niche']}  —  Voice: {r['voice_persona']}")
    print(f"Lead: {r['lead'].get('first_name','?')} {r['lead'].get('last_name','')} <{r['lead']['email']}>")
    print(f"      {r['lead']['company_name']} ({r['lead'].get('city','?')}, {r['lead'].get('state','?')})")
    print(f"Magnet: {r['magnet']}")
    print(f"{'━'*75}")
    print(f"\nSUBJECT: {r['subject']}\n")
    print(f"BODY:")
    print(r['body'])

total_cost = sum(r["cost"] for r in results)
print(f"\n\n═══ DONE — total cost ${total_cost:.2f} ═══")
