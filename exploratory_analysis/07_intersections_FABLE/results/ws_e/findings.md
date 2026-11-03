# Workstream E: "Well-balanced student populations" vs how unbalanced the 11 elementary schools are

Script: `src/ws_e_balance.py`. Outputs: `results/ws_e/`. All tests are exploratory (Fisher / Mann-Whitney /
Spearman with Monte Carlo permutation p, Benjamini-Hochberg within each family). School-level n = 11, so
every correlation here is a ranking of eleven points, not a population estimate. DPI year 2025 = 2024-25.

## Findings

1. **The parent-vs-staff gap on "well-balanced student populations" is the widest value gap in the survey and it does not come from staff handing out more 5s.**

   | Group | n | Q5 rated 4-5 (Wilson 95%) | Q5 rated 5 | Q8 top-3 | Q9 the one value |
   |---|---|---|---|---|---|
   | Other parents (not staff) | 1,231 | 48.7% (46.0-51.5) | 21.5% | 13.1% | 2.5% |
   | Parents who are staff | 84 | 83.3% (73.9-89.8) | 48.8% | 38.1% | 20.3% |
   | Non-parents (87 of 98 are staff) | 98 | 83.7% (75.1-89.7) | 55.1% | 29.6% | 18.1% |

   Excluding the 118 parents and 16 non-parents who gave 10 or more of the 13 values a 5 (9% of parents, 16% of
   non-parents), the rated-4-5 figures are parents 47.1% (44.3-50.0) vs non-parents 80.5% (70.6-87.6): the
   gap moves from 32.7 to 33.4 points. Mann-Whitney on the 1-5 rating, parents vs non-parents: p < 0.0001
   both with and without heavy raters; the probability a random non-parent rates it higher than a random
   parent is 0.71. Evidence: descriptive + exploratory Mann-Whitney. Caveat: "non-parent" is nearly
   synonymous with staff here, and staff share of the survey (171 incl. parent-staff) is small. Chart:
   dumbbell of the three groups on the four measures. Data: `wellbalanced_gap_excluding_heavy_5_raters.csv`,
   `wellbalanced_mannwhitney_parent_vs_nonparent.csv`, `survey_items_by_split.csv`. Interest 4: the board
   will hear "balance" from staff and "keep my kid where they are" from parents, and the gap is not an
   artifact of rating style.

2. **In respondents' minds "well-balanced" is a boundary-and-capacity idea first and an equity idea second: people who put it in their top-3 values are 3.5x as likely to also flag "boundaries not adjusted" as a top-3 challenge.**

   Q8 well-balanced x Q7 challenge co-selection, all respondents (n = 1,463; Fisher, BH across 13):

   | Q7 challenge | % picking it, given well-balanced in top-3 | % given not | OR | BH p |
   |---|---|---|---|---|
   | Boundaries not adjusted | 36.9% | 14.3% | 3.51 | <0.001 |
   | Partially empty school buildings | 8.9% | 3.4% | 2.76 | 0.002 |
   | Unequal access to specialty programs | 26.3% | 15.7% | 1.91 | 0.001 |
   | Retaining highly effective employees | 70.8% | 82.2% | 0.52 | 0.001 |
   | School buildings meeting safety codes | 35.6% | 47.9% | 0.60 | 0.002 |

   Parents alone give the same picture (boundaries OR 3.69, partially empty 2.81, unequal access 1.94).
   The equity reading is present but weaker: of the 69 respondents whose free text was coded "Equity & the
   achievement gap", 22 (31.9%) put well-balanced in their top-3 values vs 15.4% of everyone else (OR 2.58,
   BH p = 0.002); on Q9 the same comparison is 6 of 68 vs 4.4% (OR 2.1, p = 0.125, not supported).
   Evidence: exploratory Fisher tests. Caveat: Q7 and Q8 are each limited to three picks, so negative ORs
   partly reflect crowding-out; the 13-test family is the right unit. Chart: horizontal OR bars with CIs for
   the 13 challenges. Data: `q7_x_q8_wellbalanced_coselection.csv`, `equity_writers_vs_wellbalanced.csv`,
   `q8_wellbalanced_x_other_values.csv`. Interest 4: it tells the board that the "balance" constituency
   overlaps the "redraw the lines" constituency, which is the mandate they are looking for.

