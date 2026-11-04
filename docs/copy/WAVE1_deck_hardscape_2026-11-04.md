# Wave 1 cold email copy: Deck + Hardscape (Nov 4, 2026)

These are drafts. Neal approves or edits before anything sends.

**Stance.** Diagnose, say the uncomfortable thing, prescribe the call. One polarizing line per email. Truth only: no invented stats, no claims about the prospect we can't verify, no criticism of their business.

**Offer.** A free tool already built for their business, plus a 20-minute call.

**Merge fields:**
- `{{first_name}}`: set the fallback in Smartlead to "there".
- `{{company_name}}`
- `{{tool_url}}`: from the Tool Studio CSV import. Variant A goes to the estimator, variant B to the bid decoder.
- `[BOOKING_LINK]`: Neal to supply.

**Sign-off.** Must match the sending inbox's name.

**Footer on every email:**
```
[SENDER NAME]
FlowOperations
[POSTAL ADDRESS]
Not for you? Reply "stop" and I won't email again.
```

**Sequence:** Step 1 on day 0, step 2 on day 3 (same thread), step 3 on day 7 (same thread).

---

## DECK BUILDERS

### Variant A: Deck Cost Estimator (`deck-price-range`)

**VOC tie-in:**
- Top deck pains (~9 reviews each): "Estimate was over 15k higher than the other 2 I received" and "I never received a response" after the estimate visit.
- Top win: "Estimate was clear and reasonable compared with others."

**Step 1. Subject:** `price before the 7pm visit`

> Hey {{first_name}},
>
> Running a free estimate at 7pm for someone who's getting 3 quotes is the most expensive thing a deck builder does, and it never shows up on an invoice.
>
> So I built {{company_name}} a deck price estimator. Homeowners pick size, material and railing and see a real range before you ever drive out:
> {{tool_url}}
>
> It's yours, free. If you want to see how to put it to work, grab 20 min: [BOOKING_LINK]
>
> [SENDER NAME]

### Variant B: Deck Bid Decoder (`deck-bid-decoder`)

**VOC tie-in:**
- Pain: price shock against other bids, and price raised after the deposit.
- Win: "we appreciated the break out of all the costs involved so there were no surprises."

**Step 1. Subject:** `the cheaper bid`

> Hey {{first_name}},
>
> You know what the cheaper deck bid usually leaves out: footings, ledger flashing, the permit, tear-out. The homeowner doesn't.
>
> So I built {{company_name}} a bid decoder. A homeowner checks what each quote actually includes and sees why yours costs what it does:
> {{tool_url}}
>
> It's yours, free. If you want to see how to put it to work, grab 20 min: [BOOKING_LINK]
>
> [SENDER NAME]

### Steps 2 and 3 (deck, both variants)

**Step 2, day 3, same thread** (spine Q2, polarize on referrals):

> {{first_name}}, quick one: where are most of your jobs coming from right now, referrals, Angi, word of mouth?
>
> Asking because referrals are great until February. Then the phone goes quiet and the crew sits, and you can't turn referrals up.
>
> Your page is still live: {{tool_url}}

**Step 3, day 7, same thread** (take-away):

> Last one from me.
>
> Honestly, if you're booked out and happy at the size you are, this isn't for you and I'll leave it there.
>
> If you'd rather have homeowners show up already knowing the price, the page is yours: {{tool_url}}
> 20 min with me: [BOOKING_LINK]

---

## HARDSCAPING

### Variant A: Patio & Paver Estimator (`hardscape-patio-estimator`)

**VOC tie-in:**
- Top hardscape pain (~9): price surprises, and "not knowing the fair price."
- Wins: fair price (~13), and reliable and responsive (~30).

**Step 1. Subject:** `a number before the visit`

> Hey {{first_name}},
>
> Most homeowners asking about a patio want one thing first: a number. When they can't get one, they call the next guy on the list.
>
> So I built {{company_name}} a patio and paver estimator. They pick the project, material and size and see a real range before you drive out:
> {{tool_url}}
>
> It's yours, free. If you want to see how to put it to work, grab 20 min: [BOOKING_LINK]
>
> [SENDER NAME]

### Variant B: Hardscape Bid Decoder (`hardscape-bid-decoder`)

**VOC tie-in:**
- Pain: "I was floored to learn I had been paying two to three times the market rate", plus overcharging and hidden fees.
- Win: "Price was very reasonable."

**Step 1. Subject:** `what the cheap patio skips`

> Hey {{first_name}},
>
> Base depth, compaction, edge restraint and drainage are where a cheap patio cuts corners, and the homeowner can't see any of it until it sinks.
>
> So I built {{company_name}} a bid decoder. A homeowner checks what each quote actually includes and sees why yours costs what it does:
> {{tool_url}}
>
> It's yours, free. If you want to see how to put it to work, grab 20 min: [BOOKING_LINK]
>
> [SENDER NAME]

### Steps 2 and 3 (hardscape, both variants)

**Step 2, day 3, same thread** (spine Q2, polarize on slow season):

> {{first_name}}, quick one: where are most of your jobs coming from right now, referrals, Angi, word of mouth?
>
> Asking because slow months aren't weather. They're a pipeline you didn't fill in the fall, and it's November.
>
> Your page is still live: {{tool_url}}

**Step 3, day 7, same thread** (take-away):

> Last one from me.
>
> Honestly, if you're booked out and happy at the size you are, this isn't for you and I'll leave it there.
>
> If you'd rather have homeowners show up already knowing the price, the page is yours: {{tool_url}}
> 20 min with me: [BOOKING_LINK]

---

## Pre-send checks (CLAUDE.md rules)

- **Words:** step 1 runs 70–80 words. Plain text, no images.
- **Subjects:** lowercase and literal. No "Re:", no fake urgency.
- **Claims:**
  - No claims about the prospect's ads, reviews or website.
  - No monthly-payment promise.
  - No invented numbers. "3 quotes" is the homeowner behavior the VOC shows, not a statistic about the prospect.
- **Links:** 2 links in step 1 (tool + booking), as Neal decided. Click tracking stays OFF. Full URLs, no shorteners.
- **Merge fields:** every `{{tool_url}}` must resolve. Send a test to a seed inbox for each variant before launch.
