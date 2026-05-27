"""
Tunisia TSR-1G Sortie 1c — Omega Latent / Stored Social Potential Energy

Three-panel figure:
  Panel A: T_tension (kinetic/expressed) vs Omega_acc (latent/accumulated)
           Shows the divergence in 2010 where expressed tension falls but
           accumulated latent energy continues to rise.
  Panel B: sigma_structural and sigma_valve -- the two drivers of Omega_latent_inst.
  Panel C: Omega_latent_inst per year with regime phase strip overlay.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from pathlib import Path

REPO   = Path(__file__).resolve().parents[2]
DATA   = REPO / "DATA" / "processed" / "tunisia" / "annual_panel.csv"
OUTDIR = REPO / "OUTPUTS" / "1e"
OUTDIR.mkdir(parents=True, exist_ok=True)
OUT    = OUTDIR / "1e Tunisia_Omega_Latent.png"

df = pd.read_csv(DATA, index_col="year")
years = df.index.values

PHASE_COLORS = {
    "Stable":       "#d4edda",
    "Metastable":   "#fff3cd",
    "Pre-Critical": "#fde8d8",
    "Critical":     "#f8d7da",
}
PHASE_EDGE = {
    "Stable":       "#2d6a4f",
    "Metastable":   "#b7791f",
    "Pre-Critical": "#c05621",
    "Critical":     "#9b1c1c",
}

EVENTS = [
    (1994, "IMF SAP\npeak",        "top"),
    (2008, "Gafsa\nprotests",      "bottom"),
    (2010, "WikiLeaks /\nCablegate", "top"),
    (2011, "Bouazizi /\nJan 14",   "bottom"),
]

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

# =============================================================================
# PANEL A -- T_tension (kinetic) vs Omega_acc (latent accumulated)
# =============================================================================
ax = axes[0]

ax.plot(years, df["T_tension"],  color="#e67e22", lw=2.0, ls="--", zorder=5,
        label="T  (expressed tension, kinetic proxy)")
ax.plot(years, df["Omega_acc"], color="#8e44ad", lw=2.6, zorder=5,
        label="Omega_acc  (accumulated latent potential energy)")
ax.fill_between(years, df["T_tension"], df["Omega_acc"],
                where=(df["Omega_acc"] > df["T_tension"]),
                color="#8e44ad", alpha=0.12, zorder=3,
                label="Latent excess  (Omega_acc > T)")

# 2010 divergence annotation
ax.annotate(
    "2010: T falls (repression\nsuppresses proxy)\nbut Omega_acc continues\nto accumulate",
    xy=(2010, df.loc[2010, "Omega_acc"]),
    xytext=(2006.5, 0.62),
    fontsize=8, color="#8e44ad",
    arrowprops=dict(arrowstyle="->", color="#8e44ad", lw=1.0),
    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#cccccc", alpha=0.9),
)
ax.annotate(
    "",
    xy=(2010, df.loc[2010, "T_tension"]),
    xytext=(2010, df.loc[2010, "Omega_acc"] - 0.04),
    arrowprops=dict(arrowstyle="->", color="#e67e22", lw=1.0),
)
ax.text(2010.2, (df.loc[2010, "T_tension"] + df.loc[2010, "Omega_acc"]) / 2,
        f"gap = {df.loc[2010,'Omega_acc'] - df.loc[2010,'T_tension']:.3f}",
        fontsize=7.5, color="#555555", va="center")

ax.set_ylim(-0.02, 1.10)
ax.set_ylabel("Normalised value  [0, 1]", fontsize=9)
ax.set_title(
    "Tunisia 1990-2011  |  TSR-1G Sortie 1c: Omega Latent",
    fontsize=13, fontweight="bold", pad=10, loc="left",
)
ax.legend(loc="upper left", fontsize=8.5, framealpha=0.88, edgecolor="#cccccc")

# =============================================================================
# PANEL B -- sigma_structural and sigma_valve
# =============================================================================
ax = axes[1]

ax.plot(years, df["sigma_structural"], color="#c0392b", lw=1.8,
        label="sigma_structural  (Slots 1,2,3,4 -- structural loading)")
ax.plot(years, df["sigma_valve"],      color="#2980b9", lw=1.8, ls="--",
        label="sigma_valve  (Slots 5,6,8 -- valve closure)")
ax.fill_between(years, 0, df["Omega_latent_inst"], color="#8e44ad", alpha=0.18,
                label="Omega_latent_inst  (product)")

ax.axhline(0, color="#cccccc", lw=0.6)
ax.set_ylim(-0.02, 1.05)
ax.set_ylabel("Normalised value  [0, 1]", fontsize=9)
ax.legend(loc="upper left", fontsize=8.5, framealpha=0.88, edgecolor="#cccccc")

# sigma_valve normalization note
ax.text(1990.3, 0.92,
        "Note: sigma_valve understated 1990-2000 (minmax of narrow FH range;\n"
        "absolute FH scale would raise pre-2000 valve closure significantly).",
        fontsize=6.5, color="#888888", va="top",
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#dddddd", alpha=0.85))

# =============================================================================
# PANEL C -- Omega_latent_inst with phase strip
# =============================================================================
ax = axes[2]

bar_colors = [
    PHASE_COLORS.get(df.loc[yr, "regime_phase"], PHASE_COLORS["Stable"])
    for yr in years
]
ax.bar(years, df["Omega_latent_inst"], color=bar_colors,
       edgecolor=[PHASE_EDGE.get(df.loc[yr, "regime_phase"], PHASE_EDGE["Stable"])
                  for yr in years],
       linewidth=0.7, width=0.8, zorder=3, alpha=0.88,
       label="Omega_latent_inst  (annual contribution)")

ax.plot(years, df["Omega_acc"] * df["Omega_latent_inst"].max(), color="#8e44ad",
        lw=1.8, ls=":", zorder=4,
        label="Omega_acc  (scaled, for shape reference)")

ax.set_ylim(0, df["Omega_latent_inst"].max() * 1.25)
ax.set_ylabel("Omega_latent_inst  [0, 1]", fontsize=9)
ax.set_xlabel("Year", fontsize=9)
ax.set_xticks(range(1990, 2012, 2))
ax.set_xticklabels([str(y) for y in range(1990, 2012, 2)], fontsize=8.5)

phase_patches = [
    mpatches.Patch(facecolor=PHASE_COLORS[p], edgecolor=PHASE_EDGE[p],
                   linewidth=0.8, label=p)
    for p in ["Stable", "Metastable", "Pre-Critical"]
]
ax.legend(handles=phase_patches + ax.get_legend_handles_labels()[0][:2],
          loc="upper left", fontsize=7.5, framealpha=0.88,
          edgecolor="#cccccc", ncol=2)

# =============================================================================
# Event markers across all panels
# =============================================================================
for yr, label, pos in EVENTS:
    for panel in axes:
        panel.axvline(yr, color="#555555", lw=0.9, ls="--", alpha=0.40, zorder=6)
    y_ref = axes[0].get_ylim()[1] * (0.98 if pos == "top" else 0.02)
    va = "top" if pos == "top" else "bottom"
    axes[0].text(yr, y_ref, label, ha="center", va=va, fontsize=6.8,
                 color="#333333",
                 bbox=dict(boxstyle="round,pad=0.15", fc="white",
                           ec="#cccccc", alpha=0.85))

# =============================================================================
# Key values table (2009-2011) as text inset on Panel A
# =============================================================================
table_rows = ["year   T_tension   Omega_acc   phase"]
for yr in [2008, 2009, 2010, 2011]:
    row = df.loc[yr]
    table_rows.append(
        f"{yr}     {row['T_tension']:.3f}       {row['Omega_acc']:.3f}    "
        f"{row['regime_phase']}"
    )
axes[0].text(1990.3, 0.56, "\n".join(table_rows),
             fontsize=7, family="monospace", va="top",
             bbox=dict(boxstyle="round,pad=0.35", fc="white",
                       ec="#cccccc", alpha=0.92))

fig.tight_layout(rect=[0, 0, 1, 1], h_pad=2.5)
plt.savefig(OUT, dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
plt.close()
print(f"Saved: {OUT}")
