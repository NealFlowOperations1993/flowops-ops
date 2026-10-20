"""
Judge loader + voting logic.
Each judge picks the best candidate for one dimension (opener, pain, cta).
Coherence judge takes the picked-trio and approves/rejects the combined output.
"""
import json
from pathlib import Path
from typing import Any

JUDGES_DIR = Path(__file__).parent.parent / "judges"
HUMAN_VOICE_PATH = Path(__file__).parent.parent / "HUMAN_VOICE.md"


def _load_human_voice() -> str:
    if HUMAN_VOICE_PATH.exists():
        return HUMAN_VOICE_PATH.read_text()
    return ""


def load(name: str) -> str:
    """Load a judge prompt by file stem (e.g. 'opener_judge')."""
    path = JUDGES_DIR / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(f"Judge not found: {path}")
    body = path.read_text()
    human_voice = _load_human_voice()
    return (
        f"# CANONICAL VOICE RULES (auto-disqualify any candidate violating these)\n\n"
        f"{human_voice}\n\n"
        f"---\n\n"
        f"# YOUR JUDGING ROLE\n\n"
        f"{body}"
    )


def build_judge_user_prompt(dimension: str, candidates: list[str]) -> str:
    """
    dimension: 'opener', 'pain', or 'cta'
    candidates: list of strings (one per persona)
    """
    numbered = "\n".join(
        f"[CANDIDATE {i}]\n{text}\n" for i, text in enumerate(candidates)
    )
    return (
        f"Judge these {len(candidates)} {dimension} candidates.\n\n"
        f"{numbered}\n"
        f"Output strict JSON per the schema above. Be ruthless about disqualifying banned-word violations and AI tells."
    )


def build_coherence_user_prompt(opener: str, pain: str, cta: str) -> str:
    return (
        "Judge the coherence of this final picked email body.\n\n"
        f"[OPENER]\n{opener}\n\n"
        f"[PAIN]\n{pain}\n\n"
        f"[CTA]\n{cta}\n\n"
        "Output strict JSON per the schema above. Approve liberally; only block real coherence problems."
    )
