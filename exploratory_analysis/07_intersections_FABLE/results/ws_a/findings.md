# Workstream A: who answered vs. who is affected

Script: `src/ws_a_representation.py` (run with the Module 2 venv). All tables in `results/ws_a/`;
`summary.json` holds the headline numbers. Everything below is descriptive unless a test is named.
Groups under 10 are written "<10". Free text is reported as counts only.

1. **Families whose children live in the district but attend school elsewhere are roughly 14 times
   under-represented in the survey relative to their share of the school-age population.**

   | Year | CHCCS ADM | SAIPE pop 5-17 | Resident children not in CHCCS | % not enrolled |
   |---|---|---|---|---|
   | 2019 | 12,335 | 13,065 | 730 | 5.6% |
   | 2021 | 11,645 | 12,678 | 1,033 | 8.1% |
   | 2024 | 11,266 | 12,309 | 1,043 | 8.5% |

   In the survey, 8 of 1,323 respondents who are parents of school-age children have all their
   children outside CHCCS: 0.6% (Wilson 95% CI 0.3-1.2%). Against 8.5% of resident children, that is
   a factor of 14.1 (9.3 using the 2019 gap). A softer definition, any non-CHCCS school-age child
   (41 of 1,323, 3.1%, CI 2.3-4.2%), gives a factor of 2.7.
   Evidence: descriptive ratio. Caveats: ages 5-17 is not K-12 (5-year-olds not yet in K, 17-year-old
   graduates); SAIPE is a model-based estimate with its own error; the Durham County slice of the
   district is in SAIPE but the survey has no geography; one household can hold several children,
   so a household-level ratio would be somewhat lower than the child-level one; the survey counts
   adults, not children; the "not enrolled" layer also includes children in other public districts
   via employee transfers. Chart: paired bars, "share of school-age children" vs "share of
   school-age-parent respondents", with the 14x annotation. Data: `representation_vs_population.csv`,
   `respondent_roles.csv`. Interest 4: the board is sizing schools for a population a third of whose
   loss was families choosing other schools, and that group is nearly absent from the priorities data.

2. **About half of the children who will attend K-5 under the new boundaries in their first six years
   are not in school yet, and their parents could only answer as "resident" or by write-in.**
   Orange County 2024 cohorts: under-5 = 6,156, ages 5-9 = 7,108, ages 10-14 = 8,472. Taking K-5 as
   ages 5-10 and the boundaries' first six years as 2027-28 to 2032-33, children ever in K-5 in that
   window were born 2017-2027; those born 2022-2027 (not enrolled in fall 2026) are an estimated 52% of
   that pool. For the first year alone (fall 2027) the not-yet-enrolled slice is 16% (the 2022 birth
   cohort). The survey offers no "parent of a pre-school child" role; 19 respondents wrote one in
   (13 in the Excluded group, 6 who are also current parents; ages 30-39: 8, 40-49: 10). Seven
   respondents identified solely as Orange County residents.
   Evidence: descriptive; cohort arithmetic uses 5-year bands divided by 5 and assumes 2025-27
   births equal the 2020-24 per-year size. Caveats: county-wide (includes Orange County Schools and
   UNC-driven age structure); K-5 ages are approximate; some under-5s will enrol in charter/private;
   the fall-2027 effective date is an assumption (the vote is January 2027). Chart: a cohort ladder
   (eleven birth-year bars, shaded "in school now" vs "not yet"). Data: `orange_age_cohorts_2010_2024.csv`,
   `summary.json` (age_pipeline). Interest 5: it reframes the survey as mostly the voice of families
   who will have left elementary school before the boundaries have run their course.

3. **The under-5 pipeline has shrunk 10% since 2010 while the county's total population grew 14%,
   and the survey's parent pool is tilted away from the ages who hold those children.**

   | Cohort (Orange County) | 2010 | 2019 | 2024 | 2010-24 |
   |---|---|---|---|---|
   | Under 5 | 6,857 | 6,466 | 6,156 | -10.2% |
   | 5-9 | 7,997 | 7,848 | 7,108 | -11.1% |
   | 10-14 | 8,119 | 8,801 | 8,472 | +4.3% |
   | Adults 30-39 | 15,935 | 16,452 | 16,607 | +4.2% |
   | Adults 40-49 | 18,348 | 17,793 | 17,768 | -3.2% |

   Under-5s fell from 5.1% to 4.0% of county population. Among parent respondents 852 are 40-49 and
   289 are 30-39, so 30-39 is 25% of the 30-49 parent pool; county adults 30-39 are 48% of the 30-49
   pool. The under-5 / 5-9 ratio is flat (0.86 in both 2010 and 2024): the decline has moved through
   both bands together rather than the pipeline collapsing recently (2021 was the under-5 trough at
   6,076; 2024 is slightly higher). The stitched `podcast_data.json` series agrees with the raw
   census files in all 15 years.
   Evidence: descriptive. Caveats: adult age shares are a crude benchmark (the county's 30-39s
   include many non-parents and graduate students); parents of under-5s are not identifiable in the
   survey; the 2019 and 2024 vintages are separate estimate series (2020 appears in both; the 2024
   vintage row is used). Chart: three cohort lines 2010-2024 plus a small inset of parent ages by
   decade. Data: `orange_age_cohorts_2010_2024.csv`, `orange_cohort_change.csv`,
   `age_distribution_by_group.csv`. Interest 3: supports the "shrinking pipeline" story the board
   already tells, but the survey-age link is suggestive rather than measured.

