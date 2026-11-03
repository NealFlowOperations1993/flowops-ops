# VOC: Roofing

**Source:** `sample_roofing.txt`: 536 reviews total; all 96 at 1–3★ plus a random 80 of 440 at 4–5★. Heavily San Antonio, plus Nashville and Knoxville.
**Noise warning:** ~5 negatives are about reckless company-truck driving, and 1 is about solar-panel cleaning. One firm (Stephens Roofing) contributes ~20 negatives. ~90 negatives are relevant.

---

## 1. Top pains (1–3★, ~90 relevant)

| # | Theme | ~Count | Verbatim |
|---|---|---|---|
| 1 | **Leaks persist after repair or replacement; warranty dodged** | ~20 | "I have now been through 3 "fixes" of the SAME AREA and it is still an issue." / "Later part of 2014 we had them replace our whole roof, 2016 our roof begins to leak. Now Stephens roofing is telling us we are going to have to pay for the patch up!!!" |
| 2 | **No-show for inspection, or the quote never arrives** | ~14 | "He stated I would receive an estimate the next day… I did not receive an estimate… we’re on day 6." / "Today we were scheduled for an Inspection and Evaluation, however no one ever showed, nor did anyone contact me." |
| 3 | **Door-to-door storm chasers ignoring no-soliciting signs** | ~12 | "A representative stopped by my place on a Sunday evening (unsolicited), after we had a recent hailstorm… High-pressure sales tactics, much like storm chasers." / "Salesman knocked on my door even though I have a large NO SOLICITING sign in plain sight." |
| 4 | **Overpriced quotes vs other bids; hidden or extra charges** | ~10 | "Needed two turbines replaced..quoted it would cost $1500!! All the other bids were $300-$400" / "The price seemed competitive at first but ended up being higher once additional “unexpected” costs were added." |
| 5 | **Insurance-claim pressure and confusion** (deductible upfront, overpromising coverage, cut loose when the claim fails) | ~9 | "pressured and coerced into signing an agreement of work and into paying my insurance deductible up front, even before my insurance company (USAA) had an opportunity to inspect my roof." / ""I'll work with your insurance and get it all paid for." Nope. That didn't work. And the estimate was about 2x the amount from others." |
| 6 | **Pushed to full replacement when a repair would do** | ~8 | "out of 3 roofing companies THEY WERE THE ONLY ONES THAT SAID NEED A NEW ROOF!!!" / "Alamo only cares about working with you if you get an entire roof replaced." |
| 7 | **Property damage and nails left behind** | ~9 | "There were multiple roofing nails in driveway… My neighbor actually had one of the moisture barrier nails in his yard that went through his shoe" / "Two nails ended up in my tires, and they have taken zero accountability." |

Predatory financing appears once: "Christian tried to burn me $314 for 20 years… $30k for an asphalt roof… I was just quoted $7k for a 2100 sq. ft. roof from another roofing company."

## 2. What wins (4–5★, n=80)

| Theme | ~Count | Verbatim |
|---|---|---|
| **Handled the insurance claim for me** | ~14 | "Tiffany was especially helpful in navigating the insurance claims process… walking us through each step and handling the paperwork" / "They took care of everything with my insurance company!" |
| **Explained the process honestly; no upsell** | ~14 | "It never felt like a hard sale or an unnecessary up-sale, like other companies I spoke with." / "They gave me a thumbs up on the roof condition (something I wonder what less reputable companies would have said)" |
| **Fair price after comparing several quotes** | ~12 | "Their quote was more affordable than the other roofing bids I received" / "We shopped 4 different bidders, not looking for the absolute lowest price, but more so the value for our dollar." |
| **Clean-up** | ~11 | "Yard is cleaner now than before they came." / "Clean up was thorough, leaving no evidence that a crew had been there." |
| **Fast response to active leaks; quick installs** | ~9 | "I contacted Heaven Sent Roofing in the early morning… Jose was dispatched to my residence within an hour" / "before they came out we had a storm and my roof was leaking. I sent a text to Dustin and they were out within the hour to tarp my roof." |
| **Financing and payment options** | ~4 | "helped me secure financing with a great payment plan that fit my budget." / "Rox gave me the most options at different price points and multiple financing options." |

## 3. Buying-moment questions customers clearly had

