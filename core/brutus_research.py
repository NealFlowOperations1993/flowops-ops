"""
DEPRECATED — this module is now a thin shim over core.cara_research.

The AI research agent persona was renamed from "Brutus" to "Cara Barone"
(hello@carabarone.com). All new code should import from core.cara_research.

This shim is preserved so any existing imports keep working.
"""
from .cara_research import (
    generate_cara_block,
    generate_brutus_block,  # legacy alias returning {"cara_text", "brutus_text", ...}
    wrap_forwarded,
    CARA_FROM,
    CARA_SIGN,
)

__all__ = [
    "generate_cara_block",
    "generate_brutus_block",
    "wrap_forwarded",
    "CARA_FROM",
    "CARA_SIGN",
]
