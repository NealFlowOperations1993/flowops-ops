import json
M=json.load(open('m_2026-11-12.json')); C={int(k):v for k,v in M['campaigns'].items()}
AS='2026-11-12'
NS={4336994:60,4336993:175,4452197:67}
tracked=[4327390,4327600,4336994,4336993,4452197]
leads=sum(v['leads'] for v in C.values()); emails=sum(v['emails'] for v in C.values())
tl=sum(C[c]['leads'] for c in tracked); hum=sum(C[c]['human'] for c in tracked); maybe=sum(C[c]['maybe'] for c in tracked)
bounced=sum(v['bounced'] for v in C.values())
HR,POS,BOOK=8,5,1
pct=lambda a,b:f"{100*a/b:.2f}%" if b else '—'
pct1=lambda a,b:f"{100*a/b:.1f}%" if b else '—'
grp={}
for c,v in C.items():
  g=v['group']; d=grp.setdefault(g,dict(leads=0,emails=0,human=0,tl=0,maybe=0,bounced=0))
  d['leads']+=v['leads']; d['emails']+=v['emails']; d['bounced']+=v['bounced']
  if v['human'] is not None: d['human']+=v['human']; d['tl']+=v['leads']; d['maybe']+=v['maybe']
POSG={'W1 Deck/Hardscape':(1,1,'Bill — CM Hardscapes'),'W2 Mortgage':(1,1,'David De La Torre (BOOKED)'),'W2 Wealth':(1,0,'—'),'W3 Deck':(3,3,'Josh, Geo, Jordan'),'W3 Hardscape':(2,0,'—'),'W4 Mortgage':(0,0,'—')}
rows=[]
for g in ['W1 Deck/Hardscape','W2 Mortgage','W2 Wealth','W3 Deck','W3 Hardscape','W4 Mortgage']:
  d=grp[g]; hr,ps,who=POSG[g]
  rows.append([g,d['leads'],d['emails'],pct1(d['human'],d['tl']) if d['tl'] else 'not tracked',hr,ps,who,d['bounced']])
T=[]
def tab(tab,headline,kpis,body,tables): T.append(dict(tab=tab,as_of=AS,headline=headline,kpis=kpis,body_md=body,tables=tables))
K=lambda l,v,s=None,t=None:{k:x for k,x in dict(label=l,value=v,sub=s,tone=t).items() if x is not None}

# ---------- METRICS
tab('metrics',"Nov 4–12: 1,220 leads contacted, 5 positive replies, 1 call booked",
[K('Leads contacted',f'{leads:,}','since Nov 4, 9 campaigns'),K('Emails sent',f'{emails:,}','incl. follow-ups'),
 K('Human opens',f'≥{pct1(hum,tl)}',f'{hum} of {tl} tracked leads; likely 9–15%','warn'),
 K('Human replies',f'{HR}',pct(HR,leads)+' of leads','warn'),K('Positive replies',f'{POS}',pct(POS,leads)+' of leads','warn'),
 K('Calls booked',f'{BOOK}','David De La Torre, Fri Nov 13','warn'),K('Bounce rate',pct(bounced,emails),f'{bounced} bounces','good'),
 K('Target','2.0%','human reply rate before scaling','bad')],
"""**How these numbers are counted**
- **Human open** = first open 2+ minutes after send. 88% of all opens happen within 2 minutes (median 10 s) — those are security scanners, not people. W1 is plain text with tracking off, so it has no open data.
- **Human reply** = a real person wrote back. Auto-replies, out-of-office notes, support tickets and bounce notices are excluded (Smartlead's own reply counter includes them).
- Positive = wants to see it / talk. Opt-out = "stop" or "not interested" (auto-added to the global block list).

**Projection at today's rates** (honest): ~200 new leads/day × 0.41% positive ≈ **0.8 positives/day**, ≈ **0.2 booked calls/day**. The 3–5 calls/day goal needs ~1–1.5% booked — roughly **10× better conversion**, not more volume. Volume stays at 315/day until human replies clear 2%.""",
[dict(title='Results by campaign (Nov 4–12)',columns=['Campaign','Leads','Emails','Human opens','Human replies','Positive','Who','Bounces'],rows=rows,
      note='W3 Hardscape: 307 leads, 2 replies — both "stop". Deck and mortgage produced 4 of 5 positives.'),
 dict(title='Funnel',columns=['Stage','Count','Rate'],rows=[['Leads contacted',leads,'100%'],['Human opens (tracked campaigns)',hum,pct1(hum,tl)+' of tracked'],['Human replies',HR,pct(HR,leads)],['Positive',POS,pct(POS,leads)],['Booked',BOOK,pct(BOOK,leads)]])])

