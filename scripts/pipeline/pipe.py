import json, os, re, sys, glob, csv
from urllib.parse import urlparse, urljoin

D = os.path.dirname(os.path.abspath(__file__))
N = 400
FREE = {'gmail.com','yahoo.com','outlook.com','hotmail.com','aol.com','icloud.com','me.com','msn.com','live.com','ymail.com','comcast.net','att.net','sbcglobal.net','bellsouth.net','verizon.net','cox.net','charter.net','protonmail.com'}
BAD_DOM_SUB = ['sentry','wixpress','godaddy','example','domain.com','email.com','yourdomain','yoursite','website.com','company.com','test.com','sentry.io','wix.com','squarespace','mysite','placeholder','address.com','site.com','latofonts','schema.org']
BAD_LOCAL = ['noreply','no-reply','donotreply','do-not-reply','privacy','abuse','webmaster','careers','career','jobs','job','hr','recruit','recruiting','hiring','employment','postmaster','unsubscribe','legal','compliance','dpo','support-team','firstname','first.last','name','your','yourname','johndoe','john.doe','jane','janedoe','user','username','email','test','filler','example']
GENERIC = {'info','office','contact','contactus','admin','sales','hello','hi','support','service','services','team','mail','inquiries','inquiry','enquiries','estimates','estimate','quotes','quote','booking','bookings','customerservice','customercare','help','general','marketing','billing','accounting','accounts','ap','ar','loans','mortgage','mortgages','apply','applications','scheduling','schedule','dispatch','operations','orders','projects','design','reception','frontdesk','main','home','homes','loan','lending','deck','decks','build','builds','landscape','landscaping','pavers','hardscape','team1','office1','info1','service1','connect','welcome','questions','request','requests','news','media','pr','press','processing','closing','underwriting','servicing','payoff','payments','servicing','processing','draws','leads','ask','apply','closer','ourcustomers','reachus','application','app','apps','web','website','sales1','hola'}
MANUAL_BLOCK = {'typesetit@att.net', 'gracemitchell0408@gmail.com'}
IMG_EXT = ('.png','.jpg','.jpeg','.gif','.webp','.svg','.bmp','.ico','.tif','.tiff','.js','.css','.pdf','.mp4','.avif')
NATIONAL = ['houseloan.com','primelending.com','waterstonemortgage.com','nationslending.com','cmgfi.com','cmghomeloans.com','snmc.com','summitfunding.net','embracehomeloans.com','dhimortgage.com','guildmortgage.com','originpoint.com','naf.com','foamortgage.com','sierrapacificmortgage.com','highlandhomeloans.com','primeres.com','fairwaymc.com','fairwayindependentmc.com','movement.com','crosscountrymortgage.com','ccm.com','rocketmortgage.com','loandepot.com','rate.com','guaranteedrate.com','academymortgage.com','supremelending.com','newrez.com','wellsfargo.com','chase.com','bankofamerica.com','uwm.com','caliberhomeloans.com','pennymac.com','mrcooper.com','usbank.com','truist.com','pnc.com','citi.com','regions.com','fifththird.com','huntington.com','tdbank.com','navyfederal.org','penfed.org','usaa.com','geneva.com','genevafi.com','homebridge.com','benchmark.us','nfmlending.com','bayequityhomeloans.com','everettfinancial.com','supremelending.com','alliedmortgage.com','churchillmortgage.com','firsthome.com','annieMac.com','anniemac.com','amerisave.com','luminatehomeloans.com','homepoint.com','eustis.com','fbcmortgage.com','plazahomemortgage.com','cardinalfinancial.com','ruoff.com','unionhomemortgage.com','mutualofomahamortgage.com','americanpacificmortgage.com','apmortgage.com','paramountresidential.com','synergyonemortgage.com','newamericanfunding.com','nafinc.com','homeside.com','primarybank.com','branches.','lo.','loanofficer.','southernfirst.com','prmgapp.com','prmg.net','themoneystore.com','nationsreliable.com','firstcommunitymortgage.com','amerihome.com','nvrmortgage.com','cashcallmortgage.com','intercaplending.com','weichertfinancialservices.com','loanstreamwholesale.com','kindlending.com','deephavenmortgage.com','evergreenhomeloans.com','atlanticbay.com','leaderonefinancial.com','sfmc.com','prmg.com','mortgagecorp.com','loandepot.com','rocket.com','mymortgage-online.com','nationslending.com','sentemortgage.com','shellpointmtg.com','acralending.com','homesteadfinancial.com','barrettfinancial.com','acrisuremortgage.com']
BANK_WORDS = re.compile(r'\b(bank|credit union|federal savings|savings bank|national association)\b', re.I)
SHORT = {'bit.ly','poplme.co','linktr.ee','tinyurl.com','goo.gl','g.page','facebook.com','instagram.com','sites.google.com'}
CONTACT_KW = ['contact','about','team','get-a-quote','quote','estimate','meet','staff','our-story','who-we-are']
EMAIL_RE = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
STOPNAMES = {'The','Our','Us','Your','Me','Team','A','An','With','Me','You','Them','Today','Now','Here','Who','Mortgage','Home','Loan','Lending','Deck','Decks','Pavers','Group','Staff','Owner'}


