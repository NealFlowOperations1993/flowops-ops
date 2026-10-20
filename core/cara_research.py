"""
Cara Barone research generator (formerly Brutus).

Converts per-lead signals into the playbook's "forwarded from AI research agent"
format. Each block reads like a real internal Slack/email handoff between
Neal and Cara, his AI research agent, citing specific public details about the lead.

The signals come from signal_enricher.py (tech stack, news, Form D, GBP, etc.).
The output is a 3-5 line "Cara" message that goes inside the cold email body.

Forwarded-from identity:
    From: Cara Barone <hello@carabarone.com>
    Sign-off: — Cara

Voice: Internal-comms, casual, fact-dense. NOT salesy. NOT generated-sounding.
"""
from . import llm, signal_enricher

CARA_FROM   = "Cara Barone <hello@carabarone.com>"
CARA_SIGN   = "— Cara"


SYSTEM = """You are Cara Barone, an AI research analyst for Neal Thakkar (Founder, Flow Operations).
You just wrapped a public-records dossier on a target prospect. You're forwarding
your notes to Neal so he can decide whether to reach out.

VOICE RULES (absolute):
- Internal-comms tone. Short. Fact-dense. No marketing language.
- Cite specific public data points (not generic claims).
- If signals are weak, say "Limited public signal, recommend manual check before reach-out."
  Don't fabricate.
- Sign off with "— Cara" on its own line.
- No em-dashes inside the body. Use periods or commas.
- 3 to 5 bullet points max.

OUTPUT FORMAT (return ONLY this — no JSON, no preamble):

Wrapped research on {{company_name}}.

- {{specific bullet, cite the actual data point}}
- {{specific bullet}}
- {{specific bullet}}

{{One-line recommendation: "Strong fit, recommend reach-out." OR
                          "Decent fit, depends on {{specific gap}}." OR
                          "Limited signal. Manual review before reach-out."}}

— Cara
"""


def generate_cara_block(lead: dict, signals: dict | None = None) -> dict:
    """
    Generate the Cara Barone forwarded research block for one lead.

    Returns: {"cara_text": str, "fit_score": int, "_cost": float}
    """
    if signals is None:
        signals = signal_enricher.enrich(lead)

    company = lead.get("company") or lead.get("company_name") or "(unknown company)"
    city    = lead.get("city", "")
    state   = lead.get("state", "")
    niche   = lead.get("niche", "")

    user = f"""TARGET PROSPECT
- Company: {company}
- Niche:   {niche}
- Location: {city}, {state}

SIGNALS CARA PULLED (raw — convert to the forwarded format):
{signal_enricher.format_signals_for_council(signals or {})}

Write the forwarded research block now. Stay in Cara voice. Cite the actual signal data points specifically. Don't invent."""

    result = llm.call(
        system=SYSTEM,
        user=user,
        model=llm.GEMINI_FLASH,
        max_tokens=500,
        temperature=0.5,
    )

    if result.get("_error"):
        return {"_error": True, "details": result.get("details")}

    text = result["text"].strip()
    # Strip code fences if Gemini wrapped them
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text
        text = text.rsplit("```", 1)[0].strip()

    # Voice post-pass: strip em-dashes/en-dashes from BODY, but keep "— Cara" sign-off intact
    body, _, sign = text.rpartition("— Cara")
    body = body.replace("—", ".").replace("–", ",")
    text = (body + "— Cara" + sign) if sign != text else text  # preserve sign-off if found

    # Crude fit score extraction (look for "/10" pattern, default 7)
    import re
    m = re.search(r"(\d+)\s*/\s*10", text)
    fit = int(m.group(1)) if m else 7

    return {
        "cara_text": text,
        "fit_score":   fit,
        "_cost":       llm.estimate_cost(result["usage"], result["model"]),
    }


def wrap_forwarded(cara_text: str, lead_first_name: str = "") -> str:
    """Wrap the Cara block in the playbook's exact forwarded format."""
    name = lead_first_name or "{first_name}"
    return f"""---------- Forwarded ----------
From: {CARA_FROM}
Subject: Reach out to {name} - Quick Start fit
To: Neal

{cara_text}"""


# Backwards-compat shims so existing imports keep working
def generate_brutus_block(lead: dict, signals: dict | None = None) -> dict:
    """Deprecated alias for generate_cara_block. Kept for backwards compatibility."""
    r = generate_cara_block(lead, signals)
    if "cara_text" in r:
        r["brutus_text"] = r["cara_text"]  # legacy key
    return r


if __name__ == "__main__":
    test_leads = [
        {"company": "Lion's Share Wealth", "website": "lionssharewealth.com",
         "city": "Phoenix", "state": "Arizona", "niche": "WEALTH"},
        {"company": "Grandiose Capital", "website": "grandiosecapital.com",
         "city": "Miami", "state": "Florida", "niche": "MCA"},
    ]
    for lead in test_leads:
        print(f"\n{'='*70}")
        print(f"Cara block for {lead['company']}")
        print(f"{'='*70}")
        r = generate_cara_block(lead)
        if r.get("_error"):
            print(f"ERROR: {r}")
            continue
        block = wrap_forwarded(r["cara_text"], lead_first_name="Palmer")
        print(block)
        print(f"\n--- fit_score: {r['fit_score']} | cost: ${r['_cost']:.4f} ---")
