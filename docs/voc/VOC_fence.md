# VOC: Fence

Source: `sample_fence.txt`. There are 495 reviews in total. The sample holds all 77 reviews at 1–3★ and a random 80 of the 418 at 4–5★. I read every line.

**Noise in the negatives.** 17 of the 77 are one commercial **gate, security camera and access-control** firm (Compound Security Specialists): HOA, storage-facility and office work. About 6 are complaints about company trucks being driven badly. About 7 are off-niche: lawn care, a handyman, a mulch job, and fence-supply ordering. That leaves roughly **45–50 negatives about residential fences**. Where it matters, counts below exclude the off-niche reviews.

## 1. Top pains (1–3★, n=77; ~47 residential-fence relevant)

| # | Theme | ~Count | Verbatim |
|---|---|---|---|
| 1 | **Can't even get an estimate: forms ignored, calls unreturned, estimate no-shows** | ~13 (+2 rude-phone) | "I went on their website to request a quote and I never got a response. I even called and got no response." · "Text said someone was coming for bid between 8 and 12. Nobody came or called." |
| 2 | **Silence and delays after signing or paying a deposit** | ~15 (≈6 are Compound) | "I paid my 50% deposit and was told I would have my new fence installed within 4 weeks. … Four weeks later, no new fence and no word" · "During the install, the company could not even be bothered to return our calls." |
| 3 | **Workmanship and durability: posts, leaning, sagging gates, warping, stain fading** | ~14 | "Not a single set is on 6 foot centers. That's why the pickets won't fit." · "Reduced to three stars due to having to adjust the gate weekly to get it to close." |
| 4 | **Price changes after quoting, and unclear inclusions (stain, haul-off, dumpster)** | ~10 | "they said they had misquoted me and wanted to add $600 to the project because the salesman never came out to measure." · "the quote stated the cost but it was never explained it was a separate task." |
| 5 | **Neighbor and shared-fence friction, damage to the neighbor's side** | ~5 | "My neighbor checked the wrong box so they didn't finish my side of the fence" · "What about the guy on the other side of the fence?" |
| 6 | **Code and permit problems** | 1 (weak) | "installed a fence in our neighbors yard that is not to code." |

Other notes:
- Pain 4 includes stain specifically, 3 times: "Patriot said they made a mistake and doubled their stain quote", the stain being a separate task, and stain that faded.
- One review is directly relevant to lead-form design: "They refused to give me an estimate unless I disclosed all my personal information."

## 2. What wins (4–5★, n=80)

| # | Theme | ~Count | Verbatim |
|---|---|---|---|
| 1 | **Responsive and kept us updated** | ~23 | "They were responsive to phone calls and texts throughout the process and kept us updated on scheduling and the installation process." · "preparing the initial estimate within 24 hours" |
| 2 | **Best price after comparing bids** | ~20 (≥7 explicitly compared bids) | "I got three bids from him and two other reputable fence companies in Austin and neither of the other two could touch K2Fence in pricing." · "We got a few quotes and they were by far the best pricing around." |
| 3 | **Speed from quote to install, often 1–3 days on site** | ~14 | "They stopped by on a Thursday for a quote and the fence was installed the following Monday." · "Upon approval, fence was built/stained in just 2 days!!" |
| 4 | **Options and design within budget** | ~8 | "came up with a creative plan that helped us stay within our budget" · "gave a couple different options" |
| 5 | **Storm repair, same or next day** | ~7 | "After the storm Family Fences had a crew out the same day to fix our fence." · "Had part of our fence blow down. Chris responded promptly and had a crew out the next morning." |
| 6 | **Pets (and pool) are the reason for the fence** | ~7 | "I have a new dog that I need to protect and he worked hard to adjust the gate gap to ensure her future safety." · "…so our dog would have his yard back for the weekend" |

## 3. Buying-moment questions

