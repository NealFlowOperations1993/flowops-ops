# Tool spec: Deck Cost Estimator (deck · tool 1)

> **Paste this into Lovable as ONE prompt, after the platform spec is built.** It assumes everything in
> `00_PLATFORM_SPEC.md` already exists: ToolShell (§5), routing (§2), tables (§3), personalization and
> deep-merge of `config_overrides` (§4), the `submit-tool` pipeline (§6), the Meta Pixel (§7), the design system (§8)
> and the regional multipliers (§9). Do **not** rebuild any of that. Build only what this file describes.
> Read every config value from the merged config. Never hardcode a price in a component.

---

## 1. Header

| Field | Value |
|---|---|
| **slug** | `deck-cost-estimator` |
| **niche** | `deck` |
| **name** | Deck Cost Estimator |
| **H1 (on-page promise)** | What will your new deck cost? |
| **Sub-promise** | Get an itemized price range in about 45 seconds — before you talk to anyone. |
| **Target time to result** | **45 seconds** (8 taps, no typing needed unless "I know my size") |
| **Trust row** (ToolShell §5.1) | "★ Free · No signup to see your price · Takes ~45s" |
| **Route examples** | `/deck-cost-estimator` (demo), `/deck-cost-estimator/{prospect_slug}` |

> Importer note (§4): for `niche = 'deck'`, set `tool_slugs = ['deck-cost-estimator','deck-repair-or-replace-checker']`.
> `tools.niche` is free text. The 9-niche list in the platform's SQL comment is not a constraint.

---

## 2. Why this tool (VOC: `docs/voc/VOC_deck.md`)

- **Price is the dominant buying question.** Buyers anchor on their own numbers: *"a large deck with a $10k budget"*, *"my possibly $25,000 deck"*. They also collect 2–5 bids. An instant range meets them at that moment.
- **Price shock vs other bids is pain #1 (~9 reviews).** *"Estimate was over 15k higher than the other 2 I received."* / *"Trex materials cost 10K and they wanted 30k to build a small deck."* An itemized range shows what drives the number.
- **Itemized pricing is the #1 win (~12 reviews).** *"we appreciated the break out of all the costs involved so there were no surprises."* / *"Estimate was clear and reasonable compared with others."* That's why the result is a line-item table, not one number.
- **Scope ambiguity is pain #6 (~5).** *"they tried to say the quote for the stain… only included stain on the repaired piece of wood."* That's why the result has an explicit included / not-included list.
- **Ghosting after the estimate visit is pain #2 (~9).** *"I was told that I would get renderings in an email… I never received a response."* The homeowner sees the price immediately, and the business gets the lead instantly (platform §6.3).
- **Fast quote wins (~6).** *"Michael provided a same-day quote"* / *"We asked for a virtual quote on our first level deck."*
- **Timeline matters.** *"This is the summer I have a hot tub, bbq, and gorgeous new deck."* That's why there's a hot-tub-ready extra, a build-time line and a timeline step.
- **Cross-niche price fear (VOC README pattern 2).** Show the price before asking for contact details.

---

## 3. Seed SQL for the `tools` table

Paste exactly. Prices are **2025–2026 US installed defaults that each business tunes** in `/admin`
(through `config_overrides`). `regional_multipliers` is the platform §9 table, copied in because §4 reads it from `default_config`.

