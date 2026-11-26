# Daily Google Maps lead supply (Neal, Nov 26): never pay for a place we already have, front-load the Apify
# budget so deck keeps >=100 new leads/day, steer spend to the best usable-per-$ areas, and warn early.
#
#   python3 lead_supply.py budget                 -> Apify $ left, days to reset, today's allowance
#   python3 lead_supply.py scrape <workdir>       -> pick areas, run the cheap actor with excludeCids, update registry
#   python3 lead_supply.py verify <workdir> [max_credits]  -> Reoon via n8n (publish EWA6SgxsdzJUjXa8 first), keeps safe/catch_all/role
#   python3 lead_supply.py screen <workdir> <idx.json> <dnc.json>
#                                                 -> winning-recipe screen + dedupe -> REOON_GM_<DATE>_{DECK,HARDSCAPE}.csv
#
# Registry and area queue live in the Apify key-value store fo-lead-supply (records "registry", "areas").
# Apify calls rely on the session's network proxy adding the Apify credential (cloud environment).
# excludeCids is free: tested Nov 26, excluded places are skipped and NOT charged; the actor returns deeper,
# unseen places instead. So every run passes every known CID.
import json, os, re, subprocess, sys, time, datetime, collections, html, gzip

STORE = 'Ca6Cu8iAJ7xQuGtFv'                      # Apify KV store fo-lead-supply
ACTOR = 'santamaria-automations~google-maps-scraper'  # $1 / 1,000 places, no filter surcharge
API = 'https://api.apify.com/v2'
BUFFER_USD = 2.0                                  # never spend the last $2 of the cycle (Neal, Nov 26)
FRONT = 0.30                                      # spend up to 30% of what's left each day (front-loaded), never less than the even pace
SPLIT = {'deck': 0.85, 'hardscape': 0.15}
TERMS = {'deck': ['deck builder', 'deck contractor', 'deck company', 'deck installer'],   # last two added Nov 26 (Neal); drop if usable-per-$ is clearly worse
         'hardscape': ['hardscape contractor', 'paver installer']}
PER_QUERY = 60                                    # places per search (excluded places don't count or cost)
COST_PER_PLACE = 0.001
LOG_HOOK = 'https://exaltisgroup.app.n8n.cloud/webhook/fo-supply-log-7q2k'
REOON_HOOK = 'https://exaltisgroup.app.n8n.cloud/webhook/fo-reoon-verify-3k9d'   # n8n EWA6SgxsdzJUjXa8; publish only while verifying
KEEP_STATUS = {'safe', 'catch_all', 'role_account'}
FB_LOOKUP = False   # Nov 26 test: facebook.com returns its "Sorry, something went wrong" page to our fetcher (www and m.), so it's off
PIPE = os.path.dirname(os.path.abspath(__file__))


def api(method, path, body=None, timeout=300):
    cmd = ['curl', '-sS', '-m', str(timeout), '-X', method, API + path]
    inp = None
    if body is not None:
        cmd[6:6] = ['-H', 'Content-Type: application/json', '--data-binary', '@-']
        inp = json.dumps(body, separators=(',', ':')).encode()
    for a in range(5):                            # the proxy sometimes drops a connection mid-request
        p = subprocess.run(cmd, input=inp, capture_output=True)
        if p.returncode == 0 and not p.stdout.strip() and method == 'PUT':
            return {}
        try:
            return json.loads(p.stdout)
        except Exception:
            time.sleep(5 * (a + 1))
    raise SystemExit(f'Apify {method} {path} failed: {p.stdout[:300]!r}')


def kv_get(key):
    if key == 'registry':                         # stored gzipped (1.5 MB of JSON drops through the proxy)
        p = subprocess.run(['curl', '-sS', '-m', '300', f'{API}/key-value-stores/{STORE}/records/registry.gz'], capture_output=True)
        return json.loads(gzip.decompress(p.stdout))
    return api('GET', f'/key-value-stores/{STORE}/records/{key}')