3. **DPI data show the 11 schools are unbalanced on economic disadvantage and have become more so since 2017: the spread between the most and least disadvantaged school grew from 27.5 to 32.6 points.**

   | Year | Min (school) | Max (school) | Range | Max/min | SD | Gini | Elementary ADM-weighted mean | District LEA |
   |---|---|---|---|---|---|---|---|---|
   | 2017 | 21.5 (Morris Grove) | 49.0 (Northside) | 27.5 | 2.28 | 7.7 | 0.124 | 31.0 | 27.1 |
   | 2019 | 17.9 (Morris Grove) | 46.3 (Northside) | 28.4 | 2.59 | 8.1 | 0.138 | 30.1 | 25.8 |
   | 2023 | 19.8 (Glenwood) | 47.5 (Northside) | 27.7 | 2.40 | 8.4 | 0.134 | 33.5 | 29.9 |
   | 2025 | 20.3 (Glenwood) | 52.9 (Northside) | 32.6 | 2.61 | 9.7 | 0.147 | 34.7 | 30.5 |

   SD of the 11 shares vs year: Spearman 0.88 (p = 0.002, n = 9 years; 0.89 with the pandemic years
   2021-22 dropped). The widening is driven by Rashkis (+14.4 points, 34.1% to 48.5%), Ephesus (+8.5),
   Seawell (+7.6) and Scroggs (+5.0) on one side and Glenwood (-7.9, 28.2% to 20.3%) on the other;
   Northside (+3.9) stays top throughout. Evidence: descriptive, exploratory Spearman on 9 points. Caveats:
   the 2021-22 dip in every school (district 22.6% in 2022, 29.9% in 2023) is pandemic-era identification
   (universal free meals), not a real change; EDS is a DPI reporting construct that changed with direct
   certification; the elementary ADM-weighted mean (34.7%) sits above the all-grades LEA figure (30.5%).
   Chart: 11 lines 2017-2025 with the range band shaded, or a slope chart 2017 vs 2025. Data:
   `school_balance_long_2017_2025.csv`, `imbalance_by_year.csv`, `imbalance_trend_2017_2025.csv`,
   `eds_change_by_school.csv`. Interest 4: it gives "well-balanced" a number, and the number is moving the
   wrong way.

