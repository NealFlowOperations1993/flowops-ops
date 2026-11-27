# FlowOps Tool Studio — Platform Spec (shared by all 18 tools)

Paste this file into Lovable FIRST (as one prompt) to build the shell. Then paste each tool spec
(`<niche>_<tool>.md`) as its own prompt. Every tool spec assumes this platform exists.

---

## 0. What we are building (one paragraph for the builder)

**One** Lovable project called **"FlowOps Tool Studio"**. It hosts 18 interactive customer-facing tools
(estimators, checkers, calculators) for 9 niches. Every tool renders **personalized for one prospect business**
from a URL like `/{tool_slug}/{prospect_slug}`. For example, `/fence-cost-estimator/k2-fence-austin` shows K2 Fence's
name, logo, color, phone, city and price ranges.

We send that URL in a cold email to the owner of that business. They can try it as their own homeowner would.
Every submission is:
1. saved,
2. emailed to the business,
3. posted to our n8n webhook, and
4. fired as a Meta Pixel + Conversions API `Lead` event on the FlowOperations pixel.

The tool must work perfectly with **no prospect slug** (generic demo using niche defaults), so it can be shown on a sales call.

---

## 1. Tech + global rules

- **Stack:** React + Vite + TypeScript + Tailwind + shadcn/ui (Lovable default), with Supabase (Lovable Cloud) for DB, storage and edge functions.
- **Mobile-first.** 80%+ of cold-email clicks are on phones. Design at 390px width first. Tap targets ≥ 44px. No horizontal scroll.
- **Speed:** each tool route must reach Largest Contentful Paint (when the main content appears) under 2.0s on 4G.
  - Lazy-load each tool's code (one chunk per route).
  - Use no external fonts except one Google Font (Inter).
- **Accessibility:** every input has a label. Contrast passes WCAG AA. The stepper can be used with the keyboard.
- **No login for end users.** Admin pages (`/admin/*`) require Supabase auth, with an email allowlist held in the table `tool_admins`.
- **Number formatting:** US currency with no cents for ranges (e.g. `$8,400 – $11,900`), cents only where they matter (monthly payments).
- **Every estimate is a RANGE (low – high), never a single number.**
  - Show "Estimate only — final price confirmed after a free on-site visit." under every price result.
  - Finance tools use instead: "Illustrative estimate, not an offer to lend, a rate quote, a commitment, or financial advice."
- **Price before contact info.** The user sees their estimate or result **before** being asked for contact details.
  The contact form unlocks extras: "Email me this breakdown", "Get my exact quote", "Book my visit".
  - VOC showed customers punish companies that demand personal info first.
  - Exception: the finance tools may gate the detailed PDF, but the headline result is always shown first.
- **Disclosure footer on every tool page** (small, gray):
  - With a prospect: "This tool was set up for {business_name} by FlowOperations. Requests go directly to {business_name}."
  - Without a prospect: "Demo by FlowOperations."
  - This keeps it honest. We are not impersonating the business to the public.

---

## 2. Routing

| Route | Purpose |
|---|---|
| `/` | Simple index of all tools (internal; noindex) |
| `/:toolSlug` | Generic demo of a tool (niche defaults, FlowOperations branding) |
| `/:toolSlug/:prospectSlug` | Personalized tool for one prospect |
| `/t/:shortCode` | Short link → resolves to `/:toolSlug/:prospectSlug` (6-char code, for cold email) |
| `/admin` | Prospect list, bulk import, submissions, per-tool stats |
| `/admin/prospects/:id` | Edit one prospect's customization with live preview |

- If `prospectSlug` is not found, render the generic demo (do NOT 404). Log the miss to `tool_events` with `event='prospect_not_found'`.
- All pages: `<meta name="robots" content="noindex,nofollow">`.
  - We do not want prospect-personalized pages in Google.

---

## 3. Database (Supabase) — create exactly these tables

