import json,random,sys,collections
sys.path.insert(0,'day4')
import build_day4 as B
random.seed(1112)
L=json.load(open('day5/b2_leads.json'))
BASE='https://brandable-toolbox-studio.lovable.app/t/'
# deck + hardscape: approved W3 copy, no signals this round
import os
SDH=json.load(open('day5/sig_b2_dh.json'))
dh=[dict(r,sig=SDH.get(r['email'])) for r in L if r['niche']!='mortgage']
SM1=json.load(open('day5/sig_b2_m1.json'))
pass
RM2=json.load(open('day5/review_b2_m2.json'))
slugmap={r['email']:r['slug'] for r in L}
out=B.build(dh,slugmap)
for o in out: o['segment']='b2_'+o['niche']+'_'+o['reoon']
# mortgage
M=[r for r in L if r['niche']=='mortgage']; random.shuffle(M)
n=len(M); q=n//3
c1=[r for r in M if r['email'] in SM1]; c2=[r for r in M if r['email'] in RM2 and r['email'] not in SM1]
rest=[r for r in M if r['email'] not in SM1 and r['email'] not in RM2]
nocity=[r for r in rest if not r['city']]; withcity=[r for r in rest if r['city']]
c3=withcity[:q]; rest2=withcity[q:]+nocity
for r in rest2:
  (c1 if len(c1)<=len(c2) else c2).append(r)
Q='“';QE='”'
for v,grp in (('M1',c1),('M2',c2),('M3',c3)):
  for r in grp:
    fn=r['fn']; co=r['co']; city=r['city']; url=BASE+'mortgage-true-monthly/'+r['slug']
    sg=SM1.get(r['email']) if v=='M1' else None
    rv=RM2.get(r['email']) if v=='M2' else None
    if v=='M1' and sg:
      subj=sg[0]
      parts=[f"{fn or 'Hi there'} - {sg[1]}",f"Is it frustrating when rate shoppers reduce that kind of service to {Q}what's your best rate?{QE}",
        f"We built a payment calculator for {co}. Borrowers enter their home price and down payment, see their full monthly payment on a page with your name on it, and send the request straight to you.",
        f"Something specific to discuss, not just {Q}what's your rate?{QE}","Could I show you how it works?"]
      e2=(f"{fn}, bumping this up." if fn else "Bumping this up.")+" Want me to send the payment calculator over? It takes about a minute to try."
    elif v=='M1':
      subj='rate shoppers'
      parts=[f"{fn or 'Hi there'} - is it frustrating when rate shoppers reduce your work to {Q}what's your best rate?{QE}",
        f"We built a payment calculator for {co}. Borrowers enter their home price and down payment, see their full monthly payment on a page with your name on it, and send the request straight to you.",
        f"Something specific to discuss, not just {Q}what's your rate?{QE}","Could I show you how it works?"]
      e2=(f"{fn}, bumping this up." if fn else "Bumping this up.")+" Want me to send the payment calculator over? It takes about a minute to try."
    elif v=='M2':
      subj='tired of unqualified borrowers?'
      parts=[f"Hey {fn}," if fn else "Hi there,"]+([f"Saw this in one of your {'Google ' if rv['google_labeled'] else ''}reviews: {Q}{rv['quote']}{QE}",
        "Work like that should have you booked with borrowers who are ready to move. Instead, how often do you spend an hour on a pre-approval call and find out their numbers aren't even close?"] if rv else [
        "Good loan officers should be booked with borrowers who are ready to move. Instead, how often do you spend an hour on a pre-approval call and find out their numbers aren't even close?"])+[
        "We built a calculator that lets borrowers enter their home price and down payment and see their full monthly payment before they ever request a call.","Want to see it?"]
      e2=(f"{fn}, one more thought." if fn else "One more thought.")+"<br><br>Borrowers decide on the monthly payment, not the rate. Showing them that number, with your name next to it, is a different conversation.<br><br>Want me to send the calculator over?"
    else:
      subj=f"{city} borrowers are being auctioned off..."
      parts=[f"{fn}," if fn else "Hi there,",
        f"Right now, someone in {city} is getting pre-approved somewhere else.",
        f"They ran their numbers on a lead site, got a flood of calls by morning, and picked whoever called first. Not the best lender in {city}, just the fastest dialer.",
        "That's infuriating when you know you'd have done it better.",
        f"We built a payment calculator branded for {co}. {city} borrowers see their full monthly payment on a page with your name on it, and the request goes straight to you.","Want to see it?"]
      e2=(f"{fn}, one more thought." if fn else "One more thought.")+"<br><br>Half the first call is just collecting numbers: home price, down payment, what they can afford each month. The calculator collects them before the borrower ever reaches out, so your first call starts with real numbers.<br><br>Want me to send it over?"
    e3=f"Last one from me.<br><br>If new borrower inquiries aren't your department, should I be sending this to someone else? If it's you and the timing's off, no problem.<br><br>Here's the calculator we built for {co}: {url}"
    out.append(dict(r,variant=v,subject=subj,body_html='<br><br>'.join(parts),body_text='\n\n'.join(parts),e2_body=e2,e3_body=e3,tool_url=url,tool_name='payment calculator',sig=(sg or (['review',rv['quote']] if rv else None)),segment='b2_mortgage_'+r['reoon']))
json.dump(out,open('day5/b2_final.json','w'),indent=0)
print(len(out),collections.Counter((o['niche'],o['variant']) for o in out))
