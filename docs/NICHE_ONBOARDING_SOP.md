# Niche Onboarding SOP

**Trigger:** Neal says in chat: *"Add the niche: <niche>"* (e.g. "personal injury lawyer").
Claude runs steps 1–6 without further prompting, then stops at step 7 for approval.
Any real question goes to Neal; everything else uses the defaults below.

Copy is the one exception: **Neal writes all email copy.** Agents never draft it.

---

## 1. Source at least 500 high-quality leads

**Two-stage Google Maps scrape.** It runs through the n8n gateway `FO — Apify Gateway`
(`u15g93O0c3cll1fQ`) using actor `compass~crawler-google-places`.

### Stage A: places only ($0.003/place)

- Use 2 search terms per niche, run across affluent counties.
- Size the run backwards from the target. Today's real rates: about 26% of places pass
  Stage A filters, and Stage B email yield is measured per niche.
  For 500 verified leads, start with about 4,000 places (about 50 counties × 80).
- One run per county. Cap `maxTotalChargeUsd` at 0.5 per run.
- Keep concurrency at 16 runs or fewer at 4 GB each. Apify's account memory limit is 64 GB;
  2 GB runs allow 32.

### Required filters

- Rating ≥ 4.3
- Reviews ≥ 10
- A real website (not Facebook, Yelp, Wix-site or similar)
- Open (not closed)
- Category and title actually match the niche
- Not a chain, supplier or franchise HQ

### Exclusions

Drop anything matching old campaign exports or the blocklist (`leads_raw/*.csv`).
Dedupe by `placeId` and by domain.

### Preferred filter: running ads

The free n8n workflow `FO — Ad Pixel Check` (`epKtUqpGmyCPRO0W`) flags homepages that have:
- a Google Ads tag (`AW-…`, googleadservices), or
- a Meta Pixel (`fbq('init'` / fbevents.js).

These leads are sorted first.

A tag means "very likely spends on ads", not proof. Per the hard-won rules, never state
"you're running ads" in copy based on this alone.

### Stage B: enrichment (about $0.014/place)

Re-run only the qualified `placeIds` with:
- `scrapeContacts`
- `maximumLeadsEnrichmentRecords: 1`
- `leadsEnrichmentDepartments: ["c_suite"]`
- `verifyLeadsEnrichmentEmails: true`

## 2. Verify

- Keep only emails whose verification result is `valid`.
- Catch-all and unknown results go to a separate "risky" file and are not sent in the test.
- Once Neal buys a bulk verifier (Reoon / MillionVerifier), run every lead through it as
  a second pass.
- After upload to Smartlead, **scan every lead**, never a sample.

## 3. Add to the cold email system

- Create a **new** Smartlead campaign `<Niche> — Test <date>`. Never write to a live
  sequence.
- Upload leads with custom fields: first_name, company, city, rating, reviews, ads_flag,
  website.
- 2-variant split (63/62 per day) between the two tools or angles.
- The campaign stays **DRAFT** until Neal pastes his copy and approves.
- Run the pre-send coherence check: no orphaned lines, no monthly-payment promise,
  compliant subject.
- Volume: 125/day per niche during the 8-day test (1,000 emails).
- Inbox ceiling: 10 inboxes ≈ 300 sends/day *including follow-ups*.

## 4. Add to metrics and predictions

- Add the niche row to the Lovable dashboard: `ce_status`, the test-plan table, and the
  `leads_cache` refresh.
- Record:
  - places scraped, qualified count, verified count
  - cost per verified lead
  - ads-flag share
- The prediction uses the 2% reply gate. Do not scale a niche until it clears 2% on
  ≥ 500 sends.

## 5. Run VOC (about $0.40/niche)

- Google Maps reviews from 2 metros × 15 top businesses × 20 reviews.
  - One metro sorted `lowestRanking`, to surface pain.
  - One metro sorted `mostRelevant`, to surface what wins.
- Claude codes the reviews into themes, with counts and verbatim quotes.
- Save to `voc/<niche>.md` and to the dashboard VOC tab.
- Limit: this is the *end-customer* voice. Owner-voice sources (Reddit, forums) are
  blocked from this environment; add them when an allowed source exists.

## 6. Propose 3 tools

For each tool, give:
- name
- what the prospect gets in 30 seconds
- the VOC theme and quotes it answers
- build effort
- how the submission reaches the prospect: the n8n `fo-tool-lead` webhook **plus** the
  contractor notification

## 7. Approval, then build

Neal replies "approve 1/2/3". Claude builds the approved tool page in `flowops-assets`,
deploys it, wires the submission flow, tests it end to end, and adds the link to the
campaign's custom fields.

---

### Budget guard

- Default spend ceiling per new niche is about **$25 on Apify**.
- Apify's monthly cap is $120 (check `GET /v2/users/me/limits` first).
- If the cap would be hit, stop and tell Neal before spending.
