Tunisia TSR-1G Analysis Sortie 1b
Date: 2026-05-24

Analysis: Type 2 event log -- 12 hand-coded inforay events, Tunisia 1992-2011.

Changes from 1a:
- Built CASES/Tunisia/event_log.py: 12 events organized in three tiers.
    Tier 1 -- Structural loading   (6 events, 1992-2008, 16 years)
    Tier 2 -- Pre-conditioning     (1 event,  Nov 2010)
    Tier 3 -- Cascade              (5 events, Dec 17 2010 - Jan 14 2011, 28 days)
- Pipeline step 8 added: event_log.write_to_db() loads events into SQLite as
  tsr_inforay_events table (12 rows).
- Built CASES/Tunisia/plot_event_log.py: 3-panel event log visualization.
    Panel A -- Symbolic criticality timeline (bubble size = propagation reach,
               colour = interaction mode, star = narrative sync trigger)
    Panel B -- omega_delta per event + cumulative Omega loading line
    Panel C -- G_stored (stored amplification factor) per event

Key theoretical results:
  Gafsa (2008) vs Bouazizi (2010) contrast -- same stored Omega (~0.60), opposite outcomes:
    Gafsa:    SC=0.30, reach=0.15, multi_axis=0, G_stored=2.5x -- scattering, local containment
    Bouazizi: SC=0.97, reach=0.85, multi_axis=1, G_stored=8.0x -- amplification, national cascade
  The difference is explained entirely by multi_axis loading and Slot 9 conductivity (internet
  penetration 2008 vs 2010) -- no post-hoc parameter adjustment needed.

  Narrative sync triggered on 4 events:
    WikiLeaks Cablegate (Nov 2010), Bouazizi self-immolation (Dec 17),
    Sidi Bouzid protests (Dec 19), Ben Ali flees (Jan 14 2011).

  Political Singularity: Ben Ali flees Jan 14 2011. G_stored=10.0x.

Outputs:
  Tunisia_Inforay_Event_Log.png  -- 3-panel figure
