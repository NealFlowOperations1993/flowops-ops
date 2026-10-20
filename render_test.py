#!/usr/bin/env python3
"""
Pull 5 real leads from Smartlead (one per niche), run each through Council
with niche-aware reverse-magnet context, render the full Day 0 email by
substituting vars into the sequence body. Output for Neal's review.
"""
import sys, os, json, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from core import council

API_KEY = os.environ["SMARTLEAD_API_KEY"]
BASE = "https://server.smartlead.ai/api/v1"
UA = "Mozilla/5.0"

# Niches to test (one per niche, drawing from existing leads in campaigns)
TEST_NICHES = [
    {"niche_code": "FINANCIAL", "campaign_id": 3191292, "search": "financial advisor"},
    {"niche_code": "MORTGAGE",  "campaign_id": 3191290, "search": "mortgage broker"},
    {"niche_code": "MCA",       "campaign_id": 3263732, "search": "merchant cash advance"},
    {"niche_code": "MEDSPA",    "campaign_id": 3191285, "search": "med spa"},
    {"niche_code": "FUNDING",   "campaign_id": 3191291, "search": "business funding consultant"},
]

# Map niche_code -> sequence file (for reverse magnet + body template)
NICHE_TO_SEQ = {
    "FINANCIAL":       "v2_01_financial_advisor.json",
    "WEALTH":          "v2_02_wealth_manager.json",
    "MORTGAGE":        "v2_03_mortgage_broker.json",
    "COMMERCIAL_LOAN": "v2_05_commercial_loan_broker.json",
    "FUNDING":         "v2_04_funding_consultant.json",
    "MCA":             "v2_06_mca_broker.json",
    "AGENCY":          "v2_07_smma_agency.json",
    "MEDSPA":          "v2_08_med_spa.json",
    "PI_LAW":          "v2_09_pi_attorney.json",
    "BIZ_LAW":         "v2_10_business_attorney.json",
}

def get(url):
    r = urllib.request.Request(url, headers={"User-Agent":UA, "Accept":"application/json"})
    with urllib.request.urlopen(r, timeout=30) as resp:
        return json.loads(resp.read().decode())

def get_real_lead(cid):
    """Pull first real lead from campaign that isn't a smoke test."""
    d = get(f"{BASE}/campaigns/{cid}/leads?api_key={API_KEY}&limit=20&offset=0")
    items = d.get("data") if isinstance(d, dict) else d
    if not items:
        return None
    for l in items:
        inner = l.get("lead") if isinstance(l.get("lead"), dict) else l
        email = (inner.get("email") or "").lower()
        if "brutus_smoke" in email or "neal@flowoperations.ai" == email:
            continue
        return {
            "company_name": inner.get("company_name") or "",
            "first_name":   inner.get("first_name") or "",
            "last_name":    inner.get("last_name") or "",
            "email":        inner.get("email") or "",
            "phone_number": inner.get("phone_number") or "",
            "website":      inner.get("website") or "",
            "city":         (inner.get("custom_fields") or {}).get("city", "") if isinstance(inner.get("custom_fields"), dict) else "",
            "state":        (inner.get("custom_fields") or {}).get("state", "") if isinstance(inner.get("custom_fields"), dict) else "",
            "location":     inner.get("location") or "",
        }
    return None

def render_email_body(seq_step, personalization, lead):
    """Substitute vars into sequence body."""
    body = seq_step["body"]
    body = body.replace("{{personalized_opener}}", personalization.get("email1_opener", ""))
    body = body.replace("{{personalized_pain}}",   personalization.get("email1_pain", ""))
    body = body.replace("{{personalized_cta}}",    personalization.get("email1_cta", ""))
    body = body.replace("{{first_name}}",  lead.get("first_name", "there"))
    body = body.replace("{{company_name}}", lead.get("company_name", "your business"))
    body = body.replace("{{city}}",   lead.get("city", "") or (lead.get("location","").split(",")[0].strip()))
    body = body.replace("{{state}}",  lead.get("state", "") or (lead.get("location","").split(",")[-1].strip()))
    
    subj = seq_step["subject"]
    subj = subj.replace("{{first_name}}",  lead.get("first_name", "there"))
    subj = subj.replace("{{company_name}}", lead.get("company_name", "your business"))
    subj = subj.replace("{{city}}",   lead.get("city", "") or (lead.get("location","").split(",")[0].strip()))
    subj = subj.replace("{{state}}",  lead.get("state", "") or (lead.get("location","").split(",")[-1].strip()))
    return subj, body


print("═" * 70)
print("Pulling 5 real leads + running Council with niche-aware magnets")
print("═" * 70)

for niche_meta in TEST_NICHES:
    niche_code = niche_meta["niche_code"]
    cid = niche_meta["campaign_id"]
    
    print(f"\n{'━' * 70}")
    print(f"NICHE: {niche_code}  (cid {cid})")
    print(f"{'━' * 70}")

    # 1. Pull a real lead
    lead = get_real_lead(cid)
    if not lead:
        print(f"  No real leads found in campaign {cid}, skipping")
        continue
    lead["niche"] = niche_code
    print(f"\nLEAD: {lead.get('first_name','')} {lead.get('last_name','')} <{lead['email']}>")
    print(f"      {lead['company_name']}  ({lead['city']}, {lead['state']})")
    
    # 2. Load sequence + reverse magnet for this niche
    seq_file = NICHE_TO_SEQ.get(niche_code)
    if not seq_file:
        print(f"  No sequence file mapped for {niche_code}, skipping")
        continue
    seq_path = Path(f"/tmp/leads_recovery/sequences/{seq_file}")
    if not seq_path.exists():
        print(f"  Sequence file missing: {seq_path}, skipping")
        continue
    seq = json.loads(seq_path.read_text())
    
    magnet_name = seq["reverse_lead_magnet"]["name"]
    magnet_offer = seq["reverse_lead_magnet"]["deliverable"]
    pain_anchor  = seq["stat_anchor"]
    
    print(f"\nMAGNET: {magnet_name}")
    
    # 3. Run Council with niche context
    niche_context = {
        "reverse_magnet_name":  magnet_name,
        "reverse_magnet_offer": magnet_offer,
        "pain_anchor":          pain_anchor,
    }
    
    print(f"Running Council...")
    result = council.generate(lead, niche_context=niche_context, debug=False)
    
    print(f"  Voice persona: {result['winning_persona_for_voice']}")
    print(f"  Cost: ${result['cost_usd']}")
    print(f"  Latency: {result['latency_sec']}s")
    
    # 4. Render the Day 0 email
    e1_step = seq["emails"][0]  # Day 0
    subj, body = render_email_body(e1_step, result["final"], lead)
    
    print(f"\n┌─── RENDERED EMAIL 1 (Day 0) ─────────────────────────────────")
    print(f"│ FROM:    [warmed inbox]")
    print(f"│ TO:      {lead['email']}")
    print(f"│ SUBJECT: {subj}")
    print(f"├─────────────────────────────────────────────────────────────")
    for line in body.split("\n"):
        print(f"│ {line}")
    print(f"└─────────────────────────────────────────────────────────────")

print("\n\n═══ DONE ═══")
