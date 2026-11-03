# VOC: Deck Builders

**Source:** `sample_deck.txt`: 497 reviews total; all 50 at 1–3★ plus a random 80 of 447 at 4–5★. Denver, Northern Virginia, Wilmington NC and Kansas.
**Noise warning:** many listed businesses are general contractors. Several reviews are about driveways, bathrooms, basements, siding, roofs, fences and plumbing. A decking supply yard (Mile High Deck Supply) accounts for 2 negative and ~6 positive reviews. Deck-, porch- or fence-specific reviews are **~30 of 50 negatives** and **~35 of 80 positives**. I counted GC pricing and deposit complaints where the dynamic transfers directly to deck projects.

---

## 1. Top pains (1–3★, n=50; ~40 relevant to a contractor buying journey)

| # | Theme | ~Count | Verbatim |
|---|---|---|---|
| 1 | **Price shock: quote far above other bids, or price raised after the deposit** | ~9 | "Trex materials cost 10K and they wanted 30k to build a small deck that's only 4 feet from the ground." / "Estimate was over 15k higher than the other 2 I received." |
| 2 | **Estimate visit, then ghosted: no written quote, renderings or bid** | ~9 | "I was given a rough estimate in person and I was told that I would get renderings in an email… I never received a response." / "I set up a time with Larry for someone to come out and give a bid. Took off from work and NO one showed up or Called." |
| 3 | **Poor or unsafe workmanship** | ~9 | "It was wavy and slated and unsafe by the code. How can you be a deck builder and not be able to build a safe deck?" / "The board gaps range from 3/8" to over 1", well beyond Trex's 3/16" spec." |
| 4 | **Delays and no-shows mid-project** | ~8 | "They dug three big holes, filled one in and left after four hours.Haven’t heard a word since" / "I just spent 5 months being lied to, flaked on, and given the runaround… and never even had my project started." |
| 5 | **Deposit risk** (large upfront deposit, then scope or price change, refund refused) | ~5 | "They also require half the money up front for materials… contactors can very easily rip you off after you have paid the 50% deposit" / "after taking our deposit check they jacked up the quote doubling the quoted cost" |
| 6 | **Scope ambiguity: what the quote includes** | ~5 | "they tried to say the quote for the stain (which was over $500) only included stain on the repaired piece of wood" / "They did not arrive with the cleaner/brightener that was included in their estimate" |
| 7 | **Silence on warranty or after-care issues** | ~5 | "Be Prepared for Silence if Issues Arise" / "Electrical was installed incorrectly, still doesn’t work, and despite several communications, Deckman has refused to fix the problem." |

## 2. What wins (4–5★, n=80; ~35 deck/porch/fence/patio)

| Theme | ~Count | Verbatim |
|---|---|---|
| **Clear, fair, itemized pricing; no surprises** | ~12 | "Estimate was clear and reasonable compared with others." / "we appreciated the break out of all the costs involved so there were no surprises." |
| **Communication throughout the build** | ~10 | "There was never a time where I felt like I wasn’t in the know, and when you are spending thousands of dollars, this makes homeowners feel at ease." / "The project manager kept me informed of each step and stage, delays… and progress." |
| **Design help: listened to the vision, offered options** | ~8 | "he listened to our ideas for the layout, paver colors, and seating area, then offered thoughtful suggestions" / "came back with a detailed plan and reasonable bid." |
| **Fast quote and start** | ~6 | "Michael provided a same-day quote, and once I accepted the proposal, a crew was mobilized within 24 hours." / "We asked for a virtual quote on our first level deck and we watched it come to life exactly as we had envisioned it." |
| **Honest assessment of an existing deck; handles hidden rot fairly** | ~5 | "walked through his assessment of potential issues and the best way to solve her concerns… honest and straightforward." / "the structure had decay that was not visible… handled the changes in the scope of the job with great professionalism." |
| **Staged payments rather than a big deposit** (thin) | 1 | "I also appreciated that the payments were divided between each stage rather than a lump invoice or upfront payment." |

## 3. Buying-moment questions customers clearly had

