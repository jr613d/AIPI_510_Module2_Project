"""Workstream A: who answered the CHCCS Community Priorities Assessment vs. who the
redistricting decision affects.

Reads only the Module 1 / Module 2 inputs listed in paths.py and writes CSV/JSON tables to
results/ws_a/. Run with the Module 2 venv interpreter:

    /Users/jim/dukeaipi/510_Sourcing_Data/Module_2_Project/AIPI_510_Module2_Project/.venv/bin/python \
        src/ws_a_representation.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402

OUT = paths.RESULTS / "ws_a"
OUT.mkdir(parents=True, exist_ok=True)

SUMMARY: dict = {}


# --------------------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------------------
def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion, returned as (lo, hi) in [0, 1]."""
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def pct(k, n, nd=1):
    return round(100 * k / n, nd) if n else np.nan


def mask_small(k: int) -> str | int:
    return "<10" if 0 < k < 10 else k


def save(df: pd.DataFrame, name: str) -> None:
    df.to_csv(OUT / name, index=False)
    print(f"wrote {OUT / name}  ({len(df)} rows)")


# --------------------------------------------------------------------------------------
# load survey tables
# --------------------------------------------------------------------------------------
rw = pd.read_csv(paths.RESPONSES_WIDE)
q1 = pd.read_csv(paths.Q1_ROLES)
q9 = pd.read_csv(paths.Q9_THEMES)
wic = pd.read_csv(paths.WRITE_IN_CODES)
assert (rw.participant_id == q1.participant_id).all()
assert (rw.participant_id == q9.participant_id).all()
N = len(rw)

ROLE_COLS = {
    "student": "Current CHCCS student",
    "graduate": "CHCCS graduate",
    "parent_current": "Parent of current CHCCS student(s)",
    "parent_graduated": "Parent of graduated CHCCS student(s)",
    "parent_not_chccs": "Parent of school-age children NOT attending CHCCS",
    "teacher": "Teacher in CHCCS",
    "admin": "Administrator in CHCCS",
    "staff": "Staff in CHCCS",
    "educator_elsewhere": "Teacher, administrator, or school staff who does NOT work in CHCCS",
    "county_official": "Orange County elected official or staff",
    "municipal_official": "Local municipal elected official or staff",
    "resident": "Orange County resident",
    "other": "Other (write-in)",
}
roles = q1[list(ROLE_COLS.values())].astype(int)
roles.columns = list(ROLE_COLS.keys())
roles["any_chccs_staff"] = roles[["teacher", "admin", "staff"]].max(axis=1)
roles["parent_excl_non_chccs"] = ((roles.parent_not_chccs == 1) & (roles.parent_current == 0)).astype(int)
roles["parent_both"] = ((roles.parent_not_chccs == 1) & (roles.parent_current == 1)).astype(int)
roles["resident_only"] = (roles.drop(columns=["any_chccs_staff", "parent_excl_non_chccs", "parent_both"]).sum(axis=1) == 1) & (roles.resident == 1)
roles["resident_only"] = roles["resident_only"].astype(int)
roles["future_parent"] = rw.future_parent.astype(int)

# ======================================================================================
# 1. Representation ratios
# ======================================================================================
rows = []
for key, label in [
    ("parent_current", "Parent of current CHCCS student(s)"),
    ("parent_not_chccs", "Parent of school-age children NOT attending CHCCS (any)"),
    ("parent_excl_non_chccs", "Parent whose school-age children are ALL outside CHCCS"),
    ("parent_both", "Parent with children both in and outside CHCCS"),
    ("parent_graduated", "Parent of graduated CHCCS student(s)"),
    ("future_parent", "Future parent (write-in flag)"),
    ("resident_only", "Orange County resident and nothing else"),
    ("resident", "Orange County resident (any)"),
    ("any_chccs_staff", "CHCCS teacher, administrator or staff (any)"),
    ("teacher", "Teacher in CHCCS"),
    ("staff", "Staff in CHCCS"),
    ("admin", "Administrator in CHCCS"),
    ("student", "Current CHCCS student"),
    ("graduate", "CHCCS graduate"),
    ("educator_elsewhere", "Educator who does NOT work in CHCCS"),
    ("county_official", "Orange County elected official or staff"),
    ("municipal_official", "Local municipal elected official or staff"),
    ("other", "Other (write-in)"),
]:
    k = int(roles[key].sum())
    lo, hi = wilson(k, N)
    rows.append({"role": label, "n": k, "n_reported": mask_small(k), "pct_of_respondents": pct(k, N),
                 "wilson_lo": round(100 * lo, 1), "wilson_hi": round(100 * hi, 1)})
