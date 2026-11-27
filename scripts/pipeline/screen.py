# Screen Google Maps places with the WINNING-PERIOD rules (Nov 21).
# Usage: python3 screen.py <workdir> pull|fetch|eval
#  workdir holds runs.json (Apify runs), seen_pids.json (places already scraped), idx.json (dedupe index).
import json,re,sys,os,subprocess,collections,html
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
W=sys.argv[1]; os.environ.setdefault('FETCH_CACHE',os.path.join(W,'pages.jsonl'))
from pipe import norm_url,host_dom,site_skip,pick,contact_links,is_person,FREE,NATIONAL,BANK_WORDS
import fetch
from dedupe_index import ck,ph
CHAIN=re.compile(r"archadeck|decks & docks|lowe'?s|home depot|five star bath|re-?bath|mr\.? handyman|handyman connection|ace handyman|window nation|renewal by andersen|leaffilter|window world|bath fitter|four seasons sunrooms|patio enclosures inc|champion windows|power home|neighborly|one hour|aire serv|keller williams|re/?max|coldwell|century 21|rocket mortgage|guaranteed rate|crosscountry|fairway independent|movement mortgage|loandepot|caliber|primelending|guild mortgage|new american funding|cmg|supreme lending|\bbank\b|credit union",re.I)
SUPPLIER=re.compile(r'\b(supply|supplies|lumber|wholesale|distributor|yard materials|timber yard|hardware)\b',re.I)
FRANCH=re.compile(r'franchise|independently owned and operated|locations nationwide',re.I)
DECK=re.compile(r'\bdecks?\b|decking',re.I)
NOTRADE=re.compile(r'supply|lumber|store|wholesale|distributor|manufactur|real estate|insurance|architect|engineer|inspector',re.I)
DECK_DROP_CAT=re.compile(r'painter|pressure washing|handyman|siding|roofing|gutter|window',re.I)
JUNK=re.compile(r'^(you|your|name|email|example|test|user|noreply|no-reply|donotreply|privacy|abuse|webmaster|careers|jobs|hr|recruit|accounting|billing|press|media|reputation|reviews?|marketing|seo)$|sentry|wixpress|godaddy|squarespace|example\.|domain\.com|yourdomain',re.I)
def niche_ok(n,c,pages):
    t=' '.join((p.get('title') or '')+' '+(p.get('desc') or '') for p in pages); body=' '.join(p.get('text') or '' for p in pages)
    nm=c.get('title') or ''; cat=c.get('categoryName') or ''
    if n=='deck':   # recover_deck.py rule
        if NOTRADE.search(cat): return False,'not a contractor category'
        if DECK_DROP_CAT.search(cat) and not DECK.search(nm): return False,'painter/handyman/siding/roofing-first'
        if cat=='Deck builder': return True,''
        if len(DECK.findall(nm+' '+t+' '+body))>=2: return True,''
        return False,'no deck work on site'
    if n=='hardscape':
        H=re.compile(r'paver|hardscap|patio|retaining wall|outdoor living|stone ?work|masonry|walkway|fire ?pit|outdoor kitchen',re.I)
        if re.search(r'lawn (care|mowing)|mowing|tree service|irrigation|asphalt|sealcoat|seal ?coating|pressure wash|turf',nm+' '+(pages[0].get('title') or ''),re.I) and not H.search(nm): return False,'lawn/asphalt/sealing, not hardscape'
        if not (H.search(nm) or H.search(t) or len(H.findall(body))>=8): return False,'hardscape not main trade'
        # strict2 hardscape check
        tn=nm+' | '+t
        if not re.search(r'\bpavers?\b|hardscap|\bpatios?\b|retaining wall|outdoor living',tn,re.I): return False,'hardscape not in homepage title/description'
        return True,''
    if n=='mortgage':
        blob=(nm+' '+t+' '+cat)
        if BANK_WORDS.search(nm) or BANK_WORDS.search(cat): return False,'bank or credit union'
        if any(x in host_dom(norm_url(c.get('website') or '')) for x in NATIONAL): return False,'national lender'
        if re.search(r'commercial (loan|lending|real estate)|hard money|reverse mortgage|insurance agency|financial plann|wealth',blob,re.I): return False,'not residential mortgage broker'
        if re.search(r'mortgage|home loan|lending|loans?\b',blob,re.I): return True,''
        return False,'mortgage not main business'
