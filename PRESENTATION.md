# Zenith-V Launch Decision — student assignment deck

**Deliverable:** `Zenith-V_Launch_Decision_JGaneshKumarReddy_23BDS024.pptx`
9 slides, 16:9 (13.33 x 7.5 in), Calibri so it opens correctly on any Windows / Google Slides /
PowerPoint Online machine. The presenter name **J Ganesh Kumar Reddy · 23BDS024** appears on every
slide (title block on slide 1, running footer on slides 2–9).

`Zenith-V_Preview_All_Slides.png` is a rendered contact sheet of all nine slides.

## Slide map

| # | Slide | Rubric component |
| --- | --- | --- |
| 1 | Title — institution, submitted by/to, lecture coverage | Presentation quality |
| 2 | Market structure: four oligopoly tests, HHI ≈ 1,900, FY25 share chart | Market & demand (25) |
| 3 | Demand: petrol as a complement, demand shift, cross-price elasticity, own-price elasticity | Market & demand (25) |
| 4 | Pricing: penetration at ₹74,999 vs skimming, comparison table, break-even chart | Pricing & game theory (30) |
| 5 | Rivals: payoff matrix (Nash equilibrium) + expected response timeline | Pricing & game theory (30) |
| 6 | Capital budgeting: IRR deduced from NPV, NPV profile, risk vs uncertainty | Capital budgeting (35) |
| 7 | Conclusion: three decisions, five guardrails, what the board approves | All |
| 8 | Appendix A — every assumption and calculation | Capital budgeting (35) |
| 9 | Appendix B — recorded sessions used, rubric map, declaration | Presentation quality |

Speaker notes are attached to all nine slides.

## Lecture links (clickable in the deck)

Every reference to the recorded sessions is a live hyperlink inside the .pptx:

- Slide 1 — the five session numbers **and** the five session names in the "Lecture coverage" strip.
- Slides 2–6 — the `LECTURE LINK · SESSION …` tag in the top-right corner
  (s2 → Session 7, s3 → Session 5, s4 → Session 5, s5 → Session 7, s6 → Session 8);
  slide 7 is a recap so its tag stays plain text.
- Slide 9 — the five raw URLs in Appendix B.

| Session | Title | Link |
| --- | --- | --- |
| 5 | Pricing Strategies | https://youtu.be/T25QYasiVrM |
| 6 | Profit | https://youtu.be/d7Qw3Bu-23E |
| 7 | Game Theory | https://youtu.be/f91JEkm7XZg |
| 8 | Risk | https://youtu.be/LsGQdSKB80o |
| 9 | Capital Budgeting & Fiscal Policy | https://youtu.be/Y_NwyfpzUIo |

Verify with: `python3 -c "from pptx import Presentation; ..."` (20 link runs in total: 10 + 1 + 1 + 1 + 1 + 1 + 5).

## Numbers used

- Cost ₹60,000 → launch ₹74,999 gives ₹14,999 contribution (25% mark-up).
- Skimming alternative ₹1,10,000 → ₹49,999 contribution (83% mark-up).
- NPV +₹50 cr at 15% → PV of inflows ₹250 cr → PI 1.25 → **IRR > 15%** (≈21.3% on level
  ₹49.8 cr cash flows over 10 years, stated as illustrative).
- Break-even recovery of ₹200 cr: 1.33 lakh units at ₹74,999, 0.40 lakh at ₹1,10,000.
- Running cost: 40 litres/month × ₹105 = ₹4,200 vs ≈₹360 of electricity → **₹3,840 a month**,
  about ₹46,000 a year.

## Rebuilding

```bash
python3 scripts/make_charts.py          # charts in assets/
python3 scripts/build_deck.py           # writes the .pptx
python3 scripts/render.py <pptx> <dir>  # approximate PNG previews for layout QA
```

Text uses Calibri (metric-compatible with Carlito, which is what the QA renderer measures with);
symbols that Calibri lacks (⇒ ✓ ✗ ⟺ ★) are avoided, `→` is used instead.

`scripts/deck_lib.py` holds the design system: palette, header/footer, and a text-measuring
engine that flags any text box whose content would overflow (Calibri is measured through the
metric-compatible Carlito font).