```sql
-- tools registry (seed one row per tool; each tool spec gives its row)
create table tools (
  slug text primary key,              -- e.g. 'fence-cost-estimator'
  niche text not null,                -- 'fence','tree','roofing','hvac','pest','pool','loan_officer','wealth','biz_lender'
  name text not null,                 -- display name
  default_config jsonb not null,      -- niche-default pricing/ranges/options (each tool spec defines the shape)
  is_finance boolean default false,
  active boolean default true
);

-- one row per prospect business (bulk-importable from CSV)
create table tool_prospects (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null,          -- 'k2-fence-austin' (lowercase, hyphens; generated from business name + city)
  short_code text unique not null,    -- 6 chars [a-z0-9], generated
  business_name text not null,
  owner_first_name text,
  owner_email text,                   -- where submissions are emailed (the prospect)
  notify_emails text[] default '{}',  -- extra recipients
  phone text,                         -- shown as tap-to-call
  website text,
  city text, state text,
  service_area text,                  -- e.g. 'Austin & Round Rock'
  logo_url text,                      -- optional; falls back to monogram
  brand_color text default '#0F766E', -- hex; used for buttons/accents
  niche text not null,
  tool_slugs text[] not null,         -- which tools are enabled for this prospect
  config_overrides jsonb default '{}',-- per-tool overrides: { "fence-cost-estimator": { "price_per_ft": {...} } }
  smartlead_lead_id text,             -- for joining back to the campaign
  campaign_id text,
  created_at timestamptz default now()
);

create table tool_submissions (
  id uuid primary key default gen_random_uuid(),
  tool_slug text not null references tools(slug),
  prospect_id uuid references tool_prospects(id),
  answers jsonb not null,             -- every step answer, keyed by field id
  result jsonb not null,              -- computed output (ranges, tier, verdict)
  contact jsonb,                      -- {name,email,phone,address,zip,best_time,consent_text,consent_at}
  utm jsonb,                          -- utm_* + fbclid + referrer
  meta_event_id text,                 -- shared by Pixel + CAPI for dedup
  notified_at timestamptz,
  n8n_status int,
  created_at timestamptz default now()
);

create table tool_events (            -- lightweight analytics
  id bigserial primary key,
  tool_slug text, prospect_id uuid,
  event text not null,                -- 'view','start','step','result_shown','contact_open','submit','call_click','prospect_not_found'
  step int, meta jsonb, created_at timestamptz default now()
);

create table tool_admins (email text primary key);
```

**RLS:**
- `tools` and `tool_prospects`: public SELECT of display fields only. Expose them through a view `tool_prospects_public` that **excludes** owner_email, notify_emails and smartlead_lead_id.
- `tool_submissions` and `tool_events`: INSERT only through edge functions (service role). No public SELECT.
- Admins (email in `tool_admins`): full access.

---

## 4. Personalization (what "immediately customizable" means)

Every visible string that names the business comes from `tool_prospects`:
- the business name in the H1 subtitle ("by {business_name}")
- the logo, or a monogram circle with initials in brand_color
- the CTA button color = brand_color (auto-pick white or black text by luminance)
- the phone as a sticky tap-to-call bar on mobile ("Call {business_name}: (512) 555-0100")
- city / service_area in copy ("Prices typical for {city}")

**Pricing:** `tools.default_config` deep-merged with `tool_prospects.config_overrides[tool_slug]`.
- So we can tune one prospect's price per foot in /admin without code.

**Regional multiplier:**
- `default_config.regional_multipliers` is a map from state to a multiplier (e.g. `{"CA":1.25,"NY":1.2,"TX":0.95,...}`, default 1.0).
- The multiplier is applied to all cost ranges using `tool_prospects.state`.
- Seed it with the table in §9.

**Admin bulk import (`/admin` → "Import prospects CSV"):**
- Columns: `business_name, owner_first_name, owner_email, phone, website, city, state, niche, logo_url, brand_color, smartlead_lead_id, campaign_id`.
- The importer generates `slug` (slugify business_name + city; de-dupe with -2, -3) and `short_code`.
  It sets `tool_slugs` to both tools for that niche.
- It returns a downloadable CSV with added columns `tool_1_url, tool_2_url, short_url_1, short_url_2`.
  Those go straight into Smartlead custom fields.