# ---------- LEADS
tab('leads',"302 new leads queued; ~600 more hardscape/deck sites being searched for emails",
[K('Queued (not started)','302','W3 Deck 60 · W3 Hardscape 175 · W4 67'),K('Daily new-lead cap','225','75 deck · 100 hardscape · 50 mortgage'),
 K('Runs low','Fri Nov 13','~90 new left for Friday','warn'),K('Email search','~600 sites','hardscape first, running now'),K('Unsearched pool','~1,600','hardscape + deck from Google Maps')],
"""**Pipeline (every batch):** Google Maps scrape → find email on website (homepage + contact pages) → **Neal runs Reoon** (keep safe, catch-all, role) → dedupe vs. every past lead + Smartlead → fit check → signals from the website (checked twice) → phone + brand colours → tool page → approved copy → independent proofread of every lead → load → per-lead field check → test emails to raine@.

**Batch 2 (loaded Nov 11):** 258 built → 223 added (W3 Deck 53, W3 Hardscape 102, W4 68); 35 skipped by Smartlead as already in older campaigns. 137 of 258 personalized with a verified signal.

**Niche priority from Nov 13** (Neal, Nov 12): Home services 70% — 1 Hardscaping, 2 Deck building, 3 HVAC, 4 Pool builders, 5 Roofing. Loan brokers 30% — Hard money / fix-and-flip, SBA brokers, Business & commercial loan brokers, Credit stacking. Mortgage & wealth: finish loaded leads, no new leads.""",
[dict(title='Niche readiness',columns=['Priority','Niche','Tool page','Copy','Leads','Status'],rows=[
 ['1','Hardscaping','Patio designer + planner','Approved (+Endurance PS)','175 queued + search running','Sending'],
 ['2','Deck building','Deck designer + planner','Approved','60 queued + search running','Sending'],
 ['3','HVAC','—','—','—','Tool + copy to build'],['4','Pool builders','—','—','—','Tool + copy to build'],['5','Roofing','—','—','—','Tool + copy to build'],
 ['6','Hard money / fix-and-flip','—','—','5 verified (from batch 2)','Tool + copy to build'],['7','SBA loan brokers','—','—','—','Tool + copy to build'],
 ['8','Business / commercial loan brokers','—','—','—','Tool + copy to build'],['9','Credit stacking','—','—','—','Tool + copy to build'],
 ['—','Mortgage (W2/W4)','Payment calculator','Approved','67 queued','Finish loaded, no new'],['—','Wealth (W2)','Retirement checkup','Approved','0 queued','Finishing follow-ups']])])

