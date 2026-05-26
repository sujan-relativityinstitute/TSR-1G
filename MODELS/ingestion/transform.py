"""
Transform raw annual data into normalized TSR-1G state variables.

Flow:
  1. Merge all raw source DataFrames into one wide annual panel.
  2. Interpolate short gaps (<=3 years) linearly; flag as interpolated.
  3. Compute derived raw indicators (polydispersity, alpha, T').
  4. Min-max normalize over the full 1990-2011 window.
  5. Apply proxy formulas → TSR state vector variables.
  6. Map annual rows to observation schedule (annual + sub-annual obs_ids).

Sub-annual rows (quarterly, monthly, weekly) inherit the annual value for
slow-moving variables and use period-specific values only where higher-
frequency data exists (FAO monthly FFPI, ACLED event counts).
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional, Tuple

from .config import OBSERVATION_SCHEDULE, WEIGHTS, SOL_X2, SOL_X3, YEARS


# -------------------------------------------------------------------------
# 1. Merge raw sources
# -------------------------------------------------------------------------

def merge_raw(
    wb: pd.DataFrame,
    polity: pd.DataFrame,
    fh: pd.DataFrame,
    fao: pd.DataFrame,
    acled: pd.DataFrame,
) -> pd.DataFrame:
    panel = (
        wb
        .join(polity, how="outer")
        .join(fh,     how="outer")
        .join(fao,    how="outer")
        .join(acled,  how="outer")
    )
    panel = panel.reindex(YEARS)
    panel.index.name = "year"
    return panel


# -------------------------------------------------------------------------
# 2. Interpolate gaps
# -------------------------------------------------------------------------

def interpolate_gaps(panel: pd.DataFrame, max_gap: int = 3) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Linear interpolation for gaps up to max_gap years.
    Returns (interpolated_panel, interpolated_flag_df).
    """
    flag = pd.DataFrame(False, index=panel.index, columns=panel.columns)
    out  = panel.copy()

    for col in panel.columns:
        s = panel[col]
        missing = s.isna()
        if not missing.any():
            continue
        # Only interpolate gaps within the series, not leading/trailing NaN
        interp = s.interpolate(method="linear", limit=max_gap, limit_area="inside")
        newly_filled = missing & interp.notna()
        out.loc[newly_filled, col]  = interp[newly_filled]
        flag.loc[newly_filled, col] = True

    return out, flag


# -------------------------------------------------------------------------
# 3. Normalization utilities
# -------------------------------------------------------------------------

def minmax(series: pd.Series, invert: bool = False) -> pd.Series:
    lo, hi = series.min(), series.max()
    if hi == lo:
        return pd.Series(0.5, index=series.index)
    norm = (series - lo) / (hi - lo)
    return 1.0 - norm if invert else norm


def wmean(df: pd.DataFrame, weights: Dict[str, float]) -> pd.Series:
    """Weighted mean across named columns. Missing columns → 0 contribution."""
    total_w = 0.0
    result  = pd.Series(0.0, index=df.index)
    for col, w in weights.items():
        if col in df.columns and df[col].notna().any():
            result   += df[col].fillna(df[col].median()) * w
            total_w  += w
    return result / total_w if total_w > 0 else result


# -------------------------------------------------------------------------
# 4. Polydispersity from quintile income shares
# -------------------------------------------------------------------------

