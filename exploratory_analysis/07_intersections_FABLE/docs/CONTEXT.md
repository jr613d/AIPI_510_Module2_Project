# Context for the intersections workstreams

You are one of several analysts exploring the intersection of two AIPI 510 projects by Jim Redden
about Chapel Hill-Carrboro City Schools (CHCCS), a North Carolina district that in 2026 began a
school-closure and elementary redistricting process. An orchestrator will read your findings,
filter them, and weave the survivors into a narrative HTML data story for Jim (a district parent
whose children are about to enter elementary school) and for the CHCCS Board of Education, which is
drafting boundary scenarios in November 2026 and votes on final boundaries January 21, 2027.

## Module 1 (data storytelling): "An analysis of enrollment decline in CHCCS"
Source: NC DPI School Report Card researcher tables (`rcd_adm` Average Daily Membership by school and
district 2006-2025, `rcd_location` grade spans, `rcd_acc_eds`, `rcd_chronic_absent`, `rcd_funds2`,
`rcd_pk_enroll`), Census SAIPE district population, Census county population estimates by age,
NC DNPE private/home school counts by county, NCSEAA voucher reports, NCES school coordinates,
CHCCS board documents (Dec 11 2025 retreat deck; May 7 2026 closure study of Ephesus, Glenwood and
Seawell), the 2025 SAPFO capacity report, Carrboro GIS attendance segments with walk-zone flags,
ACS 2020-24 home values by block group (ASTRA atlas).

Headline findings (2019 -> 2024): total district population +0.7%; school-age (5-17) population −5.8%;
K-12 ADM −8.7% (12,335 -> 11,266); elementary ADM −16.5% (5,488 -> 4,583). Capture rate
(ADM / pop 5-17) fell 0.9441 -> 0.9153. Decomposition of the 1,069-student decline: 714 (67%) fewer
school-age children living in the district; 355 (33%) children who live in the district but enroll
elsewhere (charter, private, home school; indistinguishable in DPI data). CHCCS elementary decline
ranks 17th steepest of 113 NC districts (median −7.3%; 100 of 113 declined). Orange County charter
ADM grew 281 (2006) -> 1,201 (2025); county private enrollment 1,204 -> 1,338; home school estimate
581 -> 934 (county-wide, so includes Orange County Schools too). CHCCS 2024-25 district ADM 11,065;
elementary 4,522 across 11 schools. The district's financial case: state funding follows ADM
(~$8,356 per pupil FY2027, local ~$8,895), the board deck projects −2.4%/yr ADM and a cumulative
$38.3M state-funding reduction / $37.9M five-year deficit at current staffing. The closure study's
Carolina Demography forecast is nearly flat for elementary (4,294 in 2025-26 -> 4,183 in 2035-36),
while the last five years averaged about −3%/yr. Closure candidates: Ephesus (built 1972, forecast to
GROW to 100% utilization by 2031 from new housing), Glenwood (opened 1952, oldest; lottery Mandarin
Dual Language magnet; 38% Asian, lowest economically disadvantaged share), Seawell (opened 1969).
2031 projected utilization (program capacity) ranges 55% (Rashkis) to 118% (McDougle); district 81%.
2024-25 ADM / SAPFO capacity ranges 64.8% (Estes Hills) to 117.4% (Seawell).

## Module 2 (statistical analysis): "Comparing the top priorities of CHCCS parents and non-parents"
Source: the district's public Community Priorities Assessment (CPA), 1,463 responses, Sept 28-Oct 9
2026, eight language tabs (English 1,392; Spanish 37; Chinese 12; Japanese 9; Karen 4; Korean 3;
Arabic 3; Burmese 3). Questions: Q1 relationship (select all), Q2 age, Q3 rate 13 challenges 1-5,
Q4 other challenges (text), Q5 rate 13 values 1-5, Q6 other values (text), Q7 top-3 challenges,
Q8 top-3 values, Q9 the ONE value to keep top of mind (single choice + write-in), Q10 additional
thoughts (text). The questionnaire is reconstructed in
`../CHCCS_Reconstructed_Questionnaire.md` (relative to the Module_2_Project folder).
Groups: Parent = current CHCCS parent (1,315); Non-parent = no parent role (98, of whom 87 are CHCCS
employees); Excluded = other parental roles (50). Only 8 respondents are parents whose children are
all outside CHCCS. Only 7 identified solely as Orange County residents. 84 parents also work for CHCCS.
Pre-registered result: parents 70.5% vs non-parents 50.5% chose a Student Learning theme on Q9
(Monte Carlo exact p = 0.0006, Cramér's V 0.12). Exploratory follow-ups already done (do not redo;
build on them): board vs community gap on fiscal/buildings; parents-who-are-staff answer like staff;
write-in themes (teachers 26% of writers, walk zones 21%, buses 17%, keep students in place 17%,
special programs 16%, housing/growth 12%); non-parents give more 5s; parents in their 30s and
non-English respondents lean toward logistics/safety. The board (n=7) put "boundaries not adjusted
to shifted populations" in its top 3 challenges 86% vs 18% of respondents; fiscal responsibility top-3
57% vs 19%.

Value themes (Q9): Student Learning = Educational excellence, Student-centered focus.
Money & buildings = Fiscal responsibility, Maximizing use of buildings, Long-term planning, Renewable
energy. Community = Community engagement, Collaboration with county, Community partnerships.
Student logistics & well-being = Minimizing distance, School safety, Meal service, Well-balanced
student populations.

## Working rules
- Python: use `/Users/jim/dukeaipi/510_Sourcing_Data/Module_2_Project/AIPI_510_Module2_Project/.venv/bin/python`
  (pandas, numpy, scipy, statsmodels, openpyxl, matplotlib). For spatial work use
  `/Users/jim/dukeaipi/510_Sourcing_Data/Module_1_Project/ASTRA/school-map/.venv/bin/python` (shapely, pyproj).
- All input paths are in `src/paths.py` (import it with `sys.path.insert(0, <src dir>)`). READ ONLY:
  never modify anything under Module_1_Project or AIPI_510_Module2_Project.
- Write your script(s) to `src/ws_<letter>_<slug>.py`, outputs to `results/ws_<letter>/` (CSV/JSON
  tables that could feed charts), and a `results/ws_<letter>/findings.md`.
- Everything is exploratory and descriptive. If you run a test, say so and use a Monte Carlo
  chi-square or Fisher/Mann-Whitney with Benjamini-Hochberg across the family; never call anything
  confirmatory. Report Wilson CIs for small-group percentages. Groups under 10 are reported as "<10".
- Privacy: report free-text as counts and codes, never quotes, even though the workbook is public.
- Year convention: DPI `year = 2025` is school year 2024-25. SAIPE July-2024 pairs with 2023-24
  (year 2024).
- findings.md format: a numbered list. Each finding = one bold claim sentence; the key numbers (a
  small table is fine); evidence type (descriptive / exploratory test with p and effect size);
  caveats; what chart would show it and which output file holds the data; and a 1-5 "interest to a
  board member" score with one sentence of why. Also list dead ends (things you checked that showed
  nothing) in a final section. Be concrete and skeptical; a null result is a finding.
- Jim's writing style: never use the words "actually", "genuinely" or "honestly".