4. **The two most economically disadvantaged schools, Northside (52.9% EDS) and Rashkis (48.5%), are also the two emptiest in the 2031 forecast (60% and 55% of program capacity) and hold 38% of all projected empty elementary seats -- but across all 11 schools there is no EDS-to-utilization gradient.**

   | School | EDS 2025 | Util 2024-25 (SAPFO) | Util 2031 (program cap.) | Projected empty seats 2031 |
   |---|---|---|---|---|
   | Northside | 52.9 | 75.0 | 60 | 194 |
   | Rashkis | 48.5 | 87.9 | 55 | 208 |
   | Frank Porter Graham | 39.1 | 94.1 | 87 | 75 |
   | Ephesus | 35.3 | 72.6 | 100 | 0 |
   | Carrboro | 33.5 | 96.8 | 77 | 120 |
   | McDougle | 32.9 | 89.8 | 118 | -78 |
   | Seawell | 32.5 | 117.4 | 81 | 79 |
   | Scroggs | 31.6 | 79.7 | 62 | 188 |
   | Estes Hills | 27.7 | 64.8 | 84 | 74 |
   | Morris Grove | 23.6 | 73.2 | 74 | 126 |
   | Glenwood | 20.3 | 97.5 | 100 | 0 |

   Spearman EDS vs 2031 utilization: -0.31 (Monte Carlo p = 0.35, n = 11); EDS vs 2024-25 SAPFO
   utilization: -0.05 (p = 0.91). Northside + Rashkis are 18% of elementary ADM, 26% of its EDS students and
   402 of the 1,064 projected 2031 empty seats; the low-EDS tercile (Scroggs, Estes Hills, Morris Grove,
   Glenwood) holds another 388. Filling Northside and Rashkis by boundary moves would pull students from
   lower-EDS zones upward on the gradient; filling Scroggs or Morris Grove would not. Evidence: descriptive;
   the Spearman is a null. Caveats: the two utilization measures barely agree with each other (Spearman
   0.16: SAPFO vs 2026 program capacity, different denominators, and the 2031 figures are the closure
   study's demographer forecast); Glenwood's 100% is a lottery magnet, not a zone. Chart: scatter of EDS
   2025 (x) vs 2031 utilization (y), bubbles sized by projected empty seats, closure candidates outlined.
   Data: `eds_vs_utilization_scatter.csv`, `empty_seats_on_gradient.csv`, `correlations_school_level.csv`.
   Interest 5: this is the concrete redistricting tension behind the word "balance" -- the empty seats the
   board most wants to fill are in the two schools where moving students changes socioeconomic mix the most.

5. **The three closure candidates sit at different points on the gradient: Glenwood is the least disadvantaged school in the district (20.3% EDS, 38% Asian), Ephesus (35.3%, Title I) is just above the elementary mean of 34.7%, Seawell (32.5%) just below.**

   Closure-study cells (Oct 2025 20th-day): Ephesus White 50.6 / Asian 14.3 / Black 15.3 / Latinx 13.0 /
   Multiracial 6.4 / EDS 34.5 / SWD 13.3; Glenwood Asian 38.0 / White 35.4 / Black 8.6 / Latinx 4.6 /
   Multiracial 12.9 / EDS 17.5 / SWD 9.1; Seawell White 34.9 / Asian 28.6 / Black 16.5 / Latinx 11.1 /
   Multiracial 8.9 / EDS 32.2 / Multilingual 16.5. Ephesus is 1 of 6 Title I elementary schools; the study
   says Title I eligibility after redistricting is unknown. Where each school's students sit relative to its
   nearest schools (straight-line, no assignment modeled):

   | Candidate | Est. EDS students | Nearest three (km; EDS 2025; 2031 util) |
   |---|---|---|
   | Ephesus | 126 | Rashkis (2.3; 48.5; 55%), Estes Hills (2.5; 27.7; 84%), Glenwood (3.2; 20.3; 100%) |
   | Glenwood | 79 | Rashkis (1.9; 48.5; 55%), Ephesus (3.2; 35.3; 100%), Northside (3.5; 52.9; 60%) |
   | Seawell | 127 | McDougle (2.2; 32.9; 118%), Carrboro (2.8; 33.5; 77%), Northside (2.9; 52.9; 60%) |

   Dropping Glenwood from the set narrows the remaining ten schools' range to 29.3 points (SD 8.95 vs
   9.69); dropping Ephesus or Seawell leaves the range unchanged at 32.6 and nudges SD up (10.2). Said
   plainly: closing the least-disadvantaged school makes the remaining set look more balanced on paper, but
   188 of Glenwood's 391 students are district-wide Mandarin DL lottery students and 203 are World Language
   lottery students, so "spread to neighbors" does not describe what would happen to them. Ephesus's 126
   EDS students would land between a 48.5% school with 208 empty 2031 seats and a 27.7% school with 176
   empty 2024-25 seats. Evidence: descriptive. Caveats: study figures (Oct 2025) differ from DPI 2024-25 by
   up to 2.8 points (Glenwood 17.5 vs 20.3); the study's demographic table did not survive PDF extraction, so
   no district-wide comparison and no race/EL figures for the other eight schools. Chart: the 11 schools on a
   single EDS axis with candidates marked and arrows to their nearest schools. Data:
   `closure_candidates_on_gradient.csv`, `closure_study_demographic_cells.csv`, `notes.json`. Interest 4.

6. **Economic disadvantage lines up with school performance grades and chronic absenteeism across the 11 schools, which is what the EDS gradient means in outcome terms.**

   EDS 2025 vs SPG score 2025: Spearman -0.80 (Monte Carlo p = 0.005, BH p = 0.04 across 8 correlations);
   vs chronic absenteeism 2025: 0.72 (p = 0.017, BH p = 0.07). Grades: Glenwood A (85), Morris Grove B (83),
   Seawell B (79), Estes Hills B (78) ... Scroggs C (69), Rashkis C (68), Northside C (64). Chronic
   absenteeism: Glenwood 5.7% to Northside 18.7%. For the economically disadvantaged subgroup itself the SPG
   is D at 8 of 11 schools (Glenwood C 69, Morris Grove C 60, Scroggs F 35), and EDS share does not predict
   the subgroup score (rho -0.28, p = 0.40). Evidence: exploratory Spearman, n = 11. Caveats: NC's SPG is 80%
   achievement, so its correlation with poverty is built in and statewide; this is context, not a CHCCS
   finding. Chart: small multiples, EDS on x against SPG and chronic absenteeism. Data:
   `school_balance_2025.csv`, `spg_by_school_year.csv`, `correlations_school_level.csv`. Interest 3.

