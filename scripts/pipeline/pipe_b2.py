import json, os, re, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pipe
from pipe import *
D = pipe.D
N2 = 600
NICHES = ['mortgage', 'deck', 'hardscape']

def sp2(niche):
    return os.path.join(D, f'state_b2_{niche}.json')
pipe.sp = sp2
EXTRA_NATIONAL = ['cmg-homeloans.com','phmloans.com','allwestern.com','megastarfinancial.com','megastar.myportal.loan','afncorp.com','annie-mac.com','alcova.com','lennarmortgage.com','townebankmortgage.com','renasantbank.com','gatewayfirst.com','uhm.com','flatbranchhomeloans.com','interlincmortgage.com','americansenior.com','zillow.com','my1003app.com','angeloakms.com','usamortgage.com','gmccloan.com','mutualmortgage.com','homesteadfunding.com','highlandsmortgage.com','steadfastmortgage.com','summit-mortgage.com','clearmortgagecapital.com','veritymortgage.com','coast2coastmortgage.com','westcapitallending.com','homespirehomeloans.com','altitudehomeloans.com','sociable.mortgage','johnscreekmortgage.com','lenderexpressmortgage.com','lunalendingdenver.com','insightmortgagesolutions.com','thelendingcollective.com','emetropolitan.com','linqapp.com','calendly.com','blink.mortgage']
for _n in EXTRA_NATIONAL:
    if _n not in pipe.NATIONAL: pipe.NATIONAL.append(_n)

def _norm_dom(d):
    d = (d or '').lower().strip()
    return d[4:] if d.startswith('www.') else d

def old_excl():
    pids, doms, emails = set(), set(), set()
    for n in NICHES:
        st = json.load(open(os.path.join(D, f'state_{n}.json')))
        for s in st['sites'].values():
            pids.add(s['rec']['placeId'])
        for fn in (f'found_{n}.json', f'noemail_{n}.json'):
            for r in json.load(open(os.path.join(D, fn))):
                pids.add(r['placeId'])
    for f in glob.glob(os.path.join(D, 'found_*.json')):
        if os.path.basename(f).startswith('found_b2_'):
            continue
        for r in json.load(open(f)):
            doms.add(_norm_dom(r.get('dom') or host_dom(norm_url(r.get('website')))))
            if r.get('email'): emails.add(r['email'].lower())
            for a in r.get('alt_emails') or []: pass
    for r in json.load(open(os.path.join(D, 'day5_final.json'))):
        doms.add(_norm_dom(host_dom(norm_url(r.get('website')))))
        if r.get('email'): emails.add(r['email'].lower())
    doms.discard('')
    return pids, doms, emails

def load2(niche):
    if os.path.exists(sp2(niche)):
        return json.load(open(sp2(niche)))
    pids, doms, _ = old_excl()
    pool = json.load(open(os.path.join(D, f'pool_{niche}.json')))
    sel = []
    for r in pool:
        if r['placeId'] in pids: continue
        d = _norm_dom(r.get('dom') or host_dom(norm_url(r.get('website'))))
        if d in doms: continue
        sel.append(r)
        if len(sel) >= N2: break
    st = {'sites': {}, 'batch_seq': 0, 'inflight': {}}
    for i, r in enumerate(sel):
        k = f'{niche[0]}x{i}'
        s = {'rec': r, 'url': norm_url(r['website']), 'status': 'pending', 'pages': [], 'queue': []}
        why = site_skip(r, niche)
        if why:
            s['status'] = 'skipped'; s['reason'] = why
        st['sites'][k] = s
    return st
pipe.load = load2

def write2():
    _, _, old_emails = old_excl()
    seen = set(old_emails)
    for niche in NICHES:
        if not os.path.exists(sp2(niche)):
            continue
        st = json.load(open(sp2(niche)))
        found, noemail, emails = [], [], []
        for k, s in st['sites'].items():
            r = s['rec']
            base = {'placeId': r['placeId'], 'title': r['title'], 'website': r['website'], 'dom': r['dom']}
            if s['status'] == 'found' and site_skip(r, niche):
                noemail.append({**base, 'reason': site_skip(r, niche)}); continue
            if s['status'] == 'found':
                res = s['result']
                if res['email'] in seen:
                    alts = [a for a in res['alt_emails'] if a not in seen]
                    if not alts:
                        noemail.append({**base, 'reason': 'duplicate email ' + res['email']}); continue
                    res = dict(res, email=alts[0], alt_emails=[a for a in res['alt_emails'] if a != alts[0]])
                seen.add(res['email'])
                emails.append(res['email'])
                found.append({**base, 'city': r.get('city'), 'state': r.get('state'), 'rating': r.get('rating'), 'reviews': r.get('reviews'), 'niche': niche, **res})
            elif s['status'] in ('noemail', 'skipped'):
                noemail.append({**base, 'reason': s.get('reason'), 'pages_tried': [p['url'] for p in s['pages']]})
        json.dump(found, open(os.path.join(D, f'found_b2_{niche}.json'), 'w'), indent=1)
        json.dump(noemail, open(os.path.join(D, f'noemail_b2_{niche}.json'), 'w'), indent=1)
        with open(os.path.join(D, f'REOON_B2_{niche}.csv'), 'w', newline='') as f:
            f.write('email\n')
            for e in emails:
                f.write(e + '\n')
pipe.write_outputs = lambda: None  # B3: never rewrite batch-2 files during ingest

def b3_start_found():
    p = os.path.join(D, 'b2_backup', 'state_b2_%s.json')
    out = {}
    for n in NICHES:
        st = json.load(open(p % n))
        out[n] = {k for k, s in st['sites'].items() if s['status'] in ('found', 'noemail', 'skipped')}
    return out

