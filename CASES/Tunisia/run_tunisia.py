"""
TSR-1G Tunisia Arab Spring Case Study
Window: 1990-2011

Entry point for data loading, state vector computation, simulation, and output
generation for the Tunisia case. See notes.md for TSR classification and
observation_schedule.md for the full observation index.

Schema: DATA/schema/v1/
Primary validated case for TSR-1G calibration.
"""

import sqlite3
import pandas as pd
from pathlib import Path

# -------------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = REPO_ROOT / "DATA" / "schema" / "v1"
DB_PATH    = Path(__file__).parent / "data" / "tunisia_tsr.db"
OUTPUT_DIR = Path(__file__).parent / "outputs"

OUTPUT_DIR.mkdir(exist_ok=True)


def init_db(con: sqlite3.Connection) -> None:
    """Create all TSR-1G tables from schema DDL files."""
    con.execute("PRAGMA foreign_keys = ON")
    for sql_file in sorted(SCHEMA_DIR.glob("*.sql")):
        con.executescript(sql_file.read_text())
    con.commit()


def load_panel(con: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql(
        "SELECT * FROM tsr_panel WHERE case_id = 'TUNISIA' ORDER BY date_start",
        con
    )


def load_distributions(con: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql(
        """
        SELECT d.* FROM tsr_distributions d
        JOIN tsr_panel p ON d.obs_id = p.obs_id
        WHERE p.case_id = 'TUNISIA'
        ORDER BY p.date_start, d.group_type, d.group_label
        """,
        con
    )


def compute_polydispersity(dist_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute PI_n, PI_w, PI_z per obs_id from tsr_distributions.
    Write results back to tsr_panel.

    PI_n = SUM(p_i * s_i)
    PI_w = SUM(w_i * s_i^2) / SUM(w_i * s_i)
    PI_z = SUM(w_i * s_i^3) / SUM(w_i * s_i^2)
    """
    g = dist_df.groupby("obs_id")
    records = []
    for obs_id, grp in g:
        p = grp["population_fraction"]
        s = grp["s_i_normalized"]
        w = grp["w_i"]
        PI_n = (p * s).sum()
        PI_w = (w * s**2).sum() / (w * s).sum() if (w * s).sum() > 0 else None
        PI_z = (w * s**3).sum() / (w * s**2).sum() if (w * s**2).sum() > 0 else None
        records.append({
            "obs_id": obs_id,
            "PI_n_x1": PI_n,
            "PI_w_x1": PI_w,
            "PI_z_x1": PI_z,
            "PIw_PIn_ratio": PI_w / PI_n if (PI_n and PI_w) else None,
            "PIz_PIw_ratio": PI_z / PI_w if (PI_w and PI_z) else None,
            "S_entropy": (p * grp["s_Theta_group"]).sum(),
        })
    return pd.DataFrame(records)


def main():
    con = sqlite3.connect(DB_PATH)
    init_db(con)

    panel = load_panel(con)
    if panel.empty:
        print("No data loaded yet. Populate tsr_panel from DATA/raw/ sources.")
        print("See DATA/schema/v1/tsr_proxy_map.sql for source mapping.")
        con.close()
        return

    dist = load_distributions(con)
    poly = compute_polydispersity(dist)
    print(poly)

    con.close()


if __name__ == "__main__":
    main()
