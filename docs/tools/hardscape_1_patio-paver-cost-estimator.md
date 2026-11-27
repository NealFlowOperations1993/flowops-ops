# Tool spec: Patio & Paver Cost Estimator (hardscape · tool 1)

> **Paste this into Lovable as ONE prompt, after the platform spec is built.** It assumes everything in
> `00_PLATFORM_SPEC.md` already exists: ToolShell (§5), routing (§2), tables (§3), personalization and
> deep-merge of `config_overrides` (§4), the `submit-tool` pipeline (§6), the Meta Pixel (§7), the design system (§8)
> and the regional multipliers (§9). Do **not** rebuild any of that. Build only what this file describes.
> Read every value from the merged config. Never hardcode a price.

---

## 1. Header

| Field | Value |
|---|---|
| **slug** | `patio-paver-cost-estimator` |
| **niche** | `hardscape` |
| **name** | Patio & Paver Cost Estimator |
| **H1 (on-page promise)** | What will your patio or hardscape project cost? |
| **Sub-promise** | Pick your project and materials. See an itemized price range in about 45 seconds. No consult fee, no signup. |
| **Target time to result** | **45 seconds** (5–7 taps depending on project type) |
| **Trust row** (§5.1) | "★ Free · No signup to see your price · Takes ~45s" |

> Importer note (§4): for `niche = 'hardscape'`, set `tool_slugs = ['patio-paver-cost-estimator','backyard-project-planner']`.

---

## 2. Why this tool (VOC: `docs/voc/VOC_hardscape.md`)

> **Data caveat:** the hardscape scrape is polluted. 9 of the 22 negatives are a materials supply yard. This tool leans on the **4–5★ themes** and the **cross-niche price-fear pattern** (VOC README pattern 2), not on supply-yard complaints.

- **"What should this cost, and am I being overcharged?" is the top buying question.** *"I was floored to learn I had been paying two to three times the market rate for most of the work"* (the one strong installer-level price complaint). Also *"I talked to 12 companies"* and *"That was a job in the neighborhood of $100k."* An instant range meets comparison shoppers.
- **Fair, reasonable price is a top win (~13).** *"EVERY project was reasonably priced"* / *"Price was very reasonable for patio repairs."* Itemized lines let the homeowner see the price is fair.
- **Paid consults with no quote frustrate buyers.** *"Took my $200 consulting fee and never even sent a quote."* The tool gives a free first number. The contact sub-line says "No consult fee".
- **Hidden add-ons (~3).** *"in addition to the $160 delivery charge they had a $37 fuel surcharge."* That's why there's an explicit included / not-included list, and removal and drainage are separate visible lines.
- **Material choice is a real question (~13 design-help wins).** *"When we weren't sure which stone to select … Kyle gave his advice without any pressure."* Material cards carry one-line hints, and a quick-edit swaps material on the result.
- **Drainage and grading matter to buyers.** *"squaring away proper drainage for our acre of land"* / *"installed drainage systems following all codes and obtaining all permits."* That's why there's a site step and permit lines.
- **Worn-space transformations win (~8).** *"Our pool deck was looking pretty rough and worn out after years so we finally decided to replace it."* / *"Turned a terrible looking wood deck into a spectacular paver wonderland!!"* That's why the removal step includes "Old wood deck".
- **Cross-niche:** show the price before contact info. Never lead with monthly payments.

---

## 3. Seed SQL for the `tools` table

Prices are **2025–2026 US installed defaults that each business tunes**. `regional_multipliers` is platform §9.

