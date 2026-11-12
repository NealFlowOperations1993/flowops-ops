import json,sys,re,collections
from datetime import datetime as D, timezone, timedelta
p=lambda s:D.fromisoformat(s.replace('Z','+00:00'))
CT=timezone(timedelta(hours=-6))
NAMES={4315253:'W1 Deck B',4315254:'W1 Deck A',4315255:'W1 Hardscape A',4315256:'W1 Hardscape B',4327390:'W2 Mortgage',4327600:'W2 Wealth',4336994:'W3 Deck',4336993:'W3 Hardscape',4452197:'W4 Mortgage'}
GROUP={4315253:'W1 Deck/Hardscape',4315254:'W1 Deck/Hardscape',4315255:'W1 Deck/Hardscape',4315256:'W1 Deck/Hardscape',4327390:'W2 Mortgage',4327600:'W2 Wealth',4336994:'W3 Deck',4336993:'W3 Hardscape',4452197:'W4 Mortgage'}
TRACKED={4327390,4327600,4336994,4336993,4452197}
def load(path):
  d=json.load(open(path))
  res=d['data']['resultData']['runData']['Wrap'][0]['data']['main'][0][0]['json']['results']
  rows=collections.defaultdict(list); accts=None
  for x in res:
    if x['tag']=='accts': accts=x['body']; continue
    rows[int(x['tag'].split('_')[0])].extend(x['body']['data'])
  return rows,accts
def tmpl(s):
  if re.match(r'^(that|those|this) ',s): return '[signal] that/those …'
  if 'borrowers are being auctioned' in s: return '{City} borrowers are being auctioned off…'
  if s.startswith('Stop chasing'): return 'Stop chasing borrowers/clients like {name}…'
  if s.startswith('more serious buyers for'): return 'more serious buyers for {company}'
  return s
def compute(rows,today):
  out={}; subj=collections.defaultdict(lambda:[0,0,0])
  for c,R in rows.items():
    leads={r['lead_email'] for r in R}
    op=[r for r in R if r['open_time']]
    hum=set(); maybe=set()
    for r in op:
      g=(p(r['open_time'])-p(r['sent_time'])).total_seconds()
      if g>=120: hum.add(r['lead_email'])
      elif r['open_count']>=2: maybe.add(r['lead_email'])
    e1=[r for r in R if r['sequence_number']==1]
    td=[r for r in R if r['sent_time'] and p(r['sent_time']).astimezone(CT).date()==today]
    for r in e1:
      if c not in TRACKED: continue
      k=(GROUP[c],tmpl(r['email_subject'] or '')); subj[k][0]+=1
      if r['open_time'] and (p(r['open_time'])-p(r['sent_time'])).total_seconds()>=120: subj[k][1]+=1
      if r['reply_time']: subj[k][2]+=1
    out[c]=dict(name=NAMES[c],group=GROUP[c],emails=len(R),leads=len(leads),e1=len(e1),today=len(td),today_e1=sum(1 for r in td if r['sequence_number']==1),
      human=len(hum) if c in TRACKED else None,maybe=len(maybe-hum) if c in TRACKED else None,
      replies=len({r['lead_email'] for r in R if r['reply_time']}),bounced=sum(1 for r in R if r['is_bounced']),unsub=len({r['lead_email'] for r in R if r['is_unsubscribed']}))
  return out,subj
if __name__=='__main__':
  rows,accts=load(sys.argv[1]); today=D.fromisoformat(sys.argv[2]).date()
  out,subj=compute(rows,today)
  json.dump({'campaigns':{str(k):v for k,v in out.items()},'subjects':[[a,b,*v] for (a,b),v in subj.items()],'accounts':accts},open(sys.argv[3],'w'),indent=1)
  for c,v in out.items(): print(v)