role_tbl = pd.DataFrame(rows)
save(role_tbl, "respondent_roles.csv")

# Benchmark: district-resident school-age children not enrolled in CHCCS, 2019-2024
layers = pd.read_csv(paths.CHCCS_LAYERS)
layers["not_enrolled"] = layers.pop_5_17 - layers.total_adm
layers["pct_not_enrolled"] = (100 * layers.not_enrolled / layers.pop_5_17).round(1)
k_excl = int(roles.parent_excl_non_chccs.sum())
k_any = int(roles.parent_not_chccs.sum())
n_parents_schoolage = int(((roles.parent_current == 1) | (roles.parent_not_chccs == 1)).sum())
share_excl = k_excl / n_parents_schoolage
share_any = k_any / n_parents_schoolage
lo_e, hi_e = wilson(k_excl, n_parents_schoolage)
lo_a, hi_a = wilson(k_any, n_parents_schoolage)
layers["survey_pct_parents_excl_non_chccs"] = round(100 * share_excl, 2)
layers["underrep_factor_excl"] = (layers.pct_not_enrolled / (100 * share_excl)).round(1)
layers["survey_pct_parents_any_non_chccs"] = round(100 * share_any, 2)
layers["underrep_factor_any"] = (layers.pct_not_enrolled / (100 * share_any)).round(1)
save(layers[["year", "total_adm", "pop_5_17", "not_enrolled", "pct_not_enrolled", "capture_rate",
             "survey_pct_parents_excl_non_chccs", "underrep_factor_excl",
             "survey_pct_parents_any_non_chccs", "underrep_factor_any"]], "representation_vs_population.csv")

SUMMARY["representation"] = {
    "n_respondents": N,
    "parents_of_school_age_children_in_survey": n_parents_schoolage,
    "parents_excl_non_chccs": k_excl,
    "parents_excl_non_chccs_pct_of_school_age_parents": round(100 * share_excl, 2),
    "parents_excl_non_chccs_wilson": [round(100 * lo_e, 2), round(100 * hi_e, 2)],
    "parents_any_non_chccs": k_any,
    "parents_any_non_chccs_pct": round(100 * share_any, 2),
    "parents_any_non_chccs_wilson": [round(100 * lo_a, 2), round(100 * hi_a, 2)],
    "pct_children_not_enrolled_2024": float(layers.loc[layers.year == 2024, "pct_not_enrolled"].iloc[0]),
    "pct_children_not_enrolled_2019": float(layers.loc[layers.year == 2019, "pct_not_enrolled"].iloc[0]),
    "underrep_factor_excl_2024": float(layers.loc[layers.year == 2024, "underrep_factor_excl"].iloc[0]),
    "underrep_factor_any_2024": float(layers.loc[layers.year == 2024, "underrep_factor_any"].iloc[0]),
}

# ======================================================================================
# 2. The age pipeline (Orange County census cohorts) vs. parent ages in the survey
# ======================================================================================
def load_census(path: Path, year_map: dict[int, int]) -> pd.DataFrame:
    c = pd.read_csv(path, encoding="latin-1", low_memory=False)
    o = c[c.CTYNAME == "Orange County"].copy()
    o = o[o.YEAR.isin(year_map)]
    o["year"] = o.YEAR.map(year_map)
    keep = {"POPESTIMATE": "pop_total", "UNDER5_TOT": "under5", "AGE59_TOT": "age5_9", "AGE1014_TOT": "age10_14",
            "AGE513_TOT": "age5_13", "AGE1417_TOT": "age14_17", "AGE2529_TOT": "age25_29", "AGE3034_TOT": "age30_34",
            "AGE3539_TOT": "age35_39", "AGE4044_TOT": "age40_44", "AGE4549_TOT": "age45_49"}
    return o[["year"] + list(keep)].rename(columns=keep).reset_index(drop=True)


