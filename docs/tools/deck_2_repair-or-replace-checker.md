# Tool spec: "Repair, Resurface or Replace?" Old-Deck Checker (deck · tool 2)

> **Paste this into Lovable as ONE prompt, after the platform spec is built.** It assumes everything in
> `00_PLATFORM_SPEC.md` already exists: ToolShell (§5), routing (§2), tables (§3), personalization and
> deep-merge of `config_overrides` (§4), the `submit-tool` pipeline (§6), the Meta Pixel (§7), the design system (§8)
> and the regional multipliers (§9). Do **not** rebuild any of that. Build only what this file describes.
> Read every value from the merged config. Never hardcode a price, threshold or copy string.

> ⚠️ **Hard rule for this tool: it must never say the deck is unsafe.**
> - It flags symptoms as "worth an inspection" and nothing more.
> - The words in `rules.forbidden_result_words` (unsafe, dangerous, collapse, fail, failing, hazard, condemned) must never appear anywhere in the rendered result, email or thank-you.
> - See QA item 1.

---

## 1. Header

| Field | Value |
|---|---|
| **slug** | `deck-repair-or-replace-checker` |
| **niche** | `deck` |
| **name** | Repair, Resurface or Replace? Old-Deck Checker |
| **H1 (on-page promise)** | Repair, resurface or replace your deck? |
| **Sub-promise** | Answer 8 quick questions. See which path fits your deck — and what each one costs. |
| **Target time to result** | **40 seconds** (7–8 taps; the extent step only appears when needed) |
| **Trust row** (§5.1) | "★ Free · No signup to see your answer · Takes ~40s" |

---

## 2. Why this tool (VOC: `docs/voc/VOC_deck.md`)

- **Aging-deck owners are a real buying trigger.** *"I have a 25+ year old deck that needs replaced"* / *"My mom moved into a home and had some concerns around her deck"*. The VOC also lists a deck inspection for a real-estate sale (line 106).
- **An honest assessment is a win (~5 reviews).** *"walked through his assessment of potential issues and the best way to solve her concerns… honest and straightforward."* The verdict shows **all four paths with prices**, not just the most expensive one.
- **Hidden decay is a win when handled fairly.** *"the structure had decay that was not visible… handled the changes in the scope of the job with great professionalism."* That's why "Hidden damage found once boards come up" is listed as not included, and why "only an inspection can tell" appears throughout.
- **Unsafe workmanship is a pain (~9).** *"It was wavy and slated and unsafe by the code."* Safety matters to buyers, but per VOC §4 Tool B: **"Must not assert a safety failure from a checkbox; present it as 'get it inspected'."**
- **Scope ambiguity, pain #6 (~5).** *"they tried to say the quote for the stain… only included stain on the repaired piece of wood."* Each path has an included list.
- **Deadline buyers.** *"I was hoping to have my very basic deck repairs finished before my pregnant wife was due."* That's why the tool asks about selling or buying the home and has the urgency flag.
- **Confidence is 6/10 in the VOC.** Keep the tool short and honest. It is a lead magnet for inspections and repairs, not a diagnosis.

---

## 3. Seed SQL for the `tools` table

Prices are **2025–2026 US defaults that each business tunes**. `regional_multipliers` is platform §9.

