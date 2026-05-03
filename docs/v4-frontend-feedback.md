# v4 Frontend Design Feedback

*2026-05-03 | Collected via Claude Chrome extension review*

---

## Round 1: Full-Page Critique

### Core Diagnosis
The page passes the 3-second "this person is serious" test. The problem isn't that anything is wrong — it's that the dashboard doesn't yet feel like **one instrument**. It feels like five well-designed cards stacked on a page.

### Layout Rhythm & Whitespace
- **Tighten the hero, then exhale.** Pull context strip to 12–16px below KPIs (visual footer). Keep big gap before "Your Position."
- **Vary section width.** Chart goes full-bleed. System health + activity at ~720–800px.

### Panel & Card Treatment
Establish semantic vocabulary where differences mean something:

| Treatment | Style | Use For |
|-----------|-------|---------|
| **Elevated** | White fill, warm two-layer shadow, no border | Hero KPIs, position, chart |
| **Recessed** | `--bg-recessed`, inset shadow | Stat strip, system health, activity bg |
| **Hairline** | Transparent, 1px border-subtle | Scenario cards, selectable items |

Shadow: `0 1px 2px rgba(42,37,32,0.04), 0 12px 24px -8px rgba(168,139,101,0.08)`

### Color
- Reserve gold for single most important number per unit
- Deploy `--neutral` (#6B8DAD) sparingly for timestamps/metadata
- **Ink vs sand for real vs modeled** (superseded by Round 2 — now ink vs cobalt)

### Typography
- ALL-CAPS = top-level metric. Title-case-small = sub-metric.
- `font-feature-settings: "tnum" 1, "ss01" 1` for tabular alignment
- One serif moment (Source Serif 4 / GT Sectra) for section titles

### Cohesion Fixes
1. Thin horizontal rules between sections (academic paper breaks)
2. Left-aligned section meta column (~140–180px) — highest leverage move
3. "Your Position" demoted to recessed (quieter than system status)

### Patterns to Steal
- Bloomberg sticky status bar (32–40px, monospace, always-visible health)
- Observable figure captions (italic serif beneath every chart)
- Model state badge (version + calibration date + MAE)

---

## Round 2: RH Brand Integration + Full Design System

### The Discovery
ResearchHub's page background is `#FAF9F5` — warm off-white nearly identical to our `#FAF7F2`. They're a warm-paper-with-cobalt-blue site, not a cold-blue Coinbase site. Our palette doesn't need tearing down — it needs **cobalt threaded through as the epistemic signal color**.

### The Reconciled Palette

```css
:root {
  /* Surfaces — warm foundation matches RH */
  --bg:           #FAF9F5;
  --bg-elevated:  #FFFFFF;
  --bg-recessed:  #F3EFE6;
  --bg-tint-blue: #EFF4FF;  /* RH's active-state blue tint */

  /* Ink — RH's near-black */
  --ink:          #141413;
  --ink-2:        #3D3A35;
  --ink-3:        #6F6A62;
  --ink-4:        #A39E94;

  /* Borders */
  --border:       #E8E2D6;
  --border-hair:  #EFEAE0;
  --border-blue:  #DCE6FF;  /* for predicted/model regions */

  /* THE epistemic pair */
  --observed:     #141413;  /* on-chain, measured, ink */
  --predicted:    #3971FF;  /* model, projected, RH cobalt */
  --predicted-soft: rgba(57, 113, 255, 0.10);
  --predicted-band: rgba(57, 113, 255, 0.06);

  /* Status — desaturated, scholarly */
  --pos:    #2F7A5A;
  --pos-soft: rgba(47, 122, 90, 0.10);
  --neg:    #B84A3D;
  --neg-soft: rgba(184, 74, 61, 0.10);
  --warn:   #B8893E;

  /* Reserved — single most important number per view */
  --gold:   #B8893E;
}
```

### Why Cobalt Replaces Sand for "Predicted"

1. **Brand alignment** — blue lines register as "ResearchHub" instantly to leadership
2. **Stronger epistemic distinction** — ink vs cobalt is a much louder pair than ink vs warm-sand
3. **Cognitive fit** — we already read blue as "this points elsewhere" (hyperlinks), which is exactly what a forecast does
4. **Frees sandstone** — warm tones do their real job as paper/borders/recessed fills

### Deliverable 1: Panel Vocabulary

```css
.panel { border-radius: 14px; padding: 28px 32px; position: relative; }

/* ELEVATED — primary content */
.panel--elevated {
  background: var(--bg-elevated);
  box-shadow: 0 1px 2px rgba(20,20,19,0.04), 0 12px 28px -10px rgba(168,139,101,0.10);
}

/* RECESSED — supporting context */
.panel--recessed {
  background: var(--bg-recessed);
  box-shadow: inset 0 1px 0 rgba(20,20,19,0.02);
}

/* HAIRLINE — selectable items */
.panel--hairline {
  background: transparent;
  border: 1px solid var(--border-hair);
  transition: border-color 200ms, background 200ms;
}
.panel--hairline:hover { border-color: var(--predicted); background: var(--bg-tint-blue); }
.panel--hairline[aria-selected="true"] {
  border-color: var(--predicted);
  background: var(--bg-tint-blue);
  box-shadow: inset 0 0 0 1px var(--predicted);
}

/* PREDICTED variant — cobalt left rule on any model-output panel */
.panel--predicted { border-left: 2px solid var(--predicted); padding-left: 30px; }
```

**Rule a viewer learns in 3 seconds:** shadow = "look here," recessed = "context," hairline + cobalt-on-hover = "pick one," cobalt left rule = "this is a prediction."

### Deliverable 2: Model-vs-Reality Color Treatment

```css
.chart-observed { stroke: var(--observed); stroke-width: 2px; stroke-linecap: round; fill: none; }
.chart-predicted { stroke: var(--predicted); stroke-width: 1.75px; stroke-dasharray: 1 4; stroke-linecap: round; fill: none; opacity: 0.85; }
.chart-confidence-band { fill: var(--predicted-band); stroke: none; }

.value--predicted { color: var(--predicted); font-variant-numeric: tabular-nums; }
.value--predicted::before { content: "→ "; color: var(--predicted); opacity: 0.6; }
.value--observed { color: var(--observed); font-variant-numeric: tabular-nums; }
```

**Application map:**
- "11.2M RSC" → `--observed` (measured)
- "84% APY" → `--observed` if realized; `--predicted` if forecast
- "→ 1.15x in 3 wks" → cobalt (prediction)
- "was 44% day 1" → ink (it happened)
- Scenario card outcomes → cobalt (predictions)
- Activity feed → ink (observed reality)
- "Model: 12.8M" tooltip → cobalt; "Actual: 11.2M" → ink

**Figure caption pattern:**
```css
.figure-caption {
  font-family: "Source Serif 4", Georgia, serif;
  font-style: italic;
  font-size: 12.5px;
  line-height: 1.55;
  color: var(--ink-3);
  max-width: 60ch;
  margin-top: 14px;
}
```

### Deliverable 3: Section-Meta Pattern

```css
.doc-section {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 56px;
  padding: 56px 0;
  border-top: 1px solid var(--border-hair);
}
.doc-section:first-of-type { border-top: none; }
.doc-section__meta { position: sticky; top: 32px; align-self: start; }

.eyebrow {
  font-family: "JetBrains Mono", ui-monospace, monospace;
  font-size: 11px; letter-spacing: 0.08em;
  color: var(--ink-4); text-transform: uppercase; margin-bottom: 12px;
}
.doc-section__title {
  font-family: "Source Serif 4", Georgia, serif;
  font-size: 22px; font-weight: 500; line-height: 1.2;
  color: var(--ink); letter-spacing: -0.01em; margin-bottom: 8px;
}
.doc-section__desc {
  font-size: 13.5px; line-height: 1.55;
  color: var(--ink-3); margin-bottom: 20px; max-width: 28ch;
}
.doc-section__attrs {
  display: grid; grid-template-columns: auto 1fr;
  gap: 4px 12px; font-size: 11.5px;
  font-family: "JetBrains Mono", ui-monospace, monospace; color: var(--ink-4);
}

@media (max-width: 760px) {
  .doc-section { grid-template-columns: 1fr; gap: 16px; }
  .doc-section__meta { position: static; }
  .doc-section__attrs, .doc-section__desc { display: none; }
}
```

**Audience mapping:**
- Leadership on phone → section title + content only, clean
- Research community on desktop → source citations, model version, MAE everywhere
- Self → diagnostic meta (calibration error, n) without crowding content

### Sticky Status Bar (Livebar)

```css
.livebar {
  position: sticky; top: 0; z-index: 50;
  display: flex; align-items: center; gap: 10px;
  padding: 8px 24px;
  background: rgba(250, 249, 245, 0.85);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-hair);
  font-family: "JetBrains Mono", ui-monospace, monospace;
  font-size: 11.5px; color: var(--ink-3);
}
.livebar__push { flex: 1; }
.livebar__dot { width: 6px; height: 6px; border-radius: 50%; background: var(--pos); box-shadow: 0 0 0 3px var(--pos-soft); }
.livebar__label { color: var(--pos); letter-spacing: 0.06em; }
.livebar__sep { color: var(--ink-4); }
```

### Ink/Sand Epistemic Split — Full Application

The dotted/cobalt vs solid/ink rule, applied everywhere:
- "→ 1.15x in 3 wks" on time-weight → cobalt (prediction)
- "was 44% day 1" → ink (observed)
- Scenario cards → cobalt (all predictions)
- Activity feed → ink (observed reality)
- Sparklines next to KPIs → `--ink-4` (14-day trajectory, observed)

### Sparklines (next step)
Each hero KPI gets a tiny 60×20px sparkline (last 14 days, `--ink-4`). KPI = value, sparkline = trajectory. The Linear/Vercel pattern.

---

## Conceptual Layout Sketch (with vocabulary applied)

```
┌─────────────────────────────────── LIVEBAR ────────────────────────────┐
│  ● LIVE  Block 21,438,221 · synced 2h ago     11.2M · 5.1% · 84% APY  │
└────────────────────────────────────────────────────────────────────────┘

§ 01  POOL HEALTH          │  [elevated] 11.2M  [elevated] 5.1%  [elevated] 84%
      Cumulative deposits,  │  [recessed strip] 220M circ · $0.096 · 26K daily
      participation, yield  │
      SOURCE Base·21438221  │
      UPDATED 2h ago        │

§ 02  YOUR POSITION         │  [recessed] 432K  3.87%  23.1K  1.00x → 1.15x(cobalt)
      Anchor deposit Apr 10 │

§ 03  STRESS SCENARIOS      │  [hairline] Whale  [hairline] Foundation  [hairline] Cascade  [hairline] Growth
      P0 perturbation set   │  hover → cobalt border + blue tint

§ 04  MODEL vs REALITY      │  [elevated + predicted left-rule]
      ABM vs on-chain       │  ink solid = actual, cobalt dotted = forecast
      MODEL v0.4.2·MAE 1.8% │  italic serif figure caption beneath
```

---

## Summary: What Changed from Round 1 → Round 2

**Cobalt replaces sand as the predicted/forecast color.** This single decision:
- (a) ties dashboard to RH brand without looking like a Coinbase clone
- (b) gives stronger epistemic distinction (ink vs cobalt >> ink vs warm-sand)
- (c) frees sandstone to be warm paper everything sits on

**The dashboard becomes:** a ResearchHub-branded scientific working paper that updates in real time. Warm paper, ink prose, cobalt forecasts, italic captions, monospace meta. No other DeFi dashboard occupies this position.

---

## Implementation Priority

1. **Ink/cobalt epistemic split** — apply to every number, line, label
2. **Section-meta pattern** — converts stack → document
3. **Figure captions + model badge** — credibility signals
4. **Panel vocabulary** (elevated/recessed/hairline/predicted)
5. **Sticky livebar**
6. **Hero unit tightening** + context strip attachment
7. **Typography** (label hierarchy, tabular figures, serif moments)
8. **Sparklines** in hero KPIs
9. **Position card** demoted to recessed
