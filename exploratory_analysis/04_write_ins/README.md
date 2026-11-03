# 04: Themes in the free-text answers

**Question:** What did respondents raise in their own words that the survey's fixed options didn't capture?

**Data:** four free-text fields:

| Field | Responses with text |
|---|---|
| Q4 other challenges | 440 |
| Q6 other values | 233 |
| Q9 write-ins | 48 |
| Q10 additional thoughts | 348 |

In total, 637 respondents wrote something (575 parents, 32 non-parents).

**Method:** transparent keyword rules for 14 themes, listed in `run.py`. A respondent counts toward a theme if any of their free-text answers matches it; 78% of writers matched at least one theme. Keyword coding misses synonyms and can't read context, so the counts are approximate.

**Findings** (`figures/write_in_themes.png`), as the share of writers mentioning each theme:

| Theme | Share of writers |
|---|---|
| Teachers and staff (support, pay, retention) | 26% |
| Walking, biking and walk zones | 21% |
| Buses, commute and traffic | 17% |
| Keeping current students in place / minimizing disruption | 17% |
| Special programs (dual language, magnet, EC) | 16% |

- Walk zones, keeping current students in place, and neighborhood schools aren't among the survey's 13 values, yet they're among respondents' most common write-ins. The district's Full Report found the same top write-in themes.
- Non-parents' percentages rest on only 32 people and shouldn't be compared closely with parents'.

**Privacy:** outputs contain codes and counts, not quotes. Some write-ins include personal details, so the committed workbook has these free-text fields blanked. Rerunning this analysis needs the district's original workbook in `data/raw/private/` (see `data/README.md`); without it the script skips itself rather than overwrite the committed results.

**Results:** `results/write_in_themes.csv`, `results/write_in_themes_by_field.csv`, `results/write_in_codes_by_response.csv`

```bash
python exploratory_analysis/04_write_ins/run.py
```
