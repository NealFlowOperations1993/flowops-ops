# Build Smartlead custom fields + tool_prospects insert for a batch, with the WINNING Email 1 MIX (Nov 21):
#   deck: 40% J "price shoppers", 20% Q "quick question", 20% W "I'm just wondering" (project planner), 20% T "two homeowners".
#   Email 2 = "Bumping this up. Want me to send the <tool> over? It takes about a minute to try." (NO link). Email 3 = breakup with link.
# Usage: python3 build_w.py <workdir> BATCH[,BATCH2] ['["email-to-drop", ...]']
#   reads <workdir>/pre_<BATCH>.json (fields: email, co, fn, website, city, state, phone, placeId, source_url, rating, reviews,
#   lead_score, owner_evidence, signals, offer, mcity, review_quote) ; writes final_<BATCHES>.json and ins_<BATCHES>.sql
import json,re,random,string,sys,os
W=sys.argv[1]; batches=sys.argv[2].split(',')
random.seed(hash(sys.argv[2])%100000+20261120)
BASE='https://brandable-toolbox-studio.lovable.app/t/'
drop=set(json.loads(sys.argv[3])) if len(sys.argv)>3 else set()
Q='“';QE='”'
VAR=['J','Q','J','W','J','T','J','Q','W','T']
def slugify(s):
    s=s.lower().replace('&',' and ').replace("'",'').replace('’','').replace('.','')
    return re.sub(r'[^a-z0-9]+','-',s).strip('-')[:48].strip('-')
taken=set()
def slug(co):
    b=slugify(co); s=b; j=2
    while s in taken: s=f"{b}-{j}"; j+=1
    taken.add(s); return s
short=lambda: ''.join(random.choice(string.ascii_lowercase) for _ in range(6))
num=lambda v: ('%g'%v) if isinstance(v,(int,float)) else str(v)
def deck_fields(co,fn,slug_,v):
    poss=co+("'" if co.endswith('s') else "'s")
    tool='deck-project-planner' if v=='W' else 'deck-price-range'
    tname='project planner' if v=='W' else 'deck designer'
    url=BASE+tool+'/'+slug_
    if v=='J':
        subj='price shoppers'
        body=(f"{fn} - " if fn else "Hi there - ")+f"is it frustrating when price shoppers reduce your craftsmanship to {Q}what's your cheapest price?{QE}<br><br>We built a deck designer for {co}. Homeowners explore boards, colors and railings, see a price range, and send you their choices with the request.<br><br>Something specific to discuss, not just {Q}I want a deck.{QE}<br><br>Could I show you how it works?"
    elif v=='Q':
        subj=f"new jobs for {co}"
        body=(f"Hi {fn}, " if fn else "Hi there, ")+f"quick question - how does {co} get most of its deck jobs right now?<br><br>Only asking because we built a deck designer with {poss} name on it. Homeowners build their deck in 3D, see a price range and a realistic photo of it, and their request comes straight to you.<br><br>Worth a look?"
    elif v=='W':
        subj=f"new clients for {co}"
        body=(f"Hi {fn}, " if fn else "Hi there, ")+f"I'm just wondering - how does {co} decide which deck estimates are worth the drive?<br><br>We built a project planner that gives you the homeowner's budget, timeline, HOA status and yard photos before you go, with {poss} name on it.<br><br>Would a quick call next Tuesday or Wednesday work?"
    else:
        subj='the price shopper vs. the $25k buyer'
        body=(f"{fn} - " if fn else "Hi there - ")+f"two homeowners call you today. One is {Q}just getting prices.{QE} The other already picked composite boards, a black railing and a $25k budget.<br><br>You'd drive to the second one first, right? Problem is, you can't tell them apart until you're standing in the yard.<br><br>We built a free deck designer for {co} that sorts them before you drive out: homeowners pick their design, see a price range, and send you the request with every choice attached.<br><br>Could I show you how it works?"
    e2=(f"{fn}, bumping this up." if fn else "Bumping this up.")+f" Want me to send the {tname} over? It takes about a minute to try."
    e3=f"Last one from me.<br><br>If new estimates aren't your department, should I be sending this to someone else? If it's you and the timing's off, no problem.<br><br>Here's the {tname} we built for {co}: {url}"
    return dict(p_subject=subj,p_body=body,e2_body=e2,e3_body=e3,tool_url=url,variant=v)
