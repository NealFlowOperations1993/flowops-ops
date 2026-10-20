"""
Inbound reply classifier. One Haiku call, ~200ms, ~$0.0002 per reply.

Classes:
  POSITIVE   - wants to engage, asks question, says "yes/sure/send it/interested"
  NEUTRAL    - vague, "tell me more", "maybe later", needs human nudge
  NEGATIVE   - "not interested", "remove me", "wrong person"
  OOO        - out of office autoresponder
  UNSUBSCRIBE - explicit unsubscribe request

Returns: {"label": str, "confidence": 0-1, "reasoning": str, "auto_reply_safe": bool}
"""
import json
from . import llm

SYSTEM = """You are a cold-email reply classifier for a B2B sales pipeline.

Classify the inbound reply into exactly ONE of these labels:

POSITIVE — Lead is engaging. Examples: "sure", "yes send it", "interested", "tell me what you have",
           "what's the catch", "how does it work", "send the list", "let's chat", "what's the price",
           any question about the offer, any agreement to next step.

NEUTRAL  — Vague, polite brush-off, or needs human nudge. Examples: "not right now", "maybe later",
           "circle back in Q3", "I'll think about it", "send info I'll review", forwarded to someone else.

NEGATIVE — Clear no. Examples: "not interested", "stop", "wrong person", "don't email me", angry tone.

OOO      — Out-of-office autoresponder. Vacation, leave, returning [date], traveling.

UNSUBSCRIBE — Explicit removal request. "unsubscribe", "remove me from your list", "opt me out".

Return ONLY valid JSON, no markdown fences, no commentary:
{
  "label": "POSITIVE" | "NEUTRAL" | "NEGATIVE" | "OOO" | "UNSUBSCRIBE",
  "confidence": 0.0-1.0,
  "reasoning": "one sentence",
  "auto_reply_safe": true | false
}

auto_reply_safe rules:
- POSITIVE with confidence >= 0.75 → true
- Everything else → false (Neal handles manually or system ignores)
"""


def classify(reply_text: str, original_subject: str = "", lead_email: str = "") -> dict:
    """
    Classify a single inbound reply.
    Returns: {"label", "confidence", "reasoning", "auto_reply_safe", "_cost"}
    """
    user = f"""Original email subject: {original_subject or "(unknown)"}
From: {lead_email or "(unknown)"}

--- REPLY TEXT ---
{reply_text.strip()[:2000]}
--- END REPLY ---

Classify."""

    result = llm.call(
        system=SYSTEM,
        user=user,
        model=llm.GEMINI_FLASH,
        max_tokens=400,
        temperature=0.1,
    )

    if result.get("_error"):
        return {
            "label": "NEUTRAL",
            "confidence": 0.0,
            "reasoning": f"classifier_error: {result.get('details')}",
            "auto_reply_safe": False,
            "_cost": 0.0,
            "_error": True,
        }

    try:
        parsed = llm.parse_json_from_text(result["text"])
    except Exception as e:
        return {
            "label": "NEUTRAL",
            "confidence": 0.0,
            "reasoning": f"parse_error: {e}",
            "auto_reply_safe": False,
            "_cost": 0.0,
            "_error": True,
        }

    parsed["_cost"] = llm.estimate_cost(result["usage"], result["model"])
    parsed["_raw"] = result["text"]

    # Safety override — only auto-reply on high-confidence POSITIVE
    if parsed.get("label") != "POSITIVE" or parsed.get("confidence", 0) < 0.75:
        parsed["auto_reply_safe"] = False

    return parsed


if __name__ == "__main__":
    # Quick smoke test
    samples = [
        ("Sure", "mca brokers in Fort Lauderdale - quick offer"),
        ("Not interested, please remove me", "financial advisors in Chicago - quick offer"),
        ("I'm out of office until May 20, will respond then", "mortgage brokers in Kingwood - quick offer"),
        ("send it", "mca brokers in Fort Lauderdale - quick offer"),
        ("what's the catch? sounds too good", "funding consultants in Dallas - quick offer"),
        ("maybe later, swamped right now", "med spa marketing"),
        ("unsubscribe", "anything"),
    ]
    print(f"{'REPLY':<55}{'LABEL':<14}{'CONF':>6}  SAFE")
    print("-" * 90)
    for text, subj in samples:
        r = classify(text, subj)
        print(f"{text[:54]:<55}{r['label']:<14}{r.get('confidence',0):>6.2f}  {r['auto_reply_safe']}")
