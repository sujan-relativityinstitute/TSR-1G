-- TSR-1G Proxy Map
-- Static reference table documenting how raw indicators map to TSR constructs.
-- One row per variable. Update this table whenever a proxy assumption changes,
-- then record the decision in DATA/schema/CHANGELOG.md.
-- Schema version: 1  Date: 2026-05-24

CREATE TABLE IF NOT EXISTS tsr_proxy_map (

    proxy_id            TEXT PRIMARY KEY,   -- e.g. "C_cohesion", "x1_E_double_prime_proxy"
    tsr_variable        TEXT NOT NULL,      -- column name in tsr_panel or tsr_distributions
    tsr_construct       TEXT NOT NULL,      -- TSR-1G construct name (exact notation)
    context_section     TEXT,              -- Master Context File section(s): e.g. "7.1", "16A.1"

    -- -------------------------------------------------------------------------
    -- Proxy definition
    -- -------------------------------------------------------------------------
    proxy_description   TEXT NOT NULL,     -- what raw data is used and how
    raw_columns         TEXT,              -- comma-separated raw column names used
    normalization_method TEXT,             -- formula or description
    inversion_required  INTEGER DEFAULT 0, -- 1 if high raw value = low TSR value (e.g. Freedom House)

    -- -------------------------------------------------------------------------
    -- Data source
    -- -------------------------------------------------------------------------
    primary_source      TEXT,   -- e.g. "World Bank Open Data", "Arab Barometer Wave 1"
    source_indicator    TEXT,   -- specific indicator code, e.g. "SI.POV.GINI"
    source_url          TEXT,
    secondary_source    TEXT,   -- fallback or supplementary source
    update_frequency    TEXT,   -- annual / quarterly / survey_wave / event-based

    -- -------------------------------------------------------------------------
    -- Quality and limitations
    -- -------------------------------------------------------------------------
    confidence_level    TEXT,   -- high / medium / low
    known_limitations   TEXT,   -- specific weaknesses of this proxy for this case
    pre_2006_coverage   TEXT,   -- available / interpolated / unavailable / estimated
    notes               TEXT
);

-- -------------------------------------------------------------------------
-- Seed data: v1 proxy definitions
-- -------------------------------------------------------------------------

INSERT INTO tsr_proxy_map VALUES
('x1_E_prime_proxy', 'x1_E_prime_proxy', 'E'' (real economic value)', '5.2',
 'GDP per capita USD, normalized to [0,1] over full time series range',
 'gdp_pc_usd', '(value - min) / (max - min)', 0,
 'World Bank Open Data', 'NY.GDP.PCAP.CD', 'data.worldbank.org', 'IMF WEO', 'annual',
 'medium', 'Ben Ali era GDP likely overstated; treat 1990-2010 as confidence=medium', 'available', NULL),

('x1_E_double_prime_proxy', 'x1_E_double_prime_proxy', 'E" (intangible positional value)', '5.2',
 'Graduate unemployment rate / total unemployment rate. High ratio = educated-but-excluded: high E", low E''. '
 'Captures E''/E" divergence — the key crisis precursor on x1.',
 'graduate_unemployment_rate, unemployment_rate', 'graduate_unemployment_rate / unemployment_rate, then normalize',
 0, 'ILO ILOSTAT', 'UNE_2EAP_SEX_AGE_EDU_RT_A', 'ilostat.ilo.org', 'INS Tunisia', 'annual',
 'low', 'Graduate unemployment data sparse pre-2000; estimate from academic sources', 'interpolated', NULL),

('C_cohesion', 'C_cohesion', 'Cohesion* (C)', '7.1',
 'Composite: inverted political repression + institutional quality + trust surveys + elite coherence proxy. '
 'Weighted average of normalized sub-indicators.',
 'arab_barometer_trust_govt, corruption_cpi_score, freedom_house_civil_liberties, vdem_liberal_democracy_index',
 'weighted mean of normalized sub-indicators; weights: trust=0.35, corruption=0.25, civil_lib=0.20, vdem=0.20',
 0, 'Arab Barometer + TI + Freedom House + V-Dem', NULL, NULL, NULL, 'mixed',
 'medium', 'Trust surveys unavailable pre-2006; backfill from CPI and Freedom House only', 'partial', NULL),

