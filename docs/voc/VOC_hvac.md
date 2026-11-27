# VOC: HVAC

**Source:** `sample_hvac.txt`: 352 reviews total; all 118 at 1–3★ plus a random 80 of 234 at 4–5★. Dallas/Plano (DFW) and Atlanta.
**Noise warning:** ~8 negatives are about reckless company drivers, not service. Two large multi-trade firms (Barbosa Plumbing & AC, Harlen Johnson/NTX) contribute ~37 negatives, and roughly half of those are **plumbing** jobs (drains, water heaters, gas lines). I kept them in the pricing and upsell themes because the dynamic is identical, but HVAC-only counts are lower than the totals. One firm (Airtron, a builder-contracted installer) contributes 20 negatives.

---

## 1. Top pains (1–3★, n=118; ~110 service-related)

| # | Theme | ~Count | Verbatim |
|---|---|---|---|
| 1 | **Pushed to replace or buy expensive parts; a second opinion found a cheap fix** | ~20 | "he said the unit had a leak and tried to convince me that I needed to replace the whole system for $7,500… I called a different independent technician and he quickly diagnosed a bad capacitor and fixed my AC for only $250." / "Tech informed me unit was pulling too many amps, and suggested a new unit for 6k.. Called another company replaced a coil for 100.00" |
| 2 | **Opaque or inflated pricing and fees** (quotes 2–4× others; service-call and diagnostic fees; no itemization) | ~18 | "I was quoted nearly $2,000 to fix my A/C unit, including a $469 capacitor… After getting other quotes, I was able to get a new capacitor for $205" / "the call is $85 plus $129 to look at each unit. So they wanted me to pay $387 plus tax to breathe on my unit." |
| 3 | **New install fails; installer won't stand behind it** | ~18 | "We spent $12k on a new system expecting professional installation…" / "i paid $8,500. Now they said it’s not their fault and i have to pay an additional $360 to fix?" |
| 4 | **No-shows and no arrival window** (customer stuck home all day) | ~16 | "3 separate appointments, each requiring me to stay home the entire day because they refuse to provide even a basic time window." / "Promised they were going to service my AC on a Saturday! Never showed up." |
| 5 | **Left without AC or heat in extreme temperatures, often with vulnerable occupants** | ~8 | "I’m a disable veteran without AC… you gave me an appointment time well over 24 hours in triple digit temperatures." / "I am a kidney patient that handle these temps." |
| 6 | **Safety hazards from bad work** (CO venting, fire, smoke) | ~4 | "this pipe that leaves the furnace is the way it evacuates poisonous carbon monoxide gas" / "This resulted in my house almost catching on fire" |
| 7 | **Wrong-sized system** (weak but specific) | 3 | "The system is 1.5 tons smaller than the recommended unit for my size house." / "installing only 1 unit that is way too small for a two stories." |

Financing appears once, as a pain: "We did financing with Synchrony from their website because we are poor… it appears that a whole house project needs to be charged at once."

## 2. What wins (4–5★, n=80)

| Theme | ~Count | Verbatim |
|---|---|---|
| **Same-day or fast response when the system is down** | ~17 | "Our system went out, and they were out same day 2 hours later and had us up in running in an hour." / "We woke up with no heat on Christmas Eve and he came out promptly" |
| **Fair or affordable price** | ~14 | "Lest than the three quotes from the big guys" / "gave us a repair bill well under what we thought it would be" |
| **Explains the problem and answers questions** | ~11 | "They went above and beyond… to make sure I understood what was happening, how it may have occurred, what the process involved to fix my issue" / "Brandon answered all my questions and set up my HVAC for the season." |
| **Honest: repaired instead of replacing** | ~6 | "Had all the big boy A/C Companies out and all said to scrap it… Cowboy Service came out fixed it for fair price" / "The previous company… told me the whole unit was bad and needed to be replaced and the cost would be around $2000-$5000." |
| **Maintenance relationship and long-term trust** | ~6 | "I highly recommend to the point I signed up with their maintenance program" / "Replaced my furnace last year, has maintained both of my HVAC systems for years." |

## 3. Buying-moment questions customers clearly had

