# Wave 2 copy: Mortgage brokers + Wealth managers (Nov 5, 2026)

Drafts. Neal approves before anything loads into Smartlead.
Same structure as Wave 1 (v7): plain text, no links in emails 1 and 2, tool link in email 3,
`{{personal_line}}` (from the prospect's own Google reviews) opens email 1, delays 0/3/4 days.
A/B = two angles, same branded tool. 63/62 per day per niche.

Tools (Lovable Tool Studio, `{{tool_url}}`):
- Mortgage: `mortgage-true-monthly`. Borrower enters price, down payment, rate, term, taxes,
  insurance, PMI, HOA and sees one full monthly payment. Reg Z disclaimer + Equal Housing line on page.
- Wealth: `wealth-retirement-checkup`. Six yes/no/not-sure questions, result shows gaps,
  CTA to request a review. Educational-only disclaimer on page.

Footer on every email:
```
%signature%

FlowOperations · 293 Cardiff Dr., Morganville, NJ 07751
Not for you? Reply "stop" and I won't email again.
```

---

## MORTGAGE A — subject: `the borrowers you never hear from`

**Email 1 (day 0)**
Hey {{first_name}},

{{personal_line}}

Clients like that send referrals for years. The ones you lose are the borrowers who never call. They run their numbers on a bank or lead-site calculator at night, and that site passes them to whichever lender paid for the lead. You never know they existed.

We built a free payment calculator branded for {{company_name}}. Borrowers see their real monthly payment (principal, interest, taxes, insurance, PMI and HOA), and their request comes straight to you.

Want to see it?

**Email 2 (day 3)**
{{first_name}}, one more thought.

A rate quote invites comparison shopping. A full monthly payment, built from the borrower's own numbers on your page, starts a conversation with you instead.

Want me to send it over?

**Email 3 (day 7)**
Last one from me.

If your pipeline is full of borrowers who already picked you, ignore this and I'll leave it there.

If not, here's the calculator we built for {{company_name}}: {{tool_url}}

Reply "call" and Neal, our founder, will show you how to put it to work.

## MORTGAGE B — subject: `tired of rate shoppers?`

**Email 1 (day 0)**
Hey {{first_name}},

{{personal_line}}

Work like that should have borrowers coming to you ready to move. Instead, how often does someone take your quote to two other lenders and disappear over an eighth of a point?

Rate isn't what they live with. The monthly payment is.

We built a calculator branded for {{company_name}} that shows borrowers their full monthly payment and sends their request straight to you, so the conversation starts on the number that matters.

Want to see it?

**Email 2 (day 3)**
{{first_name}}, one more thought.

Most borrowers can't tell you their real payment until someone adds taxes, insurance and PMI for them. Whoever does that first usually gets the call.

Want me to send the calculator over?

**Email 3 (day 7)**: same as Mortgage A email 3.

---

## WEALTH A — subject: `the clients you never hear from`

**Email 1 (day 0)**
Hey {{first_name}},

{{personal_line}}

Clients like that stay for decades. The ones you lose are the people who never reach out. They visit an advisor's site, aren't ready to book a meeting with someone they've never met, and leave. You never know they were there.

We built a free retirement check-up branded for {{company_name}}. Six quick questions, and the visitor sees where their plan looks solid, where it has gaps, and how to ask you for a review.

Want to see it?

**Email 2 (day 3)**
{{first_name}}, one more thought.

"Schedule a consultation" is a big ask from a stranger. Six questions about their own retirement is a small one, and it gives them a reason to talk to you.

Want me to send it over?

**Email 3 (day 7)**
Last one from me.

If referrals keep your calendar as full as you want it, ignore this and I'll leave it there.

If not, here's the check-up we built for {{company_name}}: {{tool_url}}

Reply "call" and Neal, our founder, will show you how to put it to work.

## WEALTH B — subject: `when referrals slow down`

**Email 1 (day 0)**
Hey {{first_name}},

{{personal_line}}

Work like that earns referrals. The catch is that referrals arrive when they arrive. You can't turn them up when you want to grow.

We built a free retirement check-up branded for {{company_name}}. Website visitors answer six quick questions, see where their plan has gaps, and can ask you for a review in one step.

Want to see it?

**Email 2 (day 3)**
{{first_name}}, one more thought.

Most people looking for an advisor aren't ready to book a meeting yet. A short check-up meets them where they are and puts your name on the answer.

Want me to send it over?

**Email 3 (day 7)**: same as Wealth A email 3.

---

## Claims and compliance checks
- "request comes straight to you": true. Tool submissions go through n8n
  `FO — Tool Studio Lead → Contractor Email` to the prospect's own email (owner_email).
- Lead sites passing borrowers to paying lenders: describes the lead-marketplace model
  (e.g. LendingTree matches borrowers with several lenders). No numbers claimed.
- No claims about the prospect's own website, rates, or business. No performance promises.
- Wealth tool CTA currently reads "Book a free review". Not every advisor offers a free
  review. Recommend changing the default to "Request a review" before sending (Lovable copy).
- Mortgage page shows NMLS only when real; Reg Z + Equal Housing lines present.
- `{{personal_line}}` built from the prospect's own Google reviews, verified verbatim,
  praise only. Never criticism, never an absence claim.

## Metric
Positive reply rate per delivered email. Gate: 2% on 500+ sends per niche before scaling.
