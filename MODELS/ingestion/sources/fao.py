"""
Fetch FAO Food Price Index (FFPI) — global monthly series.
Tunisia is a net food importer; global FFPI is the dominant food price signal.

Data: FAO publishes the FFPI as a downloadable CSV/Excel at a stable URL.
Also fetches Transparency International CPI for Tunisia (hard-coded fallback).

Outputs:
  DATA/raw/fao/fao_ffpi_monthly.csv   — monthly FFPI 1990-2011
  DATA/raw/fao/fao_ffpi_annual.csv    — annual average FFPI
  DATA/raw/ti/tunisia_cpi.csv         — TI Corruption Perceptions Index
"""

import io
import requests
import pandas as pd
from ..config import RAW_DIR, YEARS

FAO_OUT_MONTHLY = RAW_DIR / "fao" / "fao_ffpi_monthly.csv"
FAO_OUT_ANNUAL  = RAW_DIR / "fao" / "fao_ffpi_annual.csv"
TI_OUT          = RAW_DIR / "ti" / "tunisia_cpi.csv"

# FAO FFPI direct download URL (Excel, updated monthly)
FAO_URL = "https://www.fao.org/fileadmin/templates/worldfood/Reports_and_docs/Food_price_index.xlsx"

# Transparency International CPI for Tunisia (0-10 scale, pre-2012)
# Source: TI historical reports. 10 = cleanest, 0 = most corrupt.
TI_CPI_FALLBACK = {
    1995: 4.0, 1996: 4.1, 1997: 4.3, 1998: 4.9, 1999: 4.7,
    2000: 5.2, 2001: 5.0, 2002: 4.8, 2003: 4.9, 2004: 5.0,
    2005: 4.9, 2006: 4.6, 2007: 4.2, 2008: 4.4, 2009: 4.2,
    2010: 4.3, 2011: 3.8,
}


def fetch_ffpi() -> pd.DataFrame:
    FAO_OUT_MONTHLY.parent.mkdir(parents=True, exist_ok=True)

    if FAO_OUT_MONTHLY.exists():
        print("  Loading FAO FFPI from cache...")
        monthly = pd.read_csv(FAO_OUT_MONTHLY, index_col=0, parse_dates=True)
        return _make_annual(monthly)

    print("  Downloading FAO Food Price Index...")
    try:
        resp = requests.get(FAO_URL, timeout=30)
        resp.raise_for_status()
        xls = pd.read_excel(io.BytesIO(resp.content), sheet_name=None)

        # The FFPI sheet is typically named "Figure 1" or "FFPI" — find it
        monthly = None
        for name, sheet in xls.items():
            sheet.columns = sheet.columns.str.strip()
            if "Food Price Index" in sheet.to_string() or "FFPI" in str(sheet.columns.tolist()):
                # Try to parse: first column = date, second+ = indices
                sheet = sheet.dropna(how="all")
                # Find header row heuristically
                for i, row in sheet.iterrows():
                    if "date" in str(row.values).lower() or "year" in str(row.values).lower():
                        sheet.columns = sheet.iloc[i]
                        sheet = sheet.iloc[i+1:].reset_index(drop=True)
                        break
                date_col = sheet.columns[0]
                sheet[date_col] = pd.to_datetime(sheet[date_col], errors="coerce")
                sheet = sheet.dropna(subset=[date_col]).set_index(date_col)
                # Food Price Index column
                food_cols = [c for c in sheet.columns if "food" in str(c).lower()]
                if food_cols:
                    monthly = sheet[[food_cols[0]]].rename(columns={food_cols[0]: "food_price_index"})
                    monthly = monthly.apply(pd.to_numeric, errors="coerce").dropna()
                    break

        if monthly is None:
            raise ValueError("Could not parse FFPI from Excel structure.")

        monthly.index.name = "date"
        monthly = monthly[monthly.index.year.isin(range(1990, 2012))]
        monthly.to_csv(FAO_OUT_MONTHLY)
        print(f"  Saved monthly FFPI: {FAO_OUT_MONTHLY}")
        return _make_annual(monthly)

    except Exception as e:
        print(f"  WARN: FAO download failed ({e}). food_price_index will be NaN.")
        return pd.DataFrame(index=YEARS, columns=["food_price_index"], dtype=float)


def _make_annual(monthly: pd.DataFrame) -> pd.DataFrame:
    annual = monthly.resample("YE").mean()
    annual.index = annual.index.year
    annual.index.name = "year"
    annual = annual.reindex(YEARS)
    annual.to_csv(FAO_OUT_ANNUAL)
    return annual


def fetch_ti_cpi() -> pd.DataFrame:
    TI_OUT.parent.mkdir(parents=True, exist_ok=True)
    if TI_OUT.exists():
        df = pd.read_csv(TI_OUT, index_col="year")
        df.index = df.index.astype(int)
        return df

    print("  Using hard-coded TI CPI fallback series (1995-2011)...")
    df = pd.DataFrame.from_dict(
        {yr: {"corruption_cpi_score": v} for yr, v in TI_CPI_FALLBACK.items()},
        orient="index",
    )
    df.index.name = "year"
    df = df.reindex(YEARS)
    df.to_csv(TI_OUT)
    return df


def load() -> pd.DataFrame:
    ffpi = fetch_ffpi()
    ti   = fetch_ti_cpi()
    return ffpi.join(ti, how="outer")