```sql
insert into tools (slug, niche, name, default_config, is_finance, active)
values (
  'deck-cost-estimator',
  'deck',
  'Deck Cost Estimator',
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
  "project_types": [
    {
      "id": "new",
      "label": "Build a new deck",
      "icon": "Hammer",
      "hint": "Nothing there now, or just a patio slab"
    },
    {
      "id": "replace",
      "label": "Replace my old deck",
      "icon": "RefreshCw",
      "hint": "Tear out the old one and build new"
    }
  ],
  "demo": {
    "label": "Tear out & haul away old deck",
    "per_sqft": {
      "low": 4,
      "high": 7
    },
    "disposal_flat": {
      "low": 400,
      "high": 800
    }
  },
  "size_presets": [
    {
      "id": "s",
      "label": "Small",
      "icon": "Square",
      "hint": "about 12 × 12 ft · 144 sq ft",
      "width_ft": 12,
      "depth_ft": 12
    },
    {
      "id": "m",
      "label": "Medium",
      "icon": "Grid2x2",
      "hint": "about 16 × 12 ft · 192 sq ft",
      "width_ft": 16,
      "depth_ft": 12
    },
    {
      "id": "l",
      "label": "Large",
      "icon": "Grid3x3",
      "hint": "about 20 × 16 ft · 320 sq ft",
      "width_ft": 20,
      "depth_ft": 16
    },
    {
      "id": "xl",
      "label": "Extra large",
      "icon": "LayoutGrid",
      "hint": "about 24 × 20 ft · 480 sq ft",
      "width_ft": 24,
      "depth_ft": 20
    },
    {
      "id": "custom",
      "label": "I know my size",
      "icon": "Ruler",
      "hint": "Enter width and depth"
    }
  ],
  "size_limits": {
    "width_min": 6,
    "width_max": 60,
    "depth_min": 4,
    "depth_max": 40,
    "area_min": 48,
    "area_max": 1500,
    "custom_default_width": 16,
    "custom_default_depth": 12
  },
  "heights": [
    {
      "id": "ground",
      "label": "Ground level",
      "icon": "Minus",
      "hint": "Under 2 ft off the ground",
      "multiplier": 0.92,
      "steps_per_stair": 2,
      "landing": false,
      "build_days_add": [
        0,
        0
      ]
    },
    {
      "id": "standard",
      "label": "Raised",
      "icon": "ArrowUp",
      "hint": "2–6 ft · off a first-floor door",
      "multiplier": 1.0,
      "steps_per_stair": 6,
      "landing": false,
      "build_days_add": [
        0,
        0
      ]
    },
    {
      "id": "second",
      "label": "Second story",
      "icon": "ArrowUpToLine",
      "hint": "6–12 ft · off an upper-floor door",
      "multiplier": 1.25,
      "steps_per_stair": 13,
      "landing": true,
      "build_days_add": [
        2,
        3
      ]
    },
    {
      "id": "elevated",
      "label": "Very high",
      "icon": "Mountain",
      "hint": "Over 12 ft, or a steep drop-off",
      "multiplier": 1.45,
      "steps_per_stair": 20,
      "landing": true,
      "build_days_add": [
        2,
        4
      ]
    }
  ],
  "materials": [
    {
      "id": "pt",
      "label": "Pressure-treated wood",
      "icon": "TreePine",
      "hint": "Lowest upfront cost · stain every 2–3 years",
      "per_sqft": {
        "low": 30,
        "high": 45
      },
      "per_step": {
        "low": 125,
        "high": 200
      },
      "materials_share": 0.4,
      "default_railing": "wood"
    },
    {
      "id": "cedar",
      "label": "Cedar",
      "icon": "TreeDeciduous",
      "hint": "Natural look · stain every 2–3 years",
      "per_sqft": {
        "low": 40,
        "high": 58
      },
      "per_step": {
        "low": 150,
        "high": 240
      },
      "materials_share": 0.45,
      "default_railing": "wood"
    },
    {
      "id": "composite",
      "label": "Composite (Trex, TimberTech)",
      "icon": "Layers",
      "hint": "Most popular · no staining",
      "per_sqft": {
        "low": 50,
        "high": 75
      },
      "per_step": {
        "low": 200,
        "high": 325
      },
      "materials_share": 0.55,
      "default_railing": "composite"
    },
    {
      "id": "pvc",
      "label": "PVC / premium capped",
      "icon": "Sparkles",
      "hint": "Top fade & stain resistance",
      "per_sqft": {
        "low": 60,
        "high": 90
      },
      "per_step": {
        "low": 225,
        "high": 350
      },
      "materials_share": 0.58,
      "default_railing": "aluminum"
    },
    {
      "id": "hardwood",
      "label": "Tropical hardwood (Ipe)",
      "icon": "Gem",
      "hint": "Very dense · 40+ year life",
      "per_sqft": {
        "low": 65,
        "high": 100
      },
      "per_step": {
        "low": 250,
        "high": 400
      },
      "materials_share": 0.55,
      "default_railing": "aluminum"
    }
  ],
  "railings": [
    {
      "id": "none",
      "label": "No railing",
      "icon": "Ban",
      "hint": "Only for decks under 30 in. high",
      "per_lf": {
        "low": 0,
        "high": 0
      }
    },
    {
      "id": "wood",
      "label": "Wood",
      "icon": "TreePine",
      "hint": "Matches a wood deck",
      "per_lf": {
        "low": 25,
        "high": 45
      }
    },
    {
      "id": "composite",
      "label": "Composite",
      "icon": "Layers",
      "hint": "Low-maintenance, matches composite",
      "per_lf": {
        "low": 45,
        "high": 80
      }
    },
    {
      "id": "aluminum",
      "label": "Metal / aluminum",
      "icon": "Fence",
      "hint": "Slim black or white balusters",
      "per_lf": {
        "low": 55,
        "high": 95
      }
    },
    {
      "id": "cable",
      "label": "Cable",
      "icon": "Cable",
      "hint": "Thin steel cables · open view",
      "per_lf": {
        "low": 85,
        "high": 150
      }
    },
    {
      "id": "glass",
      "label": "Glass panels",
      "icon": "RectangleVertical",
      "hint": "Clear view · highest cost",
      "per_lf": {
        "low": 140,
        "high": 240
      }
    }
  ],
  "railing_rules": {
    "stair_opening_ft": 4,
    "guard_height_warning_heights": [
      "standard",
      "second",
      "elevated"
    ]
  },
  "stairs": [
    {
      "id": "0",
      "label": "No stairs",
      "icon": "Ban",
      "hint": "Deck is at door level only",
      "sets": 0
    },
    {
      "id": "1",
      "label": "One set",
      "icon": "TrendingUp",
      "hint": "Most common",
      "sets": 1
    },
    {
      "id": "2",
      "label": "Two sets",
      "icon": "ChevronsUp",
      "hint": "e.g. to the yard and the driveway",
      "sets": 2
    }
  ],
  "landing_per_set": {
    "low": 1500,
    "high": 3000
  },
  "extras": [
    {
      "id": "roof_cover",
      "label": "Covered (solid roof)",
      "icon": "Umbrella",
      "hint": "Roof over the deck, tied into the house",
      "pricing": "per_sqft",
      "price": {
        "low": 35,
        "high": 70
      },
      "excludes": [
        "pergola"
      ],
      "build_days_add": [
        3,
        5
      ]
    },
    {
      "id": "screened",
      "label": "Screened-in porch",
      "icon": "Grid3x3",
      "hint": "Screens and a door · needs a roof (we add it)",
      "pricing": "per_sqft",
      "price": {
        "low": 15,
        "high": 30
      },
      "requires": [
        "roof_cover"
      ],
      "build_days_add": [
        2,
        3
      ]
    },
    {
      "id": "pergola",
      "label": "Pergola",
      "icon": "Grid2x2",
      "hint": "Open beams for partial shade",
      "pricing": "flat",
      "price": {
        "low": 4500,
        "high": 10000
      },
      "excludes": [
        "roof_cover",
        "screened"
      ],
      "build_days_add": [
        1,
        2
      ]
    },
    {
      "id": "lighting",
      "label": "Built-in lighting",
      "icon": "Lightbulb",
      "hint": "Post-cap, stair and rail lights",
      "pricing": "flat",
      "price": {
        "low": 1200,
        "high": 2800
      },
      "build_days_add": [
        0,
        1
      ]
    },
    {
      "id": "benches",
      "label": "Built-in benches",
      "icon": "Armchair",
      "hint": "About 12 ft of seating",
      "pricing": "flat",
      "price": {
        "low": 1200,
        "high": 2800
      },
      "build_days_add": [
        0,
        1
      ]
    },
    {
      "id": "skirting",
      "label": "Skirting",
      "icon": "PanelBottom",
      "hint": "Closes in the space under the deck",
      "pricing": "per_lf_perimeter",
      "price": {
        "low": 25,
        "high": 45
      },
      "hidden_for_heights": [
        "ground"
      ],
      "build_days_add": [
        1,
        1
      ]
    },
    {
      "id": "hot_tub",
      "label": "Hot-tub ready",
      "icon": "Bath",
      "hint": "Extra footings and framing for the weight",
      "pricing": "flat",
      "price": {
        "low": 1500,
        "high": 4000
      },
      "build_days_add": [
        1,
        1
      ]
    }
  ],
  "permit": {
    "label": "Permit & drawings (where required)",
    "low": 400,
    "high": 1200
  },
  "min_job": {
    "label": "Small-job minimum",
    "low": 4000,
    "high": 6000
  },
  "build_days_tiers": [
    {
      "max_sqft": 200,
      "days": [
        3,
        5
      ]
    },
    {
      "max_sqft": 400,
      "days": [
        5,
        8
      ]
    },
    {
      "max_sqft": 700,
      "days": [
        7,
        12
      ]
    },
    {
      "max_sqft": 100000,
      "days": [
        10,
        16
      ]
    }
  ],
  "replace_build_days_add": [
    1,
    2
  ],
  "timelines": [
    {
      "id": "asap",
      "label": "As soon as possible",
      "icon": "Zap",
      "hint": "Within the next month",
      "urgent": true
    },
    {
      "id": "1_3",
      "label": "In 1–3 months",
      "icon": "CalendarClock",
      "hint": "",
      "urgent": false
    },
    {
      "id": "3_6",
      "label": "In 3–6 months",
      "icon": "Calendar",
      "hint": "",
      "urgent": false
    },
    {
      "id": "budgeting",
      "label": "Just getting a price",
      "icon": "Calculator",
      "hint": "No date yet",
      "urgent": false
    }
  ],
  "budget_bands": [
    {
      "id": "u10",
      "label": "Under $10k"
    },
    {
      "id": "10_20",
      "label": "$10k–$20k"
    },
    {
      "id": "20_35",
      "label": "$20k–$35k"
    },
    {
      "id": "35_60",
      "label": "$35k–$60k"
    },
    {
      "id": "60p",
      "label": "$60k+"
    },
    {
      "id": "unsure",
      "label": "Not sure yet"
    }
  ],
  "copy": {
    "h1": "What will your new deck cost?",
    "sub": "Get an itemized price range in about 45 seconds — before you talk to anyone.",
    "result_title": "Your estimated deck price",
    "result_subtitle": "{area} sq ft {material_label} deck · {height_label} · prices typical for {city}",
    "materials_split": "About {mat_pct}% of this is materials and {labor_pct}% is labor.",
    "build_time": "Typical build: about {days_low}–{days_high} working days on site.",
    "permit_note": "Permits, where required, usually add 1–4 weeks before work starts.",
    "guard_warning": "Most building codes require a guard rail when a deck is more than 30 inches off the ground. We've kept your choice, but your builder will confirm.",
    "screened_note": "A screened porch needs a roof, so we've added one.",
    "disclaimer": "Estimate only — final price confirmed after a free on-site visit. Ranges are typical installed prices for {city_or_your_area} and assume normal soil, normal access and an attached deck.",
    "cta_primary": "Get my exact quote",
    "cta_secondary": "Email me this breakdown",
    "contact_heading": "Want the exact number?",
    "contact_sub": "{business_name} will confirm your price after a free on-site visit. No obligation.",
    "included": [
      "Footings, posts, beams and joists (framing to code)",
      "Decking boards and hidden or face fasteners",
      "Joist tape / flashing where the deck meets the house",
      "Railing and stairs as selected",
      "Job-site cleanup",
      "Workmanship warranty (ask {business_name} for terms)"
    ],
    "not_included": [
      "Permit fees above the allowance shown",
      "Moving utilities, AC units or gas lines in the way",
      "Rock, roots or poor soil found when digging footings",
      "Electrical service upgrades (lighting runs off a standard outlet)",
      "Furniture, grills, hot tub itself",
      "Staining a wood deck after it has weathered (usually 3–6 months later)"
    ],
    "price_drivers": [
      "Size — the biggest driver; every extra 100 sq ft adds roughly {per100_low}–{per100_high}",
      "Height — second-story decks need taller posts, bigger footings and longer stairs",
      "Material — composite and PVC cost more upfront but skip the staining",
      "Railing — glass and cable cost 3–5× a wood railing per foot",
      "Site — slopes, tight access and hard digging add labor",
      "Roof or screen — a covered deck is close to building a small room"
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

**Config shape notes for the builder**
- Every option object has `id`, `label`, `icon` (a lucide-react component name), and `hint`. The hint is the one-line card subtext and may be `""`.
- Every price is `{low, high}` in USD **before** the regional multiplier.
- `copy.*` strings use `{placeholders}`. Fill them from the prospect (`business_name`, `city`) or from the computed result. When `city` is null, use `city_or_your_area` = "your area".

---

## 4. Step-by-step flow (8 steps)

ToolShell provides the progress bar, Back/Next, Enter-to-advance, `?s=` URL state and sessionStorage (§5.2).
**Single-select card steps auto-advance 250 ms after a tap.** Multi-select steps need Next.
Store answers under the field ids below.

### Step 1: `project_type`
- **Question:** "Is this a new deck or a replacement?"
- **Helper:** "Replacing includes tearing out and hauling away the old deck."
- **Input:** single-select cards (2 columns), from `project_types`.
- **Options:** `new` "Build a new deck" (Hammer) · `replace` "Replace my old deck" (RefreshCw).
- **Default:** none selected. **Validation:** required.
- **Branch:** none. `replace` adds the demo line in the calculation.

### Step 2: `size` (+ `width_ft`, `depth_ft` when custom)
- **Question:** "About how big?"
- **Helper:** "Width runs along the house; depth is how far it sticks out. A guess is fine."
- **Input:** single-select cards from `size_presets` (2 columns; the 5th card spans both columns).
- **Options:** `s` Small 12×12 · `m` Medium 16×12 · `l` Large 20×16 · `xl` Extra large 24×20 · `custom` "I know my size".
- **Default:** `m` is pre-highlighted but not selected. The user must tap.
- **When `custom` is chosen:** do NOT auto-advance. Reveal two slider + number-box pairs (§8):
  - **Width (ft):** min `width_min` 6, max `width_max` 60, default 16.
  - **Depth (ft):** min `depth_min` 4, max `depth_max` 40, default 12.
  - Show the live "= {W×D} sq ft" under them.
- **Validation:** integers only. Area must be `area_min` 48 – `area_max` 1500.
  - Under 48: "That's smaller than most decks. Try at least 6 × 8 ft."
  - Over 1500: "For decks over 1,500 sq ft, {business_name} will price it on site. Enter 1,500 for now." Clamp to the limit.
- **Branch:** none.

### Step 3: `height`
- **Question:** "How high off the ground?"
- **Helper:** "Measure from the ground to the top of the deck surface, at its highest point."
- **Input:** single-select cards from `heights`.
- **Options:** `ground` Ground level (<2 ft) · `standard` Raised (2–6 ft) · `second` Second story (6–12 ft) · `elevated` Very high (12 ft+).
- **Default:** none. **Validation:** required.
- **Branch:**
  - `ground` sets Step 5's pre-selected default to `none` and Step 6's to `0`.
  - Otherwise Step 5 pre-selects the material's `default_railing` and Step 6 pre-selects `1`.
  - `ground` hides the `skirting` extra in Step 7.

### Step 4: `material`
- **Question:** "Which decking material?"
- **Helper:** "Not sure? Composite is the most popular choice. You can change it on the result screen."
- **Input:** single-select cards from `materials` (show the hint line).
- **Options:** `pt`, `cedar`, `composite`, `pvc`, `hardwood`.
- **Default:** none. **Validation:** required.
- **Branch:** sets Step 5's default (`default_railing`) unless height is `ground`.

### Step 5: `railing`
- **Question:** "What kind of railing?"
- **Helper:** "Railing runs along the open sides, not against the house."
- **Input:** single-select cards from `railings`.
- **Options:** `none`, `wood`, `composite`, `aluminum`, `cable`, `glass`.
- **Default:** pre-selected per the Step 3/4 branch. The user can just tap Next.
- **Validation:** required.
- **Branch:** if `none` is chosen and `height` is in `railing_rules.guard_height_warning_heights`, show `copy.guard_warning` as an amber inline note. **Do not block.**

### Step 6: `stairs`
- **Question:** "How many sets of stairs?"
- **Helper:** "Each set goes from the deck down to the yard." For `second`/`elevated`, append: "Stairs this tall usually need a landing — we've included one."
- **Input:** single-select cards from `stairs`: `0`, `1`, `2`.
- **Default:** pre-selected per the Step 3 branch.
- **Validation:** required.

### Step 7: `extras` (array)
- **Question:** "Any extras?"
- **Helper:** "Pick any that apply — or skip."
- **Input:** multi-select cards from `extras`.
- **Options:** `roof_cover`, `screened`, `pergola`, `lighting`, `benches`, `skirting` (hidden when height = `ground`), `hot_tub`.
- **Default:** `[]`. **Validation:** optional. The Next button reads "Skip" while nothing is selected.
- **Rules (apply live on tap):**
  - Selecting `screened` also selects `roof_cover` and shows `copy.screened_note` as a toast.
  - Deselecting `roof_cover` while `screened` is selected also deselects `screened`.
  - `pergola` and `roof_cover`/`screened` exclude each other (`excludes`). Selecting one greys out the other with the hint "Can't combine with a roof".

### Step 8: `timeline`
- **Question:** "When would you like it built?"
- **Helper:** "Good builders book up 4–8 weeks ahead in spring and summer."
- **Input:** single-select cards from `timelines`.
- **Options:** `asap`, `1_3`, `3_6`, `budgeting`.
- **Default:** none. **Validation:** required.
- **Branch:** `asap` sets `result.urgent = true`, which drives the thank-you "today" wording and the red urgency flag in the email (§6.3).
- **After this step**, show a 600 ms "Pricing your deck…" shimmer, then the result.

---

## 5. Calculation logic

All math runs client-side in a pure function `computeDeckEstimate(answers, cfg, prospect)` in `src/tools/deck-cost-estimator/calc.ts`. Unit-test it with the three worked examples below.

```ts
const m = cfg.regional_multipliers[prospect?.state ?? ''] ?? 1.0;   // demo (no prospect) → 1.0