```sql
insert into tools (slug, niche, name, default_config, is_finance, active)
values (
  'patio-paver-cost-estimator',
  'hardscape',
  'Patio & Paver Cost Estimator',
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
      "id": "patio",
      "label": "Patio",
      "icon": "LayoutGrid",
      "hint": "Outdoor living or dining space",
      "kind": "area",
      "type_multiplier": 1.0,
      "base_share": 0.35
    },
    {
      "id": "walkway",
      "label": "Walkway or path",
      "icon": "Footprints",
      "hint": "Front walk, side path, garden path",
      "kind": "area",
      "type_multiplier": 1.15,
      "base_share": 0.35
    },
    {
      "id": "driveway",
      "label": "Driveway",
      "icon": "Car",
      "hint": "Pavers or stamped concrete",
      "kind": "area",
      "type_multiplier": 1.25,
      "base_share": 0.4
    },
    {
      "id": "pool_deck",
      "label": "Pool deck",
      "icon": "Waves",
      "hint": "Surface around a pool",
      "kind": "area",
      "type_multiplier": 1.1,
      "base_share": 0.35
    },
    {
      "id": "retaining_wall",
      "label": "Retaining wall",
      "icon": "BrickWall",
      "hint": "Holds back a slope or creates levels",
      "kind": "wall",
      "base_share": 0.3
    },
    {
      "id": "fire_pit",
      "label": "Fire pit",
      "icon": "Flame",
      "hint": "Wood-burning or gas",
      "kind": "fire_pit"
    },
    {
      "id": "outdoor_kitchen",
      "label": "Outdoor kitchen",
      "icon": "CookingPot",
      "hint": "Grill island to full kitchen",
      "kind": "kitchen"
    }
  ],
  "size_presets": {
    "patio": [
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
        "hint": "about 15 × 20 ft · 300 sq ft",
        "sqft": 300
      },
      {
        "id": "l",
        "label": "Large",
        "icon": "Grid3x3",
        "hint": "about 20 × 25 ft · 500 sq ft",
        "sqft": 500
      },
      {
        "id": "xl",
        "label": "Extra large",
        "icon": "LayoutGrid",
        "hint": "about 25 × 32 ft · 800 sq ft",
        "sqft": 800
      }
    ],
    "walkway": [
      {
        "id": "s",
        "label": "Short path",
        "icon": "Minus",
        "hint": "about 25 ft long × 4 ft wide · 100 sq ft",
        "sqft": 100
      },
      {
        "id": "m",
        "label": "Medium path",
        "icon": "Footprints",
        "hint": "about 50 ft × 4 ft · 200 sq ft",
        "sqft": 200
      },
      {
        "id": "l",
        "label": "Long path",
        "icon": "Route",
        "hint": "about 85 ft × 4 ft · 340 sq ft",
        "sqft": 340
      }
    ],
    "driveway": [
      {
        "id": "s",
        "label": "1-car",
        "icon": "Car",
        "hint": "about 10 × 40 ft · 400 sq ft",
        "sqft": 400
      },
      {
        "id": "m",
        "label": "2-car",
        "icon": "CarFront",
        "hint": "about 20 × 30 ft · 600 sq ft",
        "sqft": 600
      },
      {
        "id": "l",
        "label": "2-car, long",
        "icon": "Route",
        "hint": "about 20 × 50 ft · 1,000 sq ft",
        "sqft": 1000
      },
      {
        "id": "xl",
        "label": "Large or circular",
        "icon": "RefreshCw",
        "hint": "about 1,600 sq ft",
        "sqft": 1600
      }
    ],
    "pool_deck": [
      {
        "id": "s",
        "label": "Small pool",
        "icon": "Waves",
        "hint": "around a 12 × 24 pool · 400 sq ft",
        "sqft": 400
      },
      {
        "id": "m",
        "label": "Standard pool",
        "icon": "Waves",
        "hint": "around a 16 × 32 pool · 700 sq ft",
        "sqft": 700
      },
      {
        "id": "l",
        "label": "Large pool",
        "icon": "Waves",
        "hint": "around a 20 × 40 pool · 1,000 sq ft",
        "sqft": 1000
      },
      {
        "id": "xl",
        "label": "Pool + lounge area",
        "icon": "Sun",
        "hint": "about 1,500 sq ft",
        "sqft": 1500
      }
    ]
  },
  "custom_size": {
    "label": "I know my size",
    "icon": "Ruler",
    "hint": "Enter square feet",
    "limits": {
      "patio": [
        50,
        3000
      ],
      "walkway": [
        20,
        1500
      ],
      "driveway": [
        200,
        5000
      ],
      "pool_deck": [
        150,
        4000
      ]
    }
  },
  "wall": {
    "length_ft": {
      "min": 8,
      "max": 300,
      "default": 30,
      "step": 1
    },
    "heights": [
      {
        "id": "h1",
        "label": "Under 2 ft",
        "icon": "Minus",
        "hint": "Garden or border wall",
        "face_height_ft": 1.5,
        "multiplier": 1.0,
        "engineering": false
      },
      {
        "id": "h2",
        "label": "2–3 ft",
        "icon": "ChevronUp",
        "hint": "Most common",
        "face_height_ft": 2.5,
        "multiplier": 1.0,
        "engineering": false
      },
      {
        "id": "h3",
        "label": "3–4 ft",
        "icon": "ChevronsUp",
        "hint": "",
        "face_height_ft": 3.5,
        "multiplier": 1.1,
        "engineering": false
      },
      {
        "id": "h4",
        "label": "Over 4 ft",
        "icon": "TriangleAlert",
        "hint": "Usually needs an engineer and permit",
        "face_height_ft": 4.5,
        "multiplier": 1.3,
        "engineering": true
      }
    ]
  },
  "kitchen_sizes": [
    {
      "id": "island",
      "label": "Grill island",
      "icon": "Utensils",
      "hint": "6–8 ft straight run",
      "lf": 7
    },
    {
      "id": "l_shape",
      "label": "L-shaped",
      "icon": "UtensilsCrossed",
      "hint": "10–14 ft with bar seating",
      "lf": 12
    },
    {
      "id": "full",
      "label": "Full outdoor kitchen",
      "icon": "CookingPot",
      "hint": "15–20 ft, room for sink & fridge",
      "lf": 18
    },
    {
      "id": "custom",
      "label": "I know the length",
      "icon": "Ruler",
      "hint": "Enter counter length in ft",
      "lf_limits": [
        4,
        40
      ]
    }
  ],
  "materials": [
    {
      "id": "concrete_pavers",
      "label": "Concrete pavers",
      "icon": "Grid3x3",
      "hint": "Most popular · many colors",
      "per_sqft": {
        "low": 16,
        "high": 28
      },
      "sealable": true,
      "sand": true,
      "not_for": []
    },
    {
      "id": "travertine",
      "label": "Travertine",
      "icon": "Sun",
      "hint": "Stays cool underfoot · great by pools",
      "per_sqft": {
        "low": 25,
        "high": 40
      },
      "sealable": true,
      "sand": true,
      "not_for": []
    },
    {
      "id": "flagstone",
      "label": "Natural flagstone",
      "icon": "Mountain",
      "hint": "Irregular natural stone",
      "per_sqft": {
        "low": 24,
        "high": 42
      },
      "sealable": true,
      "sand": true,
      "not_for": [
        "driveway"
      ]
    },
    {
      "id": "porcelain",
      "label": "Porcelain pavers",
      "icon": "Square",
      "hint": "Modern look · stain-proof",
      "per_sqft": {
        "low": 28,
        "high": 45
      },
      "sealable": false,
      "sand": false,
      "not_for": [
        "driveway"
      ]
    },
    {
      "id": "stamped",
      "label": "Stamped concrete",
      "icon": "Stamp",
      "hint": "Poured slab with a stone pattern",
      "per_sqft": {
        "low": 14,
        "high": 24
      },
      "sealable": true,
      "sand": false,
      "not_for": []
    }
  ],
  "material_not_for_hint": "Not recommended for driveways",
  "wall_materials": [
    {
      "id": "block",
      "label": "Segmental block",
      "icon": "BrickWall",
      "hint": "Interlocking concrete block",
      "per_face_sqft": {
        "low": 40,
        "high": 65
      }
    },
    {
      "id": "natural",
      "label": "Natural stone",
      "icon": "Mountain",
      "hint": "Stacked stone or boulders",
      "per_face_sqft": {
        "low": 60,
        "high": 110
      }
    },
    {
      "id": "veneer",
      "label": "Stone-veneer wall",
      "icon": "Layers",
      "hint": "Poured or block core, stone face",
      "per_face_sqft": {
        "low": 70,
        "high": 120
      }
    }
  ],
  "fire_pit_types": [
    {
      "id": "kit",
      "label": "Block fire-pit kit",
      "icon": "Flame",
      "hint": "Wood-burning, about 3–4 ft across",
      "price": {
        "low": 1500,
        "high": 3000
      },
      "build_days": [
        1,
        2
      ]
    },
    {
      "id": "custom_stone",
      "label": "Custom stone fire pit",
      "icon": "Mountain",
      "hint": "Wood-burning, built to match",
      "price": {
        "low": 3000,
        "high": 6500
      },
      "build_days": [
        2,
        4
      ]
    },
    {
      "id": "gas",
      "label": "Gas fire pit or fire table",
      "icon": "Fuel",
      "hint": "Includes gas line up to 30 ft",
      "price": {
        "low": 4500,
        "high": 9500
      },
      "build_days": [
        2,
        5
      ]
    }
  ],
  "kitchen_finishes": [
    {
      "id": "standard",
      "label": "Standard",
      "icon": "Square",
      "hint": "Block with stucco or veneer, granite top",
      "per_lf": {
        "low": 900,
        "high": 1400
      }
    },
    {
      "id": "premium",
      "label": "Premium",
      "icon": "Gem",
      "hint": "Natural stone veneer, quartz or porcelain top",
      "per_lf": {
        "low": 1400,
        "high": 2200
      }
    },
    {
      "id": "luxury",
      "label": "Luxury",
      "icon": "Crown",
      "hint": "Custom stonework, bar, storage",
      "per_lf": {
        "low": 2200,
        "high": 3500
      }
    }
  ],
  "removal": {
    "area_options": [
      {
        "id": "none",
        "label": "Nothing — grass or dirt",
        "icon": "Sprout",
        "per_sqft": {
          "low": 0,
          "high": 0
        }
      },
      {
        "id": "concrete",
        "label": "Concrete slab",
        "icon": "Square",
        "per_sqft": {
          "low": 3,
          "high": 6
        }
      },
      {
        "id": "pavers",
        "label": "Old pavers or brick",
        "icon": "Grid3x3",
        "per_sqft": {
          "low": 2,
          "high": 4
        }
      },
      {
        "id": "asphalt",
        "label": "Asphalt",
        "icon": "Car",
        "per_sqft": {
          "low": 2.5,
          "high": 5
        }
      },
      {
        "id": "wood_deck",
        "label": "Old wood deck",
        "icon": "TreePine",
        "per_sqft": {
          "low": 4,
          "high": 7
        }
      }
    ],
    "wall_options": [
      {
        "id": "none",
        "label": "Nothing there now",
        "icon": "Sprout",
        "per_face_sqft": {
          "low": 0,
          "high": 0
        }
      },
      {
        "id": "old_wall",
        "label": "An old wall to remove",
        "icon": "BrickWall",
        "hint": "Timber, block or stone",
        "per_face_sqft": {
          "low": 15,
          "high": 30
        }
      }
    ],
    "disposal_flat": {
      "low": 300,
      "high": 700
    }
  },
  "site_options": [
    {
      "id": "flat",
      "label": "Flat and drains well",
      "icon": "Minus",
      "base_multiplier": 1.0
    },
    {
      "id": "gentle",
      "label": "Gentle slope",
      "icon": "TrendingUp",
      "base_multiplier": 1.2
    },
    {
      "id": "steep",
      "label": "Steep slope or needs regrading",
      "icon": "Mountain",
      "base_multiplier": 1.6,
      "build_days_add": [
        1,
        3
      ]
    },
    {
      "id": "pools",
      "label": "Water pools there after rain",
      "icon": "Droplets",
      "base_multiplier": 1.25,
      "adds_drainage": true,
      "build_days_add": [
        1,
        2
      ]
    },
    {
      "id": "unsure",
      "label": "Not sure",
      "icon": "CircleHelp",
      "base_multiplier": 1.2
    }
  ],
  "drainage": {
    "label": "Drainage (French drain or channel drain)",
    "low": 1500,
    "high": 4500
  },
  "addons": [
    {
      "id": "seat_wall",
      "label": "Seat wall",
      "icon": "Armchair",
      "hint": "About 12–16 ft of built-in seating",
      "pricing": "flat",
      "price": {
        "low": 2800,
        "high": 6500
      },
      "project_types": [
        "patio",
        "pool_deck",
        "fire_pit"
      ]
    },
    {
      "id": "steps",
      "label": "Steps",
      "icon": "TrendingUp",
      "hint": "Stone or paver steps, 4–6 ft wide",
      "pricing": "per_unit",
      "unit_label": "steps",
      "qty": {
        "min": 1,
        "max": 10,
        "default": 3
      },
      "price": {
        "low": 350,
        "high": 800
      },
      "project_types": [
        "patio",
        "walkway",
        "pool_deck",
        "retaining_wall"
      ]
    },
    {
      "id": "lighting",
      "label": "Lighting",
      "icon": "Lightbulb",
      "hint": "Low-voltage path, step or wall lights",
      "pricing": "flat",
      "price": {
        "low": 1200,
        "high": 3500
      },
      "project_types": [
        "patio",
        "walkway",
        "driveway",
        "pool_deck",
        "retaining_wall",
        "fire_pit",
        "outdoor_kitchen"
      ]
    },
    {
      "id": "sand_seal",
      "label": "Polymeric sand + sealing",
      "label_by_material": {
        "stamped": "Sealing"
      },
      "icon": "SprayCan",
      "hint": "Locks joints, resists weeds and stains",
      "pricing": "per_sqft",
      "price": {
        "low": 1.5,
        "high": 3
      },
      "project_types": [
        "patio",
        "walkway",
        "driveway",
        "pool_deck"
      ],
      "requires_material_flag": "sealable",
      "disabled_hint": "Porcelain doesn't need sealing"
    },
    {
      "id": "gas_line",
      "label": "Gas line",
      "icon": "Fuel",
      "hint": "For a built-in grill, up to 40 ft",
      "pricing": "flat",
      "price": {
        "low": 800,
        "high": 2500
      },
      "project_types": [
        "outdoor_kitchen"
      ]
    },
    {
      "id": "electrical",
      "label": "Outlets and power",
      "icon": "Plug",
      "hint": "GFCI outlets, fridge, lights",
      "pricing": "flat",
      "price": {
        "low": 1000,
        "high": 3000
      },
      "project_types": [
        "outdoor_kitchen"
      ]
    },
    {
      "id": "sink",
      "label": "Sink and plumbing",
      "icon": "Droplet",
      "hint": "Water line and drain",
      "pricing": "flat",
      "price": {
        "low": 1500,
        "high": 4000
      },
      "project_types": [
        "outdoor_kitchen"
      ]
    }
  ],
  "permits": {
    "driveway": {
      "label": "Permit (where required)",
      "low": 300,
      "high": 900
    },
    "retaining_wall_engineered": {
      "label": "Engineering & permit",
      "low": 1500,
      "high": 4000
    },
    "outdoor_kitchen": {
      "label": "Permit & inspections (gas/electric)",
      "low": 500,
      "high": 1500
    }
  },
  "min_job": {
    "label": "Small-job minimum",
    "low": 2500,
    "high": 4000,
    "exempt_types": [
      "fire_pit"
    ]
  },
  "build_days": {
    "area_tiers": [
      {
        "max_sqft": 300,
        "days": [
          2,
          4
        ]
      },
      {
        "max_sqft": 700,
        "days": [
          3,
          6
        ]
      },
      {
        "max_sqft": 1200,
        "days": [
          5,
          9
        ]
      },
      {
        "max_sqft": 100000,
        "days": [
          7,
          14
        ]
      }
    ],
    "wall_tiers": [
      {
        "max_lf": 40,
        "days": [
          2,
          4
        ]
      },
      {
        "max_lf": 100,
        "days": [
          4,
          8
        ]
      },
      {
        "max_lf": 100000,
        "days": [
          7,
          14
        ]
      }
    ],
    "kitchen": {
      "island": [
        4,
        7
      ],
      "l_shape": [
        7,
        12
      ],
      "full": [
        10,
        20
      ],
      "custom_per_lf": [
        0.6,
        1.1
      ]
    },
    "removal_add": [
      1,
      2
    ]
  },
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
      "urgent": false
    },
    {
      "id": "3_6",
      "label": "In 3–6 months",
      "icon": "Calendar",
      "urgent": false
    },
    {
      "id": "planning",
      "label": "Just planning",
      "icon": "Calculator",
      "hint": "Getting a feel for cost",
      "urgent": false
    }
  ],
  "budget_bands": [
    {
      "id": "u10",
      "label": "Under $10k"
    },
    {
      "id": "10_25",
      "label": "$10k–$25k"
    },
    {
      "id": "25_50",
      "label": "$25k–$50k"
    },
    {
      "id": "50_100",
      "label": "$50k–$100k"
    },
    {
      "id": "100p",
      "label": "$100k+"
    },
    {
      "id": "unsure",
      "label": "Not sure yet"
    }
  ],
  "copy": {
    "h1": "What will your patio or hardscape project cost?",
    "sub": "Pick your project and materials. See an itemized price range in about 45 seconds. No consult fee, no signup.",
    "result_title": "Your estimated project price",
    "result_subtitle": {
      "area": "{sqft} sq ft {material_label} {type_label} · prices typical for {city}",
      "wall": "{length_ft} ft {wall_material_label} retaining wall, {height_label} · prices typical for {city}",
      "fire_pit": "{fire_type_label} · prices typical for {city}",
      "kitchen": "{lf} ft {finish_label} outdoor kitchen · prices typical for {city}"
    },
    "build_time": "Typical install: about {days_low}–{days_high} working days on site.",
    "permit_note_engineered": "Walls over 4 ft usually need an engineered design and a permit. That can add 2–6 weeks before work starts.",
    "kitchen_appliances_note": "Appliances aren't included. A built-in grill typically runs $1,500–$6,000, and a fridge or side burner $500–$2,500 each.",
    "porcelain_note": "Porcelain doesn't need sealing, so we've hidden that option.",
    "disclaimer": "Estimate only — final price confirmed after a free on-site visit. Ranges are typical installed prices for {city_or_your_area}. They assume normal soil and machine access to the work area.",
    "cta_primary": "Get my exact quote",
    "cta_secondary": "Email me this breakdown",
    "contact_heading": "Want the exact number?",
    "contact_sub": "{business_name} will measure, check the ground and confirm your price at a free on-site visit. No consult fee.",
    "included": {
      "area": [
        "Excavation and haul-off of soil",
        "Compacted gravel base (thicker for driveways)",
        "Edge restraint to keep pavers in place",
        "Cutting and fitting around curves and edges",
        "Joint sand",
        "Job-site cleanup"
      ],
      "wall": [
        "Excavation and a compacted gravel footing",
        "Drainage stone and a perforated drain pipe behind the wall",
        "Geogrid reinforcement where needed",
        "Wall caps",
        "Backfill and cleanup"
      ],
      "fire_pit": [
        "Level, compacted base",
        "Fire-rated insert or liner",
        "Gas line up to 30 ft (gas option only)",
        "Cleanup"
      ],
      "kitchen": [
        "Footing or slab under the island",
        "Block structure and finish",
        "Countertop",
        "Cut-outs for your appliances",
        "Cleanup"
      ]
    },
    "not_included": {
      "area": [
        "Moving sprinkler lines or utilities in the way",
        "Rock or poor soil found when digging",
        "Tree or stump removal",
        "Landscaping and sod repair beyond the work area",
        "Pool coping (ask about pool decks)"
      ],
      "wall": [
        "Engineering and permit on walls under 4 ft (only if your town requires it)",
        "Rock found when digging",
        "Moving fences or sprinklers",
        "Planting on the new levels"
      ],
      "fire_pit": [
        "A patio around the fire pit (try the Patio option)",
        "Seating",
        "Running gas more than 30 ft"
      ],
      "kitchen": [
        "Appliances (grill, fridge, burners)",
        "Gas, power or water, unless you added them",
        "A patio or slab under the seating area",
        "Roof or pergola"
      ]
    },
    "price_drivers": [
      "Size. Every extra 100 sq ft adds roughly {per100_low}–{per100_high} in your material",
      "Material. Porcelain and natural stone cost up to twice what concrete pavers do",
      "Ground prep. Slopes, soft soil and drainage fixes are the hidden half of most quotes",
      "Removal. Breaking out old concrete is slow work",
      "Access. If no machine can reach the backyard, more of the work is done by hand",
      "Extras. Seat walls, steps and lighting add up quickly"
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
- `project_types[].kind` drives the whole flow. It is one of `area` (patio, walkway, driveway, pool deck), `wall`, `fire_pit` or `kitchen`.
- `materials[].per_sqft` is the **all-in installed** rate on flat ground. `project_types[].base_share` is the share of that rate that is excavation, base and grading. The site multiplier applies to that share only.
- `addons[].project_types` lists where each add-on is offered.

---

## 4. Step-by-step flow (5–7 steps, by project kind)

| Kind | Steps shown |
|---|---|
| `area` | 1 type → 2 size → 3 material → 4 removal → 5 site → 6 add-ons → 7 timeline |
| `wall` | 1 → 2 (length + height) → 3 wall material → 4 removal (wall options) → 5 site → 6 add-ons → 7 timeline |
| `fire_pit` | 1 → 3 fire-pit type → 6 add-ons → 7 timeline (2, 4 and 5 skipped) |
| `kitchen` | 1 → 2 kitchen size → 3 finish → 6 add-ons → 7 timeline (4, 5 skipped) |

The progress bar counts only the steps shown for the chosen kind. Single-select steps auto-advance after 250 ms.

### Step 1: `type`
- **Question:** "What are you planning?"
- **Helper:** "Pick the main project. You can price another one after."
- **Input:** single-select cards from `project_types` (2 columns, the 7th card spans both).
- **Options:** `patio`, `walkway`, `driveway`, `pool_deck`, `retaining_wall`, `fire_pit`, `outdoor_kitchen`.
- **Default:** none. **Validation:** required.
- **Branch:** sets the step list per the table above.
  - If the user goes Back and changes the type, clear the answers for steps 2–6. Keep the timeline.

### Step 2: size (variant by kind)
- **`area`: field `size` (+ `sqft`)**
  - **Question:** "About how big?" **Helper:** "Pace it out or guess. Your installer will measure."
  - Cards from `size_presets[type]`, plus the `custom_size` card.
  - Custom: slider + number box in sq ft, limits `custom_size.limits[type]`, default = the preset `m` sqft.
  - **Validation:** integer within the limits. On overflow, clamp and show "For bigger projects, {business_name} will measure on site."
- **`wall`: fields `length_ft` + `wall_height`**, on one screen.
  - **Question:** "How long and how tall is the wall?"
  - Slider + number box "Length (ft)": min 8, max 300, default 30.
  - Below it, single-select height cards from `wall.heights`: `h1`, `h2`, `h3`, `h4`.
  - **Validation:** both required. Do not auto-advance.
  - **Branch:** `h4` shows an amber inline note: `copy.permit_note_engineered`.
- **`kitchen`: field `kitchen_size` (+ `lf`)**
  - **Question:** "How big a kitchen?"
  - Cards from `kitchen_sizes`. `custom` reveals a number box "Counter length (ft)" 4–40, default 10.
  - **Validation:** required. Custom must be an integer within 4–40.

### Step 3: material (variant)
- **`area`: field `material`**
  - **Question:** "Which material?"
  - **Helper:** "Not sure? Concrete pavers are the most popular. You can switch on the result screen."
  - Cards from `materials` (show hints).
  - If `type` is in a material's `not_for`, show that card disabled with `material_not_for_hint`. This applies to flagstone and porcelain for driveways.
  - **Default:** none. **Validation:** required.
- **`wall`: field `wall_material`.** "What should the wall be made of?" Cards from `wall_materials`.
- **`fire_pit`: field `fire_type`.** "What kind of fire pit?" Cards from `fire_pit_types`.
- **`kitchen`: field `finish`.** "What level of finish?" Cards from `kitchen_finishes`.

### Step 4: `removal` (`area` and `wall` only)
- **Question:** "What's there now?"
- **Helper:** "We'll include taking it out and hauling it away."
- **Input:** single-select cards: `removal.area_options` (area) or `removal.wall_options` (wall).
- **Default:** none. **Validation:** required.

### Step 5: `site` (`area` and `wall` only)
- **Question:** "How's the ground where it'll go?"
- **Helper:** "Ground prep is the hidden half of most quotes. This helps us get it right."
- **Input:** single-select cards from `site_options`: `flat`, `gentle`, `steep`, `pools`, `unsure`.
- **Default:** none. **Validation:** required.
- **Branch:** `pools` adds the drainage line in the calculation.

### Step 6: `addons` (object `{id: qty}`)
- **Question:** "Any add-ons?"
- **Helper:** "Optional — pick any that apply."
- **Input:** multi-select cards. Show only add-ons where `project_types` includes the current type.
  - `steps` (`pricing: per_unit`): when selected, the card expands an inline − / + stepper, `qty.min`–`qty.max`, default 3.
  - `sand_seal`: shown only for area types. Disabled with `disabled_hint` when the material has `sealable:false` (porcelain). Its label becomes `label_by_material[material]` when present (stamped → "Sealing").
- **Default:** `{}`. **Validation:** optional. The Next button reads "Skip" when nothing is selected.

### Step 7: `timeline`
- **Question:** "When would you like it done?"
- **Input:** single-select cards from `timelines`: `asap`, `1_3`, `3_6`, `planning`.
- **Default:** none. **Validation:** required.
- **Branch:** `asap` sets `urgent`.
- Then a 600 ms "Pricing your project…" shimmer, then the result.

---

## 5. Calculation logic

Pure function `computeHardscapeEstimate(answers, cfg, prospect)` in `src/tools/patio-paver-cost-estimator/calc.ts`.
`r()` is the standard rounding: nearest $100, or nearest $50 under $2,000.

```ts
const m  = cfg.regional_multipliers[prospect?.state ?? ''] ?? 1.0;
const pt = cfg.project_types.find(p => p.id === type);
const site = kind in ['area','wall'] ? cfg.site_options.find(s => s.id === answers.site) : null;
const lines = []; let days = [0,0]; let area = null, face = null;

