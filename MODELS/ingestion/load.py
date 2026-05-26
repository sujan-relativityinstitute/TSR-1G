"""
Write processed TSR panels to SQLite and CSV.

Targets:
  CASES/Tunisia/data/tunisia_tsr.db
    - tsr_annual_panel    : one row per year (1990-2011), all TSR variables
    - tsr_obs_panel       : one row per obs_id from observation schedule

  OUTPUTS/csv/
    - Tunisia_annual_panel.csv
    - Tunisia_obs_panel.csv
"""

import sqlite3
import pandas as pd
from pathlib import Path

from .config import DB_PATH, OUTPUT_DIR, PROCESSED_DIR


def write_to_sqlite(annual: pd.DataFrame, obs: pd.DataFrame) -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        annual.to_sql("tsr_annual_panel", conn, if_exists="replace", index=True)
        obs.to_sql("tsr_obs_panel",    conn, if_exists="replace", index=True)
        conn.commit()
        print(f"  Wrote SQLite: {DB_PATH}")
        print(f"    tsr_annual_panel : {len(annual)} rows x {annual.shape[1]} cols")
        print(f"    tsr_obs_panel    : {len(obs)} rows x {obs.shape[1]} cols")
    finally:
        conn.close()


def write_to_csv(annual: pd.DataFrame, obs: pd.DataFrame) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    sortie      = OUTPUT_DIR.name
    annual_path = OUTPUT_DIR / f"{sortie} Tunisia_annual_panel.csv"
    obs_path    = OUTPUT_DIR / f"{sortie} Tunisia_obs_panel.csv"

    annual.to_csv(annual_path)
    obs.to_csv(obs_path)

    # Also write to processed/ for internal pipeline use
    annual.to_csv(PROCESSED_DIR / "annual_panel.csv")
    obs.to_csv(PROCESSED_DIR / "obs_panel.csv")

    print(f"  Wrote CSV: {annual_path}")
    print(f"  Wrote CSV: {obs_path}")


def save(annual: pd.DataFrame, obs: pd.DataFrame) -> None:
    write_to_sqlite(annual, obs)
    write_to_csv(annual, obs)
