"""
Website Redo Pipeline (Gemini 3 Pro Image direct generation).

After A/B testing: Gemini 3 Pro Image via OpenRouter beats Sonnet HTML for
mockup quality. Generates premium designed mockups directly as PNG without
intermediate HTML.

Flow:
  1. Scrape their current site to extract real services + tagline
  2. Send to Gemini 3 Pro Image via OpenRouter with niche-specific design prompt
  3. Save returned PNG to disk
  4. Push to CDN (flowops-assets.vercel.app/mockups/<slug>.png)

Cost: ~$0.06/mockup (Gemini 3 Pro Image via OpenRouter).
Speed: ~25 sec/mockup.

Run:
  .venv-server/bin/python -m core.website_redo --url https://example.com --niche FINANCIAL --company "Acme Corp"
"""
import argparse
import base64
import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

from . import llm


OPENROUTER_KEY = os.environ["OPENROUTER_API_KEY"]


OUTPUT_DIR = Path("/tmp/website_redos")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def scrape_site(url: str) -> dict:
    """Pull homepage HTML + screenshot + meta."""
    from playwright.sync_api import sync_playwright

    out = {"url": url, "screenshot_path": None, "html": "", "title": "", "meta": {}}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        try:
            page.goto(url, timeout=20000, wait_until="domcontentloaded")
            time.sleep(2)  # let lazy assets settle
            out["html"] = page.content()
            out["title"] = page.title()

            # Screenshot
            slug = re.sub(r"[^a-z0-9]+", "_", url.lower())[:80]
            ss_path = OUTPUT_DIR / f"{slug}_original.png"
            page.screenshot(path=str(ss_path), full_page=False)
            out["screenshot_path"] = str(ss_path)

            # Meta description, OG tags
            out["meta"]["description"] = page.eval_on_selector(
                'meta[name="description"]',
                'el => el ? el.content : ""',
            ) if page.query_selector('meta[name="description"]') else ""
            out["meta"]["og_title"] = page.eval_on_selector(
                'meta[property="og:title"]',
                'el => el ? el.content : ""',
            ) if page.query_selector('meta[property="og:title"]') else ""

        except Exception as e:
            out["error"] = str(e)
        finally:
            ctx.close()
            browser.close()

    return out


REDESIGN_SYSTEM = """You are a senior conversion-focused web designer redesigning
a service business's homepage. The current site is dated and converts poorly.

Output ONLY clean HTML+CSS for a single-page redesign. Modern, dark-or-light
themed based on industry, mobile-first, conversion-optimized.

CONSTRAINTS:
- One file: HTML with <style> inline (no external CSS)
- Use Inter or Space Grotesk font, loaded via Google Fonts
- Above-the-fold hero with: niche-appropriate headline, sub-headline, primary CTA, trust marker
- Sections: Services (3-4 cards), Social Proof (1-2 testimonials), CTA band, Footer
- High-contrast, lots of whitespace, big typography
- NO emojis, NO purple gradients, NO stock-looking icons (use simple geometric SVGs)
- Real placeholder copy that's specific to THEIR niche (use the extracted services)

DELIVERABLE:
A complete <html>...</html> document I can save and screenshot.

DO NOT return JSON. Return ONLY raw HTML."""