('T_tension', 'T_tension', 'Tension* (T)', '7.2',
 'Composite: youth unemployment + Gini + repression events + protest events + Q_mismatch proxy.',
 'youth_unemployment_rate, gini_coefficient, repression_events_count, protest_events_count',
 'normalized weighted sum; weights: youth_unemp=0.30, gini=0.25, repression=0.25, protest=0.20',
 0, 'World Bank + ACLED + Freedom House', NULL, NULL, NULL, 'mixed',
 'medium', 'ACLED protest data sparser pre-2000; supplement with academic event counts', 'partial', NULL),

('Theta_social_temp', 'Theta_social_temp', 'Social Temperature (Theta)', '16A.1',
 'Population-weighted composite of economic precarity signals: food price burden, unemployment, '
 'informal labor share, poverty headcount. Higher = hotter.',
 'food_price_index, unemployment_rate, informal_labor_pct, poverty_headcount_pct',
 'normalized weighted mean; weights: food=0.30, unemployment=0.30, informal=0.20, poverty=0.20',
 0, 'FAO + World Bank + ILO', NULL, NULL, NULL, 'annual',
 'medium', 'Household-level precarity data limited; food price index is best continuous proxy', 'available', NULL),

('E_m_maintenance', 'E_m_maintenance', 'Maintenance Energy (E_m)', '16A.2',
 'Government social + education + health spending as % GDP. Proxy for fraction of total energy '
 'directed toward sustaining low-entropy configurations.',
 'govt_social_spending_pct_gdp, govt_education_spending_pct_gdp, govt_health_spending_pct_gdp',
 'sum of three spending shares, normalized to [0,1] over time series',
 0, 'World Bank + IMF Article IV', 'GC.XPN.EDUC.GD.ZS etc.', 'data.worldbank.org', 'IMF WEO', 'annual',
 'medium', 'Ben Ali era spending data may be distorted; cross-check with IMF Article IV reports', 'available', NULL),

('CODA_C_conn', 'CODA_C_conn', 'Connection (C_conn)', '6',
 'Composite: internet penetration + mobile penetration + NGO density + trade union membership. '
 'Captures long-range social linkage and network density.',
 'internet_penetration_pct, mobile_penetration_pct, ngo_count_registered, trade_union_membership_pct',
 'normalized weighted mean; weights: internet=0.35, mobile=0.25, ngo=0.25, union=0.15',
 0, 'ITU + V-Dem + ILO', 'IT.NET.USER.ZS', 'data.worldbank.org', NULL, 'annual',
 'medium', 'Digital connectivity transformation 2005-2010 is critical transition; capture quarterly if possible', 'available', NULL),

('CODA_O_ord', 'CODA_O_ord', 'Order (O_ord)', '6',
 'Composite: rule of law + judicial independence + regulatory quality. Short-to-medium range; '
 'captures institutional binding strength within jurisdiction.',
 'corruption_cpi_score, vdem_liberal_democracy_index, polity5_score',
 'normalized weighted mean; polity5 mapped from [-10,+10] to [0,1]',
 0, 'V-Dem + Transparency International + Polity5', NULL, NULL, NULL, 'annual',
 'medium', NULL, 'available', NULL),

('CODA_D_dom', 'CODA_D_dom', 'Dominion (D_dom)', '6',
 'Composite: military + police spending as % GDP + repression event density + political centralization (Polity). '
 'Captures coercive power projection from center.',
 'military_police_spending_pct_gdp, repression_events_count, polity5_score',
 'normalized weighted mean; polity5 inverted for this construct (more autocratic = higher D)',
 0, 'SIPRI + ACLED + Polity5', NULL, NULL, NULL, 'annual',
 'medium', 'Ben Ali family business control (D_dom through economic channel) requires academic sources', 'available', NULL),

('CODA_A_aut', 'CODA_A_aut', 'Autonomy (A_aut)', '6',
 'Composite: press freedom + freedom of assembly + protest events (as expression of autonomy, not just tension). '
 'Captures individual and local agency space.',
 'press_freedom_score_rsf, freedom_house_civil_liberties, protest_events_count',
 'normalized weighted mean; civil liberties inverted (1=best→1.0, 7=worst→0.0)',
 0, 'RSF + Freedom House + ACLED', NULL, NULL, NULL, 'annual',
 'medium', 'RSF index only from 2002; use Freedom House pre-2002', 'partial', NULL),