```sql
insert into tools (slug, niche, name, default_config, is_finance, active)
values (
  'deck-repair-or-replace-checker',
  'deck',
  'Repair, Resurface or Replace? Old-Deck Checker',
  $cfg$
{
  "version": 1,
  "regional_multipliers": {
    "CA": 1.3,
    "NY": 1.25,
    "MA": 1.22,
    "NJ": 1.2,
    "CT": 1.2,
    "WA": 1.18,
    "DC": 1.2,
    "MD": 1.12,
    "VA": 1.08,
    "IL": 1.1,
    "CO": 1.08,
    "MN": 1.05,
    "OR": 1.1,
    "FL": 1.0,
    "AZ": 0.98,
    "NC": 0.95,
    "GA": 0.95,
    "TN": 0.93,
    "TX": 0.95,
    "OH": 0.92,
    "IN": 0.92,
    "KS": 0.92,
    "MI": 0.95,
    "PA": 1.03
  },
  "rounding": {
    "small_threshold": 2000,
    "step_small": 50,
    "step_large": 100
  },
  "ages": [
    {
      "id": "lt5",
      "label": "Under 5 years",
      "icon": "Sprout",
      "age_pts": 0
    },
    {
      "id": "5_10",
      "label": "5–10 years",
      "icon": "Leaf",
      "age_pts": 0
    },
    {
      "id": "10_15",
      "label": "10–15 years",
      "icon": "TreeDeciduous",
      "age_pts": 1
    },
    {
      "id": "15_20",
      "label": "15–20 years",
      "icon": "TreePine",
      "age_pts": 2
    },
    {
      "id": "20_25",
      "label": "20–25 years",
      "icon": "Trees",
      "age_pts": 3
    },
    {
      "id": "25p",
      "label": "25+ years",
      "icon": "Hourglass",
      "age_pts": 4
    },
    {
      "id": "unsure",
      "label": "Not sure",
      "icon": "CircleHelp",
      "hint": "It came with the house",
      "age_pts": 2
    }
  ],
  "materials": [
    {
      "id": "pt",
      "label": "Pressure-treated wood",
      "icon": "TreePine",
      "hint": "Green-ish or brown lumber",
      "family": "wood",
      "age_pts_adjust": 0
    },
    {
      "id": "cedar",
      "label": "Cedar or redwood",
      "icon": "TreeDeciduous",
      "hint": "Reddish natural wood",
      "family": "wood",
      "age_pts_adjust": 0
    },
    {
      "id": "composite",
      "label": "Composite (Trex, etc.)",
      "icon": "Layers",
      "hint": "Plastic-wood boards, no grain gaps",
      "family": "composite",
      "age_pts_adjust": -1
    },
    {
      "id": "pvc",
      "label": "PVC / vinyl",
      "icon": "Sparkles",
      "hint": "Hollow or all-plastic boards",
      "family": "composite",
      "age_pts_adjust": -1
    },
    {
      "id": "hardwood",
      "label": "Tropical hardwood (Ipe)",
      "icon": "Gem",
      "hint": "Very dense dark wood",
      "family": "wood",
      "age_pts_adjust": -1
    },
    {
      "id": "unsure",
      "label": "Not sure",
      "icon": "CircleHelp",
      "hint": "",
      "family": "wood",
      "age_pts_adjust": 0
    }
  ],
  "sizes": [
    {
      "id": "s",
      "label": "Small",
      "icon": "Square",
      "hint": "about 10 × 15 ft · 150 sq ft",
      "sqft": 150
    },
    {
      "id": "m",
      "label": "Medium",
      "icon": "Grid2x2",
      "hint": "about 12 × 20 ft · 250 sq ft",
      "sqft": 250
    },
    {
      "id": "l",
      "label": "Large",
      "icon": "Grid3x3",
      "hint": "about 16 × 25 ft · 400 sq ft",
      "sqft": 400
    },
    {
      "id": "xl",
      "label": "Extra large",
      "icon": "LayoutGrid",
      "hint": "multi-level or 600+ sq ft",
      "sqft": 600
    },
    {
      "id": "custom",
      "label": "I know the size",
      "icon": "Ruler",
      "hint": "Enter square feet"
    }
  ],
  "size_limits": {
    "sqft_min": 40,
    "sqft_max": 1500,
    "custom_default": 250
  },
  "heights": [
    {
      "id": "ground",
      "label": "Ground level",
      "icon": "Minus",
      "hint": "Under 2 ft off the ground",
      "replace_multiplier": 0.92,
      "raises_flag": false
    },
    {
      "id": "standard",
      "label": "Raised",
      "icon": "ArrowUp",
      "hint": "2–6 ft · off a first-floor door",
      "replace_multiplier": 1.0,
      "raises_flag": false
    },
    {
      "id": "second",
      "label": "Second story",
      "icon": "ArrowUpToLine",
      "hint": "6 ft or more",
      "replace_multiplier": 1.25,
      "raises_flag": true
    }
  ],
  "symptoms": [
    {
      "id": "soft_boards",
      "label": "Soft or spongy boards",
      "icon": "Footprints",
      "hint": "Give a little when you step",
      "category": "board",
      "replace_pts": 1,
      "safety": "check"
    },
    {
      "id": "cracked_boards",
      "label": "Cracked or split boards",
      "icon": "Slash",
      "hint": "",
      "category": "board",
      "replace_pts": 0,
      "safety": null
    },
    {
      "id": "popping_nails",
      "label": "Loose or popping nails/screws",
      "icon": "Hammer",
      "hint": "",
      "category": "board",
      "replace_pts": 0,
      "safety": null
    },
    {
      "id": "wobbly_railing",
      "label": "Wobbly railing",
      "icon": "Hand",
      "hint": "Moves when you lean on it",
      "category": "structural",
      "replace_pts": 1,
      "safety": "check",
      "repair": {
        "label": "Re-secure or rebuild railing sections",
        "low": 500,
        "high": 1800
      }
    },
    {
      "id": "wobbly_stairs",
      "label": "Wobbly or loose stairs",
      "icon": "TrendingUp",
      "hint": "",
      "category": "structural",
      "replace_pts": 1,
      "safety": "check",
      "repair": {
        "label": "Re-secure or rebuild stairs",
        "low": 700,
        "high": 2200
      }
    },
    {
      "id": "rot",
      "label": "Rot you can see",
      "icon": "Droplets",
      "hint": "Dark, crumbly or soft wood on posts, beams or boards",
      "category": "structural",
      "replace_pts": 2,
      "safety": "check",
      "safety_soon_if_extent": [
        "quarter",
        "most"
      ],
      "repair": {
        "label": "Replace rotted framing",
        "low": 1200,
        "high": 4000
      },
      "extent_scaled": true
    },
    {
      "id": "rusted_fasteners",
      "label": "Rusty hangers, bolts or screws",
      "icon": "Bolt",
      "hint": "Orange streaks or flaking metal under the deck",
      "category": "structural",
      "replace_pts": 1,
      "safety": "check",
      "repair": {
        "label": "Replace corroded hangers & fasteners",
        "low": 600,
        "high": 2000
      }
    },
    {
      "id": "ledger",
      "label": "Gap where the deck meets the house",
      "icon": "Unlink",
      "hint": "Or water stains on the wall inside",
      "category": "structural",
      "replace_pts": 3,
      "safety": "soon",
      "repair": {
        "label": "Re-attach & re-flash the ledger board",
        "low": 1800,
        "high": 4500
      }
    },
    {
      "id": "bouncy",
      "label": "Bouncy or sagging when you walk",
      "icon": "MoveVertical",
      "hint": "",
      "category": "structural",
      "replace_pts": 2,
      "safety": "soon",
      "repair": {
        "label": "Add joists or blocking to stiffen the frame",
        "low": 800,
        "high": 2500
      }
    },
    {
      "id": "leaning_posts",
      "label": "Leaning or sinking posts",
      "icon": "ArrowDownToLine",
      "hint": "",
      "category": "structural",
      "replace_pts": 2,
      "safety": "soon",
      "repair": {
        "label": "Reset or replace posts & footings",
        "low": 900,
        "high": 2800
      }
    },
    {
      "id": "splinters_fading",
      "label": "Splinters, fading or gray boards",
      "icon": "Sun",
      "hint": "Looks tired but feels solid",
      "category": "cosmetic",
      "replace_pts": 0,
      "safety": null
    },
    {
      "id": "none",
      "label": "None of these",
      "icon": "CircleCheck",
      "hint": "It just looks dated",
      "category": "none",
      "replace_pts": 0,
      "safety": null,
      "exclusive": true
    }
  ],
  "extents": [
    {
      "id": "few",
      "label": "A few spots",
      "icon": "Dot",
      "replace_pts": 0,
      "board_share": 0.1,
      "rot_factor": 1.0
    },
    {
      "id": "quarter",
      "label": "About a quarter of the deck",
      "icon": "PieChart",
      "replace_pts": 1,
      "board_share": 0.25,
      "rot_factor": 1.5
    },
    {
      "id": "most",
      "label": "Most of the deck",
      "icon": "CircleDot",
      "replace_pts": 3,
      "board_share": 0.6,
      "rot_factor": 2.5
    },
    {
      "id": "unsure",
      "label": "Not sure",
      "icon": "CircleHelp",
      "replace_pts": 1,
      "board_share": 0.25,
      "rot_factor": 1.5
    }
  ],
  "plans": [
    {
      "id": "selling_12",
      "label": "Selling within 12 months",
      "icon": "Signpost",
      "urgent": true
    },
    {
      "id": "buying",
      "label": "Just bought / buying this home",
      "icon": "KeyRound",
      "urgent": false
    },
    {
      "id": "stay_1_5",
      "label": "Staying 1–5 years",
      "icon": "House",
      "urgent": false
    },
    {
      "id": "stay_5p",
      "label": "Staying 5+ years",
      "icon": "Heart",
      "urgent": false
    }
  ],
  "priorities": [
    {
      "id": "cost",
      "label": "Keep the cost down",
      "icon": "PiggyBank"
    },
    {
      "id": "low_maint",
      "label": "Less upkeep",
      "icon": "Clock"
    },
    {
      "id": "new_look",
      "label": "A whole new look",
      "icon": "Sparkles"
    },
    {
      "id": "solid",
      "label": "Make it solid again",
      "icon": "ShieldCheck"
    }
  ],
  "rules": {
    "forbidden_result_words": [
      "unsafe",
      "dangerous",
      "collapse",
      "fail",
      "failing",
      "hazard",
      "condemned"
    ],
    "replace_threshold": 7,
    "repair_to_replace_ratio": 0.5,
    "resurface_to_replace_ratio": 0.7,
    "resurface_min_age_pts": 2,
    "cosmetic_resurface_min_age_pts": 3
  },
  "costs": {
    "maintain_per_sqft": {
      "wood": {
        "low": 2.5,
        "high": 4.5
      },
      "composite": {
        "low": 0.75,
        "high": 1.5
      }
    },
    "maintain_min": {
      "low": 450,
      "high": 800
    },
    "board_replace_per_sqft": {
      "wood": {
        "low": 15,
        "high": 28
      },
      "composite": {
        "low": 25,
        "high": 40
      }
    },
    "repair_min": {
      "low": 500,
      "high": 900
    },
    "repair_generic": {
      "label": "Typical repair visit",
      "low": 500,
      "high": 1500
    },
    "resurface_per_sqft": {
      "wood": {
        "low": 18,
        "high": 30
      },
      "composite": {
        "low": 28,
        "high": 45
      }
    },
    "replace_per_sqft": {
      "wood": {
        "low": 40,
        "high": 60
      },
      "composite": {
        "low": 58,
        "high": 85
      }
    },
    "demo_per_sqft": {
      "low": 4,
      "high": 7
    },
    "disposal_flat": {
      "low": 400,
      "high": 800
    },
    "replace_min": {
      "low": 9000,
      "high": 13000
    }
  },
  "copy": {
    "h1": "Repair, resurface or replace your deck?",
    "sub": "Answer 8 quick questions. See which path fits your deck — and what each one costs.",
    "result_title": "Our read on your deck",
    "result_subtitle": "{age_label} {material_label} deck · about {sqft} sq ft · prices typical for {city}",
    "verdicts": {
      "maintain": {
        "label": "Maintain it",
        "icon": "Paintbrush",
        "headline": "Your deck sounds like it mainly needs care, not construction.",
        "body": "A clean, light sand and fresh stain or sealer (wood) — or a deep clean (composite) — should bring it back. Wood decks need this every 2–3 years."
      },
      "repair": {
        "label": "Repair it",
        "icon": "Wrench",
        "headline": "Targeted repairs should get more life out of this deck.",
        "body": "The issues you described are usually fixed piece by piece. While they're there, a builder will check that the frame underneath is in good shape."
      },
      "resurface": {
        "label": "Resurface it",
        "icon": "Layers",
        "headline": "The frame may be worth keeping. The surface probably isn't.",
        "body": "Resurfacing means new boards and stair treads on your existing frame, once a builder confirms the frame is sound. It typically costs about half of a full rebuild."
      },
      "replace": {
        "label": "Replace it",
        "icon": "Hammer",
        "headline": "A new deck is likely the better value.",
        "body": "At this age, and with the issues you described, repairs tend to keep coming. A rebuild resets the clock and lets you change the size, layout or material."
      }
    },
    "reason_repair_ratio": "Repairs here would cost about half as much as a new deck, which is the point where most owners choose to replace.",
    "reason_resurface_ratio": "Resurfacing here would cost close to a full rebuild, so replacing is usually the better value.",
    "path_titles": {
      "maintain": "Maintain",
      "repair": "Repair",
      "resurface": "Resurface",
      "replace": "Replace"
    },
    "path_blurbs": {
      "maintain": "Clean, sand, stain or seal",
      "repair": "Fix the specific problems",
      "resurface": "New boards on the existing frame",
      "replace": "Tear out and build new"
    },
    "safety": {
      "check": {
        "title": "Worth having someone look at it",
        "body": "You mentioned {symptom_list}. These can be minor, or they can point to wear in the parts of a deck that carry weight. A checklist can't tell which. Only an in-person inspection can. It's quick, and it's usually the first step on any of the paths above."
      },
      "soon": {
        "title": "Get it inspected soon",
        "body": "You mentioned {symptom_list}. These involve how the deck is supported or attached to the house, which is exactly what an inspector wants to see in person. This checker can't tell whether anything is wrong. Until someone takes a look, it's sensible to hold off on heavy loads like a hot tub, large planters or a big gathering."
      }
    },
    "old_wood_tip": "Wood decks over 20 years old can hide wear under the surface. A routine inspection is cheap peace of mind.",
    "selling_note": "Home inspectors look closely at decks. Sorting it out before you list, with an inspection and any repairs, helps you avoid last-minute renegotiation. Many sellers find a targeted repair or resurface is enough; the inspection will tell you.",
    "buying_note": "Just bought? If the home inspection report mentioned the deck, attach a photo of that page below. It helps {business_name} quote faster.",
    "alt_material_line": "In {alt_material}: {alt_low} – {alt_high}",
    "upkeep_nudge": "You said less upkeep matters most. Composite boards need no staining. See the composite prices under Resurface and Replace.",
    "disclaimer": "Estimate only — final price confirmed after a free on-site visit. This checker gives a general guide from your answers. It is not an inspection, and it can't tell whether your deck is structurally sound.",
    "cta_flagged": "Book my deck inspection",
    "cta_default": "Get my exact quote",
    "cta_secondary": "Email me this breakdown",
    "contact_heading_flagged": "Have {business_name} take a look",
    "contact_heading_default": "Want the exact number?",
    "contact_sub": "A free on-site visit confirms which path makes sense and what it costs. No obligation.",
    "included": {
      "maintain": [
        "Cleaning and brightener",
        "Light sanding of rough spots",
        "One coat of stain or sealer (wood)",
        "Re-setting popped fasteners"
      ],
      "repair": [
        "Labor and materials for the items listed",
        "Matching boards as closely as possible",
        "Haul-away of removed material"
      ],
      "resurface": [
        "Removal of old boards",
        "New decking and stair treads",
        "Joist tape on the existing frame",
        "Frame repairs listed above"
      ],
      "replace": [
        "Tear-out and disposal",
        "New footings, framing and decking",
        "Railing and one set of stairs",
        "Permit allowance (where required)"
      ]
    },
    "not_included": [
      "Hidden damage found once boards come up (quoted before any extra work)",
      "New railings when resurfacing (ask for a price)",
      "Permit fees above the allowance",
      "Moving AC units, utilities or hot tubs"
    ],
    "price_drivers": [
      "How much of the frame is still good. This is the big one, and only an inspection confirms it",
      "Deck size and height",
      "Wood vs composite boards",
      "How far any rot has spread",
      "Access under the deck"
    ]
  }
}
$cfg$::jsonb,
  false,
  true
)
on conflict (slug) do update
  set niche = excluded.niche, name = excluded.name, default_config = excluded.default_config, active = true;
```

