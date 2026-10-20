"""
Warm re-engagement drafter.

For leads who opened 2+ times but never replied — generates a niche-specific
bump email with a NEW angle (not a repeat of email 1 or 2), threaded onto
their existing Smartlead conversation.

Key voice rules:
  - Acknowledge they've been on the list, without being weird about tracking
  - Pivot to a DIFFERENT angle than the original magnet
  - Inline GHL booking link (low-friction)
  - No fault admission, no apology
  - 4-6 short sentences total
"""
import json
from . import llm, smartlead_io, signal_enricher

BOOKING_URL = "https://api.leadconnectorhq.com/widget/bookings/flowqualificationcall"


# Per-niche re-engagement angles. Each is a DIFFERENT cut of the data than
# the original magnet, so the email reads as new value, not a repeat.
NICHE_ANGLES = {
    "WEALTH": {
        "original_offer": "25 people in their city who just hit a liquidity event",
        "new_angle":      "the 3 advisors winning these accounts in their zip code, plus what their pages do that theirs doesn't",
        "angle_reason":   "Same data, different cut: competitive intel instead of prospect list. Shows them what they're losing TO, not just what they could win.",
    },
    "MCA": {
        "original_offer": "75 first-position merchants in their territory",
        "new_angle":      "30 merchants who funded 60-90 days ago and are entering reactivation window (different segment than first-position)",
        "angle_reason":   "Reactivation merchants close 3-5x faster than cold first-position. Smaller list, hotter intent.",
    },
    "COMMLOAN": {
        "original_offer": "100 SBA-eligible businesses pre-screened on 7 criteria",
        "new_angle":      "the 15 businesses in their metro approaching SBA refi window (existing loans 18-24 months old, prime rate exposure)",
        "angle_reason":   "Refi-window leads close on incoming need, not outbound pitch. Higher close rate.",
    },
}


SYSTEM = """You are drafting a single re-engagement email on behalf of Neal Thakkar
(Founder, FlowOperations.ai) to a cold-email lead who has opened multiple times
without replying. They are interested but undecided. Your job: pivot to a NEW
angle that gives them a different reason to engage.

ABSOLUTE RULES:

1. NEVER acknowledge open tracking. Don't say "I noticed you opened" or "saw you
   read the email." That reads as creepy stalking. Skip the meta-comment entirely.

2. PIVOT to a new angle. Do NOT repeat the original offer. Use the new_angle the
   user supplies.

3. NO apology, NO "circling back," NO "wanted to follow up" — these are corporate
   filler that signals weakness.

4. Inline booking link with low-friction CTA. End with a one-liner offering
   the link AND a reply-with-time fallback.

5. Sign off with just "Neal" on its own line.

6. 4 to 6 short sentences. Brevity wins.

7. NO em-dashes, NO en-dashes. Use periods or commas.

8. Bar-test every line: would Neal say this at a bar to someone in this person's
   job? If no, rewrite.

STRUCTURE:

- Sentence 1: Direct pivot statement. E.g., "Different angle on this." or
  "Switching cuts. Here's what most {{role}} actually want first."
- Sentence 2-3: Describe the new offer specifically. Concrete number, concrete
  deliverable.
- Sentence 4: One-line "why this matters" tied to a real industry pattern.
- Sentence 5: CTA — booking link inline + reply fallback.
- Sentence 6: Sign-off "Neal".

OUTPUT (JSON only, no markdown):
{
  "subject": "(re)thinking the {{first_name}} angle"  // OR a short specific subject,
  "body_plain": "the email body with newlines",
  "reasoning": "one sentence on why this works"
}
"""


def draft_reengagement(
    lead_first_name: str,
    lead_company: str,
    lead_role: str,
    lead_city: str,
    niche: str,
    open_count: int,
    booking_url: str = BOOKING_URL,
    signals: dict | None = None,
    website: str = "",
    state: str = "",
) -> dict:
    """Draft a warm re-engagement email with optional signal context."""
    angle = NICHE_ANGLES.get(niche)
    if not angle:
        return {"_error": True, "reason": f"No re-engagement angle defined for niche: {niche}"}

    # Pull signals if not provided
    if signals is None:
        try:
            signals = signal_enricher.enrich({
                "company": lead_company,
                "website": website,
                "city":    lead_city,
                "state":   state,
                "niche":   niche,
            })
        except Exception as e:
            print(f"  [enrich-warn] {e}")
            signals = {}
    signal_block = signal_enricher.format_signals_for_council(signals or {})

    user = f"""LEAD CONTEXT
- First name: {lead_first_name or "(unknown)"}
- Company:    {lead_company or "(unknown)"}
- Role:       {lead_role or "(unknown)"}
- City:       {lead_city or "(unknown)"}
- Niche:      {niche}
- Open count: {open_count} (they've been reading without replying)

{signal_block}

ORIGINAL OFFER (what we already pitched them — DO NOT REPEAT)
{angle['original_offer']}

NEW ANGLE (this is what your email should describe)
{angle['new_angle']}

WHY THE NEW ANGLE WORKS
{angle['angle_reason']}

BOOKING LINK (must appear verbatim)
{booking_url}

REQUIRED — if SIGNALS are present above (not "no specific signals available"),
the OPENING TWO SENTENCES of the email MUST reference at least one specific
signal data point (the actual number from Form D filings, the specific tool
their site is running, etc.). Do NOT bury the signal in the middle. Lead with
it. This is the difference between an email that ships and one that goes back
to drafts.

If the SIGNALS block says "no specific signals available," skip them and lean
on the new-angle pivot.

Draft the re-engagement email now. Return ONLY the JSON object."""

    result = llm.call(
        system=SYSTEM,
        user=user,
        model=llm.GEMINI_FLASH,
        max_tokens=700,
        temperature=0.75,
    )
    if result.get("_error"):
        return {"_error": True, "details": result.get("details")}

    try:
        parsed = llm.parse_json_from_text(result["text"])
    except Exception as e:
        return {"_error": True, "parse_error": str(e), "raw": result["text"][:300]}

    # Voice post-processing (same as auto_reply)
    from .auto_reply import _enforce_voice_post
    parsed["body_plain"] = _enforce_voice_post(parsed.get("body_plain", ""))
    parsed["subject"]    = _enforce_voice_post(parsed.get("subject", ""))

    # Hard safety: confirm booking URL in body
    if booking_url not in parsed.get("body_plain", ""):
        parsed["body_plain"] = parsed.get("body_plain", "") + f"\n\nBook here: {booking_url}"

    parsed["_cost"] = llm.estimate_cost(result["usage"], result["model"])
    return parsed


