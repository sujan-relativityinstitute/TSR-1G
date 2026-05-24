"""
Fetch World Bank indicators for Tunisia via wbgapi.
Saves raw CSV to DATA/raw/world_bank/tunisia_wb_raw.csv.
"""

import pandas as pd
from pathlib import Path

try:
    import wbgapi as wb
except ImportError:
    raise ImportError("Run: pip install wbgapi")

from ..config import COUNTRY_WB, YEARS, WB_INDICATORS, RAW_DIR

OUT_PATH = RAW_DIR / "world_bank" / "tunisia_wb_raw.csv"


def fetch() -> pd.DataFrame:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    print("Fetching World Bank indicators for Tunisia...")
    frames = []
    for code, col in WB_INDICATORS.items():
        try:
            df = wb.data.DataFrame(
                code,
                economy=COUNTRY_WB,
                time=YEARS,
                labels=False,
            )
            # wbgapi returns time as columns, economy as index
            series = df.loc[COUNTRY_WB] if COUNTRY_WB in df.index else df.iloc[0]
            series.name = col
            series.index = series.index.astype(str).str.replace("YR", "").astype(int)
            frames.append(series)
            print(f"  OK  {code} → {col}")
        except Exception as e:
            print(f"  WARN {code} ({col}): {e}")

    raw = pd.DataFrame(frames).T
    raw.index.name = "year"
    raw.index = raw.index.astype(int)
    raw = raw.reindex(YEARS)

    # Derive tourism_revenue_pct_gdp from receipts / GDP
    if "tourism_receipts_usd" in raw.columns and "gdp_current_usd" in raw.columns:
        raw["tourism_revenue_pct_gdp"] = (
            raw["tourism_receipts_usd"] / raw["gdp_current_usd"] * 100
        )

    # Derive bottom_40_income_share
    if "income_share_q1" in raw.columns and "income_share_q2" in raw.columns:
        raw["bottom_40pct_income_share"] = raw["income_share_q1"] + raw["income_share_q2"]

    raw.to_csv(OUT_PATH)
    print(f"Saved: {OUT_PATH}  ({len(raw)} rows, {len(raw.columns)} columns)")
    return raw


def load() -> pd.DataFrame:
    if not OUT_PATH.exists():
        return fetch()
    df = pd.read_csv(OUT_PATH, index_col="year")
    df.index = df.index.astype(int)
    return df
