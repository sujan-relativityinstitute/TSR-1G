"""
Load Freedom House Freedom in the World scores for Tunisia.

Manual download required:
  1. Go to https://freedomhouse.org/report/freedom-world
  2. Download "Aggregate Category and Subcategory Scores" (Excel)
  3. Place at: DATA/raw/freedom_house/freedom_house_aggregate.xlsx

Columns used: political_rights (PR), civil_liberties (CL)
Scale: 1 (most free) to 7 (least free) — inverted in transform.py

Fallback: hard-coded annual series from published reports (1990-2011).
Tunisia's historically reported scores are well-documented.
"""

import pandas as pd
from ..config import RAW_DIR, COUNTRY_NAME, YEARS

RAW_PATH = RAW_DIR / "freedom_house" / "freedom_house_aggregate.xlsx"
OUT_PATH = RAW_DIR / "freedom_house" / "tunisia_fh.csv"

# Fallback: manually compiled from Freedom House annual reports.
# PR = Political Rights, CL = Civil Liberties  (1=best, 7=worst)
# Source: Freedom House "Freedom in the World" historical data.
FALLBACK = {
    1990: (6, 5), 1991: (6, 5), 1992: (6, 5), 1993: (6, 5), 1994: (6, 5),
    1995: (6, 5), 1996: (6, 5), 1997: (6, 5), 1998: (6, 5), 1999: (6, 5),
    2000: (6, 5), 2001: (6, 5), 2002: (6, 5), 2003: (6, 5), 2004: (6, 5),
    2005: (6, 5), 2006: (6, 5), 2007: (6, 5), 2008: (7, 5), 2009: (7, 5),
    2010: (7, 5), 2011: (7, 5),
}


def load() -> pd.DataFrame:
    if OUT_PATH.exists():
        df = pd.read_csv(OUT_PATH, index_col="year")
        df.index = df.index.astype(int)
        return df

    if RAW_PATH.exists():
        df = _parse_excel()
        if df is not None:
            OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(OUT_PATH)
            print(f"  Saved: {OUT_PATH}")
            return df

    print(
        f"Freedom House file not found at {RAW_PATH}.\n"
        f"  Using hard-coded fallback series from published reports."
    )
    df = _from_fallback()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH)
    return df


def _parse_excel() -> pd.DataFrame | None:
    try:
        raw = pd.read_excel(RAW_PATH, sheet_name=None)
        # Sheet names vary by edition; try common patterns
        for sheet_name, sheet in raw.items():
            sheet.columns = sheet.columns.str.strip().str.lower()
            if "country" not in sheet.columns:
                continue
            mask = sheet["country"].str.strip().str.lower() == COUNTRY_NAME.lower()
            tun = sheet[mask]
            if not tun.empty:
                print(f"  Found Tunisia in sheet '{sheet_name}'")
                # Attempt to extract PR/CL across year columns or dedicated cols
                if "pr" in tun.columns and "cl" in tun.columns:
                    result = tun[["year", "pr", "cl"]].set_index("year")
                    result.columns = ["freedom_house_political_rights", "freedom_house_civil_liberties"]
                    return result.reindex(YEARS)
        return None
    except Exception as e:
        print(f"  WARN parsing Freedom House Excel: {e}")
        return None


def _from_fallback() -> pd.DataFrame:
    rows = {yr: {"freedom_house_political_rights": pr, "freedom_house_civil_liberties": cl}
            for yr, (pr, cl) in FALLBACK.items()}
    df = pd.DataFrame.from_dict(rows, orient="index")
    df.index.name = "year"
    return df.reindex(YEARS)
