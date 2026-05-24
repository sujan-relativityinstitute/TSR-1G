-- TSR-1G Group/Decile Distributions
-- Stores distributional data for polydispersity index computation.
-- One row per group per observation period.
-- PI_n, PI_w, PI_z are computed from these rows, then written to tsr_panel.
-- Schema version: 1  Date: 2026-05-24

CREATE TABLE IF NOT EXISTS tsr_distributions (

    dist_id             TEXT PRIMARY KEY,  -- e.g. "TUN-2008-Q3-D1", "TUN-2008-Q3-coastal"
    obs_id              TEXT NOT NULL REFERENCES tsr_panel(obs_id),
    case_id             TEXT NOT NULL,

    -- -------------------------------------------------------------------------
    -- Group classification
    -- -------------------------------------------------------------------------
    group_type          TEXT NOT NULL,  -- income_decile / regional / occupational / generational
    group_label         TEXT NOT NULL,  -- e.g. "D1", "D10", "coastal", "informal_labor", "youth_15_29"
    group_notes         TEXT,

    -- -------------------------------------------------------------------------
    -- Positional values for polydispersity computation
    -- -------------------------------------------------------------------------
    population_fraction REAL NOT NULL,  -- p_i: share of total population
    s_i_raw             REAL,           -- raw positional value (income, asset, composite)
    s_i_normalized      REAL,           -- s_i normalized to [0,1] within this obs_id
    w_i                 REAL,           -- weight: economic share or influence weight
                                        -- used in PI_w and PI_z numerators

    -- -------------------------------------------------------------------------
    -- Social spacetime position of this group
    -- -------------------------------------------------------------------------
    x1_position         REAL,   -- economic position [0,1]
    x2_position         REAL,   -- ideological position [-1,+1]
    x3_position         REAL,   -- cultural position [-1,+1]

    -- -------------------------------------------------------------------------
    -- Trust-Threat for this group
    -- -------------------------------------------------------------------------
    alpha_from_sol      REAL,           -- angular distance from Political Sol [0,180 degrees]
    T_prime_group       REAL,           -- trust = cos^2(alpha/2)
    T_double_prime_group REAL,          -- threat = sin^2(alpha/2)

    -- -------------------------------------------------------------------------
    -- Thermal state of this group
    -- -------------------------------------------------------------------------
    Theta_group         REAL,           -- social temperature of this group [0,1]
    s_Theta_group       REAL,           -- s(Theta_group): entropy contribution function
                                        -- linear approximation: s(Theta) = Theta

    -- -------------------------------------------------------------------------
    -- Data quality
    -- -------------------------------------------------------------------------
    data_source         TEXT,
    data_confidence     TEXT            -- high / medium / low / estimated
);

-- View: compute polydispersity indices per obs_id
-- Run this query to produce PI_n, PI_w, PI_z for writing back to tsr_panel.
--
-- SELECT
--     obs_id,
--     SUM(population_fraction * s_i_normalized) AS PI_n,
--     SUM(w_i * s_i_normalized * s_i_normalized) / SUM(w_i * s_i_normalized) AS PI_w,
--     SUM(w_i * s_i_normalized * s_i_normalized * s_i_normalized)
--         / SUM(w_i * s_i_normalized * s_i_normalized) AS PI_z,
--     SUM(population_fraction * s_Theta_group) AS S_total
-- FROM tsr_distributions
-- GROUP BY obs_id;