# ---------- VOC
tab('voc',"What prospects said: 5 yes, 3 no — short, low-commitment replies",
[K('Positive','5','"Let\'s talk", "sure", "Please do", "Sure", "I\'m open to hearing more"','good'),K('Negative','3','2 "stop", 1 "not interested"','bad'),K('Auto-replies','11','excluded from rates')],
"""**Patterns in the replies**
- Every positive reply is **1–5 words**. They are answering a small ask ("Could I show you how it works?" / "Want me to send it over?"), not agreeing to a meeting.
- All 5 positives are **owner-operators** reading their own inbox (owner/founder titles, gmail or personal domain).
- **3 of 5 came on Email 2**, the one-line bump. Follow-ups matter.
- Objection heard on the booked call: David asked up front that it be **"no pay to play"** — expect skepticism about paid lead schemes; lead with "built free, yours to use".
- The two hardscape "STOP"s came from a signal opener ("those stone steps") and a curiosity opener ("before the price becomes a headache") — no pattern yet, small sample.""",
[dict(title='Every human reply (Nov 4–12)',columns=['Date','Person','Company','Niche','Campaign / email','Subject','Reply','Outcome'],rows=[
 ['Nov 6','Josh Iddins','Tennessee Deckworks','Deck','W3 Deck · E1','price shoppers','"Let\'s talk"','Booking link sent; not booked'],
 ['Nov 9','David De La Torre','Mortgages by David (dloans.com)','Mortgage','W2 Mortgage · E2','Irvine borrowers are being auctioned off…','"sure"','BOOKED Fri Nov 13 2:30 PM ET'],
 ['Nov 9','Bill','CM Hardscapes','Hardscape','W1 Hardscape B · E2','tired of broke homeowners?','"Please do"','Call to walk through'],
 ['Nov 10','Geo Alejo','G&J General Contractors','Deck / GC','W3 Deck · E2','new clients for G&J General Contractors','"Sure"','Tool + booking link sent Nov 11'],
 ['Nov 11','Jordan','Atwood Construction','Deck','W3 Deck · E1','price shoppers','"I\'m open to hearing more"','Offered Wed Nov 18, 1 or 3 PM MT'],
 ['Nov 9','Kevin Lewis','Lewis Wealth Management','Wealth','W2 Wealth · E2','Prospects are selfish…','"I am not interested"','Blocked'],
 ['Nov 10','Jessica Dickens','Comeyer CC','Hardscape','W3 Hardscape · E1','those stone steps','"Stop"','Blocked'],
 ['Nov 10','Stones Landscaping','Stones Landscaping','Hardscape','W3 Hardscape · E2','before the price becomes a headache','"STOP"','Blocked']])])

# ---------- SPLIT
S=[s for s in M['subjects'] if s[2]>=5]
S.sort(key=lambda s:-(s[3]/s[2]))
tab('split',"Subject lines ranked by human opens — no proven winner yet (5–66 sends each)",
[K('Best (≥10 sends)','25%','"Pre-approval is a free sample…" 3/12'),K('Signal subjects','~8%','177 sends; most hidden reopens'),K('Worst','0%','"price shoppers"-style labels, city "auctioned off" in W4','bad')],
"""**Read this carefully:** most subjects went to 5–15 leads, so one opener moves the rate 7–20 points. Treat this as direction, not proof.

**Pattern so far:** subjects that hint at a **cost or a twist** get opened ("free sample", "dead-end estimate", "selfish", "used against you"). Subjects that **name the problem plainly** mostly don't ("price shoppers", "rate shoppers", "tired of unqualified borrowers?").

**But opens ≠ positives:** 2 of 5 positives came from "price shoppers" — one of the *lowest*-opened subjects. Plain, specific subject + plain ask may filter for real buyers.

**Next test (batch 3):** top 3 curiosity subjects adapted per niche vs. the signal subject as control, ~100 leads each, judged on positives not opens.""",
[dict(title='E1 subject leaderboard (tracked campaigns, ≥5 sends)',columns=['Campaign','Subject','Sent','Human opens','Human open %','Replies (incl. auto)'],
      rows=[[s[0],s[1],s[2],s[3],pct1(s[3],s[2]),s[4]] for s in S])])