if (pt.kind === 'area') {
  area = answers.size === 'custom' ? answers.sqft : cfg.size_presets[type].find(p => p.id === answers.size).sqft;
  const mat = cfg.materials.find(x => x.id === answers.material);
  const bs = pt.base_share, tm = pt.type_multiplier, sm = site.base_multiplier;
  lines.push({ id:'base', label:`Excavation, base & grading (${fmt(area)} sq ft)`,
    low: area*mat.per_sqft.low*bs*tm*sm*m,  high: area*mat.per_sqft.high*bs*tm*sm*m });
  lines.push({ id:'surface', label:`${mat.label} supply & install`,
    low: area*mat.per_sqft.low*(1-bs)*tm*m, high: area*mat.per_sqft.high*(1-bs)*tm*m });
  days = cfg.build_days.area_tiers.find(t => area <= t.max_sqft).days;
}
if (pt.kind === 'wall') {
  const h = cfg.wall.heights.find(x => x.id === answers.wall_height);
  const wm = cfg.wall_materials.find(x => x.id === answers.wall_material);
  face = answers.length_ft * h.face_height_ft;                  // sq ft of wall face
  const bs = pt.base_share, sm = site.base_multiplier;
  lines.push({ id:'footing', label:`Excavation, footing & drainage stone (${answers.length_ft} ft)`,
    low: face*wm.per_face_sqft.low*h.multiplier*bs*sm*m, high: face*wm.per_face_sqft.high*h.multiplier*bs*sm*m });
  lines.push({ id:'wall', label:`${wm.label} wall build (${face} sq ft of wall face)`,
    low: face*wm.per_face_sqft.low*h.multiplier*(1-bs)*m, high: face*wm.per_face_sqft.high*h.multiplier*(1-bs)*m });
  days = cfg.build_days.wall_tiers.find(t => answers.length_ft <= t.max_lf).days;
}
if (pt.kind === 'fire_pit') {
  const f = cfg.fire_pit_types.find(x => x.id === answers.fire_type);
  lines.push({ id:'fire_pit', label:f.label, low:f.price.low*m, high:f.price.high*m }); days = f.build_days;
}
if (pt.kind === 'kitchen') {
  const ks = cfg.kitchen_sizes.find(x => x.id === answers.kitchen_size);
  const lf = ks.id === 'custom' ? answers.lf : ks.lf;
  const fin = cfg.kitchen_finishes.find(x => x.id === answers.finish);
  lines.push({ id:'kitchen', label:`Kitchen structure & countertop (${lf} ft, ${fin.label})`,
    low: lf*fin.per_lf.low*m, high: lf*fin.per_lf.high*m });
  days = ks.id === 'custom' ? [Math.ceil(lf*cfg.build_days.kitchen.custom_per_lf[0]), Math.ceil(lf*cfg.build_days.kitchen.custom_per_lf[1])]
                            : cfg.build_days.kitchen[ks.id];
}