// rounding: nearest $100, or nearest $50 when the value is under $2,000
const r = (x) => (x < cfg.rounding.small_threshold
                  ? Math.round(x / cfg.rounding.step_small) * cfg.rounding.step_small
                  : Math.round(x / cfg.rounding.step_large) * cfg.rounding.step_large);

// 1. Geometry
const { W, D } = size === 'custom' ? { W: width_ft, D: depth_ft }
               : { W: preset.width_ft, D: preset.depth_ft };
const area = W * D;
const sets = stairsOption.sets;                         // 0 | 1 | 2

// 2. Line items. Each holds UNROUNDED {low, high} already × m
lines = [];
lines.push({ id:'deck', label:`Deck framing, footings & ${mat.label} decking (${area} sq ft)`,
             low: area * mat.per_sqft.low  * height.multiplier * m,
             high: area * mat.per_sqft.high * height.multiplier * m });

if (railing.id !== 'none') {
  const lf = Math.max(0, W + 2*D - cfg.railing_rules.stair_opening_ft * sets);  // house side has no rail
  lines.push({ id:'railing', label:`${railing.label} railing (${lf} linear ft)`,
               low: lf*railing.per_lf.low*m, high: lf*railing.per_lf.high*m });
}

if (sets > 0) {
  const steps = height.steps_per_stair;
  let lo = sets*steps*mat.per_step.low, hi = sets*steps*mat.per_step.high;
  if (height.landing) { lo += sets*cfg.landing_per_set.low; hi += sets*cfg.landing_per_set.high; }
  lines.push({ id:'stairs', label:`Stairs (${sets} set${sets>1?'s':''}, ~${steps} steps each${height.landing?', with landing':''})`,
               low: lo*m, high: hi*m });
}