- **"What should my fence cost?"** One customer did the maths themselves: "I had already figured out the cost of materials (pickets, rails, & hardware) for the exact dimensions of my fence in order to compare material costs with th…". At least 7 compared bids. Others: "Way over price had job done for half the price", "He quoted me $800 to do that."
- **"What's included: stain, removal of the old fence, dumpster, gates?"** Evidence: "We were told a dumpster was included with the job", "threw in several extras for free including hauling away my old fence", and the stain-as-separate-task complaint.
- **"Will the online or phone number hold after they measure?"** Evidence: the "+$600 … salesman never came out to measure" complaint. In a positive review, "After the correct measurements and details were confirmed, he adjusted…".
- **"Which material or build will last?"** Evidence: "The chain link fence lasted less than a year", "wood that warps", "the steel posts make it solid!", "I wasn’t given an option to have 3 rails instead of 2."
- **"How soon can it go in?"** Evidence: Pain 2 and Win 3.
- **"How do my neighbor and I split this?"** Evidence: "I was planning a fence project with my neighbor…", the paying-half story, "They allowed us time to coordinate with our neighbors".
- **"Repair or replace after storm damage?"** Evidence: about 7 reviews: windstorm, blow-down, "fence repair after a storm".
- **"Will it keep my dog in, and is the pool gate right?"** Evidence: gate gap for a dog, "the one weird corner of my fence my dog likes to bust through", "The security gate to the pool was smashed".
- **"HOA and permit?"** Evidence: "helped us handle the HOA and permit process" and the not-to-code complaint. This is thin.

## 4. Proposed tools

### Tool 1: Fence Cost Estimator (itemized)
- **What the end customer gets in about 30 seconds:** They enter linear feet (or tap a rough perimeter on a map), material (wood privacy, cedar, vinyl, aluminum/ornamental, chain link, ranch rail), height, number and width of gates, and extras (remove old fence, stain/seal, post upgrade such as steel posts, slope). They get a price range with an **itemized "included / optional" list** (removal, haul-off, stain) and a note that final price is confirmed on site.
- **VOC it answers:** The top buying question (cost, comparing bids). Pain 4: surprise add-ons, stain separate, dumpster, "+$600" after measuring. Win 2 is about price, and Win 4 about options within budget. Ask for contact details only *after* showing the range, because of the "refused to give me an estimate unless I disclosed all my personal information" complaint.
- **Lead fields:** linear feet, material, height, gates, removal (Y/N), stain (Y/N), pets/pool flag, HOA (Y/N), timeline, address, photos, contact.
- **Build effort:** M.
- **Confidence: 8/10.** Price comparison is the most explicit buyer behavior in the set. The itemized output directly addresses the price-change complaints.

### Tool 2: Storm Damage Fence Check (repair or replace)
- **What the end customer gets in about 30 seconds:** They say what is damaged (sections down, leaning posts, broken pickets, gate won't close or latch, pool gate damaged) and give the fence age and material. They get a "likely repair vs. likely replace" read with a rough range, a "secure your pets / pool now" note, and a priority request.
- **VOC it answers:** Win 5 (same/next-day storm response is praised), the pool-gate urgency ("needed to be replaced as soon as possible"), and the gate problems in Pain 3. It also gives existing-fence owners a way in, compare "we dont have enough people to work on a fence we didnt install."
- **Lead fields:** damage type, approximate feet affected, gate/pool flag, pet containment urgency, photos, fence age and material, insurance (Y/N), address, contact.
- **Build effort:** S.
- **Confidence: 6/10.** The intent is high, but it is event-driven and seasonal. About 7 positive mentions, no negative-side evidence.

### Tool 3: Neighbor Fence Cost-Split Estimator
- **What the end customer gets in about 30 seconds:** They enter the shared length, material and height, and how the cost will be split (50/50, by footage, one side pays for upgrades). They get each household's estimated share and a shareable summary link for the neighbor. Both households can be captured.
- **VOC it answers:** Pain 5 ("My neighbor checked the wrong box…", "I reached out to them to understand the quote and then the price ended up being higher"). One project was cancelled when the neighbor backed out after a price change ("My neighbor cancelled the project"). Also "allowed us time to coordinate with our neighbors".
- **Lead fields:** both households' contacts (consent from each), shared footage, material, split method, who is the decision-maker, timeline, address.
- **Build effort:** M (share link and two contacts).
- **Confidence: 4/10.** Distinctive and can capture two leads, but only about 4–5 reviews support it. A pet-containment option inside Tool 1 may beat it (about 7 pet mentions).

## 5. Caveats
- 22% of negatives (17 of 77) are a commercial gate/security integrator, and about 13 more are driving or off-niche. The residential-fence negative base is about 47.
- Several businesses do both fences and decks or roofing (Patriot, JB, SHLY, Balch), so some positives describe roofing, pergola or landscaping work.
- These are end-customer reviews, not owner voice. Owners may resist a public price range; give them a "range only, confirmed on site" setting.
- Neighbor-split and HOA/permit themes are thin. Counts are approximate hand-tags, and one review can carry several themes.