- **"What should a deck like mine cost?"** This is the dominant question. Buyers anchor on materials cost ("Trex materials cost 10K"), state budgets ("a large deck with a $10k budget"; "my possibly $25,000 deck"; "extremely tight budget… as a starting off point on where to even begin") and collect 2–5 bids (lines 5, 86, 119, 130, 108).
- **"Wood or composite?"** "refinishing it every 3 years… paying the deck refinisher guys a bunch of money"; composite, Trex and steel decks all appear in wins.
- **"Repair or replace my old deck?"** "I have a 25+ year old deck that needs replaced"; "My mom moved into a home and had some concerns around her deck"; a deck inspection for a real-estate sale (line 106).
- **"How much deposit, and when do I pay?"** (pain #5, staged-payment win).
- **"What exactly is included?"** (stain, cleaner, post caps, railings, stairs, lights).
- **"Can it be done by X?"** "I was hoping to have my very basic deck repairs finished before my my pregnant wife was due"; "This is the summer I have a hot tub, bbq, and gorgeous new deck."
- **Permits and HOA:** "K&A handled the building permit, inspection"; "helpful as I worked through our HOA requirements" (fence).

## 4. Proposed tools

### Tool A: Deck Cost Estimator (size × material × features)
- **End customer gets in ~30s:** enter dimensions (or pick S/M/L), height off the ground, material (pressure-treated, cedar, composite/Trex, PVC), railing type, stairs, cover or screen porch, lighting. Get an installed price range with a line-item breakdown (materials vs labor) and a typical build time.
- **Answers:** pain #1 (price shock vs other bids), #6 (what's included), #5 (shows deposit and payment terms if the business sets them); wins "break out of all the costs", "estimate was clear and reasonable compared with others", "virtual quote".
- **Lead fields:** contact, address, new vs replacement, dimensions, height, material, railing, stairs, extras, budget band, target completion date, HOA yes/no, photos (optional).
- **Effort:** M.
- **Confidence: 8/10.** Price is the single clearest buying-moment question, and the evidence is in customers' own numbers. Regional pricing calibration is the risk.

### Tool B: Repair, Resurface or Replace? Old-Deck Checker
- **End customer gets in ~30s:** answer about age, material, soft or spongy boards, wobbly railings, visible rot or rusted fasteners, and ledger attachment. Get a verdict (maintain / repair / replace) with a safety flag, plus a rough cost range for each path.
- **Answers:** aging-deck buyers ("25+ year old deck"; "rotten boards on our deck"), honest-assessment wins, hidden-decay wins, the unsafe-deck pain.
- **Lead fields:** contact, address, deck age, material, symptom checklist, safety flag, photos, selling/buying-home flag, timeline.
- **Effort:** S–M.
- **Confidence: 6/10.** A plausible high-intent trigger with good win evidence (~5), but direct "repair vs replace" questions are only ~4 reviews. Must not assert a safety failure from a checkbox; present it as "get it inspected".

### Tool C: Wood vs Composite 10-Year Cost Calculator
- **End customer gets in ~30s:** enter deck size. See upfront plus 10–20-year maintenance cost (staining or sealing cycles) for wood vs composite, with a breakeven year. Then "get a quote for this deck".
- **Answers:** the material question (redwood refinishing story, Trex and composite wins); the "is it worth it" angle.
- **Lead fields:** contact, ZIP, deck size, current material, preferred material, current maintenance spend, timeline.
- **Effort:** S.
- **Confidence: 5/10.** Only ~3–4 reviews raise materials directly. It's a good "is it worth it" hook, but intent is lower than a direct estimate.

## 5. Caveats

- A heavy share of the sample isn't decks (GCs doing bathrooms, basements, roofs, siding, driveways). Deck-specific evidence is ~30 negative and ~35 positive reviews.
- One business (JOB Home Services) accounts for 10 of the 50 negatives, which inflates the "no-show / poor workmanship" counts.
- Reviews are truncated at ~500 characters.
- This is customer voice, not owner voice. Builders' willingness to publish ranges is unknown.
- Financing never appears in this sample. Don't build a financing tool for decks on this evidence.
