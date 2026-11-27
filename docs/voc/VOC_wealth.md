# VOC — Wealth Management Firms

Source: `sample_wealth.txt`, 209 reviews in total. The sample holds all 12 reviews at 1–3★ and 80 random reviews at 4–5★ (of 197).
Counts are approximate hand-tallies. One review can count toward more than one theme.

> **Evidence warning: only 12 negative reviews.** Every pain count below is 1–5 reviews. Treat pains as hypotheses, not findings. The positive side (80) is more reliable.

---

## 1. Top pains (1–3★, n=12)

| # | Theme | ~Count | Verbatim |
|---|---|---|---|
| 1 | **Paid fees, got no visible value or results** | ~5 | "Paid $5000 a year for nothing." / "I did not receive any tangible benefits for the fees paid." |
| 2 | **Aggressive or spammy prospecting** (cold calls, texts, purchased lists) | ~4 | "Sales guy spammed me three times in a single day from this firm, get a life." / "Predatory phone practices, avoid like the plague." |
| 3 | **Dropped or "fired" as a client, no accountability** | ~3 | "their response is to fire me as their client because I asked them to cover the cost of their admitted error!" / "when they decided our money needs didn’t work for them then severed the long relationship. What kind of fiduciary is that?" |
| 4 | **Bad or uncoordinated advice** (projections wrong, college vs retirement muddled) | ~3 | "You drew up a retirement projection after every call as though that 200,000 was in a retirement plan. . It was not" / "Me and my employees would have made a lot of money if they had properly advised us." |
| 5 | **Price changed / advisor unavailable** | ~1 | "jack up the price after initially offering low prices. Advisors are not available for months." |

---

## 2. What wins (4–5★, n=80)

| # | Theme | ~Count | Verbatim |
|---|---|---|---|
| 1 | **Responsive / available between meetings** | ~15 | "In between regular meetings, whenever I have financial questions, he is highly responsive…" / "He checks in often and has spent more time with me on my account in the past year than my “in person” planner had in 5." |
| 2 | **Explains clearly, educates, makes it less intimidating** | ~14 | "most people are not educated enough on this so they take the time to explain everything." / "made the world of finance (something I’ve always felt clueless about) so much easier to digest." |
| 3 | **Holistic plan** (tax, estate, insurance, 401k, college, benefits) | ~11 | "Whereas other financial resources I've worked with in the past have had really narrow scopes (just tax, or just investment)…" / "helped us gain a better insight into our finances, minimize taxes, estate planning, insurance needs, etc." |
| 4 | **Confidence and peace of mind; got past fear or procrastination** | ~10 | "Have you procrastinated building a longer term financial plan? I sure had." / "I went into the experience a little hesitant/nervous but his cadence and manner in the onboarding process… made it anxiety-free" |
| 5 | **Retirement planning / on track** | ~8 | "I requested a financial plan since i'm planning to retire in 5 years." / "helping me understand how my current savings trends would affect my retirement goals." |
| 6 | **Trust / fiduciary / fee-only** | ~9 | "It's really hard to find a fiduciary that has YOUR best interests (and not their lucrative commission) at heart." / "stands out for his fee-only approach" |

A smaller but sharp segment: **IPO and company-equity holders** (~6: lines 18, 24, 25, 55, 69, 80), e.g. "my employer IPO'ed and I earned more money than I knew what to do with."

---

## 3. Decision-moment questions clients clearly had

| Question | Evidence |
|---|---|
| **"Am I on track for retirement?" / "When can I retire?"** | Lines 31 ("planning to retire in 5 years"), 70, 89, 24 ("set me up for early retirement"), 63, 4 (projection error) |
| **"Am I getting value for the fee?" / "Is this advisor a fiduciary or a salesperson?"** | Lines 6, 13 ("Paid $5000 a year for nothing"), 9, 12; positive 54, 25, 30 |
| **"Is everything coordinated — taxes, estate, insurance, old 401ks?"** | Lines 14, 21, 31 ("several prior 401k packages; he was able to stitch them all together"), 51, 78, 88 |
| **"What do I do with concentrated stock / IPO money?"** | Lines 18, 24, 25 ("diversify my company stock"), 55 |
| **"Where do I even start?" (fear, procrastination)** | Lines 58, 61 ("fear of not knowing what to do"), 67, 79 ("If you're questioning your first steps") |
| **"College vs retirement — how do I balance both?"** | Lines 4 (FAFSA / 529), 14 ("College Savings") |
| **"Will they actually communicate?"** | Wins theme 1; pains 3 and 5 |

