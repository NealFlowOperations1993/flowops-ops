# Session handoff — 2026-11-13

The previous session lost every connector (Lovable, n8n, Slack, Gmail…) after a worker restart.
Start here in the new session. Lead data (names/emails) is NOT in the repo.

## Targeting (Neal, Nov 12)
- Home services 70%: 1 Hardscaping (lead niche; Tyler's case study is the proof), 2 Deck, 3 HVAC (scores highest on paper), 4 Pool builders, 5 Roofing.
- Loan brokers 30%: hard money / fix-and-flip, SBA, business & commercial, credit stacking.
- Mortgage/wealth: finish loaded leads only, no new leads.
- **Sending now runs 7 days a week.** Campaign schedules are still Mon–Fri 8:00–16:30 CT → add Sat/Sun (schedule setting only, never the sequence).

## Lead sourcing — free, no Apify spend
- Leads come from the already-scraped Google Maps pools, then free website scraping for email, phone, signals, offer (the Josh Iddins method).
- Untouched in pools (before dedupe): hardscape ~920, deck ~208, mortgage ~353.
- New niches: free sources (manufacturer dealer locators, state licence lists, SBA lender lists) + website scraping.
- Apify account is at its $200/$200 usage cap; token looks fine. A "Cursor" app also has access (used Nov 13). Don't run new Apify scrapes without Neal.

## Done Nov 12
- Sent 315/315 (all 9 inboxes at 35). New leads: deck 55/75, hardscape 74/100, mortgage 50/50.
- Batch 3 Reoon files sent to Neal (142 hardscape, 155 deck). Waiting on his results.
- Tool pages (Lovable 66a47df4-adf0-420c-b217-e17c92b29e49): tracking + offer build finished (166 tests).
  Offers loaded for 213 prospects: services, materials, areas, licence, years, CTA, rating+count, response promise.
  Held back for review: gallery, review quotes, specialty, guarantee, financing, promo, price anchor.
  **NOT yet published.** Needs Neal's approval.
- Lead Sources doc updated: https://claude.ai/artifact/XPzV9ZPVKEFDXdnbiKy2V4
  Rule: webinars and courses target the SUBSCRIBERS (owners whose lead-gen know-how isn't working), not the creators.
  Trade shows target ATTENDEES, not speakers or exhibitors. Neal's ideas are tagged "Raine"; Claude's ideas are tagged "Claude".

## Next, in order
1. Turn on Sat/Sun sending for W3 deck 4336994, W3 hardscape 4336993, W4 4452197.
2. Check today's sends; deck likely ran dry → pull the next deck/hardscape leads from the pools.
3. Run today's dashboard update. The 7:23 CT scheduled run probably failed without connectors.
4. Publish the tool pages after Neal approves.
5. Build batch 3 when the Reoon results arrive.
6. Follow-up share: keep at 40%. Lead supply, not inbox room, is the limit.

Pipeline scripts: scripts/pipeline/. Dashboard scripts: scripts/ce_daily/.
