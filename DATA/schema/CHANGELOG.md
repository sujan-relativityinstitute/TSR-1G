# TSR-1G Dataset Schema Changelog

## v1 — 2026-05-24

Initial schema design for Tunisia Arab Spring case study (1990-2011).

### Tables introduced
- `tsr_panel` — main state panel, one row per observation period
- `tsr_distributions` — decile/group distributional data for polydispersity computation
- `tsr_inforay_events` — discrete information events with full interaction properties
- `tsr_shock_events` — discrete exogenous shocks mapped to state vector components
- `tsr_proxy_map` — static reference documenting how raw indicators map to TSR constructs

### Design decisions recorded
- Observation schedule is event-anchored, not calendar-anchored (see CASES/Tunisia/observation_schedule.md)
- All TSR state variables normalized [0,1] except x2, x3 ([-1,+1]) and Polity5 ([-10,+10])
- Polydispersity indices computed from tsr_distributions, not stored as raw inputs in tsr_panel
- T'T" trust-threat values derived from alpha angle; alpha estimated from x2-x3 positions
- E" (intangible positional value) proxied as graduate_unemployment / total_unemployment ratio
- SQLite-compatible DDL; no foreign key enforcement by default (enable with PRAGMA foreign_keys=ON)

### Known gaps at v1
- Pre-2006 survey data (Arab Barometer not available before Wave 1 2006): interpolate from academic sources
- Governorate-level economic data for interior/coastal split: requires INS Tunisia reports
- Ben Ali era official statistics likely overstated GDP growth: flag rows 1990-2010 as confidence=medium
- x3 (cultural/conformity axis) pre-2006: proxy-heavy, confidence=low
