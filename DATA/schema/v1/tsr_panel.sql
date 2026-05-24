-- TSR-1G Main State Panel
-- One row per observation period. All TSR state variables normalized [0,1]
-- unless noted. Raw indicator columns preserved for traceability.
-- Schema version: 1  Date: 2026-05-24

CREATE TABLE IF NOT EXISTS tsr_panel (

    -- -------------------------------------------------------------------------
    -- Temporal index
    -- -------------------------------------------------------------------------
    obs_id              TEXT PRIMARY KEY,  -- e.g. "TUN-1990", "TUN-2008-Q3", "TUN-2010-12-17"
    case_id             TEXT NOT NULL,     -- e.g. "TUNISIA"
    date_start          TEXT NOT NULL,     -- ISO 8601: YYYY-MM-DD
    date_end            TEXT NOT NULL,
    period_label        TEXT NOT NULL,     -- human label: "2008-Q3", "Dec 17 2010"
    resolution          TEXT NOT NULL,     -- annual / quarterly / monthly / weekly / daily
    period_notes        TEXT,              -- key historical context for this row

    -- -------------------------------------------------------------------------
    -- Social spacetime position proxies
    -- -------------------------------------------------------------------------
    x1_E_prime_proxy            REAL,  -- real economic position, normalized [0,1]
    x1_E_double_prime_proxy     REAL,  -- intangible positional value proxy [0,1]
                                       -- = grad_unemployment / total_unemployment
                                       -- high = educated-but-excluded: high E", low E'
    x1_regional_disparity       REAL,  -- coastal/interior income ratio (raw, not normalized)
    x2_sol_position             REAL,  -- Political Sol ideological position [-1,+1]
    x2_pop_centroid             REAL,  -- population ideological centroid [-1,+1]
    x3_sol_position             REAL,  -- Political Sol cultural position [-1,+1]
    x3_pop_centroid             REAL,  -- population cultural centroid [-1,+1]
    x3_conformity_level         REAL,  -- conformity proxy [0,1]
    x3_iconoclast_share         REAL,  -- dissent density [0,1]

    -- -------------------------------------------------------------------------
    -- Core TSR state vector  X(t) = [C,T,Psi,H,Q,K,D,L,P,E,R,Theta,S,E_m,CS]
    -- All [0,1]
    -- -------------------------------------------------------------------------
    C_cohesion          REAL,  -- binding strength composite
    T_tension           REAL,  -- stress field composite
    Psi_coherence       REAL,  -- narrative coherence
    Psi_div             REAL,  -- narrative divergence (variance across groups)
    H_inertia           REAL,  -- historical inertia
    Q_coupling          REAL,  -- configuration-manifold coupling quality
    K_absorption        REAL,  -- shock absorption capacity
    D_dissipation       REAL,  -- dissipation capacity
    L_legitimacy        REAL,  -- legitimacy reserve
    P_centralization    REAL,  -- political centralization
    E_economic_stress   REAL,  -- economic stress load
    R_repression        REAL,  -- repression intensity
    Theta_social_temp   REAL,  -- population-weighted social temperature
    Theta_elite         REAL,  -- social temperature of inner orbit subpopulation
    Theta_majority      REAL,  -- social temperature of outer orbit / mass subpopulation
    S_entropy           REAL,  -- social entropy
    E_m_maintenance     REAL,  -- maintenance energy fraction of total throughput
    CS_config_space     REAL,  -- configuration space magnitude (normalized to baseline)

    -- -------------------------------------------------------------------------
    -- Derived hazard indicators
    -- -------------------------------------------------------------------------
    MDI_star            REAL,  -- mass disruption index composite [0,1]
    delta_tau           REAL,  -- social proper time compression [0,1]; low = compressed
    EH_proximity        REAL,  -- event horizon proximity = d|CS|/dt / dConstraintCapacity/dt
    TG_hazard           REAL,  -- temperature gradient hazard = (Theta_maj - Theta_elite) * p_maj
    OA_mismatch         REAL,  -- omega-accessibility mismatch: stress where resolution is lowest
    regime_phase        TEXT,  -- Stable / Metastable / Pre-Critical / Critical / Post-Transition

    -- -------------------------------------------------------------------------
    -- CODA interaction fields  [0,1]
    -- -------------------------------------------------------------------------
    CODA_C_conn         REAL,  -- connection: network density, coordination capacity
    CODA_O_ord          REAL,  -- order: institutional strength within jurisdiction
    CODA_D_dom          REAL,  -- dominion: centralized power projection
    CODA_A_aut          REAL,  -- autonomy: individual/local agency
    CODA_imbalance      REAL,  -- composite imbalance index [0,1]

    -- -------------------------------------------------------------------------
    -- Trust-Threat in x2-x3 plane
    -- -------------------------------------------------------------------------
    alpha_degrees               REAL,  -- angular separation: Sol vs population centroid [0,180]
    T_prime_system              REAL,  -- weighted system trust = cos^2(alpha/2)  [0,1]
    T_double_prime_system       REAL,  -- weighted system threat = sin^2(alpha/2) [0,1]
    T_prime_inner_orbit         REAL,  -- trust of inner orbit (elite)
    T_prime_outer_orbit         REAL,  -- trust of outer orbit (mass)
    T_prime_interior_region     REAL,  -- trust of interior/peripheral regions specifically

    -- -------------------------------------------------------------------------
    -- Polydispersity indices (x1 — economic axis)
    -- Computed from tsr_distributions; stored here for fast panel queries
    -- -------------------------------------------------------------------------
    PI_n_x1             REAL,  -- number-average: arithmetic mean of s_i
    PI_w_x1             REAL,  -- weight-average: second moment / first moment
    PI_z_x1             REAL,  -- z-average: third moment / second moment
    PIw_PIn_ratio       REAL,  -- primary stratification index
    PIz_PIw_ratio       REAL,  -- ultra-elite concentration index
    regional_PI_ratio   REAL,  -- coastal blob vs interior blob polydispersity

    -- -------------------------------------------------------------------------
    -- Raw economic indicators (for traceability and recalibration)
    -- -------------------------------------------------------------------------
    gdp_pc_usd                  REAL,
    gdp_growth_rate             REAL,
    unemployment_rate           REAL,
    youth_unemployment_rate     REAL,
    graduate_unemployment_rate  REAL,
    gini_coefficient            REAL,
    top_10pct_income_share      REAL,
    bottom_40pct_income_share   REAL,
    income_share_q1             REAL,
    income_share_q2             REAL,
    income_share_q3             REAL,
    income_share_q4             REAL,
    income_share_q5             REAL,
    poverty_headcount_pct       REAL,
    food_price_index            REAL,
    inflation_cpi               REAL,
    hh_debt_to_income           REAL,
    informal_labor_pct          REAL,
    coastal_gdp_share           REAL,
    interior_unemployment_rate  REAL,
    remittances_pct_gdp         REAL,
    fdi_net_pct_gdp             REAL,
    tourism_revenue_pct_gdp     REAL,

    -- -------------------------------------------------------------------------
    -- Raw fiscal / institutional indicators
    -- -------------------------------------------------------------------------
    govt_social_spending_pct_gdp    REAL,
    govt_education_spending_pct_gdp REAL,
    govt_health_spending_pct_gdp    REAL,
    military_police_spending_pct_gdp REAL,
    public_employment_pct           REAL,
    corruption_cpi_score            REAL,

    -- -------------------------------------------------------------------------
    -- Raw political / civil liberties indicators
    -- -------------------------------------------------------------------------
    freedom_house_political_rights  INTEGER,  -- 1 (best) to 7 (worst)
    freedom_house_civil_liberties   INTEGER,  -- 1 (best) to 7 (worst)
    polity5_score                   INTEGER,  -- -10 to +10
    vdem_liberal_democracy_index    REAL,
    press_freedom_score_rsf         REAL,
    political_prisoner_estimate     INTEGER,
    protest_events_count            INTEGER,
    repression_events_count         INTEGER,

    -- -------------------------------------------------------------------------
    -- Raw connectivity / civil society indicators
    -- -------------------------------------------------------------------------
    internet_penetration_pct        REAL,
    mobile_penetration_pct          REAL,
    ngo_count_registered            INTEGER,
    trade_union_membership_pct      REAL,

    -- -------------------------------------------------------------------------
    -- Survey-based indicators (Arab Barometer; interpolated between waves)
    -- -------------------------------------------------------------------------
    arab_barometer_trust_govt           REAL,  -- [0,1]
    arab_barometer_econ_satisfaction    REAL,  -- [0,1]
    arab_barometer_regime_legitimacy    REAL,  -- [0,1]
    arab_barometer_religious_identity   REAL,  -- [0,1]; higher = stronger religious identity
    arab_barometer_wave                 TEXT,  -- which wave or "interpolated"

    -- -------------------------------------------------------------------------
    -- Data quality flags
    -- -------------------------------------------------------------------------
    data_confidence     TEXT,  -- high / medium / low / estimated
    interpolated        INTEGER DEFAULT 0,  -- 1 if this row was interpolated
    proxy_notes         TEXT   -- which specific variables were proxied or estimated
);
