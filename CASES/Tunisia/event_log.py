"""
Tunisia TSR-1G Inforay Event Log — Type 2 inputs.

Hand-coded high-criticality events following Section 8A (Inforay Mechanics)
and Section 38A.4 (Event Log Schema).

Quantitative fields (G_stored, alpha_total, E_dep_estimate, phi_delta,
omega_delta, delta_tau_effect) are estimated from the qualitative field
analysis in CASES/Tunisia/notes.md and will be replaced by simulation
engine outputs once Section 35.2 field equations are operational.
coding_confidence reflects this distinction.

Event sequence covers three tiers:
  Tier 1 — Structural background events (1992-2008): events that loaded
            the Omega field and eroded L without triggering cascade.
  Tier 2 — Surface pre-conditioning (Nov-Dec 2010): events that transformed
            the Mass surface geometry toward maximum amplification mode.
  Tier 3 — Cascade events (Dec 17 2010 - Jan 14 2011): Mode 4 amplification
            sequence from trigger through Political Singularity.
"""

import pandas as pd
import sqlite3
from pathlib import Path

CASE_ID = "TUNISIA"

EVENTS = [

    # ─── TIER 1: Structural background events ────────────────────────────────

    {
        "event_id":           "TUN-ENNAHDA-SUPPRESS-19920523",
        "case_id":            CASE_ID,
        "obs_id":             "TUN-1992",
        "date":               "1992-05-23",
        "event_name":         "Ennahda leadership arrested and tried",
        "event_description":  (
            "Mass trials sentenced Ennahda (Islamic Tendency Movement) leaders to "
            "life imprisonment following the movement's strong 1989 electoral "
            "performance. Estimated 8,000 members imprisoned. Created a large "
            "politically active population at maximum T'' toward Sol, stored in "
            "Omega throughout the Ben Ali period."
        ),
        "origin_x1":          None,
        "origin_x2":          0.60,     # government/Political Sol origin
        "origin_x3":          0.70,
        "origin_orbital_r":   0.05,     # inner Sol orbit
        "origin_type":        "government",
        "content_v1":         0.15,
        "content_v2":         0.85,     # primarily political
        "content_v3":         0.70,     # strong religious/identity component
        "multi_axis":         1,        # high on both v2 and v3
        "intensity":          0.75,
        "q_n":                -0.50,    # dissonant with popular sense of justice
        "T_prime_toward_origin":        0.65,   # early Ben Ali — trust still partial
        "T_double_prime_toward_origin": 0.35,
        "interaction_mode":   "rejection",      # Islamist population rejects regime action; energy → Omega
        "G_stored":           2.0,
        "alpha_total":        0.55,
        "E_dep_estimate":     0.60,
        "phi_delta":          -0.35,    # cohesion reduced among Islamist-adjacent population
        "omega_delta":        +0.65,    # major Omega loading
        "psi_div_delta":      +0.25,
        "symbolic_criticality":   0.55,
        "propagation_reach":      0.50,
        "narrative_sync_trigger": 0,
        "regime_response":        "repression",
        "regime_response_date":   None,
        "regime_response_T_prime": None,
        "regime_response_mode":   None,
        "systemic_outcome":       "national",
        "delta_tau_effect":       0.20,
        "data_source":            "Amnesty International reports 1991-1992; Cavatorta & Durac (2011)",
        "coding_confidence":      "medium",
        "coding_notes":           (
            "The suppression IS the regime action — no separate regime_response coded. "
            "Ennahda population (~15-20% of adult population) transitions to maximum T'' "
            "toward Sol and enters stored Omega. This population's latent activation is a "
            "primary component of the Omega field that eventually discharges in 2011."
        ),
    },

    {
        "event_id":           "TUN-IMF-SAP-PEAK-19940101",
        "case_id":            CASE_ID,
        "obs_id":             "TUN-1994",
        "date":               "1994-01-01",
        "event_name":         "IMF Structural Adjustment Program peak effects",
        "event_description":  (
            "Peak impact of the IMF SAP begun in 1986: public sector hiring freeze, "
            "subsidy reductions, trade liberalization accelerating coastal/interior "
            "divergence. Formal labor contracting fell; informal sector expanded. "
            "Coded as a diffuse event at the year representative date."
        ),
        "origin_x1":          None,
        "origin_x2":          0.0,
        "origin_x3":          0.0,
        "origin_orbital_r":   0.95,    # external international origin
        "origin_type":        "international",
        "content_v1":         0.90,    # primarily economic
        "content_v2":         0.20,
        "content_v3":         0.10,
        "multi_axis":         0,
        "intensity":          0.60,
        "q_n":                -0.50,
        "T_prime_toward_origin":        0.40,   # low trust toward IMF in population
        "T_double_prime_toward_origin": 0.60,
        "interaction_mode":   "distortive",     # official "necessary reform" vs material job loss reality
        "G_stored":           1.5,
        "alpha_total":        0.40,
        "E_dep_estimate":     0.50,
        "phi_delta":          -0.20,
        "omega_delta":        +0.45,
        "psi_div_delta":      +0.15,
        "symbolic_criticality":   0.30,
        "propagation_reach":      0.65,
        "narrative_sync_trigger": 0,
        "regime_response":        None,
        "regime_response_date":   None,
        "regime_response_T_prime": None,
        "regime_response_mode":   None,
        "systemic_outcome":       "national",
        "delta_tau_effect":       0.10,
        "data_source":            "World Bank Tunisia structural adjustment reports; Murphy (1999)",
        "coding_confidence":      "medium",
        "coding_notes":           (
            "Coded as a diffuse slow-moving event. The 1994 date represents the peak "
            "of SAP-induced labor market disruption. Symbolic criticality is low because "
            "the event is abstract and institutional — no single image or body to "
            "concentrate population identification. Primary effect is x1 Omega loading "
            "and the beginning of the E'/E'' divergence that peaks in 2009-2010."
        ),
    },

    {
        "event_id":           "TUN-CONST-MANIP-20020526",
        "case_id":            CASE_ID,
        "obs_id":             "TUN-2002",
        "date":               "2002-05-26",
        "event_name":         "Constitutional referendum removes presidential term limits",
        "event_description":  (
            "Ben Ali engineered a constitutional referendum officially approved by 99.52% "
            "of voters, removing the two-term limit and raising the eligible age ceiling "
            "to 75. Widely seen as a manufactured result. Key legitimacy erosion event: "
            "even within a managed system, the visible absurdity of 99.52% revealed "
            "the terminal hollowness of the electoral mechanism."
        ),
        "origin_x1":          None,
        "origin_x2":          0.60,
        "origin_x3":          0.70,
        "origin_orbital_r":   0.05,
        "origin_type":        "government",
        "content_v1":         0.10,
        "content_v2":         0.90,
        "content_v3":         0.20,
        "multi_axis":         0,
        "intensity":          0.55,
        "q_n":                -0.60,   # population saw through the manufactured consensus
        "T_prime_toward_origin":        0.50,
        "T_double_prime_toward_origin": 0.50,
        "interaction_mode":   "distortive",
        "G_stored":           1.3,
        "alpha_total":        0.45,
        "E_dep_estimate":     0.40,
        "phi_delta":          -0.15,
        "omega_delta":        +0.30,
        "psi_div_delta":      +0.25,   # significant — 99.52% makes the gap between Psi and reality undeniable
        "symbolic_criticality":   0.40,
        "propagation_reach":      0.70,
        "narrative_sync_trigger": 0,
        "regime_response":        None,
        "regime_response_date":   None,
        "regime_response_T_prime": None,
        "regime_response_mode":   None,
        "systemic_outcome":       "national",
        "delta_tau_effect":       0.10,
        "data_source":            "Human Rights Watch Tunisia 2002; Cassarino (2004)",
        "coding_confidence":      "medium",
        "coding_notes":           (
            "The 99.52% result is itself the key TSR signal: it represents the regime "
            "overstating its own Psi consolidation to the point of self-parody. This "
            "excessive claim damages L more than a lower but more credible result would "
            "have. Ben Ali's declining re-election margins across elections (99.9% → 89.6%) "
            "are a detectable L decay signal even within a fully managed electoral system."
        ),
    },

    {
        "event_id":           "TUN-WSIS-20051116",
        "case_id":            CASE_ID,
        "obs_id":             "TUN-2005",
        "date":               "2005-11-16",
        "event_name":         "World Summit on Information Society, Tunis",
        "event_description":  (
            "Tunisia hosted the UN WSIS summit on internet governance while maintaining "
            "some of the heaviest internet censorship in the Arab world. Civil society "
            "activists and journalists attempted to protest; several were beaten by "
            "plainclothes police in view of international delegates. The contradiction "
            "between the regime's modernisation narrative and manifest censorship reality "
            "was exposed to international actors."
        ),
        "origin_x1":          None,
        "origin_x2":          0.0,
        "origin_x3":          0.0,
        "origin_orbital_r":   0.90,
        "origin_type":        "international",
        "content_v1":         0.20,
        "content_v2":         0.70,
        "content_v3":         0.30,
        "multi_axis":         0,
        "intensity":          0.45,
        "q_n":                -0.65,
        "T_prime_toward_origin":        0.55,
        "T_double_prime_toward_origin": 0.45,
        "interaction_mode":   "distortive",
        "G_stored":           1.5,
        "alpha_total":        0.40,
        "E_dep_estimate":     0.35,
        "phi_delta":          -0.10,
        "omega_delta":        +0.25,
        "psi_div_delta":      +0.30,
        "symbolic_criticality":   0.35,
        "propagation_reach":      0.30,   # mainly educated/international-connected
        "narrative_sync_trigger": 0,
        "regime_response":        "repression",
        "regime_response_date":   "2005-11-18",
        "regime_response_T_prime": 0.35,
        "regime_response_mode":   "backfire",
        "systemic_outcome":       "national",
        "delta_tau_effect":       0.10,
        "data_source":            "Reporters Without Borders WSIS report 2005; Deibert et al. (2008)",
        "coding_confidence":      "medium",
        "coding_notes":           (
            "Primary effect is Q_coupling erosion: the summit forced the international "
            "community to observe the gap between Tunisia's official Psi and its actual "
            "information environment. Marks the point where international actors began "
            "treating the regime's modernisation narrative with explicit scepticism. "
            "Limited propagation within Tunisia due to censorship, but significant for "
            "the educated population and future Cablegate amplification."
        ),
    },

    {
        "event_id":           "TUN-GAFSA-PROTESTS-20080105",
        "case_id":            CASE_ID,
        "obs_id":             "TUN-2008-Q1",
        "date":               "2008-01-05",
        "event_name":         "Gafsa mining basin protests begin",
        "event_description":  (
            "Protests began in Redeyef (Gafsa governorate) over unemployment and "
            "nepotism in hiring at the Compagnie des Phosphates de Gafsa. Continued "
            "through June 2008. Critical comparison case for Bouazizi: near-identical "
            "stored Omega conditions but fundamentally different surface geometry and "
            "propagation topology produce opposite systemic outcomes."
        ),
        "origin_x1":          None,
        "origin_x2":          -0.25,
        "origin_x3":          0.50,
        "origin_orbital_r":   0.80,
        "origin_type":        "spontaneous",
        "content_v1":         0.85,    # primarily x1 — employment, wages
        "content_v2":         0.35,    # some political — nepotism, governance
        "content_v3":         0.30,    # regional identity
        "multi_axis":         0,       # effectively single-axis at national level — KEY contrast with Bouazizi
        "intensity":          0.55,
        "q_n":                -0.60,
        "T_prime_toward_origin":        0.75,   # interior mass identifies with origin
        "T_double_prime_toward_origin": 0.25,
        "interaction_mode":   "scattering",     # locally amplified, nationally scattered — C_conn below threshold
        "G_stored":           3.0,     # locally very high; nationally moderate
        "alpha_total":        0.35,    # low nationally because content vector is single-axis
        "E_dep_estimate":     0.55,
        "phi_delta":          -0.40,
        "omega_delta":        +0.60,
        "psi_div_delta":      +0.15,   # minor national Psi divergence
        "symbolic_criticality":   0.30,    # LOW — the critical finding
        "propagation_reach":      0.15,    # mainly local — C_conn below threshold
        "narrative_sync_trigger": 0,
        "regime_response":        "repression",
        "regime_response_date":   "2008-06-08",
        "regime_response_T_prime": 0.35,
        "regime_response_mode":   "distortive",
        "systemic_outcome":       "regional",
        "delta_tau_effect":       0.15,
        "data_source":            "International Crisis Group 2011; Gobe (2010); ACLED 2008",
        "coding_confidence":      "high",
        "coding_notes":           (
            "THE critical non-trigger case. Three factors explain the failure to cascade: "
            "(1) multi_axis=0 — x1-loaded content without x2/x3 resonance in coastal urban "
            "population. A Tunis factory worker could not identify with a phosphate miner's "
            "specific grievance the way they could with Bouazizi's market humiliation. "
            "(2) C_conn below threshold — Facebook had not yet penetrated interior-to-coast "
            "at sufficient density for Mode 4 propagation in 2008. "
            "(3) propagation_reach=0.15 — the stored energy could not reach the surface "
            "area needed to trigger national Mode 4 cascade. "
            "Omega stored in Gafsa did NOT dissipate — it accumulated and contributed to "
            "the Omega field that Bouazizi's self-immolation released in December 2010."
        ),
    },

    {
        "event_id":           "TUN-GAFSA-SUPPRESS-20080608",
        "case_id":            CASE_ID,
        "obs_id":             "TUN-2008-Q2",
        "date":               "2008-06-08",
        "event_name":         "Security forces suppress Gafsa protests",
        "event_description":  (
            "Military and security forces deployed to end the Gafsa protests. Several "
            "protesters killed, hundreds arrested, protest leaders sentenced to long "
            "prison terms. International media access was blocked. Human Rights Watch "
            "documented the crackdown through smuggled footage."
        ),
        "origin_x1":          None,
        "origin_x2":          0.60,
        "origin_x3":          0.70,
        "origin_orbital_r":   0.05,
        "origin_type":        "government",
        "content_v1":         0.20,
        "content_v2":         0.80,
        "content_v3":         0.30,
        "multi_axis":         0,
        "intensity":          0.65,
        "q_n":                -0.30,   # net: dissonant despite regime framing as stability
        "T_prime_toward_origin":        0.38,
        "T_double_prime_toward_origin": 0.62,
        "interaction_mode":   "rejection",
        "G_stored":           1.8,
        "alpha_total":        0.40,
        "E_dep_estimate":     0.50,
        "phi_delta":          -0.30,
        "omega_delta":        +0.55,   # martyrdom effect adds to Omega
        "psi_div_delta":      +0.20,
        "symbolic_criticality":   0.35,
        "propagation_reach":      0.20,
        "narrative_sync_trigger": 0,
        "regime_response":        "repression",
        "regime_response_date":   None,
        "regime_response_T_prime": None,
        "regime_response_mode":   None,
        "systemic_outcome":       "regional",
        "delta_tau_effect":       0.15,
        "data_source":            "Human Rights Watch 'Crushing the Promise of the Arab Spring' 2011",
        "coding_confidence":      "medium",
        "coding_notes":           (
            "The suppression converts the protest Omega into stored martyrdom Omega. "
            "The regime succeeds in eliminating the visible event but adds to the total "
            "Omega field. This is the standard pattern of repression in metastable systems: "
            "the relief valve is sealed, pressure increases. The Gafsa Omega reappears "
            "as a component of the 2011 release."
        ),
    },

    # ─── TIER 2: Surface pre-conditioning ────────────────────────────────────

    {
        "event_id":           "TUN-CABLEGATE-20101128",
        "case_id":            CASE_ID,
        "obs_id":             "TUN-2010-11",
        "date":               "2010-11-28",
        "event_name":         "WikiLeaks Cablegate — Tunisia cables released",
        "event_description":  (
            "WikiLeaks published US diplomatic cables describing Tunisia's ruling "
            "family as a mafia ('The Family'), documenting systemic corruption, "
            "Ben Ali son-in-law Sakher El Materi's ostentatious lifestyle, and the "
            "regime's security apparatus in frank terms. Ambassador Robert Godec's "
            "2009 cable was widely shared on Tunisian Facebook despite state censorship "
            "attempts."
        ),
        "origin_x1":          None,
        "origin_x2":          -0.10,
        "origin_x3":          -0.20,
        "origin_orbital_r":   0.90,
        "origin_type":        "international",
        "content_v1":         0.50,    # economic corruption content
        "content_v2":         0.85,    # political — regime illegitimacy
        "content_v3":         0.40,    # cultural — corruption as violation of social norms
        "multi_axis":         1,
        "intensity":          0.70,
        "q_n":                -0.85,
        "T_prime_toward_origin":        0.65,
        "T_double_prime_toward_origin": 0.35,
        "interaction_mode":   "amplification",  # pre-conditions surface — raises stored T'' toward Sol
        "G_stored":           2.5,
        "alpha_total":        0.60,
        "E_dep_estimate":     0.60,
        "phi_delta":          -0.35,
        "omega_delta":        +0.40,
        "psi_div_delta":      +0.40,   # confirms official Psi is false — significant divergence
        "symbolic_criticality":   0.65,
        "propagation_reach":      0.40,    # internet-connected urban population
        "narrative_sync_trigger": 0,
        "regime_response":        "none",   # Ben Ali initially ignored
        "regime_response_date":   None,
        "regime_response_T_prime": None,
        "regime_response_mode":   None,
        "systemic_outcome":       "national",
        "delta_tau_effect":       0.35,
        "data_source":            "WikiLeaks cable 09TUNIS492; Ryan (2011); Howard & Hussain (2013)",
        "coding_confidence":      "high",
        "coding_notes":           (
            "Surface pre-conditioning event. WikiLeaks confirmed in authoritative "
            "international terms what Tunisia's digitally connected population already "
            "suspected. Primary effect: raises T'' toward Sol in urban-educated populations "
            "and provides an internationally credible narrative that the regime's information "
            "controls cannot fully suppress. "
            "Propagation limited to ~40% of urban youth with Facebook access but this is "
            "precisely the segment with highest C_conn potential for subsequent cascade. "
            "The cables shifted the surface geometry toward maximum amplification mode: "
            "any subsequent high-criticality inforay now strikes a surface pre-loaded "
            "with confirmed regime corruption narrative."
        ),
    },

    # ─── TIER 3: Cascade events ───────────────────────────────────────────────

    {
        "event_id":           "TUN-BOUAZIZI-20101217",
        "case_id":            CASE_ID,
        "obs_id":             "TUN-2010-W50",
        "date":               "2010-12-17",
        "event_name":         "Mohamed Bouazizi self-immolation",
        "event_description":  (
            "Mohamed Bouazizi, 26-year-old street vendor in Sidi Bouzid, was publicly "
            "slapped and humiliated by municipal inspector Faida Hamdi who confiscated "
            "his produce cart. Unable to obtain redress from the regional governor, "
            "he doused himself in gasoline and set himself on fire at 11:30 AM in front "
            "of the regional headquarters. He died January 4, 2011. Video recorded by "
            "his cousin was posted to Facebook within hours."
        ),
        "origin_x1":          None,
        "origin_x2":          -0.30,   # working class, progressive grievance
        "origin_x3":          0.40,    # traditional background, religious, regional identity
        "origin_orbital_r":   0.85,    # Sidi Bouzid — deep interior, outer orbit
        "origin_type":        "spontaneous",
        "content_v1":         0.90,    # economic — market vendor denied livelihood
        "content_v2":         0.85,    # political — arbitrary state power, public humiliation by official
        "content_v3":         0.80,    # cultural — dignity, manhood, generational, regional identity
        "multi_axis":         1,       # MAXIMUM — simultaneous loading across all three axes
        "intensity":          0.95,
        "q_n":                -1.0,    # maximally dissonant with regime Psi
        "T_prime_toward_origin":        0.95,   # mass identifies completely: he IS the mass
        "T_double_prime_toward_origin": 0.05,
        "interaction_mode":   "amplification",  # Mode 4 — massive stored Omega released
        "G_stored":           8.0,     # accumulated Omega from Ennahda suppression, SAP, Gafsa, 23 years
        "alpha_total":        0.90,    # near-maximum coupling
        "E_dep_estimate":     0.95,
        "phi_delta":          -0.80,   # old regime Phi collapses; new insurgent Phi begins forming
        "omega_delta":        +0.90,   # initial massive Omega release triggering cascade
        "psi_div_delta":      +0.90,   # regime Psi collapses — narrative synchronization cascade begins
        "symbolic_criticality":   0.97,
        "propagation_reach":      0.85,    # reaches most of national Mass via Facebook/Al Jazeera/mobile
        "narrative_sync_trigger": 1,       # triggers system-wide narrative synchronization cascade
        "regime_response":        "symbolic",
        "regime_response_date":   "2010-12-28",
        "regime_response_T_prime": 0.15,
        "regime_response_mode":   "backfire",
        "systemic_outcome":       "international_cascade",
        "delta_tau_effect":       0.90,    # near-maximum time compression — Δτ collapses
        "data_source":            "Al Jazeera English; Nouri (2011); Ryan (2011); Mejri (2011)",
        "coding_confidence":      "high",
        "coding_notes":           (
            "Primary trigger event. Contrast with Gafsa 2008 is TSR-1G's critical test case. "
            "Identical Omega accumulation conditions; decisive differences: "
            "(1) multi_axis=1: content loads simultaneously across x1 (livelihood), x2 "
            "(state power/humiliation), x3 (dignity/manhood/regional identity). Gafsa was "
            "effectively x1-only at national level. "
            "(2) C_conn threshold crossed: Facebook penetration in 2010 enabled interior-to-coast "
            "propagation unavailable in 2008. "
            "(3) T'_toward_origin near unity: Bouazizi is from the outer orbit — the mass "
            "identifies with him completely. The female official's public slap activated x3 "
            "dignity content resonant across class and regional lines. "
            "(4) Surface pre-conditioned by Cablegate: T'' toward Sol already elevated. "
            "G_stored estimated at 8.0 representing accumulated Omega from 1992-2010. "
            "The symbolic criticality near-maximum because ALL conditions converge simultaneously."
        ),
    },

    {
        "event_id":           "TUN-PROTESTS-SBZ-20101219",
        "case_id":            CASE_ID,
        "obs_id":             "TUN-2010-W50",
        "date":               "2010-12-19",
        "event_name":         "First protests in Sidi Bouzid — cascade begins",
        "event_description":  (
            "Protesters took to the streets in Sidi Bouzid two days after Bouazizi's "
            "self-immolation, burning tires and confronting security forces. Security "
            "forces responded with tear gas and live ammunition. At least one protester "
            "killed. Video distributed via Facebook and Al Jazeera Arabic. This is the "
            "point at which Mode 4 amplification begins propagating nationally."
        ),
        "origin_x1":          None,
        "origin_x2":          -0.30,
        "origin_x3":          0.40,
        "origin_orbital_r":   0.80,
        "origin_type":        "spontaneous",
        "content_v1":         0.70,
        "content_v2":         0.80,
        "content_v3":         0.70,
        "multi_axis":         1,
        "intensity":          0.65,
        "q_n":                -0.90,
        "T_prime_toward_origin":        0.90,
        "T_double_prime_toward_origin": 0.10,
        "interaction_mode":   "amplification",
        "G_stored":           5.0,     # Bouazizi event has released energy now propagating
        "alpha_total":        0.80,
        "E_dep_estimate":     0.70,
        "phi_delta":          -0.60,
        "omega_delta":        +0.75,
        "psi_div_delta":      +0.70,
        "symbolic_criticality":   0.75,
        "propagation_reach":      0.55,    # spreading nationally via social media
        "narrative_sync_trigger": 0,       # partial sync — accelerating
        "regime_response":        "repression",
        "regime_response_date":   "2010-12-19",
        "regime_response_T_prime": 0.12,
        "regime_response_mode":   "backfire",   # shooting protesters accelerates cascade
        "systemic_outcome":       "national",
        "delta_tau_effect":       0.70,
        "data_source":            "Human Rights Watch 2011; Al Jazeera English broadcast logs",
        "coding_confidence":      "medium",
        "coding_notes":           (
            "Regime response (live ammunition) converts individual grievance into national "
            "martyr narrative, extending Bouazizi's symbolic criticality through secondary "
            "events. Each repression event at this stage operates as a Mode 4 amplifier "
            "rather than a Mode 1 suppressor — the surface geometry has inverted."
        ),
    },

    {
        "event_id":           "TUN-BENALI-HOSPITAL-20101228",
        "case_id":            CASE_ID,
        "obs_id":             "TUN-2010-W51",
        "date":               "2010-12-28",
        "event_name":         "Ben Ali visits Bouazizi in hospital",
        "event_description":  (
            "Ben Ali visited Mohamed Bouazizi at the military hospital in Ben Arous. "
            "Bouazizi was in a coma with burns over 90% of his body. Photographs of "
            "a suited Ben Ali next to the comatose Bouazizi circulated on Facebook within "
            "hours, widely read as cynical appropriation rather than concession."
        ),
        "origin_x1":          None,
        "origin_x2":          0.60,
        "origin_x3":          0.70,
        "origin_orbital_r":   0.05,
        "origin_type":        "government",
        "content_v1":         0.30,
        "content_v2":         0.70,
        "content_v3":         0.40,
        "multi_axis":         0,
        "intensity":          0.60,
        "q_n":                -0.70,   # intended as concession; received as cynical
        "T_prime_toward_origin":        0.15,
        "T_double_prime_toward_origin": 0.85,
        "interaction_mode":   "distortive",     # concession attempt read as insult
        "G_stored":           3.0,
        "alpha_total":        0.55,
        "E_dep_estimate":     0.50,
        "phi_delta":          -0.40,
        "omega_delta":        +0.50,   # the concession is itself fuel
        "psi_div_delta":      +0.45,
        "symbolic_criticality":   0.50,
        "propagation_reach":      0.60,
        "narrative_sync_trigger": 0,
        "regime_response":        "symbolic",
        "regime_response_date":   "2010-12-28",
        "regime_response_T_prime": 0.15,
        "regime_response_mode":   "backfire",
        "systemic_outcome":       "national",
        "delta_tau_effect":       0.45,
        "data_source":            "Libération; Le Monde; Ben Salem (2012)",
        "coding_confidence":      "high",
        "coding_notes":           (
            "Classic regime miscalculation under terminal L collapse. At T'~0.15, "
            "any symbolic gesture from the Sol is interpreted through the T'' lens. "
            "The hospital photographs became the most widely shared image of the "
            "week on Tunisian Facebook — not as evidence of care but as evidence of "
            "the distance between the comatose Bouazizi (outer orbit, burned) and "
            "the suited Ben Ali (inner Sol, intact)."
        ),
    },

    {
        "event_id":           "TUN-BENALI-SPEECH-20110110",
        "case_id":            CASE_ID,
        "obs_id":             "TUN-2011-W01",
        "date":               "2011-01-10",
        "event_name":         "Ben Ali televised address — 'terrorists and extremists'",
        "event_description":  (
            "Ben Ali's first major televised address on the protests. Called demonstrators "
            "'a minority of extremists and terrorists.' Announced he would not seek "
            "re-election in 2014 — a concession instantly dismissed as inadequate. "
            "Security forces killed protesters in Kasserine and Thala on the same day."
        ),
        "origin_x1":          None,
        "origin_x2":          0.60,
        "origin_x3":          0.70,
        "origin_orbital_r":   0.05,
        "origin_type":        "government",
        "content_v1":         0.20,
        "content_v2":         0.90,
        "content_v3":         0.40,
        "multi_axis":         0,
        "intensity":          0.70,
        "q_n":                -0.85,   # "terrorist" framing rejected instantly; deeply dissonant
        "T_prime_toward_origin":        0.10,   # near-zero trust toward regime
        "T_double_prime_toward_origin": 0.90,
        "interaction_mode":   "distortive",
        "G_stored":           4.0,
        "alpha_total":        0.65,
        "E_dep_estimate":     0.65,
        "phi_delta":          -0.60,
        "omega_delta":        +0.70,
        "psi_div_delta":      +0.60,
        "symbolic_criticality":   0.55,
        "propagation_reach":      0.80,
        "narrative_sync_trigger": 0,
        "regime_response":        "repression",
        "regime_response_date":   "2011-01-10",
        "regime_response_T_prime": 0.10,
        "regime_response_mode":   "backfire",
        "systemic_outcome":       "national",
        "delta_tau_effect":       0.65,
        "data_source":            "Al Jazeera English; BBC Arabic; Ryan (2011)",
        "coding_confidence":      "high",
        "coding_notes":           (
            "The 'terrorist' framing is the clearest example of a regime attempting "
            "a Mode 1 (rejection) interaction on a Mass surface that has already inverted. "
            "At T'=0.10, any regime communication is processed through maximum T''. "
            "The 2014 pledge was too late and too distant to affect the surface geometry. "
            "The simultaneous killing of protesters in Kasserine negated the concession "
            "signal within the same news cycle. Proper time is now fully compressed."
        ),
    },

    {
        "event_id":           "TUN-BENALI-FLEES-20110114",
        "case_id":            CASE_ID,
        "obs_id":             "TUN-2011-W02",
        "date":               "2011-01-14",
        "event_name":         "Ben Ali flees Tunisia — Political Singularity",
        "event_description":  (
            "Ben Ali boards a plane with family at Tunis-Carthage airport, destination "
            "Jeddah, Saudi Arabia. Prime Minister Ghannouchi announces interim presidency. "
            "Crowds celebrate in Avenue Habib Bourguiba. The Political Sol ceases to "
            "exist as a physical attractor. Tunisia enters Post-Transition reconfiguration."
        ),
        "origin_x1":          None,
        "origin_x2":          0.60,
        "origin_x3":          0.70,
        "origin_orbital_r":   0.05,
        "origin_type":        "government",
        "content_v1":         0.30,
        "content_v2":         1.0,     # maximum political content
        "content_v3":         0.60,
        "multi_axis":         1,
        "intensity":          1.0,     # maximum — total regime collapse
        "q_n":                -1.0,
        "T_prime_toward_origin":        0.0,    # zero — the Sol has abandoned its position
        "T_double_prime_toward_origin": 1.0,
        "interaction_mode":   "amplification",  # all stored Omega releases simultaneously
        "G_stored":           10.0,    # beyond scale — total accumulated Omega from 23 years releases
        "alpha_total":        0.95,
        "E_dep_estimate":     1.0,     # maximum energy release — Phase Transition achieved
        "phi_delta":          -1.0,    # old Phi entirely destroyed
        "omega_delta":        -0.85,   # Omega releases through the phase transition
        "psi_div_delta":      -0.60,   # paradox: Psi CONVERGES briefly ("Ben Ali Dégage") then rapidly diverges
        "symbolic_criticality":   1.0,
        "propagation_reach":      1.0,
        "narrative_sync_trigger": 1,   # complete national narrative synchronization
        "regime_response":        None,
        "regime_response_date":   None,
        "regime_response_T_prime": None,
        "regime_response_mode":   None,
        "systemic_outcome":       "international_cascade",
        "delta_tau_effect":       1.0,  # maximum — Social Event Horizon crossed
        "data_source":            "Reuters; AFP; Le Monde; Al Jazeera English live feed 2011-01-14",
        "coding_confidence":      "high",
        "coding_notes":           (
            "Political Singularity event. The Political Sol ceases to exist as a physical "
            "attractor — the Mass has no central gravity well and enters reconfiguration phase. "
            "psi_div_delta is negative (converging) in the immediate moment — 'Ben Ali Dégage' "
            "achieves near-complete narrative synchronization — before rapidly diverging as "
            "post-revolutionary political competition begins within days. "
            "systemic_outcome=international_cascade: Tunisia's Phase Transition was itself "
            "a high-criticality inforay for Egypt, Libya, Bahrain, Syria, and Yemen — each "
            "of which had their own Omega fields awaiting a sufficient trigger. "
            "G_stored=10.0 is a placeholder exceeding the [0,1] implied scale — the actual "
            "accumulated Omega from 1987-2010 has no calibrated upper bound yet. "
            "omega_delta is negative: the stress field discharges through the transition."
        ),
    },

]


def load() -> pd.DataFrame:
    """Return the Tunisia event log as a DataFrame indexed by event_id."""
    df = pd.DataFrame(EVENTS).set_index("event_id")
    return df


def write_to_db(db_path: Path) -> None:
    """Write the event log to the tsr_inforay_events table in the SQLite database."""
    df = load().reset_index()
    con = sqlite3.connect(db_path)
    df.to_sql("tsr_inforay_events", con, if_exists="replace", index=False)
    con.close()
    print(f"  Wrote {len(df)} events → tsr_inforay_events")
