"""
Ingestion pipeline configuration for TSR-1G Tunisia case study.
All paths, indicator codes, proxy weights, and the observation schedule live here.
"""

from pathlib import Path

# -------------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------------
REPO_ROOT    = Path(__file__).resolve().parents[2]
RAW_DIR      = REPO_ROOT / "DATA" / "raw"
PROCESSED_DIR = REPO_ROOT / "DATA" / "processed" / "tunisia"
CASE_DIR     = REPO_ROOT / "CASES" / "Tunisia"
DB_PATH      = CASE_DIR / "data" / "tunisia_tsr.db"
OUTPUT_DIR   = REPO_ROOT / "OUTPUTS" / "1a"

COUNTRY_WB   = "TUN"          # World Bank country code
COUNTRY_NAME = "Tunisia"      # as used in Polity5 / Freedom House files
YEARS        = list(range(1990, 2012))   # 1990-2011 inclusive

# -------------------------------------------------------------------------
# World Bank indicator codes → raw column names
# -------------------------------------------------------------------------
WB_INDICATORS = {
    # Economic — E'
    "NY.GDP.PCAP.CD":        "gdp_pc_usd",
    "NY.GDP.MKTP.KD.ZG":     "gdp_growth_rate",
    "FP.CPI.TOTL.ZG":        "inflation_cpi",
    "BX.TRF.PWKR.DT.GD.ZS": "remittances_pct_gdp",
    "BX.KLT.DINV.WD.GD.ZS": "fdi_net_pct_gdp",
    "ST.INT.RCPT.CD":        "tourism_receipts_usd",   # computed → pct GDP
    "NY.GDP.MKTP.CD":        "gdp_current_usd",        # denominator for tourism %

    # Labor
    "SL.UEM.TOTL.ZS":        "unemployment_rate",
    "SL.UEM.1524.ZS":        "youth_unemployment_rate",

    # Inequality & poverty
    "SI.POV.GINI":           "gini_coefficient",
    "SI.DST.FRST.20":        "income_share_q1",
    "SI.DST.02ND.20":        "income_share_q2",
    "SI.DST.03RD.20":        "income_share_q3",
    "SI.DST.04TH.20":        "income_share_q4",
    "SI.DST.05TH.20":        "income_share_q5",
    "SI.DST.10TH.10":        "top_10pct_income_share",
    "SI.POV.DDAY":           "poverty_headcount_pct",

    # Government spending — E_m proxies
    "SE.XPD.TOTL.GD.ZS":    "govt_education_spending_pct_gdp",
    "SH.XPD.CHEX.GD.ZS":    "govt_health_spending_pct_gdp",
    "MS.MIL.XPND.GD.ZS":    "military_police_spending_pct_gdp",

    # Connectivity — C_conn proxies
    "IT.NET.USER.ZS":        "internet_penetration_pct",
    "IT.CEL.SETS.P2":        "mobile_penetration_pct",

    # Population
    "SP.POP.TOTL":           "population_total",
    "SP.POP.GROW":           "population_growth_rate",
}

# -------------------------------------------------------------------------
# Proxy weights — must sum to 1.0 within each block
# Source: DATA/schema/v1/tsr_proxy_map.sql
# -------------------------------------------------------------------------
WEIGHTS = {
    # Keys reference only normalized columns computed from the 9 declared structural
    # input slots (Section 38A.2). No placeholder, alias, or derived variable here.
    "C_cohesion":    {"cpi": 0.45, "civil_lib": 0.35, "polity": 0.20},
    "T_tension":     {"youth_unemp": 0.35, "gini": 0.30, "repression": 0.20, "protest": 0.15},
    "Theta":         {"food": 0.45, "unemployment": 0.35, "poverty": 0.20},
    "E_m":           {"education": 0.55, "health": 0.45},
    "CODA_C_conn":   {"internet": 0.60, "mobile": 0.40},
    "CODA_O_ord":    {"cpi": 0.55, "polity": 0.45},
    "CODA_D_dom":    {"military": 0.45, "repression": 0.35, "polity_inv": 0.20},
    "CODA_A_aut":    {"civil_lib": 0.60, "protest": 0.40},
    "MDI_star": {
        "T_tension": 0.20, "Q_mismatch": 0.15, "Psi_div": 0.15,
        "E_economic_stress": 0.15, "R_repression": 0.10,
        "C_cohesion": -0.10, "K_absorption": -0.10, "L_legitimacy": -0.05,
    },
}

# Political Sol position in x2-x3 plane (Ben Ali regime, stable 1990-2011)
# x2: +0.6 (strongly order-preserving, nominally secular center-right)
# x3: +0.7 (high conformity pressure, institutional deference demanded)
SOL_X2 = 0.60
SOL_X3 = 0.70

# Arab Barometer wave years for interpolation anchors
ARAB_BAROMETER_WAVES = {
    2006: {"trust_govt": None, "econ_satisfaction": None, "legitimacy": None},
    2010: {"trust_govt": None, "econ_satisfaction": None, "legitimacy": None},
}