def norm_url(u):
    u = (u or '').strip()
    if not u:
        return ''
    if '://' not in u:
        u = 'https://' + u
    p = urlparse(u)
    # drop tracking query strings
    q = '&'.join(x for x in p.query.split('&') if x and not x.lower().startswith(('utm_', 'gclid', 'fbclid', 'y_source')))
    return p._replace(query=q, fragment='').geturl()


def host_dom(u):
    h = urlparse(u).netloc.lower().split(':')[0]
    return h[4:] if h.startswith('www.') else h


def core(d):
    parts = d.lower().split('.')
    if len(parts) >= 3 and parts[-2] in ('co', 'com', 'net', 'org') and len(parts[-1]) == 2:
        parts = parts[:-2]
    else:
        parts = parts[:-1]
    return parts[-1].replace('-', '') if parts else d


def domain_ok(edom, dom):
    edom = edom.lower(); dom = dom.lower()
    if dom.startswith('www.'):
        dom = dom[4:]
    if edom == dom or edom.endswith('.' + dom) or dom.endswith('.' + edom):
        return True
    a, b = core(edom), core(dom)
    if len(a) >= 5 and len(b) >= 5 and (a in b or b in a):
        return True
    # abbreviation variant: ampref.com for americanpreferredmortgage.com
    if len(a) >= 4 and a[0] == b[0] and a[:2] == b[:2]:
        it = iter(b)
        if all(ch in it for ch in a):
            return True
    return False


def clean_email(e):
    e = e.strip().strip('.').strip()
    if '%' in e or ' ' in e:
        return None
    if e.lower().startswith('mailto:'):
        e = e[7:]
    if not re.fullmatch(r'[A-Za-z0-9._+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,24}', e):
        return None
    local, dom = e.split('@', 1)
    # uppercase-encoded junk: long mixed-case/hex local parts
    if re.search(r'[A-Z]', local) and (len(local) > 20 or re.search(r'\d{3,}', local)):
        return None
    if re.fullmatch(r'[0-9a-f]{16,}', local.lower()):
        return None
    e = e.lower(); local = local.lower(); dom = dom.lower()
    if dom.endswith(IMG_EXT) or re.search(r'@\d+x\.', e) or local.endswith(IMG_EXT):
        return None
    if any(s in dom for s in BAD_DOM_SUB):
        return None
    if local in BAD_LOCAL or any(local.startswith(b) for b in ('noreply', 'no-reply', 'donotreply', 'privacy', 'abuse', 'webmaster', 'career', 'jobs', 'hr.', 'hr-', 'recruit', 'hiring')):
        return None
    if len(local) > 40 or len(local) < 2:
        return None
    if dom in FREE and re.search(r'web|seo|design|typeset|pixel|media|market|digital|studio|agency|graphic|wordpress|site', local):
        return None
    if e in MANUAL_BLOCK:
        return None
    return e


def is_person(local):
    l = re.sub(r'\d+$', '', local)
    if l in GENERIC:
        return False
    if any(l.startswith(g) and len(l) > len(g) and not l[len(g)].isalpha() for g in GENERIC):
        return False
    if len(l) < 3:
        return False
    if any(w in l for w in ('apply', 'applic', 'process', 'servic', 'draws', 'leads', 'customer', 'reachus', 'concierge', 'closer', 'funding', 'capital', 'financ', 'mtg', 'realty', 'quote', 'request', 'inquir', 'office', 'admin', 'hello', 'contact', 'mail', 'web', 'noreply', 'accounts', 'billing', 'payroll', 'invoice', 'paver', 'patio', 'yard', 'lawn')):
        return False
    if any(w in l for w in ('info', 'office', 'contact', 'sales', 'service', 'support', 'admin', 'estimate', 'quote', 'loan', 'mortgage', 'lending', 'team', 'deck', 'paver', 'landscap', 'hardscap', 'construct', 'build', 'outdoor', 'home', 'group', 'inc', 'llc', 'company', 'corp')):
        return False
    return True


