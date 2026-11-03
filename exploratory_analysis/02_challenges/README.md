# 02: Challenges by group

**Question:** Do parents and non-parents differ on which challenges matter most (Q3 ratings, Q7 top three)?

**Findings** (`figures/challenges_by_group.png`):

- **Shared priorities:** both groups put retaining highly effective employees (about 93–96% rate it 4–5) and building safety codes at the top.
- **Non-parents weigh buildings and boundaries more:**

  | Challenge | Rated 4–5 (non-parents vs. parents) | In top three (non-parents vs. parents) |
  |---|---|---|
  | Boundaries not adjusted to population shifts | 70% vs. 45% | 35% vs. 17% |
  | Cost of maintaining aging buildings | 78% vs. 50% | 36% vs. 18% |
  | Overcrowded buildings | 83% vs. 69% | 33% vs. 22% |
  | Partially empty buildings | 32% vs. 20% | 10% vs. 4% |

- **Parents weigh what affects their own children's daily experience more**, in their top three:
  - length of bus commute: 29% vs. 15%
  - the district's appeal to current and prospective students: 25% vs. 12%
- **This mirrors the Board comparison** in `01_values_and_board`: non-parents, who are mostly staff, lean toward the operational and facilities concerns the Board also emphasizes.

**Kind of evidence:** exploratory. Each panel tests all 13 items (Mann–Whitney U for ratings, Fisher's exact for top three) with a Benjamini–Hochberg correction; starred items have q < 0.05. These tests were not pre-registered. The non-parent group is small (98), and part of its higher ratings may be rating style (see `05_rating_patterns`).

**Check:** pooled Q7 percentages reproduce the district's Full Report (e.g. 80% chose employee retention, 46% safety codes).

**Results:** `results/challenge_ratings_q3_by_group.csv` (with rank-biserial effect sizes; positive = non-parents rate higher), `results/challenge_top3_q7_by_group.csv`

```bash
python exploratory_analysis/02_challenges/run.py
```