def kv_put(key, obj):
    if key == 'registry':
        data = gzip.compress(json.dumps(obj, separators=(',', ':')).encode())
        for a in range(4):
            p = subprocess.run(['curl', '-sS', '-m', '300', '-X', 'PUT', '-H', 'Content-Type: application/octet-stream', '--data-binary', '@-',
                                f'{API}/key-value-stores/{STORE}/records/registry.gz'], input=data, capture_output=True)
            if p.returncode == 0:
                back = kv_get('registry')
                if len(back.get('cids', {})) == len(obj['cids']):
                    return
            time.sleep(5 * (a + 1))
        raise SystemExit('registry save failed or did not verify')
    api('PUT', f'/key-value-stores/{STORE}/records/{key}', obj)


def log(rows):
    try:
        subprocess.run(['curl', '-sS', '-m', '60', '-X', 'POST', '-H', 'Content-Type: application/json', '--data-binary', '@-', LOG_HOOK],
                       input=json.dumps({'rows': rows}).encode(), capture_output=True)
    except Exception:
        pass


def budget():
    d = api('GET', '/users/me/limits')['data']
    used = d['current']['monthlyUsageUsd']; cap = d['limits']['maxMonthlyUsageUsd']
    end = datetime.datetime.fromisoformat(d['monthlyUsageCycle']['endAt'].replace('Z', '+00:00'))
    now = datetime.datetime.now(datetime.timezone.utc)
    days = max(1, (end.date() - now.date()).days + 1)
    left = cap - used
    spendable = max(0.0, left - BUFFER_USD)
    allow = min(spendable, max(spendable / days, spendable * FRONT))
    return {'used': round(used, 2), 'cap': cap, 'left': round(left, 2), 'reset': (end + datetime.timedelta(seconds=1)).date().isoformat(),
            'days_to_reset': days, 'allowance_today': round(allow, 2)}


def to_compass(x, niche):
    a = x.get('complete_address') or {}
    return {'placeId': x.get('place_id'), 'cid': str(x.get('cid') or ''), 'title': x.get('title'), 'categoryName': x.get('category'),
            'totalScore': x.get('review_rating'), 'reviewsCount': x.get('review_count'), 'website': x.get('website'), 'phone': x.get('phone'),
            'city': a.get('city'), 'state': a.get('state'), 'countryCode': x.get('country_iso'),
            'permanentlyClosed': (x.get('status') or 'OPERATIONAL') != 'OPERATIONAL', 'temporarilyClosed': False,
            'searchString': x.get('searchString') or x.get('company_id'), 'niche': niche}


def pick_areas(A, niche, n):
    """Unsearched counties first, ranked by the usable-per-$ of their state so far (unknown states get the average),
    then by how many searched (affluent) counties border them."""
    st = A[niche].setdefault('state_yield', {})
    rates = [v['usable'] / v['usd'] for v in st.values() if v.get('usd', 0) >= 0.05]
    avg = sum(rates) / len(rates) if rates else 1.0
    q = [a for a in A[niche]['queue'] if a not in A[niche]['avoid'] and a not in A[niche]['done']]
    def rate(a):
        v = st.get(a.split(', ')[-1])
        return v['usable'] / v['usd'] if v and v.get('usd', 0) >= 0.05 else avg
    return sorted(q, key=lambda a: -rate(a))[:n]


