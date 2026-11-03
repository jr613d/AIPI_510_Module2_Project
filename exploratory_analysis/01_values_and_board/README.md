# 01: Values by group, and the Board vs. survey respondents

**Question:** Beyond the four themes, which individual values separate parents from non-parents, and how do survey respondents compare with the Board of Education?

| Figure | Finding |
|---|---|
| `figures/board_vs_survey.png` | The Board (n = 7) weighs fiscal and building items far more heavily than respondents. Fiscal responsibility is in the top three values for 4 of 7 Board members vs. 19% of respondents; partially empty buildings are rated 4–5 by 5 of 7 vs. 21%. |
| `figures/values_by_group_q9.png` | The Student Learning gap comes from "Educational excellence" (54% of parents vs. 29% of non-parents as their single top value). "Student-centered focus" goes the other way (16% vs. 22%), and non-parents chose "well-balanced student populations" more often (18% vs. 4%). |
| `figures/value_ratings_by_group_q5.png` | On the 1–5 ratings, non-parents rate balanced populations (84% vs. 51% rating 4–5), building use (79% vs. 55%) and fiscal responsibility (82% vs. 66%) much higher. Part of this may be rating style: non-parents give more 5s overall (see `05_rating_patterns`). |

**Kind of evidence:** descriptive and exploratory. The Board figures are transcribed from the district's Full Report (`../data/raw/full_report_board_vs_cpa_transcribed.csv`); with 7 members, one person moves a percentage by 14 points. Individual Q9 values are too sparse to test.

**Results:** `results/values_by_group_q9.csv`, `results/value_ratings_by_group_q5.csv`

```bash
python exploratory_analysis/01_values_and_board/run.py
```
