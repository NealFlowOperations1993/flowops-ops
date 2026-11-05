# VOC — Loan Officer (scraped as "mortgage lender")

Source: `sample_loan_officer.txt`, 517 reviews in total. The sample holds all 23 reviews at 1–3★ and 80 random reviews at 4–5★ (of 494).
Counts are approximate hand-tallies. One review can count toward more than one theme.

---

## 1. Top pains (1–3★, n=23)

| # | Theme | ~Count | Verbatim |
|---|---|---|---|
| 1 | **Post-close servicing / escrow problems** (payment jumps, escrow shortages, loan sold, misapplied funds). Nearly all are about servicers (Newrez, Caliber), not the originating LO. | ~12 (escrow specifically ~6) | "My mortgage payment went up by $62 due to an escrow shortage…" / "Sold our mortgage; failed to properly notify, late payment resulted after never missing a payment for years." |
| 2 | **Unreachable / ghosted / no callback** | ~7 | "it's been 3wks and I have yet to receive a call" / "had 2 closing dates haven't heard from anyone in over a month, no response calls ort text messages" |
| 3 | **Qualification uncertainty: pre-approval that didn't hold, or "can I even qualify?"** (DACA, credit not ready, file stalled) | ~5 | "Pre-approval letter is meritless. They wait until last minute right before closing to actually see if a candidate is qualified." / "I was told several times that “we are so close” only to receive another request for documents…" |
| 4 | **Treated as not worth the time** (rude, condescending, dropped when not ready) | ~4 | "He was rude and made it seem like we were wasting his time." / "I asked for improvement tips and even for a referral… I haven't heard anything back since I'm not worthy of a commission check." |
| 5 | **Endless document requests and closing delays** | ~4 (+1 at 4★: "closing was delay 2 weeks late") | "after 10 weeks of emails and document submittals, I had to cut bait." / "they needed updated statements, ghosted agin…" |
| 6 | **Can't reach a human by phone** | ~3 | "You will NOT be able to reach a representative to talk to on the phone." / "When you call there is no one to answer your call." |

**Read:** Theme 1 is the biggest by volume, but an independent LO's tool can't fix servicing. Themes 2–5 (uncertainty, readiness and document friction before closing) are where an LO can act.

---

## 2. What wins (4–5★, n=80)

| # | Theme | ~Count | Verbatim |
|---|---|---|---|
| 1 | **Proactive communication / scheduled updates** | ~30 | "they provided weekly updates so that everything is transparent and you're not worried what's the current status of your file" / "I get an update every Tuesday, without fail" |
| 2 | **Hand-holding for first-time buyers** | ~18 | "As a first-time home buyer, I was absolutely PETRIFIED." / "We really couldn't have done it without his helpful step by step guidance." |
| 3 | **Solved a hard or "less-than-perfect" file** (self-employed, existing property debt, credit, unique income) | ~11 | "I had a difficult case as a self employed, but he always came back with a solution" / "someone who wasn't afraid to work with a less-than-perfect situation." |
| 4 | **Fast close / won the offer** | ~8 | "We went from being pre-approved to signing our paperwork in less than 3 weeks" / "Ted was able to offer the expedited closing that we needed to seal the deal on our home." |
| 5 | **Showed the numbers and options** (rate vs points, buydown, credit steps) | ~7 | "showed me how to calculate when it is feasible to buydown a loan, provided example pricing, and shared actionable steps for increasing my credit score." / "I can pay a little higher closing costs for a lower rate" |
| 6 | **Patience: no question too small** | ~8 | "she never made me feel like I was bothering her." / "No question was too small" |

---

## 3. Decision-moment questions clients clearly had

