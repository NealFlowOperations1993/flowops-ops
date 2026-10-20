"""
Council Mini — 3 personas + 1 judge for opener generation.

Cheap version of full Council. Per lead:
  - 3 opener candidates from 3 distinct voices (Analyst / Founder-peer / Direct)
  - 1 judge call ranks them with reasoning, returns the winner

Cost per lead: ~$0.0015 (3 × Gemini Flash gen + 1 × Sonnet 4.5 judge)
At 400 leads/day = ~$0.60/day = ~$18/mo (within $50/day cap easily)

Drop-in replacement for the single-shot opener in personalize_new_niches.py.
Imported as:
    from council_mini import best_opener
    opener = best_opener(lead_context_dict)
"""
import json
import os
import re
import time
import urllib.request
import urllib.error

OR_KEY = os.environ["OPENROUTER_API_KEY"]
OR_URL = "https://openrouter.ai/api/v1/chat/completions"

# Three persona prompts — each writes ONE opener line for the lead.
# If lead_ctx contains "signals" (from signal_enricher), use them.
PERSONAS = {
    "ANALYST": """You are a research analyst writing the opening of a cold email. Voice: fact-dense, neutral, no sales language. If "signals" are provided, lead with one specific public data point from them. Otherwise cite city + niche. Length: ONE sentence, max 22 words. No greeting like "Hi" — just the opening sentence itself. PRIORITY: if signals contain own_site_recent_content or company_specific_news, your opener MUST reference that specific post/event/topic naturally — cite the actual subject. NEVER invent events not present in the signals.""",

    "FOUNDER_PEER": """You are a founder writing to another founder. Voice: casual, direct, peer-to-peer. If "signals" are provided, reference one in your opener naturally — like you noticed it. Otherwise acknowledge their company by name. Length: ONE sentence, max 22 words. No greeting like "Hi" — just the opening sentence. PRIORITY: if signals contain own_site_recent_content or company_specific_news, your opener MUST reference that specific post/event/topic naturally — cite the actual subject. NEVER invent events not present in the signals.""",

    "DIRECT": """You are writing a Hormozi-style cold email opener. Voice: extremely direct, blunt, no warm-up. If "signals" suggest a recent trigger event (funding, hiring, M&A, traffic spike), open with the implication of that. Otherwise state a hard truth about their niche. Length: ONE sentence, max 18 words. No greeting — just the opening sentence. PRIORITY: if signals contain own_site_recent_content or company_specific_news, your opener MUST reference that specific post/event/topic naturally — cite the actual subject. NEVER invent events not present in the signals."""
}

JUDGE = """You are a senior cold-email copywriter ranking 3 opener candidates for the SAME prospect.

Score each opener 1-10 on:
  - SPECIFICITY (1-10): how concrete + personalized vs template
  - HUMAN_FEEL (1-10): how human vs AI-generated
  - HOOK (1-10): how likely the recipient reads sentence 2

Output ONLY valid JSON:
{
  "scores": [
    {"id": "ANALYST", "specificity": N, "human_feel": N, "hook": N, "total": N},
    {"id": "FOUNDER_PEER", "specificity": N, "human_feel": N, "hook": N, "total": N},
    {"id": "DIRECT", "specificity": N, "human_feel": N, "hook": N, "total": N}
  ],
  "winner": "ANALYST" | "FOUNDER_PEER" | "DIRECT",
  "winner_text": "the actual opener text of the winner",
  "reasoning": "1 sentence why"
}"""


def _post(model, system, user, max_tokens=300, temperature=0.7, timeout=45):
    body = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
    }
    headers = {"Authorization": f"Bearer {OR_KEY}", "Content-Type": "application/json"}
    req = urllib.request.Request(OR_URL, data=json.dumps(body).encode(),
        headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {"_error": True, "code": e.code, "body": e.read().decode()[:200]}
    except Exception as e:
        return {"_error": True, "msg": str(e)[:200]}


def _gen_opener(persona_key, lead_ctx):
    """Generate one opener candidate from one persona."""
    system = PERSONAS[persona_key]
    user = json.dumps(lead_ctx)
    r = _post("google/gemini-2.5-flash-lite", system, user, max_tokens=120, temperature=0.8)
    if r.get("_error"):
        return None
    try:
        return r["choices"][0]["message"]["content"].strip()
    except Exception:
        return None


def _judge(candidates, lead_ctx):
    """Score 3 candidates, return winner."""
    user = json.dumps({
        "lead": lead_ctx,
        "candidates": [{"id": k, "text": v} for k, v in candidates.items() if v],
    })
    r = _post("anthropic/claude-sonnet-4.5", JUDGE, user, max_tokens=500, temperature=0.2)
    if r.get("_error"):
        return None
    try:
        text = r["choices"][0]["message"]["content"].strip()
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```\s*$", "", text)
        m = re.search(r"\{[\s\S]*\}", text)
        return json.loads(m.group(0)) if m else None
    except Exception:
        return None


def best_opener(lead_ctx: dict) -> dict:
    """
    Generate 3 opener candidates and pick the winner.
    Returns: {"opener": str, "winner_id": str, "scores": list, "reasoning": str}

    On any failure, falls back to the FOUNDER_PEER candidate (or empty string).
    """
    candidates = {}
    for p in PERSONAS.keys():
        candidates[p] = _gen_opener(p, lead_ctx)

    # If we got 0 candidates, total fail
    if not any(candidates.values()):
        return {"opener": "", "winner_id": "NONE", "error": "all_personas_failed"}

    # Judge
    result = _judge(candidates, lead_ctx)
    if not result or not isinstance(result, dict):
        # Fallback: pick the first non-empty candidate
        for k, v in candidates.items():
            if v:
                return {"opener": v, "winner_id": k, "scores": [], "reasoning": "fallback (judge failed)"}
        return {"opener": "", "winner_id": "NONE", "error": "judge_failed"}

    winner_id = result.get("winner")
    winner_text = result.get("winner_text") or candidates.get(winner_id, "")
    return {
        "opener":   winner_text,
        "winner_id": winner_id,
        "scores":   result.get("scores", []),
        "reasoning": result.get("reasoning", ""),
        "candidates": candidates,
    }


if __name__ == "__main__":
    # Smoke test
    lead = {
        "first_name": "Stefan",
        "company": "Mercer Wealth Management",
        "city": "Louisville",
        "niche": "wealth management firm",
    }
    print("=== Council Mini smoke test ===")
    r = best_opener(lead)
    print(f"\nWinner: {r['winner_id']}")
    print(f"Opener: {r['opener']}")
    print(f"\nReasoning: {r.get('reasoning','')}")
    print(f"\nAll candidates:")
    for k, v in (r.get('candidates') or {}).items():
        print(f"  {k}: {v}")
    print(f"\nScores:")
    for s in r.get('scores', []):
        print(f"  {s}")
