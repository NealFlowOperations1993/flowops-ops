"""
Pre-call brief generator.

Triggered when GHL booking webhook fires (or run manually with lead email).

Pulls:
  1. Lead data from Smartlead (custom fields, niche, contact info)
  2. Full email thread (what we sent, what they replied)
  3. Personalization data (the 9-key magnet pitch)
  4. Original Apollo/Acquisity context (revenue, employees, signals if any)

Drafts:
  - 1-page Slack brief Neal reads 30 min before the call
  - Key talking points
  - The specific magnet promise they responded to
  - Recommended frame for the call

Cost: ~$0.01 per brief. Latency: ~5 sec.
"""
import json
import re
from . import llm, smartlead_io


SYSTEM = """You are writing a 1-page pre-call brief for Neal Thakkar (Founder, FlowOperations.ai)
30 minutes before a discovery call. He needs to walk in knowing exactly:

1. Who they are (name, company, role, location)
2. What email of ours hooked them (subject line + which sequence position)
3. What we promised them (the specific magnet)
4. What they said back (verbatim, short quote)
5. The frame for the first 60 seconds of the call
6. The specific Trident angle most relevant to their niche
7. 3 questions to ask early to qualify them on revenue/team-size/current-stack

Write it like a war-room one-pager. Direct. No fluff. No "build rapport" or
"discuss their needs" generic advice. Neal already knows how to have a sales conversation.
The brief should give him intel he doesn't have.

OUTPUT FORMAT (markdown, exactly this structure):

```
# Call Brief: <First Name> <Last Name> @ <Company>

**When:** <time>
**Where:** <location of business>
**Role:** <title>
**Niche:** <niche>

## What hooked them
- Sequence: <sequence_number> of our <niche> campaign
- Subject: "<original subject>"
- Magnet promised: <one sentence>

## What they said
> <verbatim quote of their reply, max 2 sentences>

## The frame (first 60 seconds)
<one sentence, Neal-voice, what to say first>

## Trident angle for this niche
<two sentences on which Trident pillar applies most to their pain — Intelligence Layer, GHL Provisioner, or both — and why>

## 3 qualifying questions
1. <revenue/scale-anchor question>
2. <current-stack question>
3. <decision-maker / urgency question>

## Likely objections
- <obj 1>: <one-line response>
- <obj 2>: <one-line response>
```

Voice rules: no em-dashes, no jargon, no apology, no fluff. Bar-test every line.
"""


def render_brief(
    lead_email: str,
    campaign_id: int,
    lead_id: int,
    call_time: str = "TBD",
) -> dict:
    """
    Build the 1-page brief. Returns:
      {"markdown": str, "lead_data": {...}, "_cost": float}
    """
    # 1. Pull thread
    msgs = smartlead_io.get_lead_thread(campaign_id, lead_id)
    sent = [m for m in msgs if (m.get("type") or m.get("email_type") or "").upper() == "SENT"]
    replies = [m for m in msgs if (m.get("type") or m.get("email_type") or "").upper() == "REPLY"]

    last_reply = replies[-1] if replies else None
    reply_text = ""
    if last_reply:
        body = last_reply.get("email_body", "") or last_reply.get("body", "")
        # Strip HTML + signature
        body = re.sub(r"<[^>]+>", " ", body)
        body = re.sub(r"\s+", " ", body).strip()
        # Pull just what's above the "From:" reply header
        if "From:" in body:
            body = body.split("From:")[0].strip()
        reply_text = body[:400]

    last_sent = sent[-1] if sent else None
    last_subject = (last_sent or {}).get("subject", "") or ""
    seq_num = (last_sent or {}).get("sequence_number", "?")

    # 2. Pull lead custom fields
    try:
        lead_lookup = smartlead_io.get_lead_by_email(lead_email, campaign_id)
        lead_data = (lead_lookup or {}).get("lead_data", {})
    except Exception:
        lead_data = {}
    cf = lead_data.get("custom_fields", {}) if isinstance(lead_data.get("custom_fields"), dict) else {}

    context = {
        "first_name":   lead_data.get("first_name", ""),
        "last_name":    lead_data.get("last_name", ""),
        "email":        lead_email,
        "company":      lead_data.get("company_name", ""),
        "website":      lead_data.get("website", ""),
        "title":        cf.get("title", "") or lead_data.get("title", ""),
        "city":         cf.get("city", "") or lead_data.get("location", ""),
        "state":        cf.get("state", ""),
        "niche":        cf.get("niche", "UNKNOWN"),
        "sequence_num": seq_num,
        "original_subject": last_subject,
        "magnet_promised":  cf.get("personalized_cta", "") or cf.get("personalized_cta_2", ""),
        "reply_text":   reply_text,
        "call_time":    call_time,
    }

    user = f"""Build the call brief from this data.

LEAD
- Name:    {context['first_name']} {context['last_name']}
- Email:   {context['email']}
- Role:    {context['title']}
- Company: {context['company']}
- Website: {context['website']}
- Location: {context['city']}, {context['state']}
- Niche:   {context['niche']}

THREAD
- Sequence position when they replied: email {context['sequence_num']}
- Original subject they responded to: "{context['original_subject']}"
- Magnet we promised: {context['magnet_promised']}

THEIR REPLY (verbatim)
{context['reply_text']}

CALL TIME: {context['call_time']}

Render the brief now."""

    result = llm.call(
        system=SYSTEM,
        user=user,
        model=llm.GEMINI_FLASH,
        max_tokens=1500,
        temperature=0.4,
    )

    if result.get("_error"):
        return {"_error": True, "details": result.get("details")}

    text = result["text"].strip()
    # Strip code fences if Haiku wrapped them
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text
        text = text.rsplit("```", 1)[0].strip()

    return {
        "markdown": text,
        "lead_data": context,
        "_cost": llm.estimate_cost(result["usage"], result["model"]),
    }


if __name__ == "__main__":
    # Run against Jon at Pasture Wealth (the real positive reply we surfaced today)
    print("Generating call brief for Jon at Pasture Wealth...\n")
    brief = render_brief(
        lead_email="jon@pasturewealth.life",
        campaign_id=3263730,
        lead_id=3725290181,
        call_time="Tuesday May 12, 11:00am CT",
    )
    if brief.get("_error"):
        print("ERROR:", brief)
    else:
        print(brief["markdown"])
        print(f"\n--- cost: ${brief.get('_cost', 0):.4f} ---")