def find_name(local, text, title):
    """First name only when the local part clearly matches a capitalised name on the page."""
    blob = (title or '') + ' ' + (text or '')
    parts = re.split(r'[._-]', local)
    parts = [re.sub(r'\d+', '', p) for p in parts if p]
    cands = []
    if parts and len(parts[0]) >= 3:
        cands.append(parts[0])
    NOTSUR = r'(?!(?:Mortgage|Mortgages|Team|Group|Home|Homes|Loans?|Lending|Financial|Funding|Capital|Decks?|Construction|Landscap\w*|Hardscap\w*|Pavers?|Outdoor|Services?|Company|Inc|LLC|Realty|Request|Requests|Form|Process|Today|Now|Us|Our|The|And|Of|In|At|For|To)\b)'
    for c in cands:
        nm = c.capitalize()
        if nm in STOPNAMES or c in GENERIC or not is_person(c):
            continue
        if len(parts) >= 2 and len(parts[1]) >= 2:
            if re.search(r'\b' + re.escape(nm) + r'\s+(?:[A-Z]\.\s+)?' + re.escape(parts[1].capitalize()) + r'\b', blob):
                return nm
        if re.search(r'\b' + re.escape(nm) + r'\s+(?:[A-Z]\.\s+)?' + NOTSUR + r"[A-Z][a-zA-Z'-]{1,20}\b", blob):
            return nm
    # jsmith style: first initial + surname
    l = re.sub(r'\d+', '', local)
    if re.fullmatch(r'[a-z]{4,15}', l):
        sur = l[1:].capitalize()
        m = re.search(r'\b(' + l[0].upper() + r'[a-z]{2,12})\s+(?:[A-Z]\.\s+)?' + re.escape(sur) + r'\b', blob)
        if m and m.group(1) not in STOPNAMES:
            return m.group(1)
    return ''


def site_skip(rec, niche):
    url = norm_url(rec.get('website'))
    h = host_dom(url)
    if not url or h in SHORT:
        return 'shortener/social url'
    FR = ['mrhandyman.com','handymanconnection.com','archadeck.com','homedepot.com','lowes.com','angi.com','homeadvisor.com','thumbtack.com','yelp.com','houzz.com','acehandymanservices.com','mosquitojoe.com','conceptsplus.com','fivestarpainting.com','bluefrog.com','decksdirect.com','trex.com','timbertech.com','unilock.com','belgard.com','techo-bloc.com','nexgrill.com','sunrooms.com','patiocover.com','renewalbyandersen.com','leaffilter.com','andersenwindows.com','superiorfence.com','fencetastic.com','ameriskillcorp.com','bathfitter.com','westshorehome.com','powerhrg.com','lumberliquidators.com','neighborly.com','outdoorlivingbrands.com','weed-man.com','grassmasters.com','lawndoctor.com','trugreen.com','brightview.com','yellowstonelandscape.com','davey.com','thegrounduys.com','unitedsitelandscaping.com','naturalawn.com','meadowsfarms.com','merrifieldgardencenter.com','spring-green.com','lawnlove.com','jobbersites.com','lawnstarter.com','duvallandscape.com','grass365.com']
    for n in FR:
        if h == n or h.endswith('.' + n):
            return 'national franchise/platform'
    if niche == 'mortgage':
        full = h + urlparse(url).path.lower()
        for n in NATIONAL:
            if n.endswith('.') and h.startswith(n):
                return 'national lender subdomain'
            if not n.endswith('.') and (h == n or h.endswith('.' + n)):
                return 'national lender/bank'
        if BANK_WORDS.search(rec.get('title', '')) or BANK_WORDS.search(rec.get('cat', '') or ''):
            return 'bank/credit union'
    return None


def sp(niche):
    return os.path.join(D, f'state_{niche}.json')