**Config shape notes**
- `symptoms[].category` is one of `structural`, `board`, `cosmetic` or `none`.
- `symptoms[].safety` is `null`, `"check"` or `"soon"`.
- Only `structural` symptoms carry a `repair` price object.
- `materials[].family` (`wood` | `composite`) selects which per-sq-ft table applies.

---

## 4. Step-by-step flow (7 or 8 steps)

Single-select steps auto-advance 250 ms after a tap. Multi-select steps need Next.

### Step 1: `age`
- **Question:** "How old is your deck?"
- **Helper:** "A rough guess is fine."
- **Input:** single-select cards from `ages` (2 columns).
- **Options:** `lt5`, `5_10`, `10_15`, `15_20`, `20_25`, `25p`, `unsure` ("Not sure — it came with the house").
- **Default:** none. **Validation:** required.

### Step 2: `material`
- **Question:** "What is the deck made of?"
- **Helper:** "Look at the boards you walk on."
- **Input:** single-select cards from `materials`.
- **Options:** `pt`, `cedar`, `composite`, `pvc`, `hardwood`, `unsure`.
- **Default:** none. **Validation:** required.

### Step 3: `size` (+ `sqft` when custom)
- **Question:** "About how big is it?"
- **Helper:** "Include all levels and landings."
- **Input:** single-select cards from `sizes`.
- **Options:** `s` 150 · `m` 250 · `l` 400 · `xl` 600 · `custom`.
- **When `custom` is chosen:** don't auto-advance. Show a slider + number box in sq ft: min 40, max 1500, default 250.
- **Validation:** for custom, integer 40–1500. Clamp, and show "We'll price decks over 1,500 sq ft on site."

