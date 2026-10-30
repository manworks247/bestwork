#!/usr/bin/env python3
"""
Generates 5 clean, student-friendly Managerial Economics charts (300 DPI)
aligned with IIIT Dharwad Recorded Sessions 1-9 (Dr. K. T. Deepak) for:
The "Zenith-V" EV Scooter Launch — J GANESH KUMAR REDDY 23BDS024
"""
import os
import numpy as np
import matplotlib.pyplot as plt

os.makedirs("assets/charts", exist_ok=True)

plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
plt.rcParams["axes.edgecolor"] = "#94A3B8"
plt.rcParams["axes.linewidth"] = 1.0

NAVY = "#1B365D"
SLATE = "#334155"
BLUE = "#2563EB"
TEAL = "#0284C7"
EMERALD = "#059669"
AMBER = "#D97706"
CORAL = "#E11D48"
PURPLE = "#4F46E5"
BG_WHITE = "#FFFFFF"


def make_chart1_oligopoly():
    """Slide 2: Indian EV 2W Market Share Concentration (CR4 = 83% Oligopoly DNA - Session 4)."""
    fig, ax = plt.subplots(figsize=(6.0, 2.95), dpi=300)
    fig.patch.set_facecolor(BG_WHITE)
    ax.set_facecolor(BG_WHITE)

    firms = [
        "Others / Startups\n(Zenith-V Entry)",
        "Hero MotoCorp (Vida)",
        "Ather Energy",
        "Bajaj Auto (Chetak)",
        "TVS Motor (iQube)",
        "Ola Electric",
    ]
    shares = [11, 6, 12, 16, 21, 34]
    colors = [EMERALD, "#64748B", TEAL, PURPLE, BLUE, NAVY]

    bars = ax.barh(firms, shares, color=colors, height=0.56, edgecolor="none")

    for bar, s in zip(bars, shares):
        ax.text(
            bar.get_width() + 0.8,
            bar.get_y() + bar.get_height() / 2,
            f"{s}%",
            va="center",
            ha="left",
            fontsize=9.2,
            fontweight="bold",
            color=NAVY,
        )

    ax.axhspan(1.6, 5.45, color="#EFF6FF", alpha=0.65, zorder=0)
    ax.text(
        21.5,
        0.72,
        "CR4 = 83% (Top 4 Players)\nSession 4 Market DNA:\n• Few Dominant Sellers\n• High ₹200 Cr Entry Barrier",
        fontsize=7.8,
        fontweight="bold",
        color="#1E3A8A",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="#DBEAFE", edgecolor="#60A5FA", lw=1.2),
    )

    ax.set_xlim(0, 44)
    ax.set_xlabel("Market Share in Indian EV Scooter Market (%)", fontsize=8.8, fontweight="bold", color=NAVY)
    ax.set_title("Indian EV Scooter Oligopoly: Top 4 Control 83% Share", fontsize=9.6, fontweight="bold", color=NAVY, pad=7)
    ax.grid(axis="x", linestyle="--", alpha=0.35, color="#94A3B8")
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="both", labelsize=8.3, colors=SLATE)

    plt.tight_layout()
    plt.savefig("assets/charts/chart1_oligopoly.png", dpi=300)
    plt.close()


