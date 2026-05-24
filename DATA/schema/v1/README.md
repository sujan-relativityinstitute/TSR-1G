# TSR-1G Dataset Schema — Version 1

## Purpose

Defines the relational schema for TSR-1G empirical datasets. Designed for
SQLite (Python/pandas workflow) but portable to PostgreSQL. All files in this
directory define the v1 schema. Do not edit in place — increment to v2/ for
any structural change and record the decision in ../CHANGELOG.md.

## Files

| File | Contents |
|---|---|
| `tsr_panel.sql` | Main state panel — one row per observation period |
| `tsr_distributions.sql` | Group/decile distributional data for polydispersity |
| `tsr_inforay_events.sql` | Discrete information events with interaction properties |
| `tsr_shock_events.sql` | Exogenous shocks mapped to state vector components |
| `tsr_proxy_map.sql` | Static reference: raw indicators to TSR constructs |

## Normalization conventions

- TSR state variables: [0, 1] unless noted
- x2 (ideological axis): [-1, +1]. -1 = progressive, +1 = conservative
- x3 (cultural/conformity axis): [-1, +1]. -1 = iconoclast, +1 = conformist
- Polity5 score: [-10, +10] stored raw, normalized to [0,1] in derived column
- Freedom House scores: stored raw (1-7), inversion applied in derived column
- alpha (angular separation): degrees [0, 180]
- T', T": [0, 1], T' + T" = 1 at all rows

## Usage

```python
import sqlite3, pandas as pd

con = sqlite3.connect("tunisia_tsr.db")
con.execute("PRAGMA foreign_keys = ON")

# Load schema
with open("DATA/schema/v1/tsr_panel.sql") as f:
    con.executescript(f.read())
# repeat for other tables

df = pd.read_sql("SELECT * FROM tsr_panel ORDER BY date_start", con)
```

## Versioning rule

A new version directory (v2/, v3/, ...) is required whenever:
- A column is added, removed, or renamed in any table
- A normalization convention changes
- A new table is introduced
- A proxy definition changes (update tsr_proxy_map AND CHANGELOG)

Backward-compatible additions (new rows in tsr_proxy_map, new case data) do
not require a version bump.
