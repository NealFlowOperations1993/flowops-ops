#!/usr/bin/env python3
"""
Test the Council locally on a real lead.

Usage:
  python3 run_local.py                      # uses built-in test lead (med spa in Phoenix)
  python3 run_local.py --niche FINANCIAL    # different niche test
  python3 run_local.py --lead path/to/lead.json
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from core import council


# Built-in test leads per niche (so we can sanity-check across niches)
SAMPLE_LEADS = {
    "MEDSPA": {
        "company_name": "Glow Aesthetics MedSpa",
        "city": "Phoenix",
        "state": "AZ",
        "niche": "MEDSPA",
        "website": "https://glowaesthetics.com",
        "category": "Med Spa",
    },
    "FINANCIAL": {
        "company_name": "Pacific Wealth Group",
        "city": "Phoenix",
        "state": "AZ",
        "niche": "FINANCIAL",
        "website": "https://pacificwealthgroup.com",
        "category": "Financial Advisor",
    },
    "MORTGAGE": {
        "company_name": "Edge Home Finance",
        "city": "Tampa",
        "state": "FL",
        "niche": "MORTGAGE",
        "website": "https://edgehomefinance.com",
        "category": "Mortgage Broker",
    },
    "PI_LAW": {
        "company_name": "Cohen Injury Law",
        "city": "Houston",
        "state": "TX",
        "niche": "PI_LAW",
        "website": "https://coheninjurylaw.com",
        "category": "Personal Injury Attorney",
    },
}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--niche", default="MEDSPA", choices=list(SAMPLE_LEADS.keys()),
                   help="Use a built-in sample lead for this niche")
    p.add_argument("--lead", help="Path to a JSON file with a custom lead")
    p.add_argument("--niche-context", help="Optional path to a JSON file with reverse_magnet_offer + pain_anchor")
    p.add_argument("--debug", action="store_true", help="Print phase-by-phase progress")
    p.add_argument("--quiet", action="store_true", help="Only print final 9-key JSON")
    args = p.parse_args()

    if args.lead:
        lead = json.loads(Path(args.lead).read_text())
    else:
        lead = SAMPLE_LEADS[args.niche]

    niche_context = None
    if args.niche_context:
        niche_context = json.loads(Path(args.niche_context).read_text())

    if not args.quiet:
        print("═" * 60)
        print(f"COUNCIL — testing {lead.get('niche', 'unknown')} niche")
        print("═" * 60)
        print(f"Lead: {lead}")
        print()

    result = council.generate(lead, niche_context=niche_context, debug=args.debug or not args.quiet)

    print()
    if args.quiet:
        print(json.dumps(result["final"], indent=2))
        return

    print("═" * 60)
    print("FINAL OUTPUT")
    print("═" * 60)
    print(f"Voice persona: {result['winning_persona_for_voice']}")
    print(f"Cost: ${result['cost_usd']}")
    print(f"Latency: {result['latency_sec']}s")
    print(f"Council run ID: {result['council_run_id']}")
    print()

    print("─" * 60)
    print("EMAIL 1 (Day 0)")
    print("─" * 60)
    print(f"Opener: {result['final']['email1_opener']}")
    print()
    print(f"Pain:   {result['final']['email1_pain']}")
    print()
    print(f"CTA:    {result['final']['email1_cta']}")
    print()

    print("─" * 60)
    print("EMAIL 2 (Day 3)")
    print("─" * 60)
    print(f"Opener: {result['final']['email2_opener']}")
    print(f"Pain:   {result['final']['email2_pain']}")
    print(f"CTA:    {result['final']['email2_cta']}")
    print()

    print("─" * 60)
    print("EMAIL 3 (Day 7)")
    print("─" * 60)
    print(f"Opener: {result['final']['email3_opener']}")
    print(f"Pain:   {result['final']['email3_pain']}")
    print(f"CTA:    {result['final']['email3_cta']}")
    print()

    print("─" * 60)
    print("JUDGE DECISIONS")
    print("─" * 60)
    for dim, decision in result["judges"].items():
        print(f"{dim:>8}: persona '{decision['winning_persona']}' won. {decision['reasoning']}")
    print()
    print(f"Coherence approved: {result['coherence'].get('approved', '?')}")


if __name__ == "__main__":
    main()
