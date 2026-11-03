# Workstream B findings: the schools people wrote about, joined to Module 1

Script: `src/ws_b_schools.py`. Inputs: survey free text (Q4, Q6, Q10 and the 48 Q9 "Other" write-ins;
non-English sheets are already translated in `responses_wide.csv`), `write_in_codes_by_response.csv`,
Module 1 school metrics, closure-study forecast, DPI ADM 2006-2025, DPI EDS 2024-25, SRTS walk counts and
the transportation table transcribed from the closure study text. 1,463 respondents; 634 wrote something
(the earlier count of 626 excluded Q9 write-ins); 79 named at least one elementary school, 81 any CHCCS
school. All counts are respondents (one per school), never mention frequency. No text is reproduced.

Detection notes (`mention_detection_variants.csv`): "Carrboro" appears in 22 responses, but only 10 refer
to something other than the town, the district name or Carrboro High, and only 8 name the elementary
school outright (the table uses the strict 8; the loose 10 is in `mentions_loose_variant`). "McDougle" 11:
4 say Elementary, 4 say Middle, 6 unspecified; the table uses elementary-or-unspecified = 10. "Estes" 6
after dropping "Estes Dr" (one remaining case is probably the road). "Culbreth" 7 after dropping the
Culbreth Ridge neighborhood. "Smith" counts only as "Smith Middle" (2). Morris Grove: zero.

## Findings

1. **Glenwood is the only school the community writes about at scale, and the writing is about the closure
   process and trust, not buildings.** 26 of 634 writers name Glenwood (4.1%; 6.7 mentions per 100 ADM,
   versus 2.8 for the next school, Northside). 14 of the 26 use close/closing/closure words in the same
   field; 6 use keep/save/stay; 0 use "walk". Among Glenwood mentioners, the coded theme "Trust,
   transparency & communication" appears in 54% (Wilson 36-71%) versus 10% of other writers (Fisher
   p = 7e-8, BH q = 4e-6 across 182 school x theme tests); "Teachers & staff" 50% vs 25% (q = 0.11);
   "Walking, biking & walk zones" 4% vs 21% (q = 0.15). Evidence: descriptive counts plus exploratory Fisher
   tests with BH. Caveat: the free text reads as if the Glenwood closure had been decided before the survey
   opened on Sept 28, 2026; CONTEXT.md still lists Glenwood as a candidate from the May 7 study. The
   orchestrator should check the board record between those dates before framing this as "candidate"
   versus "closed". Chart: horizontal bars of mentions per 100 ADM, closure-study schools highlighted,
   with a second bar for the share of mentions that co-occur with closure words. Data: `school_table.csv`,
   `theme_cooccurrence_by_school.csv`, `sentiment_cooccurrence.csv`. Interest 4: it tells the board what the
   loudest school-specific signal in its own survey is about (process, not facilities).

