# Analysis plan (pre-registration draft)

Commit this file, with the open items resolved, **before** any script reads an outcome column (Q3, Q5, Q7, Q8 or Q9). The git commit timestamp is our record that the plan came first. Only Q1 (respondent relationship) has been examined so far.

## Research question

Do current CHCCS parents and non-parents differ in which value they most want kept "top of mind" in CHCCS's facilities planning?

## Groups (from Q1, select all that apply)

| Group | Rule | n |
|---|---|---|
| **Parents** | Checked *Parent of current CHCCS student(s)* | 1,315 |
| **Non-parents** | Did not check any parent option (current, graduated, or children not in CHCCS) and did not write in a parent, future-parent, grandparent or guardian role | 98 |
| Excluded | Parents of graduates, parents of children only outside CHCCS, future parents and grandparents/guardians who aren't current parents | 50 |

- Current parents who also work for CHCCS (84) stay in the Parents group.
- Future-parent and grandparent/guardian write-ins are identified by keyword rules in `src/explore_respondent_groups.py`.
- **Composition note:** 87 of the 98 non-parents are CHCCS employees, so in practice this comparison is close to parents vs. staff. Interpret and report it that way.

## Outcome: Q9 value theme

Q9 asks for the one value "above all others" to keep top of mind. The 13 values are combined into four themes, fixed here before Q9 is examined:

| Theme | Q9 values |
|---|---|
| **Student Learning** | Educational excellence (quality & student outcomes); Student-centered focus |
| **Money & buildings** | Fiscal responsibility; Maximizing the use of currently available buildings; Long-term planning; Increasing the use of renewable energy districtwide |
| **Community** | Community engagement & trust building; Collaboration between schools and county leadership; Community partnerships |
| **Student logistics & well-being** | Minimizing the distance students travel between home and school; School safety; High quality school meal service; Ensuring well-balanced student populations across all school sites |

- "Other" write-ins and blank answers are excluded from the test; their counts are reported by group.
- Wording variants in the source ("Minimize"/"Minimizing," "School saftey") are normalized before mapping.

## Hypotheses

- **H₀:** Value theme is independent of group: parents and non-parents choose themes in the same proportions.
- **H₁:** The theme distribution differs between parents and non-parents (two-sided, no predicted direction).

## Test

- **Primary:** chi-square test of independence on the 2 × 4 table (group × theme), α = 0.05.
- **Assumption check:** every expected cell count ≥ 5. If any is below 5, use the Fisher–Freeman–Halton exact test (or a Monte Carlo exact p-value) instead, as specified here.
- **Effect size:** Cramér's V with a 95% bootstrap confidence interval (10,000 resamples within each group).
- **Post hoc:** adjusted standardized residuals for each of the 8 cells, Bonferroni-corrected (|z| > 2.73 for α = 0.05 / 8), to identify which themes drive any difference.
- **Also reported:** the percentage choosing each theme by group, with 95% confidence intervals.

## Power (sensitivity analysis)

Group sizes are fixed by who responded. With about 1,400 respondents and 3 degrees of freedom, the test has 80% power to detect Cramér's V ≈ 0.09 at α = 0.05. Because the non-parent group is small (98), practically this corresponds to differences of roughly 10–15 percentage points in a theme's share. The final calculation will use the counts after excluding Q9 "Other" answers.

## Exploratory analyses (not confirmatory)

Labeled exploratory in the report; Benjamini–Hochberg corrected where multiple tests are run.

- Each of the 13 individual Q9 values by group (descriptive; too sparse for testing).
- Q5 value ratings (1–5) by group: Mann–Whitney U with rank-biserial effect sizes.
- Q8 top-3 values by theme as a consistency check.
- Challenges: Q3 ratings and Q7 top-3 challenges by group.
- Parents by age group (Q2), once Q2 counts are available.

## Decisions made

- **One confirmatory test.** The chi-square test above is the only confirmatory test, at α = 0.05, so no multiple-comparison correction is needed. Everything else is exploratory.
- **Observational design accepted** for the assignment.
- **Data is public.** CHCCS published the survey results on its document library (https://www.chccstogether.org/document-library), so the raw data is committed to the repo.
- **All eight language tabs included**, using the English translations provided in the workbook.
