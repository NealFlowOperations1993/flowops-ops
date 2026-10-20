"""
Council orchestrator.

Phase 1: All N personas generate 9-key personalization in parallel (Haiku).
Phase 2: 3 dimension judges pick best opener, best pain, best CTA from N candidates (Sonnet).
Phase 3: Coherence judge approves/edits the combined trio (Sonnet).
Phase 4: Build final 9-key output (using winning email1_* + each persona's email2/3 from the
         persona that won email1_opener — keeps voice consistent across the sequence).

Per-lead cost target: ~$0.025 with 7 personas.
Per-lead latency: 8-15 sec (parallelized).
"""
import json
import time
from typing import Any

from . import llm, personas, judges


def generate(lead: dict, niche_context: dict | None = None, debug: bool = False) -> dict:
    """
    Run the full council on one lead.
    Returns: {
      "final": {9 keys},
      "winning_persona": str,
      "candidates": [...],     # all N persona outputs
      "judge_decisions": {...},
      "coherence": {...},
      "cost_usd": float,
      "latency_sec": float,
      "council_run_id": str
    }
    """
    t0 = time.time()
    run_id = f"council_{int(t0 * 1000)}"

    # ── PHASE 1: Generate ──────────────────────────────────────────────
    all_personas = personas.load_all()
    user_prompt = personas.build_user_prompt(lead, niche_context)

    prompts = [
        {
            "system": p["system_prompt"],
            "user": user_prompt,
            "model": llm.GEMINI_FLASH,
            "max_tokens": 1500,
            "temperature": 0.85,
            "id": p["id"],
        }
        for p in all_personas
    ]
    raw_results = llm.parallel_call(prompts, max_workers=10)

    # Parse each persona's JSON output
    candidates = []
    total_gen_cost = 0.0
    for r, p in zip(raw_results, all_personas):
        if r.get("_error"):
            if debug:
                print(f"  [persona {p['id']}] ERROR: {r}")
            continue
        try:
            parsed = llm.parse_json_from_text(r["text"])
            candidates.append({
                "persona_id": p["id"],
                "persona_name": p["name"],
                **parsed,
            })
            total_gen_cost += llm.estimate_cost(r["usage"], r["model"])
        except Exception as e:
            if debug:
                print(f"  [persona {p['id']}] PARSE FAIL: {e} | text: {r['text'][:200]}")
            continue

    if not candidates:
        raise RuntimeError("All personas failed. Check API keys + persona prompts.")

    if debug:
        print(f"\n[Phase 1] Generated {len(candidates)}/{len(all_personas)} candidates "
              f"in {time.time() - t0:.1f}s, cost ${total_gen_cost:.4f}")

    # ── PHASE 2: Judges vote per dimension ─────────────────────────────
    judge_results = {}
    total_judge_cost = 0.0
    for dim in ["opener", "pain", "cta"]:
        # Each candidate's email1_<dim> becomes a candidate for the judge
        texts = [c.get(f"email1_{dim}", "") for c in candidates]
        judge_system = judges.load(f"{dim}_judge")
        judge_user = judges.build_judge_user_prompt(dim, texts)

        result = llm.call(
            system=judge_system,
            user=judge_user,
            model=llm.GEMINI_FLASH,         # was SONNET — switched per Option A (3x cost reduction)
            max_tokens=2000,
            temperature=0.3,
        )
        if result.get("_error"):
            raise RuntimeError(f"Judge {dim} failed: {result}")

        try:
            parsed = llm.parse_json_from_text(result["text"])
        except Exception as e:
            raise RuntimeError(f"Judge {dim} returned unparseable JSON: {e} | text: {result['text'][:300]}")

        judge_results[dim] = {
            "winner_index": parsed["winner_index"],
            "winner_text": parsed["winner_text"],
            "winning_persona": candidates[parsed["winner_index"]]["persona_id"],
            "reasoning": parsed.get("reasoning", ""),
            "scores": parsed.get("scores", []),
        }
        total_judge_cost += llm.estimate_cost(result["usage"], result["model"])
        if debug:
            print(f"[Phase 2] {dim} judge picked candidate {parsed['winner_index']} "
                  f"(persona: {judge_results[dim]['winning_persona']})")

    # ── PHASE 3: Coherence ─────────────────────────────────────────────
    picked_opener = judge_results["opener"]["winner_text"]
    picked_pain = judge_results["pain"]["winner_text"]
    picked_cta = judge_results["cta"]["winner_text"]

    coh_system = judges.load("coherence_judge")
    coh_user = judges.build_coherence_user_prompt(picked_opener, picked_pain, picked_cta)
    coh_result = llm.call(
        system=coh_system,
        user=coh_user,
        model=llm.GEMINI_FLASH,         # was SONNET — switched per Option A (3x cost reduction)
        max_tokens=1000,
        temperature=0.3,
    )
    coh_parsed = llm.parse_json_from_text(coh_result["text"])
    total_judge_cost += llm.estimate_cost(coh_result["usage"], coh_result["model"])

    if debug:
        print(f"[Phase 3] Coherence: approved={coh_parsed.get('approved', False)}")

    # If coherence rejected with a fix, apply minimal rewrite
    if not coh_parsed.get("approved", True) and coh_parsed.get("final"):
        picked_opener = coh_parsed["final"].get("opener", picked_opener)
        picked_pain = coh_parsed["final"].get("pain", picked_pain)
        picked_cta = coh_parsed["final"].get("cta", picked_cta)

    # ── PHASE 3.5: Voice Judge (picks best overall voice for email2 + email3) ──
    try:
        voice_system = judges.load("voice_judge")
        # Build a compact user prompt: list all candidates with their 9-key shape
        v_lines = ["Here are the 12 full-candidate emails. Pick the best overall voice for email2 + email3 continuation.\n"]
        for i, c in enumerate(candidates):
            v_lines.append(f"--- candidate {i} (persona: {c.get('persona_id','?')}) ---")
            v_lines.append(f"e1_opener: {c.get('email1_opener','')[:150]}")
            v_lines.append(f"e2_opener: {c.get('email2_opener','')[:150]}")
            v_lines.append(f"e3_opener: {c.get('email3_opener','')[:150]}")
            v_lines.append("")
        v_user = "\n".join(v_lines) + "\n\nReturn winner_index (0-based) per voice_judge spec."
        v_result = llm.call(
            system=voice_system, user=v_user,
            model=llm.GEMINI_FLASH, max_tokens=1200, temperature=0.3,
        )
        v_parsed = llm.parse_json_from_text(v_result["text"])
        voice_persona_id = candidates[v_parsed["winner_index"]]["persona_id"]
        total_judge_cost += llm.estimate_cost(v_result["usage"], v_result["model"])
        if debug:
            print(f"[Phase 3.5] Voice judge picked candidate {v_parsed['winner_index']} (persona: {voice_persona_id})")
    except Exception as e:
        # Fallback to opener winner if voice judge fails
        voice_persona_id = judge_results["opener"]["winning_persona"]
        if debug:
            print(f"[Phase 3.5] Voice judge failed ({e}), falling back to opener winner: {voice_persona_id}")

    # ── PHASE 4: Build final 9-key output ──────────────────────────────
    # email1_* = winners from opener/pain/cta judges
    # email2_* and email3_* = use the voice_judge's picked persona for tonal consistency
    voice_candidate = next(c for c in candidates if c["persona_id"] == voice_persona_id)

    final = {
        "email1_opener": picked_opener,
        "email1_pain": picked_pain,
        "email1_cta": picked_cta,
        "email2_opener": voice_candidate.get("email2_opener", ""),
        "email2_pain": voice_candidate.get("email2_pain", ""),
        "email2_cta": voice_candidate.get("email2_cta", ""),
        "email3_opener": voice_candidate.get("email3_opener", ""),
        "email3_pain": voice_candidate.get("email3_pain", ""),
        "email3_cta": voice_candidate.get("email3_cta", ""),
    }

    elapsed = time.time() - t0
    total_cost = total_gen_cost + total_judge_cost

    return {
        "final": final,
        "winning_persona_for_voice": voice_persona_id,
        "judges": judge_results,
        "coherence": coh_parsed,
        "candidates_count": len(candidates),
        "cost_usd": round(total_cost, 5),
        "latency_sec": round(elapsed, 2),
        "council_run_id": run_id,
    }
