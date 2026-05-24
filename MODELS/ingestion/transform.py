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
    """
    df = panel.copy()
    W  = WEIGHTS

    # Normalize key raw indicators once
    youth_unemp_n = minmax(df["youth_unemployment_rate"].fillna(df["youth_unemployment_rate"].median()))
    gini_n        = minmax(df["gini_coefficient"].fillna(df["gini_coefficient"].median()))
    unemp_n       = minmax(df["unemployment_rate"].fillna(df["unemployment_rate"].median()))
    food_n        = minmax(df["food_price_index"].fillna(df["food_price_index"].median()))
    poverty_n     = minmax(df["poverty_headcount_pct"].fillna(0))
    informal_n    = pd.Series(0.5, index=df.index)   # no direct data; use neutral 0.5

    # Freedom House: 1=best, 7=worst → invert to [0,1]
    cl_n = minmax(df["freedom_house_civil_liberties"].fillna(5), invert=True)
    pr_n = minmax(df["freedom_house_political_rights"].fillna(6), invert=True)

    # Polity5: -10 to +10 → [0,1] where 1=most democratic
    polity_n = ((df["polity2"].fillna(-5) + 10) / 20).clip(0, 1)
    polity_inv = 1.0 - polity_n   # high = autocratic = high D_dom

    # CPI: 0-10 scale (pre-2012), 10=cleanest → normalize, 1=cleanest
    cpi_n = minmax(df["corruption_cpi_score"].fillna(4.5))

    # Press freedom: RSF not in raw data; proxy from civil liberties
    press_n = cl_n

    # ACLED counts normalized
    protest_n    = minmax(df["protest_events_count"].fillna(0))
    repression_n = minmax(df["repression_events_count"].fillna(0))

    # Military spending normalized
    mil_n = minmax(df["military_police_spending_pct_gdp"].fillna(
        df["military_police_spending_pct_gdp"].median()))

    # Connectivity normalized
    internet_n = minmax(df["internet_penetration_pct"].fillna(0))
    mobile_n   = minmax(df["mobile_penetration_pct"].fillna(0))

    # NGO density: no direct WB data; placeholder
    ngo_n   = pd.Series(0.3, index=df.index)
    union_n = pd.Series(0.4, index=df.index)

    # vdem: not fetched; proxy from polity + freedom house composite
    vdem_n = (polity_n * 0.6 + cl_n * 0.4).clip(0, 1)

    # MEPV: internal civil violence (0 throughout Tunisia → confirms low armed-conflict K)
    # mepv_civviol scale 0-10; normalize. Adds to repression composite when non-zero.
    if "mepv_civviol" in df.columns:
        civviol_n = minmax(df["mepv_civviol"].fillna(0))
    else:
        civviol_n = pd.Series(0.0, index=df.index)

    # MEPV: regional civil violence (neighbors — Algeria, Libya) → external Omega pressure
    if "mepv_regciv" in df.columns:
        regciv_n = minmax(df["mepv_regciv"].fillna(df["mepv_regciv"].median()
                          if "mepv_regciv" in df.columns else 0))
    else:
        regciv_n = pd.Series(0.0, index=df.index)

    # Education + health spending normalized
    edu_n  = minmax(df["govt_education_spending_pct_gdp"].fillna(
        df["govt_education_spending_pct_gdp"].median()))
    hlth_n = minmax(df["govt_health_spending_pct_gdp"].fillna(
        df["govt_health_spending_pct_gdp"].median()))
    # Social spending proxy: no WB column; estimate from 1 - military fraction
    soc_n  = (1.0 - mil_n).clip(0, 1)

    # ---- CODA forces ----
    norm = pd.DataFrame(index=df.index)
    norm["internet"] = internet_n
    norm["mobile"]   = mobile_n
    norm["ngo"]      = ngo_n
    norm["union"]    = union_n
    norm["vdem"]     = vdem_n
    norm["cpi"]      = cpi_n
    norm["polity"]   = polity_n
    norm["polity_inv"] = polity_inv
    norm["military"] = mil_n
    norm["repression"] = repression_n
    norm["press_freedom"] = press_n
    norm["civil_lib"] = cl_n
    norm["protest"]  = protest_n
    norm["trust"]    = pd.Series(0.5, index=df.index)   # placeholder; Arab Barometer needed
    norm["education"] = edu_n
    norm["health"]   = hlth_n
    norm["social"]   = soc_n
    norm["civviol"]  = civviol_n
    norm["regciv"]   = regciv_n

    out = pd.DataFrame(index=df.index)

    out["CODA_C_conn"]  = wmean(norm, W["CODA_C_conn"])
    out["CODA_O_ord"]   = wmean(norm, W["CODA_O_ord"])
    out["CODA_D_dom"]   = wmean(norm, W["CODA_D_dom"])
    out["CODA_A_aut"]   = wmean(norm, W["CODA_A_aut"])
    out["CODA_imbalance"] = (
        (out["CODA_D_dom"] - out["CODA_A_aut"]).abs() +
        (out["CODA_O_ord"] - out["CODA_C_conn"]).abs()
    ).clip(0, 1) / 2

    # ---- Core state variables ----
    out["C_cohesion"]    = wmean(norm, W["C_cohesion"])
    out["T_tension"]     = wmean(norm, W["T_tension"])
    out["Theta_social_temp"] = wmean(norm, W["Theta"])
    out["E_m_maintenance"]   = wmean(norm, W["E_m"])

    # Legitimacy: proxy from trust + civil liberties; will be updated from Arab Barometer
    out["L_legitimacy"] = (norm["trust"] * 0.5 + cl_n * 0.3 + cpi_n * 0.2).clip(0, 1)

    # Repression (civviol adds MEPV armed-violence magnitude when non-zero)
    out["R_repression"] = (repression_n * 0.45 + (1 - pr_n) * 0.30 + (1 - cl_n) * 0.15 + civviol_n * 0.10).clip(0, 1)

    # Political centralization (high autocracy = high P)
    out["P_centralization"] = polity_inv

    # Economic stress
    e_stress_norm = pd.DataFrame({
        "youth_unemp": youth_unemp_n,
        "gini": gini_n,
        "food": food_n,
        "inflation": minmax(df["inflation_cpi"].fillna(df["inflation_cpi"].median())),
    })
    out["E_economic_stress"] = wmean(e_stress_norm, {"youth_unemp": 0.30, "gini": 0.25, "food": 0.25, "inflation": 0.20})

    # Narrative coherence / divergence
    out["Psi_div"]      = (out["T_tension"] * 0.5 + (1 - press_n) * 0.5).clip(0, 1)
    out["Psi_coherence"] = 1.0 - out["Psi_div"]

    # Q: config-manifold coupling (high corruption + high tension = low Q)
    out["Q_coupling"] = ((1 - out["T_tension"]) * 0.5 + cpi_n * 0.3 + cl_n * 0.2).clip(0, 1)

    # K: shock absorption capacity (regional civil violence from neighbors depletes K)
    out["K_absorption"] = (vdem_n * 0.35 + (1 - out["T_tension"]) * 0.30 + edu_n * 0.25 + (1 - regciv_n) * 0.10).clip(0, 1)

    # D: dissipation capacity (press freedom, civil liberties, protest legitimacy)
    out["D_dissipation"] = (press_n * 0.4 + cl_n * 0.4 + protest_n * 0.2).clip(0, 1)

    # Historical Inertia: slow-moving; high throughout for Tunisia (deep H field)
    # Modeled as a function of time since last rupture (1987 Ben Ali coup)
    years = pd.Series(df.index, index=df.index)
    out["H_inertia"] = ((years - 1987) / (2011 - 1987)).clip(0, 1) * 0.4 + 0.5

    # Social Temperature (elite vs majority)
    # Elite ~ 10% of population; assume Theta_elite ≈ 0.1 (cold island)
    out["Theta_elite"]    = pd.Series(0.10, index=df.index)
    out["Theta_majority"] = (out["Theta_social_temp"] * 1.1).clip(0, 1)

    # Temperature gradient hazard
    p_majority = 0.90
    out["TG_hazard"] = (out["Theta_majority"] - out["Theta_elite"]) * p_majority

    # Social entropy S = Sigma p_i * s(Theta_i)  with s(Theta)=Theta (linear)
    out["S_entropy"] = (
        0.10 * out["Theta_elite"] + 0.90 * out["Theta_majority"]
    ).clip(0, 1)

    # Configuration space: grows with population growth and internet channels
    pop_growth_n = minmax(df["population_growth_rate"].fillna(
        df["population_growth_rate"].median()))
    out["CS_config_space"] = (
        0.50 * minmax(years.astype(float)) +   # baseline growth over time
        0.30 * internet_n +
        0.20 * pop_growth_n
    ).clip(0, 1)

    # Event Horizon proximity: proxy as CS growth rate / K_absorption
    out["EH_proximity"] = (out["CS_config_space"].diff().clip(0, None) /
                           out["K_absorption"].replace(0, 0.01)).clip(0, 3)

    # Omega-accessibility mismatch: stress accumulates where resolution is lowest
    out["OA_mismatch"] = (out["T_tension"] * (1 - out["D_dissipation"])).clip(0, 1)

    # Social proper time compression: delta_tau
    T_change = out["T_tension"].diff().abs().fillna(0)
    out["delta_tau"] = 1 / (1 + 3 * T_change + 2 * out["Psi_div"])

    # x1 E' and E" proxies
    out["x1_E_prime_proxy"] = minmax(df["gdp_pc_usd"].fillna(
        df["gdp_pc_usd"].median()))
    out["x1_E_double_prime_proxy"] = minmax(
        (df["youth_unemployment_rate"] / df["unemployment_rate"].replace(0, np.nan)).fillna(1.0)
    )

    # MDI* composite
    mdi_inputs = pd.DataFrame({
        "T_tension":       out["T_tension"],
        "Q_mismatch":      1 - out["Q_coupling"],
        "Psi_div":         out["Psi_div"],
        "E_economic_stress": out["E_economic_stress"],
        "R_repression":    out["R_repression"],
        "C_cohesion":      out["C_cohesion"],
        "K_absorption":    out["K_absorption"],
        "L_legitimacy":    out["L_legitimacy"],
    }, index=df.index)

    W_mdi = W["MDI_star"]
    out["MDI_star"] = sum(
        mdi_inputs[col] * w for col, w in W_mdi.items()
    ).clip(0, 1)

    # Regime phase classification
    out["regime_phase"] = out.apply(_classify_phase, axis=1)

    # Join trust-threat and polydispersity
    out = out.join(tt).join(pi)

    # Pass through selected raw columns
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
    c = row.get("C_cohesion", 0.5)
    t = row.get("T_tension",  0.5)
    mdi = row.get("MDI_star", 0.5)
    if t > c and mdi > 0.75:
        return "Critical"
    if t > c and mdi > 0.55:
        return "Pre-Critical"
    if t > 0.4 or mdi > 0.45:
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
