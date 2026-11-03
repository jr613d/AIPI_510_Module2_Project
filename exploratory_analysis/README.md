# Exploratory analysis

This folder holds work done **after, and outside the scope of,** the Module 2 project. Once the pre-registered test was complete, I kept exploring the CHCCS survey data for fun, and to see what else it might show about how different stakeholders see the district's redistricting priorities.

**None of this is confirmatory.** The project's only pre-registered hypothesis test is the chi-square comparison of parents and non-parents in `src/run_chi_square.py`, specified in advance in `docs/analysis_plan.md`. Nothing here was planned before the data was examined. Some analyses below report p-values, but they come from many comparisons chosen after seeing the data, so treat them as signals worth following up, not findings.

## Why keep it separate

The main project's credibility rests on the order of work: plan, then data, then one test. Exploring after the fact is useful, but every additional comparison raises the chance of finding a pattern that is really noise (the multiple comparisons problem). Keeping this work in its own folder, with its own scripts and outputs, makes clear which results were pre-registered and which were not.

## Sub-analyses

| Folder | Question | Headline |
|---|---|---|
| [`01_values_and_board`](01_values_and_board/) | Which individual values separate the groups, and how do respondents compare with the Board? | The Board weighs finances and buildings far more than respondents. The Learning gap comes from "Educational excellence." |
| [`02_challenges`](02_challenges/) | Do parents and non-parents rank the 13 challenges differently? | Both put staff retention first. Non-parents weigh boundaries and building costs more; parents weigh bus commutes and the district's appeal. |
| [`03_parent_staff`](03_parent_staff/) | Do parents who work for CHCCS answer like parents or like staff? | **Like staff.** 53% chose Student Learning, vs. 72% of other parents and 47% of non-parent staff. The main result may be about working for the district more than about being a parent. |
| [`04_write_ins`](04_write_ins/) | What did respondents raise in their own words? | Teachers and staff, walk zones, buses, and keeping current students in place, several of which aren't among the survey's listed values. |
| [`05_rating_patterns`](05_rating_patterns/) | Did people rate everything a 5? | Rarely (3% rated all values a 5), but non-parents give more 5s overall, a rating-style caveat for comparing 1–5 ratings. |
| [`06_age_and_language`](06_age_and_language/) | Do priorities differ by parent age or survey language? | Parents in their 30s and non-English respondents lean toward student logistics and well-being, especially safety. |

Each subfolder has its own `README.md` (findings and caveats), `run.py`, `figures/` and `results/`.

## Shared code and data

- `common.py`: builds one row per response from the raw workbook with the same response IDs and group rules as the main project, plus shared plotting style and an exploratory Monte Carlo chi-square helper.
- `data/processed/responses_wide.csv`: that combined table (generated).
- `data/raw/full_report_board_vs_cpa_transcribed.csv`: Board vs. survey percentages typed by hand from the district's Full Report (*CHCCS Priorities & Values Conversations, Fall 2026*), pp. 2 and 4.

The scripts read the main project's processed data without changing it. Two figures of the confirmatory result itself (pooled vs. groups, and the residual heatmap) belong to the main project and are made by `src/make_result_figures.py`.

## Reproducing

From the repository root, after running the main pipeline (see the top-level README):

```bash
for d in 01_values_and_board 02_challenges 03_parent_staff 04_write_ins 05_rating_patterns 06_age_and_language; do
  python exploratory_analysis/$d/run.py
done
```

## Ideas not yet explored

- Q8 top-three values by theme, as a check on the Q9 result
- Parent-staff by role (teachers vs. other staff) and by age, to see whether the staff pattern holds
- Linking the district's school-level capacity worksheet to respondents' concerns about crowding and empty buildings
