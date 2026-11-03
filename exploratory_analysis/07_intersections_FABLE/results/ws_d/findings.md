# Workstream D: distance, walking and housing

Scripts: `src/ws_d_spatial.py` (ASTRA interpreter: shapely/pyproj, EPSG:32617) then `src/ws_d_geography.py`
(Module 2 interpreter). Outputs in `results/ws_d/`. School-side n is 10 attendance zones (Frank Porter
Graham is a program campus with no zone) and 8 elementary schools with SRTS walk counts (Carrboro,
McDougle and Morris Grove were not counted). All school-side correlations are Spearman on n of 7-10 and
are exploratory; nothing on that side survives Benjamini-Hochberg. Survey n = 1,463 (Parent 1,315,
Non-parent 98). Percentages for groups carry Wilson 95% CIs in the CSVs.

Sources used: ASTRA `map_data.json` (166 segments, 40 flagged ESWALK = Y, dissolved zones, walk overlay,
82 block groups), raw 2024 block-group geometry (91 features, 70 assigned to a zone by centroid), ACS
2020-24 B25077/B25003, `school_metrics.csv`, the closure-study text (pp. 25-29, 58-62, 90-94 for
transportation; pp. 13-14, 47, 77 for housing-growth attribution), the closure forecast CSV,
`responses_wide.csv`, `write_in_codes_by_response.csv`, `BOARD_VS_CPA`.

## Findings

1. **Walk-zone designation on the map does not predict observed walking: Seawell has the district's
   largest walk-flagged share of zone area (56%) and the lowest observed walk rate (5.5%), while Scroggs
   has 8% walk-flagged area and the highest walk rate (28.3%).**

   | Zone | Area sq mi | Segments | ESWALK = Y | Walk-flag area share | SRTS walk % | SRTS bike % | Students within 0.5 mi (SRTS) |
   |---|---|---|---|---|---|---|---|
   | Scroggs | 7.00 | 13 | 3 | 8% | 28.3 | 3.9 | n/a |
   | Estes Hills | 4.22 | 25 | 5 | 32% | 16.3 | 3.1 | n/a |
   | Ephesus | 5.72 | 18 | 6 | 22% | 16.0 | 3.5 | 99 |
   | Northside | 11.23 | 34 | 6 | 5% | 12.8 | 1.3 | n/a |
   | Glenwood | 0.97 | 5 | 0 | 0% | 9.3 (2-4 real walkers per the Town) | 1.7 | 6 |
   | Rashkis | 2.75 | 15 | 1 | 15% | 8.7 | 4.3 | n/a |
   | Seawell | 3.42 | 11 | 4 | 56% | 5.5 | 5.0 | 0 |
   | Carrboro | 2.52 | 14 | 7 | 39% | not counted | | |
   | McDougle | 13.30 | 20 | 8 | 14% | not counted | | |
   | Morris Grove | 11.33 | 11 | 0 | 0% | not counted | | |

   Evidence: descriptive; Spearman walk-flag area share vs SRTS walk % rho = -0.14 (n = 7, p = 0.76);
   walk-segment share vs walk % rho = 0.11. Observed walk rates across the eight counted elementary
   schools run 5.5% to 28.3%; walking plus biking is 15.2% of the 3,390 students enrolled at the time
   of the counts. Caveats: ESWALK is the published segment flag, not the district's non-transportation
   roster (the atlas notes missing flags do not establish bus eligibility; Seawell's own NTZ count is
   120 students, 30% of enrollment, which is closer to its flagged area than to its walk rate). The
   SRTS count is one morning (Nov 12, 2024) and counts anyone arriving on foot, including from a
   parking lot (34 of Glenwood's 38 "walkers"). The SRTS density figures (students within 0.5 / 1 /
   1.5 miles) are only published for the three candidates: Ephesus 99 / 93 / 59, Glenwood 6 / 22 / 10,
   Seawell 0 / 60 / 107. Seawell's zero within half a mile explains its low walk rate despite a large
   flagged area: the flagged segments are north of the campus beyond easy walking. Chart: dumbbell or
   scatter of walk-flag area share vs observed walk % by school, `zone_geography.csv` and
   `srts_walk_counts.csv`. Interest 4: boundary scenarios that "preserve walk zones" on the map will
   not necessarily preserve walking; the schools where children walk are Scroggs, Estes Hills, Ephesus
   and Northside.

