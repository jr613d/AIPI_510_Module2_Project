"""Assemble data/processed/story_data.json for the HTML story from the workstream results.
Every number in the page traces to a results/ws_*/ file or a Module 1 cleaned table."""
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths as P  # noqa: E402

R = P.RESULTS
out = {}

# --- Module 1 recap: four nested layers 2019-2024 ----------------------------------------
layers = pd.read_csv(P.CHCCS_LAYERS)
base = layers.iloc[0]
out["layers"] = {
    "years": layers.year.tolist(),
    "series": [
        {"key": "pop_total", "label": "Total population", "values": layers.pop_total.tolist()},
        {"key": "pop_5_17", "label": "Ages 5-17", "values": layers.pop_5_17.tolist()},
        {"key": "total_adm", "label": "K-12 enrollment (ADM)", "values": layers.total_adm.tolist()},
        {"key": "elem_adm", "label": "Elementary enrollment", "values": layers.elem_adm.tolist()},
    ],
    "capture": layers.capture_rate.round(4).tolist(),
}
for s in out["layers"]["series"]:
    s["index"] = [round(v / s["values"][0] * 100, 1) for v in s["values"]]
    s["pct_change"] = round((s["values"][-1] / s["values"][0] - 1) * 100, 1)

# --- WS-C: levers ----------------------------------------------------------------------------
lev = pd.read_csv(R / "ws_c" / "headline_lever_x_stakeholder_top3_share.csv")
mapping = pd.read_csv(R / "ws_c" / "lever_mapping.csv")
items_by_lever = mapping[mapping.lever != "DEMAND-DEMOGRAPHIC"].groupby("lever").board_label.apply(list).to_dict()
out["levers"] = {
    "order": ["DEMAND-DEMOGRAPHIC", "DEMAND-CAPTURE", "SUPPLY-FACILITIES/COST", "LOGISTICS/COMMUNITY"],
    "labels": {"DEMAND-DEMOGRAPHIC": "Fewer children living here", "DEMAND-CAPTURE": "Whether families choose CHCCS",
               "SUPPLY-FACILITIES/COST": "Buildings, boundaries and money", "LOGISTICS/COMMUNITY": "Getting to school, community"},
    "n_items": {k: len(v) for k, v in items_by_lever.items()} | {"DEMAND-DEMOGRAPHIC": 0},
    "items": items_by_lever,
    "top3_share": {col: dict(zip(lev.lever, lev[col])) for col in ["Other parents", "Non-parent", "Board (n=7)"]},
}
dec = pd.read_csv(R / "ws_c" / "decomposition_dollars.csv")
out["decomposition"] = {r.component: {"students": int(r.students), "share_pct": r.share_pct,
                                      "state_per_year_fy2027": int(r["state_$_per_year_FY2027_rate"])}
                        for _, r in dec.iterrows() if "Module 1" in r.component or r.component.startswith("Total")}

# --- WS-C: forecasts and scenarios ---------------------------------------------------------
fc = pd.read_csv(R / "ws_c" / "elementary_adm_actual_and_forecasts.csv")
def ser(col):
    return [[int(y), (None if pd.isna(v) else round(float(v)))] for y, v in zip(fc.year, fc[col])]
out["forecasts"] = {
    "actual": ser("actual_elementary_adm"),
    "closure_study": ser("closure_study_forecast"),
    "deck_scaled": ser("board_deck_k12_scaled_by_2025_elem_share"),
    "scenario_A": ser("scenario_A_demographics_only_scaled"),
    "scenario_B": ser("scenario_B_capture_falls_scaled"),
    "trend_linear": ser("trend_linear_2019_25"),
}
sc = pd.read_csv(R / "ws_c" / "scenario_table_2025_2031.csv")
sc = sc[sc.saipe_window == "SAIPE 2019-24 OLS"]
out["scenarios"] = [
    {"name": r.scenario, "adm_2031": int(r.adm_2031), "pct_change": r.pct_change_2025_31,
     "elementary_2031": int(r.elementary_2031_scaled), "state_reduction_m": round(r.state_reduction_FY2027_31 / 1e6, 1)}
    for _, r in sc.iterrows() if not r.scenario.startswith("C")
] + [{"name": "Board deck (cohort-based, -2.4%/yr)", "adm_2031": 9535, "pct_change": -13.8, "elementary_2031": 3897, "state_reduction_m": 38.3}]
gap = pd.read_csv(R / "ws_c" / "forecast_gap_2031.csv")
out["forecast_gap_2031"] = gap.to_dict(orient="records")