# 2019 vintage: YEAR 1 = April 2010 census, 2 = April 2010 estimates base, 3..12 = July 2010..2019
# (verified against the stitched podcast series). 2024 vintage: YEAR 1 = April 2020 base, 2..6 = July 2020..2024.
c19 = load_census(paths.CENSUS_AGESEX_2019, {y: 2007 + y for y in range(3, 13)})
c24 = load_census(paths.CENSUS_AGESEX_2024, {y: 2018 + y for y in range(2, 7)})
ages = pd.concat([c19, c24]).sort_values("year").reset_index(drop=True)
ages["vintage"] = np.where(ages.year <= 2019, "2019 vintage", "2024 vintage")
ages["under5_to_5_9"] = (ages.under5 / ages.age5_9).round(3)
ages["adults_30_39"] = ages.age30_34 + ages.age35_39
ages["adults_40_49"] = ages.age40_44 + ages.age45_49

# cross-check against the stitched podcast series
pj = json.load(open(paths.PODCAST_DATA))
oa = pj["orangeAges"]
pod = pd.DataFrame({"year": oa["years"], "under5_podcast": oa["under5"], "age5_9_podcast": oa["age5_9"],
                    "age10_14_podcast": oa["age10_14"]})
ages = ages.merge(pod, on="year", how="left")
ages["podcast_agrees"] = ((ages.under5 == ages.under5_podcast) & (ages.age5_9 == ages.age5_9_podcast)
                          & (ages.age10_14 == ages.age10_14_podcast))
save(ages, "orange_age_cohorts_2010_2024.csv")

base = ages[ages.year == 2010].iloc[0]
last = ages[ages.year == 2024].iloc[0]
cohort_change = pd.DataFrame([
    {"cohort": c, "y2010": int(base[c]), "y2019": int(ages[ages.year == 2019].iloc[0][c]), "y2024": int(last[c]),
     "pct_change_2010_2024": pct(last[c] - base[c], base[c]),
     "pct_change_2019_2024": pct(last[c] - ages[ages.year == 2019].iloc[0][c], ages[ages.year == 2019].iloc[0][c])}
    for c in ["under5", "age5_9", "age10_14", "age5_13", "age14_17", "adults_30_39", "adults_40_49"]
])
save(cohort_change, "orange_cohort_change.csv")

# Share of the K-5 population under the new boundaries (first six school years, 2027-28 .. 2032-33)
# that is not in school in fall 2026. Single-year cohort sizes approximated from the 2024 5-year bands.
u = last.under5 / 5          # born 2020-2024 (approx. per-year size)
f = last.age5_9 / 5          # born 2015-2019
# K-5 = ages 5-10 at fall. Children ever in K-5 during 2027-28..2032-33 were born 2017..2027 (11 cohorts).
enrolled_fall_2026 = 3 * f + 2 * u      # born 2017-2019 (f) and 2020-2021 (u): in K-5 in fall 2026 and still there in 2027-28+
not_yet = 6 * u                         # born 2022-2027 (assume 2025-2027 births ~ under-5 per-year size)
share_not_yet = not_yet / (enrolled_fall_2026 + not_yet)
pipeline = {
    "per_year_cohort_under5_2024": round(u),
    "per_year_cohort_5_9_2024": round(f),
    "under5_vs_5_9_ratio_2024": round(last.under5 / last.age5_9, 3),
    "under5_vs_5_9_ratio_2010": round(base.under5 / base.age5_9, 3),
    # fall 2027 K-5 = born 2017-2022; only the 2022 cohort is not in school in fall 2026
    "k5_2027_28_share_not_in_school_fall_2026": round(100 * (1 * u) / (3 * f + 3 * u), 1),
    "k5_first_six_years_share_not_in_school_fall_2026": round(100 * share_not_yet, 1),
    "note": ("K-5 taken as ages 5-10 at fall. Children in K-5 at any point in 2027-28..2032-33 were born "
             "2017-2027 (11 single-year cohorts). Born 2017-2021 are already enrolled in fall 2026; born "
             "2022-2027 are not. Per-year sizes use the 2024 county 5-year bands divided by 5; births after "
             "2024 assumed equal to the under-5 per-year size. County-wide, so includes Orange County Schools."),
}
SUMMARY["age_pipeline"] = pipeline