### Step 4: `height`
- **Question:** "How high off the ground is it?"
- **Input:** single-select cards from `heights`: `ground`, `standard`, `second`.
- **Default:** none. **Validation:** required.
- **Branch:** `second` raises any `check` safety flag to `soon` (see calc).

### Step 5: `symptoms` (array, the core step)
- **Question:** "What have you noticed? Tick everything that applies."
- **Helper:** "Walk the deck and look underneath if you can. There are no wrong answers."
- **Input:** multi-select cards from `symptoms`, 2 columns, with hints.
- **Options:** `soft_boards`, `cracked_boards`, `popping_nails`, `wobbly_railing`, `wobbly_stairs`, `rot`, `rusted_fasteners`, `ledger`, `bouncy`, `leaning_posts`, `splinters_fading`, `none`.
- **Default:** `[]`.
- **Validation:** at least one card is required. "None of these" counts. `none` is `exclusive`: selecting it clears all others, and selecting any other card clears `none`.
- **Branch:** if any selected symptom has category `structural` or `board`, show Step 6. Otherwise skip to Step 7 and record `extent = null`.
- **Copy guard:** no card or hint may use the forbidden words.

### Step 6: `extent` (conditional)
- **Question:** "How widespread is it?"
- **Helper:** "Think about the problems you ticked: a few boards, or all over?"
- **Input:** single-select cards from `extents`: `few`, `quarter`, `most`, `unsure`.
- **Default:** none. **Validation:** required when shown.