# ---------- TEMPLATES
tab('templates',"Copy in market — and what is working by niche",
[K('Deck','3 positives','plain pain + tool + small ask','good'),K('Mortgage','1 booked','city "auctioned off" (W2)','good'),K('Hardscape','0 in W3','307 leads; rethink body','bad'),K('Wealth','0','1 "not interested"','bad')],
"""**What the winning emails share (5 of 5 positives)**
1. One plain problem the owner feels (price shoppers / wasted estimates / rate shoppers).
2. A **free tool already built with their company name on it** — the offer is concrete, not a meeting.
3. A tiny ask: *"Could I show you how it works?"* / E2: *"Want me to send it over? It takes about a minute to try."*
4. Short. No pricing. No criticism of their business.

**Deck — working (Josh, Jordan):**
> Hi there - is it frustrating when price shoppers reduce your craftsmanship to "what's your cheapest price?"
> We built a deck designer for {Company}. Homeowners explore boards, colors and railings, see a price range, and send you their choices with the request.
> Something specific to discuss, not just "I want a deck."
> Could I show you how it works?

**Mortgage — booked (David, W2 E2 bump of):** "{City} borrowers are being auctioned off…" — lead-site borrowers pick the fastest dialer, not the best lender; calculator branded for you.

**Hardscape — not working yet in W3:** same structure + Endurance PS, 0 positives / 307. Candidates to test as a **new campaign**: shorter body, lead with the Endurance result as the opener (variant F), visualizer-style offer (W1 Visualizer produced Bill).

**E2 (all niches):** "Bumping this up. Want me to send the {tool} over? It takes about a minute to try." — produced 3 of 5 positives.
**E3:** "Last one from me… should I be sending this to someone else?… Here's the {tool} we built for {Company}: {link}".""",
[dict(title='Live variants (W3/W4)',columns=['Niche','Variant','Subject','Opener'],rows=[
 ['Deck/Hardscape','J + signal','that {thing}','saw the {specific project} on your website.'],['Deck/Hardscape','J','price shoppers','is it frustrating when price shoppers reduce your craftsmanship…'],
 ['Deck/Hardscape','A','more serious buyers for {Company}','3 ideas list; first one built free'],['Deck/Hardscape','B','what a dead-end estimate costs you','hours per estimate math'],
 ['Deck/Hardscape','C','the price shopper vs. the $25k buyer','two homeowners call you today…'],['Deck/Hardscape','D','stood up on a Saturday?','blocked a Saturday, got stood up'],
 ['Deck/Hardscape','G','ghosted after the estimate?','signal + ghosted after estimate'],['Hardscape','F','68 estimates in November','Endurance result first'],
 ['Mortgage','M1','that {fact} / rate shoppers','verified site fact + rate shoppers'],['Mortgage','M2','tired of unqualified borrowers?','real review quote + hour-long pre-approval calls'],
 ['Mortgage','M3','{City} borrowers are being auctioned off…','lead-site borrowers pick the fastest dialer']],note='Rule: never edit a live sequence — copy changes ship as a new campaign; per-lead custom fields only.')])

# ---------- PLAYBOOK
tab('playbook',"Operating protocol (current)",[K('Sending window','Mon–Fri 8:00–4:30 CT'),K('Capacity','315/day','9 inboxes × 35'),K('Reply SLA','< 1 hour','owner-operators go cold fast')],
"""**Daily**
1. 7:30 CT — this dashboard refreshes: metrics, replies, inbox limits/health, lead runway, workflow errors.
2. Check inbox limits = 35 and warmup ≥ 98%; alert immediately if not.
3. Positive reply → draft response shown to Neal → send only on "send". Booking link: 10 minutes with our founder Neal. No pricing in replies.
4. "Stop"/"not interested" → global block list automatically (B30 pipeline).

**Every new batch** — see Leads tab pipeline. Proofread **every** lead, never a sample. Load only after per-lead QA; verify every custom field after upload; send test emails to raine@.

**Hard rules**
- Never write to a live sequence; new copy = new campaign.
- Never assert an absence; a signal that becomes a claim needs real evidence (photo/text checked twice).
- Opens are mostly scanners — judge on human replies and positives.
- A reply in under 6 minutes is usually a machine.
- Don't scale volume before human reply rate clears 2%.
- Never pause warmup. Never hardcode keys.
- Deletion filters must be allow-list narrow; check `notStarted` before judging a campaign.""",[])

