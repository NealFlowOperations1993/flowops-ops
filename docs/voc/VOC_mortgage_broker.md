# VOC: Mortgage Broker

Source: `sample_mortgage_broker.txt`. There are 429 reviews in total. The sample holds all 22 reviews at 1–3★ and a random 80 of the 407 at 4–5★. I read every line.

**Concentration warning, read this first.** **20 of the 22 negative reviews are about one lender, Cake Mortgage.** The other two are Vault Mortgage Group and GoTo Mortgage Solutions. The pains below are therefore largely one company's failure modes. They match well-known industry complaints, but this sample does not prove they are widespread. At least 2 negatives (and about 8 positives) were written by real-estate agents, title companies or wholesale partners, not borrowers.

## 1. Top pains (1–3★, n=22)

| # | Theme | ~Count | Verbatim |
|---|---|---|---|
| 1 | **Ghosting and no updates during the loan** | ~8 | "they never return phone calls and If they do its weeks later" · "paid for the appraisal, appraisal came back and toatally ghosted by Sean since then." |
| 2 | **Bait rates and numbers that change; surprise cash at closing** | ~7 | "they mislead you by telling and presenting you with interest rates that will attract you" · "I was promised money back at closing. Instead there was a lot shady sneaky switching of money/credit to which they said I owed $1200 at close." |
| 3 | **Last-minute closing failures and delays (lost deals, lost earnest money)** | ~6 | "The day of closing they have NO MONEY!!!!" · "…pushed our transaction OUT OF CONTRACT, eventually leading to the loss of my earnest…" |
| 4 | **Qualification surprises: told late, or told nothing** | ~3 | "I was unable to qualify so they decided not to reach out and tell me" · "day before closing they tell me I don't score for the loan and I have to … pay an additional $95, 000" |
| 5 | **Refinance or product didn't deliver the benefit promised** | ~2 (weak) | "They told me a refinance would benefit us, but cost us way more on our loan and more for a monthly payment." · "I asked for a 24 year fixed Mortgage which I was assured I was receiving was not the case." |
| 6 | **Pressure and sales tactics** | ~2 (weak) | "tried to get her to change her mind by talking down the competing company" · "get everything in writing and record all phone calls and messages!" |

Pains 2 and 5 together (about 9 reviews) show one underlying fear: **"Will the numbers I'm shown be the numbers I get?"** Even a reviewer who later admitted a good deal framed it as a costs question: "I have a 2.875 rate for a 15 year and paid $1200 in fees. You can decide if this…".

## 2. What wins (4–5★, n=80)

| # | Theme | ~Count | Verbatim |
|---|---|---|---|
| 1 | **Reachable and proactive communication** | ~28 | "just to be able to pick up the phone and speak to someone after hours shows that they go above and beyond." · "provided updates without being asked" |
| 2 | **Got it done when others couldn't: complex or unusual scenarios** | ~15 | "after we thought we were not going to be able to purchase a home based on what all other lenders had told us but Arshia got it done!" · "Although I didn’t initially qualify, they didn’t turn me away — instead, they provided a clear, actionable plan to help me get on track" |
| 3 | **Best rate or lowest costs compared with other lenders** | ~16 | "The loan estimate that I received had the best rates and cheapest closing costs out of the other 3 lenders' quotes that I received." · "lock in a rate that was 2% (200 bps) below our original loan rate" |
| 4 | **Fast close, on time, no surprises** | ~12 | "Miami Mortgage Advisors got the whole deal done and approved in 7 days!" · "There were absolutely no surprises at settlement." |
| 5 | **Patient education, especially for first-time buyers (~8 first-timers)** | ~11 | "someone taking an extra time to walk you through documents, numbers, and overall process at each step goes a very long way!" · "I had many questions about rates and when we should buy" |

The complex scenarios in Win 2 include self-employed or business owners, new immigrants, foreign nationals, buyers living abroad, a filed foreclosure, VA refi, jumbo, reverse mortgage, HELOC, and investment property.

## 3. Buying-moment questions

- **"What will my rate and costs actually be, and will they change?"** Evidence: Pain 2; "the numbers had already changed"; "The rate was honored" (praised); "kept up to date on everything from my mortgage rate … to closing fees".
- **"Will a refinance actually save me money?"** Evidence: "cost us way more on our loan and more for a monthly payment", "Now we are stuck with 12,000 extra on our mortgage with no benefit." On the positive side, "lock in a rate that was 2% (200 bps) below our original loan rate". Refi, cash-out or HELOC appears in about 10 positives.
- **"Can someone with my situation even get a loan?"** Evidence: about 15 positives; "issues with other mortgage brokers because of our family's unique situation and being new immigrants"; "I am an entrepreneur running my own business…"; "Although I didn’t initially qualify…".
- **"How much cash do I need at closing?"** Evidence: "they said I owed $1200 at close"; "pay an additional $95, 000" the day before closing; "cheapest closing costs"; "no surprises at settlement".
- **"Will we close on time?"** Evidence: "delayed over 60 days on closing"; "after 6 weeks he couldn't get me closed and I was running out of time"; "approved in 7 days".
- **"What documents will I need?"** Evidence: "they suddenly claimed they needed additional documents, even though we had already submitted those exact documents"; "stressful pulling together all the paperwork".
- **"Is now the right time, and should I go ahead?"** Evidence: "when we should buy"; "encourage us to move forward in the home buying process despite our initial hesitations".

