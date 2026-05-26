# TSR-1G Sortie 1d -- Data Sources
Date: 2026-05-26

All data used in the quarterly structural panel (Tunisia 2008-Q1 through 2011-Q1).

---

## Sortie Naming Convention

Sorties are numbered by TSR generation and lettered sequentially:
- 1G framework: 1a, 1b, 1c ... 1z, 1aa, 1ab, 1ac ... 1az, 1ba, 1bb ...
- 2G framework (future): 2a, 2b, 2c ...
- Each letter sequence exhausts a-z before adding a second letter (same logic as spreadsheet columns).

---

## 1. World Bank (Annual)

| Series | TSR Slot | How Used |
|---|---|---|
| Youth unemployment (% ages 15-24) | Slot 3 | Proxy for frustrated positional gradient (E"/E' tension). Weighted 0.40 in sigma_structural and 0.35 in T_tension. |
| Gini coefficient | Slot 1 | Distributional stress / wealth inequality. Weighted 0.30 in sigma_structural and 0.30 in T_tension. |
| GDP per capita (USD) | Slot 2 | Economic level stress -- inverted (high GDP = low stress). Weighted 0.10 in sigma_structural. |
| Internet penetration (% population) | Slot 9 | Information conductivity -- governs propagation speed when the valve opens. Not in Omega_latent: it explains why 2010 converted and 2008 did not, but does not add to stored pressure. |

Annual values distributed uniformly across all four quarters within each year.
World Bank gaps (2009 Gini, 2011 Gini) filled with nearest available year value.

---

## 2. FAO Food Price Index (Monthly)

| Series | TSR Slot | How Used |
|---|---|---|
| FAO FFPI (base 2002-2004 = 100) | Slot 4 | Material stress / social temperature proxy. Weighted 0.20 in sigma_structural. |

Quarterly averages computed from monthly FAO archive (Jan-Mar, Apr-Jun, Jul-Sep, Oct-Dec).
Sources: FAO Food Outlook 2008, FAO FFPI archive (fao.org).

Quarterly resolution was critical here. The annual 2010 average (106.7) looked unremarkable.
At quarterly resolution: Q1=103.3, Q2=119.0, Q3=129.0, Q4=136.7 -- a clear acceleration.
January 2011 hit 231 (record). The Q4 2010 FFPI acceleration is one of two mechanisms
that restored the precursor signal in Sortie 1d vs the annual Sortie 1c.

Note: the FFPI/214 overlay in Panel B is purely visual. Dividing by 214 (the 2008-Q2 peak)
rescales the raw series to the 0-1 display range for overlay alongside sigma_structural.
It is not used in model calculations. The model uses ffpi_n, normalized within the
precursor window (2008-Q1 to 2010-Q4).

---

## 3. Freedom House (Annual)

| Series | TSR Slot | How Used |
|---|---|---|
| Civil Liberties score (1-7 scale) | Slot 6 | Civil space closure component of sigma_valve. |
| Political Rights score (1-7 scale) | Slot 5 | Political constraint component of sigma_valve. |

Tunisia: CL=5, PR=7 throughout 2008-2011 (7 = worst on both scales).
Source: Freedom House annual country reports (freedomhouse.org).

Key methodological change vs Sorties 1a-1c:
  Sorties 1a-1c used within-Tunisia min-max normalization. Because Tunisia's CL score
  never moved from 5, min-max returned cl_n=1.0 for every year, collapsing sigma_valve
  to near-zero and hiding the suppression signal.

  Sortie 1d uses absolute FH scale: cl_n = (7 - cl_score) / 6.
  Tunisia CL=5 -> cl_n=0.333, meaning the valve is 67% closed from civil liberties alone.
  This is the second mechanism that restored the 2010-Q4 Critical classification.

---

## 4. ACLED (Armed Conflict Location and Event Data)

| Series | TSR Slot | How Used |
|---|---|---|
| Protest event count (annual) | Slot 7 | Kinetic tension proxy in T_tension; also in discharge formula. |
| Repression event count (annual) | Slot 8 | Active force component of sigma_valve (weighted 0.50). |

Annual control totals: 2008=28 protest, 2009=1, 2010=26, 2011=528.
Repression totals: 2008=1, 2009=0, 2010=2, 2011=54 (raw ACLED -- known undercount).

Quarterly distribution method: ACLED annual totals used as control totals, then
redistributed to quarters based on the documented event record from:
  Wikipedia (2008 Tunisian protests), HRW 2008-2011, Amnesty International reports,
  Al Jazeera timeline.

The quarterly repression values reflect research-documented intensity rather than raw
ACLED counts. ACLED significantly undercounts regime repression for this period
(e.g., Gafsa 2008-Q2: 3 confirmed deaths, ~300 arrested; ACLED records 1 event for
the full year).

---

## 5. Civil Space Discrete Event Adjustments (CIVIL_ADJ)

Research-derived quarterly valve closure supplement applied on top of the FH civil
liberties base. Captures within-year events not reflected in annual FH scores.

| Quarter | Event | Adjustment | Sources |
|---|---|---|---|
| 2008-Q3 | Facebook briefly blocked | +0.05 | Nawaat.org, OpenNet Initiative |
| 2008-Q4 | Kalima radio hacked and destroyed | +0.10 | CPJ, HRW |
| 2009-Q1 | Kalima radio destroyed (second wave) | +0.15 | CPJ |
| 2009-Q4 | Post-election crackdown (Ben Ali 89.62%) | +0.10 | HRW, Amnesty International |
| 2010-Q2 | Skype + Flickr blocked | +0.15 | OpenNet Initiative |
| 2010-Q4 | WikiLeaks cables blocked + activist account hacking | +0.25 | Nawaat.org, HRW, CPJ |
| 2011-Q1 | Full censorship escalation + mass account attacks | +0.30 | Al Jazeera, HRW |

Applied as: effective_civil_closure = (1 - cl_n_abs) + civil_adj, clipped to [0, 1].

---

## 6. WikiLeaks Diplomatic Cables

| Cable | Content | Role in Model |
|---|---|---|
| 08TUNIS679 | Ben Ali family corruption: "tiger," frozen yogurt from Saint-Tropez | Event log (Sortie 1b), CIVIL_ADJ context for 2010-Q4 |
| 09TUNIS492 | Regime fragility assessment | Event log (Sortie 1b) |

Source: wikileaks.org/plusd/

Cables released Nov 28, 2010 (2010-Q4). Their significance: US government confirmation
of what Tunisians already knew, with vivid detail -- a T"(alpha) event that changed the
trust geometry nationally. Does not change sigma_structural (fundamentals on the ground);
only the manifold geometry and information conductivity temporarily.

---

## Summary by Sortie

| Sortie | Resolution | Data Used |
|---|---|---|
| 1a | Annual 1990-2011 | World Bank, Freedom House, FAO (annual avg), ACLED, Polity IV |
| 1b | Event log | Research sources (HRW, CPJ, Al Jazeera, WikiLeaks) |
| 1c | Annual 1990-2011 | Same as 1a + Omega_latent derivation |
| 1d | Quarterly 2008-2011 | FAO monthly archive (aggregated), World Bank (annual distributed), Freedom House (absolute scale), ACLED (annual totals, research-distributed), discrete civil space events from CPJ/HRW/Nawaat/OpenNet |