def batch_draft(warm_leads: list[dict], with_signals: bool = True) -> list[dict]:
    """Draft re-engagement emails for a batch of warm leads."""
    # Pre-fetch all signals in parallel (much faster than sequential per-lead)
    signals_by_email = {}
    if with_signals:
        print(f"  Pulling signals for {len(warm_leads)} leads in parallel...")
        sigs = signal_enricher.enrich_batch([{
            "email":   w["lead_email"],
            "company": w.get("company",""),
            "website": w.get("website","") or "",
            "city":    w.get("city",""),
            "state":   w.get("state",""),
            "niche":   w["niche"],
        } for w in warm_leads], max_workers=8)
        for w, s in zip(warm_leads, sigs):
            signals_by_email[w["lead_email"]] = s if isinstance(s, dict) else {}
        signal_hits = sum(1 for s in signals_by_email.values() if s and not s.get("_error"))
        print(f"  {signal_hits}/{len(warm_leads)} leads got at least one signal")

    drafts = []
    for w in warm_leads:
        d = draft_reengagement(
            lead_first_name=w.get("first_name") or (w.get("lead_name","").split()[0] if w.get("lead_name") else ""),
            lead_company=w.get("company",""),
            lead_role=w.get("title",""),
            lead_city=w.get("city",""),
            niche=w["niche"],
            open_count=w.get("open_count",0),
            signals=signals_by_email.get(w["lead_email"], {}),
            website=w.get("website","") or "",
            state=w.get("state",""),
        )
        drafts.append({
            "lead_email":   w["lead_email"],
            "lead_id":      w.get("lead_id"),
            "campaign_id":  w["campaign_id"],
            "first_name":   w.get("first_name") or "",
            "company":      w.get("company",""),
            "niche":        w["niche"],
            "open_count":   w.get("open_count",0),
            "signals":      signals_by_email.get(w["lead_email"], {}),
            "draft":        d,
        })
    return drafts


def send_reengagement(draft_record: dict) -> tuple[bool, str]:
    """Send one drafted re-engagement onto the lead's existing thread."""
    cid = draft_record["campaign_id"]
    lead_id = draft_record["lead_id"]
    last = smartlead_io.get_last_outbound(cid, lead_id)
    if not last:
        return False, "no outbound message in thread"
    ok, msg = smartlead_io.send_reply(
        campaign_id=cid,
        stats_id=last["stats_id"],
        reply_message_id=last["message_id"],
        to_email=draft_record["lead_email"],
        body_plain=draft_record["draft"]["body_plain"],
        to_first_name=draft_record["first_name"],
        reply_email_body="(warm re-engagement bump)",
    )
    return ok, msg


if __name__ == "__main__":
    # Run batch on /tmp/warm_leads.json
    with open("/tmp/warm_leads.json") as f:
        warm = json.load(f)
    viable = [w for w in warm if w["niche"] in NICHE_ANGLES]
    print(f"Viable leads (WEALTH+MCA+COMMLOAN): {len(viable)} of {len(warm)} total\n")

    drafts = batch_draft(viable)
    with open("/tmp/warm_drafts.json","w") as f:
        json.dump(drafts, f, indent=2, default=str)
    total_cost = sum(d["draft"].get("_cost",0) for d in drafts if not d["draft"].get("_error"))
    errors = sum(1 for d in drafts if d["draft"].get("_error"))
    print(f"Generated {len(drafts)} drafts, {errors} errors")
    print(f"Total cost: ${total_cost:.4f}\n")
    print("SAMPLES:")
    for d in drafts[:5]:
        print("="*70)
        print(f"{d['niche']:<10} {d['first_name']} @ {d['company']}  ({d['open_count']} opens)")
        print("="*70)
        if d["draft"].get("_error"):
            print(f"ERROR: {d['draft']}")
        else:
            print(f"SUBJECT: {d['draft']['subject']}")
            print()
            print(d["draft"]["body_plain"])
        print()
    print(f"\nFull batch saved to /tmp/warm_drafts.json")