### Step 7: `plans`
- **Question:** "What are your plans for the home?"
- **Helper:** "This changes what's worth spending."
- **Input:** single-select cards from `plans`: `selling_12`, `buying`, `stay_1_5`, `stay_5p`.
- **Default:** none. **Validation:** required.
- **Branch:** `selling_12` shows `copy.selling_note` on the result and sets urgent. `buying` shows `copy.buying_note` above the photo upload.

### Step 8: `priority`
- **Question:** "What matters most to you?"
- **Input:** single-select cards from `priorities`: `cost`, `low_maint`, `new_look`, `solid`.
- **Default:** none. **Validation:** required.
- **Branch:** sets which material is "primary" in the price cards (see calc). It never changes the verdict.
- **After this step:** show a 600 ms "Checking your answers…" shimmer, then the result.

---

## 5. Calculation logic

Pure function `computeDeckVerdict(answers, cfg, prospect)` in `src/tools/deck-repair-or-replace-checker/calc.ts`.
Use the same `r()` rounding as every tool: nearest $100, or nearest $50 when the value is under $2,000.

```ts
const m    = cfg.regional_multipliers[prospect?.state ?? ''] ?? 1.0;
const sqft = size === 'custom' ? answers.sqft : cfg.sizes.find(s => s.id === size).sqft;
const mat  = cfg.materials.find(x => x.id === material); const fam = mat.family;   // 'wood' | 'composite'
const agePts = Math.max(0, cfg.ages.find(a => a.id === age).age_pts + mat.age_pts_adjust);
const h    = cfg.heights.find(x => x.id === height);

const sel  = symptoms.filter(s => s !== 'none').map(id => SYM[id]);
const S = sel.filter(s => s.category === 'structural');
const B = sel.filter(s => s.category === 'board');
const C = sel.filter(s => s.category === 'cosmetic');
const ext = (S.length || B.length) ? cfg.extents.find(e => e.id === extent) : null;

// ---- 1. Replace score
const score = agePts + Σ sel.replace_pts + (ext ? ext.replace_pts : 0);

// ---- 2. Path costs. All lines UNROUNDED × m; totals rounded with r()
const structLines = S.map(s => {
  const f = s.extent_scaled ? ext.rot_factor : 1;
  return { label: s.repair.label, low: s.repair.low*f*m, high: s.repair.high*f*m };
});

maintainLines = [{ label: fam==='wood' ? 'Clean, sand & re-stain/seal' : 'Deep clean & brighten',
  low:  Math.max(sqft*costs.maintain_per_sqft[fam].low,  costs.maintain_min.low) * m,
  high: Math.max(sqft*costs.maintain_per_sqft[fam].high, costs.maintain_min.high) * m }];

repairLines = [...structLines];
if (B.length) repairLines.push({ label:`Replace damaged boards (about ${Math.round(ext.board_share*100)}% of the deck)`,
  low:  sqft*ext.board_share*costs.board_replace_per_sqft[fam].low*m,
  high: sqft*ext.board_share*costs.board_replace_per_sqft[fam].high*m });
if (!repairLines.length) repairLines = [{ label: costs.repair_generic.label,
  low: costs.repair_generic.low*m, high: costs.repair_generic.high*m }];
// repair total = max(sum, repair_min × m), applied separately to low and high

resurfaceLines(f) = [...structLines,                       // a sound frame is a precondition, so structural fixes are included
  { label:`New ${f} boards & stair treads on existing frame (${sqft} sq ft)`,
    low: sqft*costs.resurface_per_sqft[f].low*m, high: sqft*costs.resurface_per_sqft[f].high*m }];

replaceLines(f) = [
  { label:'Tear out & haul away', low:(sqft*costs.demo_per_sqft.low + costs.disposal_flat.low)*m,
                                  high:(sqft*costs.demo_per_sqft.high + costs.disposal_flat.high)*m },
  { label:`New ${f} deck with railing & one stair set (${sqft} sq ft)`,
    low: sqft*costs.replace_per_sqft[f].low*h.replace_multiplier*m,
    high: sqft*costs.replace_per_sqft[f].high*h.replace_multiplier*m }];
// replace total = max(sum, replace_min × m), applied separately to low and high

// Totals: total.low = r(max(Σ low, min.low*m)), total.high = r(max(Σ high, min.high*m)). Only repair and replace have a min.
// Compute resurface and replace for BOTH f='wood' and f='composite'.

// ---- 3. Primary material (which price is shown big; the other shows as the alt line)
const primary = (fam === 'composite' || ['low_maint','new_look'].includes(priority)) ? 'composite' : 'wood';

// ---- 4. Verdict (first match wins)
let verdict, reason = null;
if (score >= rules.replace_threshold)                     { verdict = 'replace'; reason = 'score'; }
else if (S.length)                                        verdict = 'repair';
else if (B.length) verdict = (ext.id === 'most' || (['quarter','unsure'].includes(ext.id) && agePts >= rules.resurface_min_age_pts))
                             ? 'resurface' : 'repair';
else if (C.length) verdict = (agePts >= rules.cosmetic_resurface_min_age_pts && fam === 'wood') ? 'resurface' : 'maintain';
else               verdict = 'maintain';

const mid = t => (t.low + t.high) / 2;
if (verdict === 'repair'    && mid(repair)          >= rules.repair_to_replace_ratio    * mid(replace[primary])) { verdict = 'replace'; reason = 'repair_ratio'; }
if (verdict === 'resurface' && mid(resurface[primary]) >= rules.resurface_to_replace_ratio * mid(replace[primary])) { verdict = 'replace'; reason = 'resurface_ratio'; }

// ---- 5. Safety flag (never a verdict on safety. It only drives the "get it inspected" box.)
let flag = null;                                          // null | 'check' | 'soon'
for (const s of sel) {
  let lv = s.safety;
  if (s.id === 'rot' && ext && s.safety_soon_if_extent.includes(ext.id)) lv = 'soon';
  if (lv === 'soon') flag = 'soon'; else if (lv === 'check' && !flag) flag = 'check';
}
if (flag === 'check' && h.raises_flag) flag = 'soon';

// ---- 6. Extras
const oldWoodTip = (verdict === 'maintain' && fam === 'wood' && agePts >= 3 && !flag);
const urgent     = (flag === 'soon') || (plans === 'selling_12');
const leadValue  = Math.round(mid(verdictTotal));         // verdict path, primary material for resurface/replace
```

