# Limitations tracker

Running list of limitations, caveats and open data questions for the Module 2 report. Add items as we find them; each one should end up in the report's Limitations section, in Data Collection & Cleaning, or as a decision in the analysis plan.

**Status key:** *Report* = goes in the Limitations section as-is · *Handled* = addressed by a design choice (say how) · *Open* = needs a decision

## Study design

| # | Limitation | Why it matters | Status |
|---|---|---|---|
| D1 | Observational, not experimental. CHCCS didn't randomize anything; respondent groups are self-reported. | Group differences can't be attributed to group membership itself; anything correlated with being a parent (age, income, neighborhood) could explain them. | Report. (Observational design confirmed as acceptable for the assignment.) |
| D2 | We examined group sizes (Q1 only) before writing the analysis plan. | Could look like peeking. It doesn't touch outcomes, so it can't bias the tests. | Handled: Q1-only script (`src/explore_respondent_groups.py`); plan committed before any script reads rating columns; disclosed in the report. |
| D3 | Many possible tests across 26 items and several groupings. | Running many tests inflates false-positive risk. | Handled: one pre-specified confirmatory test; everything else labeled exploratory (Benjamini–Hochberg where several tests are run). |

## Sample and representativeness

| # | Limitation | Why it matters | Status |
|---|---|---|---|
| S1 | Self-selected sample: whoever chose to take the survey. | Results describe respondents, not the district's population. | Report |
| S2 | 90% of responses (1,315 of 1,463) are current CHCCS parents. | The survey is effectively a parent survey; pooled averages mostly reflect parent priorities. Non-parent groups are small. | Report, and use as a Background finding. |
| S3 | Families who left CHCCS are nearly absent: only 8 respondents are parents of school-age children *exclusively* outside CHCCS (41 checked the box, but 33 also have children in CHCCS). | The "missing third" from Module 1 can't be studied with this survey. Planned Comparison 2 is unusable. | Handled (comparison dropped); Report. |
| S4 | Residents with no parent or staff role are rare: 13 under the strict rule, 33 under the loose rule. | Parents vs. community comparison can only detect large effects (d ≈ 0.6–0.95). | Handled (comparison redesigned); Report. |
| S5 | Non-English responses are few: 71 across seven languages (Spanish 37, Chinese 12, Japanese 9, Karen 4, Korean 3, Arabic 3, Burmese 3). | Non-English speakers are likely under-represented relative to the district; per-language analysis is impossible. | Report |
| S7 | 87 of the 98 non-parents are CHCCS employees. | A parent vs. non-parent difference is largely a parent vs. staff difference; employees' priorities may reflect their jobs, not their non-parent status. | Report; frame results accordingly. |
| S6 | "Orange County resident" may miss district residents living in Durham County (part of Chapel Hill, and likely part of CHCCS, lies in Durham County). | Some residents may not have checked the resident box. | Open: verify district geography. |

## Measurement

| # | Limitation | Why it matters | Status |
|---|---|---|---|
| M1 | Response records, not verified people. No respondent IDs, so duplicate submissions can't be detected. | Violates independence if one person submitted twice. | Report |
| M2 | Roles are select-all-that-apply and overlap (31% picked more than one). | Groups need rules to be mutually exclusive, which excludes some respondents. | Handled: rules pre-specified in the analysis plan; Report exclusion counts. |
| M3 | Ratings are ordinal 1–5; only the endpoints (1 = low, 5 = high priority) are known. Labels for 2–4 are reconstructed. | Means and Cohen's d are hard to interpret. | Handled: Mann–Whitney U with rank-biserial effect size; means reported only as descriptive. |
| M4 | Possible ceiling effects: priorities may cluster at 4–5. | Real differences between groups can be compressed. | Open: consider top-3 (Q7/Q8) check; Report. |
| M5 | The questionnaire is reconstructed from the results workbook; original layout, option order, required questions and enforcement of the three-choice limit are unknown. | Order effects or forced answers could influence ratings. | Report |
| M6 | Write-ins are coded as "Other" and not reassigned to predefined roles. About 13 write-ins describe future CHCCS parents (expecting, preschool, starting next year). One translation was corrected (Spanish!A23). | Some people are in "Other" who arguably belong in a defined group. | Handled: future-parent write-ins flagged with a keyword rule in the script; Report. |

| M7 | If Q9 ("one item to keep top of mind") is used, it's a single forced choice among 13 values plus write-ins. | Loses information about everything but the top choice; 13 categories split across groups leave many sparse cells, which breaks chi-square's expected-count rule. | Open: pre-specify how categories are combined (themes or one target value) before looking at Q9. |

## Privacy and data sharing

| # | Limitation | Why it matters | Status |
|---|---|---|---|
| P1 | Respondent-level data in a public repo. | Rubric asks for raw and cleaned data in the repo. | Handled: CHCCS already publishes the results at https://www.chccstogether.org/document-library, so the data is committed. |
| P2 | Some write-ins mention a specific school plus family details. | Already public, but quoting them adds nothing to the analysis. | Handled: report write-ins as counts by category, not verbatim. |
| P3 | Some role counts are very small (1 municipal official, 3 county officials, 9 students). | Small cells draw attention to individuals even in public data. | Report small groups as "<10" in the written report as good practice. |
