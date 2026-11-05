# VOC — Financial Advisors

Source: `sample_advisor.txt`, 266 reviews in total. The sample holds all 9 reviews at 1–3★ and 80 random reviews at 4–5★ (of 257).
Counts are approximate hand-tallies. One review can count toward more than one theme.

> **Evidence warning: only 9 negative reviews.** Every pain theme is 1–3 reviews. These are anecdotes, not patterns. The positive side (80) carries the real signal.

---

## 1. Top pains (1–3★, n=9)

| # | Theme | ~Count | Verbatim |
|---|---|---|---|
| 1 | **Unwanted calls / won't honor do-not-call** | ~2 (+1 5★ claiming impersonation scammers, line 43) | "STOP CALLING ME!!!" / "Countless times I've tried to tell them to place me on their DO NOT CALL LIST but they continue to call non stop almost every single day." |
| 2 | **No callback / can't reach the advisor** | ~2 | "I called a few times left messages. No response." / "lack of ability to pick up a phone and call client" |
| 3 | **Scope mismatch / cookie-cutter service** (couldn't help with the actual question; couldn't track against the plan) | ~2 | "He should have told me upfront that he couldn't provide these services (and that I should go see a CPA)." / "Mercer takes a cookie cutter approach to its clients." |
| 4 | **Seminar / dinner-event bait mishandled** | ~2 | "The DAY OF I received text and email which stated the event was full…" / "Received an invite called Exclusive Invitation with topic: How to protect yourself from a tax storm." |
| 5 | **Hidden fees and pressure selling of insurance** | ~1 (echoed by 5★ line 71) | "He is deceptive about his fees and was charging significantly more than what he told me…" / (5★) "these products carried large fees." |

---

## 2. What wins (4–5★, n=80)

| # | Theme | ~Count | Verbatim |
|---|---|---|---|
| 1 | **Explains, educates, never makes you feel foolish** | ~18 | "all without ever making you feel foolish for not knowing" / "he patiently explains the logic behind his recommendations so we learn as part of the process." |
| 2 | **Retirement confidence / "on track"** | ~15 | "I am very confident we are on track to meet our financial and estate goals" / "helping us create a budget and figure out when retirement may (hopefully!) be in our near future." |
| 3 | **Responsive and reachable** | ~13 | "Never had problems getting hold of my advisers and team when needed" / "He’s responsive and always easy to get ahold of." |
| 4 | **Holistic: insurance, estate, college, debt, 401k rollovers** | ~10 | "They have helped me: create my emergency fund, investments, IRAs, life insurance AND my children's investments." / "Whether guiding us in the best way to pay college tuitions for our 4 children or preparing us for retirement…" |
| 5 | **Listens to my goals and personalizes** | ~9 | "she asks questions about my goals and really listens to my answers." / "never try to put you in a box based on your savings targets" |
| 6 | **Transparent, fair fees / trust** | ~6 | "Their flat fee rate is transparent and makes sense to me" / "Professional and cost effective portfolio management." |

---

## 3. Decision-moment questions clients clearly had

| Question | Evidence |
|---|---|
| **"Am I on track for retirement? When can I retire?"** | Lines 22, 28 (corporate buyout: "how to secure our financial position to live comfortably into our senior years"), 32, 60, 75, 85 |
| **"What am I actually paying, and is it worth it?"** | Lines 10 (deceptive fees), 71 ("questionable funds and annuities… carried large fees"), 75, 53 |
| **"Can this advisor help with MY specific issue?"** (company stock, tracking vs plan) | Lines 6, 8 |
| **"I don't know where to start."** | Lines 32 ("completely clueless"), 69 ("doesn't know how to start"), 76 (Ramsey Baby Step 4 → looking for an advisor) |
| **"Am I protected?" (life / disability / LTC insurance, estate)** | Lines 15 (LTC), 45, 55, 63, 72, 83 |
| **"What to do with old 401ks / employer plan?"** | Lines 68 ("transitioned several 401k accounts"), 72 |
| **"Will they call me back?"** | Pain 2; Win 3 |

---

## 4. Proposed tools

### Tool 1 — Retirement Readiness Snapshot
- **Client gets in about 30 seconds:** They enter age, target retirement age, savings band, monthly contribution, and desired monthly retirement income. They get an **illustrative** readiness range under conservative, middle and optimistic assumptions they can see, a "possible gap" figure, and 3 questions to discuss with an advisor. Educational only; no return promised and no allocation advice.
- **Answers:** Win 2 ("confident we are on track", "figure out when retirement may (hopefully!) be"), and decision-question lines 22, 28, 60.
- **Lead fields:** name, email, phone, age, target retirement age, savings band, contribution, spouse Y/N, pension Y/N, # employer plans, top worry.
- **Effort:** M
- **Confidence: 7/10.** It's the dominant future-oriented question in 15+ positives and segments leads by assets. It duplicates the wealth tool, so FlowOps can build it once and use it in both niches.

### Tool 2 — "What Am I Paying?" Fee & Product Cost Check
- **Client gets in about 30 seconds:** They choose what they hold (AUM account, annuity, mutual funds, whole life) and enter balance and the fee if known. They get an estimated annual dollar cost, an estimated cumulative cost over 20 years under an illustrative assumption, and a checklist of fee questions to ask ("surrender charges? 12b-1? advisory %?"). No verdict on any product.
- **Answers:** Pain 5 ("deceptive about his fees", and 5★ line 71's "these products carried large fees"), Win 6 ("flat fee rate is transparent").
- **Lead fields:** name, contact, assets band, product types held, current advisor type, known fee, age, reason for review.
- **Effort:** S–M
- **Confidence: 6/10.** It strongly matches what fee-only/flat-fee advisors sell against. The direct negative evidence is only 1–2 reviews, and commission-based advisors won't want it.

### Tool 3 — Planning Priorities Matcher ("Where should I start?")
- **Client gets in about 30 seconds:** They pick their top priorities (retirement, company stock, college, insurance, debt, estate, old 401ks), life stage and a household snapshot. They get a ranked "start here" list with a plain-English explanation, plus a note on **what this firm does and doesn't cover**, so a scope mismatch surfaces before the meeting.
- **Answers:** Pain 3 ("should have told me upfront that he couldn't provide these services"), decision question "I don't know where to start" (lines 32, 69), and Win 4 (holistic) and Win 5 (listening to goals).
- **Lead fields:** name, contact, priorities ranked, life stage, household, assets band, upcoming life event, preferred meeting type.
- **Effort:** S
- **Confidence: 6/10.** It is well supported by the positives (education plus holistic, about 28 combined). The value to the advisor is intake quality more than volume, and it's less "shareable" than a calculator.

---

## 5. Caveats
- **Extremely thin negative evidence: 9 reviews.** Four of the nine are about **prospecting** (calls, seminar invites) by people who were never clients. Only about 4 describe an actual service relationship. No pain theme here should drive a decision on its own.
- **These are client reviews, not owner voice.**
- **Big firm vs independent:** the sample includes Morgan Stanley, Mercer Advisors (national RIA) and Moneta. Mercer's "cookie cutter" complaint may not apply to independents. GWS&A alone supplies about 15 of the 80 positives, which inflates the "team/education" themes.
- The McAdam "tax storm" dinner-seminar reviews show seminar marketing is in use in this niche. That's useful context, but it's about marketing, not end-client needs.
- Heavy overlap with the wealth niche (`VOC_wealth.md`). The same retirement tool can serve both.
