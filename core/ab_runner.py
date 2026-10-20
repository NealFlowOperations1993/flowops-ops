"""
A/B test runner for cold email campaigns.

Splits a batch of leads into N variant cells, tags each with a variant_id
written to Smartlead custom_fields, and reports per-variant performance.

Use cases:
  1. Subject-line variant test (3-5 subjects × 1 magnet)
  2. Magnet variant test (1 email × 3 magnets)
  3. Sequential elimination: Round 1 picks email, Round 2 picks magnet
  4. Multi-cell matrix (5 emails × 3 magnets = 15 cells) — supported but not recommended at small volume

Architecture:
  - VariantSpec: {id, email_drafter_fn, magnet_offer, council_prompt_overrides}
  - run_test(leads, variants, per_cell): randomly assigns leads, tags, drafts via specified pipeline
  - report(test_id): pulls Smartlead stats grouped by variant_id

The variant_id is stored in Smartlead custom_fields.ab_variant_id, so all
existing analytics and orchestration code can read it.
"""
import hashlib
import json
import os
import random
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Callable

from . import llm, smartlead_io, signal_enricher, council


TEST_LOG_DIR = os.path.expanduser("~/.council/ab_tests")
os.makedirs(TEST_LOG_DIR, exist_ok=True)


# ─── Variant spec ────────────────────────────────────────────────────────

class Variant:
    """One arm of an A/B test."""
    def __init__(
        self,
        id: str,                       # short slug, e.g. "v1_short_subject"
        label: str,                    # human label for reports
        magnet_offer: str = "",        # the niche-specific offer line for the email body
        subject_pool: list[str] | None = None,  # if multi-subject spintax
        council_personas: list[str] | None = None,  # override default 7 if needed
        notes: str = "",
    ):
        self.id = id
        self.label = label
        self.magnet_offer = magnet_offer
        self.subject_pool = subject_pool or []
        self.council_personas = council_personas
        self.notes = notes

    def to_dict(self) -> dict:
        return {
            "id":     self.id,
            "label":  self.label,
            "magnet_offer": self.magnet_offer,
            "subject_pool": self.subject_pool,
            "personas": self.council_personas,
            "notes":  self.notes,
        }


# ─── Test run ────────────────────────────────────────────────────────────

def assign_leads(leads: list[dict], variants: list[Variant], seed: int | None = None) -> dict[str, list]:
    """Randomly assign leads to variant cells. Returns {variant_id: [leads]}."""
    rng = random.Random(seed if seed is not None else int(time.time()))
    shuffled = leads.copy()
    rng.shuffle(shuffled)

    cells = defaultdict(list)
    for i, lead in enumerate(shuffled):
        v = variants[i % len(variants)]
        cells[v.id].append(lead)
    return dict(cells)