# -------------------------------------------------------------------------
# Observation schedule
# Mirrors CASES/Tunisia/observation_schedule.md — this is the programmatic
# source of truth for obs_ids and date ranges.
# -------------------------------------------------------------------------
OBSERVATION_SCHEDULE = [
    # Annual 1990-2007
    {"obs_id": "TUN-1990",     "date_start": "1990-01-01", "date_end": "1990-12-31", "resolution": "annual"},
    {"obs_id": "TUN-1991",     "date_start": "1991-01-01", "date_end": "1991-12-31", "resolution": "annual"},
    {"obs_id": "TUN-1992",     "date_start": "1992-01-01", "date_end": "1992-12-31", "resolution": "annual"},
    {"obs_id": "TUN-1993",     "date_start": "1993-01-01", "date_end": "1993-12-31", "resolution": "annual"},
    {"obs_id": "TUN-1994",     "date_start": "1994-01-01", "date_end": "1994-12-31", "resolution": "annual"},
    {"obs_id": "TUN-1995",     "date_start": "1995-01-01", "date_end": "1995-12-31", "resolution": "annual"},
    {"obs_id": "TUN-1996",     "date_start": "1996-01-01", "date_end": "1996-12-31", "resolution": "annual"},
    {"obs_id": "TUN-1997",     "date_start": "1997-01-01", "date_end": "1997-12-31", "resolution": "annual"},
    {"obs_id": "TUN-1998",     "date_start": "1998-01-01", "date_end": "1998-12-31", "resolution": "annual"},
    {"obs_id": "TUN-1999",     "date_start": "1999-01-01", "date_end": "1999-12-31", "resolution": "annual"},
    {"obs_id": "TUN-2000",     "date_start": "2000-01-01", "date_end": "2000-12-31", "resolution": "annual"},
    {"obs_id": "TUN-2001",     "date_start": "2001-01-01", "date_end": "2001-12-31", "resolution": "annual"},
    {"obs_id": "TUN-2002",     "date_start": "2002-01-01", "date_end": "2002-12-31", "resolution": "annual"},
    {"obs_id": "TUN-2003",     "date_start": "2003-01-01", "date_end": "2003-12-31", "resolution": "annual"},
    {"obs_id": "TUN-2004",     "date_start": "2004-01-01", "date_end": "2004-12-31", "resolution": "annual"},
    {"obs_id": "TUN-2005",     "date_start": "2005-01-01", "date_end": "2005-12-31", "resolution": "annual"},
    {"obs_id": "TUN-2006",     "date_start": "2006-01-01", "date_end": "2006-12-31", "resolution": "annual"},
    {"obs_id": "TUN-2007",     "date_start": "2007-01-01", "date_end": "2007-12-31", "resolution": "annual"},
    # Quarterly 2008-2009
    {"obs_id": "TUN-2008-Q1",  "date_start": "2008-01-01", "date_end": "2008-03-31", "resolution": "quarterly"},
    {"obs_id": "TUN-2008-Q2",  "date_start": "2008-04-01", "date_end": "2008-06-30", "resolution": "quarterly"},
    {"obs_id": "TUN-2008-Q3",  "date_start": "2008-07-01", "date_end": "2008-09-30", "resolution": "quarterly"},
    {"obs_id": "TUN-2008-Q4",  "date_start": "2008-10-01", "date_end": "2008-12-31", "resolution": "quarterly"},
    {"obs_id": "TUN-2009-Q1",  "date_start": "2009-01-01", "date_end": "2009-03-31", "resolution": "quarterly"},
    {"obs_id": "TUN-2009-Q2",  "date_start": "2009-04-01", "date_end": "2009-06-30", "resolution": "quarterly"},
    {"obs_id": "TUN-2009-Q3",  "date_start": "2009-07-01", "date_end": "2009-09-30", "resolution": "quarterly"},
    {"obs_id": "TUN-2009-Q4",  "date_start": "2009-10-01", "date_end": "2009-12-31", "resolution": "quarterly"},
    # Monthly 2010
    {"obs_id": "TUN-2010-01",  "date_start": "2010-01-01", "date_end": "2010-01-31", "resolution": "monthly"},
    {"obs_id": "TUN-2010-02",  "date_start": "2010-02-01", "date_end": "2010-02-28", "resolution": "monthly"},
    {"obs_id": "TUN-2010-03",  "date_start": "2010-03-01", "date_end": "2010-03-31", "resolution": "monthly"},
    {"obs_id": "TUN-2010-04",  "date_start": "2010-04-01", "date_end": "2010-04-30", "resolution": "monthly"},
    {"obs_id": "TUN-2010-05",  "date_start": "2010-05-01", "date_end": "2010-05-31", "resolution": "monthly"},
    {"obs_id": "TUN-2010-06",  "date_start": "2010-06-01", "date_end": "2010-06-30", "resolution": "monthly"},
    {"obs_id": "TUN-2010-07",  "date_start": "2010-07-01", "date_end": "2010-07-31", "resolution": "monthly"},
    {"obs_id": "TUN-2010-08",  "date_start": "2010-08-01", "date_end": "2010-08-31", "resolution": "monthly"},
    {"obs_id": "TUN-2010-09",  "date_start": "2010-09-01", "date_end": "2010-09-30", "resolution": "monthly"},
    {"obs_id": "TUN-2010-10",  "date_start": "2010-10-01", "date_end": "2010-10-31", "resolution": "monthly"},
    {"obs_id": "TUN-2010-11",  "date_start": "2010-11-01", "date_end": "2010-11-30", "resolution": "monthly"},
    # Weekly Dec 2010
    {"obs_id": "TUN-2010-W49", "date_start": "2010-12-01", "date_end": "2010-12-16", "resolution": "weekly"},
    {"obs_id": "TUN-2010-W50", "date_start": "2010-12-17", "date_end": "2010-12-23", "resolution": "weekly"},
    {"obs_id": "TUN-2010-W51", "date_start": "2010-12-24", "date_end": "2010-12-30", "resolution": "weekly"},
    {"obs_id": "TUN-2010-W52", "date_start": "2010-12-31", "date_end": "2011-01-06", "resolution": "weekly"},
    # Weekly Jan 2011
    {"obs_id": "TUN-2011-W01", "date_start": "2011-01-07", "date_end": "2011-01-13", "resolution": "weekly"},
    {"obs_id": "TUN-2011-W02", "date_start": "2011-01-14", "date_end": "2011-01-14", "resolution": "daily"},
]