('L_legitimacy', 'L_legitimacy', 'Legitimacy Reserve (L)', '7.8',
 'Arab Barometer trust in government and regime legitimacy composite. '
 'Interpolated linearly between survey waves.',
 'arab_barometer_trust_govt, arab_barometer_regime_legitimacy',
 'mean of two normalized survey scores; interpolate between Wave 1 (2006) and Wave 2 (2010)',
 0, 'Arab Barometer', NULL, 'arabbarometer.org', 'Afrobarometer', 'survey_wave',
 'low', 'Only two waves available (2006, 2010); pre-2006 must be estimated from CPI + Freedom House', 'estimated', NULL),

('alpha_degrees', 'alpha_degrees', 'Angular separation alpha in x2-x3 plane', '5.9',
 'Euclidean distance in x2-x3 plane between Political Sol position and population centroid position. '
 'alpha = sqrt((x2_sol - x2_pop)^2 + (x3_sol - x3_pop)^2) mapped to [0,180] degrees.',
 'x2_sol_position, x2_pop_centroid, x3_sol_position, x3_pop_centroid',
 'alpha_raw = sqrt((x2_sol-x2_pop)^2 + (x3_sol-x3_pop)^2); scale to [0,180] degrees',
 0, 'Derived from Polity5 + Arab Barometer', NULL, NULL, NULL, 'annual',
 'low', 'x2/x3 positions are estimated; angular separation is a modeled construct not a direct measurement', 'estimated',
 'Sol position on x2 approximated from Polity5 normalized; Sol on x3 from Islamism suppression intensity'),

('PI_n_x1', 'PI_n_x1', 'PI_n (number-average polydispersity)', '5.8.2',
 'Arithmetic mean of s_i (normalized income positions) across all population units equally weighted. '
 'Computed from tsr_distributions table.',
 'tsr_distributions.s_i_normalized, tsr_distributions.population_fraction',
 'SUM(population_fraction * s_i_normalized)', 0,
 'World Bank PIP / PovcalNet', 'SI.DST.FRST.20 etc.', 'pip.worldbank.org', 'INS Tunisia', 'annual',
 'medium', 'Requires quintile or decile income share data; interpolate years with missing data', 'available', NULL),

('PI_w_x1', 'PI_w_x1', 'PI_w (weight-average polydispersity)', '5.8.3',
 'Ratio of second moment to first moment of weighted income distribution. '
 'Sensitive to elite tail. Computed from tsr_distributions.',
 'tsr_distributions.w_i, tsr_distributions.s_i_normalized',
 'SUM(w_i * s_i^2) / SUM(w_i * s_i)', 0,
 'World Bank PIP / PovcalNet', NULL, NULL, 'INS Tunisia', 'annual',
 'medium', 'w_i = income share; requires consistent weighting across years', 'available', NULL),

('PI_z_x1', 'PI_z_x1', 'PI_z (z-average polydispersity)', '5.8.4',
 'Ratio of third moment to second moment. Sensitive to ultra-elite concentration. '
 'Computed from tsr_distributions.',
 'tsr_distributions.w_i, tsr_distributions.s_i_normalized',
 'SUM(w_i * s_i^3) / SUM(w_i * s_i^2)', 0,
 'World Bank PIP + academic sources on Ben Ali wealth', NULL, NULL, 'INS Tunisia', 'annual',
 'low', 'Very top tail (Ben Ali family ~20-30% GDP) not captured in standard quintile data; '
 'supplement with academic estimates', 'estimated', NULL),

('Psi_div', 'Psi_div', 'Narrative Divergence (Psi_div)', '8',
 'Variance of narrative alignment across groups. Proxy: variance in Arab Barometer trust scores '
 'across sub-groups + GDELT media tone divergence + press freedom erosion trend.',
 'arab_barometer_trust_govt, press_freedom_score_rsf',
 'std(trust_scores_across_groups) + normalized(1 - press_freedom_score); combine with equal weights',
 0, 'Arab Barometer + GDELT + RSF', NULL, NULL, NULL, 'mixed',
 'low', 'Sub-group variance in Arab Barometer limited by sample sizes; '
 'pre-2006 proxied from media environment only', 'estimated', NULL);