# --- WS-A: representation ------------------------------------------------------------------
summ = json.loads((R / "ws_a" / "summary.json").read_text())
rep = pd.read_csv(R / "ws_a" / "representation_vs_population.csv")
out["representation"] = {
    "pct_children_not_enrolled_2024": summ["representation"]["pct_children_not_enrolled_2024"],
    "pct_children_not_enrolled_2019": summ["representation"]["pct_children_not_enrolled_2019"],
    "survey_pct_excl": summ["representation"]["parents_excl_non_chccs_pct_of_school_age_parents"],
    "survey_pct_any": summ["representation"]["parents_any_non_chccs_pct"],
    "factor_excl": summ["representation"]["underrep_factor_excl_2024"],
    "factor_any": summ["representation"]["underrep_factor_any_2024"],
    "n_excl": summ["representation"]["parents_excl_non_chccs"],
    "n_any": summ["representation"]["parents_any_non_chccs"],
    "by_year": rep[["year", "total_adm", "pop_5_17", "not_enrolled", "pct_not_enrolled"]].to_dict(orient="records"),
}
ap = summ["age_pipeline"]
# Cohort ladder: births 2017-2027; per-year sizes per the WS-A note
per5_9, per_u5 = ap["per_year_cohort_5_9_2024"], ap["per_year_cohort_under5_2024"]
ladder = []
for by in range(2017, 2028):
    size = per5_9 if by <= 2019 else per_u5
    ladder.append({"birth_year": by, "size": size, "in_school_fall_2026": by <= 2021,
                   "k5_years": f"{by+5}-{by+11}"})
out["cohort_ladder"] = {"rows": ladder, "share_not_yet": ap["k5_first_six_years_share_not_in_school_fall_2026"],
                        "share_not_yet_first_year": ap["k5_2027_28_share_not_in_school_fall_2026"]}
roles = pd.read_csv(R / "ws_a" / "respondent_roles.csv")
out["roles"] = roles[["role", "n_reported", "pct_of_respondents"]].to_dict(orient="records")
age = pd.read_csv(R / "ws_a" / "age_distribution_by_group.csv")
out["parent_age"] = age[["age_band", "Parent", "pct_Parent"]].to_dict(orient="records")
coh = pd.read_csv(R / "ws_a" / "orange_age_cohorts_2010_2024.csv")
out["orange_cohorts"] = coh[["year", "under5", "age5_9", "age10_14", "pop_total"]].to_dict(orient="records")

pv = pd.read_csv(R / "ws_a" / "pooled_vs_parent_top3.csv")
keep_items = ["Boundaries not adjusted to shifted student populations", "Cost of maintaining aging buildings",
              "Ensuring well-balanced student populations", "Maximizing the use of currently available buildings",
              "Partially empty school buildings", "Fiscal responsibility", "Long-term planning",
              "Overcrowded school buildings", "Appeal of the district to current and prospective students",
              "Retaining highly effective employees", "Minimizing the distance students travel",
              "Length of commute for students riding buses", "School safety", "Educational excellence"]
short = {"Boundaries not adjusted to shifted student populations": "Boundaries not adjusted to population shifts",
         "Appeal of the district to current and prospective students": "Appeal of the district",
         "Maximizing the use of currently available buildings": "Maximizing use of current buildings",
         "Ensuring well-balanced student populations": "Well-balanced student populations",
         "Length of commute for students riding buses": "Length of bus commute",
         "Minimizing the distance students travel": "Minimizing distance to school"}
pv = pv[pv.item.isin(keep_items)].copy()
pv["short"] = pv.item.map(lambda s: short.get(s, s))
pv["gap"] = pv["pct_Non-parent"] - pv["pct_Parent"]
pv = pv.sort_values("gap", ascending=False)
out["top3_dumbbell"] = [{"item": r.short, "section": r.section, "parent": r.pct_Parent, "nonparent": r["pct_Non-parent"],
                         "pooled": r.pct_pooled, "board": r.board_pct_top3} for _, r in pv.iterrows()]