def make_chart2_cross_elasticity():
    """Slide 3: Rightward Demand Shift (D1 -> D2) & Running Cost Comparison (Session 2)."""
    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(6.0, 2.95), dpi=300, gridspec_kw={"width_ratios": [1.35, 1.0]}
    )
    fig.patch.set_facecolor(BG_WHITE)

    ax1.set_facecolor(BG_WHITE)
    q = np.linspace(15, 85, 100)
    p_d1 = 125 - 0.85 * q
    p_d2 = 148 - 0.85 * q

    ax1.plot(q, p_d1, color=BLUE, lw=2.5, label=r"$D_1$ (Petrol @ ₹95/L)")
    ax1.plot(q, p_d2, color=EMERALD, lw=2.8, label=r"$D_2$ (Petrol $\uparrow$ ₹108/L)")

    ax1.axhline(80, color="#64748B", linestyle=":", lw=1.2)
    q1_80 = (125 - 80) / 0.85
    q2_80 = (148 - 80) / 0.85
    ax1.scatter([q1_80, q2_80], [80, 80], color=NAVY, s=36, zorder=5)
    ax1.annotate(
        "",
        xy=(q2_80 - 1.5, 80),
        xytext=(q1_80 + 1.5, 80),
        arrowprops=dict(arrowstyle="->", color=CORAL, lw=2.2),
    )
    ax1.annotate(
        "Rightward Shift\n(D1 → D2)",
        xy=((q1_80 + q2_80) / 2, 79.0),
        xytext=(24.0, 56.0),
        arrowprops=dict(arrowstyle="->", color=CORAL, lw=1.4),
        ha="center",
        va="bottom",
        fontsize=7.3,
        fontweight="bold",
        color=CORAL,
        bbox=dict(boxstyle="round,pad=0.24", facecolor="#FFF1F2", edgecolor=CORAL, lw=1.0),
    )

    ax1.set_title("A. Demand Shift When Petrol Rises\n(Exy > 0 for Substitutes)", fontsize=8.4, fontweight="bold", color=NAVY)
    ax1.set_xlabel("Zenith-V Quantity Demanded (Q)", fontsize=7.8, fontweight="bold", color=NAVY)
    ax1.set_ylabel("Zenith-V Price (₹ '000)", fontsize=7.8, fontweight="bold", color=NAVY)
    ax1.set_xlim(10, 92)
    ax1.set_ylim(50, 148)
    ax1.legend(loc="upper right", fontsize=6.8, frameon=True, facecolor="#F8FAFC")
    ax1.grid(True, linestyle="--", alpha=0.3)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.tick_params(labelsize=7.4)

    ax2.set_facecolor(BG_WHITE)
    cats = ["Petrol Scooter\n(Petrol Complement)", "Zenith-V EV\n(Power Complement)"]
    costs = [2.45, 0.25]
    bar_colors = [CORAL, EMERALD]
    bars = ax2.bar(cats, costs, color=bar_colors, width=0.44)

    for b, c in zip(bars, costs):
        ax2.text(
            b.get_x() + b.get_width() / 2,
            c + 0.08,
            f"₹{c:.2f}/km",
            ha="center",
            va="bottom",
            fontsize=8.0,
            fontweight="bold",
            color=NAVY,
        )

    ax2.annotate(
        "90% Lower Cost!\n(Exy < 0 for EV Power)",
        xy=(1.0, 0.58),
        xytext=(0.08, 1.55),
        arrowprops=dict(arrowstyle="->", color=EMERALD, lw=1.6),
        fontsize=7.2,
        fontweight="bold",
        color="#065F46",
        bbox=dict(boxstyle="round,pad=0.26", facecolor="#D1FAE5", edgecolor=EMERALD),
    )

    ax2.set_title("B. Running Cost per Km:\nPetrol vs. EV Complement", fontsize=8.4, fontweight="bold", color=NAVY)
    ax2.set_ylabel("Running Cost (₹ / km)", fontsize=7.8, fontweight="bold", color=NAVY)
    ax2.set_ylim(0, 2.95)
    ax2.grid(axis="y", linestyle="--", alpha=0.3)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.tick_params(labelsize=7.2)

    plt.tight_layout()
    plt.savefig("assets/charts/chart2_cross_elasticity.png", dpi=300)
    plt.close()