def load(niche):
    if os.path.exists(sp(niche)):
        return json.load(open(sp(niche)))
    pool = json.load(open(os.path.join(D, f'pool_{niche}.json')))[:N]
    st = {'sites': {}, 'batch_seq': 0, 'inflight': {}}
    for i, r in enumerate(pool):
        k = f'{niche[0]}{i}'
        s = {'rec': r, 'url': norm_url(r['website']), 'status': 'pending', 'pages': [], 'queue': []}
        why = site_skip(r, niche)
        if why:
            s['status'] = 'skipped'; s['reason'] = why
        st['sites'][k] = s
    return st


def save(niche, st):
    tmp = sp(niche) + '.tmp'
    json.dump(st, open(tmp, 'w'))
    os.replace(tmp, sp(niche))


def cmd_next(niche, nb):
    st = load(niche)
    inflight_keys = {j['tag'] for b in st['inflight'].values() for j in b}
    jobs = []
    for k, s in st['sites'].items():
        if s['status'] in ('pending', 'contact'):
            why = site_skip(s['rec'], niche)
            if why:
                s['status'] = 'skipped'; s['reason'] = why
        if s['status'] == 'pending' and f'{k}p0' not in inflight_keys:
            jobs.append({'tag': f'{k}p0', 'url': s['url']})
        elif s['status'] == 'contact':
            for i, u in enumerate(s['queue']):
                t = f'{k}p{i+1}'
                if t not in inflight_keys:
                    jobs.append({'tag': t, 'url': u})
    out = []
    for b in range(nb):
        BS = int(os.environ.get('BS', '20'))
        chunk = jobs[b*BS:(b+1)*BS]
        if not chunk:
            break
        st['batch_seq'] += 1
        bid = f'{niche}{st["batch_seq"]}'
        st['inflight'][bid] = chunk
        out.append((bid, chunk))
    save(niche, st)
    for bid, chunk in out:
        print(bid)
        print(json.dumps({'webhookData': {'method': 'POST', 'body': {'lean': True, 'batch': chunk}}}, separators=(',', ':')))
    if not out:
        print('NOTHING')


def pick(s, niche):
    dom = host_dom(s['url']) or s['rec']['dom']
    found = {}
    for pg in s['pages']:
        cand = list(pg.get('emails') or [])
        cand += EMAIL_RE.findall(pg.get('text') or '')
        for e in cand:
            ce = clean_email(e)
            if not ce:
                continue
            ed = ce.split('@')[1]
            if ed in FREE or domain_ok(ed, dom) or domain_ok(ed, s['rec']['dom']):
                found.setdefault(ce, pg)
    if not found:
        return None
    emails = list(found)
    person = [e for e in emails if is_person(e.split('@')[0])]
    own = [e for e in emails if e.split('@')[1] not in FREE]
    order = {e: i for i, e in enumerate(emails)}
    def rank(e):
        loc = e.split('@')[0]
        return (0 if e in person else 1, 0 if e in own else 1, 0 if re.search(r'[a-z]', loc) and not re.search(r'\d', loc) else 1, order[e])
    emails.sort(key=rank)
    best = emails[0]
    pg = found[best]
    fn = ''
    if best in person:
        for p in [pg] + s['pages']:
            fn = find_name(best.split('@')[0], p.get('text'), p.get('title'))
            if fn:
                break
    return {'email': best, 'alt_emails': emails[1:6], 'first_name': fn, 'source_url': pg['url'], 'page_title': (pg.get('title') or '')[:200]}


def contact_links(pg, base):
    h0 = host_dom(base)
    out = []
    for l in pg.get('links') or []:
        u = l.get('u') or ''
        if u.startswith(('mailto:', 'tel:', 'javascript:', '#')):
            continue
        try:
            a = urljoin(pg.get('url') or base, u)
        except Exception:
            continue
        if not a.startswith('http') or host_dom(a) != h0:
            continue
        path = urlparse(a).path.lower() + ' ' + (l.get('label') or '').lower()
        if any(k in path for k in CONTACT_KW):
            pr = 0 if 'contact' in path else (1 if any(k in path for k in ('about', 'team', 'meet', 'staff')) else 2)
            a = a.split('#')[0]
            if a.rstrip('/') != base.rstrip('/'):
                out.append((pr, a))
    seen = []
    for pr, a in sorted(out, key=lambda x: x[0]):
        if a not in seen:
            seen.append(a)
    # one contact + one about/team when possible
    c = [a for a in seen if 'contact' in a.lower()]
    o = [a for a in seen if 'contact' not in a.lower()]
    res = (c[:1] + o[:1]) if c and o else seen[:2]
    return res