out["pooled_gap_summary"] = {"mean_abs_pooled_minus_parent": round(pv_all := pd.read_csv(R / "ws_a" / "pooled_vs_parent_top3.csv").pooled_minus_parent.abs().mean(), 1),
                             "max_abs_pooled_minus_parent": round(pd.read_csv(R / "ws_a" / "pooled_vs_parent_top3.csv").pooled_minus_parent.abs().max(), 1),
                             "mean_abs_pooled_minus_nonparent": round(pd.read_csv(R / "ws_a" / "pooled_vs_parent_top3.csv").pooled_minus_nonparent.abs().mean(), 1),
                             "max_abs_pooled_minus_nonparent": round(pd.read_csv(R / "ws_a" / "pooled_vs_parent_top3.csv").pooled_minus_nonparent.abs().max(), 1)}

# --- WS-C: fiscal by age; Q8 check -------------------------------------------------------
prof = pd.read_csv(R / "ws_c" / "item_profiles_by_subgroup.csv")
fis = prof[prof.target.str.startswith("Fiscal responsibility") & (prof.breakdown == "age_band") & prof.level.isin(["30 to 39 years", "40 to 49 years", "50 to 64 years"])]
out["fiscal_by_age"] = [{"measure": "rated 4-5" if "4-5" in r.target else "top-3", "age": r.level, "pct": r.pct, "lo": r.ci_lo, "hi": r.ci_hi, "n": int(r.n)} for _, r in fis.iterrows()]
q8 = pd.read_csv(R / "ws_c" / "q8_theme_by_group.csv")
out["q8_check"] = [{"theme": r.theme, "group": r.group, "measure": "Q8 any in top 3" if r.measure.startswith("any") else "Q9 single choice", "pct": r.pct, "lo": r.ci_lo, "hi": r.ci_hi}
                   for _, r in q8.iterrows() if not r.measure.startswith("mean")]

# --- WS-B: schools, utilization spread --------------------------------------------------
st = pd.read_csv(R / "ws_b" / "school_table.csv")
cols = ["school", "closure_candidate", "dli_program", "year_built", "adm_2024_25", "sapfo_capacity_2025", "util_2024_25_pct",
        "program_capacity_2026", "forecast_2026", "forecast_2031", "forecast_2036", "util_2026_forecast_on_program_cap_pct",
        "util_2031_projected_pct", "util_2036_forecast_on_program_cap_pct", "adm_2019", "adm_change_2019_2025_pct",
        "eds_pct_2024_25", "srts_walkers", "srts_bikers", "srts_walk_pct", "srts_walk_pct_adjusted", "mentions_total", "mentions_per_100_adm"]
out["schools"] = json.loads(st[cols].to_json(orient="records"))
spread = pd.read_csv(R / "ws_b" / "utilization_spread.csv")
out["utilization_spread"] = spread.to_dict(orient="records")

# --- WS-E: balance ----------------------------------------------------------------------
es = pd.read_csv(R / "ws_e" / "empty_seats_on_gradient.csv")
out["eds_scatter"] = es[["school", "pct_eds_2025", "util_projected_2031", "projected_empty_seats_2031", "adm_2024_25", "share_of_2031_empty_seats"]].to_dict(orient="records")
long = pd.read_csv(R / "ws_e" / "school_balance_long_2017_2025.csv")
sch = long[~long.school.str.startswith("CHCCS")]
band = sch.groupby("year").pct_eds.agg(["min", "max"]).reset_index()
out["eds_band"] = {"years": band.year.tolist(), "min": band["min"].tolist(), "max": band["max"].tolist(),
                   "district": long[long.school.str.startswith("CHCCS")].set_index("year").pct_eds.reindex(band.year).tolist(),
                   "schools": {s: g.set_index("year").pct_eds.reindex(band.year).tolist() for s, g in sch.groupby("school")}}
wb = pd.read_csv(R / "ws_e" / "wellbalanced_gap_excluding_heavy_5_raters.csv")
wb = wb[(wb["sample"] == "All respondents") & wb.group.isin(["Other parents (not staff)", "Parents who are staff", "Non-parent (mostly staff)"])]
out["wellbalanced"] = [{"group": r.group, "rated_4_5": round(r.wb_rated_4_5_pct, 1), "lo": round(r.wilson_lo, 1), "hi": round(r.wilson_hi, 1),
                        "rated_5": round(r.wb_rated_5_pct, 1), "top3": round(r.q8_top3_pct, 1), "n": int(r.n)} for _, r in wb.iterrows()]