# ---------- STUDY
tab('study',"Daily study — Nov 12: positives come from plain asks, not high-open subjects",[],
"""**Observation:** The two highest-open subject families ("…is a free sample", "…are selfish") produced **0 positives**. "price shoppers" had one of the lowest human-open rates (~2% on deck) yet produced **2 of 5 positives**.

**Hypothesis:** Curiosity subjects attract readers; plain, specific subjects attract *buyers*. Owner-operators who open a plain "price shoppers" email already have that pain.

**Evidence strength:** weak — 5 positives total. Needs ~100 leads per arm.

**Action:** batch-3 test = curiosity subject vs. plain-pain subject with the **same body**, judged on positive replies per 100 leads.

**Also learned today:** inbox limits were silently dropped to 5/day; capacity can disappear without any error. Daily limit check added to this refresh.""",[])

# ---------- INBOXES
A=M['accounts']; send_ids={18159333,18159328,18159266,18159244,18018031,18018022,18017543,18017145,18016412}
irows=[]
for a in A:
  w=a.get('warmup_details') or {}
  role='Sending' if a['id'] in send_ids else ('Warming (new Nov 11)' if a['id']>=26000000 else 'Not used (warmup blocked since Aug 29)')
  lim=35 if a['id'] in send_ids else a['message_per_day']
  irows.append([a['from_email'],role,lim,w.get('warmup_reputation'),'✓ SPF ✓ DKIM ✓ DMARC'])
tab('inboxes',"9 sending inboxes restored to 35/day; all domains healthy",
[K('Sending capacity','315/day','restored Nov 12, 9:15 AM CT','good'),K('Warmup reputation','99–100%','all inboxes','good'),K('Blacklists','Clean','Spamhaus DBL, SURBL','good'),K('New inboxes warming','10','4 domains; join campaigns in 2–3 weeks')],
"""**Incident Nov 12:** all 19 inboxes had their daily limit set to 5 between 6:09–7:06 AM CT (new inboxes first, then the 9 sending ones). Sending capacity fell from 315 to 45. Restored all 9 sending inboxes to 35 at 9:15 AM CT, verified one by one (signatures untouched). Likely a manual Smartlead edit during new-inbox setup — not an n8n workflow. **The daily refresh now checks limits every morning.**

**Domain health (Nov 12):** flowoperations.org and flowopsleadgen.com — SPF `include:_spf.google.com ~all`, Google DKIM present, DMARC `p=none` (monitoring), Google MX. Not listed on Spamhaus DBL or SURBL. Smartlead shows SPF/DKIM/DMARC verified for all 4 new domains.

**To fix:** DMARC reports for flowoperations.org go to a personal address (neal@evolvere.co) — move to a team inbox. ryan@flowoperations.org has warmup blocked since Aug 29 (not in campaigns).""",
[dict(title='All inboxes',columns=['Inbox','Role','Daily limit','Warmup rep %','DNS'],rows=irows)])

# ---------- WORKFLOWS
tab('workflows',"Diagnostics — 2 issues open: Apify token rejected, booking calendar changed",
[K('Apify','401','token rejected since Nov 12 AM','bad'),K('Smartlead gateway','OK','reads + guarded writes'),K('Reply pipeline (B30)','OK','last reply Nov 11 10:24 CT','good'),K('Contractor notification','Wired','Tool Studio lead → contractor email','good')],
"""**Open issues**
1. **Apify token rejected (401) since Nov 12 morning.** Blocks: reading the reply log dataset, new Google Maps scrapes. Fix: new API token from Apify Console → Settings → API & Integrations, pasted into the n8n credential **"Apify API Token"** (used by "FO — Apify Gateway").
2. **Booking calendar (FlowOperations Qualification Call)** was changed on Nov 11: 30-min slots, Mon–Fri, 3-day booking window, phone location. Intended: 20 min, Mon/Wed/Fri/Sat. On hold per Neal.
3. **Inbox limits dropped to 5** on Nov 12 — fixed (see Inboxes).

**Resolved since last review:** contractor notification for tool submissions is wired ("FO — Tool Studio Lead → Contractor Email", active).""",
[dict(title='Cold email workflows',columns=['Workflow','Role','State'],rows=[
 ['B30 Reply Pipeline (brutus-reply)','Classify replies; auto-block stop/not interested','Active'],
 ['FO — Tool Studio Lead → Contractor Email','Emails contractor when a homeowner submits a tool','Active'],
 ['FO — Smartlead Gateway','Guarded reads/writes for campaigns W1–W4','Manual, OK'],
 ['FO — Web Page + Vision Gateway','Website reads + photo signals','Manual, OK'],
 ['FO — Apify Gateway','Google Maps scrapes, datasets','BROKEN — token 401'],
 ['FO — Daily Digest (6pm ET)','Daily digest','Active'],['FO — Cold Email Reports (4x daily)','Slack reports','Active'],
 ['FO — Budget Guard ($20/day)','Spend cap','Active'],['FO — Split-Test Referee','Legacy (Aug)','Active — legacy'],
 ['FO — Inbox Onboarding & Ramp','Inbox ramp (not visible to Claude)','Active — review']])])

