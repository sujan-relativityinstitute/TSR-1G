"""
Tunisia TSR-1G Inforay Event Log — Figure 2
Three-panel publication figure:
  Panel A: Symbolic criticality timeline — bubble size = propagation reach,
            colour = interaction mode, star = narrative sync trigger
  Panel B: Omega field perturbation per event (omega_delta) with cumulative
            Omega loading line
  Panel C: Stored amplification factor (G_stored) per event

x-axis uses event index (not calendar time) to handle the extreme temporal
compression: Tier 1 spans 16 years, Tier 3 spans 28 days. Tier time-spans
are annotated on Panel A.
"""

import sqlite3
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
DB     = REPO / "CASES" / "Tunisia" / "data" / "tunisia_tsr.db"
OUTDIR = REPO / "OUTPUTS" / "plots"
OUTDIR.mkdir(parents=True, exist_ok=True)
OUT    = OUTDIR / "Tunisia_Inforay_Event_Log.png"

# ── Load event log ─────────────────────────────────────────────────────────────
con = sqlite3.connect(DB)
ev  = pd.read_sql("SELECT * FROM tsr_inforay_events ORDER BY date", con)
con.close()

n  = len(ev)
ix = np.arange(n)

# ── Short labels ──────────────────────────────────────────────────────────────
SHORT = [
    "Ennahda\nsuppressed",
    "IMF SAP\npeak",
    "Const.\nmanip.",
    "WSIS\ncontrad.",
    "Gafsa\nprotests",
    "Gafsa\nsuppressed",
    "WikiLeaks\nCablegate",
    "Bouazizi\nself-immol.",
    "Sidi Bouzid\nprotests",
    "Ben Ali\nhospital",
    "Ben Ali\nspeech",
    "Ben Ali\nflees",
]
DATE_LABELS = [
    "May 1992", "1994", "May 2002", "Nov 2005",
    "Jan 2008", "Jun 2008",
    "Nov 28\n2010", "Dec 17\n2010", "Dec 19\n2010",
    "Dec 28\n2010", "Jan 10\n2011", "Jan 14\n2011",
]

# ── Interaction mode colour map ───────────────────────────────────────────────
MODE_COLOR = {
    "amplification": "#c0392b",   # deep red
    "distortive":    "#e67e22",   # orange
    "rejection":     "#f39c12",   # amber
    "scattering":    "#7f8c8d",   # grey
}
bubble_colors = [MODE_COLOR[m] for m in ev["interaction_mode"]]

# ── Tier bands (event index ranges) ──────────────────────────────────────────
TIERS = [
    (0,  5.5, "#f0f9f0", "Tier 1 — Structural loading\n(16 years: 1992-2008)"),
    (5.5, 6.5, "#fffde7", "Tier 2 — Pre-conditioning\n(Nov 2010)"),
    (6.5, 11.5, "#fff0f0", "Tier 3 — Cascade\n(28 days: Dec 17 2010 – Jan 14 2011)"),
]
TIER_EDGE = ["#2d6a4f", "#b7791f", "#9b1c1c"]

# ── Figure setup ──────────────────────────────────────────────────────────────
fig, axes = plt.subplots(
    3, 1, figsize=(14, 11),
    gridspec_kw={"height_ratios": [3, 1.6, 1.6]},
)
fig.patch.set_facecolor("#fafafa")
for ax in axes:
    ax.set_facecolor("#fafafa")

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size":   9.5,
    "axes.spines.top":   False,
    "axes.spines.right": False,
})

# ═══════════════════════════════════════════════════════════════════════════════
# PANEL A — Symbolic criticality timeline
# ═══════════════════════════════════════════════════════════════════════════════
ax = axes[0]

# Tier background bands
for (x0, x1, color, label), edge in zip(TIERS, TIER_EDGE):
    ax.axvspan(x0 - 0.5, x1 + 0.35, color=color, alpha=0.55, zorder=0)
    # Tier label at top
    mid = (x0 + x1) / 2
    ax.text(mid, 1.09, label, ha="center", va="bottom",
            fontsize=7.5, color=edge, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.2", fc=color, ec=edge,
                      alpha=0.85, linewidth=0.8))

# Baseline
ax.axhline(0, color="#cccccc", lw=0.6)

# Symbolic criticality threshold reference lines
for thresh, label in [(0.65, "high SC"), (0.90, "near-maximum SC")]:
    ax.axhline(thresh, color="#aaaaaa", lw=0.7, ls=":", alpha=0.7)
    ax.text(11.5, thresh + 0.01, label, fontsize=6.5, color="#888888", ha="right")

# Main bubbles — size proportional to propagation_reach
bubble_sizes = (ev["propagation_reach"] * 900 + 80).values

sc = ax.scatter(
    ix, ev["symbolic_criticality"],
    s=bubble_sizes,
    c=bubble_colors,
    alpha=0.78,
    linewidths=1.2,
    edgecolors="white",
    zorder=4,
)