def cmd_ingest(niche, path, bid):
    st = load(niche)
    d = json.load(open(path))
    status = d['execution']['status']
    try:
        items = d['data']['resultData']['runData']['Extract Page'][0]['data']['main'][0][0]['json']['data']
    except Exception as ex:
        print('NO DATA', status, ex)
        return
    jobs = st['inflight'].pop(bid, None)
    got = {it['tag']: it for it in items}
    rd = d['data']['resultData']['runData']
    try:
        prep = [x['json'] for x in rd['Prep Pages'][0]['data']['main'][0]]
        fetch = [x['json'] for x in rd['Fetch Page'][0]['data']['main'][0]]
        for p_, f_ in zip(prep, fetch):
            h = f_.get('html') or ''
            if not isinstance(h, str) or p_.get('tag') not in got:
                continue
            h2 = re.sub(r'(?is)<(script|style|noscript)[^>]*>.*?</\1>', ' ', h)
            txt = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', h2))
            txt = txt.replace('&nbsp;', ' ').replace('&amp;', '&')
            g = got[p_['tag']]
            g['text'] = txt[:20000]
            mails = re.findall(r'mailto:([^"\'?>\s]+)', h) + EMAIL_RE.findall(txt)
            g['emails'] = list(dict.fromkeys((g.get('emails') or []) + [m for m in mails]))
    except Exception as ex:
        pass
    errs = 0
    for j in (jobs or [{'tag': t} for t in got]):
        t = j['tag']
        k, p = t.rsplit('p', 1)
        s = st['sites'][k]
        it = got.get(t)
        if not it:
            errs += 1
            it = {'tag': t, 'url': j.get('url'), 'err': 'missing in result', 'text': '', 'emails': []}
        if it.get('err'):
            errs += 1
        pg = {'url': it.get('url') or j.get('url'), 'title': it.get('title'), 'text': (it.get('text') or '')[:60000], 'emails': it.get('emails') or [], 'links': it.get('links') or [], 'err': it.get('err'), 'len': it.get('len')}
        s['pages'].append(pg)
        if p == '0':
            r = pick(s, niche)
            if r:
                s['status'] = 'found'; s['result'] = r
            else:
                q = contact_links(pg, s['url']) if not it.get('err') else []
                if not q and not it.get('err') and (it.get('len') or 0) > 2000:
                    b = urlparse(s['url'])
                    root = f'{b.scheme}://{b.netloc}'
                    q = [root + '/contact', root + '/contact-us']
                if q:
                    s['status'] = 'contact'; s['queue'] = q; s['qdone'] = 0
                else:
                    s['status'] = 'noemail'; s['reason'] = ('fetch error: ' + str(it.get('err'))[:120]) if it.get('err') else 'no email on homepage, no contact links'
        else:
            s['qdone'] = s.get('qdone', 0) + 1
            if s['qdone'] >= len(s['queue']):
                r = pick(s, niche)
                if r:
                    s['status'] = 'found'; s['result'] = r
                else:
                    s['status'] = 'noemail'; s['reason'] = 'no email on homepage+contact pages'
    # trim page text to save space after decision
    for s in st['sites'].values():
        if s['status'] in ('found', 'noemail'):
            for pg in s['pages']:
                pg.pop('links', None)
                pg['text'] = (pg.get('text') or '')[:20000] if s['status'] == 'found' else ''
    save(niche, st)
    write_outputs()
    c = {}
    for s in st['sites'].values():
        c[s['status']] = c.get(s['status'], 0) + 1
    print(bid, status, 'items', len(items), 'errs', errs, c)


