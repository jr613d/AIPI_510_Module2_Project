# 06: Parents by age, and survey language

**Questions:** Among current parents, do top priorities (Q9 themes) differ by age? Do respondents who took a non-English version prioritize differently?

**Findings:**

- **Parents by age** (`figures/parents_by_age_q9_themes.png`), comparing 30–39 (n = 277), 40–49 (n = 806) and 50+ (n = 152):
  - Parents in their 30s, likely with younger children, chose Student logistics & well-being more often (30% vs. 21% for older parents) and Student Learning less often (63% vs. 74% for parents in their 40s).
  - Parents 50 and older chose Money & buildings more often (10% vs. 3%).
  - Monte Carlo chi-square p < 0.001, Cramér's V = 0.12.
- **Survey language** (`figures/language_q9_themes.png`):
  - Respondents to the seven non-English versions (n = 68 with a Q9 theme) chose Student logistics & well-being far more often (44% vs. 23%) and Student Learning less often (51% vs. 70%).
  - School safety alone was the top value for 17 of the 68 (25%), compared with about 8% of respondents overall; 5 chose meal service.
  - Monte Carlo chi-square p = 0.003, Cramér's V = 0.11.

**What it suggests:** priorities that look uniform in the pooled survey vary by family stage and language community, and the smaller groups lean toward day-to-day concerns such as safety, meals and getting to school.

**Caveats:** exploratory and not pre-registered. Parents under 30 (8) were too few to include. The language comparison pools seven languages (Spanish 37, Chinese 12, Japanese 9, Karen 4, Korean 3, Arabic 3, Burmese 3), so it can't say which community drives the difference.

**Results:** `results/parents_by_age_q9_themes.csv`, `results/parent_age_counts.csv`, `results/language_q9_themes.csv`, `results/other_language_counts.csv`, `results/tests.csv`

```bash
python exploratory_analysis/06_age_and_language/run.py
```
