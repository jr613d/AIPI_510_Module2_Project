# Limitations

What a reader should know before quoting a number from `dashboard/seats_and_voices.html`.
Workstream-specific caveats and dead ends are in each `results/ws_*/findings.md`.

## Design
- Nothing here is confirmatory. The only pre-registered test is the Module 2 parent vs non-parent
  comparison. Every test on the page was chosen after looking at the data; families of tests are
  Benjamini-Hochberg corrected, but p-values should be read as flags.
- The brief given to the workstreams described Glenwood as a closure "candidate". The board voted
  to close it on June 4, 2026, moved its Mandarin dual-language track to Rashkis in August and
  ended its World Language track on September 17, eleven days before the survey opened. The page
  and `docs/INVENTORY.md` use the corrected framing; the five findings files were written under
  the brief and some of their sentences still say "candidate".

## Survey side
- Self-selected sample, 90% current parents; 87 of 98 non-parents are CHCCS staff, so every
  parent vs non-parent contrast is a parent vs staff contrast.
- No respondent geography, school, income, race or home language, so school-level facts cannot
  be joined to respondents. School mentions in free text are a proxy for attachment, not attendance.
- Free text is coded with keyword rules, not read; non-English text is partly untranslated in the
  processed table, so the 71 non-English respondents are under-counted in every theme.
- Board percentages are transcribed from the district's report; with seven members one person is
  14 points, and no test is possible.
- Top-three strings were parsed by matching full option labels; 1,398 of 1,463 responses parse to
  exactly three challenge picks and 1,408 to three value picks.

## Enrollment and forecast side
- Eleven schools is eleven points: every school-level correlation is a ranking, not an estimate.
- Two utilization measures are used and rank the schools differently: 2024-25 ADM against
  certified SAPFO capacity, and the closure study's 2031 projection against 2026 program capacity.
  Charts name which one they use.
- The closure study forecast is Carolina Demography's at current boundaries; the deck's is the
  district's finance office, cohort-based and prepared before Carolina Demography's data. Scenarios
  A and B are linear extrapolations of Census SAIPE 5-17 estimates with a flat or linearly
  sliding capture rate, anchored to the 2025 actual. None is a prediction.
- Dollar figures use the deck's average state allotment per pupil, which is not the marginal cost
  or revenue of one student, and ignore the one-year funding lag except where the deck's own
  method is replicated.
- Economically disadvantaged share is a DPI reporting construct; the 2021-22 dip reflects
  pandemic-era identification.
- Walk counts are one morning (November 12, 2024) at eight of eleven elementary schools; Glenwood's
  observed walkers mostly came from an adjacent parking lot. Walk-zone flags are the published
  segment attribute, not the district's transportation roster.
- Block-group home values straddle zones; the page reports no home-value finding because none
  survived correction.
- The cohort ladder uses county-wide five-year age bands divided by five and assumes births after
  2024 equal the 2020-24 rate; it includes Orange County Schools territory.
- The representation ratio compares children (Census) with adults (survey); one household can
  hold several children, so the household-level factor would be smaller than 14.
