# VOC — 13 niches (2026-11-03)

## Source and method

- **Source:** 5,461 Google Maps reviews.
  - 2 metros per niche × 15 businesses × up to 20 reviews.
  - One metro sorted lowest-rated first, the other most-relevant first.
  - Apify cost: about $5 total.
- **Analysis:** every 1–3★ review plus 80 random 4–5★ reviews per niche, coded by hand.
  - Counts are approximate.
  - Quotes are exact, and were checked against the source.
- **Limit:** this is the *end-customer* voice (the prospect's customers), not the owner's voice.
  - Reddit and forums are blocked from this environment.

## Data-quality flags (read before trusting a niche)

| Niche | Clean? | Note |
|---|---|---|
| Tree | ✅ cleanest | |
| Roofing | ✅ | Heavy San Antonio hail-market weighting |
| HVAC | ✅ | Four firms make up about ⅔ of the negatives; some reviews are plumbing jobs |
| Pool | ⚠️ | About ¼ of the sample is suppliers or builders |
| Pest | ⚠️ | 14 of 61 negatives are a hardware store |
| Deck | ⚠️ | About 30 of 50 negatives are deck-specific; one firm has 10 |
| Fence | ⚠️ | 17 negatives are one commercial gate firm |
| Mortgage broker | ⚠️ | 20 of 22 negatives are one lender |
| Loan officer | ⚠️ | Post-close complaints are mostly about big servicers |
| Wealth | ❌ thin | 12 negatives |
| Advisor | ❌ thin | 9 negatives; 4 are cold-call complaints from non-clients |
| Hardscape | ❌ polluted | 9 of 22 negatives are a supply yard. **Re-scrape** |
| Business lender | ❌ polluted | Only about 25 of 104 reviews are about business lending. **Re-scrape** with "SBA lender" / "equipment financing" |

## Proposed tools (3 per niche; confidence /10)

| Niche | Tool 1 | Tool 2 | Tool 3 |
|---|---|---|---|
| Pool | New Pool Budget & Timeline Estimator (8) | Remodel/Resurface Quote Builder (6) | Problem Triage + Repair Quote (5) |
| Pest | Pest Quote Estimator — one-time vs plan (7) | "How Bad Is It?" Severity Checker (7) | Termite/Wildlife Inspection Request (5) |
| Deck | Deck Cost Estimator (8) | Repair/Resurface/Replace Checker (6) | Wood vs Composite 10-yr Cost (5) |
| HVAC | **Repair-or-Replace Calculator (8)** | No-Cool/No-Heat Emergency Triage (7) | New System Price & Sizing Estimator (6) |
| Roofing | Roof Replacement Cost Estimator (8) | Storm Damage & Claim Readiness Checker (7) | Leak Triage + Repair-or-Replace (7) |
| Hardscape | Patio & Paver Cost Estimator (6) | Patio Repair-or-Replace Checker (5) | Backyard Goals Planner (5) |
| Tree | Tree Job Price Estimator + written scope (7) | "Is My Tree a Risk?" Urgency Checker (7) | Storm Damage Fast Request (6) |
| Fence | Fence Cost Estimator, itemized (8) | Storm Damage Repair-or-Replace (6) | Neighbor Cost-Split Estimator (4) |
| Mortgage broker | Refinance Break-Even Estimator (7) | "My Situation" Loan Path Finder (7) | Payment & Cash-to-Close Estimator (6) |
| Loan officer | Mortgage Readiness Check + doc checklist (8) | All-In Monthly Payment Estimator (7) | Points vs Rate / Refi Break-Even (5) |
| Wealth | Retirement On-Track Estimator (7) | Financial Blind-Spot Checklist (7) | Advisory Fee Impact Calculator (5) |
| Business lender | Business Funding Fit Finder (7) | Funding Document Checklist (6) | True Cost of Financing Estimator (5) |
| Advisor | Retirement Readiness Snapshot (7, same build as Wealth) | Fee & Product Cost Check (6) | Planning Priorities Matcher (6) |

## Patterns across niches

1. **The #1 pain in almost every home-service niche is "I couldn't get a quote / they never called back."**
   - Seen in: pool, deck, tree, fence, roofing, pest.
   - An instant estimator answers that directly. It is also proof for our own pitch that their leads go cold.
2. **Price fear:** customers fear getting gouged, or a quote that rises after the deposit.
   - Tools should show a price range *before* asking for contact details.
   - A fence reviewer punished a company that demanded personal information first.
3. **Financing is a weak signal everywhere** (0–4 reviews per niche).
   - Do not lead with monthly payments.
   - This matches the CLAUDE.md rule: no monthly-payment promise.
4. **Finance tools must be estimates only.**
   - No promised rates, approval or returns.
   - Consent captured on submit.

Per-niche detail, with verbatim quotes, is in `VOC_<niche>.md`.