out={}
for b in batches:
    n='hardscape' if b.startswith('HARD') else ('mortgage' if b.startswith('MORT') else 'deck')
    L=[]
    for r in json.load(open(os.path.join(W,f'pre_{b}.json'))):
        if r['email'] in drop: continue
        r=dict(r); r['slug']=slug(r['co']); r['short']=short(); fn=r['fn']; co=r['co']
        base={'source':'google_maps','segment':'affluent_county','placeId':r['placeId'],'source_url':r['source_url'],'rating':num(r.get('rating') or ''),'reviews':num(r.get('reviews') or ''),
              'lead_score':str(r.get('lead_score') or ''),'owner_name':fn,'owner_evidence':r.get('owner_evidence') or '','signals':r.get('signals') or ''}
        if n=='deck':
            cf=dict(base,**deck_fields(co,fn,r['slug'],VAR[len(L)%10])); first=fn
        elif n=='mortgage':
            url=BASE+'mortgage-true-monthly/'+r['slug']; city=r['mcity']
            parts=[f"{fn}," if fn else "Hey there,",f"Right now, someone in {city} is getting pre-approved somewhere else.",
                   f"They ran their numbers on a lead site, got a flood of calls by morning, and picked whoever called first. Not the best lender in {city}, just the fastest dialer.",
                   "That's infuriating when you know you'd have done it better.",
                   f"We built a payment calculator branded for {co}. {city} borrowers see their full monthly payment on a page with your name on it, and the request goes straight to you.","Want to see it?"]
            cf=dict(base,p_subject=f"{city} borrowers are being auctioned off...",p_body='<br><br>'.join(parts),e2_open=(f"{fn}, one more thought." if fn else "One more thought."),tool_url=url,variant='W2M'); first=fn
        else:
            url=BASE+'backyard-visualizer/'+r['slug']
            q=(r.get('review_quote') or '').strip()
            pl=f'Saw this in one of your recent Google reviews: "{q}"' if q else f"{num(r['rating'])} stars across {num(r['reviews'])} Google reviews doesn't happen by accident."
            cf=dict(base,personal_line=pl,tool_url=url,variant='W1B'); first=fn or 'there'
        for k,v in cf.items():
            assert not re.search(r'[{}]|\bNone\b|\bnan\b|undefined',str(v)),(r['email'],k,v)
        r['cf']=cf; r['first']=first; r['niche']=n; L.append(r)
    out[b]=L
tag='_'.join(batches)
json.dump(out,open(os.path.join(W,f'final_{tag}.json'),'w'),indent=1)
TOOLS={'deck':['deck-price-range','deck-project-planner'],'hardscape':['backyard-visualizer'],'mortgage':['mortgage-true-monthly']}
q=lambda v: 'NULL' if v in (None,'') else "'"+str(v).replace("'","''")+"'"
rows=[]
for b,L in out.items():
    for r in L:
        rows.append("("+",".join([q(r['slug']),q(r['short']),q(r['email']),q(r['co']),q(r['fn']),q(r['email']),q(r['website']),q(r['city'] if r['state'] else None),q(r['state']),q(r['niche']),
          "ARRAY["+",".join("'"+t+"'" for t in TOOLS[r['niche']])+"]","'pending'",q(r.get('phone')),"'#1F3A5F'",'NULL',q(json.dumps(r.get('offer') or {}))+"::jsonb"])+")")
open(os.path.join(W,f'ins_{tag}.sql'),'w').write("insert into tool_prospects (slug,short_code,external_id,business_name,owner_first_name,owner_email,website,city,state,niche,enabled_tools,enrich_status,phone,brand_color,accent_color,offer) values "+",".join(rows)+" on conflict do nothing returning slug")
print({k:len(v) for k,v in out.items()},'rows',len(rows),'— check slugs against tool_prospects before inserting')
