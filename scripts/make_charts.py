"""Regenerate the four charts in a consistent light academic palette (Calibri/Carlito)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np, os
from matplotlib import font_manager as fm

FDIR = "/home/user/.local/share/fonts"
for f in os.listdir(FDIR):
    if f.endswith(".ttf"):
        fm.fontManager.addfont(os.path.join(FDIR, f))
plt.rcParams.update({
    "font.family": "Carlito", "font.size": 10.5, "text.color": "#1B2A41",
    "axes.labelcolor": "#44546A", "xtick.color": "#6B7C93", "ytick.color": "#6B7C93",
    "axes.edgecolor": "#C3CEDC",
})
NAVY = "#12263F"; BLUE = "#2B6CB0"; TEAL = "#0F766E"; AMBER = "#B45309"
GREY = "#8A99AC"; GRID = "#E6EBF2"; RED = "#B3261E"; LGREY = "#CBD5E2"
OUT = "/home/user/bestwork/assets"


def clean(ax, axis="y", grid=True):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#C3CEDC")
    if grid:
        ax.grid(axis=axis, color=GRID, lw=0.8)
        ax.set_axisbelow(True)
    ax.tick_params(length=0, labelsize=9.8)


# ── 1. market share
fig, ax = plt.subplots(figsize=(6.3, 3.55), dpi=220)
brands = ["Others", "Hero", "Ather", "Bajaj", "TVS", "Ola"]
share = [8.0, 5.0, 11.6, 20.0, 21.4, 30.0]
colors = [LGREY, "#DDE3EC", "#B9C6D8", "#7E93AF", BLUE, NAVY]
bars = ax.barh(brands, share, color=colors, height=0.6, zorder=3)
for b, v in zip(bars, share):
    ax.text(v + 0.6, b.get_y() + b.get_height() / 2, f"{v:.1f}%", va="center",
            fontsize=10.2, fontweight="bold", color="#1B2A41")
ax.set_xlim(0, 35)
ax.set_xlabel("Share of FY25 electric two-wheeler registrations (%)", fontsize=9.6, labelpad=7)
clean(ax, "x")
ax.grid(axis="x")
ax.set_title("Four firms hold 86% of the market", fontsize=12, fontweight="bold",
             color=NAVY, loc="left", pad=10)
fig.text(0.012, 0.012, "Source: VAHAN registrations FY2025, industry estimates",
         fontsize=8, color=GREY)
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig(f"{OUT}/chart_market_share.png", bbox_inches="tight"); plt.close(fig)

# ── 2. demand shift
fig, ax = plt.subplots(figsize=(6.2, 3.7), dpi=220)
q = np.linspace(0, 12, 240)
d0 = 108 - 7.0 * q
d1 = d0 + 32
ax.plot(q, d0, color=GREY, lw=2.4, label="D₀  ·  petrol ₹95 / litre")
ax.plot(q, d1, color=TEAL, lw=2.8, label="D₁  ·  petrol ₹115 / litre")
yq = 60.0
q0, q1 = (108 - yq) / 7.0, (140 - yq) / 7.0
ax.annotate("", xy=(q1, yq), xytext=(q0, yq),
            arrowprops=dict(arrowstyle="-|>", color=TEAL, lw=2.0, mutation_scale=16))
ax.plot([q0, q0], [0, yq], ls=(0, (3, 3)), color="#A9B6C7", lw=1.0)
ax.plot([q1, q1], [0, yq], ls=(0, (3, 3)), color=TEAL, lw=1.0, alpha=0.6)
ax.annotate("Q₀", (q0 - 0.32, 5), fontsize=9.6, color="#6B7C93", fontweight="bold")
ax.annotate("Q₁", (q1 - 0.32, 5), fontsize=9.6, color=TEAL, fontweight="bold")
ax.text(3.4, 30, "same price,\nhigher quantity", fontsize=9.4, color=TEAL,
        fontweight="bold", ha="center", linespacing=1.4)
ax.set_xlim(0, 12); ax.set_ylim(0, 152)
ax.set_yticks([20, 40, 60, 80, 100, 120, 140])
ax.set_xlabel("Quantity of Zenith-V demanded ('000 units)", fontsize=9.6, labelpad=10)
ax.set_ylabel("Price of Zenith-V (₹ '000)", fontsize=9.6, labelpad=6)
clean(ax)
leg = ax.legend(loc="upper right", frameon=False, fontsize=9.4, handlelength=1.7,
                bbox_to_anchor=(1.01, 0.90))
for t in leg.get_texts():
    t.set_fontweight("bold")
ax.set_title("Petrol gets dearer → EV demand shifts right", fontsize=11.6,
             fontweight="bold", color=NAVY, loc="left", pad=9)
fig.tight_layout()
fig.savefig(f"{OUT}/chart_demand_shift.png", bbox_inches="tight"); plt.close(fig)

# ── 3. break-even volume vs price
fig, ax = plt.subplots(figsize=(6.1, 3.35), dpi=220)
price = np.arange(66, 116, 0.2)
units = 200e7 / (price * 1000 - 60000) / 1e5
ax.plot(price, units, color=NAVY, lw=2.8, zorder=4)
ax.fill_between(price, units, 0, color=NAVY, alpha=0.04)
for p, lab, col, off in [(75, "Penetration\n₹75,000 · 1.33 lakh", TEAL, (18, 26)),
                         (110, "Skimming\n₹1,10,000 · 0.40 lakh", AMBER, (-20, 30))]:
    u = 200e7 / (p * 1000 - 60000) / 1e5
    ax.plot([p], [u], "o", ms=8, color=col, mec="white", mew=2, zorder=8)
    ax.annotate(lab, (p, u), textcoords="offset points", xytext=off, ha="center",
                fontsize=9.0, fontweight="bold", color=col, linespacing=1.35,
                arrowprops=dict(arrowstyle="-", color=col, lw=0.9, alpha=0.5,
                                shrinkA=0, shrinkB=5))
ax.set_xlim(66, 116); ax.set_ylim(0, 2.2); ax.set_yticks([0, 0.5, 1.0, 1.5, 2.0])
ax.set_xlabel("Launch price (₹ '000)", fontsize=9.6, labelpad=6)
ax.set_ylabel("Units to recover ₹200 cr (lakh)", fontsize=9.4, labelpad=6)
clean(ax)
ax.set_title("Break-even volume falls as the price rises", fontsize=11.4,
             fontweight="bold", color=NAVY, loc="left", pad=9)
fig.tight_layout()
fig.savefig(f"{OUT}/chart_price_tradeoff.png", bbox_inches="tight"); plt.close(fig)

# ── 4. NPV profile
fig, ax = plt.subplots(figsize=(6.1, 3.45), dpi=220)
n, cf, irr = 10, 49.81, 21.29
r = np.linspace(0.02, 0.32, 500)
npv = np.array([sum(cf / (1 + x) ** t for t in range(1, n + 1)) - 200 for x in r])
ax.plot(r * 100, npv, color=NAVY, lw=2.8, zorder=4)
ax.axhline(0, color="#9AA8BC", lw=1.2, zorder=2)
ax.fill_between(r * 100, npv, 0, where=(npv > 0), color=TEAL, alpha=0.10, zorder=1)
ax.fill_between(r * 100, npv, 0, where=(npv < 0), color=RED, alpha=0.06, zorder=1)
ax.axvline(15, color=AMBER, lw=1.3, ls=(0, (4, 3)), zorder=3)
ax.axvline(irr, color=TEAL, lw=1.3, ls=(0, (4, 3)), zorder=3)
ax.plot([15], [50], "o", ms=8, color=AMBER, mec="white", mew=2, zorder=8)
ax.annotate("NPV at 15% = +₹50 cr", (15, 50), textcoords="offset points", xytext=(-118, -34),
            fontsize=9.2, fontweight="bold", color=AMBER,
            arrowprops=dict(arrowstyle="-", color=AMBER, lw=0.9,
                            connectionstyle="arc3,rad=0.2"))
ax.plot([irr], [0], "o", ms=8, color=TEAL, mec="white", mew=2, zorder=8)
ax.annotate("IRR ≈ 21.3%\nNPV = 0", (irr, 0), textcoords="offset points", xytext=(10, 22),
            fontsize=9.2, fontweight="bold", color=TEAL, linespacing=1.35)
ax.text(3.2, 62, "ACCEPT", fontsize=9.4, fontweight="bold", color=TEAL)
ax.text(25.2, -64, "REJECT", fontsize=9.4, fontweight="bold", color=RED)
ax.set_xlabel("Discount rate (%)", fontsize=9.6, labelpad=6)
ax.set_ylabel("Project NPV (₹ crore)", fontsize=9.6, labelpad=6)
ax.set_xlim(2, 32); ax.set_ylim(-100, 104); ax.set_yticks([-100, -50, 0, 50, 100])
clean(ax)
ax.set_title("NPV falls to zero exactly at the IRR", fontsize=11.4, fontweight="bold",
             color=NAVY, loc="left", pad=9)
fig.tight_layout()
fig.savefig(f"{OUT}/chart_npv_profile.png", bbox_inches="tight"); plt.close(fig)
print("charts rebuilt")