7. **The board rates "well-balanced" between parents and staff, but on the boundary challenge it is far beyond both.**

   | Item | Board (n=7) 4-5 / top-3 | Other parents 4-5 / top-3 | Parents-who-are-staff | Non-parents |
   |---|---|---|---|---|
   | Well-balanced populations | 71% / 14% | 49% / 13% | 83% / 38% | 84% / 30% |
   | Boundaries not adjusted | 86% / 86% | 43% / 15% | 73% / 38% | 70% / 35% |
   | Partially empty buildings | 71% / 29% | 19% / 3% | 37% / 11% | 32% / 10% |
   | Unequal access to specialty programs | 86% / 14% | 50% / 17% | 49% / 23% | 57% / 19% |

   Board figures are transcribed from the district report (n = 7, so one member is 14 points); the three
   community columns are recomputed from the workbook. Evidence: descriptive. Chart: grouped dot plot, four
   items by four respondent types. Data: `board_parents_staff_four_items.csv`. Interest 3: the board already
   knows its own numbers; the useful part is that staff, not parents, are its ally on balance and boundaries.

8. **Non-English respondents and the youngest respondents rate "well-balanced" very highly, but their top-3 picks do not differ from English respondents', so this is rating style rather than priority.**

   Rated 4-5: Spanish sheet 94.6% (n = 37), all non-English sheets 78.9% (n = 71), English 51.9%; Q8
   top-3: 18.9% / 16.9% / 16.1%. Age: 18-29 (n = 19) 78.9% rated 4-5 and 26.3% top-3; 50-64 63.7% / 21.6%;
   40-49 49.0% / 16.0%. Equity-coded write-ins: 69 respondents (4.7% of all; 10.9% of the 634 who wrote
   anything), 0 on non-English sheets, and under 10 in every group except parents (59), so the equity theme
   cannot be compared across staff/parent groups. Evidence: descriptive with small n. Caveats: the
   non-English lean toward 5s is already a Module 2 result; 18-29 and 65+ bands are under 20. Chart: none
   needed. Data: `survey_items_by_split.csv`. Interest 2.

## Dead ends

- EDS share vs current (2024-25 SAPFO) utilization: Spearman -0.05; vs current empty seats: -0.01. The
  "under-filled schools are the high-EDS ones" story holds only for the 2031 forecast and only for
  Northside and Rashkis; Estes Hills (27.7% EDS) is the emptiest school today at 64.8%.
- The two capacity measures disagree (SAPFO 2024-25 vs program-capacity 2031 utilization, Spearman 0.16);
  any chart should name which one it uses.
- EDS level vs EDS change 2017-2025 (are the poor schools getting poorer?): Spearman 0.47, p = 0.14. Not supported at n = 11.
- EDS share vs the EDS-subgroup SPG score: -0.28, p = 0.40.
- Equity write-in theme vs Q9 "well-balanced": 6 of 68 vs 4.4%, p = 0.125.
- Equity write-in theme by respondent group, age band and language: all cells under 10 except parents.
- Heavy 5-raters (10+ fives on values) as an explanation of the staff gap: no; the gap is unchanged.
- Chronic absenteeism before 2022: most CHCCS elementary rows are masked "<5%" in 2018-2021, so only 2022-25 are usable; all four years are reported in `imbalance_by_year.csv`.
- Closure study district-wide race/EL comparison: not present in the text file (the demographic table on
  study p.17 did not survive extraction); EL/multilingual share is given only for Seawell (16.5%). The other
  five Title I schools are not named.
- `SPG_XLSX` archive file: usable (one sheet, 2018-2019 and 2022-2025, unmasked for all 11 schools), so no dead end there; 2020-2021 are absent because NC did not issue grades.