def make_chart3_pricing_lrac():
    """Slide 4: Session 5 & 6 Break-Even Analysis (TR = TC at Q = 1,00,000 units) & Margin of Safety."""
    fig, ax = plt.subplots(figsize=(6.0, 2.95), dpi=300)
    fig.patch.set_facecolor(BG_WHITE)
    ax.set_facecolor(BG_WHITE)

    q_k = np.linspace(0, 150, 200)
    tr = 0.08 * q_k * 100
    tc = 200 + 0.06 * q_k * 100
    fc = np.full_like(q_k, 200)

    ax.plot(q_k, tr, color=EMERALD, lw=2.8, label="Total Revenue (TR @ ₹79,999 Penetration Price)")
    ax.plot(q_k, tc, color=CORAL, lw=2.6, label="Total Cost (TC = ₹200 Cr FC + ₹60k/unit VC)")
    ax.plot(q_k, fc, color="#64748B", linestyle=":", lw=1.5, label="Fixed Cost (FC = ₹200 Cr Chennai Plant)")

    ax.fill_between(q_k, tc, tr, where=(q_k >= 100), color="#D1FAE5", alpha=0.65, label="Economic Profit & Margin of Safety Zone")
    ax.fill_between(q_k, tr, tc, where=(q_k <= 100), color="#FFE4E6", alpha=0.45)

    ax.scatter([100], [800], color=NAVY, s=70, zorder=6)
    ax.annotate(
        "Break-Even Point (TR = TC)\nQ_BEP = 1,00,000 Units\n(₹200 Cr FC ÷ ₹20k Margin)",
        xy=(100, 800),
        xytext=(12, 620),
        arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.8),
        fontsize=7.4,
        fontweight="bold",
        color=NAVY,
        bbox=dict(boxstyle="round,pad=0.32", facecolor="#FEF3C7", edgecolor=AMBER),
    )

    ax.annotate(
        "Margin of Safety\n(Sales > 100k Units)",
        xy=(132, 970),
        xytext=(103, 470),
        arrowprops=dict(arrowstyle="->", color=EMERALD, lw=1.8),
        fontsize=7.4,
        fontweight="bold",
        color="#065F46",
        bbox=dict(boxstyle="round,pad=0.28", facecolor="#D1FAE5", edgecolor=EMERALD),
    )

    ax.set_title("Session 5 & 6: Penetration Pricing Break-Even Analysis (TR = TC)", fontsize=9.2, fontweight="bold", color=NAVY)
    ax.set_xlabel("Sales Volume — Quantity of Zenith-V (Thousand Units)", fontsize=8.2, fontweight="bold", color=NAVY)
    ax.set_ylabel("Revenue & Cost (₹ Crore)", fontsize=8.2, fontweight="bold", color=NAVY)
    ax.set_xlim(0, 150)
    ax.set_ylim(0, 1250)
    ax.legend(loc="upper left", fontsize=6.6, frameon=True, facecolor="#F8FAFC")
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=7.6)

    plt.tight_layout()
    plt.savefig("assets/charts/chart3_pricing_lrac.png", dpi=300)
    plt.close()


def make_chart4_kinked_demand():
    """Slide 5: Session 7 Strategic Interdependence & Sweezy's Kinked Demand Curve."""
    fig, ax = plt.subplots(figsize=(6.0, 2.95), dpi=300)
    fig.patch.set_facecolor(BG_WHITE)
    ax.set_facecolor(BG_WHITE)

    q_upper = np.linspace(10, 50, 80)
    p_upper = 110 - 0.60 * q_upper

    q_lower = np.linspace(50, 82, 80)
    p_lower = 165 - 1.70 * q_lower

    ax.plot(q_upper, p_upper, color=TEAL, lw=2.8, label="Elastic Above P* (Rivals Ignore Price Hike)")
    ax.plot(q_lower, p_lower, color=NAVY, lw=3.0, label="Inelastic Below P* (Ola & Ather Match Cut)")

    ax.scatter([50], [80], color=CORAL, s=75, zorder=6)
    ax.axhline(80, xmax=0.55, color="#94A3B8", linestyle=":", lw=1.3)
    ax.axvline(50, ymax=0.68, color="#94A3B8", linestyle=":", lw=1.3)
    ax.axhline(60, color=EMERALD, linestyle="--", lw=1.5, label="Zenith-V Unit Cost (MC = ₹60,000)")

    ax.annotate(
        "Kink at Launch Price P* = ₹79,999\nStrategic Interdependence (Jio Parallel):\nOla & Ather match price cuts below P*",
        xy=(50, 80),
        xytext=(48, 92),
        arrowprops=dict(arrowstyle="->", color=CORAL, lw=1.8),
        fontsize=7.4,
        fontweight="bold",
        color=NAVY,
        bbox=dict(boxstyle="round,pad=0.32", facecolor="#FEF3C7", edgecolor=AMBER),
    )

    ax.set_title("Session 7: Strategic Interdependence & Kinked Demand Curve", fontsize=9.2, fontweight="bold", color=NAVY)
    ax.set_xlabel("Quantity Demanded (Q, Thousand Units)", fontsize=8.2, fontweight="bold", color=NAVY)
    ax.set_ylabel("Scooter Price (₹ '000)", fontsize=8.2, fontweight="bold", color=NAVY)
    ax.set_xlim(10, 90)
    ax.set_ylim(20, 115)
    ax.legend(loc="lower left", fontsize=6.8, frameon=True, facecolor="#F8FAFC")
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=7.6)

    plt.tight_layout()
    plt.savefig("assets/charts/chart4_kinked_demand.png", dpi=300)
    plt.close()


