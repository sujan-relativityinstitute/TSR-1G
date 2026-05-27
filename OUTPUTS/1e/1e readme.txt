Tunisia TSR-1G Analysis Sortie 1e
Date: 2026-05-27

Analysis: Quarterly structural panel -- Tunisia 2008 Q1 through 2011 Q1 (corrected).
Baseline: Sortie 1d (quarterly Omega_latent) with audit fix D.4 applied.

PRIMARY OUTPUT
  1e Tunisia_Quarterly_2008_2011.png  -- 3-panel quarterly figure
  1e Tunisia_Quarterly_Panel.csv      -- 13-row quarterly data table

Color scheme: bold high-contrast palette (Wong 2011 colorblind-safe) adopted as
the standard from sortie 1e onwards. The subdued pastel scheme used in sorties
1a-1d is retired.

---
CORRECTION FROM AUDIT (D.4 -- repression double-counting, MEDIUM severity)

repression_n previously entered the model through three simultaneous pathways:
  1. T_tension_q    (weight 0.20) -- same-period kinetic proxy
  2. sigma_valve    (weight 0.50) -- valve closure mechanism
  3. R_repression   (weight 0.50 + political/civil components)

Section 35.2 specifies R(t) affects T(t+1), not T(t). Using repression as a
direct same-period input to T_tension creates an artifact: high repression
simultaneously suppresses expressed tension (correct) and appears in the kinetic
proxy that is supposed to measure expressed tension (circular). The same signal
then arrives at MDI* through both T_tension and R_repression pathways.

Corrected T_tension_q weights:
  1d: youth_n*0.35 + gini_n*0.30 + rep_n*0.20 + protest_n*0.15
  1e: youth_n*0.45 + gini_n*0.40 + protest_n*0.15

T_tension_q is now a purely economic/distributional + protest kinetic proxy.
Repression routes only through sigma_valve (valve closure) and the discharge
formula (protest_n * (1-rep_n) * cl_n_abs).

Effect on results: T_tension_q is slightly higher in high-repression quarters
because it no longer absorbs the repression signal that was suppressing it.
2010-Q4: 0.625 (1d) -> 0.673 (1e). Phase classification unchanged.

---
ALL OTHER 1d MECHANICS PRESERVED

  - FFPI at quarterly resolution (FAO monthly archive, averaged to quarters)
  - Absolute FH scale: cl_n = (7-cl_score)/6 = 0.333 constant for Tunisia
  - Civil space discrete-event adjustments per quarter (CIVIL_ADJ vector)
  - sigma_structural = sigma_s * sigma_v (product form, theoretically correct)
  - Omega_acc decay_q = 0.85^(1/4) = 0.963 per quarter
  - Normalization within precursor window (2008-Q1 to 2010-Q4)
  - 2011-Q1 excluded from normalization (expression, not precursor)

---
KEY RESULTS (unchanged from 1d -- D.4 fix does not alter phase classification)

  quarter        T_q    Omega_acc   phase
  2008-Q2       0.350    0.104     Metastable   (Gafsa peak)
  2009-Q1       0.350    0.299     Metastable   (post-Gafsa, recession)
  2009-Q4       0.372    0.612     Metastable   (post-election crackdown)
  2010-Q1       0.445    0.686     Pre-Critical (Omega_acc gate fires)
  2010-Q2       0.517    0.772     Pre-Critical (Sidi Bouzid protests)
  2010-Q3       0.589    0.867     Pre-Critical
  2010-Q4       0.673    1.000     CRITICAL     (WikiLeaks Nov 28; Bouazizi Dec 17)
  2011-Q1       1.000    1.499     [expression -- disregarded as precursor]

PRIMARY FINDING: Tunisia was Pre-Critical from 2010-Q1 and Critical in 2010-Q4,
detectable before the Bouazizi cascade. Unchanged from sortie 1d.

---
NOTE ON ANNUAL OUTPUTS IN THIS FOLDER

OUTPUTS/1e/ also contains annual pipeline outputs generated as a byproduct of
applying the audit infrastructure fixes (alpha formula, EH_proximity denominator,
OA_mismatch label, Gini PI_z fallback) to transform.py. Those are audit-corrected
versions of the 1a/1c annual figures and are included for completeness, but the
primary sortie 1e analysis is the quarterly panel above.
