import json, sys, time, urllib.request, urllib.error
sys.path.insert(0,"/Users/nealthakkar/Desktop/council")
from core.signal_enricher import enrich
from event_signals import personal_event_signals
from council_mini import best_opener
from concurrent.futures import ThreadPoolExecutor
import os
KEY=os.environ["SMARTLEAD_API_KEY"]
BASE="https://server.smartlead.ai/api/v1"; UA="Mozilla/5.0"; CID=3489464

def get_unp(limit=1200):
    out=[]; off=0
    while len(out)<limit:
        try:
            d=json.loads(urllib.request.urlopen(urllib.request.Request(
                f"{BASE}/campaigns/{CID}/leads?limit=100&offset={off}&api_key={KEY}",headers={"User-Agent":UA}),timeout=30).read())
        except: break
        items=d.get("data",[])
        if not items: break
        for it in items:
            inner=it.get("lead") if isinstance(it.get("lead"),dict) else it
            cf=inner.get("custom_fields") or {}
            if isinstance(cf,str):
                try: cf=json.loads(cf)
                except: cf={}
            if cf.get("personalized_opener"): continue
            em=(inner.get("email") or "").lower()
            if not em: continue
            out.append({"lead_id":inner.get("id") or it.get("id"),"email":em,
                "first_name":inner.get("first_name") or "","company":inner.get("company_name") or "",
                "city":cf.get("city",""),"website":inner.get("website") or "","existing_cf":cf})
        if len(items)<100: break
        off+=100
    return out

def patch(lid,em,cf):
    try:
        urllib.request.urlopen(urllib.request.Request(
            f"{BASE}/campaigns/{CID}/leads/{lid}?api_key={KEY}",
            data=json.dumps({"email":em,"custom_fields":cf}).encode(),
            headers={"Content-Type":"application/json","User-Agent":UA},method="POST"),timeout=30).read()
        return True
    except: return False

def proc(lead):
    try:
        # site content free; SKIP news lookup to stay cheap + fast (Apify near cap)
        from event_signals import site_recent_content
        ev={}; 
        sc=site_recent_content(lead["website"])
        if sc: ev["own_site_recent_content"]=sc
        base=enrich({"first_name":lead["first_name"],"company_name":lead["company"],
            "website":lead["website"],"city":lead["city"],"state":"","niche":"SECURITY"})
        r=best_opener({"first_name":lead["first_name"],"company":lead["company"],
            "city":lead["city"],"niche":"security company","signals":{**(base or {}),**ev}})
        op=r.get("opener","")
        if not op: return False
        cf=dict(lead["existing_cf"]); cf.update({"personalized_opener":op,
            "signal_tier":str(1 if ev else 3),"opener_persona_winner":r.get("winner_id",""),"signal_regen_v2":"1"})
        return patch(lead["lead_id"],lead["email"],cf)
    except: return False

leads=get_unp()
print(f"SECURITY leads to personalize: {len(leads)}",flush=True)
ok=0
with ThreadPoolExecutor(max_workers=5) as ex:
    for i,res in enumerate(ex.map(proc,leads),1):
        if res: ok+=1
        if i%50==0: print(f"  [{i}/{len(leads)}] ok={ok}",flush=True)
print(f"DONE personalized {ok}/{len(leads)}",flush=True)