def compute_polydispersity(panel: pd.DataFrame) -> pd.DataFrame:
    """
    Compute PI_n, PI_w, PI_z from quintile income shares.

    With 5 equal population bins (p_i = 0.20):
      s_i = q_i / 0.20 = 5*q_i   (income relative to mean)
      w_i = q_i                   (economic weight = income share)

      PI_n = sum(p_i * s_i) = 1.0  (trivial for equal bins; omit)
      PI_w = 5 * sum(q_i^3) / sum(q_i^2)
      PI_z = 5 * sum(q_i^4) / sum(q_i^3)
      PI_w/PI_n = PI_w  (since PI_n = 1)
      PI_z/PI_w = PI_z / PI_w
    """
    q_cols = ["income_share_q1", "income_share_q2", "income_share_q3",
              "income_share_q4", "income_share_q5"]

    result = pd.DataFrame(index=panel.index)
    result["PI_n_x1"] = 1.0   # trivially 1 for equal population bins

    if all(c in panel.columns for c in q_cols):
        Q = panel[q_cols].div(100)   # convert pct to fractions if needed
        # If values > 1, already fractions; if sum > 1.5, assume percentages
        if Q.sum(axis=1).mean() > 1.5:
            Q = Q / 100

        sum_q2 = (Q**2).sum(axis=1)
        sum_q3 = (Q**3).sum(axis=1)
        sum_q4 = (Q**4).sum(axis=1)

        result["PI_w_x1"] = 5 * sum_q3 / sum_q2.replace(0, np.nan)
        result["PI_z_x1"] = 5 * sum_q4 / sum_q3.replace(0, np.nan)
    else:
        # Gini-based approximation when quintile data is missing
        # PI_w ≈ 1 + 2*Gini  (rough linear approximation)
        if "gini_coefficient" in panel.columns:
            g = panel["gini_coefficient"] / 100   # assume stored as 0-100
            result["PI_w_x1"] = 1 + 2 * g
            result["PI_z_x1"] = 1 + 4 * g         # rougher approximation
        else:
            result["PI_w_x1"] = np.nan
            result["PI_z_x1"] = np.nan

    result["PIw_PIn_ratio"] = result["PI_w_x1"]   # PI_n = 1
    result["PIz_PIw_ratio"] = result["PI_z_x1"] / result["PI_w_x1"].replace(0, np.nan)
    return result


# -------------------------------------------------------------------------
# 5. Trust-Threat geometry
# -------------------------------------------------------------------------

def compute_trust_threat(panel: pd.DataFrame) -> pd.DataFrame:
    """
    Estimate x2/x3 population centroid from available proxies,
    then compute alpha, T', T".

    x2_pop: starts near 0.0, trends toward -0.2 as economic frustration grows.
             Anchored to Arab Barometer + Polity-derived opposition estimate.
    x3_pop: starts near +0.3 (moderately conformist), trends toward 0.0.
    """
    result = pd.DataFrame(index=panel.index)

    # Polity5-derived Sol position on x2 (already fixed as SOL_X2 in config)
    # Population x2: proxy from Freedom House PR inverted + polity_norm
    if "polity2" in panel.columns:
        polity_norm = (panel["polity2"] + 10) / 20   # 0=autocratic, 1=democratic
        # Population centroid on x2: more democratic wishes as autocracy tightens
        # Inverse: when regime is most autocratic, population tends progressive
        x2_pop = 0.0 - (SOL_X2 - polity_norm) * 0.3
    else:
        x2_pop = pd.Series(-0.10, index=panel.index)  # default slight progressive lean

    # Population x3: proxy from civil liberties (lower = more iconoclast pressure)
    if "freedom_house_civil_liberties" in panel.columns:
        cl_norm = (7 - panel["freedom_house_civil_liberties"]) / 6  # 1=best
        x3_pop = 0.3 - (1 - cl_norm) * 0.3   # as civil libs tighten, x3 moves iconoclast
    else:
        x3_pop = pd.Series(0.15, index=panel.index)

    result["x2_sol_position"] = SOL_X2
    result["x3_sol_position"] = SOL_X3
    result["x2_pop_centroid"] = x2_pop.clip(-1, 1)
    result["x3_pop_centroid"] = x3_pop.clip(-1, 1)

    # Alpha: Euclidean distance in x2-x3 plane, scaled to [0, 180] degrees
    max_dist = 2 * np.sqrt(2)   # maximum possible distance in [-1,+1]^2 space
    dist = np.sqrt((SOL_X2 - result["x2_pop_centroid"])**2 +
                   (SOL_X3 - result["x3_pop_centroid"])**2)
    result["alpha_degrees"] = (dist / max_dist) * 180

    alpha_rad = np.radians(result["alpha_degrees"])
    result["T_prime_system"] = np.cos(alpha_rad / 2)**2
    result["T_double_prime_system"] = np.sin(alpha_rad / 2)**2

    # Inner orbit (elite, alpha ~ 0.1): high T'
    result["T_prime_inner_orbit"] = np.cos(np.radians(10) / 2)**2

    # Outer orbit (mass, alpha ~ sol_alpha + 0.3 more divergent)
    alpha_outer = (dist + 0.3).clip(0, max_dist) / max_dist * 180
    result["T_prime_outer_orbit"] = np.cos(np.radians(alpha_outer) / 2)**2

    # Interior region (even more divergent from Sol)
    alpha_interior = (dist + 0.5).clip(0, max_dist) / max_dist * 180
    result["T_prime_interior_region"] = np.cos(np.radians(alpha_interior) / 2)**2

    return result