### Edge cases
- **Only "None of these":** verdict `maintain`, no flag, no extent step. If the wood deck is 20+ years old, show `copy.old_wood_tip` (info styling, not amber).
- **`unsure` age** scores 2 points. **`unsure` material** is treated as wood.
- **Composite fading only:** `maintain` (deep clean), because the cosmetic resurface rule needs `fam === 'wood'`.
- **The ratio rule can flip `repair` to `replace`.** When it does, show the `copy.reason_repair_ratio` line under the verdict so the jump is explained.
- **A safety symptom on a second-story deck** is always flagged `soon`.
- **The flag does not change the verdict.** A `maintain` verdict can't carry a flag, because every safety symptom is structural or board, so the verdict is at least `repair`.
- **No prospect:** m = 1.0 and "your area".
- **Every rendered string** (verdict, flag, notes, line labels, email) must pass a check against `rules.forbidden_result_words`. In dev builds, throw if one appears. In production, log `pipeline_error` with `meta.forbidden_word`.

### Worked examples (verified against this config)

**Example 1: 25+ year PT deck, rot + soft boards + wobbly railing, Colorado (m = 1.08)**
Answers: age `25p`, material `pt`, size `m` (250), height `standard`, symptoms `[soft_boards, rot, wobbly_railing, splinters_fading]`, extent `quarter`, plans `stay_5p`, priority `low_maint`.
- agePts 4. Score = 4 + (1 + 2 + 1 + 0) + 1 = **9 ≥ 7**, so the verdict is **Replace** (reason `score`).
- Primary = `composite` (priority low_maint).
- Flag = **soon** (rot with extent quarter). Urgent = true.