- Must handle 2,000 rows in one upload.

**Logo auto-fetch (nice-to-have):** if logo_url is blank, try `https://logo.clearbit.com/{domain}`. On error, use the monogram.

**Admin prospect editor:** form fields for every `tool_prospects` column, with a live iframe preview of each enabled tool beside it.

---

## 5. The standard tool UX shell (every tool uses this component)

`<ToolShell tool prospect>` renders:

1. **Header:**
   - logo or monogram
   - business name (or "FlowOperations Demo")
   - a one-line promise from the tool spec (e.g. "Get a real price range for your fence in 60 seconds")
   - trust row: "★ Free · No signup to see your price · Takes ~60s"
2. **Progress bar + stepper:** one question per screen on mobile, Next and Back buttons, Enter to advance.
   - Each step's answer is kept in URL state (`?s=3`), so the browser Back button works.
   - Answers persist in sessionStorage.
3. **Result screen** (defined per tool):
   - big range or verdict
   - line-item breakdown
   - "What's included / not included"
   - "What changes the price"
4. **Contact capture card** (below the result, never before):
   - Fields: name, mobile, email, address or ZIP, "best time to reach you" (Morning / Afternoon / Evening / Anytime), optional notes, optional photo upload (to Supabase storage, max 5 images, 10MB each).
   - Consent checkbox (required): "I agree {business_name} may contact me by phone, text or email about this request. Consent is not a condition of purchase." Store the exact text and a timestamp.
   - Submit button text comes from the tool spec (e.g. "Send me my exact quote").
5. **Thank-you state:**
   - "{business_name} has your request. Expect a call from {phone} — usually within one business day." Use "today" if the tool's urgency flag is set.
   - Show a summary of their answers and result.
   - Buttons: "Call now" (tel:) and "Add to calendar" (an .ics file for a callback window if they chose one).
6. **Sticky mobile bar:** "Call {business_name}" (tel:) on every screen when a phone exists.

**Events:** log `view`, `start`, each `step`, `result_shown`, `contact_open`, `submit` and `call_click` to `tool_events`, through the edge function `track` (batched, fire-and-forget).

---

## 6. Submission pipeline (edge function `submit-tool`)

Input: `{tool_slug, prospect_slug|null, answers, result, contact, utm, meta_event_id}`

1. Validate with zod. Reject if contact.email AND contact.phone are both missing.
2. Insert into `tool_submissions`.
3. **Email the business (Resend; secret `RESEND_API_KEY`).** This is the step our old system never did; it is non-negotiable.
   - To: owner_email + notify_emails.
   - From: `leads@{our sending domain configured in secret TOOL_FROM_EMAIL}`.
   - Reply-to: the homeowner's email.
   - Subject: `New {tool name} request — {contact.name}, {city or zip}`.
   - HTML body:
     - contact block (click-to-call and mailto)
     - result (range or verdict)
     - every answer as a two-column table
     - photo links
     - urgency flag in red if set
     - footer: "Sent by your FlowOperations tool · reply to this email to reach the homeowner directly".
   - If there is no prospect (generic demo), email `TOOL_FALLBACK_EMAIL` (secret).
4. POST the full submission JSON to the n8n webhook (secret `N8N_TOOL_LEAD_WEBHOOK` = our existing `fo-tool-lead` URL). Store the HTTP status in `n8n_status`. Never block the user on it.
5. **Meta Conversions API** `Lead` event (secrets `META_PIXEL_ID`, `META_CAPI_TOKEN`):
   - `event_id` = the client's `meta_event_id` (dedup with the browser Pixel)
   - `event_source_url`
   - `action_source='website'`
   - user_data: SHA-256 of normalized email, phone (E.164 digits), first name, last name, zip, ct, st and country (`us`); plus client_ip_address, client_user_agent, fbc and fbp (from cookies, passed by the client)
   - custom_data: `{content_name: tool_slug, content_category: niche, value: result midpoint (estimators only), currency:'USD'}`
6. Set `notified_at`. Return `{ok:true, submission_id}`.
7. Retry the email and n8n once on failure. Log errors to `tool_events` with `event='pipeline_error'`.