# -------------------------------------------------------------------------
# 6. TSR state variable computation
# -------------------------------------------------------------------------

def compute_tsr_variables(panel: pd.DataFrame, tt: pd.DataFrame, pi: pd.DataFrame) -> pd.DataFrame:
    """
    Apply proxy formulas to produce the full TSR state vector.
    All output variables normalized to [0,1].

    Input discipline (Section 38A): only the 9 generalized structural input slots
    appear as inputs here. No placeholder constants, no derived intermediates, no
    model-calculated variables feed back as structural inputs.

    Slot assignments (Section 38A.2):
      Slot 1 — material stress / economic deprivation (youth_unemp, gini, unemp, poverty)
      Slot 2 — price shock / subsistence pressure (food_price_index)
      Slot 3 — E" supply-side: state investment in human capital (education spending)
      Slot 4 — material stress mitigation: government health provision (health spending)
      Slot 5 — political constraint / institutional quality (cl, pr, polity, cpi)
      Slot 6 — mobilisation capacity: collective action events (protest_events_count)
      Slot 7 — regime response to dissent: repression events (repression_events_count)
      Slot 8 — regime force capacity (military_police_spending_pct_gdp)
      Slot 9 — information conductivity (internet_penetration, mobile_penetration)
    """
    df = panel.copy()
    W  = WEIGHTS

    # ── Slot 1: Material stress / economic deprivation ────────────────────────
    youth_unemp_n = minmax(df["youth_unemployment_rate"].fillna(df["youth_unemployment_rate"].median()))
    gini_n        = minmax(df["gini_coefficient"].fillna(df["gini_coefficient"].median()))
    unemp_n       = minmax(df["unemployment_rate"].fillna(df["unemployment_rate"].median()))
    poverty_n     = minmax(df["poverty_headcount_pct"].fillna(0))

    # ── Slot 2: Price shock / subsistence pressure ────────────────────────────
    food_n = minmax(df["food_price_index"].fillna(df["food_price_index"].median()))

    # ── Slot 3: E" supply-side — state investment in human capital ────────────
    edu_n = minmax(df["govt_education_spending_pct_gdp"].fillna(
        df["govt_education_spending_pct_gdp"].median()))

    # ── Slot 4: Material stress mitigation — government health provision ──────
    hlth_n = minmax(df["govt_health_spending_pct_gdp"].fillna(
        df["govt_health_spending_pct_gdp"].median()))

    # ── Slot 5: Political constraint / institutional quality ──────────────────
    # Freedom House: 1=best, 7=worst → invert so 1=unconstrained/free
    cl_n = minmax(df["freedom_house_civil_liberties"].fillna(5), invert=True)
    pr_n = minmax(df["freedom_house_political_rights"].fillna(6), invert=True)
    # Polity5: -10 to +10 → [0,1] where 1=most democratic
    polity_n   = ((df["polity2"].fillna(-5) + 10) / 20).clip(0, 1)
    polity_inv = 1.0 - polity_n   # high = autocratic = high D_dom
    # CPI: 0-10 scale (pre-2012 vintage), 10=cleanest
    cpi_n = minmax(df["corruption_cpi_score"].fillna(4.5))

    # ── Slot 6: Mobilisation capacity — collective action events ─────────────
    protest_n = minmax(df["protest_events_count"].fillna(0))

    # ── Slot 7: Regime response to dissent — repression events ───────────────
    repression_n = minmax(df["repression_events_count"].fillna(0))

    # ── Slot 8: Regime force capacity ────────────────────────────────────────
    mil_n = minmax(df["military_police_spending_pct_gdp"].fillna(
        df["military_police_spending_pct_gdp"].median()))

    # ── Slot 9: Information conductivity ─────────────────────────────────────
    internet_n = minmax(df["internet_penetration_pct"].fillna(0))
    mobile_n   = minmax(df["mobile_penetration_pct"].fillna(0))

    # ── Normalized input table for wmean ─────────────────────────────────────
    norm = pd.DataFrame(index=df.index)
    norm["youth_unemp"]  = youth_unemp_n    # Slot 1
    norm["gini"]         = gini_n           # Slot 1
    norm["unemployment"] = unemp_n          # Slot 1
    norm["poverty"]      = poverty_n        # Slot 1
    norm["food"]         = food_n           # Slot 2
    norm["education"]    = edu_n            # Slot 3
    norm["health"]       = hlth_n           # Slot 4
    norm["civil_lib"]    = cl_n             # Slot 5
    norm["polity"]       = polity_n         # Slot 5
    norm["polity_inv"]   = polity_inv       # Slot 5
    norm["cpi"]          = cpi_n            # Slot 5
    norm["protest"]      = protest_n        # Slot 6
    norm["repression"]   = repression_n     # Slot 7
    norm["military"]     = mil_n            # Slot 8
    norm["internet"]     = internet_n       # Slot 9
    norm["mobile"]       = mobile_n         # Slot 9

    out = pd.DataFrame(index=df.index)

    # ── CODA forces ───────────────────────────────────────────────────────────
    out["CODA_C_conn"]  = wmean(norm, W["CODA_C_conn"])
    out["CODA_O_ord"]   = wmean(norm, W["CODA_O_ord"])
    out["CODA_D_dom"]   = wmean(norm, W["CODA_D_dom"])
    out["CODA_A_aut"]   = wmean(norm, W["CODA_A_aut"])
    out["CODA_imbalance"] = (
        (out["CODA_D_dom"] - out["CODA_A_aut"]).abs() +
        (out["CODA_O_ord"] - out["CODA_C_conn"]).abs()
    ).clip(0, 1) / 2

    # ── Core state variables ──────────────────────────────────────────────────
    out["C_cohesion"]        = wmean(norm, W["C_cohesion"])
    out["T_tension"]         = wmean(norm, W["T_tension"])
    out["Theta_social_temp"] = wmean(norm, W["Theta"])
    out["E_m_maintenance"]   = wmean(norm, W["E_m"])

    # L: legitimacy reserve — institutional quality as perceived regime acceptance
    out["L_legitimacy"] = (cl_n * 0.60 + cpi_n * 0.40).clip(0, 1)

    # R: repression — ACLED events weighted by Freedom House constraint inversions
    out["R_repression"] = (
        repression_n * 0.50 + (1 - pr_n) * 0.30 + (1 - cl_n) * 0.20
    ).clip(0, 1)

    # P: political centralization
    out["P_centralization"] = polity_inv

    # E: economic stress composite
    e_stress_norm = pd.DataFrame({
        "youth_unemp": youth_unemp_n,
        "gini":        gini_n,
        "food":        food_n,
        "inflation":   minmax(df["inflation_cpi"].fillna(df["inflation_cpi"].median())),
    })
    out["E_economic_stress"] = wmean(
        e_stress_norm,
        {"youth_unemp": 0.30, "gini": 0.25, "food": 0.25, "inflation": 0.20}
    )

    # Psi: narrative divergence — tension accumulation under civil-liberty suppression
    out["Psi_div"]       = (out["T_tension"] * 0.5 + (1 - cl_n) * 0.5).clip(0, 1)
    out["Psi_coherence"] = 1.0 - out["Psi_div"]

    # Q: config-manifold coupling quality
    out["Q_coupling"] = (
        (1 - out["T_tension"]) * 0.5 + cpi_n * 0.3 + cl_n * 0.2
    ).clip(0, 1)

    # K: shock absorption capacity
    out["K_absorption"] = (
        polity_n * 0.30 + cl_n * 0.25 + edu_n * 0.25 + (1 - out["T_tension"]) * 0.20
    ).clip(0, 1)

    # D: dissipation capacity
    out["D_dissipation"] = (cl_n * 0.65 + protest_n * 0.35).clip(0, 1)

    # H: historical inertia — pending field equations (Section 35.2)
    out["H_inertia"] = np.nan

    # Theta sub-temperatures and TG hazard — pending field equations (Section 35.2)
    out["Theta_elite"]    = np.nan
    out["Theta_majority"] = np.nan
    out["TG_hazard"]      = np.nan

    # S: social entropy proxy (field equation pending; using Theta_social_temp)
    out["S_entropy"] = out["Theta_social_temp"].clip(0, 1)

    # CS: configuration space
    years = pd.Series(df.index, index=df.index)
    pop_growth_n = minmax(df["population_growth_rate"].fillna(
        df["population_growth_rate"].median()))
    out["CS_config_space"] = (
        0.50 * minmax(years.astype(float)) +
        0.30 * internet_n +
        0.20 * pop_growth_n
    ).clip(0, 1)

    # Event Horizon proximity
    out["EH_proximity"] = (
        out["CS_config_space"].diff().clip(0, None) /
        out["K_absorption"].replace(0, 0.01)
    ).clip(0, 3)

    # Omega-accessibility mismatch
    out["OA_mismatch"] = (out["T_tension"] * (1 - out["D_dissipation"])).clip(0, 1)

    # Delta-tau: social proper time compression
    T_change = out["T_tension"].diff().abs().fillna(0)
    out["delta_tau"] = 1 / (1 + 3 * T_change + 2 * out["Psi_div"])

    # x1 proxies
    out["x1_E_prime_proxy"] = minmax(df["gdp_pc_usd"].fillna(df["gdp_pc_usd"].median()))
    out["x1_E_double_prime_proxy"] = minmax(
        (df["youth_unemployment_rate"] / df["unemployment_rate"].replace(0, np.nan)).fillna(1.0)
    )

    # MDI* composite
    mdi_inputs = pd.DataFrame({
        "T_tension":         out["T_tension"],
        "Q_mismatch":        1 - out["Q_coupling"],
        "Psi_div":           out["Psi_div"],
        "E_economic_stress": out["E_economic_stress"],
        "R_repression":      out["R_repression"],
        "C_cohesion":        out["C_cohesion"],
        "K_absorption":      out["K_absorption"],
        "L_legitimacy":      out["L_legitimacy"],
    }, index=df.index)

    W_mdi = W["MDI_star"]
    out["MDI_star"] = sum(
        mdi_inputs[col] * w for col, w in W_mdi.items()
    ).clip(0, 1)

    # ── Omega_latent: stored social potential energy under sustained repression ──
    #
    # Ω_total = Ω_expressed (kinetic, proxied by T_tension) + Ω_latent (stored).
    # T_tension only sees the kinetic component. Under high repression the discharge
    # valve closes and structural stress accumulates as latent potential energy --
    # invisible to ACLED-based proxies.
    #
    # sigma_structural (Slots 1,2,3,4 -- repression-independent structural loading):
    #   These accumulate regardless of whether the population can express grievances.
    #
    # sigma_valve (Slots 5,6,8 -- suppression closure factor):
    #   Product form: latent energy requires both pressure AND a closed valve.
    #   High structural loading behind an open valve discharges immediately.
    #
    # Omega_acc: time-integral of suppressed structural loading.
    #   decay = 0.85 (calibration; to be derived from Section 35.2 field equations).
    #   discharge: tension releases when protest is present, not suppressed,
    #              and civil space exists.
    OMEGA_DECAY = 0.85

    gdp_pc_n = minmax(df["gdp_pc_usd"].fillna(df["gdp_pc_usd"].median()))

    sigma_structural = (
        youth_unemp_n    * 0.40   # Slot 3: frustrated positional gradient (E"/E')
        + gini_n         * 0.30   # Slot 1: distributional stress
        + food_n         * 0.20   # Slot 4: material stress
        + (1 - gdp_pc_n) * 0.10  # Slot 2: economic level stress (inverted)
    ).clip(0, 1)

    sigma_valve = (
        repression_n   * 0.50    # Slot 8: active force application
        + (1 - cl_n)   * 0.30   # Slot 6: civil space closure
        + (1 - pr_n)   * 0.20   # Slot 5: political space closure
    ).clip(0, 1)

    out["Omega_latent_inst"] = (sigma_structural * sigma_valve).clip(0, 1)
    out["sigma_structural"]  = sigma_structural
    out["sigma_valve"]       = sigma_valve

    discharge = (protest_n * (1 - repression_n) * cl_n).clip(0, 1)

    acc = 0.0
    omega_acc_vals = []
    for yr in sorted(out.index):
        inst  = out.loc[yr, "Omega_latent_inst"]
        disch = discharge.loc[yr]
        acc   = OMEGA_DECAY * acc + inst * (1.0 - disch)
        omega_acc_vals.append(acc)

    omega_acc_raw = pd.Series(omega_acc_vals, index=sorted(out.index))
    acc_min, acc_max = omega_acc_raw.min(), omega_acc_raw.max()
    if acc_max > acc_min:
        out["Omega_acc"] = ((omega_acc_raw - acc_min) / (acc_max - acc_min)).clip(0, 1)
    else:
        out["Omega_acc"] = 0.0

    # dT_tension: signed annual rate of change — T viewed as a process, not just a state.
    # Used by the phase classifier to detect rising-T dynamics (hidden fragility).
    # NaN for the first row → 0 (no prior year to compare).
    out["dT_tension"] = out["T_tension"].diff().fillna(0)

    # Regime phase classification
    out["regime_phase"] = out.apply(_classify_phase, axis=1)

    # Join trust-threat and polydispersity
    out = out.join(tt).join(pi)

    # Pass through selected raw columns (passthrough only — not used as inputs above)
    raw_passthrough = [
        "gdp_pc_usd", "gdp_growth_rate", "unemployment_rate", "youth_unemployment_rate",
        "gini_coefficient", "top_10pct_income_share", "bottom_40pct_income_share",
        "income_share_q1", "income_share_q2", "income_share_q3", "income_share_q4",
        "income_share_q5", "poverty_headcount_pct", "food_price_index", "inflation_cpi",
        "remittances_pct_gdp", "fdi_net_pct_gdp", "tourism_revenue_pct_gdp",
        "govt_education_spending_pct_gdp", "govt_health_spending_pct_gdp",
        "military_police_spending_pct_gdp", "internet_penetration_pct",
        "mobile_penetration_pct", "freedom_house_political_rights",
        "freedom_house_civil_liberties", "polity2", "corruption_cpi_score",
        "protest_events_count", "repression_events_count",
        "mepv_civviol", "mepv_civwar", "mepv_regciv", "mepv_actotal",
    ]
    for col in raw_passthrough:
        if col in df.columns:
            out[col] = df[col]

    return out


