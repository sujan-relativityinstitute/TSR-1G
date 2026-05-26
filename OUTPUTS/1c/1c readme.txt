Tunisia TSR-1G Analysis Sortie 1c
Date: 2026-05-25

Analysis: Omega_latent -- stored social potential energy under sustained repression.

Motivation:
The 1a classifier reads 2010 as Stable because T_tension (the kinetic proxy) fell when
repression suppressed ACLED protest events. But the structural stress was not falling --
it was accumulating as stored potential energy that could not discharge through the closed
valve of repression. This is the supercooling problem: the system appears stable because
it is not moving, but its stored free energy is high and rising.

New construct -- derived from the 9 structural input slots, no new variables introduced:

  sigma_structural (Slots 1, 2, 3, 4 -- repression-independent loading):
    0.40 x youth_unemp_n    Slot 3: frustrated positional gradient (E"/E')
    0.30 x gini_n           Slot 1: distributional stress
    0.20 x food_n           Slot 4: material stress / social temperature
    0.10 x (1 - gdp_pc_n)  Slot 2: economic level stress (inverted)

  sigma_valve (Slots 5, 6, 8 -- suppression closure factor):
    0.50 x repression_n     Slot 8: active force application
    0.30 x (1 - cl_n)       Slot 6: civil space closure
    0.20 x (1 - pr_n)       Slot 5: political space closure

  Omega_latent_inst = sigma_structural x sigma_valve
    Product form: latent energy requires both pressure AND closure simultaneously.
    A closed valve on a relaxed system stores nothing. Open valve discharges immediately.

  Omega_acc(t) = decay x Omega_acc(t-1) + Omega_latent_inst(t) x (1 - discharge(t))
    discharge(t) = protest_n x (1 - repression_n) x cl_n
    decay = 0.85 (calibration value -- to be derived from field equations, Section 35.2)

  Slot 9 (information conductivity) not in Omega_latent. It governs propagation speed
  when the valve opens -- it explains why 2010 converted and 2008 did not, but it does
  not add to stored pressure.

Theoretical grounding:
  Omega_accumulated is a specific realization of H (Historical Inertia) applied to the
  tension field. H is currently NaN pending Section 35.2 field equations. This derivation
  shows what H looks like for the Ω field under persistent suppression, without requiring
  the full field equations.

  The decay parameter should eventually be derived from first principles (Section 35.2).
  For now it is a calibration value, constrained by: 2008 Gafsa and 2010 must both show
  high Omega_acc; only 2010 converted (difference is Slot 9 + multi_axis nucleation event,
  not Omega_acc itself).

Outputs:
  [To be filled after computation]