| Path | Primary | Alt line |
|---|---|---|
| Maintain | $700 – $1,200 | — |
| Repair | $3,500 – $10,300 (rot framing $1,950–$6,500 · railing $550–$1,950 · boards ~25% $1,000–$1,900) | — |
| Resurface | Composite $10,000 – $20,600 | Wood $7,300 – $16,500 |
| **Replace ✓** | **Composite $17,200 – $25,700** (tear-out $1,500–$2,800 · new deck $15,700–$23,000) | Wood $12,300 – $19,000 |

Meta `value` = **21450**.

**Example 2: 15–20 yr PT deck, cracked boards + fading, selling, North Carolina (m = 0.95)**
Answers: `15_20`, `pt`, `l` (400), `standard`, `[cracked_boards, splinters_fading]`, extent `quarter`, plans `selling_12`, priority `cost`.
- agePts 2. Score = 2 + 0 + 1 = 3.
- No structural symptoms. Board symptoms with extent quarter and agePts ≥ 2 give **Resurface**.
- Ratio check: 9,100 vs 0.7 × 21,650 = 15,155, so it stays Resurface.
- Primary = `wood`. Flag = **none**. Urgent = true (selling). Show `copy.selling_note`.

| Path | Primary | Alt |
|---|---|---|
| Maintain | $950 – $1,700 | — |
| Repair | $1,450 – $2,700 (boards ~25%) | — |
| **Resurface ✓** | **Wood $6,800 – $11,400** | Composite $10,600 – $17,100 |
| Replace | Wood $17,100 – $26,200 | Composite $23,900 – $35,700 |

Meta `value` = **9100**.

**Example 3: 8-year composite, second story, wobbly railing only, New Jersey (m = 1.20)**
Answers: `5_10`, `composite`, `s` (150), `second`, `[wobbly_railing]`, extent `few`, `stay_1_5`, `solid`.
- agePts max(0, 0 − 1) = 0. Score = 0 + 1 + 0 = 1, so the verdict is **Repair**.
- Ratio: 1,400 vs 0.5 × 17,800, so it stays Repair.
- Primary = `composite` (family).
- Flag: wobbly_railing = check, and second story raises it to **soon**. Urgent = true.

| Path | Primary | Alt |
|---|---|---|
| Maintain | $550 – $950 (deep clean) | — |
| **Repair ✓** | **$600 – $2,200** (Re-secure or rebuild railing sections) | — |
| Resurface | Composite $5,600 – $10,300 | Wood $3,800 – $7,600 |
| Replace | Composite $14,300 – $21,300 | Wood $10,800 – $15,700 |

Meta `value` = **1400**.

---

## 6. Result screen

1. **Eyebrow:** `copy.result_title` ("Our read on your deck").
2. **Verdict hero card** (brand-color border):
   - Lucide icon from `copy.verdicts[verdict].icon`.
   - Big label ("Replace it").
   - `headline` in bold, then `body`.
   - If `reason` is `repair_ratio` or `resurface_ratio`, add the matching `copy.reason_*` line in gray.
   - Then the verdict's price range in the big two-tone style with the range bar (§8).
   - Subtitle: `copy.result_subtitle`.
