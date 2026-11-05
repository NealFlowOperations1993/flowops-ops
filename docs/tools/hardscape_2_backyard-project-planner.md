# Tool spec: Backyard Project Planner (hardscape · tool 2)

> **Paste this into Lovable as ONE prompt, after the platform spec is built.** It assumes everything in
> `00_PLATFORM_SPEC.md` already exists: ToolShell (§5), routing (§2), tables (§3), personalization and
> deep-merge of `config_overrides` (§4), the `submit-tool` pipeline (§6), the Meta Pixel (§7), the design system (§8)
> and the regional multipliers (§9). Do **not** rebuild any of that. Build only what this file describes.
> Read every value from the merged config. Never hardcode a price, feature or rule.

---

## 1. Header

| Field | Value |
|---|---|
| **slug** | `backyard-project-planner` |
| **niche** | `hardscape` |
| **name** | Backyard Project Planner |
| **H1 (on-page promise)** | Plan your dream backyard in 60 seconds |
| **Sub-promise** | Tell us your goals and budget. Get 2–3 project packages with real price ranges, plus a plan to build it in phases. |
| **Target time to result** | **60 seconds** (7 steps, all taps) |
| **Trust row** (§5.1) | "★ Free · No signup to see your plan · Takes ~60s" |

---

## 2. Why this tool (VOC: `docs/voc/VOC_hardscape.md`)

> **Data caveat:** the hardscape negatives are polluted by a supply yard (9 of 22). This tool is built on the **4–5★ design-help and goals themes** plus the **cross-niche price-fear pattern** (VOC README pattern 2).

- **Buyers think in goals, not SKUs.** *"three goals: maximize our view, expand our useable space…"* / *"more privacy; an entertainment space with a bar, tv, fire pit; and an outdoor kitchen"*. The tool starts from goals and translates them into features and prices.
- **Design help is a top win (~13).** *"They came up with an incredible design at a fair price. They provided renderings of the design to help us visualize what it would look like."* / *"When we weren't sure which stone to select … Kyle gave his advice without any pressure."* Packages plus a style-driven material suggestion give that "advice without pressure".
- **Generic or paid design plans disappoint.** *"Paid $595 for a static design plan that lacked creativity and was a very basic."* / *"Some specifics communicated for design plan were not incorporated into the plan."* The submission carries every goal and must-have to the business, so the consult starts from the homeowner's specifics. The contact sub-line says so.
- **Price fear.** *"I was floored to learn I had been paying two to three times the market rate"* / *"That was a job in the neighborhood of $100k."* Every package shows a price range before contact.
- **"One trusted firm for everything, long-term" (~10 wins).** *"They do it all and do it well."* / *"it's like my property is on autopilot."* The phased plan frames a multi-season relationship.
- **Drainage and slope matter.** *"squaring away proper drainage for our acre of land"*. That's why there's a "current state" step that adds drainage and wall items.
- **Timelines are a pain.** *"Not a single timeline they promised was met — not one."* Each package shows a typical build length in weeks.

---

## 3. Seed SQL for the `tools` table

Prices are **2025–2026 US installed defaults that each business tunes**. `regional_multipliers` is platform §9.