# Survey parent ages vs. county adult cohorts
age_order = ["13 to 17 years", "18 to 29 years", "30 to 39 years", "40 to 49 years", "50 to 64 years", "65+ years"]
ct = pd.crosstab(rw.age, rw.group).reindex(age_order).fillna(0).astype(int)
ct["All"] = ct.sum(axis=1)
age_tbl = ct.reset_index().rename(columns={"age": "age_band"})
for g in ["Parent", "Non-parent", "Excluded", "All"]:
    age_tbl[f"pct_{g}"] = (100 * age_tbl[g] / age_tbl[g].sum()).round(1)
# county adults 30-39 vs 40-49 (2024) as a crude benchmark for the parent-age split
a3039, a4049 = int(last.adults_30_39), int(last.adults_40_49)
age_tbl["county_2024_adults"] = age_tbl.age_band.map({"30 to 39 years": a3039, "40 to 49 years": a4049})
save(age_tbl, "age_distribution_by_group.csv")
p3039 = int(ct.loc["30 to 39 years", "Parent"]); p4049 = int(ct.loc["40 to 49 years", "Parent"])
SUMMARY["parent_age_vs_county"] = {
    "parents_30_39": p3039, "parents_40_49": p4049,
    "parents_30_39_share_of_30_49": round(100 * p3039 / (p3039 + p4049), 1),
    "county_adults_30_39": a3039, "county_adults_40_49": a4049,
    "county_30_39_share_of_30_49": round(100 * a3039 / (a3039 + a4049), 1),
    "future_parent_writeins": int(rw.future_parent.sum()),
    "future_parent_by_age": rw[rw.future_parent].age.value_counts().to_dict(),
    "future_parent_by_group": rw[rw.future_parent].group.value_counts().to_dict(),
}

# ======================================================================================
# 3. Language: what can and cannot be benchmarked
# ======================================================================================
lang = rw.source_sheet.value_counts().rename_axis("language_tab").reset_index(name="n")
lang["pct"] = (100 * lang.n / N).round(1)
lang["n_reported"] = lang.n.map(mask_small)
lang[["wilson_lo", "wilson_hi"]] = lang.n.apply(lambda k: pd.Series([round(100 * x, 1) for x in wilson(k, N)]))
save(lang[["language_tab", "n_reported", "pct", "wilson_lo", "wilson_hi"]], "language_tabs.csv")
non_en = int((rw.source_sheet != "English").sum())
lo_l, hi_l = wilson(non_en, N)

# Closure-study demographic text (three schools only; the district-wide table is an image in the PDF)
txt = Path(paths.CLOSURE_STUDY_TXT).read_text(errors="ignore")
school_demo = pd.DataFrame([
    {"school": "Ephesus", "white": 50.6, "asian": 14.3, "black": 15.3, "latinx": 13.0, "multiracial": 6.4, "eds": 34.5, "swd": 13.3, "multilingual": np.nan},
    {"school": "Glenwood", "white": 35.4, "asian": 38.0, "black": 8.6, "latinx": 4.6, "multiracial": 12.9, "eds": 17.5, "swd": 9.1, "multilingual": np.nan},
    {"school": "Seawell", "white": 34.9, "asian": 28.6, "black": 16.5, "latinx": 11.1, "multiracial": 8.9, "eds": 32.2, "swd": np.nan, "multilingual": 16.5},
])
# sanity: the numbers above must appear in the closure-study text
for v in ["50.6%", "38.0%", "16.5%", "34.5%", "17.5%", "32.2%"]:
    assert v in txt, v
school_demo["source"] = "Closure study 2026-05-07 p.16 (Oct 2025 20th-day data); ML only stated for Seawell"
save(school_demo, "closure_study_school_demographics.csv")

eds = pd.read_csv(paths.DPI_EDS)
eds_chccs = eds[eds.agency_code.isin(list(paths.ELEM_CODES) + [paths.CHCCS_LEA])].copy()
eds_chccs["name"] = eds_chccs.agency_code.map({**paths.ELEM_CODES, paths.CHCCS_LEA: "CHCCS district"})
eds_wide = eds_chccs.pivot(index="name", columns="year", values="pct_eds").reset_index()
save(eds_wide, "dpi_eds_chccs_elementary.csv")

