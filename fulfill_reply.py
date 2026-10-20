#!/usr/bin/env python3
"""
Reply Fulfillment Kit — generate the promised deliverable when a lead replies.

Usage:
  python3 fulfill_reply.py --email tmercer@mercer-wm.com            # auto-detect niche+variant
  python3 fulfill_reply.py --domain hasnerlaw.com --type 3things
  python3 fulfill_reply.py --domain hasnerlaw.com --type mockup

Types:
  3things  -> runs REAL FlowScore on their site, formats the "3 specific things"
              reply (Variant A fulfillment)
  mockup   -> finds pre-gen mockup or generates one via Gemini 3.1 Flash
              (Variant C fulfillment)

NEVER bulk-run FlowScore (that's what 402'd it in May). One lead at a time.
"""
import argparse, json, re, sys, time, urllib.request
import os

sys.path.insert(0, "/Users/nealthakkar/Desktop/council")
from core.flowscore import score as flowscore

SL_KEY=os.environ["SMARTLEAD_API_KEY"]
SL="https://server.smartlead.ai/api/v1"
UA="Mozilla/5.0"
CAMPAIGNS={"WEALTH":3263730,"FINANCIAL":3191292,"MORTGAGE":3191290,
    "INSURANCE":3191291,"MEDSPA":3191285,"PI_LAW":3327115,
    "MCA":3263732,"COMMLOAN":3263731}

def find_lead(email):
    """Locate lead across campaigns -> (niche, lead dict)."""
    for niche,cid in CAMPAIGNS.items():
        offset=0
        while offset<3600:
            try:
                d=json.loads(urllib.request.urlopen(urllib.request.Request(
                    f"{SL}/campaigns/{cid}/leads?limit=100&offset={offset}&api_key={SL_KEY}",
                    headers={"User-Agent":UA}),timeout=30).read())
            except: break
            items=d.get("data",[])
            if not items: break
            for it in items:
                inner=it.get("lead") if isinstance(it.get("lead"),dict) else it
                if (inner.get("email") or "").lower()==email.lower():
                    return niche, inner
            if len(items)<100: break
            offset+=100
    return None, None

def fulfill_3things(domain, niche, company=""):
    url=domain if domain.startswith("http") else f"https://{domain}"
    print(f"Running FlowScore on {url} (takes ~30-60s)...", file=sys.stderr)
    fs=flowscore(url, niche or "generic")
    if fs.get("error"):
        print(f"FlowScore error: {fs}", file=sys.stderr); sys.exit(1)
    dims=sorted(fs.get("dimensions",[]), key=lambda d:d.get("score",100))[:3]
    leak=fs.get("estimated_monthly_revenue_leakage",{}) or {}
    name=company or domain
    lines=[]
    lines.append(f"Here are the 3 things, as promised — pulled from a live scan of {domain}:")
    lines.append("")
    for i,d in enumerate(dims,1):
        finding=""
        for f in d.get("findings",[]):
            if f.strip().startswith(("✗","✘","x ")):
                finding=re.sub(r"^[✗✘x]\s*","",f.strip()); break
        if not finding and d.get("findings"): finding=re.sub(r"^[✓✗⚠]\s*","",d["findings"][0])
        lines.append(f"{i}. {d.get('name','?')} — scored {d.get('score',0)}/100.")
        lines.append(f"   {finding[:220]}")
        lines.append("")
    if leak.get("max"):
        lines.append(f"Combined, this typically means ${leak.get('min',0):,}-${leak.get('max',0):,}/month "
                     f"walking past {name}.")
        lines.append("")
    lines.append("Each one is fixable — two of them in under a week. If you want, I'll walk you "
                 "through exactly how on a 15-min call (link below). And if not, at least you "
                 "know where the leaks are now.")
    print("\n".join(lines))
    print(f"\n[meta] overall_score={fs.get('overall_score')} range={fs.get('score_range')}", file=sys.stderr)

def fulfill_mockup(domain, niche, email=""):
    slug=re.sub(r"[^a-z0-9]+","_",(email.split("@")[0] if email else domain).lower())[:40]
    cdn=f"https://flowops-assets.vercel.app/mockups/{slug}.png"
    try:
        r=urllib.request.urlopen(urllib.request.Request(cdn,method="HEAD"),timeout=10)
        if r.status==200:
            print(f"Pre-generated mockup EXISTS:\n  {cdn}\n\nReply draft:")
            print(f"\nHere it is — what {domain} could look like:\n{cdn}\n\nYours to keep either way. If you want the audit behind it (why these specific changes convert), 15 min on my calendar below.")
            return
    except: pass
    print(f"No pre-gen mockup for {slug}. Generating now (~30s, $0.01)...", file=sys.stderr)
    from core.website_redo import scrape_site, generate_redesign_image
    url=domain if domain.startswith("http") else f"https://{domain}"
    s=scrape_site(url)
    if s.get("error"):
        print(f"scrape failed: {s['error']}", file=sys.stderr); sys.exit(1)
    out=f"/Users/nealthakkar/Desktop/intakebot/public/mockups/{slug}.png"
    png=generate_redesign_image(s, niche or "DEFAULT", company_name=domain, out_path=out)
    if png:
        print(f"Generated: {png}")
        print(f"⚠ Push to Vercel (cd ~/Desktop/flowops-assets && cp {png} public/mockups/ && npx vercel --prod --yes) then send: {cdn}")
    else:
        print("generation failed", file=sys.stderr); sys.exit(1)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--email")
    p.add_argument("--domain")
    p.add_argument("--type",choices=["3things","mockup"],default="3things")
    p.add_argument("--niche",default="")
    a=p.parse_args()
    niche=a.niche; domain=a.domain; company=""
    if a.email and not domain:
        n,lead=find_lead(a.email)
        if lead:
            niche=niche or n
            domain=(lead.get("website") or a.email.split("@")[1]).replace("http://","").replace("https://","").strip("/")
            company=lead.get("company_name","")
            print(f"[found] {a.email} -> niche={niche} domain={domain} company={company}", file=sys.stderr)
        else:
            domain=a.email.split("@")[1]
            print(f"[not in campaigns] using email domain {domain}", file=sys.stderr)
    if not domain: p.error("need --email or --domain")
    if a.type=="3things": fulfill_3things(domain, niche, company)
    else: fulfill_mockup(domain, niche, a.email or "")