## 4. Proposed tools

All three tools must be framed as **estimates for illustration only, not offers, rate quotes or approvals**. Use user-entered or clearly labeled illustrative rates, no "you qualify" language, and the business's NMLS and equal-housing disclosures. Contact consent (TCPA) is captured on submit. The business's compliance contact should review the output copy before launch, because specific payment terms in advertising can trigger disclosure rules.

### Tool 1: Refinance Break-Even Estimator
- **What the end customer gets in about 30 seconds:** They enter their current balance, current rate, years left, an estimated home value, a goal (lower payment / shorten term / cash out) and a rate to compare. The comparison rate is user-entered, or an "illustrative" slider with no claim that it is available. They get an estimated monthly change, an estimated break-even in months on estimated closing costs, the change in total interest over the term, and a plain "this may not be worth it if…" line.
- **VOC it answers:** Pain 5 ("They told me a refinance would benefit us, but cost us way more…") and Pain 2 (numbers that change). Win 3 (rate/cost comparison) and the 200 bps refi story.
- **Lead fields:** loan balance, current rate and term, estimated home value, goal, cash-out amount, self-reported credit band, occupancy (primary / investment), timeline, contact plus consent.
- **Build effort:** S.
- **Confidence: 7/10.** A clear, honest "is it worth it" answer, backed by both the negative and the positive evidence. Rate-sensitive leads are high-intent.

### Tool 2: "My Situation" Loan Path Finder
- **What the end customer gets in about 30 seconds:** They tick what applies: self-employed or business owner, recent job change, new to the country or foreign national, living abroad, VA eligible, 62+, investment property, past credit event, need a fast close. They get the **loan program types commonly used** for that profile (for example bank-statement, VA, reverse/HECM, DSCR, jumbo, HELOC) and a **document checklist** to start gathering. It says "a broker can review your options", never "you qualify".
- **VOC it answers:** Win 2 (about 15 "others turned me down" stories; "provided a clear, actionable plan to help me get on track"). Pain 4 (late qualification surprises). The documents question ("pulling together all the paperwork", duplicate document requests).
- **Lead fields:** scenario flags, purpose (purchase / refi / HELOC / reverse), approximate price or loan amount, self-reported credit band, timeline, whether they have been declined elsewhere (Y/N), contact plus consent.
- **Build effort:** M (the program logic needs broker sign-off).
- **Confidence: 7/10.** This is the most distinctive positive theme and plays to a broker's strength over a bank. Keep it educational to avoid any approval implication.

### Tool 3: Purchase Payment & Cash-to-Close Estimator
- **What the end customer gets in about 30 seconds:** They enter purchase price, down payment, a rate (user-entered, or an illustrative range), estimated property tax and insurance, and HOA. They get an estimated monthly payment (principal and interest, tax, insurance, HOA) and an **estimated cash-to-close range** (down payment plus a typical closing-cost band), with "costs vary; get a Loan Estimate" framing.
- **VOC it answers:** The cash-at-closing surprises ("owed $1200 at close", "$95, 000" the day before), "no surprises at settlement" (praised), "cheapest closing costs" (praised), and first-time buyers' questions ("many questions about rates and when we should buy").
- **Lead fields:** price range, down payment, first-time buyer (Y/N), target area, pre-approval status, timeline to buy, self-reported credit band, contact plus consent.
- **Build effort:** S.
- **Confidence: 6/10.** Useful and high-volume, but generic. Bank and portal calculators already exist, so the lead may be less differentiated than with Tools 1–2.

## 5. Caveats
- **Very few negatives, and they are concentrated.** 22 negatives, of which 20 are Cake Mortgage. The pain ranking reflects one lender's problems. Treat Pains 4–6 (2–3 reviews each) as anecdotal.
- About 10 of 102 reviews are from industry partners (realtors, title, wholesale AE), not borrowers.
- These are end-customer reviews, not broker or owner voice. Brokers' appetite for public calculators, and their compliance teams' sign-off, is unknown.
- Mortgage tools carry regulatory risk. No tool should display a rate as available, imply approval, or promise a payment. All outputs are estimates.
- Several positive reviews are in Spanish (Great Florida Lending), which hints at a bilingual-tool opportunity in South Florida. That is one business only, so it is weak evidence.
