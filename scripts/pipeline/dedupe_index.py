# Build the dedupe index from every Smartlead campaign: emails, domains, company keys, phones, bounced.
import json,re,sys,time
from urllib.parse import urlparse
from gw import call
FREE={'gmail.com','yahoo.com','outlook.com','hotmail.com','aol.com','icloud.com','msn.com','comcast.net','live.com','me.com','att.net','sbcglobal.net','verizon.net','ymail.com','bellsouth.net','cox.net','charter.net','protonmail.com'}
def dom(u):
    h=urlparse(u if '://' in (u or '') else 'https://'+(u or '')).netloc.lower(); return h[4:] if h.startswith('www.') else h
def ck(n):
    t=re.sub(r'[^a-z0-9 ]',' ',(n or '').lower().replace('&',' and ')).split()
    return ''.join(x for x in t if x not in ('llc','inc','co','corp','company','the','and','of','ltd','l','c','pllc'))
def ph(p):
    d=re.sub(r'\D','',p or ''); d=d[1:] if len(d)==11 and d[0]=='1' else d; return d if len(d)==10 else ''
def page(cid,o):
    # A failed page must never look like "no more leads": retry, then stop with an error.
    for a in range(6):
        x=call([{'tag':'x','method':'GET','path':f"/api/v1/campaigns/{cid}/leads",'query':{'offset':str(o),'limit':'100'}}])
        b=x[0]['body'] if x else None
        if isinstance(b,dict) and isinstance(b.get('data'),list): return b
        time.sleep(5+5*a)
    raise SystemExit(f'page failed 6x: campaign {cid} offset {o}')
if __name__=='__main__':
    cl=call([{'tag':'c','method':'GET','path':'/api/v1/campaigns/'}])[0]['body']
    E=set();D=set();C=set();P=set();n=0;expected=0
    for c in cl:
        o=0;tot=None
        while True:
            b=page(c['id'],o); data=b['data']
            if tot is None: tot=int(b.get('total_leads') or 0); expected+=tot
            for L in data:
                l=L.get('lead') or {}; e=(l.get('email') or '').strip().lower(); E.add(e); n+=1
                if '@' in e and e.split('@')[1] not in FREE: D.add(e.split('@')[1])
                w=dom(l.get('website') or '')
                if w: D.add(w)
                k=ck(l.get('company_name'))
                if len(k)>=5: C.add(k)
                p=ph(l.get('phone_number'))
                if p: P.add(p)
            if len(data)<100: break
            o+=100
    print('campaigns',len(cl),'leads',n,'expected',expected,'emails',len(E),'domains',len(D),'companies',len(C),'phones',len(P))
    if n!=expected: raise SystemExit(f'INCOMPLETE INDEX: read {n} leads but campaigns report {expected}; index not written')
    json.dump({'E':sorted(E),'D':sorted(D),'C':sorted(C),'P':sorted(P)},open(sys.argv[1],'w'))