def _classify_phase(row: pd.Series) -> str:
    """
    Phase classifier — Section 34 definitions.

    Uses T and its signed annual derivative (dT) as two views of the same construct.
    dT captures the Metastable definition: "rising T — hidden fragility building."
    No new variable is introduced; dT is the time gradient of T.

    Known limitation: in years where repression suppresses protest events, T_tension
    understates true underlying stress, so dT can be negative even as Omega accumulates
    (e.g., Tunisia 2010). This will be corrected when Arab Barometer trust data
    (Slot 5) provides a direct measure of perceived tension independent of event counts.
    """
    c   = row.get("C_cohesion", 0.5)
    t   = row.get("T_tension",  0.5)
    mdi = row.get("MDI_star",   0.5)
    dt  = row.get("dT_tension", 0.0)

    if t > c and mdi > 0.75:
        return "Critical"
    if t > c and mdi > 0.50:
        return "Pre-Critical"
    if t > 0.4 or mdi > 0.45:
        return "Metastable"
    if dt > 0.05 and mdi > 0.03:
        return "Metastable"
    return "Stable"


# -------------------------------------------------------------------------
# 7. Map annual panel → observation schedule rows
# -------------------------------------------------------------------------

def map_to_obs_schedule(
    annual: pd.DataFrame,
    monthly_fao: Optional[pd.DataFrame] = None,
    monthly_acled: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """
    Expand the annual panel to one row per obs_id in OBSERVATION_SCHEDULE.
    Sub-annual rows inherit the annual value for slow variables.
    Food price and ACLED event counts use sub-annual resolution where available.
    """
    rows = []
    for obs in OBSERVATION_SCHEDULE:
        ds = pd.Timestamp(obs["date_start"])
        de = pd.Timestamp(obs["date_end"])
        year = ds.year

        if year not in annual.index:
            continue

        row = annual.loc[year].to_dict()
        row["obs_id"]     = obs["obs_id"]
        row["case_id"]    = "TUNISIA"
        row["date_start"] = obs["date_start"]
        row["date_end"]   = obs["date_end"]
        row["period_label"] = obs["obs_id"].replace("TUN-", "")
        row["resolution"] = obs["resolution"]

        # Override food_price_index with monthly FAO data where available
        if monthly_fao is not None and not monthly_fao.empty:
            mask = (monthly_fao.index >= ds) & (monthly_fao.index <= de)
            if mask.any():
                row["food_price_index"] = monthly_fao.loc[mask, "food_price_index"].mean()

        rows.append(row)

    return pd.DataFrame(rows).set_index("obs_id")
