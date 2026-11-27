# VOC: Tree Service

Source: `sample_tree.txt`. There are 533 reviews in total. The sample holds all 47 reviews at 1–3★ and a random 80 of the 486 at 4–5★. I read every line.

The noise is small:
- one Christmas-tree farm (1 negative, 2 positives)
- one mowing complaint
- about 4 driving or rudeness complaints
- one review in Russian with no content ("not good… be careful")

Several negatives come from **neighbors** of a job, not the paying client.

## 1. Top pains (1–3★, n=47)

| # | Theme | ~Count | Verbatim |
|---|---|---|---|
| 1 | **Can't get an estimate or a date: unreturned calls, no-shows, scheduling limbo** | ~16 | "Never returned phone call after a week, asking for estimate." · "We were scheduled for an estimate for 2 large fir tree removal. No one showed. No one called." |
| 2 | **Work didn't match the quote: scope skipped, quote not honored, wrong equipment** | ~8 | "I was promised two trees in my back yard would be trimmed. I came home to find one tree trimmed and the other one not touched." · "decided the job was underbig, it was too much work and wouldn't honor the quote" |
| 3 | **Property damage: fences, gutters, roofs, cars, brickwork** | ~8 | "…damaging our fence and gutters by allowing a crane to drop a tree which landed on our house." · "Left a huge mess of branches, created a fire hazard, damaged our fence and the tree next to it" |
| 4 | **Price and value: quote too high, or cost felt unjustified** | ~7 | "For $1300, they spent about a hour at our home." · "I … was astonished by the outrageous quote in comparison to other estimates" |
| 5 | **Mess and neighbor impact: debris, blocked driveways** | ~6 | "I watched them use their blower to spread debris down the street" · "…park in my apartment complex's only entrance and block all of our cars in for multiple days in a row." |
| 6 | **Bad pruning or wrong tree-health call** | ~4 | "they just hacked the entire top of the trees off and ruined those beautiful dogwoods" · "I pointed out two limbs on the tree that looked dead to me. I was assured they were alive. One dropped a few months later." |

Pain 1 is the dominant theme by a wide margin. Inside it, at least 6 reviews are about the **estimate stage itself**: the first contact never turns into a quote. Other examples: "Won't return phone calls promptly and gave vague arrival times." and "It took several weeks, and multiple calls from me, to even hear back about scheduling."

## 2. What wins (4–5★, n=80)

| # | Theme | ~Count | Verbatim |
|---|---|---|---|
| 1 | **Fair price, often "best of several quotes"** | ~25 | "He not only had the best quote from all the bids we had" · "gave the fairest quote of four companies we called." |
| 2 | **Thorough cleanup** | ~22 | "They did not leave any debris in the yard" · "We were impressed with the thorough clean up after they completed the…" |
| 3 | **Fast response, especially after storms or emergencies** | ~12 (8 storm/emergency) | "We had a large limb break off and went through the roof into a bedroom closet. I call on Labor Day … He came that day" · "Will came out within 2 hours to remove the branch." |
| 4 | **Expert explanation and options; estimate matched the final price** | ~13 | "gave me a few options for scope to balance our needs with our budget." · "gave me a rough cost before I got the actual cost. Which both were very close." |
| 5 | **Did exactly what was agreed, on time** | ~12 | "They showed up on time, did the work described in the contract and left the yard as we asked." · "Mark's bid was excellent, and they stuck to it" |
| 6 | **Careful with property** | ~10 | "Crew placed large mats to protect the grass when the bobcat was used." · "very careful not to drop limbs on our new deck" |

## 3. Buying-moment questions

