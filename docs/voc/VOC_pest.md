# VOC: Pest Control

**Source:** `sample_pest.txt`: 508 reviews total; all 61 at 1–3★ plus a random 80 of 447 at 4–5★. Texas (Houston/Kingwood) and Charlotte/Raleigh.
**Noise warning:** 14 of the 61 low-star reviews are for **M&D Supply Ace Hardware** (a hardware store and post office) and are irrelevant. One 5★ is a lawn company. The real pest-control negative base is **~47 reviews**.

---

## 1. Top pains (1–3★, ~47 relevant)

| # | Theme | ~Count | Verbatim |
|---|---|---|---|
| 1 | **Treatment didn't work or pests came back; warranty re-service not honored** | ~11 | "with in a week got pest activity in home and they didn’t come for warranty and stopped attending my calls." / "Our ant treatment in the kitchen was unsuccessful. We scheduled a follow-up treatment but the tech never showed up." |
| 2 | **Aggressive door-to-door sales** (ignoring no-soliciting signs, rude reps) | ~10 | "3 no soliciting signs and these buds are out twice a day knocking on my door." / "Rep has been coming by all week and will ring doorbell again if they see us coming home." |
| 3 | **No-shows, changed windows, no arrival notice** | ~10 | "had a time of 9-11 am set , I took time off for this and the it was changed to 1030-1230 with out confirming with me first." / "I never received a text that Josh was coming out." |
| 4 | **Contract and billing deception** (unexpected 1-year contract, charged a different amount, cancellation fees) | ~9 | "the service was presented to me in a way that made me believe it was month-to-month. I was never clearly informed that I was agreeing to a one-year contract" / "they knock your door they give a price then… after they have your credit card information they charge you a diferent amount" |
| 5 | **Fear-based upsell / inflated diagnosis** | ~5 | "was told I need about 1000 worth of treatments over several months (before they even came to the property) Later the honest kid that was here told me I only needed 2." / "I was told I had an active termite issue, and pushed me into paying over $2400 on termite traps." |
| 6 | **Scope mismatch: what's actually treated** (inside vs outside, "entire property", nest not removed) | ~5 | "he said the phrase "we treat your entire property" no less than 5 times. What this actually means… "We normally do our granulation 10ft in all directions" / "They came and treated only the lower level and left the wasp nest." |
| 7 | **Safety for kids, pets and lawn ignored** (weak) | ~3 | "I told the company repeatedly not to treat my grass due to having a 3 month old" / "moving my daughter and her baby into our RV when we discovered that there were wasps everywhere" |

Also seen once: a home-purchase WDI (termite) report done wrong ("we needed was the Texas Official Wood Destroying Insect (WDI) report required for the real estate transaction"). That's 1 review, so it's anecdotal.

## 2. What wins (4–5★, ~79 relevant)

| Theme | ~Count | Verbatim |
|---|---|---|
| **Tech explains the process and answers questions** | ~13 | "He took the time to listen to my concerns, clearly explained what he would be doing and what to expect" / "took the time to explain everything clearly, answered all of my questions, and made me feel confident about the treatment plan." |
| **Reasonable price, often after comparing quotes** | ~12 | "I called 4 places for quotes… Proforce was the most reasonable amount AND was able to come next" / "priced really well compared to other quotes I got around Charlotte." |
| **Same-day or fast response to an active problem** | ~10 | "They answered my call promptly and sent someone to my home within just three hours." / "John was able to come out to take care of a hornet's next at my home the same day I reached out." |
| **It actually works** (visible reduction) | ~10 | "We’ve seen a dramatic reduction in bugs & spiders after their treatments." / "Used Apache 1 1/2 years ago and did not see a roach until this month." |
| **Low pressure, clear terms, guarantee** | ~5 | "I really appreciate the low-pressure environment where I’m not held to a contract." / "it came down to confidence with the overall package… the clarity of contract, products used, the termite bond" |
| **Pet and family safety instructions** | ~4 | "let me know when it was a good time to let her back in the yard" / "made sure we understood how to keep our pets safe." |

