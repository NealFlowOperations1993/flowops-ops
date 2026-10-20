"""
Persona loader. Reads .md files from /personas/ and extracts the SYSTEM PROMPT block.
Each persona is a config file, not code — non-engineers can tune voice without redeploying.
"""
import os
import glob
import re
from pathlib import Path

PERSONAS_DIR = Path(__file__).parent.parent / "personas"
HUMAN_VOICE_PATH = Path(__file__).parent.parent / "HUMAN_VOICE.md"


def _extract_system_prompt(markdown: str) -> str:
    """Pull the section starting after '## SYSTEM PROMPT' and ending at next '## EXAMPLES'."""
    m = re.search(
        r"## SYSTEM PROMPT\s*\n(.*?)(?=^## EXAMPLES|\Z)",
        markdown,
        re.DOTALL | re.MULTILINE,
    )
    if m:
        return m.group(1).strip()
    return markdown.strip()


def _load_human_voice() -> str:
    """The canonical voice rules every persona must follow."""
    if HUMAN_VOICE_PATH.exists():
        return HUMAN_VOICE_PATH.read_text()
    return ""


def load_all() -> list[dict]:
    """
    Returns list of {id, name, system_prompt, file_path}.
    Sorted by filename (so 01_, 02_, 03_ ordering is preserved).
    """
    files = sorted(glob.glob(str(PERSONAS_DIR / "*.md")))
    human_voice = _load_human_voice()
    personas = []
    for f in files:
        name = Path(f).stem
        markdown = Path(f).read_text()
        system = _extract_system_prompt(markdown)
        # Inject HUMAN_VOICE rules at the top so every persona has them
        full_system = (
            f"# CANONICAL VOICE RULES (override anything below if conflict)\n\n"
            f"{human_voice}\n\n"
            f"---\n\n"
            f"# YOUR SPECIFIC PERSONA\n\n"
            f"{system}"
        )
        personas.append({
            "id": name,
            "name": name.split("_", 1)[1].replace("_", " ").title() if "_" in name else name,
            "system_prompt": full_system,
            "file_path": f,
        })
    return personas


def build_user_prompt(lead: dict, niche_context: dict | None = None) -> str:
    """
    Build the user message sent to each persona.
    lead: {company_name, city, state, niche, website, category, ...}
    niche_context: optional {reverse_magnet_name, reverse_magnet_offer, pain_anchor}
    """
    base = {
        "company_name": lead.get("company_name", ""),
        "city": lead.get("city", ""),
        "state": lead.get("state", ""),
        "niche": lead.get("niche", ""),
        "website": lead.get("website", ""),
        "category": lead.get("category", ""),
    }
    if niche_context:
        base["the_offer_we_make"] = niche_context.get("reverse_magnet_offer", "")
        base["pain_anchor_we_can_reference"] = niche_context.get("pain_anchor", "")

    return (
        "Generate the 9-key personalization JSON for this lead.\n\n"
        f"LEAD CONTEXT:\n{__import__('json').dumps(base, indent=2)}\n\n"
        "Output ONLY the JSON object, nothing else. Schema:\n"
        '{\n'
        '  "email1_opener": "...",\n'
        '  "email1_pain": "...",\n'
        '  "email1_cta": "...",\n'
        '  "email2_opener": "...",\n'
        '  "email2_pain": "...",\n'
        '  "email2_cta": "...",\n'
        '  "email3_opener": "...",\n'
        '  "email3_pain": "...",\n'
        '  "email3_cta": "..."\n'
        '}'
    )
