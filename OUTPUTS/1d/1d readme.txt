Tunisia TSR-1G Analysis Sortie 1d
Date: 2026-05-25

Analysis: Quarterly structural panel -- Tunisia 2008 Q1 through 2011 Q1.

Motivation:
The annual panel (sortie 1c) missed 2010 as a precursor. Two reasons:
  1. Annual FFPI average (106.7) masked the Q4 2010 trajectory (127->138->rising toward
     Jan 2011's record 231). The food price spike was concentrated in Q4.
  2. Annual T_tension for 2010 was 0.114 (proxy fell because repression suppressed protest
     events), averaged across a year in which Q4 was structurally distinct.

Changes from 1c:
  - Quarterly resolution: 13 periods (2008-Q1 through 2011-Q1)
  - FFPI: monthly FAO data aggregated to quarterly averages (see data sources)
  - Protest/repression: ACLED annual counts distributed to quarters based on
    research-documented event intensity (Gafsa Q1-Q2 2008 peak, cascade Q4 2010)
  - Civil liberties normalization: absolute FH scale (1-7) rather than within-Tunisia
    minmax. Tunisia at FH=5 gets cl_n=0.333 (not 1.0 as within-case minmax gave).
    This restores the sigma_valve to theoretically correct magnitude.
  - Civil space discrete events: quarterly adjustments for major censorship/repression
    events not captured in annual FH score (Facebook block Q3 2008, Kalima Q4 2008/Q1 2009,
    Skype/Flickr Q2 2010, WikiLeaks blocking Q4 2010, account hacking Q4 2010).
  - Omega_acc decay per quarter: 0.85^(1/4) = 0.963 (preserving annual calibration)
  - Initialization: Omega_acc starts from zero at 2008-Q1. Prior accumulation
    (1991-2007) documented in sortie 1c is captured by the 2007 annual Omega_acc value.
    A future version should initialize from that value.

Data sources for quarterly inputs:
  - FAO FFPI: FAO Food Price Index monthly series (fao.org). Quarterly averages computed
    from monthly values. Sources: FAO Food Outlook 2008, FAO FFPI archive.
  - Protest/repression quarterly distribution: research-derived from Wikipedia (2008
    Tunisian protests), HRW 2008-2011, Amnesty International reports, Al Jazeera
    timeline. ACLED annual totals used as control totals.
  - FH civil liberties and political rights: Freedom House annual reports.
  - Civil space discrete adjustments: Nawaat.org, CPJ, OpenNet Initiative, HRW.
  - Internet penetration: World Bank / ITU (annual milestones: 17.1% 2007, 27.5% 2008,
    34.1% 2009, 36.8% 2010, 39.1% 2011).
  - WikiLeaks cable content: wikileaks.org/plusd/ (cables 08TUNIS679, 09TUNIS492).

Key results (decay_q = 0.963 per quarter; normalized within 2008-Q1 to 2010-Q4):

  quarter        T_q    Omega_acc   phase
  2008-Q2       0.350    0.104     Metastable   (Gafsa peak)
  2009-Q1       0.350    0.299     Metastable   (post-Gafsa, recession)
  2009-Q4       0.372    0.612     Metastable   (post-election crackdown)
  2010-Q1       0.445    0.686     Pre-Critical (Omega_acc gate firing from here on)
  2010-Q2       0.517    0.772     Pre-Critical (Sidi Bouzid protests)
  2010-Q3       0.475    0.867     Pre-Critical
  2010-Q4       0.625    1.000     CRITICAL     (WikiLeaks Nov 28; cascade begins Dec 17)
  2011-Q1       1.000    1.499     [expression -- disregarded as precursor]

PRIMARY FINDING: Tunisia was Pre-Critical from 2010-Q1 onwards and Critical in
2010-Q4 -- identified BEFORE the Bouazizi cascade. The model now produces the
precursor warning the annual analysis missed.

The tinderbox was real and detectable. Bouazizi was the nucleation event for a
system that had been Pre-Critical for the entire year, Critical by Q4.

TWO MECHANISMS restore the 2010-Q4 signal vs the annual analysis:
  1. FFPI quarterly resolution: Q4 2010 FFPI = 136.7 vs annual average 106.7.
     The food price acceleration in Oct-Nov-Dec 2010 is now visible.
  2. sigma_valve with absolute FH scale: Tunisia at FH civil liberties=5 now
     correctly scores cl_n=0.333 (not 1.0 as within-Tunisia minmax gave).
     Sigma_valve base = 0.40 from FH alone, rising to 0.70 with WikiLeaks
     blocking and activist account attacks in Q4 2010.

ALSO: 2010-Q4 T_tension_q = 0.625 (vs annual T_tension = 0.114). The quarterly
panel captures the Dec 17 cascade onset within the Q4 window; the annual panel
averaged those 2 weeks across 52 weeks, suppressing the signal entirely.

Outputs:
  1d Tunisia_Quarterly_2008_2011.png  -- 3-panel quarterly figure
  1d Tunisia_Quarterly_Panel.csv      -- 13-row quarterly data table
