"""Build the Zenith-V assignment deck — light, student-style layout."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from deck_lib import *
from deck_lib import pill_w
from PIL import Image

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(HERE, "assets")
OUT = os.path.join(HERE, "Zenith-V_Launch_Decision_JGaneshKumarReddy_23BDS024.pptx")
TOTAL = 9

def dims(p):
    w, h = Image.open(p).size
    return w / h

def note(s, x, y, w, txt, size=8.8, color=MUTED, line=1.30, italic=False):
    h = measure([{"text": txt, "size": size, "line": line}], w)
    text(s, x, y, w, h, [{"text": txt, "size": size, "color": color, "line": line,
                          "i": italic}], label="note")
    return y + h

# ══════════════════════════════════════════════════════ 1 · TITLE
def s1(prs):
    s = new_slide(prs)
    # top rule + institution line
    rect(s, 0, 0, PAGE_W, 0.10, fill=NAVY, shape=MSO_SHAPE.RECTANGLE)
    text(s, MX, 0.42, 8.0, 0.2,
         [{"runs": [("INDIAN INSTITUTE OF INFORMATION TECHNOLOGY, DHARWAD",
                     {"size": 8.4, "color": NAVY, "weight": 700, "spc": 1.3}),
                    ("     |     MANAGERIAL ECONOMICS", {"size": 8.4, "color": MUTED,
                                                         "weight": 600, "spc": 1.3})],
           "line": 1.0}], label="inst")
    text(s, PAGE_W - MX - 3.0, 0.42, 3.0, 0.2,
         [{"text": "CASE STUDY PRESENTATION   ·   OCTOBER 2026", "size": 7.8, "color": MUTED,
           "weight": 600, "spc": 1.0, "line": 1.0, "align": "r"}], align="r", label="date")

    # hero image card (right)
    iw = 5.12
    ih = iw / dims(f"{A}/hero_card.png")
    picture(s, f"{A}/hero_card.png", PAGE_W - MX - iw, 1.22, w=iw, h=ih)
    text(s, PAGE_W - MX - iw, 1.22 + ih + 0.10, iw, 0.22,
         [{"text": "The Zenith-V — flagship electric scooter of E-Mobility India, Bengaluru",
           "size": 8.6, "color": MUTED, "italic": True, "line": 1.2}], label="imgcap")

    # title block
    text(s, MX, 1.20, 6.55, 0.24,
         [{"text": "PROJECT REPORT", "size": 9.0, "color": BLUE, "weight": 700, "spc": 2.0,
           "line": 1.0}], label="kicker")
    text(s, MX, 1.48, 6.60, 1.30,
         [{"text": "The Zenith-V", "size": 33, "color": NAVY, "weight": 700, "line": 1.08},
          {"text": "Launch Decision", "size": 33, "color": BLUE, "weight": 700, "line": 1.08}],
         label="title")
    text(s, MX, 2.76, 6.10, 0.80,
         [{"text": "Market structure, pricing strategy, game theory and capital budgeting "
                   "for an electric scooter start-up", "size": 12.2, "color": BODY, "line": 1.34}],
         label="subtitle")
    hline(s, MX, 3.72, 6.20, LINE, 0.9)

    # submitted by / to
    text(s, MX, 3.90, 3.0, 0.2,
         [{"text": "SUBMITTED BY", "size": 7.8, "color": MUTED, "weight": 700, "spc": 1.4,
           "line": 1.0}], label="by")
    text(s, MX, 4.12, 3.6, 0.30,
         [{"text": "J Ganesh Kumar Reddy", "size": 14.5, "color": NAVY, "weight": 700,
           "line": 1.12}], label="name")
    text(s, MX, 4.46, 3.6, 0.24,
         [{"text": "Roll No. 23BDS024", "size": 10.4, "color": BLUE, "weight": 700,
           "line": 1.15}], label="roll")

    text(s, MX + 4.05, 3.90, 2.4, 0.2,
         [{"text": "SUBMITTED TO", "size": 7.8, "color": MUTED, "weight": 700, "spc": 1.4,
           "line": 1.0}], label="to")
    text(s, MX + 4.05, 4.12, 2.55, 0.60,
         [{"text": "Dr. K. T. Deepak", "size": 11.4, "color": NAVY, "weight": 700, "line": 1.15},
          {"text": "Associate Dean (Innovation, Entrepreneurship and IDRP)", "size": 8.6,
           "color": BODY, "line": 1.25, "sb": 2}], label="to-name")

    # session strip
    rect(s, MX, 5.46, CW, 0.74, fill=BLUE_L, line=BLUE_M, lw=0.75, radius=0.05)
    text(s, MX + 0.24, 5.56, 1.85, 0.2,
         [{"text": "LECTURE COVERAGE", "size": 7.4, "color": BLUE, "weight": 700, "spc": 1.2,
           "line": 1.0}], label="cov")
    text(s, MX + 0.24, 5.78, CW - 0.48, 0.36,
         [{"runs": [("Session 5 ", {"weight": 700, "color": NAVY}),
                    ("Pricing Strategies", {}), ("   ·   ", {"color": BLUE_M}),
                    ("Session 6 ", {"weight": 700, "color": NAVY}), ("Profit", {}),
                    ("   ·   ", {"color": BLUE_M}),
                    ("Session 7 ", {"weight": 700, "color": NAVY}), ("Game Theory", {}),
                    ("   ·   ", {"color": BLUE_M}),
                    ("Session 8 ", {"weight": 700, "color": NAVY}), ("Risk", {}),
                    ("   ·   ", {"color": BLUE_M}),
                    ("Session 9 ", {"weight": 700, "color": NAVY}),
                    ("Capital Budgeting & Fiscal Policy", {})],
           "size": 9.4, "color": BODY, "line": 1.35}], label="cov2")

    text(s, MX, 6.62, CW, 0.24,
         [{"text": "This deck answers the three tasks in the assignment brief: market and demand "
                   "analysis, pricing and game theory, and capital budgeting.",
           "size": 8.8, "color": MUTED, "line": 1.25}], label="footnote")
    footer(s, 1, TOTAL)
    return s

# ══════════════════════════════════════════════════════ 2 · MARKET STRUCTURE
def s2(prs):
    s = new_slide(prs)
    top = header(s, "1 · Market & demand analysis", "Why this market is an oligopoly",
                 "Four firms sell 86% of India's electric scooters, each sets price by watching "
                 "the others, and entry costs ₹200 crore.",
                 session="Lecture link · Session 7: Game theory")

    x, w = MX, 6.35
    rows = [
        ("Few sellers, high concentration",
         "Ola, TVS, Bajaj and Ather take 86% of FY25 registrations. The HHI works out to about "
         "1,900 — well above the 1,800 mark that signals a highly concentrated market."),
        ("Strategic interdependence",
         "No firm can set a price without guessing rivals' reactions. When Ola cut prices on the "
         "S1 X, TVS and Bajaj responded within weeks through the iQube and Chetak ranges."),
        ("Barriers to entry — and to exit",
         "A ₹200-crore plant, battery-cell contracts, a service network of 4,000+ points and "
         "brand trust. Incumbents can retaliate, and a new entrant cannot walk away easily."),
        ("Price rigidity, non-price competition",
         "List prices sit in a narrow ₹30,000–40,000 band. Rivals compete on range, charging "
         "network, warranty and software instead of open price cuts."),
    ]
    # pre-measure so the block can be centred in the content area
    geo = []
    for head, body in rows:
        hp = [{"text": head, "size": 11.2, "color": NAVY, "weight": 700, "line": 1.18}]
        bp = [{"text": body, "size": 9.6, "color": BODY, "line": 1.30}]
        geo.append((head, body, hp, bp, measure(hp, w - 0.44), measure(bp, w - 0.44)))
    block_h = sum(g[4] + g[5] for g in geo) + 0.34 * (len(geo) - 1)
    y = top + 0.06
    for i, (head, body, hp, bp, hh, bh) in enumerate(geo):
        text(s, x, y + 0.02, 0.34, 0.26,
             [{"text": str(i + 1), "size": 10.2, "color": BLUE, "weight": 700, "line": 1.0}],
             label="num")
        text(s, x + 0.42, y - 0.02, w - 0.42, hh, hp, label=head[:16])
        text(s, x + 0.42, y - 0.02 + hh + 0.04, w - 0.42, bh, bp, label=head[:16] + "b")
        if i < len(geo) - 1:
            hline(s, x, y + hh + bh + 0.17, w - 0.20, LINE, 0.6)
        y += hh + bh + 0.34

    text(s, x, y + 0.06, w, 0.58,
         [{"runs": [("Definition check:  ", {"weight": 700, "color": NAVY}),
                    ("not perfect competition — only four price-makers, and entry is not free. "
                     "Not a monopoly — no single firm can dictate price.", {})],
           "size": 9.2, "color": BODY, "line": 1.30}], label="defn")

    cw = 5.05
    chh = cw / dims(f"{A}/chart_market_share.png")
    cx = PAGE_W - MX - cw
    picture(s, f"{A}/chart_market_share.png", cx, top + 0.10, w=cw, h=chh)
    ny = note(s, cx, top + chh + 0.18, cw,
              "Concentration is the first test of an oligopoly: four firms, not the market, decide "
              "the price. Rivals track each other's prices and volumes week by week.")
    rect(s, cx, ny + 0.12, cw, 0.62, fill=GREY_L, line=LINE, lw=0.6, radius=0.04)
    text(s, cx + 0.16, ny + 0.12, cw - 0.32, 0.62,
         [{"runs": [("So what? ", {"weight": 700, "color": NAVY}),
                    ("Plan for reactions. A price list is a move in a game, not a free choice.",
                     {})], "size": 8.8, "color": BODY, "line": 1.26}], anchor="m", label="sowhat")

    bottom_line(s, [("an oligopoly, and a concentrated one — the decision rule is to predict "
                     "rivals before setting a price.", {"size": 9.0, "color": NAVY})])
    footer(s, 2, TOTAL)
    return s

# ══════════════════════════════════════════════════════ 3 · DEMAND & ELASTICITY
def s3(prs):
    s = new_slide(prs)
    top = header(s, "1 · Market & demand analysis", "How petrol prices move our demand",
                 "Petrol is the complement that makes a scooter run. When petrol gets dearer, the "
                 "petrol option loses its cost advantage and demand for Zenith-V rises.",
                 session="Lecture link · Session 5: Pricing strategies")

    cw = 5.92
    chh = cw / dims(f"{A}/chart_demand_shift.png")
    picture(s, f"{A}/chart_demand_shift.png", MX, top - 0.06, w=cw, h=chh)

    # elasticity strip spans the full width beneath the chart and the cards
    ey = 5.58
    eh = 0.72
    rect(s, MX, ey, CW, eh, fill=GREY_L, line=LINE, lw=0.6, radius=0.04)
    text(s, MX + 0.20, ey, 1.72, eh,
         [{"text": "OWN-PRICE\nELASTICITY", "size": 7.8, "color": BLUE, "weight": 700,
           "spc": 1.1, "line": 1.28}], anchor="m", label="elast")
    vline(s, MX + 2.02, ey + 0.12, eh - 0.24, LINE_D, 0.75)
    text(s, MX + 2.20, ey, CW - 2.40, eh,
         [{"runs": [("With dozens of close substitutes and only ~6% EV penetration, "
                     "|ε| > 1: a 1% price cut raises quantity by more than 1%, so revenue rises. ",
                     {}),
                    ("That is why price is our strongest lever.", {"weight": 700, "color": NAVY})],
           "size": 8.8, "color": BODY, "line": 1.28}], anchor="m", label="elast-b")

    x = PAGE_W - MX - 5.16
    w = 5.16
    y = top - 0.06
    blocks = [
        ("Petrol is a complement", BLUE, BLUE_L,
         [("A petrol scooter cannot run without petrol, so Zenith-V substitutes for the whole "
           "petrol bundle. The link is a cross-price elasticity, ", {}),
          ("Exy > 0", {"weight": 700, "color": NAVY}),
          (": a dearer litre of petrol raises the quantity of EVs demanded.", {})]),
        ("The monthly arithmetic", TEAL, TEAL_L,
         [("60 km a day at 45 km/l = 40 litres a month, about ", {}),
          ("₹4,200", {"weight": 700, "color": NAVY}),
          (" at ₹105 a litre. The same distance on electricity costs about ", {}),
          ("₹360", {"weight": 700, "color": NAVY}), (". That ", {}),
          ("₹3,840 a month, ₹46,000 a year", {"weight": 700}),
          (", is the product we are actually selling.", {})]),
        ("A shift, not a movement along the curve", AMBER, AMBER_L,
         [("Our own price has not changed, so the whole curve shifts right. Petrol price is a "
           "demand shifter; a change in our own price would only move quantity demanded along a "
           "given curve.", {})]),
    ]
    for head, col, bg, runs in blocks:
        hp = [{"text": head, "size": 10.6, "color": NAVY, "weight": 700, "line": 1.2}]
        rr = [(t, dict({"size": 9.2, "color": BODY}, **o)) for t, o in runs]
        bp = [{"runs": rr, "size": 9.2, "color": BODY, "line": 1.30}]
        hh, bh = measure(hp, w - 0.46), measure(bp, w - 0.46)
        ch = hh + bh + 0.36
        rect(s, x, y, w, ch, fill=bg, line=None, radius=0.04)
        rect(s, x, y, 0.045, ch, fill=col, shape=MSO_SHAPE.RECTANGLE)
        text(s, x + 0.22, y + 0.15, w - 0.44, hh, hp, label=head[:14])
        text(s, x + 0.22, y + 0.15 + hh + 0.05, w - 0.44, bh, bp, label=head[:14] + "b")
        y += ch + 0.16

    footer(s, 3, TOTAL)
    return s

# ══════════════════════════════════════════════════════ 4 · PRICING
def s4(prs):
    s = new_slide(prs)
    top = header(s, "2 · Pricing & game theory", "Recommendation: penetration at ₹74,999",
                 "The choice is not margin versus growth. At ₹74,999 we still earn ₹14,999 on "
                 "every scooter, so penetration is a decision for scale — not a loss leader.",
                 session="Lecture link · Session 5: Pricing strategies")

    bh = 0.56
    rect(s, MX, top - 0.04, CW, bh, fill=BLUE_L, line=BLUE_M, lw=0.6, radius=0.04)
    rect(s, MX, top - 0.04, 0.06, bh, fill=BLUE, shape=MSO_SHAPE.RECTANGLE)
    text(s, MX + 0.24, top - 0.04, CW - 0.46, bh,
         [{"runs": [("Set the launch price at ₹74,999 (ex-showroom)", {"weight": 700,
                                                                      "color": NAVY, "size": 12.2}),
                    ("  —  a 25% mark-up over the ₹60,000 unit cost, with a ₹1,05,000 premium trim "
                     "to serve the top of the market.", {"size": 10.6, "color": BODY})],
           "line": 1.26}], anchor="m", label="banner")

    ty = top + 0.68
    col0, colw = 2.02, 2.14
    tw = col0 + colw * 2
    head_h, row_h = 0.36, 0.44
    rect(s, MX, ty, tw, head_h, fill=NAVY, radius=0.0)
    text(s, MX + col0, ty, colw, head_h,
         [{"text": "PENETRATION   ←  RECOMMENDED", "size": 7.8, "color": WHITE, "weight": 700,
           "spc": 0.8, "align": "c", "line": 1.0}], align="c", anchor="m", label="h1")
    text(s, MX + col0 + colw, ty, colw, head_h,
         [{"text": "SKIMMING", "size": 7.8, "color": BLUE_M, "weight": 700, "spc": 0.8,
           "align": "c", "line": 1.0}], align="c", anchor="m", label="h2")

    rows = [
        ("Launch price", "₹74,999", "₹1,10,000"),
        ("Contribution / unit", "₹14,999  (25%)", "₹49,999  (83%)"),
        ("Units to recover ₹200 cr", "1.33 lakh", "0.40 lakh"),
        ("Works best when", "Demand is elastic and rivals are already in place",
         "Demand is inelastic and imitation is slow"),
        ("Main risk", "Thin margin if rivals match the cut", "Invites undercutting within a quarter"),
    ]
    for i, (label, a, b) in enumerate(rows):
        ry = ty + head_h + i * row_h
        rect(s, MX, ry, tw, row_h, fill=WHITE if i % 2 == 0 else GREY_L, line=LINE, lw=0.5)
        rect(s, MX + col0, ry, colw, row_h, fill=BLUE_L, line=LINE, lw=0.5)
        text(s, MX + 0.12, ry, col0 - 0.16, row_h,
             [{"text": label, "size": 8.8, "color": NAVY, "weight": 700, "line": 1.12}],
             anchor="m", label="rl")
        text(s, MX + col0 + 0.10, ry, colw - 0.18, row_h,
             [{"text": a, "size": 8.8, "color": NAVY, "line": 1.14}], anchor="m", label="ra")
        text(s, MX + col0 + colw + 0.10, ry, colw - 0.18, row_h,
             [{"text": b, "size": 8.8, "color": BODY, "line": 1.14}], anchor="m", label="rb")

    ay = ty + head_h + len(rows) * row_h + 0.20
    text(s, MX, ay, tw, 0.2,
         [{"text": "WHY PENETRATION FITS AN OLIGOPOLY", "size": 7.6, "color": BLUE, "weight": 700,
           "spc": 1.1, "line": 1.0}], label="why")
    items = ["Elastic demand: a lower price raises revenue, and volume compounds through the year.",
             "Experience curve: each doubling of output cuts cell costs 15–20%, widening the "
             "margin by year three.",
             "Deterrence: at ₹74,999 there is little room left for a rival to start a price war."]
    bullets(s, MX, ay + 0.24, tw, items, size=8.8, gap=0.055, marker="▪", label="why-item")

    cw = 4.90
    chh = cw / dims(f"{A}/chart_price_tradeoff.png")
    cx = PAGE_W - MX - cw
    picture(s, f"{A}/chart_price_tradeoff.png", cx, ty - 0.06, w=cw, h=chh)
    note(s, cx, ty + chh + 0.02, cw,
         "Skimming recovers the plant in 0.40 lakh units; penetration needs 1.33 lakh. The real "
         "question is which volume the market will let us sell.", size=8.4)

    # KPI strip
    ky, kh = 6.14, 0.62
    kpis = [("₹74,999", "launch price, ex-showroom"),
            ("₹14,999", "contribution per unit  ·  25% mark-up"),
            ("1.33 lakh", "units to recover ₹200 crore"),
            ("₹46,000", "running cost saved per customer, per year")]
    kwid = (CW - 0.36) / 4
    for i, (big, small) in enumerate(kpis):
        kx = MX + i * (kwid + 0.12)
        rect(s, kx, ky, kwid, kh, fill=TEAL_L if i == 1 else GREY_L, line=LINE, lw=0.6, radius=0.05)
        text(s, kx + 0.16, ky + 0.10, kwid - 0.32, 0.26,
             [{"text": big, "size": 13.4, "color": TEAL if i == 1 else NAVY, "weight": 700,
               "line": 1.0}], label="kpi")
        text(s, kx + 0.16, ky + 0.36, kwid - 0.32, 0.20,
             [{"text": small, "size": 7.6, "color": BODY, "line": 1.1}], label="kpi-s")
    footer(s, 4, TOTAL)
    return s

# ══════════════════════════════════════════════════════ 5 · RIVALS
def s5(prs):
    s = new_slide(prs)
    top = header(s, "2 · Pricing & game theory", "How Ola and Ather are likely to react",
                 "Strategic interdependence: a rival's best price depends on ours. Our launch "
                 "changes their payoffs, so their reaction is part of our decision.",
                 session="Lecture link · Session 7: Game theory")

    lw_, cw_, g = 1.56, 1.92, 0.08
    x0 = MX
    y0 = top + 0.26
    c1 = x0 + lw_ + g
    c2 = c1 + cw_ + g
    text(s, x0, top - 0.02, cw_ * 2 + lw_ + g * 2, 0.2,
         [{"text": "PAYOFF MATRIX  ·  (E-Mobility, Ola / Ather), ₹ crore over three years",
           "size": 7.4, "color": MUTED, "weight": 700, "spc": 0.8, "line": 1.0}], label="mt")
    hh = 0.38
    for cx, lab in ((c1, "OLA / ATHER MATCH"), (c2, "OLA / ATHER HOLD")):
        rect(s, cx, y0, cw_, hh, fill=GREY_L, line=LINE, lw=0.6, radius=0.0)
        text(s, cx, y0, cw_, hh, [{"text": lab, "size": 7.3, "color": BODY, "weight": 700,
                                   "spc": 0.7, "line": 1.0, "align": "c"}],
             align="c", anchor="m", label="colh")
    cellh = 1.16
    rows = [("WE PENETRATE", "₹74,999"), ("WE SKIM", "₹1,10,000")]
    cells = [[("(25, 30)", "price war, margins thin", "nash"),
              ("(45, 18)", "we take the volume", "plain")],
             [("(14, 32)", "we lose on both counts", "bad"),
              ("(28, 35)", "tacit truce, but unstable", "plain")]]
    for ri, (rl, rp) in enumerate(rows):
        ry = y0 + hh + g + ri * (cellh + g)
        text(s, x0, ry, lw_ - 0.10, cellh,
             [{"text": rl, "size": 7.8, "color": NAVY, "weight": 700, "line": 1.2},
              {"text": rp, "size": 8.4, "color": BLUE, "weight": 700, "line": 1.2, "sb": 1}],
             anchor="m", label="rowh")
        for ci, (pay, desc, kind) in enumerate(cells[ri]):
            cx = c1 + ci * (cw_ + g)
            if kind == "nash":
                fill, border = BLUE_L, BLUE
            elif kind == "bad":
                fill, border = RED_L, RGBColor(0xE8, 0xC4, 0xC0)
            else:
                fill, border = WHITE, LINE
            rect(s, cx, ry, cw_, cellh, fill=fill, line=border, lw=0.9, radius=0.0)
            text(s, cx, ry + 0.20, cw_, 0.32,
                 [{"text": pay, "size": 15.5, "color": NAVY, "weight": 700, "line": 1.0,
                   "align": "c"}], align="c", label="pay")
            text(s, cx, ry + 0.62, cw_, 0.26,
                 [{"text": desc, "size": 7.3, "color": MUTED, "line": 1.1, "align": "c"}],
                 align="c", label="desc")
            if kind == "nash":
                pw = pill_w("NASH EQUILIBRIUM", 6.2, 700, 0.6, pad=0.12)
                pill(s, cx + (cw_ - pw) / 2, ry + cellh - 0.26, "NASH EQUILIBRIUM",
                     BLUE, WHITE, size=6.2, spc=0.6, h=0.19, pad=0.12)
    gy = y0 + hh + g + 2 * (cellh + g) + 0.06
    text(s, x0, gy, lw_ + cw_ * 2 + g * 2, 0.72,
         [{"text": "Penetration is our dominant strategy and matching is the rivals' best reply, "
                   "so (25, 30) is the Nash equilibrium — even though both firms would prefer the "
                   "(28, 35) truce. That truce is not credible, which is why cartel-like outcomes "
                   "do not survive in this market.",
           "size": 8.0, "color": BODY, "line": 1.30, "i": True}], label="mfoot")

    x = 7.36
    w = PAGE_W - MX - x
    y = top - 0.02
    text(s, x, y, w, 0.2,
         [{"text": "EXPECTED SEQUENCE OF RESPONSES", "size": 7.6, "color": BLUE, "weight": 700,
           "spc": 1.1, "line": 1.0}], label="rt")
    steps = [
        ("Weeks 1–4", "OLA", "Matches on price — cashback and cheaper EMI on the S1 X, "
                             "repositioned around 'lowest running cost'."),
        ("Month 2", "ATHER", "Does not chase ₹75,000. It defends the premium niche with a longer "
                             "battery warranty and software features."),
        ("Months 3–6", "TVS · BAJAJ", "Respond through dealer finance and exchange offers rather "
                                      "than the list price, protecting margin and dealer trust."),
        ("Month 6+", "THE FLOOR", "Industry margin drifts to ₹8,000–10,000 a scooter; volume "
                                  "leadership becomes the only durable prize."),
    ]
    sy = y + 0.26
    for i, (when, who, what) in enumerate(steps):
        text(s, x + 0.20, sy, w - 0.20, 0.15,
             [{"text": when.upper(), "size": 6.9, "color": MUTED, "weight": 700, "spc": 0.8,
               "line": 1.0}], label="when")
        bp = [{"runs": [(who, {"weight": 700, "color": NAVY, "size": 8.8}),
                        ("   " + what, {"size": 8.8, "color": BODY})], "line": 1.30}]
        bh_ = measure(bp, w - 0.22)
        vline(s, x + 0.035, sy + 0.08, bh_ + 0.34, LINE_D, 0.75)
        rect(s, x - 0.012, sy + 0.035, 0.09, 0.09,
             fill=BLUE if i < len(steps) - 1 else TEAL, shape=MSO_SHAPE.OVAL)
        text(s, x + 0.20, sy + 0.17, w - 0.20, bh_, bp, label="step")
        sy += 0.17 + bh_ + 0.22

    cy = max(sy + 0.04, 4.92)
    ch = 6.32 - cy
    rect(s, x, cy, w, ch, fill=TEAL_L, line=RGBColor(0xBF, 0xDD, 0xD7), lw=0.6, radius=0.04)
    text(s, x + 0.20, cy + 0.11, w - 0.40, 0.2,
         [{"text": "OUR COUNTER-MOVES", "size": 7.6, "color": TEAL, "weight": 700, "spc": 1.1,
           "line": 1.0}], label="cm")
    cms = ["Sell total cost of ownership (₹46,000 a year saved), never just the sticker price.",
           "Lock in an 8-year battery warranty and service reach before rivals copy the price.",
           "Play tit-for-tat: match a rival's cut, but never lead a second one."]
    yy = cy + 0.34
    for c in cms:
        p = [{"runs": [("▪  ", {"color": TEAL, "weight": 700, "size": 8.4}),
                       (c, {"size": 8.6, "color": BODY})], "line": 1.28}]
        h = measure(p, w - 0.42)
        text(s, x + 0.20, yy, w - 0.40, h, p, label="cm-i")
        yy += h + 0.085

    bottom_line(s, [("expect a matching response within weeks — so plan for a lower industry "
                     "margin, and win on cost and service instead.", {"size": 9.0, "color": NAVY})])
    footer(s, 5, TOTAL)
    return s

# ══════════════════════════════════════════════════════ 6 · CAPITAL BUDGETING
def s6(prs):
    s = new_slide(prs)
    top = header(s, "3 · Capital budgeting", "A ₹50 crore NPV means the IRR is above 15%",
                 "If the project is worth ₹50 crore more than it costs at a 15% discount rate, "
                 "its own rate of return must be higher than 15%.",
                 session="Lecture link · Sessions 8 & 9: Risk · Capital budgeting")

    x, w = MX, 6.25
    steps = [
        ("1", "Start from the NPV identity",
         [("NPV = PV of inflows − ₹200 crore = +₹50 crore, so the PV of inflows is ₹250 crore. "
           "The profitability index is 250 ÷ 200 = ", {}), ("1.25", {"weight": 700, "color": NAVY}),
          (" — every rupee invested comes back as ₹1.25 in present value.", {})]),
        ("2", "NPV always falls as the discount rate rises",
         [("Discounting the same cash flows at a higher rate can only shrink their value. At 15% "
           "NPV is still +₹50 crore, so it reaches zero only at a rate ", {}),
          ("above", {"weight": 700, "color": NAVY}), (" 15%.", {})]),
        ("3", "That crossing point is the IRR",
         [("The IRR is the rate at which NPV = 0, so ", {}),
          ("IRR > 15%", {"weight": 700, "color": TEAL}),
          (" by construction. On level cash flows of about ₹49.8 crore a year for ten years, the "
           "IRR is ", {}), ("≈ 21.3%", {"weight": 700, "color": TEAL}),
          (" — a cushion of about 6 percentage points.", {})]),
    ]
    y = top - 0.04
    for num, head, runs in steps:
        hp = [{"text": head, "size": 10.6, "color": NAVY, "weight": 700, "line": 1.2}]
        bp = [{"runs": [(t, dict({"size": 9.2, "color": BODY}, **o)) for t, o in runs],
               "line": 1.30}]
        hh, bh = measure(hp, w - 0.44), measure(bp, w - 0.44)
        text(s, x, y + 0.01, 0.30, 0.22,
             [{"text": num, "size": 9.6, "color": BLUE, "weight": 700, "line": 1.0}], label="n")
        text(s, x + 0.32, y - 0.04, w - 0.32, hh, hp, label=head[:16])
        text(s, x + 0.32, y - 0.04 + hh + 0.03, w - 0.32, bh, bp, label=head[:16] + "b")
        y += hh + bh + 0.20

    ry = y + 0.06
    ratios = [("NPV @ 15%", "+₹50 cr"), ("Profitability index", "1.25"),
              ("IRR", "≈ 21.3%"), ("Decision", "Accept")]
    rw = w / 4
    rect(s, x, ry, w, 0.62, fill=BLUE_L, line=BLUE_M, lw=0.6, radius=0.04)
    for i, (k, v) in enumerate(ratios):
        rx = x + i * rw
        if i:
            vline(s, rx, ry + 0.12, 0.38, BLUE_M, 0.75)
        text(s, rx + 0.12, ry + 0.09, rw - 0.20, 0.18,
             [{"text": k.upper(), "size": 6.6, "color": MUTED, "weight": 700, "spc": 0.6,
               "line": 1.0}], label="rk")
        text(s, rx + 0.12, ry + 0.29, rw - 0.20, 0.24,
             [{"text": v, "size": 11.0, "color": TEAL if i == 3 else NAVY, "weight": 700,
               "line": 1.0}], label="rv")

    cw = 5.15
    chh = cw / dims(f"{A}/chart_npv_profile.png")
    cx = PAGE_W - MX - cw
    picture(s, f"{A}/chart_npv_profile.png", cx, top - 0.06, w=cw, h=chh)
    note(s, cx, top + chh + 0.04, cw,
         "The curve crosses zero exactly at the IRR. Any discount rate below 21.3% — including "
         "our 15% hurdle — leaves a positive NPV.", size=8.5)

    hy = 4.88
    text(s, MX, hy, CW, 0.2,
         [{"text": "IS THE PLANT DECISION MADE UNDER RISK OR UNDER UNCERTAINTY?",
           "size": 8.0, "color": BLUE, "weight": 700, "spc": 1.1, "line": 1.0}], label="ru")
    cards = [
        ("RISK", "outcomes known · probabilities can be estimated", AMBER, AMBER_L,
         "Cell and commodity prices · rupee–dollar rate · interest on the ₹200 crore debt · "
         "warranty claims · dealer ramp-up. Modelled with sensitivity and scenario analysis."),
        ("UNCERTAINTY", "outcomes unknown · no probability can be assigned", RED, RED_L,
         "A solid-state battery breakthrough · a redesign of the PM E-DRIVE subsidy · "
         "consolidation among rivals · a lithium supply shock · a lasting change in buyer taste. "
         "Met with staged capex and written exit rules."),
    ]
    cy = hy + 0.24
    cwid = (CW - 0.26) / 2
    chgt = 1.08
    for i, (tag, sub, col, bg, txt) in enumerate(cards):
        cx2 = MX + i * (cwid + 0.26)
        rect(s, cx2, cy, cwid, chgt, fill=bg, line=None, radius=0.04)
        rect(s, cx2, cy, 0.045, chgt, fill=col, shape=MSO_SHAPE.RECTANGLE)
        text(s, cx2 + 0.20, cy + 0.11, cwid - 0.38, 0.20,
             [{"runs": [(tag, {"size": 8.8, "color": col, "weight": 700, "spc": 1.1}),
                        ("     " + sub, {"size": 7.6, "color": MUTED, "weight": 500})],
               "line": 1.1}], label="rtag")
        text(s, cx2 + 0.20, cy + 0.36, cwid - 0.40, chgt - 0.44,
             [{"text": txt, "size": 8.6, "color": BODY, "line": 1.28}], label="rbody")

    bottom_line(s, [("mainly uncertainty — the ₹50 crore NPV is a point estimate inside a "
                     "distribution, not a promise.", {"size": 9.0, "color": NAVY})],
                y=6.22, label="VERDICT")
    footer(s, 6, TOTAL)
    return s

# ══════════════════════════════════════════════════════ 7 · CONCLUSION
def s7(prs):
    s = new_slide(prs)
    top = header(s, "4 · Conclusion", "Proceed — with a staged commitment",
                 "All three analyses point the same way. The one refinement is to release capital "
                 "in stages, because the plant is a bet under uncertainty.",
                 session="Lecture link · Sessions 5–9")

    cards = [
        ("MARKET", "Oligopoly", "86% held by four firms. Enter as a differentiated, scale-led "
                                "challenger — never as a price-taker.", BLUE),
        ("PRICE", "₹74,999", "Penetration pricing. Elastic demand, a positive contribution on "
                             "every unit, and a response we can anticipate.", TEAL),
        ("CAPITAL", "Accept", "IRR ≈ 21.3% against a 15% hurdle. Approve the plant — but stage "
                              "the ₹200 crore against demand gates.", AMBER),
    ]
    cy, ch = top - 0.04, 1.26
    cwid = (CW - 0.36) / 3
    for i, (tag, big, body, col) in enumerate(cards):
        cx = MX + i * (cwid + 0.18)
        rect(s, cx, cy, cwid, ch, fill=GREY_L, line=LINE, lw=0.6, radius=0.04)
        rect(s, cx, cy, cwid, 0.05, fill=col, shape=MSO_SHAPE.RECTANGLE)
        text(s, cx + 0.22, cy + 0.17, cwid - 0.44, 0.2,
             [{"text": tag, "size": 7.4, "color": col, "weight": 700, "spc": 1.2, "line": 1.0}],
             label="ctag")
        text(s, cx + 0.22, cy + 0.36, cwid - 0.44, 0.28,
             [{"text": big, "size": 15.2, "color": NAVY, "weight": 700, "line": 1.02}],
             label="cbig")
        text(s, cx + 0.22, cy + 0.70, cwid - 0.44, 0.50,
             [{"text": body, "size": 8.6, "color": BODY, "line": 1.26}], label="cbody")

    x, w = MX, 6.62
    py = cy + ch + 0.24
    ph = 6.30 - py
    rect(s, x, py, w, ph, fill=WHITE, line=LINE, lw=0.75, radius=0.04)
    text(s, x + 0.24, py + 0.14, w - 0.48, 0.2,
         [{"text": "CONDITIONS AND GUARDRAILS", "size": 7.8, "color": BLUE, "weight": 700,
           "spc": 1.1, "line": 1.0}], label="gt")
    guards = [
        ("Release capital in three gates", "land and line (₹60 cr) → cell contracts (₹70 cr) → "
                                           "expansion (₹70 cr), each unlocked by measured demand."),
        ("Write the exit rules now", "walk away if the run-rate stays below 6,000 scooters a month "
                                     "for two consecutive quarters."),
        ("Target about 8% share by FY28", "roughly 1.6 lakh units a year, enough to recover the "
                                          "₹200 crore inside the payback window."),
        ("Hold ₹74,999 for four quarters", "a second cut invites a price war that no firm in an "
                                           "oligopoly can win."),
        ("Recover R&D through the premium trim", "the ₹1,05,000 variant, not the base price, "
                                                 "carries the fixed-cost recovery."),
    ]
    # measure first so the list sits optically centred in the panel
    _hs = []
    for head, body in guards:
        _p = [{"runs": [(head + " — ", {"size": 8.9, "color": NAVY, "weight": 700}),
                        (body, {"size": 8.9, "color": BODY})], "line": 1.30}]
        _hs.append(measure(_p, w - 0.62))
    yy = py + 0.40 + max((ph - 0.40 - sum(_hs) - 0.17 * (len(guards) - 1)) / 2, 0)
    for i, (head, body) in enumerate(guards):
        text(s, x + 0.24, yy + 0.005, 0.26, 0.20,
             [{"text": str(i + 1), "size": 8.6, "color": BLUE, "weight": 700, "line": 1.0}],
             label="gnum")
        p = [{"runs": [(head + " — ", {"size": 8.9, "color": NAVY, "weight": 700}),
                       (body, {"size": 8.9, "color": BODY})], "line": 1.30}]
        h = _hs[i]
        text(s, x + 0.56, yy - 0.01, w - 0.56, h, p, label="guard")
        yy += h + 0.17

    bx = 7.74
    bw = PAGE_W - MX - bx
    qh = 1.30
    rect(s, bx, py, bw, qh, fill=NAVY, radius=0.04)
    rect(s, bx + 0.32, py + 0.24, 0.04, 0.62, fill=TEAL, shape=MSO_SHAPE.RECTANGLE)
    text(s, bx + 0.52, py + 0.20, bw - 0.80, 0.72,
         [{"text": "\u201cPricing low is not a discount strategy. It is a way of buying scale, "
                   "learning and a cost advantage before rivals can react.\u201d",
           "size": 10.4, "color": WHITE, "weight": 700, "line": 1.30, "i": True}], label="quote")
    hline(s, bx + 0.52, py + qh - 0.40, bw - 0.80, RGBColor(0x2E, 0x42, 0x5C), 0.75)
    text(s, bx + 0.52, py + qh - 0.30, bw - 0.80, 0.22,
         [{"text": "Build the plant. Price to own the market. Stage the risk.",
           "size": 9.4, "color": RGBColor(0x8F, 0xD8, 0xCB), "weight": 700, "line": 1.2}],
         label="close")

    ny = py + qh + 0.26
    rect(s, bx, ny, bw, 6.30 - ny, fill=WHITE, line=LINE, lw=0.75, radius=0.04)
    text(s, bx + 0.24, ny + 0.14, bw - 0.48, 0.2,
         [{"text": "WHAT WE ASK THE BOARD TO APPROVE", "size": 7.6, "color": BLUE, "weight": 700,
           "spc": 1.1, "line": 1.0}], label="ask")
    asks = ["₹60 crore now for land and the first assembly line in Chennai.",
            "A launch price of ₹74,999, reviewed after four quarters — not before.",
            "₹70 crore each for cell contracts and expansion, released only on demand evidence.",
            "A formal review at the close of FY27, with the three gates as the test."]
    yy2 = ny + 0.42
    for a in asks:
        p = [{"runs": [("▪  ", {"color": TEAL, "weight": 700, "size": 8.2}),
                       (a, {"size": 8.6, "color": BODY})], "line": 1.28}]
        h = measure(p, bw - 0.60)
        text(s, bx + 0.24, yy2, bw - 0.48, h, p, label="ask-i")
        yy2 += h + 0.09

    bottom_line(s, [("build in Chennai, launch at ₹74,999, and let measured demand release the "
                     "rest of the capital.", {"size": 9.0, "color": NAVY})],
                y=6.42, label="FINAL ANSWER")
    footer(s, 7, TOTAL)
    return s

# ══════════════════════════════════════════════════════ 8 · APPENDIX
def s8(prs):
    s = new_slide(prs)
    top = header(s, "Appendix A", "Assumptions and calculations",
                 "Every number in the deck can be re-checked from these inputs, so the argument "
                 "can be re-run with different assumptions.")

    rows = [
        ("Unit manufacturing cost", "₹60,000 per scooter", "Brief"),
        ("Recommended launch price", "₹74,999 — contribution ₹14,999 (25% mark-up)", "Analysis"),
        ("Skimming alternative", "₹1,10,000 — contribution ₹49,999 (83% mark-up)", "Analysis"),
        ("Plant investment", "₹200 crore, Chennai", "Brief"),
        ("Discount rate / hurdle rate", "15%", "Brief"),
        ("NPV at 15%", "+₹50 crore → PV of inflows ₹250 crore, profitability index 1.25", "Derived"),
        ("Implied IRR", "≈ 21.3% on level cash flows of ₹49.8 crore for 10 years",
         "Derived, illustrative"),
        ("Units needed to recover ₹200 crore", "1.33 lakh at ₹74,999  ·  0.40 lakh at ₹1,10,000",
         "Derived"),
        ("Petrol scooter running cost", "60 km/day ÷ 45 km/l × 30 days = 40 litres × ₹105 = ₹4,200",
         "Analysis"),
        ("Electric scooter running cost", "60 km/day × 0.025 kWh/km × 30 days × ₹8/kWh ≈ ₹360",
         "Analysis"),
        ("Market shares, FY25", "Ola 30.0 · TVS 21.4 · Bajaj 20.0 · Ather 11.6 · Hero 5.0",
         "VAHAN, industry"),
        ("Concentration measure", "HHI ≈ 1,900 · top-5 share 86%", "Derived"),
    ]
    x, w = MX, CW
    y = top
    rowh = 0.352
    text(s, x + 0.14, y, 4.4, 0.2, [{"text": "INPUT", "size": 7.4, "color": MUTED, "weight": 700,
                                     "spc": 1.1, "line": 1.0}], label="h1")
    text(s, x + 5.10, y, 4.9, 0.2, [{"text": "VALUE", "size": 7.4, "color": MUTED, "weight": 700,
                                     "spc": 1.1, "line": 1.0}], label="h2")
    text(s, x + 10.20, y, 1.6, 0.2, [{"text": "SOURCE", "size": 7.4, "color": MUTED, "weight": 700,
                                      "spc": 1.1, "line": 1.0}], label="h3")
    y += 0.24
    hline(s, x, y - 0.04, w, LINE_D, 0.9)
    for i, (k, v, src) in enumerate(rows):
        if i % 2 == 0:
            rect(s, x, y - 0.005, w, rowh - 0.015, fill=GREY_L, radius=0.0)
        text(s, x + 0.14, y + 0.04, 4.75, rowh - 0.08,
             [{"text": k, "size": 8.6, "color": NAVY, "weight": 700, "line": 1.1}], label="k")
        text(s, x + 5.10, y + 0.04, 5.00, rowh - 0.08,
             [{"text": v, "size": 8.6, "color": BODY, "line": 1.1}], label="v")
        text(s, x + 10.20, y + 0.04, 1.6, rowh - 0.08,
             [{"text": src, "size": 7.8, "color": MUTED, "line": 1.1}], label="s")
        y += rowh
    footer(s, 8, TOTAL)
    return s

# ══════════════════════════════════════════════════════ 9 · REFERENCES
def s9(prs):
    s = new_slide(prs)
    top = header(s, "Appendix B", "Lecture sessions used and rubric map",
                 "The concepts in this deck come from the recorded sessions listed below. Each "
                 "slide is tagged with the session it draws on.")

    x, w = MX, 6.30
    text(s, x, top - 0.02, w, 0.2,
         [{"text": "RECORDED SESSIONS REFERENCED", "size": 7.8, "color": BLUE, "weight": 700,
           "spc": 1.1, "line": 1.0}], label="rt")
    sessions = [
        ("Session 5", "Pricing Strategies", "Penetration vs skimming, mark-up pricing, elasticity "
                                            "and price setting", "https://youtu.be/T25QYasiVrM"),
        ("Session 6", "Profit", "Contribution margin, break-even volume and economic profit",
         "https://youtu.be/d7Qw3Bu-23E"),
        ("Session 7", "Game Theory", "Payoff matrix, dominant strategy, Nash equilibrium, "
                                     "tit-for-tat", "https://youtu.be/f91JEkm7XZg"),
        ("Session 8", "Risk", "Knight's risk vs uncertainty, sensitivity and scenario analysis",
         "https://youtu.be/LsGQdSKB80o"),
        ("Session 9", "Capital Budgeting & Fiscal Policy", "NPV, IRR, profitability index, "
                                                          "discount rate, subsidy policy",
         "https://youtu.be/Y_NwyfpzUIo"),
    ]
    y = top + 0.24
    for tag, name, desc, link in sessions:
        text(s, x, y, 0.95, 0.2,
             [{"text": tag, "size": 8.0, "color": BLUE, "weight": 700, "line": 1.0}], label="stag")
        text(s, x + 1.02, y - 0.03, w - 1.02, 0.22,
             [{"text": name, "size": 9.6, "color": NAVY, "weight": 700, "line": 1.1}],
             label="sname")
        text(s, x + 1.02, y + 0.19, w - 1.02, 0.20,
             [{"text": desc, "size": 8.2, "color": MUTED, "line": 1.2}], label="sdesc")
        hlink = text(s, x + 1.02, y + 0.38, w - 1.02, 0.18,
                     [{"text": link, "size": 7.8, "color": BLUE, "line": 1.0}], label="slink")
        try:
            hlink.text_frame.paragraphs[0].runs[0].hyperlink.address = link
        except Exception:
            pass
        y += 0.72
        hline(s, x, y - 0.14, w, LINE, 0.6)

    # rubric map
    rx = 7.72
    rw = PAGE_W - MX - rx
    text(s, rx, top - 0.02, rw, 0.2,
         [{"text": "HOW THIS DECK MAPS TO THE RUBRIC", "size": 7.8, "color": BLUE, "weight": 700,
           "spc": 1.1, "line": 1.0}], label="rrt")
    tbl = [("Market & demand analysis", "25", "Slides 2–3"),
           ("Pricing & game theory", "30", "Slides 4–5"),
           ("Capital budgeting", "35", "Slide 6 (+ A)"),
           ("Presentation quality", "10", "All slides"),
           ("Total", "100", "")]
    ty = top + 0.24
    hh, rh = 0.32, 0.40
    rect(s, rx, ty, rw, hh, fill=NAVY, radius=0.0)
    for cx, cwid, lab, al in ((rx + 0.12, rw - 1.30, "COMPONENT", "l"),
                              (rx + rw - 1.12, 0.46, "MARKS", "c"),
                              (rx + rw - 0.62, 0.52, "SLIDE", "c")):
        text(s, cx, ty, cwid, hh, [{"text": lab, "size": 7.0, "color": WHITE, "weight": 700,
                                     "spc": 0.8, "line": 1.0, "align": al}],
             align=al, anchor="m", label="th")
    for i, (comp, marks, where) in enumerate(tbl):
        ry = ty + hh + i * rh
        last = i == len(tbl) - 1
        rect(s, rx, ry, rw, rh, fill=GREY_L if (i % 2 == 0 and not last) else WHITE,
             line=LINE, lw=0.5)
        text(s, rx + 0.12, ry, rw - 1.30, rh,
             [{"text": comp, "size": 8.4, "color": NAVY, "weight": 700 if last else 400,
               "line": 1.1}], anchor="m", label="tc")
        text(s, rx + rw - 1.12, ry, 0.46, rh,
             [{"text": marks, "size": 8.8, "color": NAVY, "weight": 700, "line": 1.0,
               "align": "c"}], align="c", anchor="m", label="tm")
        text(s, rx + rw - 0.62, ry, 0.52, rh,
             [{"text": where, "size": 7.4, "color": MUTED, "line": 1.0, "align": "c"}],
             align="c", anchor="m", label="tw")

    ny = ty + hh + len(tbl) * rh + 0.18
    rect(s, rx, ny, rw, 1.05, fill=GREY_L, line=LINE, lw=0.6, radius=0.04)
    text(s, rx + 0.20, ny + 0.14, rw - 0.40, 0.78,
         [{"text": "NOTE ON THE DATA", "size": 7.2, "color": BLUE, "weight": 700, "spc": 1.0,
           "line": 1.0},
          {"text": "Market shares are FY25 VAHAN-based industry estimates, used to establish the "
                   "market structure — not to forecast our own volumes. The IRR is illustrative, "
                   "since the brief supplies only the NPV at 15%.",
           "size": 8.4, "color": BODY, "line": 1.28, "sb": 4}], label="datanote")

    dy = 5.62
    rect(s, x, dy, w, 0.86, fill=BLUE_L, line=BLUE_M, lw=0.6, radius=0.04)
    rect(s, x, dy, 0.05, 0.86, fill=BLUE, shape=MSO_SHAPE.RECTANGLE)
    text(s, x + 0.22, dy + 0.12, w - 0.44, 0.62,
         [{"text": "DECLARATION", "size": 7.2, "color": BLUE, "weight": 700, "spc": 1.0,
           "line": 1.0},
          {"text": "This assignment is my own work, prepared from the recorded sessions and the "
                   "case brief, and is submitted on or before the deadline set in Google "
                   "Classroom.", "size": 8.4, "color": BODY, "line": 1.26, "sb": 4}],
         label="decl")
    footer(s, 9, TOTAL)
    return s

NOTES = {
1: ("Good morning. This is my case-study presentation on the Zenith-V, the electric scooter "
    "that E-Mobility India plans to launch. The brief asks three questions: what kind of market "
    "we are entering, what we should charge, and whether the Chennai plant is worth ₹200 crore. "
    "I have drawn the concepts from Sessions 5 to 9 of the Managerial Economics course."),
2: ("An oligopoly has four recognisable features and this market shows all four. First, few "
    "sellers: Ola, TVS, Bajaj and Ather take 86% of FY25 registrations, giving an HHI of about "
    "1,900. Second, strategic interdependence — every price decision is taken after predicting "
    "rivals' reactions. Third, barriers to entry: ₹200 crore of plant and thousands of service "
    "points. Fourth, price rigidity, with competition shifting to range, warranty and software."),
3: ("Petrol is a complement to a petrol scooter, so when it becomes expensive the total cost of "
    "the petrol option rises and demand for the electric substitute rises. That is cross-price "
    "elasticity, and it is positive. Our own price has not changed, so this is a rightward shift "
    "of the demand curve, not movement along it. In money terms the customer saves about ₹3,840 "
    "a month, roughly ₹46,000 a year."),
4: ("The brief frames this as market share versus recovering R&D, but at ₹74,999 we still make "
    "₹14,999 a scooter, a 25% mark-up — so penetration is not loss-leading. Demand is elastic, so "
    "price moves revenue; and the experience curve means today's volume lowers tomorrow's cost. "
    "Skimming only works when demand is inelastic and imitation is slow, and neither holds with "
    "four rivals sitting on idle capacity."),
5: ("This slide is the core of strategic interdependence. Penetration is our dominant strategy, "
    "and matching is the rivals' best reply, so the outcome is the Nash equilibrium (25, 30), "
    "even though both firms would prefer the (28, 35) truce. That truce is not credible. Ola will "
    "match first; Ather will defend its premium niche rather than chase us down; TVS and Bajaj "
    "will respond through finance and exchange offers."),
6: ("The NPV result does most of the work. At 15% the project is worth ₹50 crore more than it "
    "costs, so the present value of inflows is ₹250 crore and the profitability index is 1.25. "
    "Because NPV falls as the discount rate rises, a positive NPV at 15% proves that the IRR is "
    "above 15%; on level cash flows of ₹49.8 crore for ten years it is about 21.3%. On risk: many "
    "inputs are measurable risks, but the big ones — a battery breakthrough or a subsidy redesign "
    "— are genuine uncertainty, which is the argument for staging the investment."),
7: ("So the recommendation has three parts. Enter as a differentiated, scale-led challenger in an "
    "oligopoly. Launch at ₹74,999 with a premium trim above it. Accept the project, since IRR of "
    "roughly 21.3% clears the 15% hurdle, but release the ₹200 crore in three gates with written "
    "exit rules."),
8: ("Appendix A lists every input and every derived figure so the analysis can be re-run. The IRR "
    "is illustrative: the brief gives only the NPV at 15%, so I assumed level cash flows to show "
    "what an IRR of about 21% implies."),
9: ("Appendix B records the recorded sessions I used and maps the deck to the marking rubric, so "
    "each component — market analysis, pricing and game theory, and capital budgeting — can be "
    "traced to specific slides."),
}

def main():
    prs = Presentation()
    prs.slide_width = I(PAGE_W)
    prs.slide_height = I(PAGE_H)
    for fn in (s1, s2, s3, s4, s5, s6, s7, s8, s9):
        print("·", fn.__name__)
        fn(prs)
    for i, sl in enumerate(prs.slides, 1):
        if i in NOTES:
            sl.notes_slide.notes_text_frame.text = NOTES[i]
    prs.core_properties.title = "The Zenith-V Launch Decision"
    prs.core_properties.author = "J Ganesh Kumar Reddy (23BDS024)"
    prs.core_properties.subject = "Managerial Economics case study — IIIT Dharwad"
    prs.save(OUT)
    print("saved", os.path.basename(OUT), os.path.getsize(OUT) // 1024, "KB")

if __name__ == "__main__":
    main()