- **"Will insurance pay for this, and do I even have storm damage?"** This is the biggest decision driver: ~14 wins and ~9 pains. "I didn't even know I had storm damage…"; "Helped me check out my roof after a hailstorm."
- **"Repair or replace?"** "what repairs were most urgent"; "did some repairs to buy us some time for replacement"; "out of 3 roofing companies THEY WERE THE ONLY ONES THAT SAID NEED A NEW ROOF".
- **"What should a roof cost?"** "$30k for an asphalt roof… quoted $7k for a 2100 sq. ft. roof"; "estimate was about 2x the amount from others"; "We shopped 4 different bidders".
- **"Can I pay over time?"** 4 wins plus 1 predatory-financing pain.
- **"What's the warranty on a repair vs a new roof?"** "this company does not give warranty on any patch repair only on complete roof replacement"; "my warranty was only for two years".
- **"Can it be done before closing or a sale?"** "a very tight timeline before closing on my home"; "My mother passed away and we needed to sell the home"; a realtor's listings.
- **"Is there a minimum charge?"** "Was told there was a $750.00 MINIMUM CHARGE which is NOT LISTED ANYWHERE on their website".

## 4. Proposed tools

### Tool A: Roof Replacement Cost Estimator (with optional payment view)
- **End customer gets in ~30s:** enter address or roof sq ft (or home sq ft plus stories), pitch (low, medium, steep), material (3-tab, architectural, metal, tile) and tear-off layers. See an installed price range per material, what's included (tear-off, underlayment, drip edge, clean-up, warranty years) and an optional monthly view only if the business offers financing.
- **Answers:** pain #4 (overpriced vs other bids), the $30k-vs-$7k financing story, "what's included", warranty questions; wins on fair price after comparing bids, price-point and financing options.
- **Lead fields:** contact, address, roof size, stories, pitch, current and desired material, roof age, leaks yes/no, insurance claim yes/no, timeline (incl. closing date), financing interest.
- **Effort:** M.
- **Confidence: 8/10.** Price comparison is well evidenced, tickets are high and the inputs are simple. Owners who sell mainly through insurance claims may prefer Tool B.

### Tool B: Storm Damage & Insurance Claim Readiness Checker
- **End customer gets in ~30s:** enter the storm date (or "recent hail/wind"), roof age and visible signs (missing shingles, dented vents or gutters, granules in gutters, interior stains), plus whether a claim has been filed. Get "worth an inspection: yes / maybe / unlikely", plain-language claim steps (inspect before signing, how the deductible works) and a free-inspection request.
- **Answers:** the biggest win theme (insurance help, ~14), pain #5 (deductible pressure, overpromising), pain #3 (gives homeowners a self-serve alternative to the door-knocker, which is an inference). It also addresses "I didn't even know I had storm damage".
- **Lead fields:** contact, address, storm date, roof age/material, visible damage checklist, photos, insurance carrier, claim status, deductible, mortgage/HOA, preferred inspection time.
- **Effort:** S–M.
- **Confidence: 7/10.** This is the strongest decision driver in the data. **Guardrail:** the tool must never say "you have damage" (no evidence from a checklist), and it must not ask for a deductible upfront, because those are the exact behaviors customers punish.

### Tool C: Leak Triage + Repair-or-Replace Advisor
- **End customer gets in ~30s:** "Is water coming in right now?" If yes, it shows an emergency tarp request and a do-now list (bucket, move valuables, photo for insurance). If no, it asks roof age, leak history, number of prior repairs and where the stain is, then gives a repair vs replace indication with a rough cost band for each and a warranty note.
- **Answers:** pain #1 (repeat leaks, the top pain), pain #6 (replacement upsell, by giving an honest repair path), fast-tarp wins, "what repairs were most urgent".
- **Lead fields:** contact, address, active leak flag, leak location, roof age, prior repairs (and by whom), photos, insurance yes/no, urgency.
- **Effort:** S.
- **Confidence: 7/10.** Leaks are the top pain and the most urgent buying moment. Repair jobs are smaller tickets, but they often convert to replacements.

## 5. Caveats

- Stephens Roofing (~20) and Alamo Roofing (~15) together make up ~35% of the negatives, which inflates the warranty and door-knocking themes.
- Geography skews to San Antonio (hail country), which over-weights the insurance and storm themes relative to non-hail markets.
- Reviews are truncated at ~500 characters.
- This is customer voice, not owner voice. Storm-chasing firms may want the claim checker, while retail/repair firms may want the estimator.
- Financing evidence is 4 wins plus 1 predatory example. Treat any payment display as optional and owner-supplied, never a promised rate.