def generate_redesign_image(scraped: dict, niche: str, company_name: str = "", out_path: str = "") -> str:
    """Use Gemini 3 Pro Image (via OpenRouter) to generate the redesigned mockup directly as PNG.
    Returns path to saved PNG, or "" on failure.
    """
    title = scraped.get("title", "")
    meta_desc = scraped.get("meta", {}).get("description", "")
    html = scraped.get("html", "")[:15000]
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()[:1500]

    NICHE_DESIGN = {
        "WEALTH":    "luxury wealth management — deep navy / bone / charcoal palette, subtle gold accent, serif display font, mountain or cinematic backdrop",
        "FINANCIAL": "trustworthy professional — deep blue / cream / dark grey palette, elegant serif/sans-serif mix, clean white space",
        "MEDSPA":    "premium spa aesthetic — soft blush / nude / rose-gold / cream palette, elegant sans-serif, soft lifestyle imagery",
        "PI_LAW":    "powerful authoritative law firm — deep black / gold / cream palette, serif display font, courthouse/columns/cinematic legal imagery",
        "MORTGAGE":  "modern home-finance brand — warm blue / amber / cream palette, sans-serif, lifestyle home imagery",
        "INSURANCE": "trustworthy modern insurance — navy / sky-blue / white palette, sans-serif, clean iconography",
        "DEFAULT":   "premium luxury brand — sophisticated muted palette, generous whitespace, large typography, cinematic imagery",
    }
    design = NICHE_DESIGN.get(niche.upper(), NICHE_DESIGN["DEFAULT"])

    prompt = f"""Generate a premium homepage screenshot mockup for {company_name}, a {niche.lower().replace('_',' ')} business.

Their current site title: "{title}"
Meta description: "{meta_desc}"
Real services hinted in current site: {text[:600]}

DESIGN REQUIREMENTS:
- Top-tier {design}
- ONE single tall vertical screenshot (portrait orientation, ~1440px wide, ~3200px tall)
- Render the page top-to-bottom in ONE continuous column. Do NOT split into 2 side-by-side panels. Do NOT show multiple devices. Do NOT show a desktop-frame mockup with an iPhone next to it. ONE flat browser screenshot, scrolled top-to-bottom in a single column.
- Browser chrome bar at the very top with their URL visible
- Hero section first (full-width, large headline preserving their actual tagline/value prop)
- Below hero, stacked vertically: services grid (3-4 cards), social proof / testimonial with photo, optional founder/about section, CTA band ("Book Free Consultation" or niche-appropriate), footer with link columns
- All sections stacked vertically in reading order, like a real website scrolled into one tall image

OUTPUT: ONE tall single-column homepage screenshot at desktop width. Photo-realistic. Looks like the screenshot of a $50K agency build. NOT a designer-portfolio side-by-side comp. NOT a generic template. Premium quality, one continuous page from top to bottom."""

    body = json.dumps({
        "model": "google/gemini-3.1-flash-image-preview",   # 6-15x cheaper than 3-pro, 90% quality
        "messages": [{"role":"user","content":prompt}],
        "modalities": ["image","text"],
    }).encode()

    try:
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=body,
            headers={"Authorization":f"Bearer {OPENROUTER_KEY}","Content-Type":"application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=180) as r:
            d = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return ""
    except Exception:
        return ""

    msg = d.get("choices",[{}])[0].get("message",{})
    if not out_path:
        slug = re.sub(r"[^a-z0-9]+","_",(company_name or "mockup").lower())[:50]
        out_path = str(OUTPUT_DIR / f"{slug}_mockup.png")

    if isinstance(msg.get("images"), list) and msg["images"]:
        url = msg["images"][0].get("image_url",{}).get("url","")
        if url.startswith("data:image"):
            Path(out_path).write_bytes(base64.b64decode(url.split(",",1)[1]))
            return out_path

    if isinstance(msg.get("content"), list):
        for block in msg["content"]:
            if block.get("type") == "image_url":
                url = block["image_url"]["url"]
                if url.startswith("data:image"):
                    Path(out_path).write_bytes(base64.b64decode(url.split(",",1)[1]))
                    return out_path
    return ""


def generate_redesign(scraped: dict, niche: str, company_name: str = "") -> str:
    """Deprecated alias — Sonnet HTML path. Use generate_redesign_image() instead."""
    html = scraped.get("html", "")[:30000]
    user = f"""COMPANY: {company_name or "(unknown)"}
NICHE: {niche}
CURRENT TITLE: {scraped.get("title","")}

CURRENT HOMEPAGE HTML (truncated):
{html}

Redesign this homepage. Return ONLY the HTML document."""
    result = llm.call(
        system=REDESIGN_SYSTEM, user=user,
        model=llm.SONNET_OR, max_tokens=8000, temperature=0.6,
    )
    if result.get("_error"):
        return ""
    text = result["text"].strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text
        text = text.rsplit("```", 1)[0].strip()
    return text


def screenshot_html(html_str: str, slug: str) -> str | None:
    """Save HTML to disk, open in Chromium, screenshot, return PNG path."""
    from playwright.sync_api import sync_playwright

    html_path = OUTPUT_DIR / f"{slug}_redesign.html"
    png_path  = OUTPUT_DIR / f"{slug}_redesign.png"

    html_path.write_text(html_str)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        try:
            page.goto(f"file://{html_path}", wait_until="load", timeout=15000)
            time.sleep(2)  # let fonts load
            page.screenshot(path=str(png_path), full_page=True)
        finally:
            ctx.close()
            browser.close()

    return str(png_path)


def run_redo(url: str, niche: str, company_name: str = "") -> dict:
    """Full pipeline: scrape → redesign → screenshot."""
    print(f"\n[1/3] Scraping {url}...")
    scraped = scrape_site(url)
    if scraped.get("error"):
        return {"_error": f"scrape failed: {scraped['error']}"}
    print(f"  Title: {scraped['title'][:80]}")
    print(f"  Original screenshot: {scraped['screenshot_path']}")

    print(f"\n[2/3] Generating redesign (Sonnet)...")
    html = generate_redesign(scraped, niche, company_name)
    if not html or "<html" not in html.lower():
        return {"_error": "redesign generation failed or returned non-HTML"}

    slug = re.sub(r"[^a-z0-9]+", "_", url.lower())[:80]

    print(f"\n[3/3] Rendering redesign PNG...")
    png_path = screenshot_html(html, slug)

    return {
        "url": url,
        "company": company_name,
        "niche": niche,
        "original_screenshot": scraped["screenshot_path"],
        "redesign_html_path":  str(OUTPUT_DIR / f"{slug}_redesign.html"),
        "redesign_png_path":   png_path,
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--url", required=True)
    p.add_argument("--niche", required=True, choices=["WEALTH","FINANCIAL","MEDSPA","PI_LAW","COMMLOAN","MORTGAGE","AGENCY"])
    p.add_argument("--company", default="")
    args = p.parse_args()

    result = run_redo(args.url, args.niche, args.company)
    print()
    print(json.dumps(result, indent=2, default=str))
