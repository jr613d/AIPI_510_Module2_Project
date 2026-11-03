# Exploratory analysis

This folder holds work done **after, and outside the scope of,** the Module 2 project. Once the pre-registered test was complete, I kept exploring the CHCCS survey data for fun, and to see what else it might show about how different stakeholders see the district's redistricting priorities.

**None of this is confirmatory.** The project's only pre-registered hypothesis test is the chi-square comparison of parents and non-parents in `src/run_chi_square.py`, specified in advance in `docs/analysis_plan.md`. Nothing here was planned before the data was examined. Several patterns below are based on small groups and were never tested for significance. Treat them as observations worth following up, not findings.

## Why keep it separate

The main project's credibility rests on the order of work: plan, then data, then one test. Exploring after the fact is useful, but every additional comparison raises the chance of finding a pattern that is really noise (the multiple comparisons problem). Keeping this work in its own folder, with its own script and outputs, makes clear which results were pre-registered and which were not.

## What's here

| Figure | What it shows | Kind of evidence |
|---|---|---|
| `fig_a_board_vs_survey.png` | Board of Education members (n = 7) vs. survey respondents: share placing each value in their top three, and share rating each challenge 4–5. The Board weighs fiscal and building items far more heavily. | Descriptive. Board figures come from the district's Full Report; with 7 members, one person moves a percentage by 14 points. |
| `fig_b_values_by_group.png` | All 13 Q9 values by group. The Learning gap comes from "Educational excellence" (54% vs. 29%); non-parents chose "well-balanced student populations" more often (18% vs. 4%). | Descriptive; individual values are too sparse to test, and some non-parent percentages rest on fewer than 5 people. |
| `fig_c_ratings_by_group.png` | Q5 ratings: share rating each value 4–5, by group. Non-parents rate balanced populations, building use and fiscal responsibility much higher than parents. | Exploratory; not tested. |

## Data

| File | Contents |
|---|---|
| `data/raw/full_report_board_vs_cpa_transcribed.csv` | Board vs. survey percentages for the 13 values and 13 challenges, typed by hand from the district's Full Report (*CHCCS Priorities & Values Conversations, Fall 2026*), pp. 2 and 4 |
| `data/processed/q5_value_ratings.csv` | Q5 ratings (1–5) of the 13 values for each response, with group |
| `data/final/exploratory_q9_values_by_group.csv` | Percent and count choosing each Q9 value, by group |
| `data/final/exploratory_q5_ratings_by_group.csv` | Percent rating each value 4–5, by group |

The script reads the main project's processed data without changing it. Two figures of the confirmatory result itself (pooled vs. groups, and the residual heatmap) belong to the main project and are made by `src/make_result_figures.py`.

## Reproducing

From the repository root, after running the main pipeline (see the top-level README):

```bash
python exploratory_analysis/src/make_exploratory_figures.py
```

## Ideas not yet explored

- Challenges (Q3 ratings, Q7 top three) by group
- Differences by respondent age (Q2) among parents
- Themes in the write-in answers
- English vs. other-language respondents
