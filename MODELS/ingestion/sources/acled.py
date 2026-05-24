"""
Load ACLED event data for Tunisia (1997-2011).
Aggregates to annual protest_events_count and repression_events_count.

Accepted input formats (checked in order):
  1. Cached annual CSV: DATA/raw/acled/tunisia_acled_annual.csv
  2. Pre-filtered Tunisia CSV: DATA/raw/acled/tunisia_acled_raw.csv
  3. ACLED Africa aggregated XLSX: DATA/raw/acled/Africa_aggregated_data*.xlsx
     (download from https://acleddata.com/conflict-data/download-data-files)
  4. ACLED API (requires ACLED_KEY + ACLED_EMAIL env vars — Research account)

Event type mappings:
  Protests + Riots        → protest_events_count
  Battles + Violence against civilians → repression_events_count
  (Actor filter applied for event-level data; not available in aggregated format)
"""

import os
import glob
from typing import Optional
import requests
import pandas as pd
from ..config import RAW_DIR, YEARS

RAW_PATH  = RAW_DIR / "acled" / "tunisia_acled_raw.csv"
OUT_PATH  = RAW_DIR / "acled" / "tunisia_acled_annual.csv"
ACLED_DIR = RAW_DIR / "acled"

ACLED_API = "https://api.acleddata.com/acled/read"

PROTEST_TYPES    = {"Protests", "Riots"}
REPRESSION_TYPES = {"Violence against civilians", "Battles"}
REPRESSION_ACTORS = {"police", "military", "security", "gendarmerie", "guard", "rassemblement"}


def fetch() -> pd.DataFrame:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    if OUT_PATH.exists():
        df = pd.read_csv(OUT_PATH, index_col="year")
        df.index = df.index.astype(int)
        return df

    raw, fmt = _load_raw()
    if raw is None or raw.empty:
        print("  WARN: No ACLED data. protest/repression counts will be NaN.")
        return _empty()

    return _aggregate(raw, fmt)


def _load_raw() -> tuple:
    """Returns (DataFrame, format_string) where format is 'event' or 'aggregated'."""
    # Pre-filtered Tunisia CSV (event-level)
    if RAW_PATH.exists():
        print(f"  Loading ACLED from: {RAW_PATH}")
        return pd.read_csv(RAW_PATH, low_memory=False), "event"

    # Africa aggregated XLSX (weekly counts by event type)
    xlsx_matches = sorted(glob.glob(str(ACLED_DIR / "Africa_aggregated_data*.xlsx")))
    if xlsx_matches:
        path = xlsx_matches[-1]   # most recent file if multiple
        print(f"  Loading ACLED Africa aggregated XLSX: {path}")
        df = pd.read_excel(path, sheet_name="Sheet1")
        df.columns = df.columns.str.upper()
        tun = df[df["COUNTRY"] == "Tunisia"].copy()
        print(f"  Filtered to {len(tun)} Tunisia rows")
        return tun, "aggregated"

    # API fallback
    key   = os.getenv("ACLED_KEY")
    email = os.getenv("ACLED_EMAIL")
    if key and email:
        return _fetch_api(key, email), "event"

    print(
        "  ACLED: no data found. Place one of:\n"
        f"    Event CSV  : {RAW_PATH}\n"
        f"    Africa XLSX: {ACLED_DIR}/Africa_aggregated_data*.xlsx\n"
        "  Or set ACLED_KEY + ACLED_EMAIL env vars."
    )
    return None, None


def _fetch_api(key: str, email: str) -> Optional[pd.DataFrame]:
    print("  Fetching ACLED via API...")
    frames = []
    for year in range(max(1997, min(YEARS)), max(YEARS) + 1):
        params = {
            "key": key, "email": email,
            "country": "Tunisia", "year": year,
            "fields": "event_date|year|event_type|actor1|fatalities",
            "limit": 5000,
        }
        try:
            r = requests.get(ACLED_API, params=params, timeout=30)
            r.raise_for_status()
            data = r.json().get("data", [])
            if data:
                frames.append(pd.DataFrame(data))
        except Exception as e:
            print(f"    WARN year {year}: {e}")

    if not frames:
        return None
    raw = pd.concat(frames, ignore_index=True)
    raw.to_csv(RAW_PATH, index=False)
    print(f"  Saved raw ACLED: {RAW_PATH}")
    return raw


def _aggregate(raw: pd.DataFrame, fmt: str) -> pd.DataFrame:
    if fmt == "aggregated":
        return _aggregate_from_weekly(raw)
    return _aggregate_from_events(raw)


def _aggregate_from_weekly(raw: pd.DataFrame) -> pd.DataFrame:
    """Handle ACLED Africa aggregated XLSX: weekly rows with EVENTS count column."""
    raw["year"] = pd.to_datetime(raw["WEEK"], errors="coerce").dt.year
    raw["EVENT_TYPE"] = raw["EVENT_TYPE"].str.strip()

    mask_years = raw["year"].isin(YEARS)
    protests = (
        raw[mask_years & raw["EVENT_TYPE"].isin(PROTEST_TYPES)]
        .groupby("year")["EVENTS"].sum()
        .rename("protest_events_count")
    )
    repression = (
        raw[mask_years & raw["EVENT_TYPE"].isin(REPRESSION_TYPES)]
        .groupby("year")["EVENTS"].sum()
        .rename("repression_events_count")
    )

    result = (
        pd.DataFrame(index=YEARS)
        .join(protests, how="left")
        .join(repression, how="left")
        .fillna(0)
        .astype(int)
    )
    result.index.name = "year"
    result.to_csv(OUT_PATH)
    print(f"  Saved ACLED annual: {OUT_PATH}")
    return result


def _aggregate_from_events(raw: pd.DataFrame) -> pd.DataFrame:
    """Handle event-level CSV with actor1 column for state-actor filtering."""
    raw["year"] = pd.to_numeric(raw["year"], errors="coerce").astype("Int64")
    raw["event_type"] = raw["event_type"].str.strip()
    raw["actor1_lower"] = raw["actor1"].fillna("").str.lower()

    protests = (
        raw[raw["event_type"].isin(PROTEST_TYPES)]
        .groupby("year").size()
        .rename("protest_events_count")
    )

    state_mask = raw["actor1_lower"].apply(
        lambda a: any(kw in a for kw in REPRESSION_ACTORS)
    )
    repression = (
        raw[raw["event_type"].isin(REPRESSION_TYPES) & state_mask]
        .groupby("year").size()
        .rename("repression_events_count")
    )

    result = (
        pd.DataFrame(index=YEARS)
        .join(protests, how="left")
        .join(repression, how="left")
        .fillna(0)
        .astype(int)
    )
    result.index.name = "year"
    result.to_csv(OUT_PATH)
    print(f"  Saved ACLED annual: {OUT_PATH}")
    return result


def _empty() -> pd.DataFrame:
    df = pd.DataFrame(
        index=YEARS,
        columns=["protest_events_count", "repression_events_count"],
        dtype=float,
    )
    df.index.name = "year"
    return df


def load() -> pd.DataFrame:
    return fetch()