2. **The three lowest-utilization schools (Rashkis, Northside, Scroggs; 55-62% projected for 2031) have
   244 observed walkers and bikers, 1.4 to 1.8 times the 171 (137 after the Town's Glenwood adjustment)
   at the three closure candidates; Scroggs alone (131) nearly equals all three candidates combined.**

   | Group | Schools | Walkers | Bikers | Active total | Enrollment at count | Active share |
   |---|---|---|---|---|---|---|
   | Closure candidates | Ephesus, Glenwood, Seawell | 127 (93 adj.) | 44 | 171 (137 adj.) | 1,265 | 13.5% (10.8% adj.) |
   | Lowest 2031 utilization | Rashkis, Northside, Scroggs | 204 | 40 | 244 | 1,242 | 19.6% |
   | All 8 counted elementary | | 419 | 96 | 515 | 3,390 | 15.2% |

   Evidence: descriptive, from the SRTS table reproduced on closure-study pp. 28, 61 and 93; "adj."
   replaces Glenwood's 38 observed walkers with the Town's 2-4 estimate (4 used). Caveats: a single
   day's count; the SRTS enrollment denominators (e.g. Ephesus 401) exceed both 2024-25 ADM (358) and
   the study's own 373, so use the counts rather than the percentages; Carrboro, McDougle and Morris
   Grove were never counted. Chart: paired bars of walkers + bikers for the two triads, or per school
   sorted, `synthesis.json` and `srts_walk_counts.csv`. Interest 5: the closure study chose candidates
   on building condition and program, not on walking; if the board weighs active travel, the
   under-used schools are the ones with more walkers.

3. **At the three closure candidates the single largest mode is a parent's car (577 students, about 46%
   of those enrolled at count, vs 457 morning bus riders), only 52-55% of bus-eligible students ride at
   Ephesus and Seawell, and the study's extra-cost estimate assumes every non-transportation-zone
   student becomes a rider.**

   | | Ephesus | Glenwood | Seawell |
   |---|---|---|---|
   | Bus-eligible | 253 (68%) | 389 (99%, lottery magnet) | 282 (70%) |
   | AM riders / share of eligible | 140 / 55% | 170 / 44% | 147 / 52% |
   | NTZ (TIMS) | 125 | 2 | 120 |
   | Driven by parent | 160 | 210 (incl. parking-lot walkers) | 207 |
   | Avg bus ride | 30 min | 38 min | 28 min |
   | Extra ride if closed | +2.3-3.3 mi, +9-12 min (to Estes Hills, Rashkis) | not estimated; program relocates | +3.0-5.0 mi, +8-12 min (to Estes Hills, Morris Grove, Northside) |
   | Extra annual bus cost | $117,000 (125 x $936.53) | none stated | $112,383 (120 x $936.53; up to 2 more buses) |

   District bus facts (NCDPI Table 32, 2024-25): 55 buses, 3,880 riders, 728,860 miles, $3,013,692,
   $4.13 per mile, $54,794 per bus, $936.53 per pupil. Closing both Ephesus and Seawell adds about
   $229,000 a year by the study's method (247 NTZ students across all three x $936.53 = $231,000).
   Evidence: descriptive, transcribed from pp. 25-29 and 90-94 (every figure asserted present in the
   text by the script). Caveats: the per-pupil cost is an average, not a marginal cost; if new
   eligibles rode at the current 52-55% rate the bus bill would be roughly half, but the rest would
   join the car line, which the study does not cost; the time estimate is for bus routes only and says
   nothing about the walkers who would become riders or passengers; Glenwood's cost and time are left
   open. Chart: stacked mode bars (bus / walk-bike / car) for the three schools, plus a small table of
   closure costs, `closure_candidates_transportation.csv`. Interest 4: $937 per pupil and 9-12 minutes
   is the district's own price tag on converting a walker into a rider.

