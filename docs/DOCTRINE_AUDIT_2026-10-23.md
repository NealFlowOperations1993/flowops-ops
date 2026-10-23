# The 22-Stage Doctrine vs. the Live Engine — Catch-Up Audit

**Date:** 2026-10-23
**Doctrine source:** `lovable-backup-cold-email/src/data/coldEmailAugust2026.ts` — the data file behind
`flowoperations.org/cold-email-august-2026` (backed up 2026-08-25; the live page could not be fetched from
the cloud session, so any edits made to it after Aug 25 are not reflected here).
**Current-state sources:** `docs/FlowOps_Cold_Email_Infrastructure.pdf` (live data 2026-10-12, addendum
2026-10-23), `CLAUDE.md` (2026-10-23), the repo code. n8n and Smartlead were not queried directly.

---

## The short version

The doctrine's own philosophy: *"The system is not a funnel, it is a circuit… Optimization is driven by
downstream revenue truth — never by vanity opens."*

Measured against that, the engine is **strong in the middle and weak at both ends**.

- **Strong:** infrastructure and hygiene (stages 06, 12, 15, 16). Bounce is the one metric at
  exceptional level; warmup is 100%; the ramp governor, bounce breaker and reply pipeline all run daily.
- **Broken:** the truth of the offer and the message (02, 09, 13). The email promises things the
  system does not do, and opened by criticising strangers. That is the 0.11% reply rate.
- **Missing:** everything after a "yes" (17, 18, 19). The best lead the system ever produced has
  waited 34 days for a price.
- **The circuit is open.** With 7 human replies and 0 calls, there is no revenue truth flowing
  back upstream, so the optimization loops (21) are tuning subject lines on open rate — the exact
  "vanity opens" signal the doctrine forbids, and which our own data shows is ~70% machines.

Status key: ✅ meets the stage's gates · ◐ partial · ⚠ gate actively failing · ✗ not built

## Stage-by-stage

