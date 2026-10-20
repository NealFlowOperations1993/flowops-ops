"""
Auto-reply drafter for POSITIVE inbound replies.

Reads the lead's reply + original send context + niche, drafts a contextual
response in Neal's voice that:
  1. Acknowledges what they said specifically (no generic "great hearing from you")
  2. Restates the offer in one sentence
  3. Drops the GHL booking link inline
  4. Keeps the door open if they don't want to book ("or reply with what works")
  5. Closes with "Neal"

Output goes straight to Smartlead reply API. Neal is not in the loop.

Voice rules enforced:
  - No em-dashes, no jargon, no apology/hedge language
  - Bar test: would Neal say this at a bar to someone in this person's job?
  - Never invents specifics about the lead
"""
import json
from pathlib import Path
from . import llm

# GHL booking link — the human-friendly slug
BOOKING_URL = "https://api.leadconnectorhq.com/widget/bookings/flowqualificationcall"

HUMAN_VOICE_PATH = Path(__file__).parent.parent / "HUMAN_VOICE.md"


def _load_voice_rules() -> str:
    """Load HUMAN_VOICE.md so the drafter inherits the latest voice rules."""
    try:
        return HUMAN_VOICE_PATH.read_text()
    except Exception:
        return "(voice rules not found)"


SYSTEM_TEMPLATE = """You are drafting a single email reply on behalf of Neal Thakkar
(Founder, FlowOperations.ai). Neal sells AI-built lead-gen systems ("Marketing Trident")
to service-based founders. Your job: turn a POSITIVE inbound reply into a booked call.

THE VOICE RULES (these are absolute — auto-fail if you violate them):

{voice_rules}

THE STRUCTURE — every auto-reply must:

1. ONE sentence that responds to what they actually said. Be specific to their reply text.
2. ONE sentence that restates the offer / next step in human language.
3. ONE inline link to the booking page (text varies, link is always the URL passed in).
4. ONE optional "or reply with [X]" fallback so they have a non-Calendar option.
5. Sign off with just "Neal" on its own line.

LENGTH: 4 to 7 short sentences total. Brevity = conversion.

BANNED in auto-replies specifically:
- "Great to hear from you" / "thanks for reaching out" / "appreciate the reply" (lazy openers)
- "Looking forward to" / "excited to" (filler enthusiasm)
- Any sentence longer than 20 words
- Any disclaimer about what we can or can't do
- Any apology for anything
- "Just a heads up" / "fyi" / "quick note" (throat-clearing)
- Em-dashes (—) and en-dashes (–). Use periods, commas, or short separate sentences instead.

Return ONLY valid JSON, no markdown:
{{
  "subject": "Re: <original subject — pass through unchanged>",
  "body_plain": "the email body, plain text with newlines",
  "reasoning": "one sentence on why this reply works"
}}
"""


def draft_reply(
    inbound_text: str,
    original_subject: str,
    lead_first_name: str = "",
    lead_company: str = "",
    niche: str = "",
    niche_offer_summary: str = "",
    booking_url: str = BOOKING_URL,
) -> dict:
    """
    Returns: {"subject", "body_plain", "reasoning", "_cost"}
    """
    voice_rules = _load_voice_rules()
    system = SYSTEM_TEMPLATE.format(voice_rules=voice_rules)

    user = f"""LEAD CONTEXT
- First name: {lead_first_name or "(unknown)"}
- Company:    {lead_company or "(unknown)"}
- Niche:      {niche or "(unknown)"}

ORIGINAL OUTBOUND SUBJECT
{original_subject}

WHAT WE OFFERED IN THE ORIGINAL EMAIL (one sentence)
{niche_offer_summary or "Free niche-specific lead list, delivered in 24 hours."}

WHAT THE LEAD JUST REPLIED
---
{inbound_text.strip()[:2000]}
---

BOOKING LINK (must appear in body verbatim)
{booking_url}

Draft the reply now. Return ONLY the JSON object."""

    result = llm.call(
        system=system,
        user=user,
        model=llm.GEMINI_FLASH,
        max_tokens=800,
        temperature=0.7,
    )

    if result.get("_error"):
        return {"_error": True, "details": result.get("details")}

    try:
        parsed = llm.parse_json_from_text(result["text"])
    except Exception as e:
        return {"_error": True, "parse_error": str(e), "raw": result["text"][:500]}

    parsed["_cost"] = llm.estimate_cost(result["usage"], result["model"])

    # Hard safety: confirm booking URL made it into body
    if booking_url not in parsed.get("body_plain", ""):
        parsed["body_plain"] = parsed.get("body_plain", "") + f"\n\nBook here: {booking_url}"
        parsed["_booking_link_appended"] = True

    # Post-process: strip banned characters per HUMAN_VOICE.md
    parsed["body_plain"] = _enforce_voice_post(parsed.get("body_plain", ""))
    parsed["subject"]    = _enforce_voice_post(parsed.get("subject", ""))

    return parsed