# Narrative sync trigger — gold star overlaid
sync_mask = ev["narrative_sync_trigger"] == 1
ax.scatter(
    ix[sync_mask], ev.loc[sync_mask, "symbolic_criticality"],
    s=120, marker="*", color="#f1c40f", zorder=5,
    label="Narrative sync triggered",
    edgecolors="#b7791f", linewidths=0.8,
)

# multi_axis ring (dashed circle edge)
multi_mask = ev["multi_axis"] == 1
ax.scatter(
    ix[multi_mask], ev.loc[multi_mask, "symbolic_criticality"],
    s=bubble_sizes[multi_mask] * 1.6,
    facecolors="none",
    edgecolors="#555555",
    linewidths=1.2,
    linestyles="--",
    zorder=3,
    label="Multi-axis content vector",
)

# Vertical drop lines
for i, sc_val in enumerate(ev["symbolic_criticality"]):
    ax.plot([i, i], [0, sc_val], color=bubble_colors[i], lw=0.9,
            alpha=0.35, zorder=2)

# Gafsa / Bouazizi contrast annotation
ax.annotate(
    "",
    xy=(7, ev.loc[7, "symbolic_criticality"]),
    xytext=(4, ev.loc[4, "symbolic_criticality"]),
    arrowprops=dict(
        arrowstyle="<->",
        color="#555555",
        lw=1.2,
        connectionstyle="arc3,rad=0.3",
    ),
    zorder=6,
)
ax.text(5.5, 0.70, "Gafsa → Bouazizi\nSame Ω, different geometry",
        ha="center", va="bottom", fontsize=7, color="#555555", style="italic",
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#cccccc", alpha=0.85))

# Event value labels
for i, (sc_val, pr_val) in enumerate(
        zip(ev["symbolic_criticality"], ev["propagation_reach"])):
    offset = 0.06 if sc_val < 0.88 else -0.08
    va_dir = "bottom" if sc_val < 0.88 else "top"
    ax.text(i, sc_val + offset, f"{sc_val:.2f}",
            ha="center", va=va_dir, fontsize=6.5, color="#333333")

ax.set_xlim(-0.7, 11.7)
ax.set_ylim(-0.05, 1.22)
ax.set_ylabel("Symbolic Criticality  [0, 1]", fontsize=9)
ax.set_title(
    "Tunisia 1992–2011  |  TSR-1G Inforay Event Log",
    fontsize=13, fontweight="bold", pad=10, loc="left",
)
ax.set_xticks(ix)
ax.set_xticklabels(DATE_LABELS, fontsize=7.5)

# Legend — interaction mode
legend_patches = [
    mpatches.Patch(facecolor=c, edgecolor="white", label=m.capitalize(), linewidth=0.8)
    for m, c in MODE_COLOR.items()
]
legend_patches += [
    Line2D([0], [0], marker="*", color="w", markerfacecolor="#f1c40f",
           markeredgecolor="#b7791f", markersize=10, label="Narrative sync trigger"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor="none",
           markeredgecolor="#555555", markersize=10, markeredgewidth=1.2,
           linestyle="--", label="Multi-axis content vector"),
]
ax.legend(handles=legend_patches, loc="upper left", fontsize=7.5,
          framealpha=0.88, edgecolor="#cccccc", ncol=3)

# Bubble size legend (propagation reach)
for pr, label in [(0.15, "reach 0.15"), (0.50, "reach 0.50"), (1.0, "reach 1.0")]:
    ax.scatter([], [], s=pr * 900 + 80, c="#cccccc", alpha=0.7,
               edgecolors="white", label=label, linewidths=1.0)
ax.legend(
    handles=ax.get_legend_handles_labels()[0][-3:],
    title="Propagation reach\n(bubble size)",
    loc="lower right", fontsize=7.5, framealpha=0.88,
    edgecolor="#cccccc", title_fontsize=7.5,
)
# Restore main legend
leg_main = ax.legend(handles=legend_patches, loc="upper left", fontsize=7.5,
                     framealpha=0.88, edgecolor="#cccccc", ncol=3)
ax.add_artist(leg_main)
reach_patches = [
    Line2D([0], [0], marker="o", color="w",
           markerfacecolor="#cccccc", markeredgecolor="white",
           markersize=np.sqrt(pr * 900 + 80) * 0.55,
           label=f"reach {pr:.2f}")
    for pr in [0.15, 0.50, 1.00]
]
ax.legend(handles=reach_patches, title="Propagation reach", title_fontsize=7,
          loc="lower right", fontsize=7.5, framealpha=0.88, edgecolor="#cccccc")
ax.add_artist(leg_main)

# Short event name labels below x-axis ticks
ax2 = ax.twiny()
ax2.set_xlim(ax.get_xlim())
ax2.set_xticks(ix)
ax2.set_xticklabels(SHORT, fontsize=6.5, color="#444444")
ax2.xaxis.set_ticks_position("bottom")
ax2.xaxis.set_label_position("bottom")
ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)
ax2.spines["bottom"].set_visible(False)
ax2.spines["left"].set_visible(False)
ax2.tick_params(axis="x", length=0, pad=18)