---

## 4. Proposed tools

### Tool 1 — Retirement On-Track Estimator
- **Client gets in about 30 seconds:** They enter age, target retirement age, current savings band, monthly contribution, and desired retirement spending. They get an **illustrative** projected range (low/mid/high assumption scenarios shown explicitly), a "gap or surplus" estimate in today's dollars, and a "number of accounts you hold" prompt (old 401ks). It carries a clear disclaimer: educational, not advice, no return promised.
- **Answers:** Win 5 ("how my current savings trends would affect my retirement goals"), the decision question "when can I retire" (line 31), and Pain 4 (a projection the client can see the inputs of, the opposite of "as though that 200,000 was in a retirement plan").
- **Lead fields:** name, email, phone, age, target retirement age, investable assets band, monthly savings, # of old 401k/IRA accounts, spouse Y/N, primary concern.
- **Effort:** M (scenario math plus clear assumption display)
- **Confidence: 7/10.** This is the most common forward-looking question in the positives and it captures asset band (lead quality). The negative evidence is thin.

### Tool 2 — Financial Blind-Spot Checklist
- **Client gets in about 30 seconds:** They answer 10 yes/no taps (will/trust in place? beneficiaries updated? old 401ks rolled? emergency fund? life/disability cover? equity comp plan? tax plan for this year? college plan?). They get a score and their top 3 gaps, explained in plain English. No product recommendations.
- **Answers:** Win 3 ("narrow scopes (just tax, or just investment)"), Win 4 ("Have you procrastinated…"), and the "is everything coordinated?" decision question (lines 14, 31, 78).
- **Lead fields:** name, contact, life stage, household (single/couple/kids), asset band, gaps flagged, equity comp Y/N, business owner Y/N, recent life event.
- **Effort:** S
- **Confidence: 7/10.** It maps to the strongest holistic and "where do I start" themes, and it is easy to keep compliant. The risk is that it feels generic unless it's branded to the firm's specialty.

### Tool 3 — Advisory Fee Impact Calculator
- **Client gets in about 30 seconds:** They enter portfolio size and current fee (percentage or flat), plus an illustrative return assumption they choose. They see the estimated cumulative dollars paid in fees over 10, 20 and 30 years, and a list of "what to ask any advisor about fees". No claim that any firm's net returns will be higher.
- **Answers:** Pain 1 ("Paid $5000 a year for nothing", "I did not receive any tangible benefits for the fees paid"), Pain 5 ("jack up the price"), Win 6 ("fee-only approach", "not their lucrative commission").
- **Lead fields:** name, contact, assets band, current fee, current advisor type (none / commission / AUM / robo), satisfaction 1–5, reason for looking.
- **Effort:** S
- **Confidence: 5/10.** It hits the sharpest pain, but the evidence is about 5 reviews. It only suits fee-only or flat-fee firms; AUM firms may decline it.

*Alternate (if the prospect serves tech/IPO clients): **Company-Stock Concentration Snapshot** shows the percentage of net worth in one stock, with an illustrative tax/diversification checklist. Evidence: about 6 positives. Effort M. Confidence 5.*

---

## 5. Caveats
- **Very thin negative evidence: 12 reviews,** 4 of them from a single firm (Savvy Wealth) and 2 from Hanke & Apolonio. Two of the four "spam" reviews are about prospecting, not clients' experience of service.
- **These are client reviews, not owner voice.** Nothing here says a wealth firm wants a calculator on its site or will act on its leads.
- **Off-niche contamination:** "Harness" reviews (lines 47, 71, 76, 90, 91, 92) are about **tax/CPA services and an apartment**, not wealth management, and were excluded from the themes. Several firms are robo/hybrid platforms (Savvy, Retirable), not local independents.
- The 5★ volume is dominated by a few firms (Financial Zen ~13, Drucker ~9, True Root ~9), so win themes partly reflect those firms' styles.
- Wealth and financial-advisor review themes overlap heavily (see `VOC_advisor.md`). Treat them as one buyer persona when choosing tools.
