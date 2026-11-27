import json,re,sys,random,string,collections
sys.path.insert(0,'day4')
from build_day4 import clean_co
random.seed(1111)
D5='day5/'
M=json.load(open(D5+'fit_b2_mortgage.json'));D=json.load(open(D5+'clean_b2_deck.json'));H=json.load(open(D5+'clean_b2_hardscape.json'))
name_fix={('m',1):'McCue Mortgage',('m',12):'Town & Country Mortgage',('m',29):'MortgageMecca',('m',33):'Ascend Lending',('m',34):'Everest Equity',
 ('m',39):'Richard Bolt Mortgage',('m',45):'Bill Rapp Mortgage',('m',49):'The Mortgage Project',('m',59):'The Beatty Team',('m',64):'Sky Mortgage',
 ('m',68):'New Paradigm Loans',('m',43):'MortgageXpress',
 ('d',2):'Artisan Decks & Remodeling',('d',8):'Sky Decks N Things',('d',25):'Sharkey Nails It',('d',28):'Kingsway Builder',('d',47):'Medeiros Home Construction',
 ('d',48):'G&D Pavers Solutions',('d',55):'Osnova Construction',('d',66):'Agave Green Landscapes',('d',76):'GN Construction',('d',110):'Idaho Installs Co.',
 ('d',115):'Master Tool Home Improvement',('d',33):"B&J's Exterior Services",
 ('h',0):"Mario's Landscaping",('h',14):'Merino Landscape',('h',52):'Arcadia Landscaping & Design',('h',65):"Hunter's Lawn & Landscaping",('h',76):'Omega',
 ('h',77):'A-Z Landscaping',('h',80):'De Luna Site & Landscape',('h',83):'Goodman Landscape',('h',99):'Guarda Sealcoating and Outdoor Living',
 ('h',100):'SoCal Epic Builds',('h',115):'Saucedo Landscaping Services',('h',123):'Blue Stream Irrigation & Landscape'}
fn_fix={('h',99):''}
# first names only where the inbox is exactly name@domain
EMAIL_FN={'ken','paul','tim','rick','jerry','josh','olga','sean','chad','mark','sal','alejandro','ryan','sharon','denise','todd','bryan','erick','tom',
 'brian','david','greg','kacy','ericka','juan','guy','john','kevin','carlos','mike','anthony','zac','tyler','rafael','jay','megan','irvin','ricky','kathryn','pablo','andrew','connor','dawn','steven','igor','jim','nan','brent','emily','ben'}
drop={'m':{71},
 'd':{11,14,27,36,37,38,42,50,67,69,80,86,91,96,104,106},
 'h':{19,22,33,40,47,57,67,68,71,75,86,87,103,105,112,113,118}}
to_h={7,13,18,19,33,34,48,63,66,97,100,107,112}
L=json.load(open(D5+'lovable_index.json')); taken_s=set()
import subprocess
out=[];dropped=[]
def slugify(s):
  s=s.lower().replace('&',' and ').replace("'",'')
  return re.sub(r'[^a-z0-9]+','-',s).strip('-')[:48].strip('-')
for k,Lst,niche in (('m',M,'mortgage'),('d',D,'deck'),('h',H,'hardscape')):
  for i,x in enumerate(Lst):
    if i in drop.get(k,()): dropped.append((k+str(i),x['email'],clean_co(x['title']))); continue
    co=name_fix.get((k,i)) or clean_co(x['title'])
    co=co.replace('™','').replace('®','').replace('‑','-').replace('’',"'").strip().rstrip('.').rstrip(',')
    fn=fn_fix.get((k,i), x.get('first_name') or '')
    lp=x['email'].split('@')[0].lower()
    if not fn and lp in EMAIL_FN: fn=lp.capitalize()
    n='hardscape' if (k=='d' and i in to_h) else niche
    city=x.get('city'); city=None if city in (None,'None','') else city
    out.append(dict(email=x['email'].lower(),co=co,fn=fn,niche=n,city=city,state=x.get('state'),website=x['website'],reoon=x['reoon'],placeId=x.get('placeId'),rating=x.get('rating'),reviews=x.get('reviews'),key='b2'+k+str(i)))
seen=set()
for r in out:
  base=slugify(r['co']) or 'business'; s=base; j=2
  while s in seen: s=f"{base}-{j}"; j+=1
  seen.add(s); r['slug']=s
  r['short']=''.join(random.choice(string.ascii_lowercase) for _ in range(6))
assert len({r['email'] for r in out})==len(out)
assert not ({r['email'] for r in out} & set(L['E']))
print(len(out),collections.Counter(r['niche'] for r in out),'dropped',len(dropped))
json.dump(out,open(D5+'b2_leads.json','w'),indent=0)
json.dump(dropped,open(D5+'b2_dropped.json','w'),indent=0)