```sql
insert into tools (slug, niche, name, default_config, is_finance, active)
values (
  'backyard-project-planner',
  'hardscape',
  'Backyard Project Planner',
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
  "goals": [
    {
      "id": "entertaining",
      "label": "Entertaining",
      "icon": "PartyPopper",
      "hint": "Room for friends, dinners, parties",
      "primary": [
        "patio"
      ],
      "secondary": [
        "seat_wall",
        "lighting"
      ]
    },
    {
      "id": "family",
      "label": "Family & kids",
      "icon": "Users",
      "hint": "Safe, open space to play",
      "primary": [
        "patio",
        "turf"
      ],
      "secondary": [
        "walkway"
      ]
    },
    {
      "id": "pool_surround",
      "label": "Pool surround",
      "icon": "Waves",
      "hint": "New or refreshed pool deck",
      "primary": [
        "pool_deck"
      ],
      "secondary": [
        "lighting"
      ]
    },
    {
      "id": "low_maintenance",
      "label": "Low maintenance",
      "icon": "Leaf",
      "hint": "Less mowing, weeding, staining",
      "primary": [
        "turf"
      ],
      "secondary": [
        "walkway"
      ]
    },
    {
      "id": "curb_appeal",
      "label": "Curb appeal",
      "icon": "House",
      "hint": "Front walk and entry",
      "primary": [
        "front_walkway"
      ],
      "secondary": [
        "lighting"
      ]
    },
    {
      "id": "outdoor_cooking",
      "label": "Outdoor cooking",
      "icon": "CookingPot",
      "hint": "Grill island or full kitchen",
      "primary": [
        "kitchen"
      ],
      "secondary": []
    },
    {
      "id": "fire_feature",
      "label": "Fire feature",
      "icon": "Flame",
      "hint": "Fire pit or fire table",
      "primary": [
        "fire_pit"
      ],
      "secondary": [
        "seat_wall"
      ]
    }
  ],
  "goal_limits": {
    "min": 1,
    "max": 3
  },
  "must_haves": [
    {
      "id": "patio",
      "label": "Patio / gathering space",
      "icon": "LayoutGrid"
    },
    {
      "id": "walkway",
      "label": "Garden path",
      "icon": "Footprints"
    },
    {
      "id": "front_walkway",
      "label": "Front walk & entry",
      "icon": "DoorOpen"
    },
    {
      "id": "pool_deck",
      "label": "Pool deck",
      "icon": "Waves"
    },
    {
      "id": "fire_pit",
      "label": "Fire pit",
      "icon": "Flame"
    },
    {
      "id": "kitchen",
      "label": "Grill island / kitchen",
      "icon": "CookingPot"
    },
    {
      "id": "seat_wall",
      "label": "Seat walls",
      "icon": "Armchair"
    },
    {
      "id": "pergola",
      "label": "Pergola / shade",
      "icon": "Grid2x2"
    },
    {
      "id": "lighting",
      "label": "Lighting",
      "icon": "Lightbulb"
    },
    {
      "id": "retaining_wall",
      "label": "Retaining wall / levels",
      "icon": "BrickWall"
    },
    {
      "id": "turf",
      "label": "Artificial turf",
      "icon": "Sprout"
    },
    {
      "id": "none",
      "label": "No must-haves — surprise me",
      "icon": "Sparkles",
      "exclusive": true
    }
  ],
  "yard_sizes": [
    {
      "id": "small",
      "label": "Small",
      "icon": "Square",
      "hint": "Townhome or compact yard · under 1,500 sq ft",
      "scale": 0.75
    },
    {
      "id": "medium",
      "label": "Medium",
      "icon": "Grid2x2",
      "hint": "Typical suburban yard · 1,500–4,000 sq ft",
      "scale": 1.0
    },
    {
      "id": "large",
      "label": "Large",
      "icon": "Grid3x3",
      "hint": "4,000–10,000 sq ft",
      "scale": 1.35
    },
    {
      "id": "xl",
      "label": "Very large",
      "icon": "Trees",
      "hint": "Over 10,000 sq ft (¼ acre+)",
      "scale": 1.7
    }
  ],
  "styles": [
    {
      "id": "classic",
      "label": "Classic",
      "icon": "Landmark",
      "hint": "Warm tones, traditional pavers",
      "material_label": "concrete pavers",
      "per_sqft": {
        "low": 18,
        "high": 28
      }
    },
    {
      "id": "modern",
      "label": "Modern",
      "icon": "Square",
      "hint": "Clean lines, large-format porcelain",
      "material_label": "porcelain pavers",
      "per_sqft": {
        "low": 28,
        "high": 45
      }
    },
    {
      "id": "natural",
      "label": "Natural",
      "icon": "Mountain",
      "hint": "Flagstone, boulders, soft edges",
      "material_label": "natural flagstone",
      "per_sqft": {
        "low": 24,
        "high": 42
      }
    },
    {
      "id": "resort",
      "label": "Resort",
      "icon": "TreePalm",
      "hint": "Travertine, Mediterranean feel",
      "material_label": "travertine",
      "per_sqft": {
        "low": 25,
        "high": 40
      }
    }
  ],
  "budgets": [
    {
      "id": "u15",
      "label": "Under $15k",
      "icon": "PiggyBank",
      "max": 15000
    },
    {
      "id": "15_30",
      "label": "$15k–$30k",
      "icon": "Wallet",
      "max": 30000
    },
    {
      "id": "30_60",
      "label": "$30k–$60k",
      "icon": "DollarSign",
      "max": 60000
    },
    {
      "id": "60_100",
      "label": "$60k–$100k",
      "icon": "Gem",
      "max": 100000
    },
    {
      "id": "100p",
      "label": "$100k+",
      "icon": "Crown",
      "max": null
    },
    {
      "id": "unsure",
      "label": "Not sure — show me options",
      "icon": "CircleHelp",
      "max": null
    }
  ],
  "current_state": [
    {
      "id": "lawn",
      "label": "Mostly lawn or dirt",
      "icon": "Sprout",
      "adds": []
    },
    {
      "id": "old_hardscape",
      "label": "Old patio or deck to remove",
      "icon": "Hammer",
      "adds": [
        "removal"
      ]
    },
    {
      "id": "slope",
      "label": "It slopes",
      "icon": "Mountain",
      "adds": [
        "retaining_wall"
      ]
    },
    {
      "id": "drainage",
      "label": "Water pools after rain",
      "icon": "Droplets",
      "adds": [
        "drainage"
      ]
    }
  ],
  "timelines": [
    {
      "id": "asap",
      "label": "As soon as possible",
      "icon": "Zap",
      "urgent": true
    },
    {
      "id": "season",
      "label": "This season",
      "icon": "Sun",
      "urgent": false
    },
    {
      "id": "spring",
      "label": "Next spring",
      "icon": "Flower2",
      "urgent": false
    },
    {
      "id": "dreaming",
      "label": "Just dreaming",
      "icon": "Cloud",
      "urgent": false
    }
  ],
  "tiers": [
    {
      "id": "essentials",
      "label": "Essentials",
      "tagline": "The must-haves, done right",
      "surface_factor": 1.0
    },
    {
      "id": "signature",
      "label": "Signature",
      "tagline": "The full plan for your goals",
      "surface_factor": 1.05
    },
    {
      "id": "showpiece",
      "label": "Showpiece",
      "tagline": "Everything, with premium finishes",
      "surface_factor": 1.15
    }
  ],
  "showpiece_extras": [
    "lighting",
    "pergola"
  ],
  "features": {
    "patio": {
      "label": "Patio",
      "kind": "surface",
      "phase": 1,
      "main_surface": true,
      "area_by_yard": {
        "small": [
          150,
          200,
          250
        ],
        "medium": [
          300,
          400,
          550
        ],
        "large": [
          450,
          650,
          900
        ],
        "xl": [
          600,
          900,
          1200
        ]
      },
      "type_multiplier": 1.0,
      "desc": {
        "essentials": "{sqft} sq ft {material} patio",
        "signature": "{sqft} sq ft {material} patio with border",
        "showpiece": "{sqft} sq ft {material} patio with inlay & border"
      }
    },
    "pool_deck": {
      "label": "Pool deck",
      "kind": "surface",
      "phase": 1,
      "main_surface": true,
      "area_by_yard": {
        "small": [
          300,
          400,
          500
        ],
        "medium": [
          500,
          650,
          800
        ],
        "large": [
          700,
          900,
          1200
        ],
        "xl": [
          900,
          1200,
          1600
        ]
      },
      "type_multiplier": 1.1,
      "desc": {
        "essentials": "{sqft} sq ft {material} pool deck",
        "signature": "{sqft} sq ft {material} pool deck with coping",
        "showpiece": "{sqft} sq ft {material} pool deck, coping & lounge area"
      }
    },
    "walkway": {
      "label": "Garden path",
      "kind": "surface",
      "phase": 1,
      "area_by_yard": {
        "small": [
          60,
          80,
          100
        ],
        "medium": [
          100,
          140,
          180
        ],
        "large": [
          150,
          220,
          300
        ],
        "xl": [
          200,
          300,
          400
        ]
      },
      "type_multiplier": 1.15,
      "desc": {
        "essentials": "{sqft} sq ft {material} path",
        "signature": "{sqft} sq ft {material} path",
        "showpiece": "{sqft} sq ft {material} path with lit edges"
      }
    },
    "front_walkway": {
      "label": "Front walk & entry",
      "kind": "surface",
      "phase": 1,
      "area_by_yard": {
        "small": [
          60,
          80,
          100
        ],
        "medium": [
          100,
          140,
          180
        ],
        "large": [
          150,
          220,
          300
        ],
        "xl": [
          200,
          300,
          400
        ]
      },
      "type_multiplier": 1.15,
      "desc": {
        "essentials": "{sqft} sq ft {material} front walk",
        "signature": "{sqft} sq ft {material} front walk with entry landing",
        "showpiece": "{sqft} sq ft {material} front walk, landing & steps"
      }
    },
    "turf": {
      "label": "Artificial turf",
      "kind": "turf",
      "phase": 2,
      "area_by_yard": {
        "small": [
          150,
          200,
          250
        ],
        "medium": [
          300,
          400,
          500
        ],
        "large": [
          500,
          700,
          900
        ],
        "xl": [
          800,
          1000,
          1400
        ]
      },
      "per_sqft": {
        "essentials": {
          "low": 9,
          "high": 14
        },
        "signature": {
          "low": 10,
          "high": 15
        },
        "showpiece": {
          "low": 12,
          "high": 18
        }
      },
      "desc": {
        "essentials": "{sqft} sq ft artificial turf",
        "signature": "{sqft} sq ft pet- and kid-friendly turf",
        "showpiece": "{sqft} sq ft premium turf with cooling infill"
      }
    },
    "seat_wall": {
      "label": "Seat wall",
      "kind": "flat",
      "phase": 2,
      "scales": false,
      "price": {
        "essentials": {
          "low": 2500,
          "high": 4500
        },
        "signature": {
          "low": 3500,
          "high": 6500
        },
        "showpiece": {
          "low": 6000,
          "high": 11000
        }
      },
      "desc": {
        "essentials": "12 ft block seat wall",
        "signature": "16 ft seat wall with stone cap",
        "showpiece": "20+ ft natural-stone seat walls with lit caps"
      }
    },
    "fire_pit": {
      "label": "Fire pit",
      "kind": "flat",
      "phase": 2,
      "scales": false,
      "needs_rough_in": {
        "showpiece": true
      },
      "price": {
        "essentials": {
          "low": 1500,
          "high": 3000
        },
        "signature": {
          "low": 3000,
          "high": 6500
        },
        "showpiece": {
          "low": 5500,
          "high": 11000
        }
      },
      "desc": {
        "essentials": "Block fire-pit kit (wood-burning)",
        "signature": "Custom stone fire pit",
        "showpiece": "Gas fire feature with stone surround"
      }
    },
    "kitchen": {
      "label": "Outdoor cooking",
      "kind": "flat",
      "phase": 2,
      "scales": false,
      "needs_rough_in": {
        "signature": true,
        "showpiece": true
      },
      "price": {
        "essentials": {
          "low": 5500,
          "high": 9500
        },
        "signature": {
          "low": 14000,
          "high": 24000
        },
        "showpiece": {
          "low": 28000,
          "high": 48000
        }
      },
      "desc": {
        "essentials": "6–8 ft grill island (no utilities, appliances extra)",
        "signature": "12 ft L-shaped kitchen with gas & power (appliances extra)",
        "showpiece": "18 ft full kitchen with gas, power & sink (appliances extra)"
      }
    },
    "pergola": {
      "label": "Pergola",
      "kind": "flat",
      "phase": 2,
      "scales": false,
      "price": {
        "essentials": {
          "low": 4000,
          "high": 7500
        },
        "signature": {
          "low": 6000,
          "high": 12000
        },
        "showpiece": {
          "low": 12000,
          "high": 25000
        }
      },
      "desc": {
        "essentials": "10 × 10 wood pergola",
        "signature": "12 × 14 cedar or aluminum pergola",
        "showpiece": "Louvered aluminum pergola with lights"
      }
    },
    "lighting": {
      "label": "Lighting",
      "kind": "flat",
      "phase": 2,
      "scales": true,
      "needs_rough_in": {
        "essentials": true,
        "signature": true,
        "showpiece": true
      },
      "price": {
        "essentials": {
          "low": 1200,
          "high": 2500
        },
        "signature": {
          "low": 2500,
          "high": 4500
        },
        "showpiece": {
          "low": 4500,
          "high": 8500
        }
      },
      "desc": {
        "essentials": "Path & step lights",
        "signature": "Path, step & wall lights on a timer",
        "showpiece": "Full design lighting with app control"
      }
    },
    "retaining_wall": {
      "label": "Retaining wall / levels",
      "kind": "flat",
      "phase": 1,
      "scales": true,
      "price": {
        "essentials": {
          "low": 4000,
          "high": 8000
        },
        "signature": {
          "low": 7000,
          "high": 14000
        },
        "showpiece": {
          "low": 12000,
          "high": 25000
        }
      },
      "desc": {
        "essentials": "~20 ft block wall, up to 2 ft",
        "signature": "~30 ft block wall with cap",
        "showpiece": "Natural-stone walls and terraces"
      }
    }
  },
  "site_items": {
    "removal": {
      "label": "Remove old patio or deck",
      "phase": 1,
      "scales": true,
      "price": {
        "low": 2500,
        "high": 5000
      }
    },
    "drainage": {
      "label": "Drainage fix",
      "phase": 1,
      "scales": true,
      "price": {
        "low": 1500,
        "high": 4500
      }
    },
    "rough_in": {
      "label": "Gas & power rough-in for phase 2",
      "phase": 1,
      "scales": false,
      "price": {
        "low": 500,
        "high": 1500
      }
    }
  },
  "duration_weeks": [
    {
      "max_mid": 15000,
      "weeks": [
        1,
        2
      ]
    },
    {
      "max_mid": 40000,
      "weeks": [
        2,
        4
      ]
    },
    {
      "max_mid": 80000,
      "weeks": [
        4,
        7
      ]
    },
    {
      "max_mid": 100000000,
      "weeks": [
        6,
        10
      ]
    }
  ],
  "rules": {
    "hide_showpiece_if_low_over_budget_x": 2.0,
    "default_recommended_when_no_max": {
      "unsure": "signature",
      "100p": "showpiece"
    },
    "phase2_label_by_month": {
      "1": "this summer",
      "2": "this summer",
      "3": "this summer",
      "4": "next spring",
      "5": "next spring",
      "6": "next spring",
      "7": "next spring",
      "8": "next spring",
      "9": "next spring",
      "10": "next spring",
      "11": "next spring",
      "12": "next spring"
    }
  },
  "copy": {
    "h1": "Plan your dream backyard in 60 seconds",
    "sub": "Tell us your goals and budget. Get 2–3 project packages with real price ranges, plus a plan to build it in phases.",
    "result_title": "Your backyard plan",
    "result_subtitle": "{goal_list} · {style_label} style · {yard_label} yard · prices typical for {city}",
    "recommended_badge": "Best fit for your budget",
    "fits_badge": "Fits your budget",
    "over_budget_banner": "Your must-haves usually run above your budget ({budget_label}). Building in phases helps: Phase 1 starts at {p1_low} – {p1_high}.",
    "no_max_note_unsure": "You weren't sure on budget, so we've marked the package most people choose.",
    "phase_heading": "Build it in phases",
    "phase_intro_fits": "Prefer to spread it out? Here's how {package_label} splits:",
    "phase_intro_over": "Here's how to get started within your budget:",
    "phase1_title": "Phase 1: now",
    "phase1_why": "The groundwork and main surfaces come first. That's where the heavy machines are needed, and doing it first means nothing gets torn up later.",
    "phase2_title": "Phase 2: {phase2_label}",
    "phase2_why": "The features. They go on top of Phase 1 without disturbing it.",
    "single_phase_note": "This plan is a single-phase project, about {weeks_low}–{weeks_high} weeks on site.",
    "duration_line": "Typical build: about {weeks_low}–{weeks_high} weeks on site.",
    "material_line": "Main surfaces are priced in {material_label} for your {style_label} style.",
    "kitchen_appliances_note": "Grill and appliances aren't included. A built-in grill typically adds $1,500–$6,000.",
    "disclaimer": "Estimate only — final price confirmed after a free on-site visit. Packages are typical starting points for {city_or_your_area}, not a design. Your designer will tailor sizes, materials and layout to your yard.",
    "cta_primary": "Get my design consult",
    "cta_secondary": "Email me this plan",
    "contact_heading": "Turn this plan into a design",
    "contact_sub": "{business_name} will walk your yard, listen to what you want and show you what's possible. Bring this plan, and nothing you've told us gets lost.",
    "included": [
      "Excavation, base and grading for every surface",
      "Materials and installation for each listed item",
      "Drainage behind any walls",
      "Cleanup and haul-off"
    ],
    "not_included": [
      "Design and rendering fees, if {business_name} charges them (ask)",
      "Appliances, furniture, fire-pit fuel",
      "Plants, trees and irrigation changes",
      "Permits beyond standard allowances",
      "Pool work beyond the deck"
    ],
    "price_drivers": [
      "Size of the main patio or pool deck. It's usually the biggest line",
      "Style. Porcelain and natural stone cost more than concrete pavers",
      "Outdoor kitchens. They range from a $6k grill island to $50k+",
      "Slope and drainage. Walls and drains add cost but protect everything else",
      "Access for machines into the backyard"
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
- `features` is a map keyed by feature id. Each feature has a `kind`:
  - `surface`: priced as area × the style's $/sq ft × `type_multiplier` × the tier's `surface_factor`.
  - `turf`: area × the tier's $/sq ft.
  - `flat`: the tier price, × the yard `scale` when `scales: true`.
- `area_by_yard[yard]` is `[essentials_sqft, signature_sqft, showpiece_sqft]`.
- `phase` is 1 (groundwork and main surfaces) or 2 (features on top).
- `needs_rough_in[tier] = true` means that feature at that tier needs gas or power stubbed in during Phase 1.
- `goals[].primary` features go into **every** package. `goals[].secondary` features join from **Signature** up.

---

## 4. Step-by-step flow (7 steps)

Single-select steps auto-advance after 250 ms. Multi-select steps need Next.

### Step 1: `goals` (array)
- **Question:** "What do you want your backyard to do for you?"
- **Helper:** "Pick up to 3."
- **Input:** multi-select cards from `goals` (2 columns, with hints).
- **Options:** `entertaining`, `family`, `pool_surround`, `low_maintenance`, `curb_appeal`, `outdoor_cooking`, `fire_feature`.
- **Default:** `[]`. **Validation:** `goal_limits.min` 1 to `goal_limits.max` 3.
  - Tapping a 4th card does nothing and shakes the counter "3 of 3 picked".
  - The Next button stays disabled at 0.
- **Order matters.** Store the goals in tap order. The first goal is shown first in copy.

### Step 2: `must` (array)
- **Question:** "Any must-haves?"
- **Helper:** "Things you already know you want. These go into every package."
- **Input:** multi-select cards from `must_haves` (2 columns on mobile, 4 on desktop).
- **Options:** `patio`, `walkway`, `front_walkway`, `pool_deck`, `fire_pit`, `kitchen`, `seat_wall`, `pergola`, `lighting`, `retaining_wall`, `turf`, `none`.
- **Default:** `[]`. **Validation:** at least one card, where `none` counts. `none` is exclusive: it clears the others, and they clear it.
- **Smart pre-select:** on entering the step, pre-tick the primary features of the chosen goals (visually ticked, editable). The user may un-tick them, but goal primaries are still included in every package by the calc, so the un-tick only removes the visual duplication. Show the hint "Already included from your goals" on those cards.

### Step 3: `yard`
- **Question:** "How big is the area you want to work on?"
- **Helper:** "Just the part of the yard this project covers."
- **Input:** single-select cards from `yard_sizes`: `small`, `medium`, `large`, `xl`.
- **Default:** none. **Validation:** required.

### Step 4: `style`
- **Question:** "Which style feels most like you?"
- **Helper:** "This sets the main material. Your designer can mix and match."
- **Input:** single-select cards from `styles` (show the hint): `classic`, `modern`, `natural`, `resort`.
- **Default:** none. **Validation:** required.

### Step 5: `current` (array)
- **Question:** "What's there now?"
- **Helper:** "Pick all that apply."
- **Input:** multi-select cards from `current_state`: `lawn`, `old_hardscape`, `slope`, `drainage`.
- **Default:** `[]`. **Validation:** at least 1.
  - `lawn` is not exclusive. The yard can be lawn and sloped.
- **Branch (calc):**
  - `old_hardscape` adds the removal item.
  - `slope` adds a `retaining_wall` feature to every package.
  - `drainage` adds the drainage item.

### Step 6: `budget`
- **Question:** "What budget feels comfortable?"
- **Helper:** "Honest is best. We'll show what fits, plus a phased option."
- **Input:** single-select cards from `budgets`: `u15`, `15_30`, `30_60`, `60_100`, `100p`, `unsure`.
- **Default:** none. **Validation:** required.

### Step 7: `timeline`
- **Question:** "When would you like to start?"
- **Input:** single-select cards from `timelines`: `asap`, `season`, `spring`, `dreaming`.
- **Default:** none. **Validation:** required.
- **Branch:** `asap` sets `urgent`.
- Then a 900 ms "Building your packages…" shimmer with three skeleton cards, then the result.

---

## 5. Calculation logic

Pure function `computeBackyardPlan(answers, cfg, prospect, today = new Date())` in `src/tools/backyard-project-planner/calc.ts`.
`r()` is the standard rounding: nearest $100, or nearest $50 under $2,000.

```ts
const m  = cfg.regional_multipliers[prospect?.state ?? ''] ?? 1.0;
const ys = cfg.yard_sizes.find(y => y.id === yard);
const st = cfg.styles.find(s => s.id === style);
const TIERS = ['essentials','signature','showpiece'];
const G  = id => cfg.goals.find(x => x.id === id);          // arrays are looked up by id
const CS = id => cfg.current_state.find(x => x.id === id);

