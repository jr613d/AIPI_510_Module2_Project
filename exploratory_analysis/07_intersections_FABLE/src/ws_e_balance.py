"""Workstream E: "Well-balanced student populations" -- the value where parents and staff differ
most -- against what DPI data show about how unbalanced the 11 CHCCS elementary schools are.

Inputs are read-only (see paths.py). Outputs go to results/ws_e/.
Run: /Users/jim/dukeaipi/510_Sourcing_Data/Module_2_Project/AIPI_510_Module2_Project/.venv/bin/python src/ws_e_balance.py
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.proportion import proportion_confint

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths as P  # noqa: E402

OUT = P.RESULTS / "ws_e"
OUT.mkdir(parents=True, exist_ok=True)
RNG = np.random.default_rng(20261102)
ELEM = P.ELEM_CODES
NAME = {v: k for k, v in ELEM.items()}

pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 60)


def wilson(k, n):
    if n == 0:
        return (np.nan, np.nan)
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    return (100 * lo, 100 * hi)


def gini(x):
    x = np.sort(np.asarray(x, dtype=float))
    n = len(x)
    if n == 0 or x.sum() == 0:
        return np.nan
    cum = np.cumsum(x)
    return (n + 1 - 2 * np.sum(cum) / cum[-1]) / n


def dispersion(x):
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    return dict(n=len(x), min=x.min(), max=x.max(), range=x.max() - x.min(),
                max_min_ratio=x.max() / x.min(), mean=x.mean(), sd=x.std(ddof=1),
                cv=x.std(ddof=1) / x.mean(), gini=gini(x))


# ----------------------------------------------------------------------------------------------
# Task 1: school-level balance table
# ----------------------------------------------------------------------------------------------
eds = pd.read_csv(P.DPI_EDS, dtype={"agency_code": str})
eds = eds[eds.agency_code.isin(list(ELEM) + [P.CHCCS_LEA])].copy()
eds["school"] = eds.agency_code.map(ELEM).fillna("CHCCS (district, all grades)")
eds["eds_masked"] = eds.pct_eds_masking.notna()
assert not eds.eds_masked.any(), "unexpected EDS masking for CHCCS"
eds_wide = eds.pivot(index="school", columns="year", values="pct_eds")

chronic = pd.read_csv(P.DPI_CHRONIC, dtype={"agency_code": str})
chronic = chronic[chronic.agency_code.isin(list(ELEM) + [P.CHCCS_LEA]) & (chronic.subgroup == "ALL")].copy()
chronic["school"] = chronic.agency_code.map(ELEM).fillna("CHCCS (district, all grades)")
# masking == 2 means DPI reports the rate as "<5%" and stores 0.05; treat as a floor, not a value
chronic["chronic_pct"] = np.where(chronic.masking.notna(), np.nan, 100 * chronic.pct)
chronic["chronic_masked_lt5"] = chronic.masking.notna()

adm = pd.read_csv(P.SCHOOL_ADM, dtype={"agency_code": str})
adm = adm[adm.agency_code.isin(ELEM)].copy()
adm["school"] = adm.agency_code.map(ELEM)

long = (eds[["school", "year", "pct_eds"]]
        .merge(chronic[["school", "year", "chronic_pct", "chronic_masked_lt5"]], on=["school", "year"], how="outer")
        .merge(adm[["school", "year", "avg_student_num"]].rename(columns={"avg_student_num": "adm"}),
               on=["school", "year"], how="left"))
long = long[long.year.between(2017, 2025)].sort_values(["school", "year"])
long.to_csv(OUT / "school_balance_long_2017_2025.csv", index=False)

metrics = pd.read_csv(P.SCHOOL_METRICS, dtype={"dpi_code": str})
metrics = metrics[metrics.dpi_code.isin(ELEM)].copy()
metrics["school"] = metrics.dpi_code.map(ELEM)
metrics = metrics.rename(columns={"adm": "adm_2024_25", "adm_utilization_percent": "util_sapfo_2024_25",
                                  "projected_utilization_2030_31": "util_projected_2031"})

# School performance grades (archive file). Inspected: one sheet, years 2018-2019 and 2022-2025,
# subgroup rows; spg_score/spg_grade unmasked for all 11 schools. Use ALL and EDS subgroups, 2025.
spg = pd.read_excel(P.SPG_XLSX, dtype=str)
spg = spg[spg.agency_code.isin(ELEM)].copy()
spg["school"] = spg.agency_code.map(ELEM)
spg["year"] = spg.year.astype(int)
spg_all = spg[(spg.subgroup == "ALL")][["school", "year", "spg_score", "spg_grade", "ach_score", "eg_status", "eg_score"]]
spg_all = spg_all.astype({"spg_score": float, "ach_score": float, "eg_score": float})
spg_all.sort_values(["school", "year"]).to_csv(OUT / "spg_by_school_year.csv", index=False)
spg25 = spg_all[spg_all.year == 2025].drop(columns="year").rename(
    columns={"spg_score": "spg_score_2025", "spg_grade": "spg_grade_2025", "ach_score": "ach_score_2025",
             "eg_status": "growth_status_2025", "eg_score": "growth_score_2025"})
spg25_eds = spg[(spg.subgroup == "EDS") & (spg.year == 2025)][["school", "spg_score", "spg_grade"]].rename(
    columns={"spg_score": "spg_score_eds_subgroup_2025", "spg_grade": "spg_grade_eds_subgroup_2025"})
spg25_eds["spg_score_eds_subgroup_2025"] = spg25_eds.spg_score_eds_subgroup_2025.astype(float)

# Closure study cells (May 7 2026 study, Oct 2025 20th-day data; narrative text only -- the table
# itself did not survive PDF-to-text). District-wide comparison figures are NOT given in the text.
closure_cells = pd.DataFrame([
    ("Ephesus", "White", 50.6), ("Ephesus", "Asian", 14.3), ("Ephesus", "Black", 15.3), ("Ephesus", "Latinx", 13.0),
    ("Ephesus", "Multiracial", 6.4), ("Ephesus", "Economically Disadvantaged", 34.5), ("Ephesus", "SWD", 13.3),
    ("Glenwood", "Asian", 38.0), ("Glenwood", "White", 35.4), ("Glenwood", "Black", 8.6), ("Glenwood", "Latinx", 4.6),
    ("Glenwood", "Multiracial", 12.9), ("Glenwood", "Economically Disadvantaged", 17.5), ("Glenwood", "SWD", 9.1),
    ("Seawell", "White", 34.9), ("Seawell", "Asian", 28.6), ("Seawell", "Black", 16.5), ("Seawell", "Latinx", 11.1),
    ("Seawell", "Multiracial", 8.9), ("Seawell", "Economically Disadvantaged", 32.2), ("Seawell", "Multilingual Learners", 16.5),
], columns=["school", "measure", "pct"])
closure_cells["source"] = "closure_study_2026-05-07.txt pp.16 (Oct 2025 20th-day); ML given for Seawell only; no district comparison in text"
closure_cells.to_csv(OUT / "closure_study_demographic_cells.csv", index=False)
closure_notes = {
    "title_i": "Ephesus is 1 of 6 Title I elementary schools (study p.16, p.36); the other five are not named in the text",
    "glenwood_lottery": "Glenwood March 2026: 391 enrolled, 188 Mandarin Dual Language + 203 World Language; both lottery-based, district-wide; zoned non-lottery students go to Estes Hills, Rashkis or Scroggs",
    "attendance_2024_25": "ADA: Glenwood 95.3, Ephesus 95.0, Seawell 94.6 (study p.20)",
}

eds25 = eds_wide[2025].rename("pct_eds_2025")
eds17 = eds_wide[2017].rename("pct_eds_2017")
chr25 = chronic[chronic.year == 2025].set_index("school").chronic_pct.rename("chronic_absent_pct_2025")
bal = (metrics.set_index("school")[["dpi_code", "adm_2024_25", "sapfo_capacity", "util_sapfo_2024_25",
                                    "program_capacity_2026", "util_projected_2031"]]
       .join(eds17).join(eds25).join(chr25)
       .join(spg25.set_index("school")).join(spg25_eds.set_index("school")))
bal["eds_change_2017_2025_pts"] = bal.pct_eds_2025 - bal.pct_eds_2017
bal["eds_students_2025_est"] = (bal.pct_eds_2025 / 100 * bal.adm_2024_25).round(0)
bal["empty_seats_sapfo_2024_25"] = bal.sapfo_capacity - bal.adm_2024_25
bal["closure_candidate"] = bal.index.isin(P.CLOSURE_CANDIDATES)
bal["dli"] = bal.index.map(lambda s: P.DLI_SCHOOLS.get(s, ""))
bal = bal.sort_values("pct_eds_2025", ascending=False)
bal.to_csv(OUT / "school_balance_2025.csv")
print("\n== School balance table 2025 ==")
print(bal[["pct_eds_2017", "pct_eds_2025", "util_sapfo_2024_25", "util_projected_2031", "chronic_absent_pct_2025",
           "spg_score_2025", "spg_grade_2025", "spg_score_eds_subgroup_2025"]].round(1).to_string())

# ----------------------------------------------------------------------------------------------
# Task 2: quantify imbalance
# ----------------------------------------------------------------------------------------------
rows = []
for yr in range(2017, 2026):
    x = eds_wide.loc[list(ELEM.values()), yr]
    d = dispersion(x)
    d.update(measure="pct_eds", year=yr, top=x.idxmax(), bottom=x.idxmin(),
             district_lea=eds_wide.loc["CHCCS (district, all grades)", yr])
    # ADM-weighted mean of the 11 schools (elementary-only EDS share)
    w = adm[adm.year == yr].set_index("school").avg_student_num.reindex(x.index)
    d["adm_weighted_mean"] = float(np.average(x, weights=w)) if w.notna().all() else np.nan
    rows.append(d)
for col, label in [("util_sapfo_2024_25", "utilization_sapfo_2024_25"), ("util_projected_2031", "utilization_projected_2031")]:
    x = bal[col]
    d = dispersion(x)
    d.update(measure=label, year=2025 if "2024" in label else 2031, top=x.idxmax(), bottom=x.idxmin())
    rows.append(d)
for yr in [2022, 2023, 2024, 2025]:  # chronic absenteeism unmasked for all 11 from 2022
    x = chronic[(chronic.year == yr) & (chronic.school != "CHCCS (district, all grades)")].set_index("school").chronic_pct
    if x.notna().sum() == 11:
        d = dispersion(x)
        d.update(measure="chronic_absent_pct", year=yr, top=x.idxmax(), bottom=x.idxmin())
        rows.append(d)
imb = pd.DataFrame(rows)
imb.to_csv(OUT / "imbalance_by_year.csv", index=False)
print("\n== Dispersion of EDS share across 11 schools, by year ==")
print(imb[imb.measure == "pct_eds"][["year", "min", "max", "range", "max_min_ratio", "sd", "cv", "gini", "adm_weighted_mean", "district_lea", "top", "bottom"]].round(3).to_string())
print(imb[imb.measure != "pct_eds"][["measure", "year", "min", "max", "range", "max_min_ratio", "sd", "cv", "gini", "top", "bottom"]].round(3).to_string())

# Trend in dispersion: Spearman of year vs SD / range over the 9 years, plus Monte Carlo p
e = imb[imb.measure == "pct_eds"]
trend = []
for col in ["sd", "range", "gini", "cv"]:
    rho, p = stats.spearmanr(e.year, e[col])
    trend.append(dict(stat=col, spearman_rho_vs_year=rho, p_asymptotic=p, value_2017=e[col].iloc[0], value_2025=e[col].iloc[-1]))
trend = pd.DataFrame(trend)
trend.to_csv(OUT / "imbalance_trend_2017_2025.csv", index=False)
print("\n== Trend of dispersion statistics vs year (n=9 years) ==")
print(trend.round(3).to_string())

# Which schools moved: change 2017->2025 and 2019->2025 by school
mv = pd.DataFrame({"pct_eds_2017": eds_wide[2017], "pct_eds_2019": eds_wide[2019], "pct_eds_2025": eds_wide[2025]})
mv["change_2017_2025"] = mv.pct_eds_2025 - mv.pct_eds_2017
mv["change_2019_2025"] = mv.pct_eds_2025 - mv.pct_eds_2019
mv.sort_values("change_2017_2025", ascending=False).to_csv(OUT / "eds_change_by_school.csv")

# Demographic vs capacity imbalance: Spearman with n=11 and a Monte Carlo permutation p
def spearman_mc(x, y, n_perm=20000):
    x = np.asarray(x, float); y = np.asarray(y, float)
    ok = ~(np.isnan(x) | np.isnan(y)); x, y = x[ok], y[ok]
    rho, p_asym = stats.spearmanr(x, y)
    perm = np.array([stats.spearmanr(x, RNG.permutation(y))[0] for _ in range(n_perm)])
    p_mc = (np.sum(np.abs(perm) >= abs(rho)) + 1) / (n_perm + 1)
    return rho, p_asym, p_mc, int(ok.sum())

pairs = [
    ("pct_eds_2025", "util_sapfo_2024_25"), ("pct_eds_2025", "util_projected_2031"),
    ("pct_eds_2025", "empty_seats_sapfo_2024_25"), ("pct_eds_2025", "chronic_absent_pct_2025"),
    ("pct_eds_2025", "spg_score_2025"), ("pct_eds_2025", "spg_score_eds_subgroup_2025"),
    ("pct_eds_2025", "eds_change_2017_2025_pts"), ("util_sapfo_2024_25", "util_projected_2031"),
]
corr = []
for a, b in pairs:
    rho, pa, pmc, n = spearman_mc(bal[a], bal[b])
    corr.append(dict(x=a, y=b, n=n, spearman_rho=rho, p_asymptotic=pa, p_monte_carlo=pmc))
corr = pd.DataFrame(corr)
corr["p_bh"] = multipletests(corr.p_monte_carlo, method="fdr_bh")[1]
corr.to_csv(OUT / "correlations_school_level.csv", index=False)
print("\n== School-level Spearman correlations (n=11, Monte Carlo p, BH across 8) ==")
print(corr.round(3).to_string())

scatter = bal[["dpi_code", "pct_eds_2025", "util_sapfo_2024_25", "util_projected_2031", "adm_2024_25", "sapfo_capacity",
               "program_capacity_2026", "chronic_absent_pct_2025", "spg_score_2025", "spg_grade_2025", "closure_candidate", "dli"]].copy()
scatter.to_csv(OUT / "eds_vs_utilization_scatter.csv")

# ----------------------------------------------------------------------------------------------
# Task 3: closure candidates on the EDS gradient (no assignment modelling)
# ----------------------------------------------------------------------------------------------
md = json.load(open(P.MAP_DATA))
loc = {s["name"].replace(" Elementary", ""): s["location"] for s in md["schools"] if s.get("level") == "elementary"}
loc = {k: v for k, v in loc.items() if k in NAME}
assert len(loc) == 11, loc.keys()

def hav(a, b):
    R = 6371.0
    la1, lo1, la2, lo2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))

wmean25 = float(np.average(bal.pct_eds_2025, weights=bal.adm_2024_25))
rank = bal.pct_eds_2025.rank(ascending=False).astype(int)
crow = []
for cand in sorted(P.CLOSURE_CANDIDATES):
    dists = sorted(((hav(loc[cand], loc[o]), o) for o in loc if o != cand))
    nbrs = dists[:3]
    rem = bal.drop(index=cand).pct_eds_2025
    drem = dispersion(rem)
    r = dict(school=cand, pct_eds_2025=bal.loc[cand, "pct_eds_2025"], eds_rank_of_11=rank[cand],
             adm_2024_25=bal.loc[cand, "adm_2024_25"], eds_students_est=bal.loc[cand, "eds_students_2025_est"],
             pts_vs_adm_weighted_mean=bal.loc[cand, "pct_eds_2025"] - wmean25,
             util_sapfo_2024_25=bal.loc[cand, "util_sapfo_2024_25"], util_projected_2031=bal.loc[cand, "util_projected_2031"],
             spg_grade_2025=bal.loc[cand, "spg_grade_2025"], chronic_absent_pct_2025=bal.loc[cand, "chronic_absent_pct_2025"],
             range_remaining_10=drem["range"], sd_remaining_10=drem["sd"], gini_remaining_10=drem["gini"])
    for i, (dk, o) in enumerate(nbrs, 1):
        r[f"nearest_{i}"] = o
        r[f"nearest_{i}_km"] = round(dk, 2)
        r[f"nearest_{i}_pct_eds_2025"] = bal.loc[o, "pct_eds_2025"]
        r[f"nearest_{i}_util_2031"] = bal.loc[o, "util_projected_2031"]
        r[f"nearest_{i}_empty_seats_2024_25"] = bal.loc[o, "empty_seats_sapfo_2024_25"]
    crow.append(r)
cand_tbl = pd.DataFrame(crow)
cand_tbl.to_csv(OUT / "closure_candidates_on_gradient.csv", index=False)
print(f"\n== Closure candidates on the EDS gradient (ADM-weighted elementary mean EDS 2025 = {wmean25:.1f}%) ==")
print(cand_tbl.round(2).T.to_string())
full = dispersion(bal.pct_eds_2025)
print(f"All 11: range {full['range']:.1f}, sd {full['sd']:.2f}, gini {full['gini']:.3f}")

# ----------------------------------------------------------------------------------------------
# Task 4: survey side
# ----------------------------------------------------------------------------------------------
r = pd.read_csv(P.RESPONSES_WIDE)
rp = pd.read_csv(P.M2_EXPL / "05_rating_patterns" / "results" / "rating_patterns_by_response.csv")
wi = pd.read_csv(P.WRITE_IN_CODES)
r = r.merge(rp[["participant_id", "values_n5", "values_straightline", "challenges_n5"]], on="participant_id", how="left")
eq_cols = [c for c in wi.columns if c.endswith("|Equity & the achievement gap")]
wi["equity_any"] = wi[eq_cols].any(axis=1)
wi["wrote_any_text"] = wi.drop(columns=["participant_id", "equity_any"]).any(axis=1)
r = r.merge(wi[["participant_id", "equity_any"]], on="participant_id", how="left")
r["wrote_any_text"] = r[["other_challenges", "other_values", "additional_thoughts"]].notna().any(axis=1) | (r.q9_value == "Other (write-in)")

V_WB = "V: Ensuring well-balanced student populations across all school sites"
C_UNEQ = "C: Unequal access to specialty programs"
C_BND = "C: Student populations have shifted, but school boundaries have not been adjusted to accommodate those changes"
C_EMPTY = "C: Partially empty school buildings"
# Q7 / Q8 free-text lists: match by substring (the boundaries item contains a comma; "School saftey" typo exists)
C_SUB = {
    "Cost of maintaining aging buildings": "Cost of maintaining aging buildings",
    "School buildings meeting safety codes": "meeting safety codes",
    "Length of commute for students riding buses": "Length of commute",
    "Retaining highly effective employees": "Retaining highly effective employees",
    "Partially empty school buildings": "Partially empty school buildings",
    "Overcrowded school buildings": "Overcrowded school buildings",
    "The number of trailers / mobile classrooms": "number of trailers",
    "Buildings do not fit the modern academic program": "fit the modern academic program",
    "Buildings do not fit modern operational expectations": "fit the modern operational expectations",
    "Unequal access to specialty programs": "Unequal access to specialty programs",
    "Classroom technology updates": "Classroom technology updates",
    "Appeal of the district to current and prospective students": "Appeal of the district",
    "Boundaries not adjusted to shifted student populations": "boundaries have not been adjusted",
}
V_SUB = {
    "Educational excellence": "Educational excellence", "Student-centered focus": "Student-centered focus",
    "Fiscal responsibility": "Fiscal responsibility", "Community engagement & trust building": "Community engagement",
    "Minimizing the distance students travel": "distance students travel",
    "Maximizing the use of currently available buildings": "use of currently available buildings",
    "School safety": "School saf", "Long-term planning": "Long-term planning",
    "Collaboration between schools and county leadership": "Collaboration between schools",
    "Community partnerships": "Community partnerships", "High-quality school meal service": "school meal service",
    "Increasing the use of renewable energy": "renewable energy",
    "Ensuring well-balanced student populations": "well-balanced student populations",
}
for k, s in C_SUB.items():
    r["q7|" + k] = r.top3_challenges.fillna("").str.contains(s, regex=False)
for k, s in V_SUB.items():
    r["q8|" + k] = r.top3_values.fillna("").str.contains(s, regex=False)
r["q9_wb"] = r.q9_value == "Ensuring well-balanced student populations across all school sites"
r["q9_answered"] = r.q9_value.notna()
r["q8_answered"] = r.top3_values.notna()
r["q7_answered"] = r.top3_challenges.notna()

def splits(df):
    out = [("group", "Parent (all)", df.group == "Parent"),
           ("group", "Other parents (not staff)", (df.group == "Parent") & ~df.employee),
           ("group", "Parents who are staff", (df.group == "Parent") & df.employee),
           ("group", "Non-parent (mostly staff)", df.group == "Non-parent"),
           ("group", "Non-parent staff", (df.group == "Non-parent") & df.employee),
           ("group", "All respondents", pd.Series(True, index=df.index))]
    for a in ["18 to 29 years", "30 to 39 years", "40 to 49 years", "50 to 64 years", "65+ years"]:
        out.append(("age", a, df.age == a))
    out.append(("language", "English sheet", df.source_sheet == "English"))
    out.append(("language", "Non-English sheets (all)", df.source_sheet != "English"))
    for s in ["Spanish", "Chinese"]:
        out.append(("language", s + " sheet", df.source_sheet == s))
    return out

ITEMS = [
    ("Well-balanced populations", "Q5 rated 4-5", lambda d: d[V_WB] >= 4, lambda d: d[V_WB].notna()),
    ("Well-balanced populations", "Q5 rated 5", lambda d: d[V_WB] == 5, lambda d: d[V_WB].notna()),
    ("Well-balanced populations", "Q8 top-3", lambda d: d["q8|Ensuring well-balanced student populations"], lambda d: d.q8_answered),
    ("Well-balanced populations", "Q9 the one value", lambda d: d.q9_wb, lambda d: d.q9_answered),
    ("Unequal access to specialty programs", "Q3 rated 4-5", lambda d: d[C_UNEQ] >= 4, lambda d: d[C_UNEQ].notna()),
    ("Unequal access to specialty programs", "Q7 top-3", lambda d: d["q7|Unequal access to specialty programs"], lambda d: d.q7_answered),
    ("Boundaries not adjusted", "Q3 rated 4-5", lambda d: d[C_BND] >= 4, lambda d: d[C_BND].notna()),
    ("Boundaries not adjusted", "Q7 top-3", lambda d: d["q7|Boundaries not adjusted to shifted student populations"], lambda d: d.q7_answered),
    ("Partially empty buildings", "Q3 rated 4-5", lambda d: d[C_EMPTY] >= 4, lambda d: d[C_EMPTY].notna()),
    ("Partially empty buildings", "Q7 top-3", lambda d: d["q7|Partially empty school buildings"], lambda d: d.q7_answered),
    ("Equity & achievement gap write-in theme", "any text field coded equity", lambda d: d.equity_any.fillna(False), lambda d: pd.Series(True, index=d.index)),
    ("Equity & achievement gap write-in theme", "among those who wrote any text", lambda d: d.equity_any.fillna(False), lambda d: d.wrote_any_text),
]
srows = []
for sname, level, mask in splits(r):
    d = r[mask]
    for item, measure, num, den in ITEMS:
        dd = d[den(d)]
        n = len(dd); k = int(num(dd).sum())
        if n < 10:
            srows.append(dict(split=sname, level=level, item=item, measure=measure, n="<10", k="<10", pct=np.nan, wilson_lo=np.nan, wilson_hi=np.nan))
            continue
        lo, hi = wilson(k, n)
        srows.append(dict(split=sname, level=level, item=item, measure=measure, n=n, k=k if k >= 10 or k == 0 else "<10",
                          pct=100 * k / n, wilson_lo=lo, wilson_hi=hi))
surv = pd.DataFrame(srows)
surv.to_csv(OUT / "survey_items_by_split.csv", index=False)
print("\n== Survey items by group ==")
print(surv[surv.split == "group"].pivot_table(index=["item", "measure"], columns="level", values="pct").round(1).to_string())
print("\n== Survey items by age / language (pct) ==")
print(surv[surv.split != "group"].pivot_table(index=["item", "measure"], columns="level", values="pct").round(1).to_string())
print(surv[surv.item.str.startswith("Equity")][["split", "level", "measure", "n", "k", "pct"]].to_string())

# Q7 x Q8 co-selection: is "well-balanced" in a respondent's top-3 values associated with each top-3 challenge?
def coselect(df, label):
    base = df[df.q8_answered & df.q7_answered]
    wb = base["q8|Ensuring well-balanced student populations"]
    rows = []
    for k in C_SUB:
        c = base["q7|" + k]
        a = int((wb & c).sum()); b = int((wb & ~c).sum()); cc = int((~wb & c).sum()); d = int((~wb & ~c).sum())
        orr, p = stats.fisher_exact([[a, b], [cc, d]])
        rows.append(dict(sample=label, q8_value="Well-balanced populations", q7_challenge=k, n=len(base),
                         wb_and_item=a, wb_not_item=b, item_not_wb=cc, neither=d,
                         pct_item_given_wb=100 * a / (a + b), pct_item_given_not_wb=100 * cc / (cc + d),
                         odds_ratio=orr, fisher_p=p))
    t = pd.DataFrame(rows)
    t["p_bh"] = multipletests(t.fisher_p, method="fdr_bh")[1]
    return t
co = pd.concat([coselect(r, "All respondents"), coselect(r[r.group == "Parent"], "Parents"),
                coselect(r[r.group == "Non-parent"], "Non-parents")], ignore_index=True)
co.to_csv(OUT / "q7_x_q8_wellbalanced_coselection.csv", index=False)
print("\n== Q8 well-balanced x Q7 challenge co-selection (Fisher, BH within sample) ==")
print(co[co["sample"] == "All respondents"][["q7_challenge", "wb_and_item", "pct_item_given_wb", "pct_item_given_not_wb", "odds_ratio", "fisher_p", "p_bh"]].round(3).to_string())
print(co[co["sample"] == "Parents"][["q7_challenge", "wb_and_item", "pct_item_given_wb", "pct_item_given_not_wb", "odds_ratio", "fisher_p", "p_bh"]].round(3).to_string())

# Q8 well-balanced vs other Q8 values (which values travel with it?) -- within-Q8 co-selection is
# constrained by the 3-pick limit, so ORs are biased below 1; shown for ranking only.
base = r[r.q8_answered]
wb = base["q8|Ensuring well-balanced student populations"]
q8rows = []
for k in V_SUB:
    if k.startswith("Ensuring"):
        continue
    c = base["q8|" + k]
    a = int((wb & c).sum()); b = int((wb & ~c).sum()); cc = int((~wb & c).sum()); d = int((~wb & ~c).sum())
    orr, p = stats.fisher_exact([[a, b], [cc, d]])
    q8rows.append(dict(other_q8_value=k, wb_and_item=a, pct_item_given_wb=100 * a / (a + b), pct_item_given_not_wb=100 * cc / (cc + d), odds_ratio=orr, fisher_p=p))
q8t = pd.DataFrame(q8rows); q8t["p_bh"] = multipletests(q8t.fisher_p, method="fdr_bh")[1]
q8t.to_csv(OUT / "q8_wellbalanced_x_other_values.csv", index=False)
print("\n== Q8 well-balanced x other Q8 values (3-pick constrained) ==")
print(q8t.round(3).to_string())

# Equity writers and well-balanced; heavy 5-raters
ex = []
def fisher_row(label, df, x, y):
    a = int((x & y).sum()); b = int((x & ~y).sum()); c = int((~x & y).sum()); d = int((~x & ~y).sum())
    orr, p = stats.fisher_exact([[a, b], [c, d]])
    return dict(test=label, n=len(df), x_and_y=a, x_not_y=b, y_not_x=c, neither=d,
                pct_y_given_x=100 * a / (a + b) if a + b else np.nan, pct_y_given_not_x=100 * c / (c + d), odds_ratio=orr, fisher_p=p)
b8 = r[r.q8_answered]
ex.append(fisher_row("Equity write-in theme (x) vs Q8 top-3 includes well-balanced (y), all", b8, b8.equity_any.fillna(False), b8["q8|Ensuring well-balanced student populations"]))
b8p = b8[b8.group == "Parent"]
ex.append(fisher_row("Equity write-in theme (x) vs Q8 well-balanced (y), parents", b8p, b8p.equity_any.fillna(False), b8p["q8|Ensuring well-balanced student populations"]))
b9 = r[r.q9_answered]
ex.append(fisher_row("Equity write-in theme (x) vs Q9 well-balanced (y), all", b9, b9.equity_any.fillna(False), b9.q9_wb))
b5 = r[r[V_WB].notna()]
ex.append(fisher_row("Equity write-in theme (x) vs Q5 well-balanced rated 4-5 (y), all", b5, b5.equity_any.fillna(False), b5[V_WB] >= 4))
bt = b8[b8.wrote_any_text]
ex.append(fisher_row("Equity theme (x) vs Q8 well-balanced (y), among respondents who wrote any text", bt, bt.equity_any.fillna(False), bt["q8|Ensuring well-balanced student populations"]))
ext = pd.DataFrame(ex); ext["p_bh"] = multipletests(ext.fisher_p, method="fdr_bh")[1]
ext.to_csv(OUT / "equity_writers_vs_wellbalanced.csv", index=False)
print("\n== Equity write-in theme vs well-balanced ==")
print(ext.round(3).to_string())

# Heavy 5-raters: exclude respondents with 10+ fives on the 13 values, recompute the group gap
heavy = r.values_n5 >= 10
hrows = []
for excl_label, mask in [("All respondents", pd.Series(True, index=r.index)), ("Excluding 10+ fives on values", ~heavy),
                         ("Excluding 13/13 fives (straightline 5s)", ~(r.values_n5 == 13))]:
    for g, gm in [("Parent (all)", r.group == "Parent"), ("Other parents (not staff)", (r.group == "Parent") & ~r.employee),
                  ("Parents who are staff", (r.group == "Parent") & r.employee), ("Non-parent (mostly staff)", r.group == "Non-parent")]:
        d = r[mask & gm & r[V_WB].notna()]
        n = len(d); k = int((d[V_WB] >= 4).sum()); k5 = int((d[V_WB] == 5).sum())
        lo, hi = wilson(k, n)
        d8 = r[mask & gm & r.q8_answered]; k8 = int(d8["q8|Ensuring well-balanced student populations"].sum())
        hrows.append(dict(sample=excl_label, group=g, n=n, pct_heavy_5_raters_in_group=100 * (r[gm].values_n5 >= 10).mean(),
                          wb_rated_4_5_pct=100 * k / n, wilson_lo=lo, wilson_hi=hi, wb_rated_5_pct=100 * k5 / n,
                          wb_mean_rating=d[V_WB].mean(), q8_top3_pct=100 * k8 / len(d8), q8_n=len(d8)))
hv = pd.DataFrame(hrows)
hv.to_csv(OUT / "wellbalanced_gap_excluding_heavy_5_raters.csv", index=False)
print("\n== Well-balanced parent vs staff gap, with and without heavy 5-raters ==")
print(hv.round(1).to_string())
# Mann-Whitney on the 1-5 rating, parents vs non-parents, both samples
mw = []
for excl_label, mask in [("All respondents", pd.Series(True, index=r.index)), ("Excluding 10+ fives on values", ~heavy)]:
    a = r[mask & (r.group == "Parent")][V_WB].dropna(); b = r[mask & (r.group == "Non-parent")][V_WB].dropna()
    u, p = stats.mannwhitneyu(a, b, alternative="two-sided")
    cles = u / (len(a) * len(b))
    mw.append(dict(sample=excl_label, n_parent=len(a), n_nonparent=len(b), parent_mean=a.mean(), nonparent_mean=b.mean(),
                   mann_whitney_U=u, p=p, prob_parent_rates_higher=cles))
mw = pd.DataFrame(mw); mw.to_csv(OUT / "wellbalanced_mannwhitney_parent_vs_nonparent.csv", index=False)
print(mw.round(4).to_string())

# ----------------------------------------------------------------------------------------------
# Task 5: board vs parents vs staff on four items
# ----------------------------------------------------------------------------------------------
board = pd.read_csv(P.BOARD_VS_CPA)
bmap = {"Well-balanced populations": "Ensuring well-balanced student populations",
        "Boundaries not adjusted": "Boundaries not adjusted to shifted student populations",
        "Partially empty buildings": "Partially empty school buildings",
        "Unequal access to specialty programs": "Unequal access to specialty programs"}
rating_col = {"Well-balanced populations": V_WB, "Boundaries not adjusted": C_BND, "Partially empty buildings": C_EMPTY, "Unequal access to specialty programs": C_UNEQ}
top3_col = {"Well-balanced populations": "q8|Ensuring well-balanced student populations", "Boundaries not adjusted": "q7|Boundaries not adjusted to shifted student populations",
            "Partially empty buildings": "q7|Partially empty school buildings", "Unequal access to specialty programs": "q7|Unequal access to specialty programs"}
brows = []
for item, bitem in bmap.items():
    bb = board[board.item == bitem].iloc[0]
    brows.append(dict(item=item, respondent="Board (n=7, district report)", measure="rated 4-5", n=7, pct=bb.board_pct_rated_4_5, wilson_lo=wilson(round(bb.board_pct_rated_4_5 * 7 / 100), 7)[0], wilson_hi=wilson(round(bb.board_pct_rated_4_5 * 7 / 100), 7)[1]))
    brows.append(dict(item=item, respondent="Board (n=7, district report)", measure="top-3", n=7, pct=bb.board_pct_top3, wilson_lo=wilson(round(bb.board_pct_top3 * 7 / 100), 7)[0], wilson_hi=wilson(round(bb.board_pct_top3 * 7 / 100), 7)[1]))
    brows.append(dict(item=item, respondent="All CPA respondents (district report)", measure="rated 4-5", n=1463, pct=bb.cpa_pct_rated_4_5, wilson_lo=np.nan, wilson_hi=np.nan))
    brows.append(dict(item=item, respondent="All CPA respondents (district report)", measure="top-3", n=1463, pct=bb.cpa_pct_top3, wilson_lo=np.nan, wilson_hi=np.nan))
    for g, gm in [("Other parents (not staff)", (r.group == "Parent") & ~r.employee), ("Parents who are staff", (r.group == "Parent") & r.employee),
                  ("Non-parent (mostly staff)", r.group == "Non-parent")]:
        d = r[gm & r[rating_col[item]].notna()]; n = len(d); k = int((d[rating_col[item]] >= 4).sum()); lo, hi = wilson(k, n)
        brows.append(dict(item=item, respondent=g, measure="rated 4-5", n=n, pct=100 * k / n, wilson_lo=lo, wilson_hi=hi))
        ans = r.q8_answered if item == "Well-balanced populations" else r.q7_answered
        d = r[gm & ans]; n = len(d); k = int(d[top3_col[item]].sum()); lo, hi = wilson(k, n)
        brows.append(dict(item=item, respondent=g, measure="top-3", n=n, pct=100 * k / n, wilson_lo=lo, wilson_hi=hi))
bt = pd.DataFrame(brows)
bt.to_csv(OUT / "board_parents_staff_four_items.csv", index=False)
print("\n== Board vs parents vs staff ==")
print(bt.pivot_table(index=["item", "measure"], columns="respondent", values="pct").round(0).to_string())

json.dump({"closure_study_notes": closure_notes, "adm_weighted_elementary_eds_2025": wmean25,
           "n_heavy_5_raters_values": int(heavy.sum()), "n_equity_writers": int(r.equity_any.fillna(False).sum())},
          open(OUT / "notes.json", "w"), indent=2)
print("\nWrote", sorted(p.name for p in OUT.iterdir()))

# ----------------------------------------------------------------------------------------------
# Extras: where the empty seats are on the EDS gradient; trend without pandemic years
# ----------------------------------------------------------------------------------------------
es = bal[["pct_eds_2025", "adm_2024_25", "sapfo_capacity", "program_capacity_2026", "util_projected_2031"]].copy()
es["projected_adm_2031"] = (es.program_capacity_2026 * es.util_projected_2031 / 100).round(0)
es["projected_empty_seats_2031"] = es.program_capacity_2026 - es.projected_adm_2031
es["empty_seats_sapfo_2024_25"] = es.sapfo_capacity - es.adm_2024_25
es["eds_students_2025_est"] = (es.pct_eds_2025 / 100 * es.adm_2024_25).round(0)
es["share_of_elem_adm_2024_25"] = 100 * es.adm_2024_25 / es.adm_2024_25.sum()
es["share_of_elem_eds_students"] = 100 * es.eds_students_2025_est / es.eds_students_2025_est.sum()
pos = es.projected_empty_seats_2031.clip(lower=0)
es["share_of_2031_empty_seats"] = 100 * pos / pos.sum()
es["eds_tercile"] = pd.qcut(es.pct_eds_2025, 3, labels=["low EDS", "mid EDS", "high EDS"])
es.to_csv(OUT / "empty_seats_on_gradient.csv")
print("\n== Empty seats on the EDS gradient ==")
print(es.round(1).to_string())
print(es.groupby("eds_tercile", observed=True)[["adm_2024_25", "eds_students_2025_est", "empty_seats_sapfo_2024_25", "projected_empty_seats_2031"]].sum().to_string())
top2 = es.loc[["Northside", "Rashkis"]]
print(f"Northside+Rashkis: {top2.share_of_elem_adm_2024_25.sum():.1f}% of elementary ADM, {top2.share_of_elem_eds_students.sum():.1f}% of EDS students, "
      f"{top2.share_of_2031_empty_seats.sum():.1f}% of projected 2031 empty seats ({int(top2.projected_empty_seats_2031.sum())} of {int(pos.sum())})")
e2 = e[~e.year.isin([2021, 2022])]
print("Trend of SD excluding 2021-22:", stats.spearmanr(e2.year, e2.sd))
print("Trend of range excluding 2021-22:", stats.spearmanr(e2.year, e2.range))