# ═══════════════════════════════════════════════════════════════════════════════
# PANEL B — Omega field perturbation + cumulative Omega loading
# ═══════════════════════════════════════════════════════════════════════════════
ax = axes[1]

omega = ev["omega_delta"].values
cumulative_omega = np.cumsum(omega)

# Per-event bars: red = loading (+), blue = release (-)
bar_colors = ["#c0392b" if v >= 0 else "#2980b9" for v in omega]
ax.bar(ix, omega, color=bar_colors, alpha=0.70, width=0.55, zorder=3)
ax.axhline(0, color="#999999", lw=0.7)

# Cumulative Omega line (right axis)
ax_r = ax.twinx()
ax_r.plot(ix, cumulative_omega, color="#8e44ad", lw=2.2, ls="-",
          zorder=4, label="Cumulative Ω loading")
ax_r.fill_between(ix, 0, cumulative_omega, color="#8e44ad", alpha=0.10, zorder=3)
ax_r.set_ylabel("Cumulative Ω  (running total)", fontsize=8.5, color="#8e44ad")
ax_r.tick_params(axis="y", colors="#8e44ad")
ax_r.spines["right"].set_color("#8e44ad")
ax_r.spines["top"].set_visible(False)

# Annotate the Omega peak
peak_i = int(np.argmax(cumulative_omega))
ax_r.annotate(
    f"Peak Ω = {cumulative_omega[peak_i]:.2f}",
    xy=(peak_i, cumulative_omega[peak_i]),
    xytext=(peak_i - 2.5, cumulative_omega[peak_i] - 0.6),
    fontsize=7.5, color="#8e44ad",
    arrowprops=dict(arrowstyle="->", color="#8e44ad", lw=0.9),
)

# Tier bands
for (x0, x1, color, _), edge in zip(TIERS, TIER_EDGE):
    ax.axvspan(x0 - 0.5, x1 + 0.35, color=color, alpha=0.30, zorder=0)

ax.set_xlim(-0.7, 11.7)
ax.set_ylabel("ω-delta  (per event)", fontsize=9)
ax.set_xticks(ix)
ax.set_xticklabels(DATE_LABELS, fontsize=7.5)

# Legend
omega_patches = [
    mpatches.Patch(facecolor="#c0392b", alpha=0.7, label="Omega loading (stress ↑)"),
    mpatches.Patch(facecolor="#2980b9", alpha=0.7, label="Omega release (discharge)"),
    Line2D([0], [0], color="#8e44ad", lw=2.2, label="Cumulative Ω"),
]
ax.legend(handles=omega_patches, loc="upper left", fontsize=7.5,
          framealpha=0.88, edgecolor="#cccccc")

# ═══════════════════════════════════════════════════════════════════════════════
# PANEL C — G_stored (stored amplification factor)
# ═══════════════════════════════════════════════════════════════════════════════
ax = axes[2]

g_vals = ev["G_stored"].values

# Bar coloured by interaction mode
for i, (g, mode) in enumerate(zip(g_vals, ev["interaction_mode"])):
    ax.bar(i, g, color=MODE_COLOR[mode], alpha=0.72, width=0.55, zorder=3)

ax.axhline(1.0, color="#999999", lw=0.7, ls="--", alpha=0.6)
ax.text(11.4, 1.05, "baseline (G=1)", fontsize=6.5, color="#888888", ha="right")

# Value labels
for i, g in enumerate(g_vals):
    ax.text(i, g + 0.15, f"{g:.1f}×", ha="center", va="bottom",
            fontsize=6.5, color="#333333", fontweight="bold")

# Annotate Bouazizi and Ben Ali flees
ax.annotate(
    "Bouazizi\nG = 8.0×",
    xy=(7, 8.0), xytext=(5.5, 7.2),
    fontsize=7.5, color=MODE_COLOR["amplification"],
    arrowprops=dict(arrowstyle="->", color=MODE_COLOR["amplification"], lw=0.9),
    fontweight="bold",
)
ax.annotate(
    "Ben Ali flees\nG = 10.0×",
    xy=(11, 10.0), xytext=(9.3, 9.2),
    fontsize=7.5, color=MODE_COLOR["amplification"],
    arrowprops=dict(arrowstyle="->", color=MODE_COLOR["amplification"], lw=0.9),
    fontweight="bold",
)

# Tier bands
for (x0, x1, color, _), edge in zip(TIERS, TIER_EDGE):
    ax.axvspan(x0 - 0.5, x1 + 0.35, color=color, alpha=0.30, zorder=0)

ax.set_xlim(-0.7, 11.7)
ax.set_ylim(0, 12)
ax.set_ylabel("G_stored  (amplification factor)", fontsize=9)
ax.set_xlabel("Event (indexed by date — see Panel A for calendar dates)", fontsize=8.5)
ax.set_xticks(ix)
ax.set_xticklabels(DATE_LABELS, fontsize=7.5)

# ── Tight layout and save ──────────────────────────────────────────────────────
fig.tight_layout(rect=[0, 0, 1, 1], h_pad=2.5)
plt.savefig(OUT, dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
plt.close()
print(f"Saved: {OUT}")
