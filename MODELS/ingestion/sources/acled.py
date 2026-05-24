"""
Fetch ACLED event data for Tunisia (1997-2011).
Aggregates to annual protest_events_count and repression_events_count.

Requires free API key from https://developer.acleddata.com/
Set in environment or .env file:
  ACLED_KEY=your_key
  ACLED_EMAIL=your_email

If no API key: falls back to manually placed CSV at DATA/raw/acled/tunisia_acled_raw.csv
Download from: https://acleddata.com/data-export-tool/ (select Tunisia, 1997-2011)
"""

import os
import requests
import pandas as pd
from pathlib import Path
from ..config import RAW_DIR, YEARS

RAW_PATH = RAW_DIR / "acled" / "tunisia_acled_raw.csv"
OUT_PATH = RAW_DIR / "acled" / "tunisia_acled_annual.csv"

ACLED_API = "https://api.acleddata.com/acled/read"

# ACLED event type classifications
PROTEST_TYPES = {"Protests"}
REPRESSION_TYPES = {"Violence against civilians", "Battles"}
REPRESSION_ACTORS = {"police", "military", "security", "gendarmerie", "guard", "rassemblement"}


def fetch() -> pd.DataFrame:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    if OUT_PATH.exists():
        df = pd.read_csv(OUT_PATH, index_col="year")
        df.index = df.index.astype(int)
        return df

    raw = _load_raw()
    if raw is None or raw.empty:
        print("  WARN: No ACLED data. protest/repression counts will be NaN.")
        return _empty()

    return _aggregate(raw)


def _load_raw() -> pd.DataFrame | None:
    if RAW_PATH.exists():
        print(f"  Loading ACLED from manual file: {RAW_PATH}")
        return pd.read_csv(RAW_PATH, low_memory=False)

    key   = os.getenv("ACLED_KEY")
    email = os.getenv("ACLED_EMAIL")
    if not key or not email:
        print(
            "  MANUAL STEP REQUIRED for ACLED data:\n"
            "  Option A: Set ACLED_KEY and ACLED_EMAIL environment variables.\n"
            "  Option B: Download Tunisia 1997-2011 from https://acleddata.com/data-export-tool/\n"
            f"            and place CSV at: {RAW_PATH}"
        )
        return None

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
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    raw.to_csv(RAW_PATH, index=False)
    print(f"  Saved raw ACLED: {RAW_PATH}")
    return raw


def _aggregate(raw: pd.DataFrame) -> pd.DataFrame:
    raw["year"] = pd.to_numeric(raw["year"], errors="coerce").astype("Int64")
    raw["event_type"] = raw["event_type"].str.strip()
    raw["actor1_lower"] = raw["actor1"].fillna("").str.lower()

    # Protests
    protests = (
        raw[raw["event_type"].isin(PROTEST_TYPES)]
        .groupby("year")
        .size()
        .rename("protest_events_count")
    )

    # Repression: state violence events
    state_mask = raw["actor1_lower"].apply(
        lambda a: any(kw in a for kw in REPRESSION_ACTORS)
    )
    repression = (
        raw[raw["event_type"].isin(REPRESSION_TYPES) & state_mask]
        .groupby("year")
        .size()
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