SUMMARY["language"] = {
    "non_english_n": non_en, "non_english_pct": round(100 * non_en / N, 1),
    "non_english_wilson": [round(100 * lo_l, 1), round(100 * hi_l, 1)],
    "spanish_pct": round(100 * int((rw.source_sheet == "Spanish").sum()) / N, 1),
    "east_asian_tabs_pct": round(100 * int(rw.source_sheet.isin(["Chinese", "Japanese", "Korean"]).sum()) / N, 1),
    "benchmarks_available": {
        "district_multilingual_share": "not in local files (closure-study district table is an image)",
        "school_multilingual_share": "Seawell 16.5% only (closure study text)",
        "school_latinx_share": "Ephesus 13.0, Glenwood 4.6, Seawell 11.1 (closure study text)",
        "school_asian_share": "Ephesus 14.3, Glenwood 38.0, Seawell 28.6 (closure study text)",
        "district_eds_2024": float(eds[(eds.agency_code == paths.CHCCS_LEA) & (eds.year == 2024)].pct_eds.iloc[0]),
        "district_eds_2025": float(eds[(eds.agency_code == paths.CHCCS_LEA) & (eds.year == 2025)].pct_eds.iloc[0]),
        "survey_income_item": "none; the CPA asks no income, race/ethnicity, home-language or school-of-attendance question",
    },
}

# ======================================================================================
# 4. Staff share: is there a local employee count?
# ======================================================================================
staff_n = int(roles.any_chccs_staff.sum())
deck = Path(paths.BOARD_DECK_TXT).read_text(errors="ignore")
pat_emp = re.compile(r"\b[\d,]{3,6}\s+(employees|staff members|FTEs?|positions|teachers)\b", re.I)
emp_hits = {"board_deck": len(pat_emp.findall(deck)), "closure_study": len(pat_emp.findall(txt))}
salary_line = re.search(r"Salaries, Wages, and Employee Benefits: \$([\d.]+)M", deck)
staff_tbl = pd.DataFrame([{
    "chccs_staff_respondents_any_role": staff_n,
    "teacher": int(roles.teacher.sum()), "staff": int(roles.staff.sum()), "admin": int(roles.admin.sum()),
    "staff_who_are_also_current_parents": int(((roles.any_chccs_staff == 1) & (roles.parent_current == 1)).sum()),
    "staff_pct_of_respondents": pct(staff_n, N),
    "parent_respondents": int(roles.parent_current.sum()),
    "students_2024_25_adm": 11065,
    "parent_responses_per_100_students": round(100 * int(roles.parent_current.sum()) / 11065, 1),
    "employee_count_found_locally": False,
    "employee_count_regex_hits_board_deck": emp_hits["board_deck"],
    "employee_count_regex_hits_closure_study": emp_hits["closure_study"],
    "board_deck_salaries_benefits_total": salary_line.group(0) if salary_line else None,
}])
save(staff_tbl, "staff_share.csv")
SUMMARY["staff"] = staff_tbl.iloc[0].to_dict()

# ======================================================================================
# 5. Alternatives inventory vs. the survey
# ======================================================================================
so = pd.read_csv(paths.SCHOOL_OPTIONS)
so_k5 = so[so.servesK5 == True].copy()  # noqa: E712
so_k5 = so_k5.drop_duplicates(subset=["name"])
# Durham Academy appears as two campus rows with the same ~1,195 enrollment; keep one
so_k5 = so_k5[~so_k5.name.str.contains("Durham Academy Middle", case=False)]
inv_rows = []
for radius in (5, 10):
    sub = so_k5[so_k5.miles <= radius]
    for t in ("charter", "private"):
        s = sub[sub.type == t]
        inv_rows.append({"radius_miles": radius, "type": t, "n_schools": len(s),
                         "total_enrollment": int(s.students.sum()), "enrollment_year": "; ".join(sorted(s.studentsYear.dropna().unique())),
                         "vouchers_2024_sum": int(s.vouchers2024.fillna(0).sum()),
                         "n_with_voucher_data": int(s.vouchers2024.notna().sum())})
inv = pd.DataFrame(inv_rows)
save(inv, "alternatives_within_radius.csv")
save(so_k5[so_k5.miles <= 10][["name", "type", "grades", "students", "studentsYear", "county", "miles", "vouchers2024"]]
     .sort_values("miles"), "alternatives_within_10mi_list.csv")
n_dnpe_only_10 = int(((so.approx == False) & (so.miles <= 10)).sum())  # noqa: E712