3. **Safety box** (only when `flag`):
   - Amber (#D97706) left border, lucide `ShieldAlert` icon.
   - Title and body from `copy.safety[flag]`, with `{symptom_list}` = lower-cased labels of the selected safety symptoms joined as "a, b and c".
   - Never red. Never the words "unsafe" or "danger".
   - Button inside: "Book my deck inspection" scrolls to the contact card.
4. **"All four paths, side by side":**
   - Four cards: 2×2 on mobile, 4 across on desktop. Order: maintain, repair, resurface, replace.
   - Each card: `path_titles[p]`, `path_blurbs[p]`, the range (primary material), and for resurface/replace the alt line `copy.alt_material_line`.
   - The verdict card gets a "Our pick" badge and the brand-color border.
   - Tapping a card expands its line items (same table style as the estimator) and its `copy.included[p]` list.
5. **Notes** (stacked info callouts, as applicable):
   - `selling_note` (plans = selling_12)
   - `upkeep_nudge` (priority = low_maint and fam = wood)
   - `old_wood_tip`
6. **What's not included:** `copy.not_included`.
7. **What changes your price:** `copy.price_drivers`.
8. **Disclaimer:** `copy.disclaimer`, under the hero card and at the bottom.
9. Contact card (section 7).

---

## 7. Contact card

- **Heading:** `copy.contact_heading_flagged` when `flag`, else `copy.contact_heading_default`. **Sub:** `copy.contact_sub`.
- **Primary submit:** `copy.cta_flagged` **"Book my deck inspection"** when `flag`, else `copy.cta_default` **"Get my exact quote"**.
- **Secondary:** "Email me this breakdown" (`contact.intent='email_breakdown'`).
- **Extra fields:**
  1. Photo upload (standard §5.4), labeled "Photos help a lot: the problem spots and underneath, if you can (optional)". When `plans = buying`, show `copy.buying_note` above it.
  2. `access`: segmented "Can we see underneath the deck?" Yes / Partly / No. Optional.
  3. `deadline`: date picker, "Need it sorted by a date? (closing, event…) (optional)".
- **Urgency:** `result.urgent` (flag `soon` OR selling_12) OR `deadline` within 30 days.
- **Thank-you variant:**
  - Flagged: "{business_name} has your request and will reach out to set up an inspection."
  - Not flagged: "{business_name} has your request and will confirm the best path after a quick visit."
  - Use the platform's "today" wording when urgent.
  - Summary card: verdict, its range, symptoms ticked, and age/material/size.

---

## 8. Business notification email

- **Subject:** `New Old-Deck Checker request — {contact.name}, {city or zip}`. Prefix `🔴 URGENT · ` when urgent.
- **Headline:** `{contact.name}'s {age label} {material label} deck: our read is "{verdict label}" ({range})`
- **Sub-headline:**
  - `Symptoms: {labels or "none"} · Extent: {extent label or "—"} · Plans: {plans label}`
  - When flagged, add a second line in amber: `Inspection suggested: they mentioned {symptom_list}.`
  - Never use the forbidden words in the email either.
- Then the platform blocks, plus the four-path table.

---

## 9. Personalization hooks (`config_overrides["deck-repair-or-replace-checker"]`)

| Key | Use |
|---|---|
| `costs.*` (any) | Their real maintain, repair, resurface and replace rates, demo and minimums |
| `symptoms[].repair` | Their price for each specific repair (replace the whole `symptoms` array) |
| `rules.replace_threshold`, `rules.repair_to_replace_ratio`, `rules.resurface_to_replace_ratio` | How readily they recommend a rebuild |
| `heights[].replace_multiplier` | Height pricing |
| `regional_multipliers` | Their state factor |
| `copy.verdicts.*`, `copy.included.*`, `copy.not_included`, `copy.contact_sub` | Their voice and scope. Also mention a paid or free inspection if they offer one |
| `copy.cta_flagged` | e.g. "Book my free deck inspection" if their inspection is free |

`rules.forbidden_result_words` can be added to, but never emptied. The admin UI should reject removing a default word.

---

## 10. Meta events

- **`ToolResult`:** `{tool:'deck-repair-or-replace-checker', niche:'deck', verdict, flag: flag ?? 'none', age, material, symptom_count}`
- **`Lead`:** `value` = midpoint of the verdict path's total, using the primary material for resurface/replace (examples: 21450 / 9100 / 1400). `currency:'USD'`.
  - For §6.5 CAPI, treat this tool as an estimator: send `custom_data.value` = the same number.
- **`ToolPathExpand`** (custom): fired when a path card is expanded, `{tool, path}`.

---

## 11. QA checklist

1. **Forbidden words:** tick every symptom at once, at second story, 25+ years, extent most. Search the rendered DOM, the email HTML and the thank-you for each word in `forbidden_result_words`. **Zero matches.**
2. Examples 1–3 reproduce the verdict, flag, every path range and the Meta value exactly. Add them as unit tests.
3. "None of these" clears the other cards and vice versa. With only "None" or only cosmetic, Step 6 is skipped and Back from Step 7 returns to Step 5.
4. Age `10_15`, `cedar`, size `m`, height `ground`, only splinters/fading, TX → **Maintain**, no safety box, maintain range $600 – $1,050, Meta value 825.
5. 20–25 yr PT deck with only `ledger`, extent `few`, PA → **Repair** $1,850 – $4,600, flag **soon**, amber box shown, CTA reads "Book my deck inspection".
6. The ratio rule: set `rules.repair_to_replace_ratio` to `0.05` via an override. Example 3 then flips to Replace and shows the reason line.
7. The safety box is amber, never red, and only appears when `flag` is set.
8. All four path cards show prices **before** the contact form. Resurface and replace show both materials.
9. Submitting stores `result = {verdict, reason, flag, score, paths:{...}, primary, urgent}`, emails the business with the headline format, and fires Lead with the same event_id in Pixel and CAPI.
10. Demo route (no prospect) runs with m = 1.0, says "your area" and has no `{business_name}` placeholders left unfilled.
11. 360 px: the four path cards are a 2×2 grid with no horizontal scroll, and the expanded tables wrap.
