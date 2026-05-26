"""
Sortie 1d: Quarterly TSR-1G Structural Panel -- Tunisia 2008 Q1 through 2011 Q1.

Motivation: the annual panel misses 2010 as a precursor because:
  (a) Annual FFPI average masks the Q4 2010 food price acceleration.
  (b) Annual T_tension conflates protest-suppressed quarters with genuinely calm ones.
  (c) The absolute FH scale is more theoretically correct than within-Tunisia minmax,
      which was returning cl_n = 1.0 because FH score was constant.

Key changes vs sortie 1c:
  - FFPI at quarterly resolution (from FAO monthly archive)
  - Protest/repression distributed quarterly from research event record
  - FH civil liberties/political rights on absolute 1-7 scale
  - Civil space discrete-event adjustments per quarter
  - Omega_acc decay_q = 0.85^(1/4) = 0.963 per quarter
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from pathlib import Path

REPO   = Path(__file__).resolve().parents[2]
OUTDIR = REPO / "OUTPUTS" / "1d"
OUTDIR.mkdir(parents=True, exist_ok=True)
OUT_PNG = OUTDIR / "1d Tunisia_Quarterly_2008_2011.png"
OUT_CSV = OUTDIR / "1d Tunisia_Quarterly_Panel.csv"

# =============================================================================
# QUARTERLY INPUT DATA TABLE
# Compiled from FAO, ACLED, Freedom House, HRW, Nawaat, WikiLeaks research.
# See 1d readme.txt for full source citations.
# =============================================================================

QUARTERS = [
    '2008-Q1','2008-Q2','2008-Q3','2008-Q4',
    '2009-Q1','2009-Q2','2009-Q3','2009-Q4',
    '2010-Q1','2010-Q2','2010-Q3','2010-Q4',
    '2011-Q1',
]

# Slot 4: FAO FFPI quarterly averages (base 2002-2004=100)
# Source: FAO monthly archive; averages computed over Jan-Mar, Apr-Jun, Jul-Sep, Oct-Dec
FFPI = [
    209.0, 214.0, 200.7, 158.0,   # 2008: global food price crisis peak in Q2
     91.3,  98.0,  99.0, 108.0,   # 2009: crash and recovery
    103.3, 119.0, 129.0, 136.7,   # 2010: accelerating rise (Q4: Oct=127, Nov=138, Dec~145)
    231.0,                          # 2011-Q1: record high (Jan=231); revolution quarter
]

# Slot 3: Youth unemployment % (annual WB values distributed uniformly within year)
YOUTH_UNEMP = [
    28.66, 28.66, 28.66, 28.66,   # 2008 annual: 28.66%
    31.15, 31.15, 31.15, 31.15,   # 2009 annual: 31.15%
    29.57, 29.57, 29.57, 29.57,   # 2010 annual: 29.57%
    42.64,                          # 2011 annual: 42.64% (revolution year)
]

# Slot 1: Gini coefficient (annual; minimal variation 2008-2010)
GINI = [
    38.18, 38.18, 38.18, 38.18,
    38.18, 38.18, 38.18, 38.18,   # 2009: NaN in WB; use 2008 value
    38.50, 38.50, 38.50, 38.50,
    38.50,                          # 2011: NaN in WB; use 2010 value
]

# Slot 2: GDP per capita USD (annual WB; distributed uniformly within year)
GDP_PC = [
    4255.05, 4255.05, 4255.05, 4255.05,
    4080.09, 4080.09, 4080.09, 4080.09,
    4291.86, 4291.86, 4291.86, 4291.86,
    4420.65,
]

# Slot 7: Protest events (quarterly) -- ACLED annual totals distributed by
# known quarterly intensity from research (Gafsa: Jan-Jun 2008; cascade: Dec 2010)
# ACLED annual: 2008=28, 2009=1, 2010=26, 2011=528
PROTEST_Q = [
     8, 18,  2,  0,    # 2008: Gafsa protests peak in Q2, suppressed by Q3
     0,  1,  0,  0,    # 2009: minimal; 1 event (UGET hunger strike)
     2,  8,  3, 13,    # 2010: Sidi Bouzid Q2, cascade beginning Q4 (Dec 17)
   528,                 # 2011-Q1: revolution
]

# Slot 8: Repression events (quarterly) -- ACLED annual counts are sparse
# (2008=1, 2009=0, 2010=2, 2011=54). Research shows much higher intensity:
# Gafsa: 3 deaths, ~300 arrested; Q4 2010: activist account hacking, pre-cascade crackdown.
# These quarterly values reflect research-documented intensity, not raw ACLED count.
REPRESSION_Q = [
     3, 10,  5,  2,    # 2008: Q2 peak (killings Jun 6, mass arrests)
     1,  1,  1,  2,    # 2009: low but persistent
     1,  2,  2,  5,    # 2010: Q4 includes WikiLeaks blocking + account attacks
    54,                  # 2011-Q1: sniper fire, mass arrests (ACLED annual)
]

# Slot 5+6: Freedom House -- ABSOLUTE scale (1=free, 7=not free)
# Tunisia: Civil Liberties=5, Political Rights=7 (2008-2011); PR=6 in 2007
# Using absolute normalization: cl_n = (7-cl_score)/6; pr_n = (7-pr_score)/6
CL_SCORE = [5]*13   # constant; absolute norm gives cl_n = 0.333, (1-cl_n) = 0.667
PR_SCORE = [7]*13   # constant; absolute norm gives pr_n = 0.000, (1-pr_n) = 1.000

# Slot 9: Internet penetration % (annual WB values; interpolated quarterly)
INTERNET = [
    27.53, 27.53, 27.53, 27.53,   # 2008
    34.07, 34.07, 34.07, 34.07,   # 2009
    36.80, 36.80, 36.80, 36.80,   # 2010
    39.10,                          # 2011-Q1
]

# Civil space discrete-event adjustment (0=none; higher=more suppression)
# Captures within-year events not reflected in annual FH score.
# Applied as additional valve closure: effective (1-cl_n) += civil_adj
CIVIL_ADJ = [
    0.00, 0.00, 0.05, 0.10,   # 2008: Q3 Facebook briefly blocked; Q4 Kalima hacked/destroyed
    0.15, 0.05, 0.05, 0.10,   # 2009: Q1 Kalima radio destroyed; Q4 post-election crackdown
    0.05, 0.15, 0.10, 0.25,   # 2010: Q2 Skype+Flickr blocked; Q4 WikiLeaks blocked+account attacks
    0.30,                       # 2011-Q1: full censorship escalation + activist account hacking
]

# Key events for figure annotation
KEY_EVENTS = {
    '2008-Q1': 'Gafsa protests\nbegin (Jan 5)',
    '2008-Q2': 'Gafsa killings\n(Jun 6)',
    '2009-Q4': 'Ben Ali re-elected\n89.62% (Oct 25)',
    '2010-Q2': 'Sidi Bouzid\npeasant protests',
    '2010-Q4': 'WikiLeaks (Nov 28)\nBouazizi (Dec 17)',
}

# =============================================================================
# BUILD QUARTERLY DATAFRAME
# =============================================================================
n = len(QUARTERS)
df = pd.DataFrame({
    'quarter':      QUARTERS,
    'ffpi':         FFPI,
    'youth_unemp':  YOUTH_UNEMP,
    'gini':         GINI,
    'gdp_pc':       GDP_PC,
    'protest_q':    PROTEST_Q,
    'repression_q': REPRESSION_Q,
    'cl_score':     CL_SCORE,
    'pr_score':     PR_SCORE,
    'internet':     INTERNET,
    'civil_adj':    CIVIL_ADJ,
})
df = df.set_index('quarter')

# Exclude 2011-Q1 from normalization range (it is expression, not precursor)
PRECURSOR_IDX = [i for i, q in enumerate(QUARTERS) if not q.startswith('2011')]

def norm_precursor(series, invert=False):
    vals = series.values
    lo = vals[PRECURSOR_IDX].min()
    hi = vals[PRECURSOR_IDX].max()
    if hi <= lo:
        return pd.Series(np.zeros(n), index=df.index)
    normed = (vals - lo) / (hi - lo)
    if invert:
        normed = 1.0 - normed
    return pd.Series(np.clip(normed, 0, 1.5), index=df.index)  # allow 2011 to exceed 1

ffpi_n    = norm_precursor(df['ffpi'])
youth_n   = norm_precursor(df['youth_unemp'])
gini_n    = norm_precursor(df['gini'])
gdp_pc_n  = norm_precursor(df['gdp_pc'])           # high GDP = low stress
protest_n = norm_precursor(df['protest_q'])
rep_n     = norm_precursor(df['repression_q'])

# Slot 9 conductivity
internet_n = norm_precursor(df['internet'])

# Absolute FH normalization (fixes constant-value problem from within-Tunisia minmax)
cl_n_abs = ((7 - df['cl_score']) / 6.0).clip(0, 1)   # 0.333 constant
pr_n_abs = ((7 - df['pr_score']) / 6.0).clip(0, 1)   # 0.000 constant

# sigma_structural: Slots 1,2,3,4 -- repression-independent structural loading
# (1 - gdp_pc_n): higher GDP = lower economic stress
sigma_structural = (
      youth_n  * 0.40    # Slot 3: frustrated positional gradient
    + gini_n   * 0.30    # Slot 1: distributional stress
    + ffpi_n   * 0.20    # Slot 4: material stress (now quarterly)
    + (1 - gdp_pc_n) * 0.10  # Slot 2: economic level stress
).clip(0, 1.5)

# sigma_valve: Slots 5,6,8 -- suppression closure factor (absolute FH scale)
# civil_adj adds to the civil component of the valve
effective_civil_closure = ((1 - cl_n_abs) + df['civil_adj']).clip(0, 1)
sigma_valve = (
      rep_n             * 0.50   # Slot 8: active force
    + effective_civil_closure * 0.30   # Slot 6: civil space (absolute + events)
    + (1 - pr_n_abs)    * 0.20  # Slot 5: political constraint (absolute)
).clip(0, 1)

df['sigma_structural']  = sigma_structural.clip(0, 1)
df['sigma_valve']        = sigma_valve.clip(0, 1)
df['Omega_latent_inst']  = (sigma_structural * sigma_valve).clip(0, 1)

# T_tension proxy (kinetic -- expressed tension):
# Same formula as annual, applied at quarterly resolution
df['T_tension_q'] = (
      youth_n * 0.35
    + gini_n  * 0.30
    + rep_n   * 0.20
    + protest_n * 0.15
).clip(0, 1)

# discharge: tension releases when protest is present, not suppressed, civil space exists
discharge = (protest_n * (1 - rep_n) * cl_n_abs).clip(0, 1)

# Omega_acc: time-integral with quarterly decay
# decay_q = annual_decay^(1/4) = 0.85^0.25 ≈ 0.963
DECAY_Q = 0.85 ** 0.25

acc = 0.0
omega_acc_raw = []
for q in QUARTERS:
    inst  = df.loc[q, 'Omega_latent_inst']
    disch = discharge[q]
    acc   = DECAY_Q * acc + inst * (1.0 - disch)
    omega_acc_raw.append(acc)

omega_acc_s = pd.Series(omega_acc_raw, index=df.index)
# Normalise within precursor range
acc_lo = omega_acc_s.iloc[PRECURSOR_IDX].min()
acc_hi = omega_acc_s.iloc[PRECURSOR_IDX].max()
df['Omega_acc'] = ((omega_acc_s - acc_lo) / (acc_hi - acc_lo)).clip(0, 1.5)

# Export quarterly panel
df.to_csv(OUT_CSV)
print(f"Quarterly panel:\n{df[['sigma_structural','sigma_valve','Omega_latent_inst','T_tension_q','Omega_acc']].round(3).to_string()}")

# =============================================================================
# FIGURE
# =============================================================================
PHASE_COLORS = {
    'Stable':       '#d4edda',
    'Metastable':   '#fff3cd',
    'Pre-Critical': '#fde8d8',
    'Critical':     '#f8d7da',
}
PHASE_EDGE = {
    'Stable':       '#2d6a4f',
    'Metastable':   '#b7791f',
    'Pre-Critical': '#c05621',
    'Critical':     '#9b1c1c',
}

# Simple phase estimate based on Omega_acc (precursor-aware)
def qphase(row):
    oa = row['Omega_acc']
    t  = row['T_tension_q']
    if oa > 0.90 or t > 0.85:
        return 'Critical'
    if oa > 0.65 or t > 0.55:
        return 'Pre-Critical'
    if oa > 0.40 or t > 0.30:
        return 'Metastable'
    return 'Stable'

df['phase'] = df.apply(qphase, axis=1)

xs = np.arange(n)
labels = [q.replace('-', '\n') for q in QUARTERS]

fig, axes = plt.subplots(3, 1, figsize=(15, 12),
                          gridspec_kw={'height_ratios': [3, 2, 2]},
                          sharex=True)
fig.patch.set_facecolor('#fafafa')
for ax in axes:
    ax.set_facecolor('#fafafa')

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size':   9.5,
    'axes.spines.top':   False,
    'axes.spines.right': False,
})

# Phase background spans (Panel A)
for xi, q in enumerate(QUARTERS):
    ph = df.loc[q, 'phase']
    for ax in axes:
        ax.axvspan(xi - 0.5, xi + 0.5, color=PHASE_COLORS[ph], alpha=0.35, zorder=0)

# ── Panel A: T_tension_q vs Omega_acc ──────────────────────────────────────
ax = axes[0]
ax.plot(xs, df['T_tension_q'], color='#e67e22', lw=2.0, ls='--', zorder=5,
        label='T_q  (quarterly kinetic proxy)')
ax.plot(xs, df['Omega_acc'],   color='#8e44ad', lw=2.6, zorder=5,
        label='Omega_acc  (accumulated latent potential)')
ax.fill_between(xs, df['T_tension_q'], df['Omega_acc'],
                where=(df['Omega_acc'] > df['T_tension_q']),
                color='#8e44ad', alpha=0.12, zorder=3,
                label='Latent excess (Omega_acc > T_q)')

# 2011 boundary (user: disregard 2011 as expression, not precursor)
ax.axvline(11.5, color='#555555', lw=1.2, ls=':', alpha=0.6)
ax.text(11.6, 0.95, '2011: expression\n(disregarded as\nprecursor)', fontsize=7,
        color='#888888', va='top')

ax.set_ylim(-0.05, 1.25)
ax.set_ylabel('Normalised value  [0, 1]', fontsize=9)
ax.set_title('Tunisia 2008-2011  |  TSR-1G Sortie 1d: Quarterly Omega Latent Analysis',
             fontsize=13, fontweight='bold', pad=10, loc='left')

leg = ax.legend(loc='upper left', fontsize=8, framealpha=0.88, edgecolor='#cccccc')
ax.add_artist(leg)
phase_patches = [mpatches.Patch(facecolor=PHASE_COLORS[p], edgecolor=PHASE_EDGE[p],
                                linewidth=0.8, label=p)
                 for p in ['Stable', 'Metastable', 'Pre-Critical', 'Critical']]
ax.legend(handles=phase_patches, loc='lower left', fontsize=7.5,
          framealpha=0.88, edgecolor='#cccccc', ncol=4,
          title='Phase (Omega_acc-based)', title_fontsize=7)
ax.add_artist(leg)

# ── Panel B: sigma_structural and sigma_valve ───────────────────────────────
ax = axes[1]
ax.plot(xs, df['sigma_structural'], color='#c0392b', lw=1.8,
        label='sigma_structural  (Slots 1,2,3,4 -- structural loading)')
ax.plot(xs, df['sigma_valve'],      color='#2980b9', lw=1.8, ls='--',
        label='sigma_valve  (Slots 5,6,8 -- suppression closure; absolute FH scale)')
ax.fill_between(xs, 0, df['Omega_latent_inst'], color='#8e44ad', alpha=0.18,
                label='Omega_latent_inst  (product)')
ax.axvline(11.5, color='#555555', lw=1.2, ls=':', alpha=0.6)
ax.set_ylim(-0.02, 1.05)
ax.set_ylabel('Normalised value  [0, 1]', fontsize=9)
ax.legend(loc='upper left', fontsize=8, framealpha=0.88, edgecolor='#cccccc')

# FFPI secondary line
ax2 = ax.twinx()
ax2.plot(xs, [f/214.0 for f in FFPI], color='#e67e22', lw=1.2, ls=':', alpha=0.6,
         label='FFPI  (normalised, right axis)')
ax2.set_ylabel('FFPI / 214  (2008 Q2 peak = 1.0)', fontsize=7.5, color='#e67e22')
ax2.tick_params(axis='y', colors='#e67e22')
ax2.set_ylim(-0.02, 1.8)
ax2.spines['right'].set_color('#e67e22')
ax2.spines['top'].set_visible(False)
ax2.legend(loc='upper right', fontsize=7.5, framealpha=0.88, edgecolor='#cccccc')

# ── Panel C: Omega_latent_inst bars + Omega_acc (for shape reference) ───────
ax = axes[2]
bar_colors = [PHASE_COLORS[df.loc[q, 'phase']] for q in QUARTERS]
bar_edges  = [PHASE_EDGE[df.loc[q, 'phase']]  for q in QUARTERS]
ax.bar(xs, df['Omega_latent_inst'], color=bar_colors, edgecolor=bar_edges,
       linewidth=0.7, width=0.7, zorder=3, alpha=0.85,
       label='Omega_latent_inst  (quarterly contribution)')

scale = df['Omega_latent_inst'].max()
ax.plot(xs, df['Omega_acc'] * scale, color='#8e44ad', lw=1.8, ls=':',
        label='Omega_acc  (scaled for shape reference)')

ax.axvline(11.5, color='#555555', lw=1.2, ls=':', alpha=0.6)
ax.set_ylim(0, scale * 1.35)
ax.set_ylabel('Omega_latent_inst  [0, 1]', fontsize=9)
ax.set_xlabel('Quarter', fontsize=9)
ax.set_xticks(xs)
ax.set_xticklabels(labels, fontsize=7.5)
ax.legend(loc='upper left', fontsize=8, framealpha=0.88, edgecolor='#cccccc')

# ── Event markers and annotations ───────────────────────────────────────────
for q, label in KEY_EVENTS.items():
    xi = QUARTERS.index(q)
    top_y = 1.18
    for ax in axes:
        ax.axvline(xi, color='#333333', lw=1.0, ls='--', alpha=0.5, zorder=6)
    axes[0].text(xi, top_y, label, ha='center', va='top', fontsize=6.5,
                 color='#222222',
                 bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='#cccccc', alpha=0.9))

# ── Value table inset (key quarters) ─────────────────────────────────────────
key_q = ['2008-Q2', '2009-Q1', '2009-Q4', '2010-Q2', '2010-Q3', '2010-Q4']
rows = ['quarter        T_q   Omega_acc  phase']
for q in key_q:
    r = df.loc[q]
    rows.append(f"{q}   {r['T_tension_q']:.3f}   {r['Omega_acc']:.3f}    {r['phase']}")
axes[0].text(0.01, 0.46, '\n'.join(rows),
             transform=axes[0].transAxes, fontsize=6.8, family='monospace', va='top',
             bbox=dict(boxstyle='round,pad=0.35', fc='white', ec='#cccccc', alpha=0.92))

fig.tight_layout(rect=[0, 0, 1, 1], h_pad=2.5)
plt.savefig(OUT_PNG, dpi=220, bbox_inches='tight', facecolor=fig.get_facecolor())
plt.close()
print(f"Saved: {OUT_PNG}")