- **"What should this cost, and is this quote fair?"** About 12 reviews say they compared several bids: "three other local arborists bid our project", "I got a few quotes before deciding who to hire", "I was pulling quotes from everywhere", "fairest quote of four companies". Seven negatives are about price.
- **"Is this tree dangerous, and how urgent is it?"** About 9 reviews mention dead, dying or leaning trees: "several dead and waiting to cause damage", "leaning on a terrible angle and growing closer to the house each year", "had not yet leafed this spring. The tree was dying", "a tree that was endangering a neighbor's home". Another review says "he was worried about the health of one of my trees (he was right, it was diseased…)".
- **"Can someone come now? There's storm damage."** About 8 reviews: "damaged by our recent ice storm", "an extremely large oak tree fell on my back porch and roof", "removing a 40 ft. leaning dead tree before the ice storm".
- **"When will you actually show up?"** This is Pain 1 (~16 reviews).
- **"What's included: stump grinding, haul-off, the neighbor's overhanging branches?"** Evidence: "did not remove the stump at that time", "took care of the stump for a very small fee", "Didn’t trim neighbors tree as they said they would", and about 5 stump mentions.
- **"Do I need a permit, and are you insured?"** Evidence: "He helped us navigate tree permit application with City of PDX", "didn't pull the correct permits", "They provided a written estimate and certificate of insurance."
- **"Can you handle my access or equipment situation?"** Evidence: a steep driveway, "they don't have one [bucket truck] and won't tell you beforehand", and a crane in narrow confines.

## 4. Proposed tools

### Tool 1: Tree Job Price Estimator (removal, trim, stump)
- **What the end customer gets in about 30 seconds:** For each tree they choose the job (remove / trim / deadwood / stump only), a height band (<30 ft, 30–60, 60+), proximity (over the house, near power lines, open yard), access (backyard, steep, narrow) and extras (stump grinding, haul away wood, leave firewood). They get a price range per tree and in total, plus a written scope checklist of what is and isn't included.
- **VOC it answers:** Pain 4 and the most common buying question (comparing many bids). Win 4 ("rough cost … very close" to the actual) shows customers value an accurate early number. The per-tree written scope speaks to Pain 2 ("did not perform what was on the quote", one of two trees trimmed).
- **Lead fields:** number of trees; type, height, job and hazards for each tree; access notes; extras; photos; urgency; ZIP/address; HOA or permit flag; contact.
- **Build effort:** M.
- **Confidence: 7/10.** "Fair quote out of several bids" is the most common win theme. The written-scope output addresses a documented complaint.

### Tool 2: Is My Tree a Risk? (Urgency Checker)
- **What the end customer gets in about 30 seconds:** They tick warning signs: leaning or a new lean, dead or hanging limbs, no leaves in season, cracks or splits, fungus at the base, over the house, driveway or lines, storm damage. They get an urgency tier ("Get it looked at this week" / "Schedule an inspection" / "Monitor"). The tool frames this as signs worth an arborist inspection, **not** a safety guarantee.
- **VOC it answers:** About 9 reviews about dead, dying or leaning trees ("several dead and waiting to cause damage", "growing closer to the house each year"). It also covers Pain 6 (wrong health call on dead limbs) and the "worried about the health of one of my trees" story.
- **Lead fields:** symptoms, tree location relative to structures, approximate height, photos, tier result, best time for an inspection, address, contact.
- **Build effort:** S.
- **Confidence: 7/10.** Urgency produces high-intent leads, and the evidence is concrete. Keep the copy free of safety assurances.

### Tool 3: Storm Damage Fast Request
- **What the end customer gets in about 30 seconds:** A mobile-first emergency form: what happened (limb on roof, tree on house, blocking the driveway, hanging limb, down in the yard), photo upload, and whether anyone is at risk or power lines are involved. They get an on-screen "what to do now" checklist (stay clear of lines, photograph for insurance) and confirmation that the request was sent to the business.
- **VOC it answers:** Win 3 (same-day storm response is praised: "He came that day", "within 2 hours"). It also tackles Pain 1 head-on: a structured request with photos gives the business what it needs to quote fast, in place of a voicemail that never gets returned.
- **Lead fields:** damage type, structures affected, power-line flag, photos, insurance claim (Y/N), address, callback number, availability.
- **Build effort:** S.
- **Confidence: 6/10.** The highest-intent lead of the three, but seasonal. It is only valuable to firms that take emergency work. Note: the tool cannot fix a business that doesn't call back.

## 5. Caveats
- The sample is reasonable: 47 negatives across about 15 businesses. Some businesses dominate, for example All Around Arbor (10 negatives) and Tree Masters (7).
- About 8 negatives were written by neighbors, not customers (blocked driveways, debris), so they say little about the buyer's decision.
- These are end-customer reviews, not owner voice. Owners' willingness to adopt a public price estimator is untested, and some arborists avoid published pricing.
- The storm theme is regionally clustered: Portland ice storm, NC hurricane/lightning. Counts are approximate hand-tags, and one review can carry several themes.