2. **The three schools the district studied for closure are not the three its own forecast says will be
   emptiest in 2031, and the two groups differ sharply on poverty share and building age.**

   | set | school | built | util 2024-25 (SAPFO) | util 2031 (program cap.) | forecast 2026->36 | ADM 2019->25 | EDS % | SRTS walk % | mentions | closure-word mentions |
   |---|---|---|---|---|---|---|---|---|---|---|
   | studied | Ephesus | 1972 | 72.6 | 100 | +23% | -19% | 35.3 | 16.0 | 2 | 2 |
   | studied | Glenwood | 1952 | 97.5 | 100 | +6% | -20% | 20.3 | 9.3 (1.0 adj.) | 26 | 14 |
   | studied | Seawell | 1969 | 117.4 | 81 | -7% | -22% | 32.5 | 5.5 | 8 | 4 |
   | emptiest 2031 | Rashkis | n/a | 87.9 | 55 | -30% | -7% | 48.5 | 8.7 | 10 | 2 |
   | emptiest 2031 | Northside | n/a | 75.0 | 60 | -14% | -12% | 52.9 | 12.8 | 11 | 1 |
   | emptiest 2031 | Scroggs | n/a | 79.7 | 62 | -14% | -19% | 31.6 | 28.3 | 10 | 3 |
   | mean studied | | 1964 | 95.8 | 93.7 | +8% | -21% | 29.4 | 10.3 | 12.0 | 6.7 |
   | mean emptiest | | n/a | 80.8 | 59.0 | -19% | -13% | 44.3 | 16.6 | 10.3 | 2.0 |

   The studied set was chosen on recent decline (mean -21% since 2019) and age (52-74 years); on the
   forecast, Ephesus and Glenwood reach 100% of program capacity by 2031 while Rashkis, Northside and
   Scroggs fall to 55-62%. Rashkis and Northside are the two highest-EDS schools in the district; Glenwood is
   the lowest. Scroggs has the district's highest observed walk share (28%). Mention counts are similar across
   the two sets (36 vs 31 respondents), but closure framing is not (20 vs 6). Evidence: descriptive, from the
   district's own documents. Caveats: building years are stated only for the three studied schools; the
   forecast assumes current boundaries and is the Carolina Demography model the closure study adopted, whose
   district total is far flatter than the last five years (see CONTEXT.md). Chart: a two-panel dot plot,
   2024-25 utilization vs 2031 projected utilization, six schools labeled and colored by set. Data:
   `candidates_vs_emptiest.csv`, `school_table.csv`. Interest 5: this is the single table a board member
   drawing boundaries in November most needs in front of them.

3. **On the district's own forecast with unchanged boundaries, the spread of utilization across the 11
   elementary schools widens, which is the factual basis for the "boundaries not adjusted" survey item.**

   | measure | min | max | range (pts) | mean | SD | CV | schools < 75% | schools > 100% |
   |---|---|---|---|---|---|---|---|---|
   | 2024-25 ADM / SAPFO capacity | 64.8 (Estes Hills) | 117.4 (Seawell) | 52.6 | 86.2 | 15.1 | 17.5% | 4 | 1 |
   | 2026 forecast / 2026 program capacity | 69.2 (Northside) | 108.6 (McDougle) | 39.4 | 83.3 | 11.6 | 13.9% | 3 | 1 |
   | 2031 projected (study) | 55.0 (Rashkis) | 118.0 (McDougle) | 63.0 | 81.6 | 19.2 | 23.5% | 4 | 1 |
   | 2036 forecast / 2026 program capacity | 55.4 (Rashkis) | 114.6 (McDougle) | 59.2 | 81.7 | 18.5 | 22.7% | 4 | 2 |

   On the consistent program-capacity basis the coefficient of variation rises from 14% (2026) to 23-24%
   (2031-36); the mean stays at 81-83%. Staff (70% rated 4-5) and the board (86% top-3) prioritize this
   item; parents do not (45% rated 4-5, 17% top-3). Evidence: descriptive. Caveat: the 2024-25 row uses SAPFO
   capacity and the others use 2026 program capacity, so compare rows 2-4 with each other. Chart: a slope
   chart of each school's utilization 2026 -> 2031 -> 2036 (11 lines) with the 75% and 100% bands shaded.
   Data: `utilization_spread.csv`, `school_table.csv`. Interest 5: it quantifies the board's top-ranked
   challenge in one number that is easy to say aloud (the gap between emptiest and fullest grows from 39 to
   63 points).

4. **Respondents who name a school rate "student populations have shifted, but boundaries have not been
   adjusted" lower than everyone else; they are the constituency least aligned with the board's top
   challenge.** 30.7% of elementary-school mentioners (n = 75, Parent + Non-parent) rate it 4-5 versus 47.8%
   of all non-mentioners (n = 1,338; Mann-Whitney p = 0.005, rank-biserial -0.19, BH q = 0.02 in a 4-test
   family) and 46.9% of other writers (p = 0.04, q = 0.08). "Partially empty school buildings" shows no
   difference (21.3% vs 21.2%, p = 0.19). Across all 26 rating items (mentioners vs other writers) nothing
   survives BH (smallest q = 0.16), but the direction is consistent: mentioners rate trailers (21 vs 37%
   4-5), overcrowding (57 vs 68%), maximizing buildings (43 vs 53%) and fiscal responsibility (55 vs 68%)
   lower, and student-centered focus (93 vs 87%) higher. Rashkis mentioners are the extreme case (10% rate
   the boundaries item 4-5 vs 45.5%, n = 10, p = 0.055, q = 0.33, not significant). Evidence: exploratory
   Mann-Whitney with BH. Caveat: naming a school is a marker of attachment to the current map, so this is
   selection, not persuasion; n = 75. Chart: paired bars of % rating 4-5 for the two focal items, mentioners
   vs non-mentioners, with Wilson CIs. Data: `ratings_mann_whitney.csv`. Interest 4: the people most engaged
   with specific schools are the ones who least accept the premise of redistricting.

