-- TSR-1G Inforay Events
-- Discrete information events with full TSR interaction properties.
-- Each row is a specific event that struck the Mass surface.
-- See Master Context File Section 8A for construct definitions.
-- Schema version: 1  Date: 2026-05-24

CREATE TABLE IF NOT EXISTS tsr_inforay_events (

    event_id            TEXT PRIMARY KEY,  -- e.g. "TUN-BOUAZIZI-20101217"
    case_id             TEXT NOT NULL,
    obs_id              TEXT REFERENCES tsr_panel(obs_id),  -- nearest panel period
    date                TEXT NOT NULL,     -- ISO 8601

    event_name          TEXT NOT NULL,     -- e.g. "Bouazizi self-immolation"
    event_description   TEXT,

    -- -------------------------------------------------------------------------
    -- Origin position in social spacetime
    -- -------------------------------------------------------------------------
    origin_x1           REAL,   -- economic position of origin [0,1]
    origin_x2           REAL,   -- ideological position [-1,+1]
    origin_x3           REAL,   -- cultural position [-1,+1]
    origin_orbital_r    REAL,   -- orbital radius of origin from Political Sol [0,1]
    origin_type         TEXT,   -- government / dissident / media / international / social_media / spontaneous

    -- -------------------------------------------------------------------------
    -- Content vector (axis loading)
    -- -------------------------------------------------------------------------
    content_v1          REAL,   -- x1 loading: economic content [0,1]
    content_v2          REAL,   -- x2 loading: political content [0,1]
    content_v3          REAL,   -- x3 loading: cultural/identity content [0,1]
    multi_axis          INTEGER,-- 1 if high loading on 2+ axes simultaneously (key for symbolic criticality)

    -- -------------------------------------------------------------------------
    -- Inforay properties
    -- -------------------------------------------------------------------------
    intensity           REAL,   -- signal amplitude [0,1]
    q_n                 REAL,   -- narrative charge [-1 fully dissonant, +1 fully consonant]
                                -- relative to dominant Psi at time of event
    T_prime_toward_origin  REAL,  -- trust toward origin at point of contact
    T_double_prime_toward_origin REAL,

    -- -------------------------------------------------------------------------
    -- Interaction outcome (Section 8A.5)
    -- -------------------------------------------------------------------------
    interaction_mode    TEXT,   -- constructive / rejection / distortive / amplification / scattering
    G_stored            REAL,   -- stored Omega amplification factor (1 = normal, >1 = Mode 4)
    alpha_total         REAL,   -- composite coupling coefficient [0,1]
    E_dep_estimate      REAL,   -- estimated energy deposited (relative units, same scale as Omega)
    phi_delta           REAL,   -- change in Phi (cohesion field): positive = binding
    omega_delta         REAL,   -- change in Omega (stress field): positive = stress
    psi_div_delta       REAL,   -- change in narrative divergence: positive = more fragmented

    -- -------------------------------------------------------------------------
    -- Symbolic criticality (Section 8A.9)
    -- -------------------------------------------------------------------------
    symbolic_criticality    REAL,   -- SC estimate [0,1]
    propagation_reach       REAL,   -- estimated fraction of Mass volume reached [0,1]
    narrative_sync_trigger  INTEGER,-- 1 if this event triggered system-wide narrative synchronization

    -- -------------------------------------------------------------------------
    -- Regime response (Section 8A.8)
    -- -------------------------------------------------------------------------
    regime_response         TEXT,   -- none / concession / repression / symbolic
    regime_response_date    TEXT,
    regime_response_T_prime REAL,   -- trust toward regime response at time of response
    regime_response_mode    TEXT,   -- how the response was received: constructive / distortive / backfire

    -- -------------------------------------------------------------------------
    -- Systemic effect
    -- -------------------------------------------------------------------------
    systemic_outcome        TEXT,   -- local / regional / national / international_cascade
    delta_tau_effect        REAL,   -- estimated compression of social proper time from event

    -- -------------------------------------------------------------------------
    -- Data quality
    -- -------------------------------------------------------------------------
    data_source             TEXT,   -- citation or reference
    coding_confidence       TEXT,   -- high / medium / low
    coding_notes            TEXT
);
