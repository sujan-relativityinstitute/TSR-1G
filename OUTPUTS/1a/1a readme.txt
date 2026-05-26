Tunisia TSR-1G Analysis Sortie 1a
Date: 2026-05-24

Analysis: Initial Tunisia pipeline (1990-2011) -- post-audit baseline.

Changes from prior state:
- Audit fixes A-F: removed placeholder constants and derived pseudo-inputs from
  compute_tsr_variables(). All inputs now map strictly to the 9 declared structural slots.
- WEIGHTS dict in config.py cleaned: renormalized all blocks, removed non-slot keys
  (trust, informal, ngo, union, vdem, press_freedom, social).
- Added dT_tension: signed annual derivative of T_tension. T viewed as a process,
  not a new metric -- consistent with GR simplicity principle (Section 2A).
- Added dT gate to _classify_phase(): catches Metastable years where tension is rising
  faster than MDI* threshold would detect alone.
- Recalibrated Pre-Critical MDI* threshold: 0.55 -> 0.50. Driven by change in MDI*
  distribution after removing placeholder inputs. 2011 MDI* = 0.537.
- 4-panel regime trajectory figure: MDI*/C/T (Panel A), CODA forces (Panel B),
  observable drivers (Panel C), phase classification strip (Panel D).

Phase classification results (1990-2011):
  1995 -- Metastable  (dT = +0.135, IMF SAP structural adjustment peak)
  2004 -- Metastable  (dT = +0.094, Ben Ali political consolidation)
  2009 -- Metastable  (dT = +0.198, post-Gafsa economic accumulation)
  2011 -- Pre-Critical (MDI* = 0.537)
  All other years -- Stable

Known limitation: 2010 classified as Stable. Repression suppressed ACLED protest proxy,
causing dT = -0.149 despite high structural loading. Documented in _classify_phase()
docstring in MODELS/ingestion/transform.py.

Outputs:
  Tunisia_Regime_Phase_Trajectory.png  -- 4-panel figure
  Tunisia_annual_panel.csv             -- 22 rows x 80 cols, annual TSR state vector
  Tunisia_obs_panel.csv                -- 43 rows x 85 cols, observation schedule
