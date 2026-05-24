-- TSR-1G Shock Events
-- Discrete exogenous shocks mapped to state vector components.
-- See Master Context File Section 35.3 for the shock vector definition:
-- Shock(t) = [S_econ, S_pol, S_soc, S_ext, S_sym]
-- Schema version: 1  Date: 2026-05-24

CREATE TABLE IF NOT EXISTS tsr_shock_events (

    shock_id            TEXT PRIMARY KEY,  -- e.g. "TUN-GFC-2008", "TUN-GAFSA-2008"
    case_id             TEXT NOT NULL,
    date_start          TEXT NOT NULL,     -- ISO 8601
    date_end            TEXT,
    shock_name          TEXT NOT NULL,
    shock_description   TEXT,

    -- -------------------------------------------------------------------------
    -- Shock vector components  [0,1]
    -- -------------------------------------------------------------------------
    S_econ              REAL,  -- economic shock component
    S_pol               REAL,  -- political shock component
    S_soc               REAL,  -- social shock component
    S_ext               REAL,  -- external / exogenous shock component
    S_sym               REAL,  -- symbolic shock component
    shock_magnitude     REAL,  -- composite magnitude [0,1]
    duration_months     REAL,

    -- -------------------------------------------------------------------------
    -- State vector impact (estimated change to each variable)
    -- -------------------------------------------------------------------------
    C_delta             REAL,  -- estimated impact on Cohesion (negative = degrading)
    T_delta             REAL,  -- estimated impact on Tension (positive = increasing)
    Psi_delta           REAL,  -- estimated impact on narrative coherence
    K_delta             REAL,  -- estimated impact on shock absorption capacity
    L_delta             REAL,  -- estimated impact on legitimacy reserve
    E_delta             REAL,  -- estimated impact on economic stress
    Theta_delta         REAL,  -- estimated impact on social temperature

    -- -------------------------------------------------------------------------
    -- Affected panel periods
    -- -------------------------------------------------------------------------
    obs_id_start        TEXT REFERENCES tsr_panel(obs_id),
    obs_id_end          TEXT REFERENCES tsr_panel(obs_id),

    -- -------------------------------------------------------------------------
    -- Inforay linkage
    -- -------------------------------------------------------------------------
    triggered_inforay   TEXT REFERENCES tsr_inforay_events(event_id),
                               -- if the shock produced a key inforay event

    -- -------------------------------------------------------------------------
    -- Data quality
    -- -------------------------------------------------------------------------
    data_source         TEXT,
    coding_confidence   TEXT,  -- high / medium / low
    coding_notes        TEXT
);