def make_chart5_npv_irr():
    """Slide 6: Session 9 NPV Profile Showing NPV = +₹50 Cr @ 15% => IRR = 23.0% (> 15%)."""
    fig, ax = plt.subplots(figsize=(6.0, 2.75), dpi=300)
    fig.patch.set_facecolor(BG_WHITE)
    ax.set_facecolor(BG_WHITE)

    cf = 250.0 / sum(1.0 / ((1.0 + 0.15) ** t) for t in range(1, 8))
    r_vals = np.linspace(0.04, 0.30, 300)
    npv_vals = np.array([sum(cf / ((1.0 + r) ** t) for t in range(1, 8)) - 200.0 for r in r_vals])
    r_pct = r_vals * 100.0

    irr_est = float(np.interp(0.0, npv_vals[::-1], r_pct[::-1]))

    ax.plot(r_pct, npv_vals, color=NAVY, lw=2.8, label="Chennai Plant NPV Curve")
    ax.axhline(0, color=SLATE, lw=1.4, linestyle="-")

    ax.fill_between(
        r_pct, npv_vals, 0, where=(npv_vals >= 0), color="#D1FAE5", alpha=0.55, label="Accept Zone (NPV > 0)"
    )
    ax.fill_between(
        r_pct, npv_vals, 0, where=(npv_vals < 0), color="#FFE4E6", alpha=0.55, label="Reject Zone (NPV < 0)"
    )

    ax.scatter([15.0], [50.0], color=EMERALD, s=70, zorder=6)
    ax.plot([15.0, 15.0], [0, 50.0], color=EMERALD, linestyle="--", lw=1.6)
    ax.plot([4.0, 15.0], [50.0, 50.0], color=EMERALD, linestyle="--", lw=1.6)
    ax.annotate(
        "At r = 15%:\nNPV = +₹50 Cr (> 0)",
        xy=(15.0, 50.0),
        xytext=(5.2, 11.0),
        arrowprops=dict(arrowstyle="->", color=EMERALD, lw=1.8),
        fontsize=7.6,
        fontweight="bold",
        color="#065F46",
        bbox=dict(boxstyle="round,pad=0.28", facecolor="#ECFDF5", edgecolor=EMERALD),
    )

    ax.scatter([irr_est], [0.0], color=CORAL, s=75, marker="D", zorder=6)
    ax.annotate(
        f"IRR ≈ {irr_est:.1f}% (> 15%)\n(Rate where NPV = 0)",
        xy=(irr_est, 0.0),
        xytext=(18.2, 52),
        arrowprops=dict(arrowstyle="->", color=CORAL, lw=1.8),
        fontsize=7.6,
        fontweight="bold",
        color="#9F1239",
        bbox=dict(boxstyle="round,pad=0.28", facecolor="#FFF1F2", edgecolor=CORAL),
    )

    ax.set_title("Session 9: NPV Profile (Why NPV = ₹50 Cr @ 15% ⇒ IRR > 15%)", fontsize=9.0, fontweight="bold", color=NAVY)
    ax.set_xlabel("Discount Rate (r %)", fontsize=8.0, fontweight="bold", color=NAVY)
    ax.set_ylabel("NPV (₹ Crore)", fontsize=8.0, fontweight="bold", color=NAVY)
    ax.set_xlim(4, 30)
    ax.set_ylim(-55, 165)
    ax.legend(loc="upper right", fontsize=6.8, frameon=True, facecolor="#F8FAFC")
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=7.5)

    plt.tight_layout()
    plt.savefig("assets/charts/chart5_npv_irr.png", dpi=300)
    plt.close()


if __name__ == "__main__":
    make_chart1_oligopoly()
    make_chart2_cross_elasticity()
    make_chart3_pricing_lrac()
    make_chart4_kinked_demand()
    make_chart5_npv_irr()
    print("All 5 lecture-aligned charts generated successfully.")