def site_match(c,pages):
    blob=' '.join((p.get('title') or '')+' '+(p.get('text') or '') for p in pages)
    b=ck(blob); k=ck(c.get('title'))
    if len(k)>=5 and k in b: return True
    stop={'deck','decks','decking','builders','builder','construction','contracting','contractors','services','company','design','designs','home','improvement','mortgage','lending','llc','inc','ltd','landscaping','landscape','hardscapes'}
    toks=[x for x in re.findall(r'[a-z]{4,}',(c.get('title') or '').lower()) if x not in stop]
    if toks and all(t in blob.lower() for t in toks[:2]): return True
    d=re.sub(r'\D','',c.get('phone') or '')[-9:]
    if len(d)>=8 and d in re.sub(r'\D','',blob): return True
    dom=host_dom(norm_url(c['website'])).replace('www.','').split('.')[0]
    if len(k)>=5 and (k[:8] in dom or dom[:8] in k): return True
    return False
stage=sys.argv[2]
if stage=='pull':
    runs=json.load(open(os.path.join(W,'runs.json'))); seen=set(json.load(open(os.path.join(W,'seen_pids.json'))))
    raw=[]
    for r in runs:
        o=0
        while True:
            d=json.loads(subprocess.run(['curl','-sS','-m','120',f"https://api.apify.com/v2/datasets/{r['datasetId']}/items?offset={o}&limit=1000&clean=true"],capture_output=True,text=True).stdout)
            for x in d: x['niche']=r['niche']
            raw+=d
            if len(d)<1000: break
            o+=1000
    rej=collections.Counter(); c=[]; got=set()
    for x in raw:
        pid=x.get('placeId'); n=x['niche']
        if not pid or pid in got: rej[(n,'duplicate place')]+=1; continue
        got.add(pid)
        if pid in seen: rej[(n,'already scraped before')]+=1; continue
        if x.get('permanentlyClosed') or x.get('temporarilyClosed'): rej[(n,'closed')]+=1; continue
        if (x.get('countryCode') or 'US')!='US': rej[(n,'not US')]+=1; continue
        if (x.get('totalScore') or 0)<4.3 or (x.get('reviewsCount') or 0)<20: rej[(n,'rating<4.3 or <20 reviews')]+=1; continue
        w=x.get('website') or ''
        if not w or site_skip({'website':norm_url(w),'title':x.get('title') or '','cat':x.get('categoryName')},n): rej[(n,'no real website/platform')]+=1; continue
        if CHAIN.search(x.get('title') or ''): rej[(n,'chain/bank/national')]+=1; continue
        c.append(x)
    json.dump(c,open(os.path.join(W,'prefilt.json'),'w'))
    print('raw',len(raw),'prefilter pass',collections.Counter(x['niche'] for x in c))
    for k,v in sorted(rej.items()): print('  ',k,v)
elif stage=='fetch':
    c=json.load(open(os.path.join(W,'prefilt.json')))
    urls=[norm_url(x['website']) for x in c]
    P=fetch.run(urls); P=fetch.run(urls,refetch_errors=True)   # refetch failures once
    more=[]
    for u in urls:
        pg=P.get(u)
        if pg and not pg.get('err'): pg['url']=pg.get('url') or u; more+=contact_links(pg,u)
    fetch.run(more); print('fetched',len(urls),'+',len(more))
