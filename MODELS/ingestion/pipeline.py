"""
TSR-1G Tunisia ingestion pipeline.

Usage:
    python -m MODELS.ingestion.pipeline          # from repo root
    python -m MODELS.ingestion.pipeline --force  # re-fetch even if cached

Steps:
  1. Fetch raw data from each source
  2. Merge into annual panel
  3. Interpolate short gaps
  4. Compute derived indicators (polydispersity, trust-threat)
  5. Compute full TSR state vector
  6. Map annual panel → observation schedule rows
  7. Save to SQLite + CSV
"""

import argparse
import sys
from pathlib import Path

# Ensure repo root is on the path when run as a module
_repo_root = Path(__file__).resolve().parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from MODELS.ingestion.sources import world_bank, polity5, freedom_house, fao, acled
from MODELS.ingestion import transform, load
from MODELS.ingestion.config import DB_PATH


def run(force: bool = False) -> None:
    if force:
        _clear_cache()

    # ---- 1. Fetch raw sources ----
    print("\n[1/7] Fetching World Bank indicators...")
    wb = world_bank.load()

    print("\n[2/7] Loading Polity5...")
    pol = polity5.load()

    print("\n[3/7] Loading Freedom House...")
    fh = freedom_house.load()

    print("\n[4/7] Fetching FAO FFPI + TI CPI...")
    fao_df = fao.load()
    # Keep monthly FFPI separate for sub-annual override
    monthly_fao = _load_monthly_fao()

    print("\n[5/7] Fetching ACLED event data...")
    acl = acled.load()

    # ---- 2. Merge ----
    print("\n[6/7] Merging and transforming...")
    panel = transform.merge_raw(wb, pol, fh, fao_df, acl)

    # ---- 3. Interpolate gaps ----
    panel, interp_flags = transform.interpolate_gaps(panel, max_gap=3)
    n_interp = interp_flags.sum().sum()
    if n_interp:
        print(f"  Interpolated {n_interp} cell(s) across {interp_flags.any(axis=1).sum()} year(s)")

    # ---- 4. Derived indicators ----
    pi = transform.compute_polydispersity(panel)
    tt = transform.compute_trust_threat(panel)

    # ---- 5. TSR state vector ----
    annual = transform.compute_tsr_variables(panel, tt, pi)

    # ---- 6. Map to observation schedule ----
    obs = transform.map_to_obs_schedule(annual, monthly_fao=monthly_fao)

    # ---- 7. Save ----
    print("\n[7/7] Saving outputs...")
    load.save(annual, obs)

    print("\nPipeline complete.")
    print(f"  Annual rows : {len(annual)} (1990-2011)")
    print(f"  Obs rows    : {len(obs)} observation points")
    print(f"  Database    : {DB_PATH}")
    _print_coverage(annual)


def _load_monthly_fao():
    from MODELS.ingestion.config import RAW_DIR
    import pandas as pd
    monthly_path = RAW_DIR / "fao" / "fao_ffpi_monthly.csv"
    if monthly_path.exists():
        df = pd.read_csv(monthly_path, index_col=0, parse_dates=True)
        return df
    return None


def _clear_cache():
    from MODELS.ingestion.config import RAW_DIR, PROCESSED_DIR, DB_PATH
    import shutil
    print("  --force: clearing cached outputs (raw data preserved)")
    if PROCESSED_DIR.exists():
        shutil.rmtree(PROCESSED_DIR)
    if DB_PATH.exists():
        DB_PATH.unlink()


def _print_coverage(annual):
    total_cells = annual.shape[0] * annual.shape[1]
    missing = annual.isna().sum().sum()
    pct_complete = 100 * (1 - missing / total_cells)
    print(f"\n  Data coverage: {pct_complete:.1f}% complete ({missing} NaN cells)")

    core_vars = ["C_cohesion", "T_tension", "MDI_star", "L_legitimacy", "Q_coupling"]
    print("  Core TSR variable coverage:")
    for v in core_vars:
        if v in annual.columns:
            n_ok = annual[v].notna().sum()
            print(f"    {v:<25} {n_ok}/22 years")

    print("\n  Regime phases by year:")
    if "regime_phase" in annual.columns:
        for yr, phase in annual["regime_phase"].items():
            print(f"    {yr}: {phase}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TSR-1G Tunisia ingestion pipeline")
    parser.add_argument("--force", action="store_true", help="Clear cached outputs and re-run")
    args = parser.parse_args()
    run(force=args.force)