| # | Stage | Status | Evidence | Gap against the doctrine's gates |
|---|---|---|---|---|
| 01 | Pick Niche | ◐ | Outdoor-living contractors in 14 affluent counties (median home >$500K) | **Reachable TAM never sized.** 917 fresh leads lasted ~3 days. Deal value (KPI) not recorded anywhere in the repo |
| 02 | Create Offer | ⚠ | Give-first reverse lead magnet; estimator / booking page matched to where the homeowner gets stuck | Gate "believable mechanism" fails in practice: **tool submissions never reach the contractor** while the email says they do (all ~2,558 pages). No proof attached (peer-proof is an open decision). No ready price — Ben's "Ballpark?" is still unanswered |
| 03 | ICP + Segments | ◐ | Four queryable layer-2 gates (hardscape vocabulary, not mow-and-blow, portfolio, 15+ reviews/4.0+) | Tiers exist on paper (8+ sniper / 5–7 precision) but **every lead scores 5–6** — no Tier 1, because owner names and review mining aren't built |
| 04 | Find Lead Sources | ⚠ | Google Maps via Apify, $0.033/qualified lead | Gate "two independent sources per segment" fails: contractors come from **one source**. Lead Engine v1's sources (OnlineJobs, Skool, EDGAR) don't serve this niche |
| 05 | Scrape / Acquire | ◐ | Last run 1,460 places → 221 qualified, $7.30 | Generator scripts still **only run on the Mac** (deferred by design). Per-row provenance not verified |
| 06 | Normalize + Dedupe | ✅ | Master list 33,132 deduped by email; domain dedupe; "never previously contacted" send gate | Merge trail not confirmed |
| 07 | Enrich | ◐ | Evidence-based signals (real `fbq('init')`, real `AW-` IDs, real Angi links); score computed | No owner names → role-inbox skew (−2 score). Required-variable gate exists (merge-field scan of every lead) |
| 08 | Verify + Suppress | ◐ | MX check, junk/placeholder filters, Smartlead global block list | No mailbox-level verification. **Deck Builders 3.8% and Hardscape v2 7.1% bounce** — both above the breaker |
| 09 | Personalize | ⚠ (rules now ✅) | Rule now: state only what was observed | History: criticism openers produced most hostile replies; signal false positives put false claims in 11 emails. "Fallback present" gate not verified. **Conflicting records** about whether openers are LLM-written (`council_mini.py`, Haiku scripts) or deterministic (Aug Engine Map) — needs one answer |
| 10 | Domain Architecture | ◐ | 2 sending domains, separate from the primary | No written retirement rules or per-domain caps beyond the inbox cap |
| 11 | DNS + Inbox | ◐ | SPF/DKIM/MX valid on both | DMARC `p=none`. Gate "signatures match a real, findable entity": **8 of 10 inboxes are fictional people** — an open decision, flagged not changed |
| 12 | Warm-up + Reputation | ✅ | 169–176-day inboxes, 100% reputation, 35/inbox cap, age-based ramp, bounce freeze at 2% | No seed-list placement tests (gate "placement verified by seed tests") |
| 13 | Build Messaging | ⚠ **binding constraint** | 0.11% human reply rate, 20× below the 2–3% floor | Gate "all claims supported" fails (instant-lead promise, monthly-payment promise). Orphaned line ("Rather than send you a list of problems"). Subjects break the rules (fake "Re:", ellipsis, "free"). Live copy can't be fixed in place — needs a **new campaign** |
| 14 | Assembly + QA | ◐ | Send gates: URL 200, every merge field populated, MX, not a duplicate | **No coherence check** across subject / body / merge fields / tool type — 119 leads got estimator copy with a booking page. `judges/coherence_judge.md` exists but only checks opener + pain + CTA, not the rendered email. No seed addresses. No formal launch approval |
| 15 | Launch + Sending | ✅ (idle) | Ramp Governor = min(curve, capacity, supply); bounce freeze; 06:00–10:00 ET window from our own data | 0 sends since Oct 5 — 38 untouched leads vs 315/day capacity |
| 16 | Reply Classification | ✅ | B30: webhook → classify → log → unsubscribe → guardrail → call push → Slack; 6-minute machine filter | Fine. (Remember: `from_email` is ours, `sl_lead_email` is theirs) |
| 17 | Qualification + Response | ⚠ | Call Push sends tool + booking link on positives | Gate "response within SLA" fails: **Ben unanswered since Sep 19 (34 days)**. Auto-reply sends a link when the prospect asked a question. No qualification criteria captured |
| 18 | Booking + Show-Up | ✗ | Bare GHL calendar link; booking threads into Slack | No confirmation content, reminders, rescheduling or no-show recovery. Never exercised — 0 calls |
| 19 | CRM + Handoff | ◐ | Slack thread per lead; GHL calendar | No opportunity record carrying source, signal, copy variant and offer — so revenue can't be attributed backward when it arrives |
| 20 | Analytics + Attribution | ◐ | Reports 4×/day; bot-vs-human reply split; open rate correctly debunked (48% → ~15–18%) | Variant attribution should use `seq_variant_id`. Chain stops at "replied" — booked/held/won/revenue/CAC are empty |
| 21 | Optimization Loops | ⚠ | Daily Study, Copy Forge, Split-Test Referee (recommend-only), Phase Optimizer | At 7 human replies **no test can reach significance**. The loops propose subject lines judged on opens — the vanity metric the doctrine rules out |
| 22 | Governance | ◐ | Incidents → rules (11 logged); keys moved to env; repos private | 4 exposed keys **not yet rotated**. Spend cap disagrees: $20/day (n8n Budget Guard) vs $50/day (`spend_guard.py`). 18 files hardcode `/Users/nealthakkar/...`. Several docs contradict each other (below) |

## The five feedback loops

| Loop | Status | What happened |
|---|---|---|
| Replies/objections → offer + copy | **Blocked** | Lessons were learned (stop criticising, stop false claims) but couldn't reach live copy because Smartlead sequence writes re-queue contacted leads. The outage removes that blocker — the new campaign closes this loop |
| Revenue → ICP, segments, sources | **Open** | No meetings, no revenue — nothing to feed back yet |
| Deliverability → verification, infra | **Working** | 11.9% bounce → extraction filters; reputation decay → 35/inbox cap; bounce breaker |
| Personalization failures → research rules | **Working** | 34% signal false positives → "real evidence, never a keyword" |
| Test results → backlog → relaunch | **Starved** | Machinery exists; sample too small to learn from |

## Documents that are now out of date

| Document | Says | Current |
|---|---|---|
| FlowOps Engine Map (Aug 24 HTML) | 2 campaigns active, 500/day, 50/inbox, 7 days a week 6–6 | 0 running, 315/day safe capacity, 35/inbox, Mon–Fri 06:00–10:00 |
| Engine Map | Openers "deterministic, zero LLM" | Repo contains LLM opener pipelines; which ran is unresolved |
| `rubric/RUBRIC.md` (Aug 25) | Raw reply 2.4%, open 53–61% | 0.11% human reply; true open ~15–18% |
| `morning_check.py` | Checks MCA / WEALTH / INSURANCE etc. campaigns | Program is the four contractor campaigns |
| `spend_guard.py` | $50/day cap | n8n Budget Guard enforces $20/day |
| Lovable War Machine / SOP tabs | $577K/mo projections, 70–100/inbox | Already recorded as fiction in `EXTRACTION.md` |

## Catch-up plan, in order

The restart plan in the infrastructure guide (§11) is right. Mapped to the doctrine, with the gaps
above folded in:

1. **Answer Ben** (stage 17) — a straight number for "Ballpark?". Needs a price, which also fills
   stage 02's missing pricing.
2. **Make the promise true** (02) — on every tool submission, email the lead to the contractor. One
   n8n workflow (`oXeFIbzjw458LXdN`), fixes all ~2,558 pages.
3. **One new campaign + a real coherence gate** (13, 14) — compliant subjects, no orphaned lines, no
   monthly-payment promise, copy routed by tool type. The gate renders the actual email for every lead and
   fails on unresolved tags, rule violations, tool/copy mismatch, or any claim the tool can't back.
4. **Refill and add a second source** (04, 05) — ~$8.60/day of Maps scraping, plus one independent
   contractor source to meet the two-source gate.
5. **Restart at 150–200/day** (15) — hold until human reply rate clears 2% on a few hundred sends.
   Judge on replies, never opens.
6. **Build what happens after yes** (17–19) — answer questions before sending links; confirmation,
   reminders and no-show recovery in GHL; an opportunity record that carries source, variant and offer.
7. **Governance clean-up** (22) — rotate the 4 keys; pick one spend cap; mark stale docs as superseded;
   remove hardcoded Mac paths.

Steps 1–2 are each under an hour of work and unblock everything else. Steps 3–5 are the test the whole
program depends on. None of it requires more inboxes, more domains, or more volume.

## Goals check: 3,000 sends/day by Jan 1, 4% reply rate

**4% reply rate.** That is the "good" band (4–6%) on the industry table in the infrastructure guide, and
36× today's 0.11%. Top operators reach it, so it is a reasonable target. It is also unproven for this
offer. Count **human** replies only (the six-minute filter), and track positive replies (target ≥1%)
alongside, because a hostile reply also counts as a reply.

**3,000/day by Jan 1 (69 days).** Inbox warmup, lead supply and spend all have to be sorted out first:

| Need | Math | Implication |
|---|---|---|
| Inboxes | 3,000 ÷ ~30–35/inbox, with a 10% margin | **~100 inboxes across ~35 domains**, i.e. ~90 new inboxes and ~33 new domains |
| Warmup time | New inboxes reach the full 35/day cap at 21+ days; graduation needs 14+ days and ≥90% reputation | Domains must be bought by **~Nov 7** to be at full capacity by mid-December |
| Leads | 3-email sequence → ~1,000 **new** leads/day at steady state | ~22,000 new leads/month. The current 14-county contractor pool cannot supply this; needs national geography and probably a second niche (TAM still unsized: stage 01) |
| Lead cost | 1,000 × $0.033 | ~$33/day, which is above the $20/day Budget Guard cap |
| Inbox cost | ~90 new mailboxes | A recurring monthly cost; needs an explicit decision |

**Does this conflict with the 2% rule?** No, as long as the work runs in parallel. Warmup sends no cold
email, so warming new domains does not break the rule against scaling volume before reply rate clears 2%.
The safe sequence:

1. **Now → ~Nov 7:** new campaign live at 150–200/day on the existing 10 inboxes. In parallel, buy and
   start warming the new domains.
2. **~Nov 17 (decision gate):** ~2,000 sends on the new copy. If human reply rate is ≥2%, ramp. If not,
   fix the copy again, because scaling would only spread a 0.11% result across 35 new domains.
3. **Late Nov → Jan 1:** the Ramp Governor raises volume as new inboxes mature: ~1,000/day by early
   December, 3,000/day by late December.

**Do you need 3,000/day?** The stated outcome is 3–5 calls/day. At a 4% reply rate and roughly one in four
replies converting to a booked call (~1% booked), **~400–500 sends/day already gets there**. At 3,000/day
with 4% replies, that is ~120 replies/day, which needs a reply desk and booking flow (stages 17–18) that
do not exist yet. Decide which goal is primary: volume, or calls.

## Open rate: what "good" means here

Do not set an open-rate goal. Raw opens are inflated by security scanners and Apple Mail Privacy
Protection: the measured median time-to-open is 24 seconds, and 1,610 opens produced 0 clicks. Use open
rate only as a **deliverability alarm**:

- **Filtered human opens** (excluding opens under 60 seconds): currently ~15–18%. Treat ~15–25% as healthy
  for cold email. A sustained drop well below that is a placement problem worth investigating.
- **Raw dashboard opens:** compare each domain against its own baseline, and investigate a sudden fall
  (e.g. 56.8% → 26.7% on the young domains in September), not the absolute number.
- **Better placement signal:** seed-list inbox-placement tests (stage 12), which are not built yet.

The goal metrics are human reply rate, positive reply rate and booked calls.

## An honest limit

Seven human replies is a small sample. This audit names defects that can be shown to exist; it does not
prove that fixing them will lift reply rate to 2%. It does make the next test clean and cheap — and the
infrastructure to run it is already built and paid for.