- **"Repair or replace?"** This is the dominant question and the core of the trust problem: ~20 negatives (pain #1) and ~6 wins hinge on it. "They saved me a ton of money, because I have an old furnace… Otherwise, I would have had to get a whole new furnace which costs thousands."
- **"What is this going to cost?"** "We were terrified at what this repair bill would be". Shoppers compare 3–5 quotes ("three quotes from the big guys"; "We initially spoke to a total of 5 companies").
- **"Is the service-call fee waived if I hire you?"** "They did try to include the service call charge in the final bill even though I was told that the service call will be waived"; also the $85, $95, $125 and $154 diagnostic fees.
- **"How fast can you get here?"** Heat or cold emergencies, often with seniors, patients or babies.
- **"Is this covered by my warranty?"** "I was told that the motor for my AC was broken but covered under warranty. I was then charged $1500 for “labor”"; "they found my warranty info and were open and honest".
- **"Is my system the right size?"** (3 reviews, all one builder subdivision.)
- **Financing** (1 review). Thin.

## 4. Proposed tools

### Tool A: AC/Furnace Repair-or-Replace Calculator
- **End customer gets in ~30s:** enter system age, type (AC, heat pump, furnace), the repair quote they have (or the symptom), how many repairs in the last 2 years and home sq ft. Get a verdict (repair / borderline / replace) using the common age × repair-cost rule, plus a rough new-system range. CTA: "get a second opinion visit".
- **Answers:** pain #1 (~20 reviews of replace-upsell vs cheap fix), pain #2 (inflated quotes), wins on honest repair-not-replace, "terrified at what this repair bill would be".
- **Lead fields:** contact, address, system type/age/brand, symptom, existing quote amount and company (a strong signal), repairs history, sq ft, warranty status, "want a second opinion" flag.
- **Effort:** S–M.
- **Confidence: 8/10.** This is the strongest, most specific theme in any of my five niches, and it captures customers holding a competitor's quote. The business must be comfortable sometimes saying "repair".

### Tool B: No-Cool / No-Heat Emergency Triage
- **End customer gets in ~30s:** pick the symptom (not cooling, blowing warm, frozen line, water leaking, no heat, strange smell or smoke). Get 3 safe checks (breaker, thermostat, filter, condensate), a safety stop if gas or smoke is present, and an urgency score that factors in indoor temperature and vulnerable occupants. Then request the earliest slot with an arrival window.
- **Answers:** pain #4 (no arrival window), #5 (vulnerable people in heat), #6 (safety); the dominant win "same-day, fast response".
- **Lead fields:** contact, address, symptom, indoor temp, system age, vulnerable occupants (elderly, medical, infant), checks already done, preferred window, "need today" flag, landlord or tenant.
- **Effort:** S.
- **Confidence: 7/10.** This is the highest-intent moment and well evidenced on both sides. The value depends on the business actually honoring speed, since the tool raises expectations.

### Tool C: New System Price & Sizing Estimator (with fee transparency)
- **End customer gets in ~30s:** enter sq ft, stories, current tonnage if known, fuel type and efficiency tier. See a suggested capacity band (flagged "confirm with a load calc"), an installed price range per tier, and what's included (permits, thermostat, labor warranty). An optional monthly-cost view is only shown if the business offers financing.
- **Answers:** the undersized-unit pain (3), install price comparison (5-company shopping), "what's included" (extended labor warranty disputes), the one financing mention.
- **Lead fields:** contact, address, sq ft, stories, current system age/size, fuel, tier, timeline, financing interest yes/no.
- **Effort:** M.
- **Confidence: 6/10.** Replacement buyers are high-value, but the sizing and financing evidence is thin (3 and 1 reviews), and sizing advice carries liability, so it must stay indicative.

## 5. Caveats

- Plumbing contamination: ~half of the Barbosa and Harlen Johnson negatives are plumbing jobs, so HVAC-only counts for pains #1 and #2 are probably ~12–14 each.
- Concentration: Airtron (20), Barbosa (19), Harlen Johnson (20) and Mondragon (19) together make up ~66% of the negatives. The themes may reflect a few bad actors more than the niche.
- Reviews are truncated at ~500 characters. A few are in Spanish (2 are usable).
- This is customer voice, not owner voice. Owners who earn on replacements may dislike a tool that can recommend repair.
- Financing evidence is a single review. Any monthly-payment display must be optional and owner-supplied, not promised.
