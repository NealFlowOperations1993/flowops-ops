"""
Anthropic API wrapper with parallel calls + prompt caching + retry logic.
Used by council.py to fan out to N personas at once.
"""
import json
import os
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

ANTHROPIC_KEY = os.environ["ANTHROPIC_API_KEY"]

# OpenRouter key, loaded from ~/.config/openrouter/key.env if not in env
def _load_or_key():
    if os.environ.get("OPENROUTER_API_KEY"):
        return os.environ["OPENROUTER_API_KEY"]
    path = os.path.expanduser("~/.config/openrouter/key.env")
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                if line.startswith("OPENROUTER_API_KEY="):
                    return line.strip().split("=", 1)[1]
    return ""

OPENROUTER_KEY = _load_or_key()

# Anthropic models (direct)
HAIKU = "claude-haiku-4-5-20251001"
SONNET = "claude-sonnet-4-5"
# OpenRouter models — namespaced with "or:" prefix to route differently
GEMINI_FLASH = "or:google/gemini-2.5-flash-lite"
GPT4O_MINI   = "or:openai/gpt-4o-mini"
LLAMA_70B    = "or:meta-llama/llama-3.3-70b-instruct"
DEEPSEEK_V3  = "or:deepseek/deepseek-chat"
SONNET_OR    = "or:anthropic/claude-sonnet-4.5"  # Sonnet routed via OpenRouter (HARDCODED rule)

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def _post_anthropic(body: dict, timeout: int = 60) -> dict:
    req = urllib.request.Request(
        ANTHROPIC_URL,
        data=json.dumps(body).encode(),
        headers={
            "x-api-key": ANTHROPIC_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read().decode())
        except Exception:
            err = {"error": str(e)}
        return {"_error": True, "code": e.code, "body": err}


def _post_openrouter(body: dict, timeout: int = 60) -> dict:
    """Post to OpenRouter using OpenAI-compatible interface."""
    req = urllib.request.Request(
        OPENROUTER_URL,
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type":  "application/json",
            "HTTP-Referer":  "https://flowoperations.ai",
            "X-Title":       "FlowOps Council",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read().decode())
        except Exception:
            err = {"error": str(e)}
        return {"_error": True, "code": e.code, "body": err}


def _post(body: dict, timeout: int = 60) -> dict:
    """Legacy alias — routes to Anthropic. Kept for backward compatibility."""
    return _post_anthropic(body, timeout)


def call(
    system: str,
    user: str,
    model: str = HAIKU,
    max_tokens: int = 1500,
    temperature: float = 0.7,
    cache_system: bool = True,
    retries: int = 2,
) -> dict:
    """
    Single LLM call. Routes to Anthropic or OpenRouter based on model prefix.
    Models prefixed "or:" route through OpenRouter. Others route to Anthropic.
    Returns: {"text", "usage", "model"} or {"_error": ..., "details": ...}.
    """
    is_openrouter = model.startswith("or:")

    if is_openrouter:
        provider_model = model[3:]  # strip "or:" prefix
        body = {
            "model": provider_model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
        }
        last_err = None
        for attempt in range(retries + 1):
            resp = _post_openrouter(body)
            if resp.get("_error"):
                last_err = resp
                time.sleep(1.5 ** attempt)
                continue
            # OpenAI-compatible response format
            choices = resp.get("choices", [])
            if not choices:
                last_err = {"reason": "no choices", "body": resp}
                time.sleep(1.5 ** attempt)
                continue
            text = (choices[0].get("message") or {}).get("content", "")
            usage = resp.get("usage", {})
            return {
                "text":  text,
                "usage": {
                    "input_tokens":  usage.get("prompt_tokens", 0),
                    "output_tokens": usage.get("completion_tokens", 0),
                },
                "model": model,
            }
        return {"_error": True, "details": last_err, "model": model}

    # ── Anthropic direct ──
    if cache_system:
        system_block = [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}]
    else:
        system_block = system

    body = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "system": system_block,
        "messages": [{"role": "user", "content": user}],
    }

    last_err = None
    for attempt in range(retries + 1):
        resp = _post_anthropic(body)
        if resp.get("_error"):
            last_err = resp
            time.sleep(1.5 ** attempt)
            continue
        return {
            "text": (resp.get("content", [{}])[0] or {}).get("text", ""),
            "usage": resp.get("usage", {}),
            "model": model,
        }
    return {"_error": True, "details": last_err, "model": model}


def parallel_call(prompts: list[dict], max_workers: int = 10) -> list[dict]:
    """
    Fire N Claude calls in parallel.
    prompts: list of {"system": str, "user": str, "model": str?, "max_tokens": int?, "temperature": float?, "id": str?}
    Returns list of results in INPUT ORDER (not completion order).
    """
    results = [None] * len(prompts)

    def _do(idx_and_prompt):
        idx, p = idx_and_prompt
        return idx, call(
            system=p["system"],
            user=p["user"],
            model=p.get("model", HAIKU),
            max_tokens=p.get("max_tokens", 1500),
            temperature=p.get("temperature", 0.7),
            cache_system=p.get("cache_system", True),
        )

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [pool.submit(_do, (i, p)) for i, p in enumerate(prompts)]
        for fut in as_completed(futures):
            idx, result = fut.result()
            # Preserve input id if provided
            if "id" in prompts[idx]:
                result["id"] = prompts[idx]["id"]
            results[idx] = result
    return results


def parse_json_from_text(text: str) -> Any:
    """
    Personas/judges return JSON. Sometimes wrapped in markdown fences. Strip them.
    """
    cleaned = text.strip()
    fence = "```"
    if fence in cleaned:
        # Find first fence
        start = cleaned.find(fence)
        cleaned = cleaned[start + len(fence):]
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        # Strip trailing fence
        end = cleaned.rfind(fence)
        if end != -1:
            cleaned = cleaned[:end]
    cleaned = cleaned.strip()
    return json.loads(cleaned)


def estimate_cost(usage: dict, model: str) -> float:
    """Rough cost estimate in USD for one call."""
    pricing = {
        HAIKU:        {"in": 1.0   / 1_000_000, "out": 5.0  / 1_000_000},
        SONNET:       {"in": 3.0   / 1_000_000, "out": 15.0 / 1_000_000},
        SONNET_OR:    {"in": 3.0   / 1_000_000, "out": 15.0 / 1_000_000},
        GEMINI_FLASH: {"in": 0.075 / 1_000_000, "out": 0.30 / 1_000_000},
        GPT4O_MINI:   {"in": 0.15  / 1_000_000, "out": 0.60 / 1_000_000},
        LLAMA_70B:    {"in": 0.59  / 1_000_000, "out": 0.79 / 1_000_000},
        DEEPSEEK_V3:  {"in": 0.14  / 1_000_000, "out": 0.28 / 1_000_000},
    }
    p = pricing.get(model, pricing[HAIKU])
    in_tokens = usage.get("input_tokens", 0) + usage.get("cache_read_input_tokens", 0) * 0.1
    out_tokens = usage.get("output_tokens", 0)
    return in_tokens * p["in"] + out_tokens * p["out"]