---

## 7. Meta Pixel (FlowOperations pixel on EVERY tool page)

- Install the standard Meta Pixel base code in `index.html` `<head>`, with the pixel ID from the env var `VITE_META_PIXEL_ID`.
  - Pixel ID: **`1783217289488696`** ("FlowOps" pixel — confirmed by Neal 2026-11-03).
- `fbq('init', PIXEL_ID)` once.
- On every route change: `fbq('track','PageView')`.
- Custom and standard events. The `eventID` must equal `meta_event_id` for the Lead event:
  - On result shown: `fbq('trackCustom','ToolResult',{tool:slug, niche})`.
  - On contact card open: `fbq('track','InitiateCheckout'...)` is NOT appropriate. Use `fbq('trackCustom','ToolContactOpen',{tool:slug})`.
  - On successful submit: `fbq('track','Lead',{content_name:slug, content_category:niche, value, currency:'USD'},{eventID: meta_event_id})`.
  - On a tap-to-call click: `fbq('track','Contact',{content_name:slug})`.
- Generate `meta_event_id` with `crypto.randomUUID()` when the contact card opens. Send the same id to `submit-tool`, which uses it for CAPI dedup.
- Read the `_fbp` and `_fbc` cookies and pass them to `submit-tool`. If `fbclid` is in the URL and `_fbc` is missing, build fbc = `fb.1.{ms}.{fbclid}`.
- Respect `navigator.globalPrivacyControl === true`: skip the Pixel, but still send CAPI without fbp/fbc.

---

## 8. Visual design system

- Background `#F8FAFC`, cards white with `rounded-2xl`, `shadow-sm`, 24px padding.
- Primary = prospect brand_color (default teal `#0F766E`). Success `#16A34A`, warning `#D97706`, danger `#DC2626`.
- Type: Inter. H1 28/34 bold (mobile), 40/48 (desktop). Body 16/24.
- Option pickers are **big tappable cards** (icon + label + optional one-line hint), 2 columns on mobile, 3–4 on desktop. A selected card gets a brand-color border plus a check.
- Numeric inputs: a slider plus an editable number box side by side, with units shown ("ft", "sq ft").
- Result ranges: a large two-tone number, and a horizontal "range bar" showing low–high with a marker at the midpoint.
- Use lucide-react icons.
- Never use stock photos of people. Simple illustrations or icons only.

---

## 9. Regional multipliers seed (applies to all home-service cost tools)

`{"CA":1.30,"NY":1.25,"MA":1.22,"NJ":1.20,"CT":1.20,"WA":1.18,"DC":1.20,"MD":1.12,"VA":1.08,"IL":1.10,"CO":1.08,"MN":1.05,"OR":1.10,"FL":1.00,"AZ":0.98,"NC":0.95,"GA":0.95,"TN":0.93,"TX":0.95,"OH":0.92,"IN":0.92,"KS":0.92,"MI":0.95,"PA":1.03}`

Any state not listed = 1.00.

These are reasonable relative cost-of-construction factors to start from. Every prospect can override them in /admin.

---

## 10. Acceptance checklist (builder must verify before calling a tool done)

1. The generic demo works with no prospect.
2. The personalized route shows the name, logo or monogram, color and phone.
3. A slug that doesn't exist falls back to the demo.
4. The result shows before the contact form.
5. A submit writes the row, sends the email to owner_email (test with your own), posts to n8n (check the status), and fires the Pixel `Lead` plus CAPI with the same event_id. Verify in Meta Events Manager → Test Events.
6. It's usable at 360px width.
7. Lighthouse mobile performance ≥ 85.
8. The CSV import of 3 test rows produces working URLs and short codes.
9. Every money output is a range and carries the disclaimer.

---

> **Pixel:** `1783217289488696` ("FlowOps"), confirmed by Neal on 2026-11-03. Do NOT use the silent `1688114569601600`.
>
> **Hosting:** ONE Lovable project hosts all tools, decided by Neal on 2026-11-03.
>
> The CAPI token is generated in Events Manager → that pixel → Settings → Conversions API.