npub = pd.read_csv(paths.NONPUBLIC)
orange_np = npub[npub.county == "Orange"][["year", "home_students_est", "private_students"]]
ch = pd.read_csv(paths.CHARTER_BY_COUNTY)
ch_o = ch[ch.county == "Orange"].drop(columns="county").T.reset_index()
ch_o.columns = ["year", "charter_adm"]
ch_o["year"] = ch_o.year.astype(int)
series = orange_np.merge(ch_o, on="year", how="outer").sort_values("year")
series = series[(series.year >= 2015) & (series.year <= 2026)]
series["non_chccs_total_est"] = series[["home_students_est", "private_students", "charter_adm"]].sum(axis=1, min_count=3)
v = pd.read_csv(paths.VOUCHERS)
v681 = v[v.agency_code == paths.CHCCS_LEA][["year", "new_recipients_prior_lea"]]
series = series.merge(v681, on="year", how="left").rename(columns={"new_recipients_prior_lea": "voucher_new_recipients_prior_chccs"})
series["note"] = "county-wide (includes Orange County Schools); home school is a DNPE estimate; charter ADM = DPI"
save(series, "orange_alternatives_2015_2026.csv")

# Free-text mentions of leaving / alternatives (counts only, never quotes)
PATTERNS = {
    "charter": r"\bcharter",
    "private": r"\bprivate\b",
    "homeschool": r"\bhome\s?-?school",
    "leave_the_district": r"leav\w*\s+(?:the\s+)?district",
    "pull_my_child": r"pull\w*\s+(?:my|our)\s+(?:kid|child)",
    "other_district": r"other\s+district|another\s+district|durham\s+public|wake\s+county|orange\s+county\s+schools",
    "voucher": r"\bvoucher",
    "opportunity_scholarship": r"opportunity\s+scholarship",
}
ANY = re.compile("|".join(f"(?:{p})" for p in PATTERNS.values()), re.I)
text_cols = ["other_challenges", "other_values", "additional_thoughts"]
texts = rw[["participant_id", "group", "source_sheet", "q9_theme"] + text_cols].copy()
texts["q9_write_in"] = np.where(q9.q9_theme == "Other", q9.q9_english, np.nan)
FIELDS = text_cols + ["q9_write_in"]
for fcol in FIELDS:
    texts[f"hit|{fcol}"] = texts[fcol].fillna("").str.contains(ANY)
texts["any_hit"] = texts[[f"hit|{f}" for f in FIELDS]].any(axis=1)
texts["any_text"] = texts[FIELDS].notna().any(axis=1)
for key, p in PATTERNS.items():
    rx = re.compile(p, re.I)
    texts[f"pat|{key}"] = texts[FIELDS].fillna("").apply(lambda r: any(rx.search(x) for x in r), axis=1)

pat_counts = pd.DataFrame([{"pattern": k, "respondents_matching": int(texts[f"pat|{k}"].sum()),
                            "reported": mask_small(int(texts[f"pat|{k}"].sum()))} for k in PATTERNS])
save(pat_counts, "alt_mentions_by_pattern.csv")

field_counts = pd.DataFrame([{"field": f, "respondents_with_text": int(texts[f].notna().sum()),
                              "respondents_matching": int(texts[f"hit|{f}"].sum())} for f in FIELDS])
save(field_counts, "alt_mentions_by_field.csv")

by_group = texts.groupby("group").agg(n=("participant_id", "size"), wrote_any_text=("any_text", "sum"),
                                      alt_mentions=("any_hit", "sum")).reset_index()
by_group["pct_of_group"] = (100 * by_group.alt_mentions / by_group.n).round(1)
by_group["pct_of_writers"] = (100 * by_group.alt_mentions / by_group.wrote_any_text).round(1)
by_group["alt_mentions_reported"] = by_group.alt_mentions.map(mask_small)
by_group[["wilson_lo_of_group", "wilson_hi_of_group"]] = by_group.apply(
    lambda r: pd.Series([round(100 * x, 1) for x in wilson(int(r.alt_mentions), int(r.n))]), axis=1)
save(by_group, "alt_mentions_by_group.csv")

