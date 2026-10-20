"""
Generate 10 photoreal AI headshots for Flow Ops sender personas via OpenAI Image API.

Each headshot:
  - Professional business-casual portrait
  - Plain neutral background
  - Photorealistic, warm authentic expression
  - 1024x1024, suitable for email signature embedding

Saves to ~/Desktop/team_photos/{persona}.png
"""
import base64
import json
import os
import time
import urllib.request
from pathlib import Path

OPENAI_KEY = os.environ.get(
    "OPENAI_API_KEY",
    "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"
)

OUT_DIR = Path.home() / "Desktop" / "team_photos"
OUT_DIR.mkdir(parents=True, exist_ok=True)


# Persona spec — name, gender/look guidance, vibe
_BASE = "ultra photorealistic professional headshot, model-quality stunning features, symmetric face, clear glowing skin, bright expressive eyes, perfect teeth, editorial portrait lighting like Vogue or GQ, soft golden-hour glow, shallow depth of field, sharp focus on face, plain blurred light grey studio background, square crop, looks like a top-tier executive LinkedIn photo, dressed sharp business casual"

PERSONAS = [
    {"slug": "lilly",   "name": "Lilly Smith",  "prompt": f"{_BASE}, attractive young white woman, late 20s, lustrous shoulder-length blonde hair with natural highlights, soft genuine smile, wearing a crisp white silk blouse, model-quality"},
    {"slug": "priya",   "name": "Priya Iyer",   "prompt": f"{_BASE}, stunning South Asian woman, early 30s, long sleek dark hair, warm confident smile, sharp jawline, wearing a tailored navy blue blazer over a white top, model-quality"},
    {"slug": "ryan",    "name": "Ryan Mitchell","prompt": f"{_BASE}, handsome white man, mid 30s, short styled brown hair, strong jaw, genuine confident smile, light stubble, wearing a fitted charcoal blazer over a fitted t-shirt, model-quality, looks like a polished startup founder"},
    {"slug": "ashley",  "name": "Ashley Park",  "prompt": f"{_BASE}, beautiful East Asian woman, late 20s, sleek black shoulder-length hair with subtle wave, warm radiant smile, flawless skin, wearing a soft blush silk blouse, model-quality"},
    {"slug": "nealt",   "name": "Neal Thakkar (alt)", "prompt": f"{_BASE}, handsome Indian American man, early 30s, thick styled dark hair, neat short beard, genuine warm smile, sharp features, wearing a fitted black quarter-zip pullover, model-quality, founder energy"},
    {"slug": "roddy",   "name": "Roddy Hayes",  "prompt": f"{_BASE}, very handsome Black man, mid 30s, short neat fade haircut, confident warm smile, strong cheekbones, wearing a fitted dark forest green button-down shirt, model-quality"},
    {"slug": "mason",   "name": "Mason Reed",   "prompt": f"{_BASE}, very attractive Latino man, late 20s, well-styled dark hair, genuine warm smile, athletic build, wearing a fitted heather grey crewneck sweater, model-quality"},
    {"slug": "john",    "name": "John Carter",  "prompt": f"{_BASE}, distinguished handsome white man, early 40s, neatly groomed brown hair with a touch of grey at temples, clean shaven, kind confident smile, strong features, wearing a fitted navy blazer over a crisp white shirt no tie, model-quality, executive energy"},
    {"slug": "carly",   "name": "Carly Bauer",  "prompt": f"{_BASE}, stunning redheaded white woman, late 20s, long flowing wavy auburn hair, bright radiant smile, fair luminous skin with a few subtle freckles, wearing a fitted cream cashmere sweater, model-quality"},
    {"slug": "neal",    "name": "Neal Thakkar", "prompt": f"{_BASE}, handsome Indian American man, early 30s, perfectly styled thick dark hair, neat short beard, confident genuine smile, sharp cheekbones, wearing a fitted black quarter-zip pullover, model-quality, founder energy"},
]


def generate_image(prompt: str, slug: str) -> str | None:
    """Call OpenAI Image API. Returns path to saved PNG."""
    body = {
        "model":   "gpt-image-1",
        "prompt":  prompt,
        "size":    "1024x1024",
        "n":       1,
        "quality": "high",
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {OPENAI_KEY}",
            "Content-Type":  "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            resp = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code}: {e.read().decode()[:300]}")
        return None
    except Exception as e:
        print(f"  ERR: {e}")
        return None

    data = resp.get("data", [])
    if not data:
        print(f"  no data in response")
        return None

    # gpt-image-1 returns base64
    b64 = data[0].get("b64_json")
    if b64:
        out_path = OUT_DIR / f"{slug}.png"
        out_path.write_bytes(base64.b64decode(b64))
        return str(out_path)
    # fallback if URL response
    url = data[0].get("url")
    if url:
        out_path = OUT_DIR / f"{slug}.png"
        with urllib.request.urlopen(url, timeout=60) as r:
            out_path.write_bytes(r.read())
        return str(out_path)
    return None


import urllib.error


def main():
    print(f"Generating {len(PERSONAS)} team photos to {OUT_DIR}/\n")
    for i, p in enumerate(PERSONAS, 1):
        print(f"[{i}/{len(PERSONAS)}] {p['name']} ({p['slug']})...")
        t = time.time()
        path = generate_image(p["prompt"], p["slug"])
        if path:
            print(f"  ✓ {path}  ({time.time()-t:.1f}s)")
        else:
            print(f"  ✗ failed")
    print(f"\nDone. Photos at {OUT_DIR}/")


if __name__ == "__main__":
    main()
