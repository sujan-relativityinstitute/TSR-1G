Tunisia TSR-1G Analysis Sortie 1e
Date: 2026-05-27

Analysis: Annual structural panel -- Tunisia 1990-2011 (corrected).
Baseline: Sortie 1c (Omega_latent) with six mathematical corrections from audit.

---
CORRECTIONS FROM AUDIT

D.1 -- Alpha formula (HIGH severity)
  Previous: dist = sqrt((SOL_X2-x2_pop)^2 + (SOL_X3-x3_pop)^2)
            alpha = (dist / max_dist) * 180
  This is Euclidean distance scaled linearly to degrees -- not angular separation.
  For small separations the approximation is close; for large separations it diverges.

  Corrected: alpha = arccos( (Sol . Pop) / (|Sol| * |Pop|) )
  where Sol = (SOL_X2, SOL_X3) and Pop = (x2_pop_centroid, x3_pop_centroid)
  are position vectors from the origin in the x2-x3 plane (Section 5.9).
  This is the standard definition of angular separation between two vectors.

D.2 -- EH_proximity denominator (HIGH severity)
  Previous: dCS / K  (rate divided by level -- dimensionally inconsistent)
  Corrected: dCS / dK  (rate divided by rate, per Section 16A.12)
  When dK <= 0 (constraint capacity not growing while CS expands), EH_proximity
  is set to 3.0 (maximum). When dCS = 0, EH_proximity = 0.

D.3 -- OA_mismatch (MEDIUM severity -- label only, no formula change)
  Section 33 defines OA_mismatch as a spatial field correlation:
  Omega(x1,x2,x3,t) correlated with 1/E_acc(x1,x2,x3,t).
  The code implements a scalar approximation (T_tension * (1 - D_dissipation)).
  Correct direction but loses all spatial information. Explicitly labelled as
  scalar approximation pending sub-group distributional data.

D.4 -- Repression double-counting (MEDIUM severity)
  repression_n previously entered through three independent paths simultaneously:
    - T_tension (weight 0.20) -- Section 35.2 routes R -> T at t+1, not same period
    - sigma_valve (weight 0.50) -- correct mechanism for latent energy accumulation
    - R_repression (weight 0.50 + political/civil components)
  The same raw signal then arrived at MDI* through T_tension AND R_repression.
  Corrected: repression removed from T_tension. Weights redistributed:
    1c: {"youth_unemp": 0.35, "gini": 0.30, "repression": 0.20, "protest": 0.15}
    1e: {"youth_unemp": 0.45, "gini": 0.40, "protest": 0.15}
  T_tension is now a purely economic/distributional + protest expression proxy.
  Repression routes only through sigma_valve and R_repression.

D.5 -- Gini PI fallback (MEDIUM severity)
  Previous: PI_z_x1 ≈ 1 + 4*Gini (no derivation from moment ratio definitions)
  PI_z is tail-sensitive; Gini averages over the tail. The approximation is unreliable.
  Corrected: PI_z_x1 = NaN when quintile data is unavailable. PI_gini_fallback flag
  column added so downstream consumers can filter. PI_w_x1 ≈ 1 + 2*Gini retained
  (rough linear approximation documented in inequality literature).

D.6 -- Orbital T' hardcoded offsets (LOW severity)
  Previous: T_prime_inner_orbit = cos^2(10/2) -- hardcoded, not derived
            alpha_outer = (dist + 0.3) / max_dist * 180 -- arbitrary Euclidean offset
            alpha_interior = (dist + 0.5) / max_dist * 180 -- same problem
  Corrected: Inner orbit calibrated at 15 degrees angular separation from Sol.
             Outer orbit = pop centroid alpha + 20 degrees.
             Interior = pop centroid alpha + 35 degrees.
  All offsets are now geometrically principled angular divergences, not Euclidean
  distance offsets. Values (15, 20, 35) are calibration; the form is correct.

---
POSITIVE GAPS NOTED (no formula change -- formalization only)

B.1 -- Omega_latent product form (Omega_latent_inst = sigma_structural * sigma_valve)
  Confirmed as theoretically correct. To be formalized in context file as canonical
  form for the latent energy mechanism (Section 33 does not write it explicitly).

B.2 -- Discharge triple product (protest_n * (1 - repression_n) * cl_n)
  Confirmed as theoretically correct. Follows from Section 14 dissipation channel
  definitions. To be formalized in context file.

B.3 -- sigma_structural / sigma_valve slot assignment
  Slot 1-4 (economic/material) feed sigma_structural; Slots 5,6,8 feed sigma_valve.
  Separation is theoretically grounded in the structural stress / suppression
  distinction. To be formalized in context file.

---
REGIME PHASES (1e corrected annual panel)

  1990-1992: Stable
  1993:      Metastable
  1994:      Stable
  1995:      Metastable
  1996-1998: Metastable
  1999:      Stable
  2000:      Metastable
  2001-2003: Stable
  2004:      Metastable
  2005-2010: Stable   (2010 still Stable at annual resolution -- documented limitation)
  2011:      Pre-Critical

NOTE: 2010 Stable classification at annual resolution is a known limitation.
Quarterly analysis (Sortie 1d) correctly identifies 2010-Q1 as Pre-Critical and
2010-Q4 as Critical. The annual panel averages the Q4 spike across the full year,
suppressing the signal. This is a resolution problem, not a model failure.

---
Outputs:
  1e Tunisia_Regime_Phase_Trajectory.png  -- 4-panel annual figure (corrected)
  1e Tunisia_Omega_Latent.png             -- 3-panel Omega_latent figure (corrected)
  1e Tunisia_annual_panel.csv             -- 22 rows, corrected TSR state vector
  1e Tunisia_obs_panel.csv                -- 43 observation rows
