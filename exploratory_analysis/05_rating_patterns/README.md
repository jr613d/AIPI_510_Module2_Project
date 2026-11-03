# 05: Rating patterns and survey quality

**Question:** Did respondents rate everything a 5 (ceiling effects) or give every item the same rating (straight-lining)? Respondents complained the survey was confusing, and either pattern would weaken what the 1–5 ratings can show.

**Findings** (`figures/values_rated_5.png`):

- **Ceiling effects are modest.** All 1,463 responses completed both 13-item grids. Only 3.3% rated all 13 values a 5, and 9.7% rated 10 or more a 5. The typical respondent rated 4 of the 13 values a 5. Challenge ratings were less compressed (1.4% all 5s).
- **Non-parents give more 5s than parents** (median 5.5 vs. 4 of 13 values; Mann–Whitney p < 0.001; 8.2% vs. 3.0% rated everything a 5). That's a rating-style difference, so part of the higher non-parent ratings in `01` and `03` may reflect how people use the scale rather than different priorities. The main project's Q9 test is unaffected, since it uses a single forced choice.
- **Heavy 5-raters chose slightly differently on Q9.** Those who rated 10 or more values a 5 chose Student Learning less often (60% vs. 70%), but the difference isn't statistically clear (Monte Carlo p = 0.06).

**Kind of evidence:** exploratory, not pre-registered.

**Results:** `results/rating_pattern_summary.csv`, `results/rating_patterns_by_response.csv`, `results/q9_theme_by_rating_style.csv`

```bash
python exploratory_analysis/05_rating_patterns/run.py
```