# ---------- WHY
tab('why',"Why results are where they are (Nov 12)",[],
"""**1. Delivery is not the problem.** Bounces 0.6%, warmup 99–100%, domains clean, ~9–15% of leads open as humans.

**2. Conversion is the problem.** 0.41% positive / 0.08% booked vs. a goal needing ~1–1.5% booked. Readers who open reply at roughly 1 in 13, so the leak is mostly **who opens** (subject + targeting) and **what the offer asks for**.

**3. Hardscape copy underperforms.** W3 Hardscape: 307 leads, 0 positives, 2 stops — while W3 Deck with near-identical structure got 3 positives. Differences: patio designer vs. deck designer, Endurance PS on every email. Next: test a hardscape-specific rewrite as a new campaign.

**4. Lead supply and capacity are fragile.** Each batch lasts ~1½ days; Reoon credits and email search gate it. On Nov 12 capacity silently dropped to 45/day (inbox limits) and Apify auth failed — both caught by today's audit.

**5. Booking path has friction.** Positives get a booking link; the calendar settings changed Nov 11; Josh never booked from a bare link. A personal reply with two specific times (as sent to Jordan) is the better path.""",[])

# ---------- SYSTEM
tab('system',"System map — status of each stage (Nov 12)",
[K('Sourcing','Working','Google Maps pool ~1,600 unsearched'),K('Enrichment','Working','email search running'),K('Verification','Manual','Neal runs Reoon'),K('Personalization','Working','51–53% verified signals'),
 K('Tool pages','Working','deck, hardscape, mortgage, wealth'),K('Sending','Restored','315/day','good'),K('Replies','Working','auto-block opt-outs'),K('Booking','Needs fix','calendar changed','warn')],
"""Lead source → Email search → Reoon (Neal) → Dedupe + fit → Website signals (2× verified) → Phone + brand colour → Tool page (Lovable) → Approved copy → Per-lead proofread → Smartlead W3/W4 → Reply pipeline → Neal approves replies → Booking call.

**Blocked stages for new niches:** HVAC, pool, roofing and all loan-broker niches need a tool page + copy + a new campaign before sending.""",[])

# ---------- MEETINGS
tab('meetings',"Cold email in meetings — latest: Team Huddle Nov 11",[],
"""**No "Cold Outreach Meeting" recording found in Fathom since Nov 4** (the recurring Wed 11 AM ET invite exists on the calendar). The meetings feed now picks up any title containing "cold" automatically.

**Team Huddle — Nov 11** ([Fathom](https://fathom.video/calls/894128818))
- Win: cold email booked a call (strategy call from Raine's cold email); ads booked a qualification call.
- Plan: double down on cold email; add 5–10 inboxes after the next deal; explore niches beyond hardscapers.
- Lead gen: the n8n build scrapes free leads from Google Maps (e.g. Josh Iddins).
- Ana: set up 10 new cold email accounts. **Raine: warm up new inboxes and connect them to Smartlead.**

**Nov 12 (Neal):** new niche order — hardscaping, deck, HVAC, pool builders, roofing (70%); hard money, SBA, business/commercial loans, credit stacking (30%). Mortgage/wealth: finish loaded leads.""",[])

json.dump(T,open('tabs_2026-11-12.json','w'),ensure_ascii=False)
print(len(T),[t['tab'] for t in T])
