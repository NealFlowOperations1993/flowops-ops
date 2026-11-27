# VOC: Pool (builders, remodel, repair)

**Source:** `sample_pool.txt`: 412 reviews total; all 77 at 1–3★ plus a random 80 of 335 at 4–5★. Mostly Phoenix and Tampa businesses.
**Noise warning:** the sample includes some businesses that are not pool companies: a tile supply house (Noble Tile, ~10 reviews), a concrete coatings firm (Cardinal, ~13), a rebar sub (Scholz, ~9), a luxury home builder (Steven Anthony, ~11), bathroom/kitchen remodelers (Salt & Pepper, UV Builds) and a fire-bowl maker. I counted pool-deck coating complaints as pool-relevant. I excluded tile-store retail complaints from the themes below.

---

## 1. Top pains (1–3★, n=77; about 60 are relevant to pool contracting)

| # | Theme | ~Count | Verbatim |
|---|---|---|---|
| 1 | **Quote or estimate never delivered; no callback after the sales visit.** The buyer is ready to buy but can't get a number. | ~15 | "The sales person came to our house and took some measurements… Several weeks later, I have yet to hear back. I sent a follow up email asking when I will get my quote...still waiting." / "he took measurements of our backyard and answered all my questions. THEN.....I never heard from him again! Its been almost a month, I haven't seen any designs" |
| 2 | **Workmanship defects** (tile falling off, cracked cool deck, coatings peeling, leaks) | ~13 | "sir the tile is falling off their pool" / "My cool deck concrete around the pool has now cracked and several tiles in the pool have cracked." |
| 3 | **Service collapses after final payment** (warranty and post-build support) | ~11 | "The service has gone into the toilet once they received full payment for the construction." / "once you cut them the check the customer service goes from great to horrible." |
| 4 | **Timeline promised at signing, then missed** | ~11 | "Was told our pool would be finished in August. Guess what? There is not even a hole dug in our backyard!… If they would have told us October… I would have gone with another company." / "Our pool was delayed by a long time and took about 9 months to finish." |
| 5 | **Price surprises and deposit disputes** (price rose after scope cut, non-refundable deposit, fee for estimate) | ~9 | "we made some modifications to fit the budget, however, the price actually went up even though we reduced some things." / "A week later I received a bill for $105 just for the estimate." |
| 6 | **Communication blackout during the build** | ~8 (overlaps #3, #4) | "There is zero communication from our project manager." / "getting ahold at anyone in the office, sales rep or construction super is near impossible." |
| 7 | **Home buyers or sellers can't get a repair quote during escrow** (weak but specific) | 3 | "I'm in escrow on a home that needs significant work done on a pool… they stated that they will not visit a property to give a quote" / "they refused to give us a quote because the sale is not final" |

## 2. What wins (4–5★, n=80; about 45 are actual pool or pool-deck reviews)

| Theme | ~Count | Verbatim |
|---|---|---|
| **Seeing the design or rendering before building** | ~7 | "We really appreciated getting a design image that showed how our backyard pool project would look before construction started." / "Hive Outdoor Living, hit a home run from the initial computer assisted design demonstration using our home specs" |
| **Proactive communication and set expectations** | ~10 | "proper scheduling expectations were set and met." / "Staff were friendly and helpful in giving information ahead of when each phase was to begin." |
| **On schedule and within budget** | ~8 | "Our new pool was completed on schedule and stayed within the budget we expected." / "They did a great job staying in budget and got everything done within our timeline." |
| **Clear, competitive estimates at several price points** (buyers compare 3–7 bids) | ~7 | "sought proposals and quotes from six companies… ensuring we received detailed options and estimates at various price points." / "We chose Emerald Pools to resurface our pool and decking after getting 3 other bids." |
| **Educating first-time owners and answering questions after the build** | ~6 | "I'm a first time pool owner… not only replaced the pump quickly but taught me how to care for the pool." / "Had questions as we are pool novices. All questions received prompt attention." |

## 3. Buying-moment questions customers clearly had

- **"What will it cost me?"** Buyers wait weeks for a number (pain #1). The salesperson "gave a general feel for what a pool would cost" but no written figure followed. Buyers compare 3–7 bids (lines 141, 145, 157, 81).
- **"What can I get within my budget?"** "we made some modifications to fit the budget". Winners offered "estimates at various price points".
- **"When will it be finished?"** The August-vs-October complaint shows the timeline decides which builder gets the job.
- **"What will it look like?"** Renderings are praised repeatedly.
- **"Is the deposit refundable, and what's in the contract?"** "The non-refundable deposit was never stated verbally or in writing." / "I requested something and had it written in the contract and it was left off."
- **"Can I get a repair quote before closing?"** 3 escrow reviews.
- **"What's wrong with my pool or equipment?"** (green water, leaks, failed pump or ozone system). This shows up in about 6 reviews across both star groups.

## 4. Proposed tools

### Tool A: New Pool Budget & Timeline Estimator
- **End customer gets in ~30s:** pick pool size/shape, spa yes/no, deck type, water features and finish level, and see a price range for each tier (good, better, best) plus a typical build timeline in months.
- **Answers:** pain #1 (no number after the visit), #4 (timeline), #5 (budget surprises); wins "estimates at various price points", "within the budget we expected".
- **Lead fields:** name, phone, email, address/ZIP, pool size/shape, spa, deck sq ft and material, features, finish tier, budget band, target completion date ("swim by"), HOA yes/no, financing interest.
- **Effort:** M (needs a regional price table per business, or a default with a caveat).
- **Confidence: 8/10.** This is the most-cited pain, and the buyers are clearly high-intent and comparing bids. The risk is that builders won't like publishing ranges.

### Tool B: Pool Remodel / Resurface Quote Builder
- **End customer gets in ~30s:** enter pool age, current surface (plaster, pebble, tile line), deck condition and desired upgrades, and get a remodel price range plus a "resurface vs full remodel" indication.
- **Answers:** remodel/resurface reviews (lines 92, 123, 131, 145, 157); "Brought them in for a quote to remodel our pool"; budget/price-point wins.
- **Lead fields:** contact, address, pool age, sq ft or gallons if known, surface type, issues (cracks, stains, tile loss), upgrades wanted, photos (optional), timeline.
- **Effort:** M.
- **Confidence: 6/10.** The evidence is real but spread thin across a few reviews, and pricing varies a lot.

### Tool C: Pool Problem Triage + Repair Request (incl. "buying/selling a home" mode)
- **End customer gets in ~30s:** pick the symptom (green or cloudy water, losing water, pump/filter noise or leak, equipment won't run, cracked deck or tile) and get a likely cause, an urgency level and safe DIY checks. Then request a diagnostic visit. An "in escrow / selling" toggle requests a written quote by a deadline.
- **Answers:** escrow pain (#7, 3 reviews); equipment failures ("my pool is turning green", "about 2500 gallons of water saturating the ground"); first-time-owner education wins.
- **Lead fields:** contact, address, symptom, equipment brand if known, photos, urgency, escrow/closing date, realtor/inspector report upload (optional).
- **Effort:** S–M.
- **Confidence: 5/10.** The pain is real, but escrow and repair evidence is thin (~3–6 reviews), and repair jobs are lower-ticket than builds.

## 5. Caveats

- Small sample: ~60 relevant negative and ~45 relevant positive reviews. Counts are approximate and themes overlap.
- About 25–30% of the sample is adjacent businesses (tile supply, coatings, rebar, home builders, bathroom remodelers). This dilutes the pool-specific signal.
- Reviews are truncated at ~500 characters, so many complaints end mid-story.
- This is end-customer voice, not owner voice. It says nothing about which tools pool owners would agree to put on their site.
- Geography skews to Arizona and Florida (ROC references are Arizona-specific).
- Financing never appears explicitly in this sample. Don't build a financing tool for pool on this evidence.