by_theme = texts.groupby("q9_theme").agg(n=("participant_id", "size"), alt_mentions=("any_hit", "sum")).reset_index()
by_theme["pct"] = (100 * by_theme.alt_mentions / by_theme.n).round(1)
by_theme["alt_mentions_reported"] = by_theme.alt_mentions.map(mask_small)
save(by_theme, "alt_mentions_by_q9_theme.csv")

# which excl-non-CHCCS parents / non-English respondents mention alternatives
excl_ids = rw.participant_id[roles.parent_excl_non_chccs == 1]
any_non_ids = rw.participant_id[roles.parent_not_chccs == 1]
SUMMARY["alt_mentions"] = {
    "respondents_with_any_text": int(texts.any_text.sum()),
    "respondents_mentioning_alternatives": int(texts.any_hit.sum()),
    "pct_of_all": round(100 * texts.any_hit.sum() / N, 1),
    "pct_of_writers": round(100 * texts.any_hit.sum() / texts.any_text.sum(), 1),
    "among_parents_excl_non_chccs": mask_small(int(texts[texts.participant_id.isin(excl_ids)].any_hit.sum())),
    "among_parents_any_non_chccs": mask_small(int(texts[texts.participant_id.isin(any_non_ids)].any_hit.sum())),
    "among_non_english": mask_small(int(texts[texts.source_sheet != "English"].any_hit.sum())),
    "caveat": ("Non-English text fields in responses_wide are untranslated for several tabs, so keyword counts "
               "under-count non-English respondents. 'private' also matches 'private' in other senses."),
    "dnpe_only_rows_within_10mi_excluded": n_dnpe_only_10,
}

# Fisher exact: parents vs non-parents mentioning alternatives (exploratory; one test, no family)
a = int(texts[texts.group == "Parent"].any_hit.sum()); b = int((texts.group == "Parent").sum()) - a
c = int(texts[texts.group == "Non-parent"].any_hit.sum()); d = int((texts.group == "Non-parent").sum()) - c
odds, p_f = stats.fisher_exact([[a, b], [c, d]])
SUMMARY["alt_mentions"]["fisher_parent_vs_nonparent"] = {"table": [[a, b], [c, d]], "odds_ratio": round(odds, 2), "p": round(p_f, 3)}

# co-occurring write-in themes among alternative-mentioners (collapsed across fields)
theme_cols = [c for c in wic.columns if "|" in c]
themes = sorted({c.split("|", 1)[1] for c in theme_cols})
wic_any = pd.DataFrame({t: wic[[c for c in theme_cols if c.endswith("|" + t)]].any(axis=1) for t in themes})
wic_any["participant_id"] = wic.participant_id
m = texts[["participant_id", "any_hit", "any_text"]].merge(wic_any, on="participant_id")
co = []
for t in themes:
    k_hit = int(m.loc[m.any_hit, t].sum()); n_hit = int(m.any_hit.sum())
    k_oth = int(m.loc[m.any_text & ~m.any_hit, t].sum()); n_oth = int((m.any_text & ~m.any_hit).sum())
    co.append({"write_in_theme": t, "among_alt_mentioners_n": mask_small(k_hit), "among_alt_mentioners_pct": pct(k_hit, n_hit),
               "among_other_writers_n": k_oth, "among_other_writers_pct": pct(k_oth, n_oth),
               "ratio": round((k_hit / n_hit) / (k_oth / n_oth), 2) if k_oth and n_hit else np.nan})
co = pd.DataFrame(co).sort_values("among_alt_mentioners_pct", ascending=False)
save(co, "alt_mentions_cooccurring_themes.csv")

