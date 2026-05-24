"""
Load Polity5 data for Tunisia.

Manual download required:
  1. Go to https://www.systemicpeace.org/inscrdata.html
  2. Download "Polity5 Annual Time-Series, 1946-2018" (p5v2018.xls)
  3. Place at: DATA/raw/polity5/p5v2018.xls

Columns used: country, year, polity, polity2, democ, autoc, xconst
Tunisia country code in Polity5: 616 (or match on country name "Tunisia")
"""

import pandas as pd
from ..config import RAW_DIR, COUNTRY_NAME, YEARS

RAW_PATH = RAW_DIR / "polity5" / "p5v2018.xls"
OUT_PATH = RAW_DIR / "polity5" / "tunisia_polity5.csv"

POLITY_COLS = ["year", "polity", "polity2", "democ", "autoc", "xconst"]


def load() -> pd.DataFrame:
    if OUT_PATH.exists():
        df = pd.read_csv(OUT_PATH, index_col="year")
        df.index = df.index.astype(int)
        return df

    if not RAW_PATH.exists():
        print(
            f"MANUAL STEP REQUIRED:\n"
            f"  Download Polity5 from https://www.systemicpeace.org/inscrdata.html\n"
            f"  Place at: {RAW_PATH}\n"
            f"  Skipping Polity5 — columns will be NaN."
        )
        return _empty()

    print("Loading Polity5...")
    raw = pd.read_excel(RAW_PATH)
    raw.columns = raw.columns.str.lower().str.strip()

    # Match Tunisia by country name (handle variations)
    name_col = next(c for c in raw.columns if "country" in c)
    mask = raw[name_col].str.strip().str.lower() == COUNTRY_NAME.lower()
    tun = raw[mask].copy()

    if tun.empty:
        print(f"  WARN: '{COUNTRY_NAME}' not found in Polity5 file.")
        return _empty()

    tun = tun[tun["year"].isin(YEARS)].set_index("year")[
        [c for c in POLITY_COLS[1:] if c in tun.columns]
    ]

    # Recode missing/special values (-66, -77, -88) as NaN
    tun = tun.replace([-66, -77, -88], float("nan"))

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    tun.to_csv(OUT_PATH)
    print(f"  Saved: {OUT_PATH}")
    return tun.reindex(YEARS)


def _empty() -> pd.DataFrame:
    return pd.DataFrame(
        index=YEARS,
        columns=["polity", "polity2", "democ", "autoc", "xconst"],
        dtype=float,
    )