def write3():
    excl = set()
    for f in glob.glob(os.path.join(D, 'REOON_B2_*.csv')):
        excl |= {l.strip().lower() for l in open(f) if l.strip() and l.strip() != 'email'}
    for f in glob.glob(os.path.join(D, 'found_*.json')):
        if os.path.basename(f).startswith('found_b3_'): continue
        for r in json.load(open(f)):
            if r.get('email'): excl.add(r['email'].lower())
    for r in json.load(open(os.path.join(D, 'day5_final.json'))):
        if r.get('email'): excl.add(r['email'].lower())
    done_b2 = b3_start_found()
    seen = set(excl); summ = {}
    for niche in NICHES:
        st = json.load(open(sp2(niche)))
        found, emails, nsites = [], [], 0
        for k, s in st['sites'].items():
            if k in done_b2[niche] or s['status'] not in ('found', 'noemail', 'skipped'): continue
            nsites += 1
            if s['status'] != 'found' or site_skip(s['rec'], niche): continue
            r = s['rec']; res = s['result']
            cands = [res['email']] + list(res.get('alt_emails') or [])
            pick_ = next((c for c in cands if c and c.lower() not in seen), None)
            if not pick_: continue
            seen.add(pick_.lower()); emails.append(pick_.lower())
            found.append({'placeId': r['placeId'], 'title': r['title'], 'website': r['website'], 'dom': r['dom'], 'city': r.get('city'), 'state': r.get('state'), 'rating': r.get('rating'), 'reviews': r.get('reviews'), 'niche': niche, **dict(res, email=pick_, alt_emails=[a for a in cands if a != pick_])})
        json.dump(found, open(os.path.join(D, f'found_b3_{niche}.json'), 'w'), indent=1)
        with open(os.path.join(D, f'REOON_B3_{niche}.csv'), 'w', newline='') as f:
            f.write('email\n')
            for e in emails: f.write(e + '\n')
        summ[niche] = (nsites, len(emails))
    print('B3 sites_done/new_emails', summ)

T = '/root/.claude/projects/-home-user/97df8f00-07e4-550b-ac1b-c25c5dd29f51/tool-results/'
def auto(pairs):
    files = sorted(glob.glob(T + 'mcp-n8n-get_workflow_execution-*.txt') + glob.glob(T + 'toolu_*.txt'), key=os.path.getmtime)[-250:]
    idx = {}
    for f in files:
        try:
            with open(f) as fh: head = fh.read(300)
            m = re.search(r'"id":\s*"(\d+)"', head)
            if m: idx[m.group(1)] = f
        except Exception: pass
    for pair in pairs:
        bid, ex = pair.split(':', 1)
        n = re.sub(r'B\d+$', '', bid)
        if os.path.exists(ex) or ex in idx:
            path = ex if os.path.exists(ex) else idx[ex]
            try:
                d = json.load(open(path)); rd = d['data']['resultData']['runData']
                if 'Prep Pages' not in rd and 'Fetch Page' in rd:
                    jobs = load2(n)['inflight'].get(bid) or []
                    nf = len(rd['Fetch Page'][0]['data']['main'][0])
                    if len(jobs) == nf:
                        rd['Prep Pages'] = [{'data': {'main': [[{'json': j} for j in jobs]]}}]
                        path = os.path.join(D, '_ing_tmp.json'); json.dump(d, open(path, 'w'))
                    else:
                        print('fetch/job count mismatch', nf, len(jobs))
            except Exception as e:
                print('prep inject fail', e)
            pipe.cmd_ingest(n, path, bid)
        else: print('no file for', bid, ex)

def nxt(niche, nb):
    st = load2(niche)
    inflight_keys = {j['tag'] for b in st['inflight'].values() for j in b}
    jobs = []
    for k, s in st['sites'].items():
        if s['status'] == 'pending' and f'{k}p0' not in inflight_keys:
            jobs.append({'tag': f'{k}p0', 'url': s['url']})
        elif s['status'] == 'contact':
            for i, u in enumerate(s['queue']):
                if i < s.get('qdone', 0): continue
                t = f'{k}p{i+1}'
                if t not in inflight_keys: jobs.append({'tag': t, 'url': u})
    BS = int(os.environ.get('BS', '10'))
    for b in range(nb):
        chunk = jobs[b*BS:(b+1)*BS]
        if not chunk: break
        st['batch_seq'] += 1
        bid = f'{niche}B{st["batch_seq"]}'
        st['inflight'][bid] = chunk
        fp = os.path.join(D, 'b3_payloads', bid + '.json'); os.makedirs(os.path.dirname(fp), exist_ok=True)
        json.dump({'method': 'POST', 'body': {'lean': True, 'batch': chunk}}, open(fp, 'w'), separators=(',', ':'))
        print(bid, len(chunk), fp)
    save(niche, st)

def stats():
    for n in NICHES:
        if not os.path.exists(sp2(n)): continue
        st = json.load(open(sp2(n))); c = {}
        for s in st['sites'].values(): c[s['status']] = c.get(s['status'], 0) + 1
        print(n, len(st['sites']), c, 'inflight', list(st['inflight']))

if __name__ == '__main__':
    a = sys.argv[1:]
    if a[0] == 'init':
        for n in NICHES: save(n, load2(n))
        write2(); stats()
    elif a[0] == 'next':
        for q in a[1:]: nxt(q.split(':')[0], int(q.split(':')[1]))
    elif a[0] == 'auto': auto(a[1:])
    elif a[0] == 'stats': stats()
    elif a[0] == 'out': write2()
    elif a[0] == 'out3': write3()
    elif a[0] == 'requeue':
        n = re.sub(r'B\d+$', '', a[1]); st = load2(n); print(st['inflight'].pop(a[1], None)); save(n, st)