const ex = new Set(extras); if (ex.has('screened')) ex.add('roof_cover');
for (const e of cfg.extras) if (ex.has(e.id)) {       // keep config order
  const q = e.pricing === 'per_sqft' ? area
          : e.pricing === 'per_lf_perimeter' ? (W + 2*D) : 1;
  const unit = e.pricing === 'per_sqft' ? ` (${area} sq ft)`
             : e.pricing === 'per_lf_perimeter' ? ` (${W+2*D} linear ft)` : '';
  lines.push({ id:e.id, label:e.label+unit, low:q*e.price.low*m, high:q*e.price.high*m });
}

if (project_type === 'replace')
  lines.push({ id:'demo', label: cfg.demo.label,
               low:(area*cfg.demo.per_sqft.low  + cfg.demo.disposal_flat.low)*m,
               high:(area*cfg.demo.per_sqft.high + cfg.demo.disposal_flat.high)*m });

lines.push({ id:'permit', label:cfg.permit.label, low:cfg.permit.low*m, high:cfg.permit.high*m });

// 3. Small-job minimum, compared on unrounded sums
let sumL = Σ lines.low, sumH = Σ lines.high;
const minL = cfg.min_job.low*m, minH = cfg.min_job.high*m;
if (sumL < minL || sumH < minH) {
  lines.push({ id:'min_job', label:cfg.min_job.label,
               low:Math.max(0, minL - sumL), high:Math.max(0, minH - sumH) });
  sumL = Σ lines.low; sumH = Σ lines.high;
}

