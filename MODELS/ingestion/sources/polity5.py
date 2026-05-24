"""
Load Polity5 and MEPV data for Tunisia.

Polity5 Annual Time-Series (p5v2018.xls):
  Download: https://www.systemicpeace.org/inscrdata.html
  Place at: DATA/raw/polity5/p5v2018.xls
  Columns: polity, polity2, democ, autoc, xconst
  Note: 2011 uses polity2=4.0 (imputed transition value); -88/-66/-77 → NaN

Major Episodes of Political Violence (MEPV2012ex.xls):
  Download: https://www.systemicpeace.org/inscrdata.html
  Place at: DATA/raw/polity5/MEPV2012ex.xls
  Columns: civviol, civwar, regciv, actotal
  Tunisia civviol/civwar=0 throughout (no armed conflict) — confirms narrative cascade.
  regciv = regional civil violence from neighbors (Algeria 1991-2000, Libya 2011).
"""

import pandas as pd
from ..config import RAW_DIR, COUNTRY_NAME, YEARS

P5_PATH   = RAW_DIR / "polity5" / "p5v2018.xls"
MEPV_PATH = RAW_DIR / "polity5" / "MEPV2012ex.xls"
OUT_PATH  = RAW_DIR / "polity5" / "tunisia_polity5.csv"

POLITY_COLS = ["polity", "polity2", "democ", "autoc", "xconst"]
MEPV_COLS   = ["civviol", "civwar", "regciv", "actotal"]


def load() -> pd.DataFrame:
    if OUT_PATH.exists():
        df = pd.read_csv(OUT_PATH, index_col="year")
        df.index = df.index.astype(int)
        return df

    p5   = _load_polity5()
    mepv = _load_mepv()

    combined = p5.join(mepv, how="outer").reindex(YEARS)
    combined.index.name = "year"

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(OUT_PATH)
    print(f"  Saved: {OUT_PATH}")
    return combined


def _load_polity5() -> pd.DataFrame:
    if not P5_PATH.exists():
        print(
            f"  Polity5 file not found at {P5_PATH}.\n"
            "  Download p5v2018.xls from https://www.systemicpeace.org/inscrdata.html\n"
            "  Polity columns will be NaN."
        )
        return _empty_polity5()

    print("  Loading Polity5...")
    raw = pd.read_excel(P5_PATH)
    raw.columns = raw.columns.str.lower().str.strip()

    name_col = next(c for c in raw.columns if "country" in c)
    tun = raw[raw[name_col].str.strip().str.lower() == COUNTRY_NAME.lower()].copy()

    if tun.empty:
        print(f"  WARN: '{COUNTRY_NAME}' not found in Polity5.")
        return _empty_polity5()

    tun = tun[tun["year"].isin(YEARS)].set_index("year")
    avail = [c for c in POLITY_COLS if c in tun.columns]
    tun = tun[avail].copy()

    # Identify interruption years before recoding (polity=-88 = regime transition)
    # For TSR purposes we model the pre-collapse regime, so transition-year polity2
    # (which carries the post-transition imputed score) should also be set to NaN
    # and interpolated from the preceding autocratic value.
    transition_years = tun.index[tun["polity"] == -88] if "polity" in tun.columns else []

    # Recode all special codes → NaN
    tun = tun.replace([-66, -77, -88], float("nan"))

    # polity2 for transition years: imputed value reflects post-transition democracy,
    # not the pre-collapse state. Set to NaN so interpolation gives the regime value.
    if "polity2" in tun.columns and len(transition_years) > 0:
        tun.loc[transition_years, "polity2"] = float("nan")

    return tun


def _load_mepv() -> pd.DataFrame:
    if not MEPV_PATH.exists():
        print(f"  MEPV file not found at {MEPV_PATH}. Regional violence columns will be NaN.")
        return _empty_mepv()

    print("  Loading MEPV (Major Episodes of Political Violence)...")
    raw = pd.read_excel(MEPV_PATH)
    raw.columns = raw.columns.str.lower().str.strip()

    name_col = next((c for c in raw.columns if "country" in c), None)
    if name_col is None:
        return _empty_mepv()

    tun = raw[raw[name_col].str.strip().str.lower() == COUNTRY_NAME.lower()].copy()
    if tun.empty:
        return _empty_mepv()

    tun = tun[tun["year"].isin(YEARS)].set_index("year")
    avail = [c for c in MEPV_COLS if c in tun.columns]
    tun = tun[avail].rename(columns={c: f"mepv_{c}" for c in avail})
    return tun


def _empty_polity5() -> pd.DataFrame:
    return pd.DataFrame(index=YEARS, columns=POLITY_COLS, dtype=float)


def _empty_mepv() -> pd.DataFrame:
    return pd.DataFrame(index=YEARS, columns=[f"mepv_{c}" for c in MEPV_COLS], dtype=float)