elif stage=='eval':
    c=json.load(open(os.path.join(W,'prefilt.json'))); P=fetch.cached()
    IDX=json.load(open(os.path.join(W,'idx.json'))); E=set(IDX['E']); D=set(IDX['D']); C=set(IDX['C']); PH=set(IDX['PH'] if 'PH' in IDX else IDX['P'])
    out={}
    for n in ('deck','mortgage','hardscape'):
        rej=collections.Counter(); keep=[]; sE=set();sC=set();sP=set();sW=set()
        for x in [z for z in c if z['niche']==n]:
            u=norm_url(x['website']); R=lambda w: rej.__setitem__(w,rej[w]+1)
            pg=P.get(u)
            if not pg or pg.get('err') or int(pg.get('len') or 0)<500: R('site unreadable'); continue
            pg['url']=pg.get('url') or u; pages=[pg]
            for l in contact_links(pg,u):
                q=P.get(l)
                if q and not q.get('err'): q['url']=q.get('url') or l; pages.append(q)
            text=' '.join(p.get('text') or '' for p in pages)
            if SUPPLIER.search((x.get('title') or '')+' '+(pg.get('title') or '')): R('supplier'); continue
            if FRANCH.search(text): R('franchise'); continue
            ok,w=niche_ok(n,x,pages)
            if not ok: R(w); continue
            if not site_match(x,pages): R("site doesn't match listing"); continue
            r=pick({'url':u,'rec':{'dom':host_dom(u)},'pages':pages},n)
            if not r: R('no email published'); continue
            e=r['email'].lower(); ed=e.split('@')[1]; wd=host_dom(u).replace('www.','')
            if JUNK.search(e.split('@')[0]) or JUNK.search(e): R('junk email'); continue
            k=ck(x.get('title')); p10=ph(x.get('phone'))
            if e in E: R('already emailed (email)'); continue
            if (ed not in FREE and ed in D) or wd in D: R('already emailed (domain)'); continue
            if len(k)>=5 and k in C: R('already emailed (company)'); continue
            if p10 and p10 in PH: R('already emailed (phone)'); continue
            if e in sE or (k and k in sC) or (p10 and p10 in sP) or wd in sW: R('duplicate in batch'); continue
            if n=='mortgage' and any(z in ed for z in NATIONAL): R('national lender email'); continue
            sE.add(e); sC.add(k); sW.add(wd); p10 and sP.add(p10)
            fn=r.get('first_name') or ''; oe=''
            if fn and re.search(re.escape(fn)+r"[^.]{0,60}\b(owner|founder|president|ceo)\b",text,re.I): oe=f'{fn} named as owner/founder on site'
            sc=0; sigs=[]
            if (x.get('totalScore') or 0)>=4.7: sc+=1; sigs.append(f"rating {x.get('totalScore')}")
            rc=x.get('reviewsCount') or 0
            if rc>=50: sc+=1
            sigs.append(f'{rc} reviews')
            if is_person(e.split('@')[0]): sc+=2; sigs.append('named inbox')
            if oe: sc+=1; sigs.append('owner named')
            if ed not in FREE: sc+=1
            keep.append({'email':e,'company':x.get('title'),'first_name':fn,'phone':x.get('phone'),'website':u,'city':x.get('city'),'state':x.get('state'),'country':'US','niche':n,
              'categoryName':x.get('categoryName'),'placeId':x['placeId'],'source':'google_maps','segment':'affluent_county',
              'source_url':f"https://www.google.com/maps/place/?q=place_id:{x['placeId']}",'searchString':x.get('searchString'),'email_found_on':r.get('source_url'),
              'owner_name':fn if oe else '','owner_evidence':oe,'score':min(sc,10),'signals':sigs,'rating':x.get('totalScore'),'reviews':rc,
              'homepage_title':html.unescape(pg.get('title') or ''),'meta_description':html.unescape(pg.get('desc') or ''),'h1':''})
        keep.sort(key=lambda z:(z['niche']=='deck' and z['categoryName']!='Deck builder',-z['score']))
        out[n]=keep; print(n,'keep',len(keep)); [print('    ',k,v) for k,v in rej.most_common()]
    json.dump(out,open(os.path.join(W,'keep.json'),'w'),indent=1)
