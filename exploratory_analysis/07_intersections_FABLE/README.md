# Seats and Voices: the intersection of the CHCCS enrollment data and the community priorities survey

An exploratory companion to two AIPI 510 projects by Jim Redden: the Module 1 data story on
Chapel Hill-Carrboro City Schools (CHCCS) enrollment decline and the Module 2 statistical analysis
of the district's Community Priorities Assessment (this repository). It is the seventh piece of the
Module 2 project's [exploratory analysis](../README.md) and, like the rest of that folder, sits
outside the pre-registered scope. It asks what the two datasets say together
about the elementary redistricting the Board of Education is deciding between November 2026 and
January 21, 2027.

**The deliverable:** `dashboard/seats_and_voices.html`. Open it by double-clicking. It is a single
self-contained file: data, charts and text are embedded, every chart has a table view and hover
details, and it works offline (web fonts fall back to system fonts).

## What it finds

1. The survey has no item about the driver of two-thirds of the decline (fewer children) and
   thirteen about buildings and money. Parents answer it as a demand question, the board as a
   supply question.
2. The survey is a survey of current parents: families whose children are outside CHCCS are about
   14 times under-represented, about half of the children the boundaries will serve are not in
   school yet, and the pooled results sit 0.6 points from the parent figure and 7 from staff.
3. The capture-rate third of the decline is worth about $3.0M a year of state funding; the
   deck's $38.3M five-year case assumes an enrollment path steeper than demographics alone
   ($21.5M), while the closure study's flat forecast is the demographics-only path.
4. The board's top challenge, unadjusted boundaries, is real: the utilization spread across the
   eleven schools widens from 39 to 63 points by 2031. The closure left the three emptiest schools
   (Rashkis, Northside, Scroggs) open.
5. "Well-balanced student populations" is the widest parent-staff gap; respondents read it as a
   capacity idea first (odds ratio 3.5 with the boundaries challenge). The two emptiest schools are
   the two most economically disadvantaged and hold 38% of projected empty seats; Rashkis is also
   receiving Glenwood's Mandarin program.
6. Distance is the value the board rates but will not rank. Walk-zone map flags do not predict
   who walks; the emptiest schools have 244 observed walkers and bikers against 137 to 171 at the
   studied schools; the district's price for converting a walker is $937 and 9 to 12 minutes a year.
7. The loudest school-specific voice in the survey (Glenwood, 26 writers) is about trust, and the
   only exit talk is about programs and growth, not money.

Everything is exploratory. The only pre-registered test is in the Module 2 report.

## Layout

```
README.md, LIMITATIONS.md, requirements.txt
docs/CONTEXT.md       brief given to the five analysis workstreams
docs/INVENTORY.md     orchestrator's pass over all 46 findings: kept, folded, parked, and the narrative arc
src/paths.py          every input path (read-only pointers into the Module 1 and Module 2 projects)
src/ws_a_representation.py   who answered vs who is affected
src/ws_b_schools.py          schools named in write-ins, joined to capacity and forecasts
src/ws_c_drivers.py          priorities vs the drivers of decline; the money; the forecasts
src/ws_d_spatial.py, ws_d_geography.py   zones, walk flags, home values, transportation
src/ws_e_balance.py          economic disadvantage and utilization across the 11 schools
src/build_story_data.py      assembles data/processed/story_data.json from results/
src/story_template.html      the page (prose, CSS, chart code)
src/build_story.py           inlines the data and writes dashboard/
results/ws_*/                each workstream's tables and findings.md
dashboard/seats_and_voices.html            the deliverable
dashboard/seats_and_voices_artifact.html   the same page without the document skeleton, for claude.ai
tests/render_check.py        headless-Chrome check: console errors, horizontal overflow, screenshots
```

## Reproduce

The survey inputs are read from this repository (the main pipeline and `exploratory_analysis/04_write_ins`
must have been run first). The enrollment inputs are read in place from the Module 1 projects, which
`src/paths.py` expects at `../../Module_1_Project` relative to this repository, and the school grades
workbook at `../archive`; nothing in them is modified. The workstream scripts therefore only run on a
machine with both projects. Their result tables, `data/processed/story_data.json` and the finished
page are committed, so the page itself can be rebuilt from this repository alone with the last two
build steps.

```bash
# from the repository root
M2=.venv/bin/python                                                 # pandas, scipy, statsmodels, openpyxl
ASTRA=../../Module_1_Project/ASTRA/school-map/.venv/bin/python     # shapely, pyproj, playwright
D=exploratory_analysis/07_intersections_FABLE
$M2 $D/src/ws_a_representation.py
$M2 $D/src/ws_b_schools.py
$M2 $D/src/ws_c_drivers.py
$ASTRA $D/src/ws_d_spatial.py && $M2 $D/src/ws_d_geography.py
$M2 $D/src/ws_e_balance.py
$M2 $D/src/build_story_data.py
$M2 $D/src/build_story.py
$ASTRA $D/tests/render_check.py     # needs Google Chrome at /Applications
```

## Sources

NC DPI School Report Card researcher tables; Census SAIPE and county population estimates; the
2025 SAPFOTAC certified report; the CHCCS closure study (May 7, 2026) and board retreat deck
(December 11, 2025); Carrboro GIS assignment segments; ACS 2020-24 block-group home values; the
CHCCS Community Priorities Assessment workbook and the district's Fall 2026 Priorities and Values
report; public reporting on the Glenwood decisions (WUNC, Chapelboro, ABC11, June to September
2026). Full citations are in the two parent projects and at the end of the page.

## How it was built

Five analysis agents (Claude Fable 5.1) worked in parallel from `docs/CONTEXT.md`, each writing a
script, result tables and a findings file. An orchestrator pass read all 46 findings, checked the
public record (which corrected the brief: Glenwood's closure was decided in June 2026, before the
survey), filtered to the 23 that sit at the intersection of the two projects and would change what
a board member does, and wrote the narrative and the page. Jim set the question, the scope and the
audience, and reviews the result.