// ---- 1. Feature sets (ordered, de-duplicated, insertion order kept)
const prim = uniq(goals.flatMap(g => G(g).primary));
const sec  = uniq(goals.flatMap(g => G(g).secondary));
const must = answers.must.filter(x => x !== 'none');
let E = uniq([...prim, ...must]);
if (!E.includes('patio') && !E.includes('pool_deck')) E.unshift('patio');      // always a main surface
for (const c of current) if (CS(c).adds.includes('retaining_wall')) E = uniq([...E, 'retaining_wall']);
const S = uniq([...E, ...sec]);
const P = uniq([...S, ...cfg.showpiece_extras]);                               // + lighting, pergola
const sets = { essentials:E, signature:S, showpiece:P };

// ---- 2. Price each package
for (const [ti, tier] of TIERS.entries()) {
  const lines = []; let rough = false;
  const sf = cfg.tiers[ti].surface_factor;
  // site items first (always phase 1, same in every tier)
  for (const c of current) for (const add of CS(c).adds)
    if (add === 'removal' || add === 'drainage') {
      const it = cfg.site_items[add];
      lines.push({ label:it.label, phase:1, low:it.price.low*ys.scale*m, high:it.price.high*ys.scale*m });
    }
  for (const f of sets[tier]) {
    const d = cfg.features[f]; let lo, hi, sq;
    if (d.kind === 'surface') { sq = d.area_by_yard[yard][ti];
      lo = sq*st.per_sqft.low*d.type_multiplier*sf; hi = sq*st.per_sqft.high*d.type_multiplier*sf; }
    else if (d.kind === 'turf') { sq = d.area_by_yard[yard][ti];
      lo = sq*d.per_sqft[tier].low; hi = sq*d.per_sqft[tier].high; }
    else { const k = d.scales ? ys.scale : 1; lo = d.price[tier].low*k; hi = d.price[tier].high*k; }
    if (d.needs_rough_in?.[tier]) rough = true;
    lines.push({ feature:f, phase:d.phase, label: fill(d.desc[tier], {sqft:fmt(sq), material:st.material_label}),
                 low:lo*m, high:hi*m });
  }
  if (rough) { const it = cfg.site_items.rough_in;
    lines.push({ label:it.label, phase:1, low:it.price.low*m, high:it.price.high*m }); }

  pkg[tier] = {
    lines,                                               // display each line r(low)–r(high)
    total:  { low:r(Σlow), high:r(Σhigh) },
    phase1: { low:r(Σlow where phase 1), high:r(Σhigh where phase 1) },
    phase2: { low:r(Σlow where phase 2), high:r(Σhigh where phase 2) },
  };
}