def write_outputs():
    seen = set()
    for niche in ['mortgage', 'deck', 'hardscape']:
        if not os.path.exists(sp(niche)):
            continue
        st = json.load(open(sp(niche)))
        found, noemail, emails = [], [], []
        for k, s in st['sites'].items():
            r = s['rec']
            if s['status'] == 'found' and site_skip(r, niche):
                noemail.append({'placeId': r['placeId'], 'title': r['title'], 'website': r['website'], 'dom': r['dom'], 'reason': site_skip(r, niche)})
                continue
            if s['status'] == 'found':
                res = s['result']
                if res['email'] in seen:
                    # pick an alternate not yet used
                    alts = [a for a in res['alt_emails'] if a not in seen]
                    if not alts:
                        noemail.append({'placeId': r['placeId'], 'title': r['title'], 'website': r['website'], 'dom': r['dom'], 'reason': 'duplicate email ' + res['email']})
                        continue
                    res = dict(res, email=alts[0], alt_emails=[a for a in res['alt_emails'] if a != alts[0]])
                seen.add(res['email'])
                emails.append(res['email'])
                found.append({'placeId': r['placeId'], 'title': r['title'], 'website': r['website'], 'dom': r['dom'], 'city': r.get('city'), 'state': r.get('state'), 'rating': r.get('rating'), 'reviews': r.get('reviews'), 'niche': niche, **res})
            elif s['status'] in ('noemail', 'skipped'):
                noemail.append({'placeId': r['placeId'], 'title': r['title'], 'website': r['website'], 'dom': r['dom'], 'reason': s.get('reason'), 'pages_tried': [p['url'] for p in s['pages']]})
        json.dump(found, open(os.path.join(D, f'found_{niche}.json'), 'w'), indent=1)
        json.dump(noemail, open(os.path.join(D, f'noemail_{niche}.json'), 'w'), indent=1)
        with open(os.path.join(D, f'REOON_Day5_{niche}.csv'), 'w', newline='') as f:
            f.write('email\n')
            for e in emails:
                f.write(e + '\n')


def cmd_stats():
    for niche in ['mortgage', 'deck', 'hardscape']:
        if not os.path.exists(sp(niche)):
            continue
        st = json.load(open(sp(niche)))
        c = {}
        for s in st['sites'].values():
            c[s['status']] = c.get(s['status'], 0) + 1
        print(niche, c, 'inflight', list(st['inflight']))


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[0] == 'next':
        cmd_next(a[1], int(a[2]))
    elif a[0] == 'ingest':
        cmd_ingest(a[1], a[2], a[3])
    elif a[0] == 'auto':
        import glob as g
        T = '/root/.claude/projects/-home-user/97df8f00-07e4-550b-ac1b-c25c5dd29f51/tool-results/'
        files = sorted(g.glob(T + 'mcp-n8n-get_workflow_execution-*.txt'), key=os.path.getmtime)[-40:]
        idx = {}
        for f in files:
            try:
                with open(f) as fh:
                    head = fh.read(300)
                m = re.search(r'"id":\s*"(\d+)"', head)
                if m: idx[m.group(1)] = f
            except Exception:
                pass
        for pair in a[2:]:
            bid, ex = pair.split(':')
            if ex in idx:
                cmd_ingest(a[1], idx[ex], bid)
            else:
                print('no file for', bid, ex)
    elif a[0] == 'rerank':
        for niche in a[1:]:
            st = load(niche); ch = 0
            for s_ in st['sites'].values():
                if s_['status'] in ('found', 'noemail') and s_['pages']:
                    old = s_.get('result')
                    r = pick(s_, niche)
                    if r and old and r['email'] == old['email'] and not r['first_name'] and old.get('first_name'):
                        on = old['first_name']; loc = r['email'].split('@')[0]
                        if is_person(loc) and re.split(r'[._-]', loc)[0].capitalize() == on and on not in STOPNAMES:
                            r['first_name'] = on
                    if r:
                        if not old or old['email'] != r['email'] or old.get('first_name') != r['first_name']: ch += 1
                        s_['status'] = 'found'; s_['result'] = r
                    elif s_['status'] == 'found':
                        s_['status'] = 'noemail'; s_['reason'] = 'only email(s) rejected on review'; s_.pop('result', None); ch += 1
            save(niche, st); print(niche, 'changed', ch)
        write_outputs()
    elif a[0] == 'repick':
        for niche in a[1:]:
            st = load(niche); n = 0
            for s_ in st['sites'].values():
                if s_['status'] == 'noemail' and s_['pages']:
                    r = pick(s_, niche)
                    if r:
                        s_['status'] = 'found'; s_['result'] = r; n += 1
            save(niche, st); print(niche, 'repicked', n)
        write_outputs()
    elif a[0] == 'requeue':
        st = load(a[1]); print(st['inflight'].pop(a[2], None)); save(a[1], st)
    elif a[0] == 'out':
        write_outputs()
    elif a[0] == 'stats':
        cmd_stats()