wbx = wb_excl = pd.read_csv(R / "ws_e" / "wellbalanced_gap_excluding_heavy_5_raters.csv")
wbx = wbx[wbx["sample"].str.startswith("Excluding 10+")]
out["wellbalanced_excl_heavy"] = {r.group: round(r.wb_rated_4_5_pct, 1) for _, r in wbx.iterrows()}
co = pd.read_csv(R / "ws_e" / "q7_x_q8_wellbalanced_coselection.csv")
co = co[co["sample"] == "All respondents"].sort_values("odds_ratio", ascending=False)
out["wellbalanced_or"] = [{"item": r.q7_challenge, "or": round(r.odds_ratio, 2), "pct_given": round(r.pct_item_given_wb, 1),
                           "pct_not": round(r.pct_item_given_not_wb, 1), "q": r.p_bh} for _, r in co.iterrows()]
eq = pd.read_csv(R / "ws_e" / "equity_writers_vs_wellbalanced.csv").iloc[0]
out["equity_or"] = {"or": round(eq.odds_ratio, 2), "pct_given": round(eq.pct_y_given_x, 1), "pct_not": round(eq.pct_y_given_not_x, 1), "q": eq.p_bh}
four = pd.read_csv(R / "ws_e" / "board_parents_staff_four_items.csv")
out["four_items"] = four.to_dict(orient="records")

# --- WS-D: walking and transportation --------------------------------------------------
zg = pd.read_csv(R / "ws_d" / "zone_geography.csv")
out["zones"] = zg[["zone", "area_sqmi", "n_segments", "n_walk_segments", "walk_area_share", "renter_share", "bg_value_median"]].to_dict(orient="records")
srts = pd.read_csv(R / "ws_d" / "srts_walk_counts.csv")
srts = srts[srts.level == "ES"]
out["srts"] = srts[["zone", "walk", "bike", "enrollment_at_count", "walk_pct", "bike_pct"]].to_dict(orient="records")
syn = json.loads((R / "ws_d" / "synthesis.json").read_text())
out["walk_synthesis"] = syn
tr = pd.read_csv(R / "ws_d" / "closure_candidates_transportation.csv")
out["transport"] = json.loads(tr.to_json(orient="records"))
dist = pd.read_csv(R / "ws_d" / "survey_distance_by_split.csv")
out["distance_splits"] = json.loads(dist.to_json(orient="records"))
dp = pd.read_csv(R / "ws_d" / "distance_prioritizers_vs_others_challenges.csv")
out["distance_prioritizers"] = json.loads(dp.to_json(orient="records"))

# --- WS-B: Glenwood themes; WS-A: exit talk -----------------------------------------------
th = pd.read_csv(R / "ws_b" / "theme_cooccurrence_by_school.csv")
g = th[th.school == "Glenwood"].sort_values("pct_mentioners", ascending=False)
out["glenwood_themes"] = [{"theme": r.theme, "mentioners_pct": r.pct_mentioners, "lo": r.wilson_lo, "hi": r.wilson_hi,
                           "others_pct": r.pct_other_writers, "q": r.bh_q, "k": int(r.mentioners_with_theme), "n": int(r.mentioners)} for _, r in g.iterrows()]
alt = pd.read_csv(R / "ws_a" / "alt_mentions_cooccurring_themes.csv")
out["exit_talk"] = {"n_mentioners": 41, "pct_of_all": 2.8, "pct_of_writers": 6.5,
                    "themes": [{"theme": r.write_in_theme, "mentioners_pct": r.among_alt_mentioners_pct, "others_pct": r.among_other_writers_pct, "ratio": r.ratio}
                               for _, r in alt.iterrows()]}
altpat = pd.read_csv(R / "ws_a" / "alt_mentions_by_pattern.csv")
out["exit_patterns"] = altpat.to_dict(orient="records")
oa = pd.read_csv(R / "ws_a" / "orange_alternatives_2015_2026.csv")
out["orange_alternatives"] = json.loads(oa[["year", "home_students_est", "private_students", "charter_adm", "non_chccs_total_est"]].to_json(orient="records"))

P.PROCESSED.mkdir(parents=True, exist_ok=True)
def _clean(o):
    """Replace NaN floats with None so the page's JSON.parse succeeds."""
    if isinstance(o, dict):
        return {k: _clean(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_clean(v) for v in o]
    if isinstance(o, float) and o != o:
        return None
    return o

out = _clean(out)
(P.PROCESSED / "story_data.json").write_text(json.dumps(out, indent=1, allow_nan=False))
print("wrote", P.PROCESSED / "story_data.json", len(json.dumps(out)), "bytes")