## 3. Buying-moment questions customers clearly had

- **"How much will this cost?"** Buyers shop 4–10 firms ("I called 4 places for quotes"; "after speaking with 10 firms in CLT"; "I got some quotes from several companies").
- **"Is it a contract, and can I cancel?"** Pain #4 plus the low-pressure win. This is a top trust question.
- **"Is this infestation real, and how bad is it?"** The mice and termite upsell reviews show customers can't judge severity themselves.
- **"How fast can you come?"** Active-problem panic: "What a panic I was in! Coming home from vacation with an unexpected bill is no fun."
- **"What exactly gets treated?"** Inside vs outside, nest removal, "entire property".
- **"Is it safe for my kids and pets?"** (4–7 reviews across both groups.)
- **"What does the monthly plan cost after the first visit?"** "after the initial fee, it’s only 54.00 a month for me".

## 4. Proposed tools

### Tool A: Pest Problem Quote Estimator (one-time vs plan)
- **End customer gets in ~30s:** pick the pest (ants, roaches, spiders, rodents, wasps/hornets, mosquitoes, termites, wildlife), where it is (inside, outside, attic) and home size. See a typical one-time treatment range vs. a quarterly-plan price, with the contract terms stated up front ("no contract" or "12 months" as the business sets it).
- **Answers:** pain #4 (contract/billing surprise), #5 (inflated quotes), #6 (scope); wins on price after comparing quotes and on low pressure.
- **Lead fields:** contact, address, pest type, location in the home, severity (seen once / daily / visible nest or droppings), home sq ft, kids/pets yes/no, preferred service (one-time vs plan), urgency.
- **Effort:** S–M.
- **Confidence: 7/10.** Comparison shopping is well evidenced. The risk is that many pest firms quote only after inspection and may resist posted prices.

### Tool B: "How Bad Is It?" Infestation Severity & Urgency Checker
- **End customer gets in ~30s:** answer 5–6 sign questions (droppings, noises in the attic, mud tubes or soft wood, nest size, how many seen per day, bites). Get a severity level (monitor / treat soon / call today), a what-to-do-now tip including pet and kid precautions, and "request same-day inspection" if urgent.
- **Answers:** the fast-response win (~10), panic moments, the upsell distrust (#5: gives the customer an independent read before the tech arrives), and safety (#7).
- **Lead fields:** contact, address, pest, signs checked, severity result, photos, vulnerable occupants (baby, elderly, pets), preferred time window, "need same-day" flag.
- **Effort:** S.
- **Confidence: 7/10.** It captures the highest-intent moment (an active problem). The result logic must not claim a diagnosis; present it as "signs suggest".

### Tool C: Termite / Wildlife Inspection Request (incl. real-estate WDI mode)
- **End customer gets in ~30s:** choose termite or wildlife (raccoon, bats, rodents in the attic). For termites, a "buying/selling a home?" toggle shows what the closing report usually requires. They get an inspection booking slot plus what the inspection covers.
- **Answers:** high-ticket exclusion and termite work (wins on raccoon, bats and rodent exclusion; "$1,250+ for rodent exclusion"; "$2400 on termite traps"); the WDI review.
- **Lead fields:** contact, address, issue type, signs, closing date, lender/realtor, loan type, report needed by.
- **Effort:** S.
- **Confidence: 5/10.** Tickets are high, but there's only one WDI review, wildlife evidence is ~6 reviews, and the right report name varies by state.

## 5. Caveats

- ~23% of the low-star sample is a hardware store, so the real negative base is ~47 reviews.
- Door-to-door sales (#2) is the loudest theme, but **no tool fixes it**. It's a channel-trust problem. It does suggest that inbound, self-serve tools are a welcome alternative, but that's inference, not evidence.
- Reviews are truncated at ~500 characters.
- This is customer voice, not owner voice. Many pest businesses run on recurring plans and may value plan sign-ups over one-time quotes.
- Positive reviews are mostly short tech shout-outs ("Matt is great"), so they're thin on buying-decision detail.