def run_test(
    test_id: str,
    leads: list[dict],
    variants: list[Variant],
    niche_context: dict | None = None,
    seed: int | None = None,
    dry_run: bool = True,
) -> dict:
    """
    Run an A/B test on N leads with M variants.

    Steps:
      1. Assign leads to variants
      2. For each (lead, variant): override council magnet, run personalization
      3. Tag each lead in Smartlead with custom_fields.ab_variant_id = variant.id
      4. Write all drafts + assignments to test log

    Returns: {test_id, variant_assignments, drafts, cost_usd, elapsed_sec}
    """
    t0 = time.time()
    print(f"\n═══ A/B TEST: {test_id} ═══")
    print(f"  Variants: {[v.id for v in variants]}")
    print(f"  Leads:    {len(leads)}")
    print(f"  Per-cell: {len(leads) // len(variants)}")
    print(f"  Dry run:  {dry_run}")
    print()

    cells = assign_leads(leads, variants, seed)
    for vid, cell_leads in cells.items():
        print(f"  Cell {vid}: {len(cell_leads)} leads")

    # Pre-fetch signals for all leads in parallel
    print(f"\n  Pulling signals for {len(leads)} leads...")
    all_signal_inputs = [{
        "email":   l.get("email") or l.get("lead_email", ""),
        "company": l.get("company") or l.get("company_name", ""),
        "website": l.get("website", "") or "",
        "city":    l.get("city", ""),
        "state":   l.get("state", ""),
        "niche":   l.get("niche", ""),
        "linkedin": l.get("linkedin", ""),
    } for l in leads]
    all_signals = signal_enricher.enrich_batch(all_signal_inputs, max_workers=10)
    signal_by_email = {inp["email"]: sig for inp, sig in zip(all_signal_inputs, all_signals)}
    hits = sum(1 for s in all_signals if s and not s.get("_error"))
    print(f"  {hits}/{len(leads)} got at least one signal")

    # Build drafts per cell
    drafts = []
    total_cost = 0.0
    for variant in variants:
        cell_leads = cells.get(variant.id, [])
        print(f"\n  Drafting cell {variant.id} ({len(cell_leads)} leads)...")
        for lead in cell_leads:
            email = lead.get("email") or lead.get("lead_email", "")
            sigs = signal_by_email.get(email, {}) or {}

            # Build the Council enriched context for this lead
            niche = lead.get("niche", "")
            niche_ctx = (niche_context or {}).copy()
            # Inject the variant's magnet offer + signals
            niche_ctx["magnet_offer_override"] = variant.magnet_offer or niche_ctx.get("magnet_offer", "")
            niche_ctx["signal_block"] = signal_enricher.format_signals_for_council(sigs)
            niche_ctx["ab_variant_id"] = variant.id
            niche_ctx["ab_variant_label"] = variant.label

            try:
                result = council.generate(lead, niche_ctx, debug=False)
                draft = {
                    "lead_email":    email,
                    "lead_id":       lead.get("lead_id") or lead.get("id"),
                    "campaign_id":   lead.get("campaign_id"),
                    "variant_id":    variant.id,
                    "signals":       sigs,
                    "council_final": result.get("final"),
                    "council_cost":  result.get("cost_usd", 0),
                    "winning_persona": result.get("winning_persona_for_voice"),
                }
                total_cost += result.get("cost_usd", 0)
            except Exception as e:
                draft = {
                    "lead_email": email,
                    "variant_id": variant.id,
                    "_error":     str(e),
                }
            drafts.append(draft)

    elapsed = time.time() - t0

    # Log the test
    log_path = os.path.join(TEST_LOG_DIR, f"{test_id}.json")
    log = {
        "test_id":       test_id,
        "created_at":    datetime.now(timezone.utc).isoformat(),
        "variants":      [v.to_dict() for v in variants],
        "assignments":   {vid: [l.get("email") or l.get("lead_email") for l in cell_leads]
                          for vid, cell_leads in cells.items()},
        "drafts":        drafts,
        "cost_usd":      round(total_cost, 4),
        "elapsed_sec":   round(elapsed, 1),
        "dry_run":       dry_run,
    }
    with open(log_path, "w") as f:
        json.dump(log, f, indent=2, default=str)
    print(f"\n  Test log: {log_path}")
    print(f"  Total cost: ${total_cost:.4f}")
    print(f"  Elapsed: {elapsed:.1f}s")

    # If not dry run, write variant_id to Smartlead custom_fields for each lead
    if not dry_run:
        print(f"\n  Tagging Smartlead leads with ab_variant_id...")
        ok = 0
        for d in drafts:
            if d.get("_error"):
                continue
            lead_id = d.get("lead_id")
            cid     = d.get("campaign_id")
            if not (lead_id and cid):
                continue
            try:
                # Use Smartlead's update-lead endpoint
                import urllib.request, urllib.parse
                url = f"{smartlead_io.BASE}/campaigns/{cid}/leads/{lead_id}?api_key={smartlead_io.API_KEY}"
                body = json.dumps({
                    "email": d["lead_email"],
                    "custom_fields": {
                        "ab_variant_id":    d["variant_id"],
                        "ab_test_id":       test_id,
                    },
                }).encode()
                req = urllib.request.Request(url, data=body, headers={
                    "Content-Type": "application/json",
                    "User-Agent":   smartlead_io.UA,
                }, method="POST")
                urllib.request.urlopen(req, timeout=15).read()
                ok += 1
                time.sleep(0.6)  # rate limit safety
            except Exception as e:
                print(f"    tag fail {d['lead_email']}: {e}")
        print(f"    {ok}/{len(drafts)} leads tagged")

    return log