4. **The most car-dependent zones are Morris Grove (11.3 sq mi, no walk-flagged segment, 34 ADM per
   sq mi), McDougle (13.3 sq mi, 14% walk-flagged area, 36 ADM per sq mi) and Northside (11.2 sq mi, 5%
   walk-flagged area); Glenwood's 0.97 sq mi zone is a residual, since 99% of its students are
   bus-eligible as a lottery magnet.** Zone areas reproduce the atlas's figures to 0.01 sq mi. The three
   large western and southern zones hold 36 sq mi of the district's 47; Carrboro (2.5 sq mi, 50% of
   segments walk-flagged, 192 ADM per sq mi) and Seawell are the most compact. Among the seven counted
   zones, larger area goes with a higher observed walk rate (rho = 0.61, n = 7, p = 0.15), the opposite
   of the naive expectation, because walking depends on who lives within half a mile of the campus
   (Scroggs) rather than on zone size. Evidence: descriptive; `car_dependence_rank` is the mean of ranks
   on low walk-flag area share and large area. Caveats: area is geometry, not students; ESWALK caveats
   as in finding 1; none of the three car-dependent zones has an SRTS count, so their walk rates are
   unknown. Chart: map or bar of zone area with walk-flagged share, `zone_geography.csv`. Interest 3.

5. **Zone home values show no relationship with forecast growth, utilization or walking that survives
   correction (n = 10 Spearman); the one suggestive pattern is that renter-heavy zones are the ones
   forecast to shrink.**

   | Zone | Block groups (centroid / touching) | BG median home value min / median / max | Renter share | 2026-31 forecast change | 2031 utilization |
   |---|---|---|---|---|---|
   | Ephesus | 6 / 20 | $300k / $618k / $772k | 37% | +21.6% | 100% |
   | Estes Hills | 10 / 17 | $481k / $653k / $1.01m | 49% | +20.1% | 84% |
   | McDougle | 7 / 18 | $365k / $580k / $716k | 40% | +9.0% | 118% |
   | Glenwood | 1 / 9 | $379k (one BG, 18% inside zone) | 61% | +6.9% | 100% |
   | Morris Grove | 7 / 17 | $506k / $628k / $1.05m | 26% | -4.0% | 74% |
   | Seawell | 2 / 16 | $541k / $586k / $631k | 53% | -7.7% | 81% |
   | Northside | 14 / 35 | $275k / $509k / $945k | 53% | -13.1% | 60% |
   | Carrboro | 9 / 26 | $329k / $566k / $1.05m | 67% | -13.9% | 77% |
   | Scroggs | 7 / 17 | $439k / $588k / $880k | 41% | -16.1% | 62% |
   | Rashkis | 7 / 26 | $307k / $492k / $984k | 70% | -31.1% | 55% |

   Evidence: exploratory Spearman, 16 pairs, BH across the family (`zone_spearman.csv`). Median home
   value vs 2026-31 growth rho = 0.47 (p = 0.17, BH 0.35); vs 2031 utilization rho = 0.18; vs current
   ADM utilization rho = -0.66 (raw p = 0.038, BH 0.35); vs observed walk % rho = 0.64 (n = 7, p = 0.12).
   Renter share vs 2026-31 growth rho = -0.59 (p = 0.07, BH 0.35); vs walk % rho = -0.68 (n = 7,
   p = 0.09). Caveats: block groups straddle zones badly (touching counts are 2-9 times centroid
   counts; the median share of a block group's land inside its assigned zone is 0.73-0.96, Glenwood's
   one block group is 18% inside); the "median" is a median of block-group medians, not a zone median,
   as the atlas warns; values are owner-reported 2020-24 estimates of the existing stock, which cannot
   see the new developments the study credits for Ephesus's growth (49 students; Glenwood 12, Seawell
   18); Seawell rests on two block groups; two Carrboro block groups have no estimate and nine across
   the district carry margins over 30%. Chart: scatter of renter share vs 2026-31 forecast change with
   zone labels, `zone_geography.csv` and `zone_blockgroups.csv`. Interest 2: a null result with a hint;
   worth one sentence, not a chart, unless the board wants housing context for the forecast.