// 4. Rounding and output
display each line as r(line.low) – r(line.high);
total = { low: r(sumL), high: r(sumH) };                  // total is rounded from the UNROUNDED sum
mid   = Math.round((total.low + total.high) / 2);        // used for Meta value

// 5. Materials vs labor (one sentence, no extra table)
mat_pct = Math.round(mat.materials_share * 100); labor_pct = 100 - mat_pct;

// 6. Build time
let [dl, dh] = cfg.build_days_tiers.find(t => area <= t.max_sqft).days;
dl += height.build_days_add[0]; dh += height.build_days_add[1];
for (const e of cfg.extras) if (ex.has(e.id)) { dl += e.build_days_add[0]; dh += e.build_days_add[1]; }
if (project_type === 'replace') { dl += cfg.replace_build_days_add[0]; dh += cfg.replace_build_days_add[1]; }

// 7. "What changes your price" placeholder
per100_low = r(100*mat.per_sqft.low*height.multiplier*m); per100_high = r(100*mat.per_sqft.high*height.multiplier*m);
```

Because lines and total are rounded independently, the lines can differ from the total by up to ~$50 per line. Show the small gray note "Lines rounded; total is exact to the nearest $100." under the table.

### Edge cases
- **No prospect / unknown state:** m = 1.0, and the copy says "your area" instead of the city.
- **Custom size out of range:** clamp as in Step 2. Never compute with 0 or NaN. Disable Next until both fields are valid.
- **Ground deck with railing chosen:** allowed. Price it normally.
- **Raised deck with no railing:** allowed, with the warning. Price with no railing line.
- **Stairs with height `ground`:** allowed (2 steps per set). No landing.
- **Screened without roof:** roof is auto-added and both lines show.
- **Pergola + roof:** impossible by the UI rule. If the URL state somehow holds both, drop `pergola`.
- **Tiny deck:** the min-job line appears (see Example 3). Never show a total under `min_job × m`.
- **Freestanding decks** are not modeled (the railing formula assumes the house side is open). The not-included list covers it, and the builder confirms on site.
- **Config override missing a key:** the deep-merge (§4) falls back to the default.
- **Changing an earlier answer** (Back) recomputes everything. Pre-selected defaults update only if the user hasn't touched that step yet.

### Worked examples (all verified against this exact config)

**Example 1: new medium composite deck, raised, Texas (m = 0.95)**
Answers: `new`, `m` (16×12 = 192 sq ft), `standard`, `composite`, railing `composite`, stairs `1`, extras `[lighting]`, timeline `1_3`.

| Line | Low | High |
|---|---|---|
| Deck framing, footings & Composite (Trex, TimberTech) decking (192 sq ft) | $9,100 | $13,700 |
| Composite railing (36 linear ft) | $1,550 | $2,700 |
| Stairs (1 set, ~6 steps each) | $1,150 | $1,850 |
| Built-in lighting | $1,150 | $2,700 |
| Permit & drawings (where required) | $400 | $1,150 |
| **Total** | **$13,300** | **$22,100** |

Railing LF = 16 + 2·12 − 4·1 = 36. Materials split "About 55% … 45% labor". Build days 3–5 + lighting 0–1 = **3–6 days**. Meta `value` = **17700**. per100 = $4,800–$7,100.

**Example 2: replace with a second-story screened porch, Virginia (m = 1.08)**
Answers: `replace`, custom 20 × 14 (280 sq ft), `second`, `pt`, railing `wood`, stairs `1`, extras `[screened]` (roof auto-added), timeline `asap` (urgent).

| Line | Low | High |
|---|---|---|
| Deck framing, footings & Pressure-treated wood decking (280 sq ft) | $11,300 | $17,000 |
| Wood railing (44 linear ft) | $1,200 | $2,100 |
| Stairs (1 set, ~13 steps each, with landing) | $3,400 | $6,000 |
| Covered (solid roof) (280 sq ft) | $10,600 | $21,200 |
| Screened-in porch (280 sq ft) | $4,500 | $9,100 |
| Tear out & haul away old deck | $1,650 | $3,000 |
| Permit & drawings (where required) | $450 | $1,300 |
| **Total** | **$33,100** | **$59,700** |

Build days: 5–8 (tier) + 2–3 (second) + 3–5 (roof) + 2–3 (screened) + 1–2 (replace) = **13–21 days**. Materials 40% / labor 60%. Meta `value` = **46400**. Urgent = true.

**Example 3: tiny ground-level landing deck, Ohio (m = 0.92). Min-job case**
Answers: `new`, custom 8 × 8 (64 sq ft), `ground`, `pt`, railing `none`, stairs `0`, extras `[]`, timeline `budgeting`.

| Line | Low | High |
|---|---|---|
| Deck framing, footings & Pressure-treated wood decking (64 sq ft) | $1,650 | $2,400 |
| Permit & drawings (where required) | $350 | $1,100 |
| Small-job minimum | $1,700 | $2,000 |
| **Total** | **$3,700** | **$5,500** |

Unrounded: deck 1,625.1–2,437.6, permit 368–1,104, so the sum is 1,993.1–3,541.6. The minimum is 4,000×0.92 = 3,680 and 6,000×0.92 = 5,520, so the min-job line is 1,686.9–1,978.4. Build days **3–5**. Meta `value` = **4600**.

---

## 6. Result screen

Order, top to bottom, inside ToolShell's result slot (§5.3, §8):

1. **Eyebrow:** `copy.result_title` ("Your estimated deck price").
2. **Big two-tone range:** "$13,300 – $22,100", with the range bar and midpoint marker (§8).
3. **Subtitle:** `copy.result_subtitle`, e.g. "192 sq ft Composite (Trex, TimberTech) deck · Raised · prices typical for Austin". Use the height `label`.
4. **Two chips in a row:**
   - ⏱ `copy.build_time` ("Typical build: about 3–6 working days on site.")
   - 🧱 `copy.materials_split`
   - Use lucide `Clock` and `Package`, not emoji.
5. **"Your price, line by line"** table. Two columns: Item | Range. One row per line in the order computed. Bold total row. Gray note under it: "Lines rounded; total is exact to the nearest $100."
6. **"Change one thing" quick-edit row:** three small dropdowns (Material, Railing, Height) that recompute instantly without leaving the result. Log `tool_events` `step` with `meta:{quick_edit:field}`. This answers the "wood or composite?" question in the VOC.
7. **What's included / not included:** two side-by-side lists (stacked on mobile). Green `Check` icons for `copy.included`, gray `Minus` for `copy.not_included`.
8. **What changes your price:** bullet list from `copy.price_drivers`, filling `{per100_low}`/`{per100_high}`.
9. **Permit note:** `copy.permit_note`, small text.
10. **Disclaimer:** `copy.disclaimer` in small gray, directly under the price block **and** repeated at the bottom (platform §1 requires it under every price).
11. Contact card (section 7).

If `answers.railing === 'none'` and the height warning applied, repeat `copy.guard_warning` as an amber callout above the table.

---

## 7. Contact card

Uses the ToolShell contact card (§5.4) with these tool-specific settings:

- **Heading:** `copy.contact_heading` ("Want the exact number?")
- **Sub:** `copy.contact_sub`
- **Primary submit text:** `copy.cta_primary` = **"Get my exact quote"**
- **Secondary link-button:** `copy.cta_secondary` "Email me this breakdown". Same form with phone made optional. Store `contact.intent = 'email_breakdown'` (vs `'quote'`).
- **Extra fields** (after the standard ones, before consent):
  1. `budget_band`: select from `budget_bands`, label "Rough budget (optional)".
  2. `hoa`: segmented Yes / No / Not sure, label "Is there an HOA?" Optional.
  3. `target_date`: date picker, label "Need it done by a certain date? (optional)", min = today.
  4. Photo upload (standard §5.4), label "Photos of the spot or your old deck (optional)".
- **Urgency:** `result.urgent = (timeline === 'asap')` OR `target_date` within 45 days of today.
- **Thank-you variant** (§5.5) adds the line: "We've sent your breakdown to {email}. {business_name} will confirm the price after a quick site visit." When urgent, use the platform's "today" wording.
  - Summary card shows: size, height, material, railing, stairs, extras, the total range and the build days.

---

## 8. Business notification email

The platform builds it (§6.3). This tool supplies:
- **Subject:** `New Deck Cost Estimator request — {contact.name}, {city or zip}`. Prefix with `🔴 URGENT · ` when `result.urgent`.
- **Headline (first line of the body, H1):** `{contact.name} priced a {area} sq ft {material label} deck: {total.low} – {total.high}`
- **Sub-headline:** `{project_type label} · {height label} · {railing label} railing · {stairs} stair set(s) · Extras: {extras labels or "none"} · Timeline: {timeline label}`
- Then the platform blocks: contact, the line-item table (same as the result screen), all answers, photos, and the footer.

---

## 9. Personalization hooks (`config_overrides["deck-cost-estimator"]`)

A prospect can override any of these keys in `/admin`. The deep-merge replaces arrays whole, so to change one material, paste the whole `materials` array.

| Key | Typical use |
|---|---|
| `materials[].per_sqft`, `materials[].per_step` | Their real $/sq ft by material |
| `materials` (whole array) | Drop materials they don't install (e.g. remove `hardwood`) |
| `railings[].per_lf`, or the whole `railings` array | Their railing pricing; remove `glass` if not offered |
| `heights[].multiplier` | How much they charge for height |
| `extras[].price` or remove an extra | e.g. a builder that doesn't do roofs |
| `demo`, `permit`, `min_job`, `landing_per_set` | Their tear-out, permit and minimum |
| `regional_multipliers` | Override their state factor (or set it to 1.0 when the prices above are already local) |
| `build_days_tiers` | Their real schedule |
| `copy.included`, `copy.not_included`, `copy.price_drivers`, `copy.sub` | Their scope and warranty language |
| `timelines[].hint` | Their current lead time, e.g. "We're booking 3 weeks out" |

---

## 10. Meta events (in addition to platform §7)

- **`ToolResult`** custom params: `{tool:'deck-cost-estimator', niche:'deck', material, height, project_type, area, range_low, range_high}`
- **`ToolContactOpen`:** as in the platform.
- **`Lead`:** `value` = `mid` (e.g. 17700 for Example 1), `currency:'USD'`, `content_name:'deck-cost-estimator'`, `content_category:'deck'`. CAPI `custom_data.value` = the same `mid`.
- **Quick-edit** on the result: `fbq('trackCustom','ToolQuickEdit',{tool:'deck-cost-estimator', field})`.

---

## 11. QA checklist

1. Example 1, 2 and 3 inputs reproduce the tables above exactly: every line, the totals, the build days and the Meta value. Add them as unit tests for `calc.ts`.
2. Demo route (no prospect) uses m = 1.0. Example 1's answers give **$14,000 – $23,200** (value 18600): deck $9,600–$14,400, railing $1,600–$2,900, stairs $1,200–$1,950, lighting $1,200–$2,800, permit $400–$1,200.
3. Selecting `screened` auto-selects `roof_cover`. Deselecting the roof removes screened. Pergola is greyed out while a roof is selected.
4. Height `ground` hides skirting and pre-selects railing `none` and stairs `0`. Height `second` shows the landing helper text.
5. A raised deck with railing `none` shows the amber guard warning on Step 5 and the result, and still allows Next.
6. Custom size: 5 × 5 is blocked with the message, 60 × 40 is clamped to 1,500 sq ft with the message, and Next is disabled while empty.
7. The price, breakdown and disclaimer render **before** any contact field. No contact field appears above the fold on the result.
8. The quick-edit dropdowns recompute without page reload and log `ToolQuickEdit`.
9. Submitting writes `answers` (all 8 fields plus custom dims), `result` (lines, total, mid, days, urgent), emails the business with the headline format above, posts to n8n, and fires `Lead` with value = mid and the same event_id in Pixel and CAPI.
10. `/admin` override: set `materials` composite `per_sqft` to `{low:60, high:85}` for one prospect. Only that prospect's page changes.
11. At 360 px: the breakdown table doesn't scroll horizontally (long labels wrap) and the cards are 2 columns.
12. Every money figure is a range. No result screen shows a single price.
