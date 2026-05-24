"""
Tunisia TSR-1G Regime Phase Trajectory — Figure 1
Three-panel publication figure:
  Panel A: MDI* with C/T crossover and phase classification bands
  Panel B: CODA structural forces (D_dom, A_aut, C_conn, O_ord)
  Panel C: Observable drivers (protest events, food price index)
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
REPO   = Path(__file__).resolve().parents[2]
DATA   = REPO / "DATA" / "processed" / "tunisia" / "annual_panel.csv"
OUTDIR = REPO / "OUTPUTS" / "plots"
OUTDIR.mkdir(parents=True, exist_ok=True)
OUT    = OUTDIR / "Tunisia_Regime_Phase_Trajectory.png"

# ── Load ──────────────────────────────────────────────────────────────────────
df = pd.read_csv(DATA, index_col="year")
years = df.index.values

# ── Phase band definitions (MDI* thresholds from classify_phase) ───────────────
PHASE_COLORS = {
    "Stable":       "#d4edda",   # soft green
    "Metastable":   "#fff3cd",   # soft amber
    "Pre-Critical": "#fde8d8",   # soft orange
    "Critical":     "#f8d7da",   # soft red
}
PHASE_BOUNDS = [
    ("Stable",       0.00, 0.45),
    ("Metastable",   0.45, 0.55),
    ("Pre-Critical", 0.55, 0.75),
    ("Critical",     0.75, 1.00),
]
PHASE_EDGE = {
    "Stable": "#2d6a4f", "Metastable": "#b7791f",
    "Pre-Critical": "#c05621", "Critical": "#9b1c1c",
}

# ── Key historical events ─────────────────────────────────────────────────────
EVENTS = [
    (1991, "Ben Ali\nconsolidation",  "top"),
    (1994, "IMF SAP\npeak",           "bottom"),
    (2002, "Political\ntightening",   "top"),
    (2008, "Gafsa\nprotests",         "bottom"),
    (2010, "WikiLeaks /\nCablegate",  "top"),
    (2011, "Bouazizi /\nJan 14",      "bottom"),
]

# ── Normalise protest counts and food price for Panel C ───────────────────────
def norm01(s):
    lo, hi = s.min(), s.max()
    return (s - lo) / (hi - lo) if hi > lo else s * 0

protest_n  = norm01(df["protest_events_count"])
food_n     = norm01(df["food_price_index"])

# ── Figure setup ──────────────────────────────────────────────────────────────
fig, axes = plt.subplots(
    3, 1, figsize=(13, 11),
    gridspec_kw={"height_ratios": [3, 2, 2]},
    sharex=True,
)
fig.patch.set_facecolor("#fafafa")
for ax in axes:
    ax.set_facecolor("#fafafa")

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size":   10,
    "axes.spines.top":   False,
    "axes.spines.right": False,
})

# ═══════════════════════════════════════════════════════════════════════════════
# PANEL A — MDI*, Cohesion, Tension + phase bands
# ═══════════════════════════════════════════════════════════════════════════════
ax = axes[0]

# Phase background bands (horizontal)
for name, lo, hi in PHASE_BOUNDS:
    ax.axhspan(lo, hi, color=PHASE_COLORS[name], alpha=0.55, zorder=0)
    ax.axhline(lo, color=PHASE_EDGE[name], lw=0.6, ls="--", alpha=0.5, zorder=1)

# Phase band labels (right margin)
for name, lo, hi in PHASE_BOUNDS:
    mid = (lo + hi) / 2
    ax.text(2011.6, mid, name, va="center", ha="left",
            fontsize=7.5, color=PHASE_EDGE[name], fontweight="bold")

# MDI* — primary hazard line
ax.plot(years, df["MDI_star"], color="#c0392b", lw=2.8, zorder=5,
        label="MDI* (Mass Disruption Index)")
ax.fill_between(years, 0, df["MDI_star"], color="#c0392b", alpha=0.12, zorder=4)

# C_cohesion and T_tension
ax.plot(years, df["C_cohesion"], color="#2980b9", lw=1.8, ls="-",
        zorder=5, label="C  (Cohesion)")
ax.plot(years, df["T_tension"],  color="#e67e22", lw=1.8, ls="-",
        zorder=5, label="T  (Tension)")

# C/T crossover shading — area where T > C
ct_cross = np.maximum(df["T_tension"] - df["C_cohesion"], 0)
ax.fill_between(years, df["C_cohesion"], df["T_tension"],
                where=(df["T_tension"] > df["C_cohesion"]),
                color="#e74c3c", alpha=0.20, zorder=3, label="T > C  (destabilising)")

ax.set_ylim(-0.02, 1.08)
ax.set_ylabel("Normalised value  [0, 1]", fontsize=9)
ax.set_title(
    "Tunisia 1990–2011  |  TSR-1G Regime Phase Trajectory",
    fontsize=13, fontweight="bold", pad=10, loc="left"
)

leg_a = ax.legend(loc="upper left", fontsize=8.5, framealpha=0.85,
                  edgecolor="#cccccc", ncol=2)
ax.add_artist(leg_a)

# ═══════════════════════════════════════════════════════════════════════════════
# PANEL B — CODA structural forces
# ═══════════════════════════════════════════════════════════════════════════════
ax = axes[1]

coda_series = {
    "D_dom  (Dominion)":    (df["CODA_D_dom"],  "#8e44ad", "-"),
    "A_aut  (Autonomy)":    (df["CODA_A_aut"],  "#27ae60", "--"),
    "C_conn (Connection)":  (df["CODA_C_conn"], "#2980b9", ":"),
    "O_ord  (Order)":       (df["CODA_O_ord"],  "#e67e22", "-."),
}
for label, (series, color, ls) in coda_series.items():
    ax.plot(years, series, color=color, lw=1.8, ls=ls, label=label)

# Imbalance: D_dom - A_aut gap (shaded)
gap = df["CODA_D_dom"] - df["CODA_A_aut"]
ax.fill_between(years, df["CODA_A_aut"], df["CODA_D_dom"],
                where=(gap > 0), color="#8e44ad", alpha=0.10,
                label="D_dom > A_aut  (autonomy deficit)")

ax.axhline(0.5, color="#555555", lw=0.6, ls=":", alpha=0.4)
ax.set_ylim(-0.02, 1.08)
ax.set_ylabel("CODA force magnitude  [0, 1]", fontsize=9)
ax.legend(loc="upper left", fontsize=8, framealpha=0.85,
          edgecolor="#cccccc", ncol=2)

# ═══════════════════════════════════════════════════════════════════════════════
# PANEL C — Observable drivers: protest events + food price
# ═══════════════════════════════════════════════════════════════════════════════
ax = axes[2]

# Food price index (right-axis scale shown via color + label)
ax.fill_between(years, food_n, color="#e67e22", alpha=0.25, zorder=2)
ax.plot(years, food_n, color="#e67e22", lw=1.8, zorder=3,
        label="FAO FFPI  (norm.)")

# Protest event count
ax.bar(years, protest_n, color="#c0392b", alpha=0.55, width=0.7, zorder=3,
       label="Protest events  (norm.)")

ax.set_ylim(-0.02, 1.15)
ax.set_ylabel("Normalised value  [0, 1]", fontsize=9)
ax.set_xlabel("Year", fontsize=9)
ax.legend(loc="upper left", fontsize=8.5, framealpha=0.85,
          edgecolor="#cccccc")

# ═══════════════════════════════════════════════════════════════════════════════
# Event markers — across all panels
# ═══════════════════════════════════════════════════════════════════════════════
for yr, label, pos in EVENTS:
    for i, ax in enumerate(axes):
        ax.axvline(yr, color="#555555", lw=0.9, ls="--", alpha=0.45, zorder=6)

    # Label only on Panel A
    y_pos = 1.02 if pos == "top" else -0.01
    va    = "bottom" if pos == "top" else "top"
    axes[0].text(yr, y_pos, label, ha="center", va=va,
                 fontsize=6.8, color="#333333",
                 bbox=dict(boxstyle="round,pad=0.15", fc="white",
                           ec="#cccccc", alpha=0.85))

# ═══════════════════════════════════════════════════════════════════════════════
# X-axis ticks
# ═══════════════════════════════════════════════════════════════════════════════
axes[2].set_xticks(range(1990, 2012, 2))
axes[2].set_xticklabels([str(y) for y in range(1990, 2012, 2)], fontsize=8.5)

# ── Tight layout and save ──────────────────────────────────────────────────────
fig.tight_layout(rect=[0, 0, 0.92, 1])   # leave right margin for phase labels
plt.savefig(OUT, dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
plt.close()
print(f"Saved: {OUT}")