4. **Non-English responses are 4.9% of the sample; the only local benchmarks are school-level and
   say the multilingual share is several times that at the schools being considered for closure.**
   71 of 1,463 (Wilson CI 3.9-6.1%): Spanish 2.5%, Chinese/Japanese/Korean together 1.6%, four other
   tabs <10 each. The closure study text (Oct 2025 20th-day data) gives Seawell 16.5% multilingual
   learners (highest of the three) and Latinx shares of 13.0% (Ephesus), 4.6% (Glenwood), 11.1%
   (Seawell); Asian shares 14.3%, 38.0%, 28.6%. The district-wide demographic table is an image in the
   PDF and not in the text extract, so no district multilingual or race/ethnicity share is available
   locally. Economically disadvantaged: CHCCS 31.1% (2024), 30.5% (2025); elementary range 20.3%
   (Glenwood) to 52.9% (Northside) in 2025. The survey has no income, race/ethnicity, home-language or
   school-of-attendance item, so EDS cannot be benchmarked at all; language tab is the only proxy.
   Evidence: descriptive. Caveats: language of response is not ethnicity (most Latinx and Asian
   families answer in English); student shares are not parent shares; the three-school figures are
   not a district benchmark. Chart: dot plot of survey language shares against the three schools'
   Latinx/Asian/ML shares, with a greyed "no benchmark" row for EDS. Data: `language_tabs.csv`,
   `language_by_group.csv`, `closure_study_school_demographics.csv`, `dpi_eds_chccs_elementary.csv`.
   Interest 3: a board member can see at a glance which equity dimensions the survey cannot speak to.

5. **Staff are 12.4% of respondents but no staff response rate can be computed: no employee count
   exists in the local documents.** 182 respondents hold a CHCCS teacher (103), staff (80) or
   administrator (10) role (overlapping; the brief's 183 is not reproducible from `Q1_ROLES`, which
   gives 182, as does the `employee` flag). 84 of them are also current parents. Parent responses per
   100 students: 11.9 (1,315 / 11,065). A regex for "N employees / staff members / FTE / positions"
   finds nothing in the board deck, closure study, SAPFO report or BOCC agenda; the deck gives only
   salaries and benefits ($78.7M). DPI `rcd_funds2` has salary dollars, not headcount.
   Evidence: descriptive; null search. Caveats: none beyond the absence. Chart: none, a sentence.
   Data: `staff_share.csv`. Interest 2: useful mainly as a caveat on the pooled percentages.

6. **The district's pooled top-3 percentages are the parents' percentages: the mean gap is 0.6 points
   (max 1.4), against a mean gap of 7.0 points (max 16.8) from non-parents.** The recomputed pooled
   figures match the district's published report within 0.3 points on average, confirming the
   top-3 regexes. Largest parent vs non-parent gaps: boundaries not adjusted to shifted populations
   (parents 16.7%, non-parents 34.7%), cost of aging buildings (18.1% vs 35.7%), well-balanced student
   populations (14.8% vs 29.6%), maximizing building use (7.5% vs 21.4%), minimizing distance (28.0%
   vs 14.3%), bus commute length (29.0% vs 15.3%). The board's own top-3 picks sit on the non-parent
   side of every one of those six.
   Evidence: descriptive (differences of proportions; non-parent n = 98, so single-item CIs are about
   +/-9 points). Caveats: non-parents are 89% employees, so this is parents vs staff; the Excluded
   group (n = 50) is shown but too small to read. Chart: dumbbell per item, pooled marker sitting on
   the parent dot, non-parent dot offset, board value as a hollow marker. Data:
   `pooled_vs_parent_top3.csv`. Interest 4: it tells the board that "the community said X" means
   "parents said X", and that the building/boundary items the board ranks highest are the ones
   parents rank lowest.

