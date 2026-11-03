"""Workstream C: do the survey's priorities line up with what is driving the decline, and with the money?

Five tasks, all exploratory/descriptive:
  1. Map each of the 26 survey items to a Module 1 "lever" and score each stakeholder's attention per lever.
  2. Q8 (top-3 values) by Q9 theme, as a check on the pre-registered Q9 result.
  3. Dollar-ize the 714 / 355 decomposition with the board deck's own per-pupil figures; scenario table to 2031.
  4. Who picks "Appeal of the district", "Retaining highly effective employees", "Fiscal responsibility".
  5. One table of elementary ADM: actuals, closure-study forecast, scaled board-deck projection, naive trend.

Inputs are read-only (see paths.py). Outputs go to results/ws_c/.
Run with the Module 2 venv python (pandas, numpy, scipy).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import fisher_exact, chi2_contingency
from statsmodels.stats.multitest import multipletests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths as P  # noqa: E402

OUT = P.RESULTS / "ws_c"
OUT.mkdir(parents=True, exist_ok=True)
SEED = 510
N_PERM = 20_000

# --------------------------------------------------------------------------- helpers
def wilson(k, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    d = 1 + z**2 / n
    c = (p + z**2 / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / d
    return (100 * (c - h), 100 * (c + h))


def monte_carlo_chi2(labels, outcome, n_perm=N_PERM, seed=SEED):
    """Permutation p-value for independence of two categorical arrays (same approach as Module 2)."""
    rng = np.random.default_rng(seed)
    labels = pd.Categorical(labels)
    outcome = pd.Categorical(outcome)
    lc, oc = labels.codes.copy(), outcome.codes
    k_l, k_o = len(labels.categories), len(outcome.categories)

    def stat(codes):
        t = np.bincount(codes * k_o + oc, minlength=k_l * k_o).reshape(k_l, k_o)
        e = t.sum(1, keepdims=True) * t.sum(0, keepdims=True) / t.sum()
        with np.errstate(divide="ignore", invalid="ignore"):
            return np.nansum((t - e) ** 2 / e)

    observed = stat(lc)
    hits = sum(stat(rng.permutation(lc)) >= observed - 1e-12 for _ in range(n_perm))
    return observed, (hits + 1) / (n_perm + 1)


def cramers_v(table):
    t = np.asarray(table)
    chi2 = chi2_contingency(t, correction=False)[0]
    return float(np.sqrt(chi2 / (t.sum() * (min(t.shape) - 1))))


def pct_row(k, n):
    lo, hi = wilson(k, n)
    return dict(n=int(n), k=int(k), pct=round(100 * k / n, 1) if n else np.nan,
                ci_lo=round(lo, 1), ci_hi=round(hi, 1))


# --------------------------------------------------------------------------- item catalogue
# key, question, rating-column label (as in RESPONSES_WIDE minus the "C: "/"V: " prefix),
# top-3 label variants (longest first), board label (BOARD_VS_CPA), lever, Q9 theme (values only)
CAP, SUP, LOG, DEM = "DEMAND-CAPTURE", "SUPPLY-FACILITIES/COST", "LOGISTICS/COMMUNITY", "DEMAND-DEMOGRAPHIC"
ITEMS = [
    # challenges (Q3 ratings, Q7 top 3)
    ("aging_cost", "C", "Cost of maintaining aging buildings", ["Cost of maintaining aging buildings"],
     "Cost of maintaining aging buildings", SUP, None),
    ("safety_codes", "C", "School buildings meeting safety codes", ["School buildings meeting safety codes"],
     "School buildings meeting safety codes", SUP, None),
    ("bus_commute", "C", "Length of commute for students riding buses", ["Length of commute for students riding buses"],
     "Length of commute for students riding buses", LOG, None),
    ("retain_staff", "C", "Retaining highly effective employees", ["Retaining highly effective employees"],
     "Retaining highly effective employees", CAP, None),
    ("empty", "C", "Partially empty school buildings", ["Partially empty school buildings"],
     "Partially empty school buildings", SUP, None),
    ("overcrowded", "C", "Overcrowded school buildings", ["Overcrowded school buildings"],
     "Overcrowded school buildings", SUP, None),
    ("trailers", "C", "The number of trailers / mobile classrooms", ["The number of trailers / mobile classrooms"],
     "The number of trailers / mobile classrooms", SUP, None),
    ("fit_academic", "C", "Current school buildings do not fit the modern academic program (e.g. classroom layout and size, classroom flexibility, ADA compliance, etc.)",
     ["Current school buildings do not fit the modern academic program"],
     "Buildings do not fit the modern academic program", SUP, None),
    ("fit_operational", "C", "Current school buildings do not fit the modern operational expectations (e.g. right sized car rider lines, sports facilities, suitable sidewalks, meal service program, air quality, etc.)",
     ["Current school buildings do not fit the modern operational expectations"],
     "Buildings do not fit modern operational expectations", SUP, None),
    ("specialty_access", "C", "Unequal access to specialty programs", ["Unequal access to specialty programs"],
     "Unequal access to specialty programs", CAP, None),
    ("technology", "C", "Classroom technology updates", ["Classroom technology updates"],
     "Classroom technology updates", CAP, None),
    ("appeal", "C", "Appeal of the district to current and prospective students",
     ["Appeal of the district to current and prospective students"],
     "Appeal of the district to current and prospective students", CAP, None),
    ("boundaries", "C", "Student populations have shifted, but school boundaries have not been adjusted to accommodate those changes",
     ["Student populations have shifted, but school boundaries have not been adjusted to accommodate those shifts",
      "Student populations have shifted, but school boundaries have not been adjusted to accommodate those changes"],
     "Boundaries not adjusted to shifted student populations", SUP, None),
    # values (Q5 ratings, Q8 top 3, Q9 single)
    ("excellence", "V", "Educational excellence (quality & student outcomes)",
     ["Educational excellence (quality & student outcomes)"], "Educational excellence", CAP, "Student Learning"),
    ("student_centered", "V", "Student-centered focus", ["Student-centered focus"], "Student-centered focus", CAP, "Student Learning"),
    ("fiscal", "V", "Fiscal responsibility", ["Fiscal responsibility"], "Fiscal responsibility", SUP, "Money & buildings"),
    ("engagement", "V", "Community engagement & trust building",
     ["Community engagement & trust building", "Community engagement"], "Community engagement & trust building", LOG, "Community"),
    ("distance", "V", "Minimizing the distance students travel between home and school",
     ["Minimizing the distance students travel between home and school",
      "Minimize the distance students travel between home and school",
      "Minimize the distance student travel between home and school"],
     "Minimizing the distance students travel", LOG, "Student logistics & well-being"),
    ("max_buildings", "V", "Maximizing the use of currently available buildings",
     ["Maximizing the use of currently available buildings", "Maximize the use of currently available buildings"],
     "Maximizing the use of currently available buildings", SUP, "Money & buildings"),
    ("safety", "V", "School safety", ["School safety", "School saftey"], "School safety", CAP, "Student logistics & well-being"),
    ("long_term", "V", "Long-term planning", ["Long-term planning"], "Long-term planning", SUP, "Money & buildings"),
    ("county_collab", "V", "Collaboration between schools and county leadership",
     ["Collaboration between schools and county leadership"], "Collaboration between schools and county leadership", LOG, "Community"),
    ("partnerships", "V", "Community partnerships", ["Community partnerships"], "Community partnerships", LOG, "Community"),
    ("meals", "V", "High quality school meal service", ["High quality school meal service"],
     "High-quality school meal service", CAP, "Student logistics & well-being"),
    ("renewable", "V", "Increasing the use of renewable energy districtwide",
     ["Increasing the use of renewable energy districtwide"], "Increasing the use of renewable energy", SUP, "Money & buildings"),
    ("balanced", "V", "Ensuring well-balanced student populations across all school sites",
     ["Ensuring well-balanced student populations across all school sites"],
     "Ensuring well-balanced student populations", SUP, "Student logistics & well-being"),
]
CAT = pd.DataFrame(ITEMS, columns=["key", "question", "rating_label", "top3_variants", "board_label", "lever", "q9_theme"])
LEVERS = [DEM, CAP, SUP, LOG]
LEVER_WHY = {
    DEM: "Fewer children living in the district (birth rates, housing cost, age structure). No board can change it.",
    CAP: "Whether resident families choose CHCCS over charter/private/home school. Module 1's 355-student capture-rate loss.",
    SUP: "Buildings, boundaries and money: the supply side the closure/redistricting process is about.",
    LOG: "Getting to school and the district's relationships with the community and county.",
}
MAP_WHY = {
    "aging_cost": "Cost of the building stock", "safety_codes": "Building condition", "bus_commute": "Getting to school",
    "retain_staff": "Teacher quality is the most-cited reason families choose or leave a district",
    "empty": "Under-used buildings", "overcrowded": "Over-used buildings", "trailers": "Capacity shortfall",
    "fit_academic": "Building fitness", "fit_operational": "Building fitness",
    "specialty_access": "Program access shapes whether families stay (magnets, DLI, EC)",
    "technology": "Classroom offer", "appeal": "The survey's own capture-rate item",
    "boundaries": "Matching boundaries to where children live is a supply-side fix",
    "excellence": "Core of the district's offer", "student_centered": "Core of the district's offer",
    "fiscal": "Money", "engagement": "Relationship with the community", "distance": "Getting to school",
    "max_buildings": "Buildings", "safety": "A reason families choose a school", "long_term": "Planning the supply side",
    "county_collab": "County relationship (also the funder, but framed as collaboration)", "partnerships": "Community relationship",
    "meals": "Part of the daily offer to families", "renewable": "Facilities policy",
    "balanced": "A boundary-drawing objective (listed under supply per workstream brief; arguably capture too)",
}
mapping = CAT[["key", "question", "rating_label", "board_label", "lever", "q9_theme"]].copy()
mapping["why"] = mapping["key"].map(MAP_WHY)
mapping.loc[len(mapping)] = ["(none)", "-", "No survey item asks about birth rates, housing cost or the number of children in the district",
                             "-", DEM, None, "The 714-student (67%) demographic driver has no survey item"]
mapping.to_csv(OUT / "lever_mapping.csv", index=False)

# --------------------------------------------------------------------------- load survey
df = pd.read_csv(P.RESPONSES_WIDE, keep_default_na=False, na_values=[""])
df["stakeholder"] = np.where(df.group == "Parent", np.where(df.employee, "Parents who work for CHCCS", "Other parents"),
                             np.where(df.group == "Non-parent", "Non-parent", "Excluded"))
analysis = df[df.group.isin(["Parent", "Non-parent"])].copy()
STAKE = {
    "Parent": df.group == "Parent",
    "Non-parent": df.group == "Non-parent",
    "Parents who work for CHCCS": (df.group == "Parent") & df.employee,
    "Other parents": (df.group == "Parent") & ~df.employee,
    "All 1,463 respondents": pd.Series(True, index=df.index),
}


def parse_top3(text, question):
    """Return (list of item keys, other_flag, n_picks). Full labels matched longest-first, then removed,
    so the comma inside the boundaries option and misspellings (saftey, Minimize/Maximize) are handled."""
    rem = "" if pd.isna(text) else str(text)
    keys = []
    cands = [(v, k) for k, q, _, variants, *_ in ITEMS if q == question for v in variants]
    cands.sort(key=lambda t: -len(t[0]))
    for variant, key in cands:
        if variant in rem and key not in keys:
            keys.append(key)
            rem = rem.replace(variant, "", 1)
    residual = rem.replace(",", "").strip()
    other = len(residual) > 0
    return keys, other, len(keys) + int(other)


for q, col in [("C", "top3_challenges"), ("V", "top3_values")]:
    parsed = df[col].apply(lambda s: parse_top3(s, q))
    for key in CAT[CAT.question == q].key:
        df[f"T3_{key}"] = parsed.apply(lambda t: key in t[0])
    df[f"T3_other_{q}"] = parsed.apply(lambda t: t[1])
    df[f"T3_npicks_{q}"] = parsed.apply(lambda t: t[2])
pick_dist = pd.DataFrame({
    "challenges_Q7": df["T3_npicks_C"].value_counts().sort_index(),
    "values_Q8": df["T3_npicks_V"].value_counts().sort_index()}).fillna(0).astype(int)
pick_dist.index.name = "n_picks_parsed"
pick_dist.to_csv(OUT / "top3_pick_count_distribution.csv")

# cross-check against Module 2's published Q7 shares
chk = pd.read_csv(P.M2_EXPL / "02_challenges" / "results" / "challenge_top3_q7_by_group.csv")
lab2key = {}
for k, q, lab, variants in CAT[["key", "question", "rating_label", "top3_variants"]].itertuples(index=False):
    lab2key[lab] = k
    for v in variants:
        lab2key[v] = k
mine = {r: lab2key[r] for r in chk.challenge}
chk["ws_c_parent_pct"] = [round(100 * df.loc[STAKE["Parent"], f"T3_{mine[c]}"].mean(), 4) for c in chk.challenge]
assert np.allclose(chk.parent_pct_top3, chk.ws_c_parent_pct, atol=0.01), "Q7 parsing disagrees with Module 2"

# --------------------------------------------------------------------------- Task 1: lever x stakeholder
board = pd.read_csv(P.BOARD_VS_CPA)
board = board.merge(CAT[["key", "board_label", "lever", "question"]], left_on="item", right_on="board_label", how="left")
assert board.key.notna().all(), board[board.key.isna()]
board.to_csv(OUT / "board_vs_cpa_with_levers.csv", index=False)

rows = []
for lever in LEVERS:
    items_c = CAT[(CAT.lever == lever) & (CAT.question == "C")].key.tolist()
    items_v = CAT[(CAT.lever == lever) & (CAT.question == "V")].key.tolist()
    n_items = len(items_c) + len(items_v)
    for stake, mask in STAKE.items():
        sub = df[mask]
        n = len(sub)
        # share of picks landing in lever (denominator: all parsed picks incl. 'other')
        picks_c = sub[[f"T3_{k}" for k in items_c]].sum().sum() if items_c else 0
        picks_v = sub[[f"T3_{k}" for k in items_v]].sum().sum() if items_v else 0
        tot_c, tot_v = sub["T3_npicks_C"].sum(), sub["T3_npicks_V"].sum()
        any_c = sub[[f"T3_{k}" for k in items_c]].any(axis=1).mean() if items_c else np.nan
        any_v = sub[[f"T3_{k}" for k in items_v]].any(axis=1).mean() if items_v else np.nan
        rate_cols = [("C: " if q == "C" else "V: ") + lab for k, q, lab in CAT[["key", "question", "rating_label"]].itertuples(index=False) if k in items_c + items_v]
        if rate_cols:
            mean_rating = sub[rate_cols].mean(axis=1).mean()
            pct45 = np.mean([(sub[c] >= 4).mean() for c in rate_cols]) * 100
        else:
            mean_rating = pct45 = np.nan
        q9_keys = CAT[(CAT.lever == lever) & (CAT.question == "V")].rating_label.tolist()
        q9_share = sub.q9_value.isin(q9_keys).sum() / sub.q9_value.notna().sum() * 100 if n else np.nan
        rows.append(dict(lever=lever, stakeholder=stake, n=n, n_items=n_items,
                         items_offered_share=round(100 * n_items / 26, 1),
                         q7_pick_share=round(100 * picks_c / tot_c, 1) if items_c else 0.0,
                         q8_pick_share=round(100 * picks_v / tot_v, 1) if items_v else 0.0,
                         top3_pick_share_all=round(100 * (picks_c + picks_v) / (tot_c + tot_v), 1),
                         q7_any_in_top3_pct=round(100 * any_c, 1) if items_c else 0.0,
                         q8_any_in_top3_pct=round(100 * any_v, 1) if items_v else 0.0,
                         mean_rating_1_5=round(mean_rating, 2) if rate_cols else np.nan,
                         pct_rated_4_5=round(pct45, 1) if rate_cols else np.nan,
                         q9_share=round(q9_share, 1) if items_v else 0.0))
    # Board (n=7) from the transcribed report: percentages only
    b = board[board.lever == lever]
    bc, bv = b[b.question == "C"], b[b.question == "V"]
    tot_bc, tot_bv = board[board.question == "C"].board_pct_top3.sum(), board[board.question == "V"].board_pct_top3.sum()
    rows.append(dict(lever=lever, stakeholder="Board (n=7)", n=7, n_items=n_items,
                     items_offered_share=round(100 * n_items / 26, 1),
                     q7_pick_share=round(100 * bc.board_pct_top3.sum() / tot_bc, 1),
                     q8_pick_share=round(100 * bv.board_pct_top3.sum() / tot_bv, 1),
                     top3_pick_share_all=round(100 * (bc.board_pct_top3.sum() + bv.board_pct_top3.sum()) / (tot_bc + tot_bv), 1),
                     q7_any_in_top3_pct=np.nan, q8_any_in_top3_pct=np.nan, mean_rating_1_5=np.nan,
                     pct_rated_4_5=round(b.board_pct_rated_4_5.mean(), 1) if len(b) else np.nan, q9_share=np.nan))
lever_long = pd.DataFrame(rows)
lever_long["attention_index"] = (lever_long.top3_pick_share_all / lever_long.items_offered_share).round(2)
lever_long.to_csv(OUT / "lever_by_stakeholder_long.csv", index=False)
wide = lever_long.pivot(index="lever", columns="stakeholder",
                        values=["top3_pick_share_all", "pct_rated_4_5", "q9_share", "attention_index"])
wide.to_csv(OUT / "lever_by_stakeholder_wide.csv")
# headline: lever x stakeholder, top-3 pick share
headline = lever_long.pivot(index="lever", columns="stakeholder", values="top3_pick_share_all").reindex(LEVERS)
headline = headline[["Other parents", "Parents who work for CHCCS", "Parent", "Non-parent", "All 1,463 respondents", "Board (n=7)"]]
headline.to_csv(OUT / "headline_lever_x_stakeholder_top3_share.csv")

# item-level table (every stakeholder, every item) to feed a dot plot
item_rows = []
for k, q, lab, lever in CAT[["key", "question", "rating_label", "lever"]].itertuples(index=False):
    col = ("C: " if q == "C" else "V: ") + lab
    r = dict(key=k, question=q, item=lab, lever=lever)
    for stake, mask in STAKE.items():
        sub = df[mask]
        r[f"top3_pct|{stake}"] = round(100 * sub[f"T3_{k}"].mean(), 1)
        r[f"rated_4_5_pct|{stake}"] = round(100 * (sub[col] >= 4).mean(), 1)
    b = board[board.key == k].iloc[0]
    r["top3_pct|Board (n=7)"] = b.board_pct_top3
    r["rated_4_5_pct|Board (n=7)"] = b.board_pct_rated_4_5
    r["top3_pct|CPA report"] = b.cpa_pct_top3
    r["rated_4_5_pct|CPA report"] = b.cpa_pct_rated_4_5
    if q == "V":
        r["q9_pct|Parent"] = round(100 * (df.loc[STAKE["Parent"], "q9_value"] == lab).mean(), 1)
        r["q9_pct|Non-parent"] = round(100 * (df.loc[STAKE["Non-parent"], "q9_value"] == lab).mean(), 1)
    item_rows.append(r)
pd.DataFrame(item_rows).to_csv(OUT / "item_by_stakeholder.csv", index=False)

# --------------------------------------------------------------------------- Task 2: Q8 by Q9 theme
THEMES = ["Student Learning", "Money & buildings", "Community", "Student logistics & well-being"]
theme_keys = {t: CAT[CAT.q9_theme == t].key.tolist() for t in THEMES}
for t, keys in theme_keys.items():
    df[f"Q8n_{t}"] = df[[f"T3_{k}" for k in keys]].sum(axis=1)
    df[f"Q8any_{t}"] = df[f"Q8n_{t}"] > 0
analysis = df[df.group.isin(["Parent", "Non-parent"])].copy()
q8_rows, tests = [], []
for t in THEMES:
    for g in ["Parent", "Non-parent"]:
        sub = df[df.group == g]
        q8_rows.append(dict(theme=t, group=g, measure="any value from theme in Q8 top 3", **pct_row(sub[f"Q8any_{t}"].sum(), len(sub))))
        q8_rows.append(dict(theme=t, group=g, measure="mean number of Q8 picks from theme (0-3)", n=len(sub), k=np.nan,
                            pct=round(sub[f"Q8n_{t}"].mean(), 3), ci_lo=np.nan, ci_hi=np.nan))
        q8_rows.append(dict(theme=t, group=g, measure="Q9 single choice from theme (pre-registered framing)",
                            **pct_row((sub.q9_theme == t).sum(), sub.q9_theme.notna().sum())))
    a = analysis
    chi, p = monte_carlo_chi2(a.group, a[f"Q8any_{t}"])
    tab = pd.crosstab(a.group, a[f"Q8any_{t}"])
    tests.append(dict(theme=t, indicator="any in Q8 top 3", n=len(a), chi_square=round(chi, 2), p_monte_carlo=round(p, 4),
                      cramers_v=round(cramers_v(tab), 3),
                      parent_pct=round(100 * a.loc[a.group == "Parent", f"Q8any_{t}"].mean(), 1),
                      non_parent_pct=round(100 * a.loc[a.group == "Non-parent", f"Q8any_{t}"].mean(), 1)))
# count-based version for Student Learning (0 / 1 / 2 picks) and 'both' indicator
a = analysis
chi, p = monte_carlo_chi2(a.group, a["Q8n_Student Learning"].clip(upper=2))
tests.append(dict(theme="Student Learning", indicator="number of Student Learning picks in Q8 (0/1/2)", n=len(a), chi_square=round(chi, 2),
                  p_monte_carlo=round(p, 4), cramers_v=round(cramers_v(pd.crosstab(a.group, a["Q8n_Student Learning"].clip(upper=2))), 3),
                  parent_pct=round(100 * (a.loc[a.group == "Parent", "Q8n_Student Learning"] == 2).mean(), 1),
                  non_parent_pct=round(100 * (a.loc[a.group == "Non-parent", "Q8n_Student Learning"] == 2).mean(), 1)))
tests = pd.DataFrame(tests)
tests["q_bh"] = multipletests(tests.p_monte_carlo, method="fdr_bh")[1].round(4)
tests.to_csv(OUT / "q8_theme_tests.csv", index=False)
pd.DataFrame(q8_rows).to_csv(OUT / "q8_theme_by_group.csv", index=False)
sl_counts = pd.crosstab(analysis.group, analysis["Q8n_Student Learning"], normalize="index").mul(100).round(1)
sl_counts.to_csv(OUT / "q8_student_learning_pick_counts_by_group.csv")
# Q9 conditional on Q8: among those with both Student Learning values in Q8, does Q9 still differ?
cond = []
for label, m in [("both SL values in Q8 top 3", df["Q8n_Student Learning"] == 2), ("exactly one SL value in Q8", df["Q8n_Student Learning"] == 1),
                 ("no SL value in Q8", df["Q8n_Student Learning"] == 0)]:
    for g in ["Parent", "Non-parent"]:
        sub = df[m & (df.group == g) & df.q9_theme.notna()]
        cond.append(dict(q8_condition=label, group=g, **pct_row((sub.q9_theme == "Student Learning").sum(), len(sub)),
                         measure="Q9 = Student Learning"))
pd.DataFrame(cond).to_csv(OUT / "q9_student_learning_conditional_on_q8.csv", index=False)

# --------------------------------------------------------------------------- Task 3: dollars and scenarios
lay = pd.read_csv(P.CHCCS_LAYERS).set_index("year")
y0, y1 = 2019, 2024
adm0, adm1 = lay.loc[y0, "total_adm"], lay.loc[y1, "total_adm"]
pop0, pop1 = lay.loc[y0, "pop_5_17"], lay.loc[y1, "pop_5_17"]
cap0, cap1 = adm0 / pop0, adm1 / pop1
decline = adm0 - adm1
demo_m1 = (pop0 - pop1) * cap0                 # Module 1 convention: demographic change at 2019 capture
capt_m1 = (cap0 - cap1) * pop1                 # capture change applied to 2024 population
demo_sh = (pop0 - pop1) * (cap0 + cap1) / 2    # symmetric (Shapley) split
capt_sh = (cap0 - cap1) * (pop0 + pop1) / 2
needed_cap = adm0 / pop1
PP = {2027: 8356, 2028: 8690, 2029: 9038, 2030: 9400, 2031: 9776}      # board deck, state funding per pupil
LOCAL_PP_2026 = 8895
deck_reduction = {2027: 2565340, 2028: 4892697, 2029: 7591936, 2030: 10123304, 2031: 13099198}
deck_adm = {2025: 11065, 2026: 10758, 2027: 10502, 2028: 10225, 2029: 9988, 2030: 9725, 2031: 9535}
# replicate the deck: reduction_t = (FY2025 actual ADM - funded ADM_t) x per-pupil_t, funded = prior-year ADM (arrears)
rep = []
for fy in range(2027, 2032):
    funded = deck_adm[fy - 1]
    est = (deck_adm[2025] - funded) * PP[fy]
    rep.append(dict(fiscal_year=fy, projected_adm=deck_adm[fy], funded_adm_arrears=funded, state_pp=PP[fy],
                    adm_below_fy2025=deck_adm[2025] - funded, replicated_reduction=est, deck_reduction=deck_reduction[fy],
                    diff=est - deck_reduction[fy]))
rep = pd.DataFrame(rep)
rep.to_csv(OUT / "deck_state_funding_replication.csv", index=False)
cum_deck = sum(deck_reduction.values())

dollar = pd.DataFrame([
    dict(component="Total K-12 ADM decline 2019->2024", students=decline, share_pct=100.0),
    dict(component="Demographic (fewer 5-17 residents; Module 1 convention)", students=round(demo_m1), share_pct=round(100 * demo_m1 / decline, 1)),
    dict(component="Capture-rate loss (residents enrolling elsewhere; Module 1 convention)", students=round(capt_m1), share_pct=round(100 * capt_m1 / decline, 1)),
    dict(component="Demographic (symmetric split)", students=round(demo_sh), share_pct=round(100 * demo_sh / decline, 1)),
    dict(component="Capture-rate loss (symmetric split)", students=round(capt_sh), share_pct=round(100 * capt_sh / decline, 1)),
])
dollar["state_$_per_year_FY2027_rate"] = (dollar.students * PP[2027]).round(0)
dollar["state_$_FY2027_31_cumulative"] = (dollar.students * sum(PP.values())).round(0)
dollar["local_$_per_year_FY2026_rate"] = (dollar.students * LOCAL_PP_2026).round(0)
dollar["share_of_deck_38.3M_pct"] = (100 * dollar["state_$_FY2027_31_cumulative"] / cum_deck).round(1)
dollar.to_csv(OUT / "decomposition_dollars.csv", index=False)

# scenarios 2025 -> 2031 (DPI year = fiscal year; 2025 = 2024-25 actual 11,065)
pop = pd.read_csv(P.LEA_POP)
pop = pop[pop.agency_code == P.CHCCS_LEA].set_index("year").pop_5_17
def ols_slope(s):
    x = np.array(s.index, dtype=float); y = s.values.astype(float)
    return float(np.polyfit(x, y, 1)[0])
slope_fast = ols_slope(pop.loc[2019:2024])
slope_slow = ols_slope(pop.loc[2014:2024])
cap_slope = (cap1 - cap0) / (y1 - y0)
years = list(range(2024, 2032))
scen_rows = []
for window, slope in [("SAIPE 2019-24 OLS", slope_fast), ("SAIPE 2014-24 OLS", slope_slow)]:
    pop_path = {y: pop1 + slope * (y - 2024) for y in years}
    caps = {
        "A: demographics only (capture held at 2024 = %.4f)" % cap1: {y: cap1 for y in years},
        "B: demographics + capture keeps falling (%.4f pts/yr)" % cap_slope: {y: cap1 + cap_slope * (y - 2024) for y in years},
        "C: demographics with capture restored to 2019 from 2026 (%.4f)" % cap0: {y: (cap0 if y >= 2026 else cap1) for y in years},
    }
    for scen, cpath in caps.items():
        unanchored = {y: pop_path[y] * cpath[y] for y in years}
        # anchor on the 2025 actual (11,065) and roll forward by scenario year-over-year ratios
        # (scenario C steps capture from the 2024 level back to 2019 in 2026, then holds it)
        adm = {2024: adm1, 2025: deck_adm[2025]}
        for y in range(2026, 2032):
            adm[y] = adm[y - 1] * (pop_path[y] / pop_path[y - 1]) * (cpath[y] / cpath[y - 1])
        # deck-method state-funding reduction FY2027-31 (funded = prior-year ADM, vs FY2025 actual)
        red = {fy: (deck_adm[2025] - adm[fy - 1]) * PP[fy] for fy in range(2027, 2032)}
        scen_rows.append(dict(saipe_window=window, pop_5_17_slope_per_yr=round(slope, 1), scenario=scen,
                              pop_5_17_2031=round(pop_path[2031]), capture_2031=round(cpath[2031], 4),
                              adm_2025_unanchored_check=round(unanchored[2025]), adm_2025_actual=deck_adm[2025],
                              adm_2031=round(adm[2031]), change_2025_31=round(adm[2031] - deck_adm[2025]),
                              pct_change_2025_31=round(100 * (adm[2031] / deck_adm[2025] - 1), 1),
                              deck_adm_2031=deck_adm[2031], gap_vs_deck_2031=round(adm[2031] - deck_adm[2031]),
                              elementary_2031_scaled=round(adm[2031] * 4522 / 11065),
                              closure_study_elementary_2031=4177,
                              state_reduction_FY2027_31=round(sum(red.values())), deck_state_reduction_FY2027_31=cum_deck,
                              **{f"adm_{y}": round(adm[y]) for y in range(2026, 2031)}))
scen = pd.DataFrame(scen_rows)
scen.to_csv(OUT / "scenario_table_2025_2031.csv", index=False)
# students per year the continuing capture trend costs (B minus A), by year, fast window
fast = scen[scen.saipe_window == "SAIPE 2019-24 OLS"].set_index("scenario")
A_row, B_row, C_row = [fast.iloc[i] for i in range(3)]
cap_cost = pd.DataFrame({
    "year": range(2026, 2032),
    "adm_A_demographics_only": [A_row[f"adm_{y}"] for y in range(2026, 2032)],
    "adm_B_capture_keeps_falling": [B_row[f"adm_{y}"] for y in range(2026, 2032)],
    "adm_C_capture_at_2019": [C_row[f"adm_{y}"] for y in range(2026, 2032)],
})
cap_cost["students_lost_to_capture_trend_cum"] = cap_cost.adm_A_demographics_only - cap_cost.adm_B_capture_keeps_falling
cap_cost["students_lost_to_capture_trend_per_yr"] = cap_cost.students_lost_to_capture_trend_cum.diff().fillna(cap_cost.students_lost_to_capture_trend_cum)
cap_cost["state_$_at_that_years_pp"] = [round(r * PP.get(y, PP[2027])) for r, y in zip(cap_cost.students_lost_to_capture_trend_cum, cap_cost.year)]
cap_cost.to_csv(OUT / "capture_trend_cost_by_year.csv", index=False)
misc3 = dict(adm_2019=adm0, adm_2024=adm1, pop_5_17_2019=pop0, pop_5_17_2024=pop1, capture_2019=round(cap0, 4), capture_2024=round(cap1, 4),
             capture_needed_2024_to_hold_2019_adm=round(needed_cap, 4), adm_2024_if_capture_held_at_2019=round(pop1 * cap0),
             capture_pts_per_yr=round(cap_slope, 5), slope_fast=round(slope_fast, 1), slope_slow=round(slope_slow, 1),
             deck_cum_reduction=cum_deck, deck_five_year_deficit=37.9e6)
pd.Series(misc3).to_csv(OUT / "task3_key_numbers.csv", header=["value"])

# --------------------------------------------------------------------------- Task 4: who picks the three items
df["age_band"] = df.age.replace({"13 to 17 years": "Under 30", "18 to 29 years": "Under 30"}).fillna("Missing")
df["language"] = np.where(df.source_sheet == "English", "English form", "Non-English form")
wi = pd.read_csv(P.WRITE_IN_CODES).set_index("participant_id")
themes_wi = sorted({c.split("|")[1] for c in wi.columns})
wi_any = pd.DataFrame({t: wi[[c for c in wi.columns if c.endswith("|" + t)]].max(axis=1) for t in themes_wi})
wi_any["is_writer"] = wi_any.max(axis=1) > 0
df = df.merge(wi_any, left_on="participant_id", right_index=True, how="left")
df[themes_wi] = df[themes_wi].fillna(0).astype(int)
df["is_writer"] = df["is_writer"].fillna(False).astype(bool)

TARGETS = {
    "Appeal of the district (Q7 top 3)": df["T3_appeal"],
    "Retaining highly effective employees (Q7 top 3)": df["T3_retain_staff"],
    "Fiscal responsibility rated 4-5 (Q5)": df["V: Fiscal responsibility"] >= 4,
    "Fiscal responsibility (Q8 top 3)": df["T3_fiscal"],
}
BREAKS = {"stakeholder": "stakeholder", "age_band": "age_band", "language": "language", "q9_theme": "q9_theme"}
prof_rows, prof_tests = [], []
base = df[df.group.isin(["Parent", "Non-parent"])]
for tname, ind in TARGETS.items():
    ind = ind[base.index]
    prof_rows.append(dict(target=tname, breakdown="all", level="Parent + Non-parent (n=1,413)", **pct_row(ind.sum(), len(ind))))
    for bname, col in BREAKS.items():
        levels = base[col].value_counts()
        for lev, n in levels.items():
            if lev in ("Missing",) or n < 10:
                prof_rows.append(dict(target=tname, breakdown=bname, level=lev, n="<10" if n < 10 else n, k=np.nan, pct=np.nan, ci_lo=np.nan, ci_hi=np.nan))
                continue
            m = base[col] == lev
            prof_rows.append(dict(target=tname, breakdown=bname, level=lev, **pct_row(ind[m].sum(), m.sum())))
        keep = base[col].notna() & (base[col] != "Missing") & base[col].map(levels) .ge(10)
        chi, p = monte_carlo_chi2(base.loc[keep, col], ind[keep])
        prof_tests.append(dict(target=tname, breakdown=bname, n=int(keep.sum()), chi_square=round(chi, 2), p_monte_carlo=round(p, 4),
                               cramers_v=round(cramers_v(pd.crosstab(base.loc[keep, col], ind[keep])), 3)))
    # parent vs non-parent Fisher for the record
    tab = pd.crosstab(base.group, ind)
    orr, p = fisher_exact(tab.values)
    prof_tests.append(dict(target=tname, breakdown="Parent vs Non-parent (Fisher)", n=len(base), chi_square=np.nan, p_monte_carlo=round(p, 4),
                           cramers_v=round(cramers_v(tab), 3)))
prof = pd.DataFrame(prof_rows)
prof.to_csv(OUT / "item_profiles_by_subgroup.csv", index=False)
prof_tests = pd.DataFrame(prof_tests)
prof_tests["q_bh_within_target"] = np.nan
for t in TARGETS:
    m = prof_tests.target == t
    prof_tests.loc[m, "q_bh_within_target"] = multipletests(prof_tests.loc[m, "p_monte_carlo"], method="fdr_bh")[1].round(4)
prof_tests.to_csv(OUT / "item_profile_tests.csv", index=False)

# write-in theme co-occurrence (writers only) and co-picks
co_rows = []
writers = base[base.is_writer]
for tname, ind in TARGETS.items():
    ind_w = ind[writers.index]
    for t in themes_wi:
        a_, b_ = writers.loc[ind_w, t].sum(), (~writers.loc[ind_w, t].astype(bool)).sum()
        c_, d_ = writers.loc[~ind_w, t].sum(), (~writers.loc[~ind_w, t].astype(bool)).sum()
        orr, p = fisher_exact([[a_, b_], [c_, d_]])
        co_rows.append(dict(target=tname, write_in_theme=t, n_writers_picking=int(ind_w.sum()), n_writers_not=int((~ind_w).sum()),
                            pct_pickers_mentioning=round(100 * a_ / ind_w.sum(), 1), pct_nonpickers_mentioning=round(100 * c_ / (~ind_w).sum(), 1),
                            k_pickers=int(a_), odds_ratio=round(orr, 2), p_fisher=round(p, 4)))
co = pd.DataFrame(co_rows)
co["q_bh_within_target"] = np.nan
for t in TARGETS:
    m = co.target == t
    co.loc[m, "q_bh_within_target"] = multipletests(co.loc[m, "p_fisher"], method="fdr_bh")[1].round(4)
co["k_pickers"] = co.k_pickers.where(co.k_pickers >= 10, other=np.nan)  # suppress tiny cells in the published table
co.to_csv(OUT / "item_writein_cooccurrence.csv", index=False)
writer_share = dict(n_base=len(base), n_writers=len(writers),
                    pct_writers_appeal=round(100 * base.loc[base["T3_appeal"], "is_writer"].mean(), 1),
                    pct_writers_not_appeal=round(100 * base.loc[~base["T3_appeal"], "is_writer"].mean(), 1))
pd.Series(writer_share).to_csv(OUT / "writer_share_by_appeal.csv", header=["value"])

copick_rows = []
for tname, ind, q in [("Appeal of the district (Q7 top 3)", df["T3_appeal"], "C"), ("Retaining highly effective employees (Q7 top 3)", df["T3_retain_staff"], "C"),
                      ("Fiscal responsibility (Q8 top 3)", df["T3_fiscal"], "V")]:
    ind = ind[base.index]
    for k, lab, lever in CAT[CAT.question == q][["key", "rating_label", "lever"]].itertuples(index=False):
        col = f"T3_{k}"
        copick_rows.append(dict(target=tname, co_item=lab, lever=lever, pct_among_pickers=round(100 * base.loc[ind, col].mean(), 1),
                                pct_among_non_pickers=round(100 * base.loc[~ind, col].mean(), 1)))
copick = pd.DataFrame(copick_rows)
copick["diff_pts"] = (copick.pct_among_pickers - copick.pct_among_non_pickers).round(1)
copick.to_csv(OUT / "item_copicks.csv", index=False)

# --------------------------------------------------------------------------- Task 5: elementary forecast table
sa = pd.read_csv(P.SCHOOL_ADM, dtype={"agency_code": str})
elem = sa[(sa.lea_code == P.CHCCS_LEA) & (sa.span == "E")].groupby("year").avg_student_num.sum()
assert elem.loc[2019] == 5488 and elem.loc[2025] == 4522
k12 = sa[sa.lea_code == P.CHCCS_LEA].groupby("year").avg_student_num.sum()
cf = pd.read_csv(P.CLOSURE_FORECAST)
closure = cf[[str(y) for y in range(2026, 2037)]].sum()
closure.index = closure.index.astype(int)
assert closure.loc[2026] == 4294 and abs(closure.loc[2036] - 4183) <= 2  # per-school sum is 4,184; study text says 4,183
elem_share_2025 = 4522 / 11065
bf = pd.read_csv(P.BOARD_FORECAST).set_index("fiscal_year").projected_adm
deck_scaled = {2026: deck_adm[2026] * elem_share_2025, **{y: bf.loc[y] * elem_share_2025 for y in bf.index}}
# naive continuations of 2019-2025 elementary
x = np.arange(2019, 2026); yv = elem.loc[2019:2025].values.astype(float)
lin_slope, lin_int = np.polyfit(x, yv, 1)
cagr = (elem.loc[2025] / elem.loc[2019]) ** (1 / 6) - 1
table = pd.DataFrame(index=range(2015, 2037))
table.index.name = "year"
table["actual_elementary_adm"] = elem.reindex(table.index)
table["actual_k12_adm"] = k12.reindex(table.index)
table["closure_study_forecast"] = closure.reindex(table.index)
table["board_deck_k12_scaled_by_2025_elem_share"] = pd.Series(deck_scaled).reindex(table.index).round(0)
table["trend_linear_2019_25"] = [round(elem.loc[2025] + lin_slope * (y - 2025)) if y >= 2026 else np.nan for y in table.index]
table["trend_cagr_2019_25"] = [round(elem.loc[2025] * (1 + cagr) ** (y - 2025)) if y >= 2026 else np.nan for y in table.index]
table["scenario_A_demographics_only_scaled"] = pd.Series({y: A_row[f"adm_{y}"] * elem_share_2025 for y in range(2026, 2032)}).reindex(table.index).round(0)
table["scenario_B_capture_falls_scaled"] = pd.Series({y: B_row[f"adm_{y}"] * elem_share_2025 for y in range(2026, 2032)}).reindex(table.index).round(0)
table.to_csv(OUT / "elementary_adm_actual_and_forecasts.csv")
AVG_SCHOOL = 4522 / 11
gap = []
for name, col in [("Naive linear trend 2019-25", "trend_linear_2019_25"), ("Naive CAGR trend 2019-25", "trend_cagr_2019_25"),
                  ("Board deck K-12 x 2025 elementary share", "board_deck_k12_scaled_by_2025_elem_share"),
                  ("Scenario A demographics only (scaled)", "scenario_A_demographics_only_scaled"),
                  ("Scenario B capture keeps falling (scaled)", "scenario_B_capture_falls_scaled")]:
    v = table.loc[2031, col]
    gap.append(dict(comparison=name, value_2031=v, closure_study_2031=closure.loc[2031], gap_students=round(closure.loc[2031] - v),
                    gap_in_avg_elementary_schools=round((closure.loc[2031] - v) / AVG_SCHOOL, 2)))
gap = pd.DataFrame(gap)
gap.to_csv(OUT / "forecast_gap_2031.csv", index=False)
task5 = dict(elem_2019=5488, elem_2025=4522, pct_change_2019_25=round(100 * (4522 / 5488 - 1), 1), linear_slope_per_yr=round(lin_slope, 1),
             cagr_pct=round(100 * cagr, 2), elem_share_2025=round(elem_share_2025, 4), avg_elementary_school_adm=round(AVG_SCHOOL, 1),
             closure_2026=4294, closure_2031=int(closure.loc[2031]), closure_2036=4183, drop_2025_to_closure_2026=4522 - 4294,
             drop_pct=round(100 * (4294 / 4522 - 1), 1), closure_change_2026_36_pct=round(100 * (4183 / 4294 - 1), 1),
             deck_change_2025_31_pct=round(100 * (9535 / 11065 - 1), 1))
pd.Series(task5).to_csv(OUT / "task5_key_numbers.csv", header=["value"])

# Long-term planning attention (survey vs board) for the Task 5 narrative
ltp = board[board.key == "long_term"].iloc[0]
ltp_out = dict(board_rated_4_5=ltp.board_pct_rated_4_5, cpa_rated_4_5=ltp.cpa_pct_rated_4_5, board_top3=ltp.board_pct_top3, cpa_top3=ltp.cpa_pct_top3,
               q9_long_term_count=int((df.q9_value == "Long-term planning").sum()), q9_long_term_pct=round(100 * (df.q9_value == "Long-term planning").mean(), 1),
               parent_top3=round(100 * df.loc[STAKE["Parent"], "T3_long_term"].mean(), 1), non_parent_top3=round(100 * df.loc[STAKE["Non-parent"], "T3_long_term"].mean(), 1))
pd.Series(ltp_out).to_csv(OUT / "long_term_planning_attention.csv", header=["value"])

print("done; outputs in", OUT)