5. **McDougle, the one school forecast to be overcrowded (118% in 2031), draws write-ins about siblings,
   capacity and walking.** Of 10 McDougle mentioners, 40% carry the "Siblings & keeping families together"
   code versus 2.2% of other writers (Fisher p = 9e-5, BH q = 0.003); "Class size, capacity & crowding" 40%
   vs 5% (q = 0.03); "Walking, biking & walk zones" 60% vs 20% (q = 0.10). 5 of 10 co-occur with "walk" and
   5 with keep/stay. Evidence: exploratory Fisher with BH; only two school x theme pairs in the whole family
   reach q < 0.05 (this one and Glenwood-trust). Caveats: n = 10; McDougle Elementary and Middle share a
   campus and a name, and 6 of the 10 did not say which. Chart: a small heatmap of school x theme share for
   schools with 8+ mentioners. Data: `theme_cooccurrence_by_school.csv`. Interest 3: it names the specific
   constituency (walk-zone families with children across the two McDougle schools) a boundary change there
   would meet.

6. **School-level attributes do not predict how often a school is written about; Glenwood is the whole
   signal.** Across 11 schools, Spearman rho between mention count and 2024-25 utilization is 0.45
   (p = 0.17), 2031 utilization -0.12, EDS share 0.16, SRTS walk share -0.10 (n = 8), ADM change 2019-25
   0.45, forecast change -0.33; closure-study schools have a median of 8 mentions vs 9 for the rest; DLI
   schools 8 vs 9. Per 100 ADM the correlations are weaker still. Evidence: descriptive correlations, n = 11,
   no power. Chart: none recommended. Data: `school_attribute_correlations.csv`. Interest 2: a null that
   stops anyone from reading school mention counts as a measure of anything but the Glenwood process.

7. **Module 1 attributes only: the schools that lost the most students since 2019 are the low-poverty ones,
   while the forecast puts the future losses at the high-poverty ones.** EDS share vs ADM change 2019-25:
   rho = +0.69 (p = 0.019, n = 11): Estes Hills -31%, Morris Grove -31%, Seawell -22%, Glenwood -20% (EDS
   20-33%) versus Rashkis -7%, Northside -12%, Carrboro -1% (EDS 34-53%). EDS vs forecast change 2026-36:
   rho = -0.48 (p = 0.13): Rashkis -30%, Carrboro -16%, Northside -14% versus Ephesus +23%, Estes Hills
   +24%. Evidence: descriptive, exploratory, n = 11; the two correlations have opposite signs. Caveat: the
   forecast is the closure study's model at current boundaries and the reversal may reflect specific new
   housing (Ephesus, Estes) rather than a demographic turn; we cannot tell from here. Chart: scatter of EDS
   share (x) against 2019-25 ADM change and 2026-36 forecast change (two series), 11 labeled points. Data:
   `school_table.csv`, `school_attribute_correlations.csv`. Interest 4: if the forecast is right, the
   emptiest buildings in 2031 serve the district's poorest students, which changes the equity reading of
   any closure or consolidation.

8. **Naming a school is a parent behavior; staff respondents rarely do it and never raise magnet or
   lottery programs.** 72 of 572 parent writers name an elementary school (12.6%, Wilson 10.1-15.6%) vs 3
   of 32 non-parent writers (9.4%, 3.2-24.2%; the CI overlaps). Of the 45 writers who mention dual language,
   immersion, Mandarin or Spanish, 43 are parents (1 non-parent); all 28 who mention magnet or lottery are
   parents. Non-English-sheet writers (29) name an elementary school fewer than 5 times (suppressed).
   Evidence: descriptive with Wilson CIs. Chart: none needed; a sentence. Data: `mention_rates_by_group.csv`.
   Interest 2: it confirms the program-protection voice in the write-ins is parents, not staff.