7. **Around the district there are 4 private K-5 schools within 5 miles (685 students) and 19 private
   plus 3 charter within 10 miles (4,373 and 989 students), with roughly 490 Opportunity Scholarship
   recipients at the private schools in 2024; county-wide non-CHCCS enrollment grew 32% 2015-2025.**

   | Year | Home (est.) | Private | Charter | Total |
   |---|---|---|---|---|
   | 2015 | 941 | 1,174 | 528 | 2,643 |
   | 2019 | 1,231 | 1,087 | 1,013 | 3,331 |
   | 2021 | 1,796 | 1,063 | 1,113 | 3,972 |
   | 2025 | 1,002 | 1,283 | 1,201 | 3,486 |

   Home school peaked in 2021 and has fallen back; charter has plateaued near 1,200 since 2019;
   private is at its highest. Only 14 (2021) and 19 (2023) new voucher recipients list CHCCS as the
   prior district in `VOUCHERS`.
   Evidence: descriptive. Caveats: county-wide, so Orange County Schools families are included;
   private enrollment is the 2021-22 NCES survey (14 DNPE-only schools within 10 miles have no
   enrollment and are excluded); charter rows include Chatham and Durham schools that also draw from
   those counties; `vouchers2024` is per school regardless of the student's home district; Durham
   Academy's duplicate campus row was removed. Chart: stacked area of the county series with the
   survey's 8 exclusively-non-CHCCS parents annotated as a dot. Data: `alternatives_within_radius.csv`,
   `alternatives_within_10mi_list.csv`, `orange_alternatives_2015_2026.csv`. Interest 3: the
   alternatives exist and are growing, but the survey contains almost nobody who uses them.

8. **Only 41 respondents (2.8%; 6.5% of the 634 who wrote anything) mention charter, private, home
   school, vouchers or leaving the district, and those who do cluster on special programs and
   housing/growth rather than on money.** By pattern: private 26, charter 11, other district <10, leave
   the district <10, home school <10, voucher <10, opportunity scholarship 0, "pull my child" <10. All
   mentions come from parents (39 of 1,315, Wilson CI 2.2-4.0%) or the Excluded group (<10); none from
   the 98 non-parents (Fisher exact parents vs non-parents p = 0.11, exploratory, single test). By Q9
   theme the share is highest among Community (<10 of 41, 9.8%) and Other (<10 of 48, 10.4%) and
   lowest in Money & buildings (<10 of 59, 1.7%) and Student logistics (<10 of 333, 1.2%). Among
   mentioners, co-occurring write-in themes over-index on special programs (39% vs 14% of other
   writers, ratio 2.8), housing/growth (34% vs 11%, 3.3), screens/technology (20% vs 7%, 2.9) and
   neighborhood schools (27% vs 11%, 2.5); walk zones under-index (12% vs 21%).
   Evidence: keyword counts plus one exploratory Fisher test. Caveats: keyword matching, not coding
   ("private" can carry other senses; "charter" could be a comparison, not a threat); non-English
   free text in `responses_wide` is largely untranslated so the 71 non-English respondents are
   under-counted (0 hits); theme cells are mostly under 10. Chart: small horizontal bars of the eight
   patterns and a ratio chart of co-occurring themes. Data: `alt_mentions_by_pattern.csv`,
   `alt_mentions_by_field.csv`, `alt_mentions_by_group.csv`, `alt_mentions_by_q9_theme.csv`,
   `alt_mentions_cooccurring_themes.csv`. Interest 3: exit talk is rare in the survey but, where it
   appears, it is tied to magnets/dual language and to growth, which are redistricting levers.

## Dead ends

- Employee headcount: no figure in the board deck, closure study, SAPFO report, BOCC agenda, DPI
  funds table or the Module 2 docs; the staff response rate (finding 5) cannot be computed.
- District-wide multilingual, race/ethnicity and EDS-by-group benchmarks from the closure study: the
  demographic table on p.17 is an image; only the p.16 prose for three schools survived extraction.
- A survey proxy for economically disadvantaged, race/ethnicity, home language or school of
  attendance: none exists in the questionnaire, so finding 4 stops at language of response.
- Non-English free text: `responses_wide` stores several tabs untranslated (Spanish text is Spanish),
  so keyword counts for non-English respondents are zero by construction, not by evidence.
- Vouchers by prior district: `VOUCHERS` has CHCCS rows only for 2021 (14) and 2023 (19), too sparse
  for a series.
- Parent-age benchmark: no local source gives the age distribution of Orange County parents of
  school-age or pre-school children; the adult 30-39 vs 40-49 county split is the only available
  comparison and is weak.
- Under-5 "collapse": the under-5 / 5-9 ratio is unchanged since 2010 (0.86); the pipeline is
  smaller, not newly cratering, and the 2024 under-5 count is above the 2021 trough.
- Staff count discrepancy: the brief's 183 staff respondents is 182 in every local table.