# Banned characters and phrases that MUST be auto-stripped before send.
_EM_DASH_REPLACEMENTS = {
    "—": ".",   # em-dash → period
    "–": ",",   # en-dash → comma
    # NOTE: ASCII " - " is left alone — it's a legitimate separator in subject lines
    # like "financial advisors in Chicago - quick offer" and shouldn't be rewritten.
}

_BANNED_PHRASES = [
    "great to hear from you",
    "great hearing from you",
    "thanks for reaching out",
    "thanks for the reply",
    "appreciate the reply",
    "looking forward to",
    "excited to",
    "just a heads up",
    "quick heads up",
    "no pitch after",
    "no follow up",
    "no follow-up",
    "no strings",
    "this isn't a sales",
    "i hope this finds you well",
    "i hope you're doing well",
]


def _enforce_voice_post(text: str) -> str:
    """Final-pass voice enforcement. Strips banned punctuation and flags banned phrases."""
    if not text:
        return text
    import re
    out = text
    for bad, good in _EM_DASH_REPLACEMENTS.items():
        out = out.replace(bad, good)
    # Collapse artifacts from em-dash replacement: " . " -> ". " and " , " -> ", "
    out = re.sub(r"\s+\.\s+", ". ", out)
    out = re.sub(r"\s+,\s+", ", ", out)
    # Collapse double spaces (but preserve newlines/paragraphs)
    out = re.sub(r"[ \t]{2,}", " ", out)
    # Phrase scan: log surviving banned phrases (don't mangle the text)
    lower = out.lower()
    for phrase in _BANNED_PHRASES:
        if phrase in lower:
            print(f"  [voice-warn] banned phrase survived: '{phrase}'")
    return out


# Niche → one-line offer summary (used as context for the drafter)
NICHE_OFFERS = {
    "MCA":         "75 first-position merchants in their territory, no stacks, delivered in 24 hours.",
    "MORTGAGE":    "50 borrowers from their dead-lead pile who'd save $400+/mo by refi'ing today.",
    "FINANCIAL":   "The 7 advisors in their city stealing their Google clicks, plus the 3 page fixes that move them into the top 5.",
    "WEALTH":      "A 90-day map of every Form D raise, $2M+ property deal, and business sale in their metro.",
    "COMMERCIAL_LOAN": "100 SBA-eligible growing businesses in their metro, pre-screened on 7 SBA criteria.",
    "FUNDING":     "50 bankable-looking owners in their metro, scored on 8 public signals.",
    "AGENCY":      "The 4 to 6 of their clients who are about to fire them, with the signals to prove it.",
    "MEDSPA":      "Where their no-shows are leaking 30-60% in the 48-hour pre-appointment window.",
    "PI_LAW":      "A 90-day injury and competitor-ad-spend pulse for their metro.",
    "BIZ_LAW":     "(TBD)",
    "TAX_RES":     "(TBD)",
    "IT_MSP":      "(TBD)",
}


if __name__ == "__main__":
    # Smoke test on Ralph's actual reply
    print("=" * 70)
    print("Auto-reply test: Ralph (MCA)")
    print("=" * 70)
    r = draft_reply(
        inbound_text="Sure",
        original_subject="mca brokers in Fort Lauderdale - quick offer",
        lead_first_name="Ralph",
        lead_company="First Choice Debt Solutions",
        niche="MCA",
        niche_offer_summary=NICHE_OFFERS["MCA"],
    )
    if r.get("_error"):
        print("ERROR:", r)
    else:
        print(f"SUBJECT: {r['subject']}")
        print(f"\nBODY:\n{r['body_plain']}")
        print(f"\nREASONING: {r.get('reasoning')}")
        print(f"COST: ${r.get('_cost', 0):.5f}")

    print("\n" + "=" * 70)
    print("Auto-reply test: 'what's the catch?' (FINANCIAL)")
    print("=" * 70)
    r2 = draft_reply(
        inbound_text="what's the catch? sounds too good",
        original_subject="financial advisors in Chicago - quick offer",
        lead_first_name="Tom",
        lead_company="Wintrust Wealth",
        niche="FINANCIAL",
        niche_offer_summary=NICHE_OFFERS["FINANCIAL"],
    )
    if r2.get("_error"):
        print("ERROR:", r2)
    else:
        print(f"SUBJECT: {r2['subject']}")
        print(f"\nBODY:\n{r2['body_plain']}")
        print(f"COST: ${r2.get('_cost', 0):.5f}")
