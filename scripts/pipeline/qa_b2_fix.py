import json
P='day5/'
L=json.load(open(P+'b2_leads.json'))
drop={'sharkeynailsit72@gmail.com','valleyofwisconsin@yahoo.com','shawnh@creeksidecoverings.com','tmandujanolara@yahoo.com','info@capitaldevelopmenthomes.com',
 'info@marshcreekcontracting.com','ormenogc@gmail.com','cuzzinllc@gmail.com','andrewsconstructioncotn@gmail.com','david@mnbr.homes','waypointhic@gmail.com',
 'hkcsny@gmail.com','greghomeimprovement@hotmail.com','ngcbuilders13@gmail.com','newlineremodeling1@gmail.com','kingofhardwood@yahoo.com','general@allprogcusa.com',
 'tom@simplexrepairs-remodeling.com','info@sealcoatingfairfieldct.com','fsandpavers@gmail.com','plm@plmscape.com','greenbaybyhernandez@gmail.com','zac@semperscapes.com',
 'andrew@bluestreamlandscapes.com','southernstreamofpc@gmail.com','info@southernbrushga.com','thegreenmanlandscaping@yahoo.com','hello@defymortgage.com','sharon@horizonlendingservices.com'}
to_h={'office@goliathconstructionmd.com','juan@outertainment.com'}
co={'megan@omegalc.com':'Omega Landscape Construction','castlerockdeckandfence@yahoo.com':'Castle Rock Deck & Fence','monteiroandsons@gmail.com':'Monteiro & Sons Landscaping',
 'franciscozarcogardens@gmail.com':'Francisco Zarco Gardens & Landscape','jsenterprise1@msn.com':'JS Enterprises','alexander@newparadigmloans.com':'New Paradigm Lending',
 'guarda27@gmail.com':'Guarda Landscaping','carlos@stglandscape.com':'STG Landscaping','info@the1mortgagespecialist.com':'The #1 Mortgage Specialist',
 'info@kenneylandscape.com':'Kenney Landscape','management@hmmtg.com':'H&M Mortgage Group'}
fn={'teampeyton@mortgage-project.com':'Peyton','nicog@firstteamlending.com':'Nico','chase@capratefunding.net':'Chase','billjrappjr@gmail.com':'Bill',
 'jimb@ascendlending.net':'Jim','mortgagemeccajoe@gmail.com':'Joe','todolistron@gmail.com':'Ron','rickkfriend@yahoo.com':'Rick','cobbtyler2@gmail.com':'Tyler','aimeeschu@yahoo.com':'Aimee'}
import re
def slugify(s):
  s=s.lower().replace('&',' and ').replace("'",'').replace('#','')
  return re.sub(r'[^a-z0-9]+','-',s).strip('-')[:48].strip('-')
out=[]
for r in L:
  e=r['email']
  if e in drop: continue
  if e in to_h: r['niche']='hardscape'
  if e in co: r['co']=co[e]; r['slug']=slugify(co[e])
  if e in fn: r['fn']=fn[e]
  out.append(r)
assert len({r['slug'] for r in out})==len(out)
json.dump(out,open(P+'b2_leads.json','w'),indent=0)
# signal overrides
S=json.load(open(P+'sig_b2_dh.json'))
for e in ['contact@gcsfpavers.com','contact@artistsmasonry.com','brian@fsland.com','exoticlandscapeservice@gmail.com','info@austinreno.com','info@saltydogremodeling.com']: S.pop(e,None)
S['monteiroandsons@gmail.com']=[S['monteiroandsons@gmail.com'][0].replace('gas ',''),S['monteiroandsons@gmail.com'][1].replace('gas ','')]
json.dump(S,open(P+'sig_b2_dh.json','w'),indent=0)
M1=json.load(open(P+'sig_b2_m1.json'))
M1['info@everestequity.com'][0]='those Inc. 5000 wins'
M1['teampeyton@mortgage-project.com'][1]="saw you've been producing in the top 1% of lenders nationwide."
for k,v in M1.items(): M1[k]=[x.replace('Best Of','Best of').replace('’',"'") for x in v]
json.dump(M1,open(P+'sig_b2_m1.json','w'),indent=0)
R=json.load(open(P+'review_b2_m2.json')); R.pop('info@smoothmortgageloans.com',None)
for v in R.values(): v['quote']=v['quote'].replace('’',"'")
json.dump(R,open(P+'review_b2_m2.json','w'),indent=0)
print(len(out))