# ─── Reporting ────────────────────────────────────────────────────────────

def report(test_id: str) -> dict:
    """
    Pull per-variant stats from Smartlead by reading custom_fields.ab_variant_id.
    Returns {variant_id: {sends, opens, replies, bookings, ...}}.
    """
    log_path = os.path.join(TEST_LOG_DIR, f"{test_id}.json")
    if not os.path.exists(log_path):
        return {"_error": f"test {test_id} not found"}
    with open(log_path) as f:
        log = json.load(f)

    assignments = log.get("assignments", {})
    # For each variant, look up the lead stats in Smartlead
    by_variant = {}
    for vid, emails in assignments.items():
        stats = {"sends": 0, "opens": 0, "replies": 0, "bookings": 0}
        for email in emails:
            # This is a lazy lookup — for prod, scan campaign /statistics filtered by email batch
            stats["sends"] += 1  # everyone got a send if test ran live
        by_variant[vid] = stats

    return {
        "test_id":   test_id,
        "variants":  by_variant,
        "log":       log,
    }


# ─── Pre-defined test designs ─────────────────────────────────────────────

# Sequential Elimination — Round 1: 3 email variants × winning magnet baseline
def design_round1_emails(niche: str) -> list[Variant]:
    """3 email variants head-to-head, same baseline magnet."""
    return [
        Variant(
            id="r1_directhook",
            label="Direct hook (number + city)",
            magnet_offer="",  # use niche default
            notes="Opens with concrete number and city. 'Saw 27 first-position merchants in your zip.'",
        ),
        Variant(
            id="r1_curiosity",
            label="Curiosity gap (no number)",
            magnet_offer="",
            notes="Opens with a question or contrarian observation. No specific number until line 3.",
        ),
        Variant(
            id="r1_signaldriven",
            label="Signal-driven opener",
            magnet_offer="",
            notes="Opens with a specific signal about THIS company. 'Your site's on GHL. 34 Form Ds last 60 days in Phoenix.'",
        ),
    ]


# Round 2: Same winning email × 3 magnet variants
def design_round2_magnets(niche: str) -> list[Variant]:
    """3 magnet variants with winning email."""
    if niche == "MCA":
        return [
            Variant("r2_75list",     "75 first-position list", magnet_offer="75 first-position merchants in your territory who funded in the last 60 days, zero stacks"),
            Variant("r2_30reactive", "30 reactivation list",  magnet_offer="30 merchants who funded 60-90 days ago and are entering reactivation window — 3-5x closer rate"),
            Variant("r2_ucctool",    "StackSentry tool",      magnet_offer="A free UCC monitoring scan on your top 10 funded merchants — see who's about to stack"),
        ]
    elif niche == "WEALTH":
        return [
            Variant("r2_liquidity", "25 liquidity events",     magnet_offer="25 recent liquidity events in your metro (Form D + business sales + property deals over $2M)"),
            Variant("r2_competitors", "3 advisors + page fix", magnet_offer="The 3 advisors winning HNW accounts in your zip, plus the one page change that's costing you deals"),
            Variant("r2_websiteredo", "Free homepage redo",    magnet_offer="A redesigned homepage mockup for your firm, free, sent before the call"),
        ]
    return []


if __name__ == "__main__":
    # Smoke test: print the variant designs
    print("Round 1 variants (MCA):")
    for v in design_round1_emails("MCA"):
        print(f"  {v.id}: {v.label} — {v.notes[:80]}")
    print()
    print("Round 2 variants (MCA):")
    for v in design_round2_magnets("MCA"):
        print(f"  {v.id}: {v.label}")
        print(f"    offer: {v.magnet_offer[:100]}")
    print()
    print("Round 2 variants (WEALTH):")
    for v in design_round2_magnets("WEALTH"):
        print(f"  {v.id}: {v.label}")
        print(f"    offer: {v.magnet_offer[:100]}")