if (site?.adds_drainage) lines.push({ id:'drainage', label:cfg.drainage.label, low:cfg.drainage.low*m, high:cfg.drainage.high*m });
if (site?.build_days_add) days = [days[0]+site.build_days_add[0], days[1]+site.build_days_add[1]];

if (answers.removal && answers.removal !== 'none') {
  const opt = (area !== null ? cfg.removal.area_options : cfg.removal.wall_options).find(o => o.id === answers.removal);
  const q = area ?? face; const rate = opt.per_sqft ?? opt.per_face_sqft;
  lines.push({ id:'removal', label:`Remove & haul away ${opt.label.toLowerCase()}`,
    low:(q*rate.low + cfg.removal.disposal_flat.low)*m, high:(q*rate.high + cfg.removal.disposal_flat.high)*m });
  days = [days[0]+cfg.build_days.removal_add[0], days[1]+cfg.build_days.removal_add[1]];
}

for (const ad of cfg.addons) if (ad.id in answers.addons) {     // config order
  const q = ad.pricing === 'flat' ? 1 : ad.pricing === 'per_unit' ? answers.addons[ad.id] : area;
  const label = ad.pricing === 'per_unit' ? `${ad.label} (${q})` : (ad.label_by_material?.[answers.material] ?? ad.label);
  lines.push({ id:ad.id, label, low:q*ad.price.low*m, high:q*ad.price.high*m });
}

