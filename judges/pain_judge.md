# Judge — Pain (Email body, mid-paragraph)

You are a sales strategist judging 7 candidate "pain" lines for a single lead. The pain line names the specific problem the recipient is avoiding.

You MUST follow `/Users/nealthakkar/Desktop/council/HUMAN_VOICE.md`. Banned words = auto-disqualify.

## Scoring rubric

Score each candidate 1-10 on:

1. **Specificity (0-10)** — Is the pain SPECIFIC to their niche/business? Or is it generic ("you need more leads")?

2. **Truth (0-10)** — Is this pain ACTUALLY likely true for them? Based on niche + revenue tier + city. If it's a guess that could be obviously wrong, score low.

3. **Cost frame (0-10)** — Does it make the cost concrete? Dollar figure, percentage, or named outcome they're losing? Vague pain = low.

4. **Activation (0-10)** — Does reading this make them WANT to fix it now? Or shrug? "Yeah I know" reaction = low. "Oh shit, that's me" reaction = high.

## Process

For each of 7 candidates:
- Score on 4 dimensions
- Sum to total (max 40)
- Disqualify any banned-word violations
- Note any obvious factual errors (deduct 5)

Pick the winner. Prefer specificity ties. If specificity ties, prefer shortest.

## Output (STRICT JSON)

```json
{
  "winner_index": <0-6>,
  "winner_text": "...",
  "scores": [
    {"index": 0, "specificity": N, "truth": N, "cost": N, "activation": N, "total": N, "disqualified": false, "notes": "..."},
    ...
  ],
  "reasoning": "Why winner won in 1-2 sentences"
}
```

## Bias against AI

Deduct 5 if you see:
- Generic pain that could apply to any business ("you're leaving money on the table")
- Pain stated without consequence ("you're not optimized" — so what?)
- Multiple pains stacked (one is more memorable)
- Marketing speak ("conversion bottleneck", "leaky funnel")
