"""Workstream D: distance, walking and housing. What the survey says about getting to school
versus what the atlas (zone geometry, walk flags, ACS home values) and the May 2026 closure study
(SRTS walk counts, bus ridership, transport cost) show.

Run with the Module 2 interpreter after the spatial helper:

    ASTRA_PY=/Users/jim/dukeaipi/510_Sourcing_Data/Module_1_Project/ASTRA/school-map/.venv/bin/python
    $ASTRA_PY src/ws_d_spatial.py
    /Users/jim/dukeaipi/510_Sourcing_Data/Module_2_Project/AIPI_510_Module2_Project/.venv/bin/python src/ws_d_geography.py

Outputs go to results/ws_d/. Everything is descriptive or exploratory; n is tiny on the school side
(10 zones, 8 schools with SRTS counts) so correlations are Spearman and reported as such.
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.proportion import proportion_confint

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402

OUT = paths.RESULTS / "ws_d"
OUT.mkdir(parents=True, exist_ok=True)
SPATIAL = OUT / "zone_geography_spatial.json"
if not SPATIAL.exists():
    sys.exit("Run src/ws_d_spatial.py with the ASTRA interpreter first.")

V_DIST = "V: Minimizing the distance students travel between home and school"
C_BUS = "C: Length of commute for students riding buses"
C_BOUND = ("C: Student populations have shifted, but school boundaries have not been adjusted to "
           "accommodate those changes")
C_EMPTY = "C: Partially empty school buildings"
LOW_UTIL = ["Rashkis", "Northside", "Scroggs"]        # lowest 2031 projected utilization
CANDIDATES = ["Ephesus", "Glenwood", "Seawell"]


def wilson(k, n):
    if n == 0:
        return (np.nan, np.nan)
    lo, hi = proportion_confint(k, n, method="wilson")
    return round(100 * lo, 1), round(100 * hi, 1)


def pct_row(label, mask_num, mask_den):
    n = int(mask_den.sum())
    k = int((mask_num & mask_den).sum())
    lo, hi = wilson(k, n)
    return {"split": label, "n": n if n >= 10 else "<10", "k": k if n >= 10 else "<10",
            "pct": round(100 * k / n, 1) if n >= 10 else "<10", "wilson_lo": lo if n >= 10 else "",
            "wilson_hi": hi if n >= 10 else ""}


# ----------------------------------------------------------------------------------------------
# 1. Zone geography (from the spatial helper) + atlas metrics
# ----------------------------------------------------------------------------------------------
sp = json.loads(SPATIAL.read_text())
zones = pd.DataFrame(sp["zones"])
bgs = pd.DataFrame(sp["blockgroups"])
bgs.to_csv(OUT / "zone_blockgroups.csv", index=False)

metrics = pd.read_csv(paths.SCHOOL_METRICS)
metrics = metrics[metrics["school"].str.endswith("Elementary")].copy()
metrics["zone"] = metrics["school"].str.replace(" Elementary", "", regex=False)
fc = pd.read_csv(paths.CLOSURE_FORECAST)
fc["zone"] = fc["school"].str.replace(" Elementary", "", regex=False).replace({"FPG": "Frank Porter Graham"})
fc["growth_2026_2031"] = fc["2031"] - fc["2026"]
fc["growth_2026_2031_pct"] = (100 * fc["growth_2026_2031"] / fc["2026"]).round(1)
fc["growth_2026_2036_pct"] = (100 * (fc["2036"] - fc["2026"]) / fc["2026"]).round(1)

# ----------------------------------------------------------------------------------------------
# 2. Closure-study transportation facts (transcribed; every figure is asserted present in the text)
# ----------------------------------------------------------------------------------------------
txt = paths.CLOSURE_STUDY_TXT.read_text()
srts_block = txt.split("Counts by School (observations Nov. 12, 2024)")[1].split("--- PDF PAGE")[0]
srts_rows = []
for m in re.finditer(r"^(.+?) (ES|MS|HS) (\d+) (\d+) ([\d,]+) ([\d.]+)% ([\d.]+)%$", srts_block, re.M):
    srts_rows.append({"srts_school": f"{m.group(1)} {m.group(2)}", "level": m.group(2),
                      "walk": int(m.group(3)), "bike": int(m.group(4)),
                      "enrollment_at_count": int(m.group(5).replace(",", "")),
                      "walk_pct": float(m.group(6)), "bike_pct": float(m.group(7))})
srts = pd.DataFrame(srts_rows)
assert len(srts) == 14, srts
srts["zone"] = srts["srts_school"].str.replace(r" (ES|MS|HS)$", "", regex=True).replace(
    {"FPG Bilingüe": "Frank Porter Graham"})
srts["active"] = srts["walk"] + srts["bike"]
srts["active_pct"] = (100 * srts["active"] / srts["enrollment_at_count"]).round(1)
srts["source"] = "Closure study p.28/61/93, Town of Chapel Hill SRTS walk counts Nov 12 2024"
srts.to_csv(OUT / "srts_walk_counts.csv", index=False)

for needle in ["253 389 282", "140 170 147", "164 0 121", "125 2 120", "64 38 (4) 25", "14 7 23",
               "160 210 207", "30 minutes 38 minutes 28 minutes", "3 buses 7 buses 4 buses",
               "operated 55 buses, transported 3,880 students", "$3,013,692", "$936.53",
               "2.3 to 3.3 miles, resulting in an additional 9-12 minutes", "approximately $117,000",
               "3.0 to 5.0 miles, resulting in an additional 8–12 minutes", "approximately $112,383",
               "99 students live within 0.5 miles, 93 live", "6 students live within 0.5 miles, 22 live",
               "0 students live within 0.5 miles, 60 live", "up to 2 additional",
               "school may only have 2-4 walkers daily"]:
    assert needle in txt, needle

three = pd.DataFrame({
    "zone": CANDIDATES,
    "study_enrollment": [373, 391, 402],
    "bus_eligible": [253, 389, 282],
    "buses": [3, 7, 4],
    "am_riders": [140, 170, 147],
    "ntz_infinite_campus": [164, 0, 121],
    "ntz_tims": [125, 2, 120],
    "srts_walkers_observed": [64, 38, 25],
    "srts_walkers_adjusted": [64, 4, 25],        # Glenwood: Town says 2-4 real walkers; 34 came from a parking lot
    "srts_bikers": [14, 7, 23],
    "driven_by_parent": [160, 210, 207],
    "avg_bus_ride_min": [30, 38, 28],
    "study_bus_share_pct": [38, 43, 37],
    "study_active_share_pct": [19, 0.5, 12],     # study text: 19%, <1%, 12%
    "study_driven_share_pct": [43, 56, 51],
    "srts_within_0_5mi": [99, 6, 0],
    "srts_0_5_to_1mi": [93, 22, 60],
    "srts_1_to_1_5mi": [59, 10, 107],
    "closure_extra_miles": ["2.3-3.3", "not estimated (lottery magnet; program relocates)", "3.0-5.0"],
    "closure_extra_minutes": ["9-12", "not estimated", "8-12"],
    "closure_extra_cost_usd": [117000, np.nan, 112383],
    "closure_extra_cost_basis": ["125 NTZ students x $936.53", "n/a", "120 NTZ students x $936.53; up to 2 extra buses"],
    "receiving_schools": ["Estes Hills, Rashkis", "to be determined", "Estes Hills, Morris Grove, Northside"],
    "new_housing_students_forecast": [49, 12, 18],
    "source_pages": ["25-29", "58-62", "90-94"],
})
three["within_1_5mi"] = three[["srts_within_0_5mi", "srts_0_5_to_1mi", "srts_1_to_1_5mi"]].sum(axis=1)
three["eligible_who_ride_pct"] = (100 * three["am_riders"] / three["bus_eligible"]).round(0)
three.to_csv(OUT / "closure_candidates_transportation.csv", index=False)

district_bus = {"buses": 55, "riders": 3880, "miles": 728860, "cost_usd": 3013692,
                "cost_per_mile": 4.13, "cost_per_bus": 54794.40, "cost_per_pupil": 936.53,
                "source": "Closure study p.29 citing NCDPI Table 32, 2024-25"}

# per-school transportation table: SRTS for everyone with counts, three-school facts where present
trans = metrics[["zone", "adm", "sapfo_capacity", "adm_utilization_percent", "program_capacity_2026",
                 "projected_utilization_2030_31"]].merge(
    srts[srts["level"] == "ES"][["zone", "walk", "bike", "enrollment_at_count", "walk_pct", "bike_pct", "active", "active_pct"]],
    on="zone", how="left").merge(three.drop(columns=["study_enrollment"]), on="zone", how="left").merge(
    fc[["zone", "2026", "2031", "2036", "growth_2026_2031", "growth_2026_2031_pct", "growth_2026_2036_pct"]], on="zone", how="left")
trans["closure_candidate"] = trans["zone"].isin(CANDIDATES)
trans["lowest_util_2031"] = trans["zone"].isin(LOW_UTIL)
trans.to_csv(OUT / "transportation_by_school.csv", index=False)

# ----------------------------------------------------------------------------------------------
# 3. Zone table joined to metrics and forecast; Spearman on n = 10 zones / 8 SRTS schools
# ----------------------------------------------------------------------------------------------
zone_tbl = zones.merge(metrics[["zone", "adm", "adm_utilization_percent", "program_capacity_2026",
                                "projected_utilization_2030_31"]], on="zone", how="left").merge(
    fc[["zone", "2026", "2031", "growth_2026_2031", "growth_2026_2031_pct", "growth_2026_2036_pct"]], on="zone", how="left").merge(
    srts[srts["level"] == "ES"][["zone", "walk_pct", "bike_pct", "active_pct"]], on="zone", how="left")
zone_tbl["adm_per_sqmi"] = (zone_tbl["adm"] / zone_tbl["area_sqmi"]).round(0)
zone_tbl["closure_candidate"] = zone_tbl["zone"].isin(CANDIDATES)
# car-dependence: rank on low walk-area share and large area (mean of two ranks; higher = more car-dependent)
zone_tbl["car_dependence_rank"] = (zone_tbl["walk_area_share"].rank(ascending=True) +
                                   zone_tbl["area_sqmi"].rank(ascending=False)).rank(ascending=True).astype(int)
zone_tbl = zone_tbl.sort_values("zone")
zone_tbl.to_csv(OUT / "zone_geography.csv", index=False)

corr_rows = []
pairs = [
    ("bg_value_median", "growth_2026_2031_pct", "zones with values"),
    ("bg_value_median", "growth_2026_2036_pct", "zones with values"),
    ("bg_value_median", "projected_utilization_2030_31", "zones with values"),
    ("bg_value_median", "adm_utilization_percent", "zones with values"),
    ("bg_value_median", "walk_area_share", "zones with values"),
    ("bg_value_median", "walk_pct", "SRTS schools"),
    ("renter_share", "growth_2026_2031_pct", "zones with values"),
    ("renter_share", "projected_utilization_2030_31", "zones with values"),
    ("renter_share", "walk_pct", "SRTS schools"),
    ("walk_area_share", "walk_pct", "SRTS schools"),
    ("walk_segment_share", "walk_pct", "SRTS schools"),
    ("area_sqmi", "walk_pct", "SRTS schools"),
    ("adm_per_sqmi", "walk_pct", "SRTS schools"),
    ("area_sqmi", "projected_utilization_2030_31", "zones"),
    ("walk_area_share", "projected_utilization_2030_31", "zones"),
    ("walk_area_share", "growth_2026_2031_pct", "zones"),
]
for x, y, label in pairs:
    d = zone_tbl[[x, y]].dropna()
    if len(d) < 4:
        continue
    rho, p = stats.spearmanr(d[x], d[y])
    corr_rows.append({"x": x, "y": y, "n": len(d), "spearman_rho": round(rho, 2), "p": round(p, 3), "sample": label})
corr = pd.DataFrame(corr_rows)
corr["p_bh"] = multipletests(corr["p"], method="fdr_bh")[1].round(3)
corr.to_csv(OUT / "zone_spearman.csv", index=False)

# ----------------------------------------------------------------------------------------------
# 4. Survey side
# ----------------------------------------------------------------------------------------------
df = pd.read_csv(paths.RESPONSES_WIDE, keep_default_na=False, na_values=[""])
codes = pd.read_csv(paths.WRITE_IN_CODES)
df = df.merge(codes, on="participant_id", how="left")
code_cols = [c for c in codes.columns if c != "participant_id"]
df[code_cols] = df[code_cols].fillna(False).astype(bool)

df["dist_top3"] = df["top3_values"].fillna("").str.contains("the distance students travel", regex=False)
df["dist_q9"] = df["q9_value"] == "Minimizing the distance students travel between home and school"
df["dist_45"] = df[V_DIST] >= 4
df["dist_rated"] = df[V_DIST].notna()
df["bus_top3"] = df["top3_challenges"].fillna("").str.contains("Length of commute", regex=False)
df["bus_45"] = df[C_BUS] >= 4
df["bus_rated"] = df[C_BUS].notna()
df["any_text"] = (df["other_challenges"].notna() | df["other_values"].notna() | df["additional_thoughts"].notna()
                  | (df["q9_value"] == "Other (write-in)"))
walk_cols = [c for c in code_cols if c.endswith("Walking, biking & walk zones")]
bus_cols = [c for c in code_cols if c.endswith("Buses, commute & traffic")]
keep_cols = [c for c in code_cols if c.endswith("Keep current students in place / minimize disruption")]
nbhd_cols = [c for c in code_cols if c.endswith("Neighborhood & community schools")]
df["walk_theme"] = df[walk_cols].any(axis=1)
df["bus_theme"] = df[bus_cols].any(axis=1)
df["keep_theme"] = df[keep_cols].any(axis=1)
df["nbhd_theme"] = df[nbhd_cols].any(axis=1)
df["age_band"] = df["age"].map({"30 to 39 years": "30-39", "40 to 49 years": "40-49",
                                "50 to 64 years": "50+", "65+ years": "50+"})
parent = df["group"] == "Parent"
nonparent = df["group"] == "Non-parent"
splits = {
    "All respondents": df.index == df.index,
    "Parent": parent,
    "Non-parent": nonparent,
    "Parent 30-39": parent & (df["age_band"] == "30-39"),
    "Parent 40-49": parent & (df["age_band"] == "40-49"),
    "Parent 50+": parent & (df["age_band"] == "50+"),
    "English sheet": df["english"],
    "Other-language sheet": ~df["english"],
    "Parent, not CHCCS staff": parent & ~df["employee"],
    "Parent who is CHCCS staff": parent & df["employee"],
    "Non-parent CHCCS staff": nonparent & df["employee"],
    "Board (n=7, from BOARD_VS_CPA)": None,
}
board = pd.read_csv(paths.BOARD_VS_CPA)
b_dist = board[board["item"] == "Minimizing the distance students travel"].iloc[0]
b_bus = board[board["item"] == "Length of commute for students riding buses"].iloc[0]

rows = []
for label, mask in splits.items():
    if mask is None:
        rows.append({"split": label, "n": 7,
                     "dist_q5_pct_4_5": b_dist["board_pct_rated_4_5"], "dist_q8_top3_pct": b_dist["board_pct_top3"],
                     "dist_q9_pct": np.nan, "bus_q3_pct_4_5": b_bus["board_pct_rated_4_5"], "bus_q7_top3_pct": b_bus["board_pct_top3"]})
        continue
    n = int(mask.sum())
    r = {"split": label, "n": n}
    for name, num, den in [("dist_q5_pct_4_5", "dist_45", "dist_rated"), ("dist_q8_top3_pct", "dist_top3", None),
                           ("dist_q9_pct", "dist_q9", None), ("bus_q3_pct_4_5", "bus_45", "bus_rated"),
                           ("bus_q7_top3_pct", "bus_top3", None)]:
        d = mask & df[den] if den else mask
        k = int((df[num] & d).sum()); nn = int(d.sum())
        lo, hi = wilson(k, nn)
        if nn < 10:
            r[name], r[name + "_ci"] = "<10", ""
        else:
            r[name] = round(100 * k / nn, 1); r[name + "_ci"] = f"{lo}-{hi}"
    r["dist_q5_mean"] = round(df.loc[mask, V_DIST].mean(), 2) if n >= 10 else "<10"
    r["bus_q3_mean"] = round(df.loc[mask, C_BUS].mean(), 2) if n >= 10 else "<10"
    writers = mask & df["any_text"]
    nw = int(writers.sum())
    r["writers"] = nw if nw >= 10 else "<10"
    for theme in ["walk_theme", "bus_theme", "keep_theme", "nbhd_theme"]:
        k = int((writers & df[theme]).sum())
        lo, hi = wilson(k, nw)
        r[theme + "_pct_of_writers"] = round(100 * k / nw, 1) if nw >= 10 else "<10"
        r[theme + "_ci"] = f"{lo}-{hi}" if nw >= 10 else ""
    rows.append(r)
survey = pd.DataFrame(rows)
survey.to_csv(OUT / "survey_distance_by_split.csv", index=False)

# Q5 distance rating distribution by group (for a stacked bar)
dist_dist = (df[df["group"].isin(["Parent", "Non-parent"])].groupby("group")[V_DIST]
             .value_counts(normalize=True).unstack().mul(100).round(1))
dist_dist.to_csv(OUT / "q5_distance_rating_distribution.csv")

# Distance-prioritizers (Q9) vs everyone else on the 13 challenge ratings: Mann-Whitney, BH
analytic = df[df["group"].isin(["Parent", "Non-parent"])]
dp = analytic["dist_q9"]
challenge_cols = [c for c in df.columns if c.startswith("C: ")]
mw = []
for c in challenge_cols:
    a = analytic.loc[dp, c].dropna(); b = analytic.loc[~dp, c].dropna()
    u, p = stats.mannwhitneyu(a, b, alternative="two-sided")
    rb = 2 * u / (len(a) * len(b)) - 1         # rank-biserial, positive = prioritizers rate higher
    mw.append({"challenge": c[3:], "n_distance_prioritizers": len(a), "n_others": len(b),
               "mean_prioritizers": round(a.mean(), 2), "mean_others": round(b.mean(), 2),
               "pct45_prioritizers": round(100 * (a >= 4).mean(), 1), "pct45_others": round(100 * (b >= 4).mean(), 1),
               "U": u, "p": p, "rank_biserial": round(rb, 3)})
mw = pd.DataFrame(mw)
mw["p_bh"] = multipletests(mw["p"], method="fdr_bh")[1]
mw["p"] = mw["p"].round(4); mw["p_bh"] = mw["p_bh"].round(4)
mw = mw.sort_values("p")
mw.to_csv(OUT / "distance_prioritizers_vs_others_challenges.csv", index=False)

# Age x group for the Q5 distance 4-5 share and Q9 (for the narrative)
age_tbl = []
for g in ["Parent", "Non-parent"]:
    for band in ["30-39", "40-49", "50+"]:
        m = (df["group"] == g) & (df["age_band"] == band)
        age_tbl.append({"group": g, "age_band": band, **{k: v for k, v in pct_row("", df["dist_45"], m & df["dist_rated"]).items() if k != "split"}})
pd.DataFrame(age_tbl).to_csv(OUT / "distance_q5_by_group_age.csv", index=False)

# ----------------------------------------------------------------------------------------------
# 5. Putting it together: walkers at closure candidates vs lowest-utilization schools
# ----------------------------------------------------------------------------------------------
es = srts[srts["level"] == "ES"].set_index("zone")
cand = es.loc[CANDIDATES]
low = es.loc[LOW_UTIL]
glen_adj = 4  # Town's own estimate of real Glenwood walkers (2-4)
synth = {
    "closure_candidates": {
        "schools": CANDIDATES,
        "srts_walkers_observed": int(cand["walk"].sum()), "srts_bikers": int(cand["bike"].sum()),
        "srts_active_observed": int(cand["active"].sum()),
        "srts_active_adjusted_glenwood": int(cand["active"].sum() - 38 + glen_adj),
        "enrollment_at_count": int(cand["enrollment_at_count"].sum()),
        "active_pct_observed": round(100 * cand["active"].sum() / cand["enrollment_at_count"].sum(), 1),
        "active_pct_adjusted": round(100 * (cand["active"].sum() - 38 + glen_adj) / cand["enrollment_at_count"].sum(), 1),
        "ntz_tims": int(three["ntz_tims"].sum()),
        "ntz_cost_at_936_53": round(float(three["ntz_tims"].sum() * 936.53)),
        "study_stated_extra_cost": {"Ephesus": 117000, "Seawell": 112383, "Glenwood": None},
        "students_within_1_5mi": int(three["within_1_5mi"].sum()),
        "driven_by_parent": int(three["driven_by_parent"].sum()),
        "am_riders": int(three["am_riders"].sum()),
    },
    "lowest_utilization_2031": {
        "schools": LOW_UTIL,
        "srts_walkers_observed": int(low["walk"].sum()), "srts_bikers": int(low["bike"].sum()),
        "srts_active_observed": int(low["active"].sum()),
        "enrollment_at_count": int(low["enrollment_at_count"].sum()),
        "active_pct_observed": round(100 * low["active"].sum() / low["enrollment_at_count"].sum(), 1),
        "projected_utilization_2031": metrics.set_index("zone").loc[LOW_UTIL, "projected_utilization_2030_31"].to_dict(),
    },
    "all_8_srts_elementary": {
        "walkers": int(es["walk"].sum()), "bikers": int(es["bike"].sum()), "active": int(es["active"].sum()),
        "enrollment_at_count": int(es["enrollment_at_count"].sum()),
        "active_pct": round(100 * es["active"].sum() / es["enrollment_at_count"].sum(), 1),
        "walk_pct_range": [float(es["walk_pct"].min()), float(es["walk_pct"].max())],
        "missing_schools": ["Carrboro", "McDougle", "Morris Grove"],
    },
    "district_bus": district_bus,
    "survey": {
        "distance_top3_pct_all": float(survey.loc[survey["split"] == "All respondents", "dist_q8_top3_pct"].iloc[0]),
        "distance_q5_45_pct_all": float(survey.loc[survey["split"] == "All respondents", "dist_q5_pct_4_5"].iloc[0]),
        "bus_top3_pct_all": float(survey.loc[survey["split"] == "All respondents", "bus_q7_top3_pct"].iloc[0]),
        "bus_q3_45_pct_all": float(survey.loc[survey["split"] == "All respondents", "bus_q3_pct_4_5"].iloc[0]),
        "walk_theme_pct_of_writers": float(survey.loc[survey["split"] == "All respondents", "walk_theme_pct_of_writers"].iloc[0]),
        "bus_theme_pct_of_writers": float(survey.loc[survey["split"] == "All respondents", "bus_theme_pct_of_writers"].iloc[0]),
        "n_writers": int(survey.loc[survey["split"] == "All respondents", "writers"].iloc[0]),
        "board_distance_45": int(b_dist["board_pct_rated_4_5"]), "board_distance_top3": int(b_dist["board_pct_top3"]),
        "board_bus_45": int(b_bus["board_pct_rated_4_5"]), "board_bus_top3": int(b_bus["board_pct_top3"]),
    },
}
(OUT / "synthesis.json").write_text(json.dumps(synth, indent=1))

# ----------------------------------------------------------------------------------------------
# Supporting exploratory tests (Monte Carlo chi-square, 20,000 draws) and response-style check
# ----------------------------------------------------------------------------------------------
rng = np.random.default_rng(510)


def mc_chi2(tab, draws=20000):
    tab = np.asarray(tab)
    chi2, _, _, _ = stats.chi2_contingency(tab, correction=False)
    r, c = tab.sum(1), tab.sum(0)
    ge = 0
    for _ in range(draws):
        sim = stats.random_table(r, c, seed=rng).rvs()
        if stats.chi2_contingency(sim, correction=False)[0] >= chi2 - 1e-9:
            ge += 1
    n = tab.sum()
    v = np.sqrt(chi2 / (n * (min(tab.shape) - 1)))
    return chi2, (ge + 1) / (draws + 1), v


extra = []
pa = df[parent & df["age_band"].notna() & df["dist_rated"]]
tab = pd.crosstab(pa["age_band"], pa["dist_45"])
chi2, p, v = mc_chi2(tab.values)
extra.append({"test": "Parents: Q5 distance rated 4-5 x age band (30-39/40-49/50+)", "chi2": round(chi2, 2), "p_mc": round(p, 4), "cramers_v": round(v, 3), "n": len(pa)})
tab = pd.crosstab(pa["age_band"], pa["dist_top3"])
chi2, p, v = mc_chi2(tab.values)
extra.append({"test": "Parents: Q8 distance in top 3 x age band", "chi2": round(chi2, 2), "p_mc": round(p, 4), "cramers_v": round(v, 3), "n": len(pa)})
pn = df[df["group"].isin(["Parent", "Non-parent"])]
tab = pd.crosstab(pn["group"], pn["dist_top3"])
chi2, p, v = mc_chi2(tab.values)
extra.append({"test": "Parent vs non-parent: Q8 distance in top 3", "chi2": round(chi2, 2), "p_mc": round(p, 4), "cramers_v": round(v, 3), "n": len(pn)})
tab = pd.crosstab(pn["group"], pn["bus_top3"])
chi2, p, v = mc_chi2(tab.values)
extra.append({"test": "Parent vs non-parent: Q7 bus commute in top 3", "chi2": round(chi2, 2), "p_mc": round(p, 4), "cramers_v": round(v, 3), "n": len(pn)})
pp = df[parent]
tab = pd.crosstab(pp["employee"], pp["dist_top3"])
chi2, p, v = mc_chi2(tab.values)
extra.append({"test": "Parents: staff vs not, Q8 distance in top 3", "chi2": round(chi2, 2), "p_mc": round(p, 4), "cramers_v": round(v, 3), "n": len(pp)})
dr = df[df["dist_rated"]]
tab = pd.crosstab(dr["english"], dr["dist_45"])
chi2, p, v = mc_chi2(tab.values)
extra.append({"test": "English vs other-language sheet: Q5 distance rated 4-5", "chi2": round(chi2, 2), "p_mc": round(p, 4), "cramers_v": round(v, 3), "n": len(dr)})
extra = pd.DataFrame(extra)
extra["p_bh"] = multipletests(extra["p_mc"], method="fdr_bh")[1].round(4)
extra.to_csv(OUT / "survey_extra_tests.csv", index=False)

# response-style check: distance prioritizers' mean over all 13 challenge ratings vs others
style = {
    "n_distance_prioritizers": int(dp.sum()),
    "prioritizers_parent_share": round(100 * (analytic.loc[dp, "group"] == "Parent").mean(), 1),
    "mean_of_13_challenge_ratings_prioritizers": round(analytic.loc[dp, challenge_cols].mean(axis=1).mean(), 2),
    "mean_of_13_challenge_ratings_others": round(analytic.loc[~dp, challenge_cols].mean(axis=1).mean(), 2),
    "mean_excl_bus_prioritizers": round(analytic.loc[dp, [c for c in challenge_cols if c != C_BUS]].mean(axis=1).mean(), 2),
    "mean_excl_bus_others": round(analytic.loc[~dp, [c for c in challenge_cols if c != C_BUS]].mean(axis=1).mean(), 2),
    "either_distance_or_bus_top3_pct_all": round(100 * (df["dist_top3"] | df["bus_top3"]).mean(), 1),
    "both_distance_and_bus_top3_pct_all": round(100 * (df["dist_top3"] & df["bus_top3"]).mean(), 1),
    "walk_or_bus_theme_pct_of_writers": round(100 * (df.loc[df["any_text"], "walk_theme"] | df.loc[df["any_text"], "bus_theme"]).mean(), 1),
}
(OUT / "distance_prioritizers_style_check.json").write_text(json.dumps(style, indent=1))

# ----------------------------------------------------------------------------------------------
# console summary
# ----------------------------------------------------------------------------------------------
print("\n== extra tests ==")
print(extra.to_string(index=False))
print(json.dumps(style, indent=1))
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
print("\n== zones ==")
print(zone_tbl[["zone", "area_sqmi", "n_segments", "n_walk_segments", "walk_segment_share", "walk_area_share",
                "n_blockgroups_centroid", "n_blockgroups_touching", "bg_value_min", "bg_value_median", "bg_value_max",
                "renter_share", "adm_per_sqmi", "projected_utilization_2030_31", "growth_2026_2031_pct", "walk_pct",
                "car_dependence_rank"]].to_string(index=False))
print("\n== spearman ==")
print(corr.to_string(index=False))
print("\n== survey splits ==")
print(survey.to_string(index=False))
print("\n== Q5 distance distribution ==")
print(dist_dist)
print("\n== distance prioritizers vs others (challenges) ==")
print(mw[["challenge", "mean_prioritizers", "mean_others", "pct45_prioritizers", "pct45_others", "rank_biserial", "p", "p_bh"]].to_string(index=False))
print("\n== synthesis ==")
print(json.dumps(synth, indent=1))
print("\n== age x group ==")
print(pd.DataFrame(age_tbl).to_string(index=False))
