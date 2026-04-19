# CLAUDE.md
## Standing Instructions for Claude Code — TSR-1G Project

---

## 1. Project Identity

This repository contains the theoretical and computational work for the **Theory of Social Relativity, Generation 1 (TSR-1G)**, an original interdisciplinary framework that models socioeconomic and political systems using physics-inspired constructs.

The theory treats collective social entities as dynamical masses embedded in a curved, information-laden manifold, drawing from general relativity, thermodynamics, quantum mechanics, polymer physics, political science, economics, and sociology.

---

## 2. First Action on Every Session

Before doing anything else, read the master context file:

```
CONTEXT/TSR-1G_Master_Context_File.md
```

This file is the canonical reference for all TSR-1G constructs, variables, definitions, and constraints. Every modeling decision, variable name, and analytical output must align with this file. Do not proceed with any task until you have read it.

---

## 3. Repository Structure

```
TSR-1G/
├── CONTEXT/          # Theory. Master context file lives here.
├── MODELS/           # Python simulation and analysis code
├── DATA/
│   ├── raw/          # Original data. Never modify.
│   └── processed/    # Cleaned and transformed data
├── OUTPUTS/
│   ├── plots/        # Generated figures
│   ├── hazard_timelines/
│   └── csv/          # Numerical outputs
├── CASES/            # One subfolder per case study
├── NOTEBOOKS/        # Exploratory analysis and visualization
├── CLAUDE.md         # This file
└── README.md
```

---

## 4. Core TSR-1G Constructs to Always Respect

These are non-negotiable definitions. Never redefine, rename, or reinterpret them.

**Social Spacetime Axes:**
- x0: Time evolution
- x1: Economic axis, complex plane. x1 = E' + iE". E' is currency-denominated value. E" is intangible positional and social value.
- x2: Ideological axis, normalized [-1, +1]. -1 is progressive, +1 is conservative.
- x3: Cultural and Conformity axis, normalized [-1, +1]. -1 is iconoclast/skeptic, +1 is conformist/traditionalist.

**Primary State Variables:**
- C: Cohesion* — internal binding strength
- T: Tension* — internal stress field
- MDI*: Mass Disruption Index
- Φ: Cohesion field (spatial distribution of C)
- Ω: Tension field (spatial distribution of T), also a scalar field Ω(x1, x2, x3, t)
- Ψ: Narrative field
- Δτ: Social proper time
- H: Historical Inertia
- Q: Configuration-Manifold coupling quality
- K: Shock absorption capacity
- D: Dissipation capacity
- L: Legitimacy reserve
- Θ: Social Temperature
- S: Social Entropy
- E_m: Maintenance Energy
- CS: Configuration Space magnitude

**Polydispersity Indices:**
- PI_n: Number-average polydispersity index
- PI_w: Weight-average polydispersity index
- PI_z: Z-average polydispersity index
- PI_w/PI_n: Primary stratification diagnostic
- PI_z/PI_w: Ultra-elite concentration diagnostic

**Trust and Threat:**
- T'(α) = cos²(α/2): Trust as function of angular separation in x2-x3 plane
- T"(α) = sin²(α/2) = 1 - T'(α): Threat
- α: Angular separation between Political Sol position and population sub-blob centroid

**CODA Interaction Fields:**
- C_conn: Connection — long-range, network and coordination
- O_ord: Order — short-to-medium range, institutional
- D_dom: Dominion — long-range, center-weighted, accumulative
- A_aut: Autonomy — ultra-short range, individual transformation

**Key Emergent Structures:**
- Political Sol: high-cohesion, high-centralization attractor
- Economic Singularity: extreme wealth concentration with black hole dynamics
- Political Singularity: governance continuity collapse

**Scope Boundary:** TSR-1G models single-mass dynamics only. Do not model interactions between two or more distinct Masses. Multi-mass dynamics are reserved for TSR-2G.

---

## 5. Modeling Principles

- All variable names in code must match TSR-1G notation exactly
- Normalize all variables to [0, 1] unless otherwise specified
- x2 and x3 are normalized to [-1, +1]
- Separate observation from interpretation in all outputs
- Document all proxy assumptions explicitly
- Do not introduce new constructs without noting them as extensions
- Calibration must not erase theory. Weights serve the model architecture.
- Every model output should be traceable to a specific TSR-1G construct

---

## 6. Simulation Engine Guidelines

The TSR Engine Prototype state vector is:

```python
X(t) = [C, T, Psi, H, Q, K, D, L, P, E, R, Theta, S, E_m, CS]
```

Core update equations are defined in CONTEXT/TSR-1G_Master_Context_File.md Section 35.2. Use those as the canonical forms. Any modifications must be documented.

Time steps may represent months, quarters, or years depending on case resolution. Document the chosen resolution in every model file.

---

## 7. Case Study Guidelines

Each case in CASES/ should contain:
- `data/` — case-specific input data
- `outputs/` — plots, CSV, hazard timelines
- `notes.md` — TSR classification, historical inertia summary, key findings
- A Python script named `run_[casename].py`

Primary validated case: Tunisia Arab Spring (2010-2011). Use as the baseline calibration reference.

---

## 8. Output Conventions

File naming:
- `[CaseName]_Phase3_Hazard_Timeline.png`
- `[CaseName]_Best_Hazard_Thresholds_Summary.csv`
- `[CaseName]_TSR_Phase2_3_Analysis.md`

All plots must include:
- Labeled axes with TSR variable names
- Threshold lines for regime classification
- Event markers where applicable
- Publication-ready formatting (clean, minimal, high contrast)

---

## 9. After Every File Update

After modifying any file in this repository, run:

```bash
git add -A && git commit -m "[description of what changed]" && git push
```

Or using the alias:

```bash
git sync "[description of what changed]"
```

---

## 10. Style Rules

- No em dashes in any output
- Use TSR-1G (not TSR-G1) for this generation
- Use TSR-2G, TSR-3G for future generations
- Strict terminology adherence throughout
- Preserve the distinction between Configuration and Manifold at all times