def scrape(W, max_usd=None):
    os.makedirs(W, exist_ok=True)
    b = budget(); allow = b['allowance_today'] if max_usd is None else min(max_usd, b['allowance_today'])
    reg = kv_get('registry'); A = kv_get('areas'); cids = reg['cids']
    today = datetime.date.today().isoformat()
    if A.get('last_scrape') == today and not os.environ.get('FORCE_SCRAPE'):   # one paid scrape per day, even if fired twice
        return {'skipped': f'already scraped today ({today})', 'budget': b}
    known = list(cids.keys()); known_set = set(known)
    runs = []
    for niche, share in SPLIT.items():
        usd = round(allow * share, 2)
        # what one county actually costs (Google returns far fewer than PER_QUERY places for most searches)
        per_area = A[niche].get('avg_area_cost') or PER_QUERY * len(TERMS[niche]) * COST_PER_PLACE * 0.3
        pick = pick_areas(A, niche, max(1, int(usd // per_area)))
        if not pick or usd < 0.05:
            continue
        inp = {'searchStrings': [f'{t} in {a}' for a in pick for t in TERMS[niche]], 'maxResultsPerQuery': PER_QUERY,
               'maxTotalResults': int(usd / COST_PER_PLACE), 'language': 'en', 'includeReviewCount': True, 'areaTiling': 'off', 'excludeCids': known}
        r = api('POST', f'/acts/{ACTOR}/runs?maxTotalChargeUsd={usd}', inp)['data']
        runs.append({'niche': niche, 'areas': pick, 'id': r['id'], 'ds': r['defaultDatasetId'], 'cap_usd': usd})
    for r in runs:                                    # wait for every run
        for _ in range(240):
            d = api('GET', f"/actor-runs/{r['id']}")['data']
            if d['status'] not in ('READY', 'RUNNING'):
                break
            time.sleep(20)
        r['status'] = d['status']; r['cost'] = round(d.get('usageTotalUsd') or 0, 4)
        items = api('GET', f"/datasets/{r['ds']}/items?clean=true&limit=20000")
        r['places'] = len(items)
        new = [x for x in items if str(x.get('cid') or '') not in known_set]
        r['new_places'] = len(new); r['known_returned'] = r['places'] - len(new)   # should be ~0: known places are excluded
        today = datetime.date.today().isoformat()
        for x in items:
            cids.setdefault(str(x.get('cid') or ''), [r['niche'][0], today])
        json.dump([to_compass(x, r['niche']) for x in new], open(os.path.join(W, f"raw_{r['niche']}.json"), 'w'))
        got = collections.Counter((x.get('searchString') or '').split(' in ', 1)[-1] for x in items)
        searched = {(x.get('searchString') or '').split(' in ', 1)[-1] for x in items}
        for a in r['areas']:
            if a in searched or r['status'] == 'SUCCEEDED':
                A[r['niche']]['done'].append(a)
                A[r['niche']]['queue'] = [z for z in A[r['niche']]['queue'] if z != a]
                if got.get(a, 0) == 0:
                    A[r['niche']]['avoid'].append(a)
        r['places_per_area'] = dict(got)
        if r['areas'] and r['cost']:
            prev = A[r['niche']].get('avg_area_cost')
            cur = r['cost'] / len(r['areas'])
            A[r['niche']]['avg_area_cost'] = round(cur if not prev else 0.5 * prev + 0.5 * cur, 4)
    reg['cids'] = cids; reg['updated'] = today; A['last_scrape'] = today
    kv_put('registry', reg); kv_put('areas', A)
    json.dump(runs, open(os.path.join(W, 'runs.json'), 'w'), indent=1)
    return {'budget': b, 'allowance_used': allow, 'runs': runs, 'registry_size': len(cids),
            'queue_left': {n: len(A[n]['queue']) for n in A}}


def screen(W, idx_path, dnc_path):
    """Exact Nov 21 winning-recipe screen (screen.py rules), plus deeper contact pages, Cloudflare email decode
    and ads tags. Needs the page gateway (fo-page-fetch-x81k2) published while it runs."""
    sys.path.insert(0, PIPE)
    os.environ['FETCH_CACHE'] = os.path.join(W, 'pages.jsonl'); os.environ['FETCH_KEEP_HTML'] = '1'
    src = open(os.path.join(PIPE, 'screen.py')).read().split("\nstage=sys.argv[2]")[0]
    src = src.replace("W=sys.argv[1]; os.environ.setdefault('FETCH_CACHE',os.path.join(W,'pages.jsonl'))", "")
    g = {'__file__': os.path.join(PIPE, 'screen.py'), '__name__': 'screenlib'}
    exec(compile(src, 'screen.py', 'exec'), g)
    from dedupe_index import ck, ph
    F = g['fetch']; norm_url = g['norm_url']; host_dom = g['host_dom']; contact_links = g['contact_links']
    FREE = g['FREE']; is_person = g['is_person']
    IDX = json.load(open(idx_path)); DN = json.load(open(dnc_path))
    E = set(IDX['E']) | set(DN.get('E', [])); D = set(IDX['D']) | set(DN.get('D', []))
    C = set(IDX['C']) | {ck(k) for k in DN.get('K', []) if len(ck(k)) >= 5}; PH = set(IDX.get('PH') or IDX.get('P') or [])
    CHAIN = g['CHAIN']; site_skip = g['site_skip']
    date = datetime.date.today().strftime('%b%d').upper()
    report = {}
    for niche in ('deck', 'hardscape'):
        raw = []
        for fn_ in (f'raw_{niche}.json', f'raw_retry_{niche}.json'):   # today's new places + weekly retry of unreadable sites
            fp = os.path.join(W, fn_)
            if os.path.exists(fp):
                raw += [dict(x, _retry=fn_.startswith('raw_retry')) for x in json.load(open(fp))]
        if not raw:
            continue
        rej = collections.Counter(); pre = []; via = collections.Counter(); unread = []; back = []
        for x in raw:
            if x['permanentlyClosed']: rej['closed'] += 1; continue
            if (x['countryCode'] or 'US') != 'US': rej['not US'] += 1; continue
            if (x['totalScore'] or 0) < 4.3 or (x['reviewsCount'] or 0) < 20: rej['rating<4.3 or <20 reviews'] += 1; continue
            w = x.get('website') or ''
            if not w or site_skip({'website': norm_url(w), 'title': x['title'] or '', 'cat': x['categoryName']}, niche): rej['no real website'] += 1; continue
            if CHAIN.search(x['title'] or ''): rej['chain'] += 1; continue
            pre.append(x)
        urls = []
        for x in pre:
            u = norm_url(x['website']); base = re.match(r'https?://[^/]+', u).group(0)
            urls += [u] + [base + p for p in ('/contact', '/contact-us', '/about', '/about-us', '/free-estimate', '/get-a-quote', '/estimate')]
        P = F.run(urls); P = F.run(urls, refetch_errors=True)
        more = []
        for x in pre:
            u = norm_url(x['website']); pg = P.get(u)
            if pg and not pg.get('err'):
                pg['url'] = pg.get('url') or u; more += contact_links(pg, u)
        P = F.run(more)
        # the company's OWN Facebook page, when its website links to it (used only if the site publishes no email)
        FB = re.compile(r'https?://(?:www\.|m\.)?facebook\.com/(?!sharer|share|plugins|tr\b|dialog|events|groups|watch|photo)[A-Za-z0-9.\-_/%]+', re.I)
        fbmap = {}
        for x in pre:
            pg = P.get(norm_url(x['website']))
            if pg and not pg.get('err'):
                links = [l.get('u') or '' for l in (pg.get('links') or [])] + FB.findall(pg.get('html') or '')
                fb = [l.split('?')[0].rstrip('/') for l in links if FB.match(l or '')]
                if fb: fbmap[x['placeId']] = fb[0]
        if FB_LOOKUP:
            P = F.run(list(set(fbmap.values())))
        else:
            fbmap = {}
        ok = lambda q: q and not q.get('err') and int(q.get('len') or 0) >= 500
        keep = []; sE = set(); sC = set(); sP = set(); sW = set()
        for x in pre:
            u = norm_url(x['website']); base = re.match(r'https?://[^/]+', u).group(0); home = P.get(u)
            if not ok(home):
                rej['site unreadable'] += 1; unread.append({k: v for k, v in x.items() if k != '_retry'}); continue
            home['url'] = home.get('url') or u; pages = [home]
            if x.get('_retry'): back.append(x['placeId'])
            for l in dict.fromkeys(contact_links(home, u) + [base + p for p in ('/contact', '/contact-us', '/about', '/about-us', '/free-estimate', '/get-a-quote', '/estimate')]):
                q = P.get(l)
                if ok(q) and q is not home: q['url'] = q.get('url') or l; pages.append(q)
            for pgx in list(pages):                     # Cloudflare-protected emails: decode the published address
                for h in re.findall(r'data-cfemail="([0-9a-fA-F]+)"', pgx.get('html') or ''):
                    k0 = int(h[:2], 16); e0 = ''.join(chr(int(h[i:i + 2], 16) ^ k0) for i in range(2, len(h), 2))
                    pages.append({'url': pgx.get('url'), 'emails': [e0], 'text': '', 'title': ''})
            text = ' '.join(p.get('text') or '' for p in pages)
            if g['SUPPLIER'].search((x.get('title') or '') + ' ' + (home.get('title') or '')): rej['supplier'] += 1; continue
            if g['FRANCH'].search(text): rej['franchise'] += 1; continue
            okn, why = g['niche_ok'](niche, x, pages)
            if not okn: rej[why] += 1; continue
            if not g['site_match'](x, pages): rej["site doesn't match listing"] += 1; continue
            r = g['pick']({'url': u, 'rec': {'dom': host_dom(u)}, 'pages': pages}, niche)
            src_ = 'retry' if x.get('_retry') else ('cloudflare' if r and any(p.get('url') == r.get('source_url') and not p.get('text') for p in pages) else 'site')
            if not r and x['placeId'] in fbmap:      # their own Facebook page; same email rules (own domain or free mailbox)
                fbp = P.get(fbmap[x['placeId']])
                if ok(fbp):
                    fbp['url'] = fbmap[x['placeId']]
                    r = g['pick']({'url': u, 'rec': {'dom': host_dom(u)}, 'pages': [fbp]}, niche)
                    src_ = 'facebook'
                else:
                    via['facebook_unreadable'] += 1
            if not r: rej['no email published'] += 1; continue
            e = r['email'].lower(); ed = e.split('@')[1]; wd = host_dom(u).replace('www.', '')
            if g['JUNK'].search(e.split('@')[0]) or g['JUNK'].search(e): rej['junk email'] += 1; continue
            k = ck(x.get('title')); p10 = ph(x.get('phone'))
            if e in E or (ed not in FREE and ed in D) or wd in D or (len(k) >= 5 and k in C) or (p10 and p10 in PH): rej['already emailed / DNC'] += 1; continue
            if e in sE or (k and k in sC) or (p10 and p10 in sP) or wd in sW: rej['duplicate in batch'] += 1; continue
            sE.add(e); sC.add(k); sW.add(wd); p10 and sP.add(p10)
            hom = home.get('html') or ''
            ads_g = 'yes' if re.search(r'AW-\d{6,}|googleadservices|gtag/js\?id=AW', hom) else ('no' if hom else 'unknown')
            ads_m = 'yes' if re.search(r'fbq\(|fbevents\.js', hom) else ('no' if hom else 'unknown')
            fn = r.get('first_name') or ''; oe = ''
            if fn and re.search(re.escape(fn) + r"[^.]{0,60}\b(owner|founder|president|ceo)\b", text, re.I): oe = f'{fn} named as owner/founder on site'
            rc = x.get('reviewsCount') or 0
            via[src_] += 1
            keep.append({'found_via': src_, 'email': e, 'company': x.get('title'), 'first_name': fn, 'phone': x.get('phone'), 'website': u, 'city': x.get('city'), 'state': x.get('state'),
                         'country': 'US', 'niche': niche, 'categoryName': x.get('categoryName'), 'placeId': x['placeId'], 'source': 'google_maps', 'segment': 'affluent_county',
                         'source_url': f"https://www.google.com/maps/place/?q=place_id:{x['placeId']}", 'searchString': x.get('searchString'),
                         'email_found_on': r.get('source_url'), 'owner_name': fn if oe else '', 'owner_evidence': oe, 'rating': x.get('totalScore'), 'reviews': rc,
                         'ads_google': ads_g, 'ads_meta': ads_m, 'homepage_title': html.unescape(home.get('title') or ''),
                         'named_inbox': is_person(e.split('@')[0])})
        if niche == 'deck':
            keep.sort(key=lambda z: (0 if (z['categoryName'] == 'Deck builder' and (z['reviews'] or 0) >= 35) else 1 if (z['reviews'] or 0) >= 35 else 2))
        tag = 'DECK' if niche == 'deck' else 'HARDSCAPE'
        out = os.path.join(os.path.dirname(PIPE), '..', f'REOON_GM_{date}_{tag}.csv')
        with open(os.path.abspath(out), 'w') as f:
            f.write('email\n' + ''.join(k['email'] + '\n' for k in keep))
        json.dump(keep, open(os.path.join(W, f'srcs_GM_{date}_{tag}.json'), 'w'), indent=1)
        phrase = collections.Counter(k['searchString'].split(' in ', 1)[0] for k in keep if k.get('searchString'))
        area = collections.Counter(k['searchString'].split(' in ', 1)[-1] for k in keep if k.get('searchString'))
        report[niche] = {'raw_new': len(raw), 'prefilter_pass': len(pre), 'usable': len(keep), 'file': os.path.abspath(out), 'rejected': dict(rej),
                         'found_via': dict(via), 'usable_by_phrase': dict(phrase), 'usable_by_area': dict(area),
                         'places_by_phrase': dict(collections.Counter((x.get('searchString') or '').split(' in ', 1)[0] for x in raw if not x.get('_retry'))),
                         'unreadable': len(unread)}
        report[niche]['_unread'] = unread; report[niche]['_back'] = back; report[niche]['retry_sites_back'] = len(back)
    # learn: usable per $ by state (steers tomorrow's county picks), unreadable places for the weekly retry, log rows
    A = kv_get('areas'); runs = json.load(open(os.path.join(W, 'runs.json'))) if os.path.exists(os.path.join(W, 'runs.json')) else []
    U = api('GET', f'/key-value-stores/{STORE}/records/unreadable')
    U = U if isinstance(U, dict) and 'error' not in U else {}
    today = datetime.date.today().isoformat(); rows = []
    for r in runs:
        n = r['niche']; rep = report.get(n, {})
        for a, places in (r.get('places_per_area') or {}).items():
            usd = places * COST_PER_PLACE; us = rep.get('usable_by_area', {}).get(a, 0); stt = a.split(', ')[-1]
            sy = A[n].setdefault('state_yield', {}).setdefault(stt, {'usd': 0, 'usable': 0})
            sy['usd'] = round(sy['usd'] + usd, 4); sy['usable'] += us
            rows.append({'date': today, 'niche': n, 'area': a, 'places': places, 'cost_usd': round(usd, 4), 'usable': us, 'run_id': r['id']})
    for n, rep in report.items():
        for k in rep.pop('_back', []):
            U.pop(k, None)
        for x in rep.pop('_unread', []):
            e = U.setdefault(x['placeId'], {'place': x, 'first_failed': today})
            e['last_try'] = today; e['tries'] = e.get('tries', 0) + 1
    kv_put('areas', A); kv_put('unreadable', U)
    log(rows + [{'date': today, 'niche': n, 'area': '(by phrase) ' + ph_, 'places': rep['places_by_phrase'].get(ph_, 0),
                 'cost_usd': round(rep['places_by_phrase'].get(ph_, 0) * COST_PER_PLACE, 4), 'usable': rep['usable_by_phrase'].get(ph_, 0), 'run_id': ''}
                for n, rep in report.items() for ph_ in set(rep['places_by_phrase']) | set(rep['usable_by_phrase'])])
    b = budget()
    daily = {'date': today, 'apify_left_usd': b['left'], 'days_to_reset': b['days_to_reset'],
             'spent_today_usd': round(sum(r.get('cost', 0) for r in runs), 2),
             'deck_usable': report.get('deck', {}).get('usable', 0), 'hardscape_usable': report.get('hardscape', {}).get('usable', 0),
             'registry_size': len(kv_get('registry')['cids']), 'warning': ''}
    try:
        subprocess.run(['curl', '-sS', '-m', '60', '-X', 'POST', '-H', 'Content-Type: application/json', '--data-binary', '@-', LOG_HOOK],
                       input=json.dumps({'daily': [daily]}).encode(), capture_output=True)
    except Exception:
        pass
    report['daily'] = daily
    json.dump(report, open(os.path.join(W, 'screen_report.json'), 'w'), indent=1)
    return report


def prep_retry(W, days=7):
    """Weekly: write places whose site was unreadable >= `days` ago into raw_retry_<niche>.json (sites come back)."""
    U = api('GET', f'/key-value-stores/{STORE}/records/unreadable')
    U = U if isinstance(U, dict) and 'error' not in U else {}
    cut = (datetime.date.today() - datetime.timedelta(days=days)).isoformat(); out = collections.defaultdict(list)
    for k, v in U.items():
        if v.get('last_try', '') <= cut and v.get('tries', 0) < 4:
            out[v['place'].get('niche', 'deck')].append(v['place'])
    for n, xs in out.items():
        json.dump(xs, open(os.path.join(W, f'raw_retry_{n}.json'), 'w'))
    return {n: len(xs) for n, xs in out.items()}


def verify(W, max_credits=480):
    """Reoon-verify today's sidecars (best-first, deck before hardscape) without exceeding max_credits
    (Reoon daily limit is 500). Keep safe + catch_all + role_account. Writes READY_GM_<DATE>_<TAG>.json in W."""
    date = datetime.date.today().strftime('%b%d').upper(); used = 0; out = {}
    for tag in ('DECK', 'HARDSCAPE'):
        fp = os.path.join(W, f'srcs_GM_{date}_{tag}.json')
        if not os.path.exists(fp):
            continue
        rows = json.load(open(fp)); todo = [r for r in rows if not r.get('reoon')]
        for i in range(0, len(todo), 25):
            chunk = todo[i:i + 25][:max(0, max_credits - used)]
            if not chunk:
                break
            res = []
            for a in range(3):
                p = subprocess.run(['curl', '-sS', '-m', '600', '-X', 'POST', '-H', 'Content-Type: application/json', '--data-binary', '@-', REOON_HOOK],
                                   input=json.dumps({'emails': [r['email'] for r in chunk]}).encode(), capture_output=True)
                try:
                    res = json.loads(p.stdout); break
                except Exception:
                    time.sleep(10)
            st = {x['email']: x['status'] for x in res if isinstance(x, dict)}
            for r in chunk:
                r['reoon'] = st.get(r['email'], '')
            used += len(chunk)
        json.dump(rows, open(fp, 'w'), indent=1)
        ready = [r for r in rows if r.get('reoon') in KEEP_STATUS]
        json.dump(ready, open(os.path.join(W, f'READY_GM_{date}_{tag}.json'), 'w'), indent=1)
        out[tag] = {'rows': len(rows), 'verified': sum(1 for r in rows if r.get('reoon')), 'ready': len(ready),
                    'status': dict(collections.Counter(r.get('reoon') or 'not verified' for r in rows))}
    out['credits_used'] = used
    return out


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'budget':
        print(json.dumps(budget(), indent=1))
    elif cmd == 'scrape':
        print(json.dumps(scrape(sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else None), indent=1, default=str))
    elif cmd == 'verify':
        print(json.dumps(verify(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 480), indent=1))
    elif cmd == 'prep_retry':
        print(json.dumps(prep_retry(sys.argv[2])))
    elif cmd == 'screen':
        print(json.dumps(screen(sys.argv[2], sys.argv[3], sys.argv[4]), indent=1))