# ======================================================================================
# 6. Pooled vs. parent dominance in Q7/Q8 top-3
# ======================================================================================
CHALLENGES = {
    "Cost of maintaining aging buildings": r"cost of maintaining",
    "School buildings meeting safety codes": r"safety codes",
    "Length of commute for students riding buses": r"length of commute",
    "Retaining highly effective employees": r"retaining highly",
    "Partially empty school buildings": r"partially empty",
    "Overcrowded school buildings": r"overcrowded",
    "The number of trailers / mobile classrooms": r"trailers",
    "Buildings do not fit the modern academic program": r"modern academic",
    "Buildings do not fit modern operational expectations": r"modern operational",
    "Unequal access to specialty programs": r"unequal access",
    "Classroom technology updates": r"classroom technology",
    "Appeal of the district to current and prospective students": r"appeal of the district",
    "Boundaries not adjusted to shifted student populations": r"populations have shifted",
}
VALUES = {
    "Educational excellence": r"educational excellence",
    "Student-centered focus": r"student-centered|student centered",
    "Fiscal responsibility": r"fiscal responsibility",
    "Community engagement & trust building": r"community engagement",
    "Minimizing the distance students travel": r"minimiz\w* the distance",
    "Maximizing the use of currently available buildings": r"maximiz\w* the use",
    "School safety": r"school saf",
    "Long-term planning": r"long-term planning|long term planning",
    "Collaboration between schools and county leadership": r"collaboration between",
    "Community partnerships": r"community partnerships",
    "High-quality school meal service": r"meal service",
    "Increasing the use of renewable energy": r"renewable",
    "Ensuring well-balanced student populations": r"well-balanced|well balanced",
}
bvc = pd.read_csv(paths.BOARD_VS_CPA)


def top3_table(col: str, items: dict[str, str], section: str) -> pd.DataFrame:
    s = rw[col].fillna("")
    out = []
    groups = {"pooled": rw.index, "Parent": rw.index[rw.group == "Parent"],
              "Non-parent": rw.index[rw.group == "Non-parent"], "Excluded": rw.index[rw.group == "Excluded"]}
    for item, rx in items.items():
        hit = s.str.contains(rx, case=False, regex=True)
        row = {"section": section, "item": item}
        for g, idx in groups.items():
            row[f"pct_{g}"] = pct(int(hit[idx].sum()), len(idx))
            row[f"n_{g}"] = int(hit[idx].sum())
        row["pooled_minus_parent"] = round(row["pct_pooled"] - row["pct_Parent"], 1)
        row["pooled_minus_nonparent"] = round(row["pct_pooled"] - row["pct_Non-parent"], 1)
        row["parent_minus_nonparent"] = round(row["pct_Parent"] - row["pct_Non-parent"], 1)
        rep = bvc[(bvc.section == section) & (bvc.item == item)]
        row["district_reported_pct_top3"] = int(rep.cpa_pct_top3.iloc[0]) if len(rep) else np.nan
        row["board_pct_top3"] = int(rep.board_pct_top3.iloc[0]) if len(rep) else np.nan
        out.append(row)
    df = pd.DataFrame(out)
    # coverage check: how many selections did the regexes capture vs. tokens present
    n_sel = sum(df[f"n_pooled"])
    print(f"{section}: regexes captured {n_sel} selections across {N} respondents ({n_sel / N:.2f} per respondent)")
    return df


top3 = pd.concat([top3_table("top3_challenges", CHALLENGES, "challenge"), top3_table("top3_values", VALUES, "value")]).reset_index(drop=True)
save(top3, "pooled_vs_parent_top3.csv")
SUMMARY["pooled_vs_parent"] = {
    "mean_abs_pooled_minus_parent": round(float(top3.pooled_minus_parent.abs().mean()), 2),
    "max_abs_pooled_minus_parent": round(float(top3.pooled_minus_parent.abs().max()), 2),
    "mean_abs_pooled_minus_nonparent": round(float(top3.pooled_minus_nonparent.abs().mean()), 2),
    "max_abs_pooled_minus_nonparent": round(float(top3.pooled_minus_nonparent.abs().max()), 2),
    "mean_abs_pooled_minus_district_reported": round(float((top3.pct_pooled - top3.district_reported_pct_top3).abs().mean()), 2),
    "largest_parent_nonparent_gaps": top3.reindex(top3.parent_minus_nonparent.abs().sort_values(ascending=False).index)
        .head(6)[["section", "item", "pct_Parent", "pct_Non-parent", "parent_minus_nonparent"]].to_dict("records"),
}

# ======================================================================================
# extras: group x language, parent-age x group
# ======================================================================================
gl = pd.crosstab(rw.source_sheet, rw.group)
gl["All"] = gl.sum(axis=1)
save(gl.reset_index().rename(columns={"source_sheet": "language_tab"}).map(lambda x: mask_small(x) if isinstance(x, (int, np.integer)) else x),
     "language_by_group.csv")

with open(OUT / "summary.json", "w") as fh:
    json.dump(SUMMARY, fh, indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o))
print(f"wrote {OUT / 'summary.json'}")
print(json.dumps(SUMMARY, indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