// ---- 3. Which packages to show, and which is recommended
const b = cfg.budgets.find(x => x.id === budget); const mid = t => (t.low+t.high)/2;
let shown = [...TIERS];
if (b.max && pkg.showpiece.total.low > cfg.rules.hide_showpiece_if_low_over_budget_x * b.max) shown = ['essentials','signature'];
let rec, over = false;
if (b.max) {
  rec = [...TIERS].reverse().find(t => mid(pkg[t].total) <= b.max);   // highest tier whose midpoint fits
  if (!rec) { rec = 'essentials'; over = true; }
} else rec = cfg.rules.default_recommended_when_no_max[b.id];         // unsure→signature, 100p→showpiece
const fits = t => b.max ? pkg[t].total.high <= b.max : false;         // "Fits your budget" badge

// ---- 4. Phased plan (recommended package only)
const phase2Label = cfg.rules.phase2_label_by_month[String(today.getMonth()+1)];  // Nov → "next spring"
const singlePhase = pkg[rec].phase2.high === 0;

// ---- 5. Duration
const weeks = cfg.duration_weeks.find(d => mid(pkg[rec].total) <= d.max_mid).weeks;  // also per package for the cards

leadValue = Math.round(mid(pkg[rec].total));
```

**Display order of lines in a package:** Phase 1 lines first (site items, then features with phase 1, then rough-in), then Phase 2 lines in feature order.

### Edge cases
- **Goals with no surface** (e.g. only `outdoor_cooking`): Patio is auto-added as the main surface, so every plan has somewhere to stand.
- **Both `patio` and `pool_deck`:** both are priced. That's allowed and common.
- **`none` must-haves plus a single goal** like `low_maintenance`: E = [patio, turf]. Valid.
- **Showpiece adds nothing new:** if P equals S (lighting and pergola already in S), the Showpiece still differs by tier pricing and descriptions. Show it.
- **Budget under every package:** `over = true`, the recommended package is Essentials, the amber `over_budget_banner` shows with Essentials' Phase 1 range, and the phased plan uses `phase_intro_over`.
- **Showpiece hidden:** only when its low is more than 2× the budget max. Never hide Essentials or Signature, so 2–3 packages always show.
- **Single-phase plan** (no phase-2 features): hide the two-column phase block and show `single_phase_note`.
- **No prospect:** m = 1.0 and "your area".
- **Date:** compute `phase2Label` from the viewer's local date. In unit tests, inject `today`.

### Worked examples (verified against this config; `today` = 2026-11-04 → phase 2 label "next spring")

**Example 1: entertaining + fire feature, must-have lighting, medium yard, classic, $30k–$60k, lawn, North Carolina (m = 0.95)**
- E = [patio, fire_pit, lighting]; S = E + [seat_wall]; P = S + [pergola]. Rough-in in all tiers (lighting).
- Showpiece mid 54,450 ≤ 60,000, so the **recommended package is Showpiece**. All three are shown.

| Package | Total | Phase 1 | Phase 2 | Weeks |
|---|---|---|---|---|
| Essentials | $8,200 – $14,600 | $5,600 – $9,400 | $2,600 – $5,200 | 1–2 |
| Signature | $16,200 – $29,200 | $7,700 – $12,600 | $8,600 – $16,600 | 2–4 |
| **Showpiece ★** | **$37,900 – $71,000** | **$11,300 – $18,200** | **$26,600 – $52,700** | **4–7** |

Showpiece lines:
- P1: 550 sq ft concrete pavers patio with inlay & border, $10,800–$16,800
- P1: Gas & power rough-in for phase 2, $500–$1,450
- P2: Gas fire feature with stone surround, $5,200–$10,500
- P2: Full design lighting with app control, $4,300–$8,100
- P2: 20+ ft natural-stone seat walls with lit caps, $5,700–$10,500
- P2: Louvered aluminum pergola with lights, $11,400–$23,800

"Fits your budget" badges: Essentials and Signature (their high ≤ 60k). Showpiece gets the "Best fit for your budget" badge. Meta `value` = **54450**.

**Example 2: pool surround + low maintenance, no must-haves, large yard, resort, $60k–$100k, old patio to remove, Florida (m = 1.00)**
- E = [pool_deck, turf]; S = E + [lighting, walkway]; P = S + [pergola]. Removal (× 1.35) in every tier.
- Showpiece mid 109,050 > 100k. Signature mid 61,950 ≤ 100k, so the **recommended package is Signature**. All three are shown (showpiece low 80,600 < 200k).

| Package | Total | Phase 1 | Phase 2 | Weeks |
|---|---|---|---|---|
| Essentials | $27,100 – $44,600 | $22,600 – $37,600 | $4,500 – $7,000 | 2–4 |
| **Signature ★** | **$46,900 – $77,000** | **$36,500 – $60,500** | **$10,400 – $16,600** | **4–7** |
| Showpiece | $80,600 – $137,500 | $51,700 – $84,800 | $28,900 – $52,700 | 6–10 |

Signature lines:
- P1: Remove old patio or deck, $3,400–$6,800
- P1: 900 sq ft travertine pool deck with coping, $26,000–$41,600
- P1: 220 sq ft travertine path, $6,600–$10,600
- P1: Gas & power rough-in for phase 2, $500–$1,500
- P2: 700 sq ft pet- and kid-friendly turf, $7,000–$10,500
- P2: Path, step & wall lights on a timer, $3,400–$6,100

Meta `value` = **61950**.

**Example 3: outdoor cooking + entertaining, must-have pergola, small yard, modern, under $15k, drainage issue, New Jersey (m = 1.20). Over-budget case**
- E = [patio, kitchen, pergola]; S = E + [seat_wall, lighting]; P = S (extras already present).
- Essentials mid 25,200 > 15,000, so `over = true` and the **recommended package is Essentials**.
- Showpiece low 70,900 > 2 × 15,000, so it is **hidden**. Two packages show.
- The banner reads: "Your must-haves usually run above your budget (Under $15k). Building in phases helps: Phase 1 starts at $6,400 – $12,200."

| Package | Total | Phase 1 | Phase 2 | Weeks |
|---|---|---|---|---|
| **Essentials ★** | **$17,800 – $32,600** | **$6,400 – $12,200** | **$11,400 – $20,400** | **2–4** |
| Signature | $39,500 – $72,200 | $9,000 – $17,200 | $30,500 – $55,100 | 4–7 |

Essentials lines:
- P1: Drainage fix, $1,350–$4,100
- P1: 150 sq ft porcelain pavers patio, $5,000–$8,100
- P2: 6–8 ft grill island (no utilities, appliances extra), $6,600–$11,400
- P2: 10 × 10 wood pergola, $4,800–$9,000

There's no rough-in, because the Essentials grill island has no utilities. The kitchen appliances note shows. Meta `value` = **25200**.

---

## 6. Result screen

1. **Eyebrow:** `copy.result_title` ("Your backyard plan").
   - Subtitle: `copy.result_subtitle`, with `{goal_list}` = goal labels in tap order joined by " + ".
   - Then `copy.material_line`.
2. **Over-budget banner** (amber) when `over`.
3. **Package cards**: horizontal snap-scroll carousel on mobile (a peek of the next card shows), 2–3 columns on desktop.
   - Order: Essentials → Signature → Showpiece. On mobile, initially scroll to the recommended card.
   - Each card contains:
     - **Badges:** "Best fit for your budget" (`recommended_badge`, brand color) on `rec`. "Fits your budget" (`fits_badge`, green outline) where `fits(t)` is true and the tier isn't `rec`. For `unsure`, use `copy.no_max_note_unsure` as the small note under the recommended badge.
     - **Title:** tier label, then tagline in gray.
     - **Big range:** total, two-tone, with a mini range bar.
     - "Typical build: about {weeks} weeks".
     - **Feature list:** each line's label with a `Check` icon. The price per line is hidden until "See line-by-line prices" is tapped, which expands a table with P1/P2 tags.
     - **Button:** "Choose this package". It sets `selected_package` (defaults to `rec`), highlights the card, and scrolls to the contact card. Log `tool_events` `step` `{select_package}`.
4. **Phased plan block** (for `selected_package`, default `rec`). Heading `copy.phase_heading`, intro `phase_intro_fits` or `phase_intro_over`. Two stacked cards:
   - **"Phase 1: now"**: its lines and the `phase1` range, plus `copy.phase1_why`.
   - **"Phase 2: {phase2Label}"**: its lines and the `phase2` range, plus `copy.phase2_why`.
   - A vertical connector between them, with lucide `ArrowDown`.
   - If single-phase, show `single_phase_note` instead.
5. **Notes:** `kitchen_appliances_note` when any shown package contains `kitchen`.
6. **Included / not included:** `copy.included` / `copy.not_included`.
7. **What changes your price:** `copy.price_drivers`.
8. **Disclaimer:** `copy.disclaimer`, under the cards and at the bottom.
9. Contact card.

---

## 7. Contact card

- **Heading:** `copy.contact_heading` "Turn this plan into a design". **Sub:** `copy.contact_sub`.
- **Primary submit:** **"Get my design consult"** (`copy.cta_primary`).
- **Secondary:** **"Email me this plan"** (`intent='email_plan'`).
- **Extra fields:**
  1. `selected_package`: read-only chip showing the chosen package ("Signature — $46,900 – $77,000") with a "change" link that scrolls up.
  2. `consult_type`: segmented "On-site visit" / "Video call" / "Either" (default "Either").
  3. `household`: chips, optional multi: Kids · Dogs · Pool · HOA · Entertaining often.
  4. Photo upload (standard), labeled "Photos of the yard (optional, a big help for your designer)".
  5. Notes (standard), with the placeholder "Anything else? Views to keep, things to hide, must-avoid…"
- **Urgency:** `timeline === 'asap'`.
- **Thank-you variant:** "{business_name} has your plan. They'll reach out to book your design consult and bring your goals, must-haves and package with them." Summary card: goals, must-haves, style, yard, chosen package and range, phase 1/2 split. "Today" wording when urgent.

---

## 8. Business notification email

- **Subject:** `New Backyard Project Planner request — {contact.name}, {city or zip}`. Prefix `🔴 URGENT · ` when urgent.
- **Headline:** `{contact.name} wants a design consult: {selected_package label} package, {total.low} – {total.high}`
- **Sub-headline:** `Goals: {goal labels} · Must-haves: {labels or "none"} · {yard label} yard · {style label} style · Budget: {budget label} · Now there: {current labels} · Start: {timeline label} · Consult: {consult_type}`
- Then the platform blocks, plus: the selected package's line table with P1/P2 tags, and a compact table of all shown packages (tier | total).

---

## 9. Personalization hooks (`config_overrides["backyard-project-planner"]`)

| Key | Use |
|---|---|
| `features.<id>.price` / `.per_sqft` / `.area_by_yard` / `.desc` | Their real feature pricing, sizes and wording |
| `styles[].per_sqft`, `styles[].material_label` | Their main material per style (e.g. a firm that only lays pavers sets every style to pavers with different patterns) |
| `goals[].primary` / `.secondary` | How they map goals to features (e.g. curb_appeal adds lighting as primary) |
| `tiers[].label` / `.tagline` / `.surface_factor` | Rename the packages (e.g. "Good / Better / Best") |
| `showpiece_extras` | What their top package always adds |
| `site_items.*`, `yard_sizes[].scale` | Removal, drainage and rough-in costs; how they scale with yard size |
| `budgets` | Budget bands for their market |
| `rules.*` | Recommendation and hide rules; `phase2_label_by_month` for their climate (e.g. "next fall" in Arizona) |
| `duration_weeks` | Their real build lengths |
| `regional_multipliers` | Their state factor |
| `copy.contact_sub`, `copy.not_included` | Whether design or renderings are free or paid. Say it plainly (VOC: the "$595 static design plan" complaint) |

---

## 10. Meta events

- **`ToolResult`:** `{tool:'backyard-project-planner', niche:'hardscape', goals: goals.join(','), style, yard, budget, recommended: rec, over_budget: over}`
- **`ToolPackageSelect`** (custom): `{tool, package}` on "Choose this package".
- **`Lead`:** `value` = midpoint of the **selected** package total (defaults to the recommended one; examples 54450 / 61950 / 25200), `currency:'USD'`.
  - For CAPI (§6.5), treat this tool as an estimator and send the same `value`.

---

## 11. QA checklist

1. Examples 1–3 (with `today` injected as 2026-11-04) reproduce every package total, phase split, the line items listed, the recommended tier, the shown tiers and the Meta value. Add them as unit tests.
2. The goals step blocks a 4th pick and requires at least 1. The tap order is preserved into the subtitle and email.
3. Must-haves: `none` is exclusive. Goal primaries are pre-ticked with the "Already included" hint.
4. A plan with only `outdoor_cooking` still includes a patio in every package.
5. `slope` adds the retaining-wall line to every package. `old_hardscape` and `drainage` add phase-1 site lines scaled by yard.
6. Showpiece hides only when its low is over 2× the budget max (Example 3). Never fewer than 2 cards.
7. Over-budget: the amber banner shows Essentials' Phase 1 range, and the phased plan uses the "within your budget" intro.
8. The phase 2 label follows the date: Jan–Mar → "this summer", otherwise "next spring" (test with an injected date).
9. "Choose this package" updates the phased plan, the contact chip and the Lead value. The email headline names the chosen package.
10. Prices and packages render before any contact field. The submit stores `result = {packages, recommended, selected_package, over, phase2Label}`, emails, posts to n8n, and fires Lead with matching event_id.
11. 360 px: the carousel snaps with a visible peek, the expanded line tables wrap, and there's no page-level horizontal scroll.
12. Override test: set `tiers` labels to Good/Better/Best for one prospect. Only that prospect's cards and email change.