| Question | Evidence |
|---|---|
| **"Can I qualify given my situation?"** (self-employed, DACA, credit, already own property, VA) | Line 7 (DACA), 11 (credit "wasn't where I want to be yet"), 28 ("I wasn't qualifying for the new home the traditional way"), 44 (self-employed), 97 (VA), 32 ("clients who think it might be hard to get approved") |
| **"Will my pre-approval actually hold?"** | Line 8 ("Pre-approval letter is meritless"), 24 ("we are so close") |
| **"What documents will you need from me?"** | Line 49 ("surprised at the amount of documentation needed"), 45 ("the many many many documents needed to qualify"), 21, 24 |
| **"How fast can we close?"** (and can I make a competitive offer) | Lines 35, 51, 53, 69, 79, 98 ("10 day Fast as Cash close was what got our offer accepted") |
| **"What will my real monthly payment be, and will it change?"** | Line 35 ("the mortgage payment was lower than expected"), 14 and 23 (escrow-driven increases) |
| **"Should I pay points / buy down, or is refinancing worth it?"** | Lines 29, 67, 39 ("we could lower our rate at no cost") |
| **"How do I improve my credit to get there?"** | Lines 11, 29, 48 ("advice on how to manage our credit") |
| **"Who do I call, and will they answer?"** | Lines 6, 9, 13; mirrored in wins theme 1 |

---

## 4. Proposed tools

### Tool 1 — Mortgage Readiness Check (with personalized document checklist)
- **Client gets in about 30 seconds:** They answer about 7 taps (goal: buy or refi; income type: W-2, self-employed or 1099; credit band; down-payment saved; monthly debts; timeline; special situation: VA, own other property, non-citizen, etc.). They get a readiness band ("Ready to talk / Close / Building"), the document list for their income type, and 3 questions to bring to the LO. Wording is "general guidance, not an approval".
- **Answers:** Pain 3 ("Pre-approval letter is meritless…"), Pain 4 ("I'm not worthy of a commission check" — the "Building" band gives next steps instead of a dead end), Pain 5 ("another request for documents"), and Wins 2 and 3 ("difficult case as a self employed").
- **Lead fields:** name, phone, email, goal (purchase/refi), target price or loan band, income type, credit band, down-payment band, debts band, timeline, first-time buyer Y/N, VA Y/N, special situation, readiness band.
- **Effort:** M (branching logic plus per-income-type checklists)
- **Confidence: 8/10.** "Can I qualify?" is the most frequent pre-decision question across negatives and positives. The lead it captures is pre-qualified and segmented by timeline.

### Tool 2 — All-In Monthly Payment Estimator (PITI + PMI + escrow note)
- **Client gets in about 30 seconds:** They enter price, down payment, ZIP or state, and credit band. They get an estimated range for principal & interest, taxes, insurance and mortgage insurance, plus a plain note that escrow can rise when taxes or insurance rise. Rate inputs are shown as illustrative assumptions, never quoted rates.
- **Answers:** Pain 1 ("payment went up by $62 due to an escrow shortage", "increased by approximately $115 per month"), and the decision question "what will my real payment be" (line 35, "lower than expected").
- **Lead fields:** name, contact, price range, down-payment amount, location, credit band, purchase timeline, first-time buyer Y/N.
- **Effort:** S
- **Confidence: 7/10.** The need is clear, but payment calculators are common, so the escrow and all-in framing is the differentiator.

### Tool 3 — Points vs. Rate / Refi Break-Even Estimator
- **Client gets in about 30 seconds:** They enter loan balance, current rate (or an illustrative new rate), the cost of points or closing, and how long they plan to stay. They see the estimated months to break even and the total over their horizon. Illustrative only, with no rate offered.
- **Answers:** Wins 5 ("how to calculate when it is feasible to buydown a loan", "higher closing costs for a lower rate"), line 39 ("lower our rate at no cost").
- **Lead fields:** name, contact, current balance, current rate, home value band, years planning to stay, purpose (rate / cash-out / term), credit band.
- **Effort:** S
- **Confidence: 5/10.** The evidence comes only from about 3 positive reviews. Refi demand depends on the rate environment, but these are high-intent existing homeowners.

---

## 5. Caveats
- **The negative sample is small (23).** The largest negative theme (servicing/escrow, ~12) is mostly about **servicers like Newrez and Caliber**, not independent LOs. It has 8+ reviews against a single Newrez listing. Don't build a "servicing" tool for LOs on this evidence.
- **These are client reviews, not owner voice.** They tell us what borrowers want, not what LOs will pay for or put on their site.
- **Big-firm mix:** many listings are branches or teams of large lenders (CrossCountry, Chase, Rate, Movement, Newrez). One team (Johnson Team, CrossCountry) accounts for about 15 of the 80 positives, which inflates the "weekly updates" theme.
- One 5★ (line 82, Chase) is about an ATM and was ignored.
- The positive sample is 80 random reviews of 494, so counts are directional only.