6. **Distance is the value where the board's own rating and ranking diverge most from the community:
   57% of the seven board members rate it 4-5 and none rank it top-3, against 60% and 27% of
   respondents; bus commute shows the same split (board 43% / 0%, community 59% / 28%).** 38% of
   respondents put distance or bus commute in a top-3 list, 17% put both. Evidence: descriptive from
   `BOARD_VS_CPA` and `responses_wide.csv`; the board n of 7 allows no test. Caveat: the board's survey
   was the same instrument answered separately; 0 of 7 is consistent with one or two members having it
   fourth. Chart: paired dots, board vs community, rated 4-5 and top-3, for distance and bus commute,
   `survey_distance_by_split.csv`. Interest 5: the board agrees it matters and does not rank it, while
   its top-ranked challenge (boundaries, 86% top-3) is precisely the one that changes who walks.

7. **Parents put distance in their top 3 twice as often as non-parents (28% vs 14%; Monte Carlo
   chi-square p = 0.0035, Cramer's V 0.08, BH 0.01), bus commute likewise (29% vs 15%, p = 0.0035), and
   parents who work for CHCCS answer like non-parents (18% top-3, 1% choose it on Q9, vs 29% and 10%
   for other parents; p = 0.03, BH 0.06).**

   | Split | n | Q5 distance 4-5 | Q8 distance top-3 | Q9 distance | Q3 bus 4-5 | Q7 bus top-3 |
   |---|---|---|---|---|---|---|
   | Parent | 1,315 | 59.9% | 28.0% | 9.1% | 59.0% | 29.0% |
   | Non-parent | 98 | 56.1% (46-66) | 14.3% (9-23) | 3.1% | 56.1% | 15.3% (10-24) |
   | Parent 30-39 | 289 | 64.0% (58-69) | 29.1% | 9.0% | 61.2% | 30.1% |
   | Parent 40-49 | 852 | 60.3% | 28.3% | 9.6% | 58.2% | 29.1% |
   | Parent 50+ | 160 | 51.9% (44-60) | 25.6% | 7.5% | 59.4% | 28.1% |
   | English sheet | 1,392 | 59.3% | 27.6% | 9.1% | 58.2% | 27.7% |
   | Other-language sheet | 71 | 67.6% (56-77) | 18.3% (11-29) | 2.8% | 70.4% (59-80) | 31.0% (21-43) |
   | Parent, not staff | 1,231 | 60.3% | 28.7% | 9.7% | 58.8% | 29.8% |
   | Parent who is staff | 84 | 54.8% (44-65) | 17.9% (11-27) | 1.2% | 61.9% | 17.9% (11-27) |
   | Non-parent staff | 87 | 56.3% (46-66) | 14.9% (9-24) | 3.4% | 54.0% | 14.9% |
   | Board | 7 | 57% | 0% | | 43% | 0% |

   Evidence: exploratory Monte Carlo chi-square (20,000 draws), BH across six tests in
   `survey_extra_tests.csv`. Parent age: the 4-5 rating falls from 64% (30-39) to 52% (50+), p = 0.04,
   V 0.07, BH 0.06, but the top-3 share is flat (p = 0.72); younger parents rate it higher without
   ranking it higher. Other-language respondents rate both items higher than English respondents (68%
   and 70%) but the Q5 difference does not test out (p = 0.18) and n = 71 gives wide intervals; they
   rank bus commute (31%) above distance (18%). Caveats: the parent-staff split repeats the known
   "parents who are staff answer like staff" pattern; effect sizes are small (V under 0.1). Chart:
   dot plot of top-3 share by split with Wilson bars, `survey_distance_by_split.csv`,
   `distance_q5_by_group_age.csv`. Interest 3.

8. **The 123 respondents who chose distance as their one value (98% parents) rate bus commute far
   higher than everyone else (85% vs 56% rate it 4-5; rank-biserial 0.43, Mann-Whitney p < 0.0001 after
   BH) and rate "boundaries not adjusted to shifted populations" lower (35% vs 48%, rank-biserial
   -0.16, BH p = 0.005); "partially empty buildings" is lower but does not survive (16% vs 22%,
   rank-biserial -0.09, BH p = 0.09).** Evidence: exploratory Mann-Whitney over all 13 challenge
   ratings, BH-corrected, Parent + Non-parent only (`distance_prioritizers_vs_others_challenges.csv`).
   Caveat: distance-prioritizers rate 11 of 13 challenges lower (mean 3.26 vs 3.55 excluding the bus
   item), so part of this is a rating style, people who see fewer problems except the commute; the
   boundaries result is among the stronger of the lowered items but not unique (unequal access to
   specialty programs is lowered more, rank-biserial -0.25). Chart: diverging bars of the 13
   rank-biserial values. Interest 4: the respondents most invested in proximity are the least persuaded
   by the challenge the board ranks first, which is the collision the boundary process has to manage.

9. **Walking and walk zones is a parent write-in theme (20% of 575 parent writers vs 12.5% of 32
   non-parent writers and 3% of 29 other-language writers), while buses are raised at similar rates by
   parents (17%) and non-parents (22%); 31% of all 637 writers mention walking or buses.** Parent
   writers aged 30-39 raise "keep current students in place" at 26% vs 7% of parent writers 50+, and
   walking at 20% vs 15%. Evidence: descriptive counts from `write_in_codes_by_response.csv`; no
   quotes. Caveats: non-parent, staff and other-language writer groups are 27-36 people, so the
   intervals span 5-30 points; the 637 writers are self-selected. Chart: small multiples of theme share
   by split, `survey_distance_by_split.csv`. Interest 3.

## Dead ends

- Home value vs walk-flagged area share (rho 0.22), vs 2031 utilization (0.18), vs walk % (0.64, n = 7):
  nothing survives BH; the n = 10 school side cannot support a home-value story.
- Walk-flagged area share vs 2031 utilization (rho 0.13) and vs 2026-31 growth (0.02): no relationship.
  Zone area vs 2031 utilization (0.02): none.
- Parent age vs Q8 distance top-3: flat (29 / 28 / 26%, p = 0.72). English vs other-language sheet on
  the Q5 distance rating: p = 0.18.
- "Partially empty buildings" among distance-prioritizers: lower, but BH p = 0.09.
- Glenwood extra ride time and cost: the study gives none ("difficult to estimate", program relocates);
  Seawell's is +3.0-5.0 miles, +8-12 minutes, $112,383 and up to two more buses (pp. 92, 94).
- SRTS walk counts exist only for 8 of 11 elementary schools; the three uncounted (Carrboro, McDougle,
  Morris Grove) include the two most car-dependent zones, so the walk-rate range 5.5-28.3% may not be
  the full range.
- 21 of 91 raw block groups have centroids outside every zone (9 lie fully outside the district; 12
  overlap but centre elsewhere); they are listed in `zone_geography_spatial.json`.
- The segment-level `Shape.area` field is not carried into `map_data.json`; areas were recomputed in
  UTM 17N and match the atlas's dissolved-zone figures.