if (type === 'driveway')                       push(cfg.permits.driveway);
if (pt.kind === 'wall' && h.engineering)       push(cfg.permits.retaining_wall_engineered);
if (pt.kind === 'kitchen')                     push(cfg.permits.outdoor_kitchen);       // push = {label, low*m, high*m}

// Small-job minimum (not for fire pits), compared on unrounded sums
if (!cfg.min_job.exempt_types.includes(type)) {
  const sL = Σlow, sH = Σhigh, mL = cfg.min_job.low*m, mH = cfg.min_job.high*m;
  if (sL < mL || sH < mH) lines.push({ id:'min_job', label:cfg.min_job.label, low:Math.max(0,mL-sL), high:Math.max(0,mH-sH) });
}

total = { low: r(Σlow), high: r(Σhigh) };  mid = Math.round((total.low + total.high)/2);
// each displayed line = r(low) – r(high)

// "What changes your price" placeholders (area kinds only; omit that bullet for other kinds)
per100 = 100*mat.per_sqft.{low|high}*tm*(bs*sm + (1-bs))*m → r()
```

### Edge cases
- **Driveway + flagstone/porcelain:** the card is disabled, so it can't be selected. If the URL state has it, reset the step to unanswered.
- **Porcelain + `sand_seal`:** the add-on is disabled and `copy.porcelain_note` shows. If it is already in state from an earlier material choice, drop it when the material changes.
- **Fire pit:** no size, removal or site step, no min-job line. **Kitchen:** no removal or site step. Always show `copy.kitchen_appliances_note` on the result.
- **Wall `h4`:** adds the engineering & permit line, the amber note on Step 2 and the result, and the 1.3 multiplier.
- **Changing type on Back** clears steps 2–6.
- **Min job:** a small walkway (e.g. 60 sq ft stamped on flat ground) triggers the `Small-job minimum` line. Never show a total under `min_job × m`, except for fire pits.
- **No prospect:** m = 1.0 and "your area".

### Worked examples (verified against this config)

**Example 1: medium paver patio replacing a concrete slab, gentle slope, Georgia (m = 0.95)**
Answers: `patio`, size `m` (300 sq ft), `concrete_pavers`, removal `concrete`, site `gentle`, add-ons `{seat_wall:1, sand_seal:1}`, timeline `1_3`.

| Line | Low | High |
|---|---|---|
| Excavation, base & grading (300 sq ft) | $1,900 | $3,400 |
| Concrete pavers supply & install | $3,000 | $5,200 |
| Remove & haul away concrete slab | $1,150 | $2,400 |
| Seat wall | $2,700 | $6,200 |
| Polymeric sand + sealing | $450 | $850 |
| **Total** | **$9,100** | **$17,900** |

The base line is 300 × 16 × 0.35 × 1.0 × 1.2 × 0.95 = 1,915.2 → $1,900. Build days 2–4 (tier) + removal 1–2 = **3–6 days**. per100 = $1,650–$2,800. Meta `value` = **13500**.

**Example 2: 60 ft engineered block retaining wall over 4 ft, steep slope, California (m = 1.30)**
Answers: `retaining_wall`, length 60, height `h4` (face 4.5 ft → 270 sq ft), `block`, removal `none`, site `steep`, add-ons `{steps:4}`, timeline `3_6`.

| Line | Low | High |
|---|---|---|
| Excavation, footing & drainage stone (60 ft) | $8,800 | $14,200 |
| Segmental block wall build (270 sq ft of wall face) | $12,800 | $20,800 |
| Steps (4) | $1,800 | $4,200 |
| Engineering & permit | $1,950 | $5,200 |
| **Total** | **$25,300** | **$44,400** |

The footing line is 270 × 40 × 1.3 × 0.30 × 1.6 × 1.3 = 8,761 → $8,800. Build days 4–8 + steep 1–3 = **5–11 days**. The amber engineering note shows. Meta `value` = **34850**.

**Example 3: L-shaped premium outdoor kitchen with gas and power, Florida (m = 1.00)**
Answers: `outdoor_kitchen`, `l_shape` (12 ft), finish `premium`, add-ons `{gas_line:1, electrical:1}`, timeline `asap` (urgent).

| Line | Low | High |
|---|---|---|
| Kitchen structure & countertop (12 ft, Premium) | $16,800 | $26,400 |
| Gas line | $800 | $2,500 |
| Outlets and power | $1,000 | $3,000 |
| Permit & inspections (gas/electric) | $500 | $1,500 |
| **Total** | **$19,100** | **$33,400** |

Build days **7–12**. The appliances note shows. Meta `value` = **26250**.

---

## 6. Result screen

1. **Eyebrow:** `copy.result_title`.
2. **Big two-tone range** with the range bar and midpoint marker (§8).
3. **Subtitle:** `copy.result_subtitle[kind]`, filled, e.g. "300 sq ft Concrete pavers patio · prices typical for Atlanta". Use lower-case type labels inside the sentence.
4. **Chip:** lucide `Clock` + `copy.build_time`.
5. **Amber notes** (as applicable):
   - `permit_note_engineered` (wall h4)
   - `kitchen_appliances_note` (kitchen)
   - `porcelain_note` (porcelain)
6. **"Your price, line by line"** table: Item | Range, with a bold total. Gray note: "Lines rounded; total is exact to the nearest $100."
7. **"Try a different material"** quick-edit (area kinds only):
   - A horizontal chip row of the materials allowed for this type. Tapping one recomputes in place.
   - Log `tool_events` `step` `{quick_edit:'material'}`.
   - Wall kind: the same for `wall_materials`. Kitchen kind: for `kitchen_finishes`.
8. **Included / not included:** `copy.included[kind]` / `copy.not_included[kind]`, side by side (stacked on mobile).
9. **What changes your price:** `copy.price_drivers`. Omit the first bullet for non-area kinds.
10. **Disclaimer:** `copy.disclaimer`, under the price block and at the bottom.
11. Contact card.

---

## 7. Contact card

- **Heading:** `copy.contact_heading` "Want the exact number?" **Sub:** `copy.contact_sub` (includes "No consult fee").
- **Primary submit:** **"Get my exact quote"** (`copy.cta_primary`).
- **Secondary:** **"Email me this breakdown"** (`intent='email_breakdown'`).
- **Extra fields:**
  1. `budget_band`: select from `budget_bands` (optional).
  2. `hoa`: segmented Yes / No / Not sure (optional), "HOA approval needed?"
  3. Photo upload (standard), labeled "Photos of the area (optional — speeds up your quote)".
  4. `want_design`: checkbox "I'd also like design ideas or a rendering" (optional; flows to the email).
- **Urgency:** `timeline === 'asap'`.
- **Thank-you variant:** "{business_name} has your request and will reach out to set up a free on-site measure." Summary card shows the project, size/length, material, add-ons and the range. "Today" wording when urgent.

---

## 8. Business notification email

- **Subject:** `New Patio & Paver Cost Estimator request — {contact.name}, {city or zip}`. Prefix `🔴 URGENT · ` when urgent.
- **Headline:** `{contact.name} priced a {size phrase} {material/finish label} {type label}: {total.low} – {total.high}`
  - Size phrase: "{sqft} sq ft" for area, "{length} ft × {height label}" for a wall, "{lf} ft" for a kitchen, empty for a fire pit.
- **Sub-headline:** `Now there: {removal label or "—"} · Ground: {site label or "—"} · Add-ons: {labels or "none"} · Timeline: {timeline label}`. Add `· Wants design ideas` when checked.
- Then the platform blocks, plus the line-item table.

---

## 9. Personalization hooks (`config_overrides["patio-paver-cost-estimator"]`)

| Key | Use |
|---|---|
| `materials` (whole array) | Their $/sq ft; remove materials they don't install |
| `project_types` (whole array) | Hide project types they don't do (e.g. remove `outdoor_kitchen`); tune `type_multiplier`, `base_share` |
| `wall_materials`, `wall.heights[].multiplier` | Wall pricing |
| `fire_pit_types`, `kitchen_finishes`, `kitchen_sizes` | Feature pricing |
| `removal.*`, `site_options[].base_multiplier`, `drainage` | Their prep and removal costs |
| `addons` (whole array) | Prices; add or remove add-ons |
| `permits.*`, `min_job` | Local permit costs and their minimum |
| `size_presets.*`, `custom_size.limits` | Typical sizes in their market |
| `regional_multipliers` | Their state factor |
| `copy.included.*`, `copy.not_included.*`, `copy.contact_sub` | Their scope, warranty, and free vs paid design |

---

## 10. Meta events

- **`ToolResult`:** `{tool:'patio-paver-cost-estimator', niche:'hardscape', project_type, material_or_variant, size_value, range_low, range_high}`
- **`Lead`:** `value` = `mid` (13500 / 34850 / 26250 in the examples), `currency:'USD'`. CAPI `custom_data.value` = the same.
- **`ToolQuickEdit`** (custom): `{tool, field:'material'}`.

---

## 11. QA checklist

1. Examples 1–3 reproduce every line, total, build-day range and Meta value. Add them as unit tests.
2. The step list matches the kind table. Fire pit shows 4 steps, kitchen 5, area and wall 7, and the progress bar reflects that.
3. Driveway disables the flagstone and porcelain cards with the hint. Porcelain disables `sand_seal` and shows the note. Stamped relabels the add-on to "Sealing".
4. The `steps` add-on stepper clamps to 1–10. The line label reads "Steps (n)".
5. Wall `h4` shows the amber note on Step 2 and the result, and adds "Engineering & permit".
6. Site `pools` adds the drainage line. `steep` adds 1–3 build days.
7. Fire pit kit, TX: **$1,450 – $2,900**, no min-job line, 1–2 days.
8. Changing the type via Back clears steps 2–6 and recomputes. No stale add-ons from another type appear.
9. The price, table and disclaimer render before any contact field. The submit writes all answers and the result, sends the email, posts to n8n, and fires Lead with matching event_id.
10. A per-prospect override of `materials` (e.g. concrete pavers `{low:20, high:32}`) changes only that prospect's page.
11. 360 px: the material chip row scrolls inside its own container (allowed), the page itself never scrolls horizontally, and the table labels wrap.
