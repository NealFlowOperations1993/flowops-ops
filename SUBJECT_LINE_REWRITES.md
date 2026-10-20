# Subject Line Rewrites — Spintax-ready

For each paused/active campaign, 5 new subject variants with spintax syntax that Smartlead accepts directly.

Format: `{{variant1|variant2|variant3|variant4|variant5}}` — Smartlead rotates per send.

## Voice rules in effect

- All lowercase or sentence case, never Title Case
- No emojis, no em-dashes
- 2-7 words ideal
- Concrete > abstract
- Curiosity gap > offer pitch
- Reference the prospect's city or role when it's a natural fit
- Never lead with "[Niche] in [City]" pattern again — that's what killed FINANCIAL

---

## FINANCIAL (currently 9.8% open — needs hard reset)

**Current dead subject:** `financial advisors in Chicago - quick offer`

**Diagnosis:** Reads like a mailing list header. No curiosity, no specificity to recipient. "Quick offer" telegraphs "this is an ad."

**New rotation (paste into Smartlead Email 1 subject field):**

```
{{quick question about your zip code|the 7 advisors stealing your clicks|saw your firm on google. one thing.|3 things your competitors are doing in {{city}}|your firm doesn't show up first}}
```

Why these work:
- "quick question about your zip code" — sounds 1:1, conversational
- "the 7 advisors stealing your clicks" — specific number, threat framing
- "saw your firm on google. one thing." — implies they reviewed something specific
- "3 things your competitors are doing in {{city}}" — competitive pressure + locality
- "your firm doesn't show up first" — bald statement, hard to ignore

---

## MORTGAGE (currently 11.5% bounce — need list fix first, but subject also weak)

**Current subject:** `mortgage brokers in Kingwood - quick offer`

**New rotation:**

```
{{50 borrowers in your dead lead pile|your old leads are saving $400/mo somewhere else|3 minute look at your CRM|the borrowers you stopped calling|rates dropped. your old leads didn't.}}
```

---

## MCA (working: 34% open, but can lift more)

**Current subject:** `mca brokers in Fort Lauderdale - quick offer`

**New rotation:**

```
{{75 merchants who just funded once|first position renewals in {{city}}|your best merchant is already on your list|the 4x rule for funded merchants|merchants funded 30 days ago, zero stacks}}
```

---

## WEALTH (best converter at 2.22% reply — don't break it)

**Current subject pattern (working):** `wealth managers in Cockrell Hill - quick offer`

**New rotation (light evolution, not revolution):**

```
{{25 liquidity events in your radius|who just got rich in {{city}}|the 90 day window most advisors miss|saw 3 exits near you. names attached.|fresh capital in your zip code}}
```

---

## COMMLOAN

**Current subject:** unknown / generic

**New rotation:**

```
{{100 SBA-ready owners in {{city}}|7 point SBA screen, done|the businesses too big to bank|your SBA pipeline next monday|owners ready for a 7(a). pre-screened.}}
```

---

## INSURANCE (FUNDING in old map)

**New rotation:**

```
{{50 bankable owners in {{city}}|the 8 signals lenders miss|your next 50 underwriting wins|owners that look fundable on every public signal|filtered to clean books and 3 years of revenue}}
```

---

## AGENCY (when relaunched)

**New rotation:**

```
{{4 of your clients are about to fire you|the churn signals you can't see|3 clients showing red flags|the agencies their clients are talking to now|client retention math for {{city}} agencies}}
```

---

## MEDSPA (COACH_FIT slot was wrong niche tag — keep separate)

**New rotation:**

```
{{30-60% of bookings die in 48 hours|the no-show window most med spas miss|your booking page is leaking. probably.|why prequal text isn't enough|reactivation script for {{city}} med spas}}
```

---

## PI_LAW

**New rotation:**

```
{{90 day injury map for {{city}}|where the accidents are happening|the OSHA citation list nobody pulls|3 ad gaps in {{city}} PI marketing|competitor ad spend across {{city}} PI firms}}
```

---

## TAX_RES (when launched)

**New rotation:**

```
{{your IRS notice list, 30 days fresh|state tax lien filings in {{city}}|owners 60 days from levy|tax notices nobody filters|the 3 signs a tax case will close fast}}
```

---

## IT_MSP (when launched)

**New rotation:**

```
{{your 5 biggest competitors and what they price|3 MSPs in {{city}} just won a contract|the AV stack most MSPs miss|the 90 day MSP win/loss board for {{city}}|companies that lost their MSP last week}}
```

---

## How to deploy these in Smartlead

1. Open each campaign
2. Sequence → Email 1 → Subject field
3. Paste the spintax string verbatim (including the `{{` and `}}`)
4. Save sequence — Smartlead's UI will show "spintax detected" and validate
5. Run a single test send to a flowoperations.org inbox to confirm rotation works

## When to swap subjects

Per Smartlead best practice, swap subject rotations every 2-3 weeks while a campaign is active. Inboxes get tired of the same patterns. The 5 variants above give you ~10-15 days of fresh rotation; after that, write new ones based on what's working.

## Tracking

Smartlead's analytics will show open rate per subject variant after ~50 sends per variant. Kill the bottom 2, write 2 new ones, rotate.