9. **The transportation profile of the three studied schools differs more than their enrollment does.**
   Glenwood: 389 of 391 students bus-eligible (lottery magnet), 7 buses, 170 AM riders, 38-minute average
   ride, 2 NTZ students, 2-4 true walkers (the 38 observed came from an adjacent retail lot), ~210-220 driven.
   Ephesus: 253 of 373 eligible, 3 buses, 140 riders, 30 minutes, 125 NTZ, 64 walkers + 14 bikers (19%), 160
   driven. Seawell: 282 of 402 eligible, 4 buses, 147 riders, 28 minutes, 120 NTZ, 25 walkers + 23 bikers
   (12%), 207 driven. Evidence: transcribed from closure study p.26. Chart: stacked bar of mode share (bus /
   walk+bike / driven) for the three. Data: `transport_closure_candidates.csv`. Interest 3: moving the
   Mandarin program moves seven buses and a 38-minute ride with it; closing Ephesus or Seawell adds ~120-125
   bus riders and ~$112-117K per year by the study's own estimate.

10. **Sentiment proxies by school (counts only).** Closure words co-occur with Glenwood (14 of 26) and
    Seawell (4 of 8) but barely with the forecast-emptiest schools (Rashkis 2 of 10, Northside 1 of 11,
    Scroggs 3 of 10). "Walk" co-occurs with McDougle (5 of 10) and Scroggs (3 of 10), the two schools with
    the strongest walk-zone identity in the text (Scroggs has the district's highest SRTS walk share, 28%).
    Dual-language words co-occur with FPG (4 of 8), Glenwood (4 of 26), Carrboro and Rashkis (2 each).
    Evidence: descriptive. Chart: a school x word-group dot matrix sized by count. Data:
    `sentiment_cooccurrence.csv`. Interest 2.

## Dead ends

- Morris Grove: 0 mentions among 634 writers despite -31% ADM since 2019, 73% utilization and the
  second-lowest EDS share. Nobody is writing about it.
- Ephesus: 2 mentions, both closure-framed. A studied school the survey barely registers.
- Q9 value themes do not differ between school mentioners and other writers (Monte Carlo chi-square
  p = 0.68, Cramér's V 0.06; parents only p = 0.44). Student Learning share: mentioners 67.6% (56-77),
  other writers 60.3% (56-64), non-writers 71.2% (68-74). The writer/non-writer gap is the only visible
  one and it is already known. Data: `q9_theme_by_school_mentioner.csv`, `q9_theme_test.csv`,
  `q9_student_learning_by_segment.csv`.
- "Partially empty school buildings": no rating difference for any mentioner group (overall, Glenwood,
  Northside, Rashkis).
- Per-school rating comparisons (Glenwood, Northside, Rashkis mentioners, two focal items): none survive BH.
- Walk share vs mentions (rho -0.10, n = 8), EDS vs mentions (0.16), DLI status vs mentions: nothing.
- Expected pairings that did not appear: Glenwood with "Special programs" (7 of 26, 27% vs 15% of other
  writers, p = 0.16); Scroggs with "Walking" (4 of 10, 40% vs 20%, p = 0.13); Scroggs with "Buses, commute
  & traffic" is the closer fit (5 of 10, 50% vs 17%, q = 0.13).
- Building years for the eight schools outside the closure study are not in the Module 1 corpus (the
  study's "Year Built" table covers only Ephesus, Glenwood, Seawell).
- Language split: fewer than 5 non-English-sheet respondents name any school, so no by-language table.
- Middle and high schools: Culbreth 7, Smith Middle 2, Phillips 2, McDougle Middle 4, Chapel Hill High 3,
  East 1, Carrboro High 3. Too few for anything beyond the counts in `mention_detection_variants.csv`.
