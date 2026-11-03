# 03: Parents who work for CHCCS vs. other parents

**Why this matters:** the main project's biggest limitation is that 87 of its 98 non-parents work for CHCCS, so "non-parent" and "staff" can't be separated. Parents who also work for CHCCS break that tie. Their parenthood is the same as other parents'; their job is the same as non-parent staff's. If they answer like other parents, the main difference is about being a parent. If they answer like staff, it's about working for the district.

**Findings:**

- **On the top-priority question (Q9), parents who work for CHCCS answer like staff, not like other parents** (`figures/parent_staff_q9_themes.png`):

  | Group | Chose Student Learning |
  |---|---|
  | Other parents (n = 1,172) | 72% |
  | Parents who work for CHCCS (n = 76) | 53% |
  | Non-parent CHCCS staff (n = 83) | 47% |

  Parent-staff differ from other parents (Monte Carlo chi-square p = 0.002, Cramér's V = 0.12) but not from non-parent staff (p = 0.92, V = 0.06).
- **On the 1–5 ratings, parent-staff mostly fall between the two groups, closer to staff.** On the 9 values where other parents and non-parent staff differ by 10 or more points, parent-staff sit a median of about two-thirds of the way toward staff; on the 5 such challenges, about four-fifths. For example, "well-balanced student populations": other parents 49%, parent-staff 83%, non-parent staff 84%.
- **Not every item follows the pattern.** On the cost of maintaining aging buildings, parent-staff look like other parents (55% vs. 50%), not staff (78%).

**What it suggests:** the parent vs. non-parent difference in the main project may be driven more by **working for the district** than by **not being a parent**. That reframes the main result as a difference between people inside and outside the school system.

**Caveats:** exploratory and not pre-registered. The parent-staff group is small (76 in the Q9 comparison), so its percentages carry wide uncertainty. Parent-staff may also differ from other parents in other ways, such as age or which schools their children attend.

**Results:** `results/q9_themes_by_subgroup.csv`, `results/q9_theme_tests.csv`, `results/q5_values_pct_4_5_by_subgroup.csv`, `results/q3_challenges_pct_4_5_by_subgroup.csv`

```bash
python exploratory_analysis/03_parent_staff/run.py
```
