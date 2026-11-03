"""Workstream B: the schools people wrote about, joined to what Module 1 knows about each school.

Detects CHCCS school-name mentions in the survey free text (Q4, Q6, Q10 and the Q9 "Other"
write-in), joins the 11 elementary schools to Module 1 school attributes (ADM, capacity,
utilization, forecasts, EDS share, SRTS walk counts, building age, DLI/closure status), and
tests descriptively whether mention rates and themes track those attributes.

Outputs go to results/ws_b/. Free text is never written out; only counts and codes.
"""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.proportion import proportion_confint

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths as P  # noqa: E402

OUT = P.RESULTS / "ws_b"
OUT.mkdir(parents=True, exist_ok=True)
RNG = np.random.default_rng(510)

ELEM = list(P.ELEM_CODES.values())
CODE_BY_NAME = {v: k for k, v in P.ELEM_CODES.items()}

# ----------------------------------------------------------------------------------------------
# 1. School mention detection
# ----------------------------------------------------------------------------------------------
# Each pattern is applied case-insensitively to one text field at a time. A respondent counts
# once per school regardless of how many times or in how many fields the name appears.
PATTERNS = {
    # Elementary schools
    "Northside": r"\bnorthside\b",
    "Carrboro": (  # strict: the elementary school named as such
        r"\bcarrboro\s+(elementary|elem\b|es\b)|\bCES\b"
    ),
    "Carrboro (raw, any use)": r"\bcarrboro\b",  # includes the town, the district name and the high school
    "Carrboro (loose)": (  # any Carrboro that is not the high school, the district name or the town
        r"(?<!chapel hill[- ])(?<!chapel hill and )(?<!town of )\bcarrboro\b(?!\s+(high|city|hs\b|town|planning|government|school district))"
    ),
    "Seawell": r"\bseawell\b",
    "Ephesus": r"\bephesus\b(?!\s+(church|rd\b|road|park))",
    "Estes Hills": r"\bestes\b(?!\s+(dr\b|drive))",
    "Frank Porter Graham": r"\bFPGB?\b|frank\s+porter|biling[uü]e?\b",
    "Glenwood": r"\bglenwood\b",
    "McDougle": r"\bmcdougle\b",  # any McDougle (split below)
    "McDougle (elementary stated)": r"\bmcdougle\s+(elementary|elem\b|es\b)",
    "McDougle (middle stated)": r"\bmcdougle\s+(middle|ms\b)|\bMMS\b",
    "Scroggs": r"\b(mary\s+)?scroggs\b",
    "Morris Grove": r"\bmorris\s+grove\b",
    "Rashkis": r"\brashkis\b",
    # Middle schools
    "Culbreth MS": r"\bculbreth\b(?!\s+ridge)",
    "Smith MS": r"\bsmith\s+(middle|ms\b)",
    "Phillips MS": r"\bphillips\b",
    "McDougle MS": r"\bmcdougle\s+(middle|ms\b)|\bMMS\b",
    # High schools
    "Chapel Hill HS": r"(?<!east )chapel\s+hill\s+high|\bCHHS\b",
    "East Chapel Hill HS": r"east\s+chapel\s+hill|\bECHHS\b",
    "Carrboro HS": r"carrboro\s+high|\bCHS\b",
    # Programs
    "prog: dual language / immersion": r"dual[\s-]language|\bDLI\b|immersion|mandarin|spanish",
    "prog: magnet / lottery": r"\bmagnet|\blottery",
}
SENTIMENT = {
    "close": r"\bclos(e|ed|es|ing|ure|ures)\b",
    "keep_save_stay": r"\bkeep(s|ing)?\b|\bsave\b|\bstay(s|ing|ed)?\b",
    "walk": r"\bwalk",
    "bus": r"\bbus(es|sed|sing|ses|ing)?\b",
    "dual_language": r"dual[\s-]language|\bDLI\b|immersion|mandarin|spanish",
}
TEXT_FIELDS = ["other_challenges", "other_values", "additional_thoughts", "q9_write_in"]


def load_text():
    w = pd.read_csv(P.RESPONSES_WIDE, dtype=str)
    q9 = pd.read_csv(P.Q9_THEMES, dtype=str)
    q9o = q9.loc[q9.q9_theme == "Other", ["participant_id", "q9_english"]].rename(
        columns={"q9_english": "q9_write_in"})
    t = w[["participant_id", "source_sheet", "group", "other_challenges", "other_values",
           "additional_thoughts"]].merge(q9o, on="participant_id", how="left")
    for f in TEXT_FIELDS:
        t[f] = t[f].fillna("").astype(str)
    t["is_writer"] = t[TEXT_FIELDS].apply(lambda r: any(s.strip() for s in r), axis=1)
    return w, q9, t


def detect(t):
    """Boolean matrix respondent x (pattern) with per-field detail for co-occurrence."""
    rx = {k: re.compile(v, re.I) for k, v in PATTERNS.items()}
    srx = {k: re.compile(v, re.I) for k, v in SENTIMENT.items()}
    rows = []
    for _, r in t.iterrows():
        d = {"participant_id": r.participant_id}
        for k in PATTERNS:
            d[k] = any(rx[k].search(r[f]) for f in TEXT_FIELDS)
        # sentiment co-occurrence: same field contains both the school name and the word
        for k in PATTERNS:
            if k.startswith("prog:"):
                continue
            for s in SENTIMENT:
                d[f"{k}~{s}"] = any(rx[k].search(r[f]) and srx[s].search(r[f]) for f in TEXT_FIELDS)
        rows.append(d)
    m = pd.DataFrame(rows)
    # McDougle elementary = any McDougle mention that is not exclusively the middle school
    m["McDougle (elementary or unspecified)"] = m["McDougle"] & ~(
        m["McDougle (middle stated)"] & ~m["McDougle (elementary stated)"])
    m["McDougle (unspecified)"] = m["McDougle"] & ~m["McDougle (elementary stated)"] & ~m["McDougle (middle stated)"]
    for s in SENTIMENT:
        m[f"McDougle (elementary or unspecified)~{s}"] = m[f"McDougle~{s}"] & m["McDougle (elementary or unspecified)"]
    return m


def elem_col(school):
    """Column in the detection matrix used as the elementary-school mention for the join."""
    if school == "McDougle":
        return "McDougle (elementary or unspecified)"
    return school


def wilson(k, n):
    if n == 0:
        return (np.nan, np.nan)
    lo, hi = proportion_confint(k, n, method="wilson")
    return (round(100 * lo, 1), round(100 * hi, 1))


# ----------------------------------------------------------------------------------------------
# 2. Module 1 school attributes
# ----------------------------------------------------------------------------------------------
def norm_name(s):
    s = re.sub(r"\s+Elementary$", "", s.strip())
    return {"FPG": "Frank Porter Graham", "FPG Bilingüe": "Frank Porter Graham"}.get(s, s)


def school_attributes():
    sm = pd.read_csv(P.SCHOOL_METRICS, dtype={"dpi_code": str})
    sm = sm[sm.dpi_code.isin(P.ELEM_CODES)].copy()
    sm["school"] = sm.dpi_code.map(P.ELEM_CODES)
    sm = sm.rename(columns={
        "adm": "adm_2024_25", "sapfo_capacity": "sapfo_capacity_2025",
        "adm_utilization_percent": "util_2024_25_pct", "program_capacity_2026": "program_capacity_2026",
        "projected_utilization_2030_31": "util_2031_projected_pct"})[
        ["school", "dpi_code", "adm_2024_25", "sapfo_capacity_2025", "util_2024_25_pct",
         "program_capacity_2026", "util_2031_projected_pct"]]

    cf = pd.read_csv(P.CLOSURE_FORECAST)
    cf["school"] = cf.school.map(norm_name)
    cf = cf.rename(columns={"2026": "forecast_2026", "2031": "forecast_2031", "2036": "forecast_2036"})
    cf["forecast_change_2026_2036_pct"] = (100 * (cf.forecast_2036 / cf.forecast_2026 - 1)).round(1)
    cf = cf[["school", "forecast_2026", "forecast_2031", "forecast_2036",
             "forecast_change_2026_2036_pct", "closure_candidate"]]

    adm = pd.read_csv(P.SCHOOL_ADM, dtype={"agency_code": str, "lea_code": str})
    adm = adm[(adm.lea_code == P.CHCCS_LEA) & adm.agency_code.isin(P.ELEM_CODES)].copy()
    adm["school"] = adm.agency_code.map(P.ELEM_CODES)
    piv = adm.pivot_table(index="school", columns="year", values="avg_student_num", aggfunc="first")
    hist = pd.DataFrame({
        "adm_2019": piv[2019], "adm_2025": piv[2025],
        "adm_change_2019_2025_pct": (100 * (piv[2025] / piv[2019] - 1)).round(1),
        "adm_peak_year": piv.idxmax(axis=1), "adm_peak": piv.max(axis=1),
        "adm_change_peak_to_2025_pct": (100 * (piv[2025] / piv.max(axis=1) - 1)).round(1),
    }).reset_index()

    eds = pd.read_csv(P.DPI_EDS, dtype={"agency_code": str})
    eds = eds[(eds.year == 2025) & eds.agency_code.isin(P.ELEM_CODES)].copy()
    eds["school"] = eds.agency_code.map(P.ELEM_CODES)
    eds = eds[["school", "pct_eds"]].rename(columns={"pct_eds": "eds_pct_2024_25"})

    # SRTS walk counts, parsed from the closure study text (Nov 12, 2024 observations)
    txt = Path(P.CLOSURE_STUDY_TXT).read_text(encoding="utf-8")
    walk_rx = re.compile(r"^(.+?) ES (\d+) (\d+) ([\d,]+) ([\d.]+)% ([\d.]+)%\s*$", re.M)
    walk = {}
    for name, wk, bk, enr, wp, bp in walk_rx.findall(txt):
        nm = norm_name(name)
        if nm in ELEM and nm not in walk:
            walk[nm] = dict(srts_walkers=int(wk), srts_bikers=int(bk), srts_enrollment=int(enr.replace(",", "")),
                            srts_walk_pct=float(wp), srts_bike_pct=float(bp))
    walk = pd.DataFrame.from_dict(walk, orient="index").reset_index().rename(columns={"index": "school"})
    # The study itself says Glenwood's 38 observed walkers were mostly parents parking next door;
    # SRTS estimates 2-4 true walkers. Keep the raw count and add an adjusted column.
    walk["srts_walk_pct_adjusted"] = walk.srts_walk_pct
    walk.loc[walk.school == "Glenwood", "srts_walk_pct_adjusted"] = round(100 * 4 / 408, 1)

    # Building year: the closure study states these for the three studied schools only.
    built = {"Ephesus": 1972, "Glenwood": 1952, "Seawell": 1969}
    # Verify the three stated years are in the text as written.
    assert "constructed in 1972" in txt and "opened in 1952" in txt and "opened in 1969" in txt

    a = sm.merge(cf, on="school", how="left").merge(hist, on="school", how="left") \
          .merge(eds, on="school", how="left").merge(walk, on="school", how="left")
    a["year_built"] = a.school.map(built)
    a["building_age_2026"] = 2026 - a.year_built
    a["dli_program"] = a.school.map(P.DLI_SCHOOLS).fillna("")
    a["is_dli"] = a.school.isin(P.DLI_SCHOOLS)
    a["closure_candidate"] = a.school.isin(P.CLOSURE_CANDIDATES)
    a["util_2026_forecast_on_program_cap_pct"] = (100 * a.forecast_2026 / a.program_capacity_2026).round(1)
    a["util_2036_forecast_on_program_cap_pct"] = (100 * a.forecast_2036 / a.program_capacity_2026).round(1)
    return a


def transport_table():
    """Closure study p.26 table for the three studied schools (transcribed from CLOSURE_STUDY_TXT)."""
    txt = Path(P.CLOSURE_STUDY_TXT).read_text(encoding="utf-8")
    assert "for Bus Transportation 253 389 282" in txt
    assert "Riding Bus (AM) 140 170 147" in txt
    assert "125 2 120" in txt and "160 210 207" in txt
    assert "30 minutes 38 minutes 28 minutes" in txt
    rows = [
        dict(school="Ephesus", enrollment_in_study=373, bus_eligible=253, buses=3, am_riders=140,
             ntz_tims=125, srts_walkers=64, srts_bikers=14, driven_by_parents=160, avg_ride_min=30),
        dict(school="Glenwood", enrollment_in_study=391, bus_eligible=389, buses=7, am_riders=170,
             ntz_tims=2, srts_walkers=38, srts_bikers=7, driven_by_parents=210, avg_ride_min=38),
        dict(school="Seawell", enrollment_in_study=402, bus_eligible=282, buses=4, am_riders=147,
             ntz_tims=120, srts_walkers=25, srts_bikers=23, driven_by_parents=207, avg_ride_min=28),
    ]
    t = pd.DataFrame(rows)
    t["bus_eligible_pct"] = (100 * t.bus_eligible / t.enrollment_in_study).round(0)
    t["am_riders_pct_of_enrollment"] = (100 * t.am_riders / t.enrollment_in_study).round(0)
    t["driven_pct"] = (100 * t.driven_by_parents / t.enrollment_in_study).round(0)
    t["note"] = ""
    t.loc[t.school == "Glenwood", "note"] = ("study: most of the 38 observed walkers came from an adjacent "
                                             "retail lot; SRTS estimates 2-4 true walkers; ~220 driven")
    t["source"] = "CHCCS closure study 2026-05-07, p.26 (Criteria #7 transportation)"
    return t


# ----------------------------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------------------------
def main():
    w, q9, t = load_text()
    m = detect(t)
    d = t[["participant_id", "source_sheet", "group", "is_writer"]].merge(m, on="participant_id")
    d["english"] = d.source_sheet == "English"
    n_writers = int(d.is_writer.sum())
    writers = d[d.is_writer]

    # --- mention counts for every pattern (detection variants table) --------------------------
    var_rows = []
    for k in list(PATTERNS) + ["McDougle (elementary or unspecified)", "McDougle (unspecified)"]:
        n = int(d[k].sum())
        var_rows.append(dict(pattern=k, regex=PATTERNS.get(k, "derived"), respondents=n,
                             pct_of_writers=round(100 * n / n_writers, 1),
                             parent=int(d.loc[d.group == "Parent", k].sum()),
                             non_parent=int(d.loc[d.group == "Non-parent", k].sum()),
                             excluded=int(d.loc[d.group == "Excluded", k].sum())))
    variants = pd.DataFrame(var_rows)
    variants.to_csv(OUT / "mention_detection_variants.csv", index=False)

    # respondent-level flags (no text) for other workstreams
    elem_cols = [elem_col(s) for s in ELEM]
    d["any_elem_school"] = d[elem_cols].any(axis=1)
    d["any_school"] = d[elem_cols + ["Culbreth MS", "Smith MS", "Phillips MS", "McDougle MS",
                                     "Chapel Hill HS", "East Chapel Hill HS", "Carrboro HS"]].any(axis=1)
    d["n_elem_schools_mentioned"] = d[elem_cols].sum(axis=1)
    keep = ["participant_id", "group", "english", "is_writer", "any_elem_school", "any_school",
            "n_elem_schools_mentioned"] + elem_cols + ["Carrboro (loose)", "McDougle", "Culbreth MS",
            "Smith MS", "Phillips MS", "McDougle MS", "Chapel Hill HS", "East Chapel Hill HS",
            "Carrboro HS", "prog: dual language / immersion", "prog: magnet / lottery"]
    d[keep].to_csv(OUT / "respondent_school_mentions.csv", index=False)

    # --- 2. school table ---------------------------------------------------------------------
    attrs = school_attributes()
    rows = []
    for s in ELEM:
        c = elem_col(s)
        tot = int(d[c].sum())
        par = int(d.loc[d.group == "Parent", c].sum())
        non = int(d.loc[d.group == "Non-parent", c].sum())
        exc = int(d.loc[d.group == "Excluded", c].sum())
        eng = int(d.loc[d.english, c].sum())
        oth = tot - eng
        if 0 < oth < 5:
            eng_s, oth_s = "<5 (suppressed)", "<5"
        else:
            eng_s, oth_s = str(eng), str(oth)
        r = dict(school=s, mentions_total=tot, mentions_parent=par, mentions_non_parent=non,
                 mentions_excluded_group=exc, mentions_english=eng_s, mentions_other_language=oth_s,
                 pct_of_writers=round(100 * tot / n_writers, 2))
        for sk in SENTIMENT:
            r[f"cooccur_{sk}"] = int(d[f"{c}~{sk}"].sum())
        rows.append(r)
    mentions = pd.DataFrame(rows)
    if "Carrboro" in ELEM:
        mentions["mentions_loose_variant"] = mentions.school.map({
            "Carrboro": int(d["Carrboro (loose)"].sum()), "McDougle": int(d["McDougle"].sum())})
    table = attrs.merge(mentions, on="school", how="left")
    table["mentions_per_100_adm"] = (100 * table.mentions_total / table.adm_2024_25).round(2)
    table["mentions_parent_per_100_adm"] = (100 * table.mentions_parent / table.adm_2024_25).round(2)
    col_order = ["school", "dpi_code", "closure_candidate", "dli_program", "is_dli", "year_built",
                 "building_age_2026", "adm_2024_25", "sapfo_capacity_2025", "util_2024_25_pct",
                 "program_capacity_2026", "forecast_2026", "forecast_2031", "forecast_2036",
                 "util_2026_forecast_on_program_cap_pct", "util_2031_projected_pct",
                 "util_2036_forecast_on_program_cap_pct", "forecast_change_2026_2036_pct",
                 "adm_2019", "adm_2025", "adm_change_2019_2025_pct", "adm_peak_year", "adm_peak",
                 "adm_change_peak_to_2025_pct", "eds_pct_2024_25", "srts_walkers", "srts_bikers",
                 "srts_enrollment", "srts_walk_pct", "srts_walk_pct_adjusted", "srts_bike_pct",
                 "mentions_total", "mentions_parent", "mentions_non_parent", "mentions_excluded_group",
                 "mentions_english", "mentions_other_language", "mentions_loose_variant",
                 "pct_of_writers", "mentions_per_100_adm", "mentions_parent_per_100_adm"] + \
                [f"cooccur_{k}" for k in SENTIMENT]
    table = table[col_order].sort_values("mentions_total", ascending=False)
    table.to_csv(OUT / "school_table.csv", index=False)

    transport = transport_table()
    transport.to_csv(OUT / "transport_closure_candidates.csv", index=False)

    # --- 3a. correlations across 11 schools (n=11; descriptive) --------------------------------
    corr_rows = []
    numeric_attrs = ["util_2024_25_pct", "util_2031_projected_pct", "eds_pct_2024_25", "srts_walk_pct",
                     "srts_walk_pct_adjusted", "adm_change_2019_2025_pct", "adm_change_peak_to_2025_pct",
                     "forecast_change_2026_2036_pct", "adm_2024_25"]
    for y in ["mentions_total", "mentions_per_100_adm", "mentions_parent"]:
        for x in numeric_attrs:
            sub = table[[x, y]].dropna()
            rho, p = stats.spearmanr(sub[x], sub[y])
            corr_rows.append(dict(outcome=y, attribute=x, n_schools=len(sub), spearman_rho=round(rho, 3),
                                  p_value=round(p, 3)))
        for flag in ["closure_candidate", "is_dli"]:
            a = table.loc[table[flag], y]
            b = table.loc[~table[flag], y]
            u, p = stats.mannwhitneyu(a, b, alternative="two-sided", method="exact")
            corr_rows.append(dict(outcome=y, attribute=flag, n_schools=len(table), spearman_rho=np.nan,
                                  p_value=round(p, 3), flag_true_median=float(a.median()),
                                  flag_false_median=float(b.median()), flag_true_n=len(a)))
    # attribute-vs-attribute (Module 1 facts only): is the forecast emptiness tied to poverty share?
    for x, y in [("eds_pct_2024_25", "util_2031_projected_pct"), ("eds_pct_2024_25", "util_2024_25_pct"),
                 ("eds_pct_2024_25", "forecast_change_2026_2036_pct"), ("eds_pct_2024_25", "adm_change_2019_2025_pct"),
                 ("srts_walk_pct", "util_2031_projected_pct"), ("util_2024_25_pct", "util_2031_projected_pct")]:
        sub = table[[x, y]].dropna()
        rho, p = stats.spearmanr(sub[x], sub[y])
        corr_rows.append(dict(outcome=y, attribute=x, n_schools=len(sub), spearman_rho=round(rho, 3),
                              p_value=round(p, 3)))
    corr = pd.DataFrame(corr_rows)
    corr.to_csv(OUT / "school_attribute_correlations.csv", index=False)

    # --- 3b. write-in theme co-occurrence ------------------------------------------------------
    wc = pd.read_csv(P.WRITE_IN_CODES)
    themes = sorted({c.split("|", 1)[1] for c in wc.columns if "|" in c})
    th = pd.DataFrame({"participant_id": wc.participant_id})
    for theme in themes:
        cols = [c for c in wc.columns if c.endswith("|" + theme)]
        th[theme] = wc[cols].astype(str).apply(lambda r: any(v == "True" for v in r), axis=1)
    dw = writers.merge(th, on="participant_id", how="left")
    co_rows = []
    school_cols = elem_cols + ["Culbreth MS", "Smith MS", "Phillips MS", "any_elem_school",
                               "prog: dual language / immersion", "prog: magnet / lottery"]
    for sc in school_cols:
        if sc == "any_elem_school":
            flag = dw[elem_cols].any(axis=1)
        else:
            flag = dw[sc].astype(bool)
        n_m = int(flag.sum())
        if n_m < 5:
            continue
        for theme in themes:
            a = int((flag & dw[theme]).sum())
            b = n_m - a
            c = int((~flag & dw[theme]).sum())
            e = int((~flag).sum()) - c
            _, p = stats.fisher_exact([[a, b], [c, e]])
            lo, hi = wilson(a, n_m)
            co_rows.append(dict(school=sc, theme=theme, mentioners=n_m, mentioners_with_theme=a,
                                pct_mentioners=round(100 * a / n_m, 1), wilson_lo=lo, wilson_hi=hi,
                                other_writers=int((~flag).sum()), other_writers_with_theme=c,
                                pct_other_writers=round(100 * c / max(1, (~flag).sum()), 1),
                                fisher_p=p))
    co = pd.DataFrame(co_rows)
    co["bh_q"] = multipletests(co.fisher_p, method="fdr_bh")[1]
    co["ratio"] = (co.pct_mentioners / co.pct_other_writers.replace(0, np.nan)).round(2)
    co = co.sort_values(["school", "fisher_p"])
    co.to_csv(OUT / "theme_cooccurrence_by_school.csv", index=False)

    # --- 3c. Q9 themes: mentioners vs other writers vs non-writers ----------------------------
    dq = d.merge(q9[["participant_id", "q9_theme"]], on="participant_id")
    dq = dq[dq.group.isin(["Parent", "Non-parent"])]
    dq["segment"] = np.where(dq.any_elem_school, "Mentions an elementary school",
                             np.where(dq.is_writer, "Writes, no school named", "No free text"))
    ct = pd.crosstab(dq.segment, dq.q9_theme)
    ct_pct = (100 * ct.div(ct.sum(axis=1), axis=0)).round(1)
    q9_out = ct.copy()
    q9_out.columns = [f"n_{c}" for c in q9_out.columns]
    for c in ct.columns:
        q9_out[f"pct_{c}"] = ct_pct[c]
    q9_out["n_total"] = ct.sum(axis=1)
    # Monte Carlo chi-square on the two text segments (mentioners vs other writers), themes with Missing dropped
    sub = dq[dq.is_writer & (dq.q9_theme != "Missing")]
    obs = pd.crosstab(sub.any_elem_school, sub.q9_theme)
    chi_obs = stats.chi2_contingency(obs, correction=False)[0]
    labels = sub.any_elem_school.values.copy()
    themes_arr = sub.q9_theme.values
    cnt = 0
    B = 10000
    for _ in range(B):
        RNG.shuffle(labels)
        chi = stats.chi2_contingency(pd.crosstab(labels, themes_arr), correction=False)[0]
        cnt += chi >= chi_obs - 1e-12
    p_mc = (cnt + 1) / (B + 1)
    n = obs.values.sum()
    v = np.sqrt(chi_obs / (n * (min(obs.shape) - 1)))
    q9_out.to_csv(OUT / "q9_theme_by_school_mentioner.csv")
    q9_test = pd.DataFrame([dict(test="chi-square Monte Carlo (10,000 label permutations)",
                                 comparison="elementary-school mentioners vs other writers, Parent+Non-parent, Missing dropped",
                                 n=n, chi2=round(chi_obs, 2), p_mc=round(p_mc, 4), cramers_v=round(v, 3))])
    # Within parents only, same comparison
    subp = sub[sub.group == "Parent"]
    obsp = pd.crosstab(subp.any_elem_school, subp.q9_theme)
    chi_p = stats.chi2_contingency(obsp, correction=False)[0]
    labels = subp.any_elem_school.values.copy()
    themes_arr = subp.q9_theme.values
    cnt = 0
    for _ in range(B):
        RNG.shuffle(labels)
        cnt += stats.chi2_contingency(pd.crosstab(labels, themes_arr), correction=False)[0] >= chi_p - 1e-12
    q9_test = pd.concat([q9_test, pd.DataFrame([dict(
        test="chi-square Monte Carlo (10,000 label permutations)",
        comparison="elementary-school mentioners vs other writers, Parents only, Missing dropped",
        n=obsp.values.sum(), chi2=round(chi_p, 2), p_mc=round((cnt + 1) / (B + 1), 4),
        cramers_v=round(np.sqrt(chi_p / (obsp.values.sum() * (min(obsp.shape) - 1))), 3))])])
    q9_test.to_csv(OUT / "q9_theme_test.csv", index=False)
    # Also: Student Learning share by segment with Wilson CIs
    sl_rows = []
    for seg, g in dq[dq.q9_theme != "Missing"].groupby("segment"):
        k = int((g.q9_theme == "Student Learning").sum())
        lo, hi = wilson(k, len(g))
        sl_rows.append(dict(segment=seg, n=len(g), student_learning=k, pct=round(100 * k / len(g), 1),
                            wilson_lo=lo, wilson_hi=hi))
    for seg, g in dq[(dq.q9_theme != "Missing") & (dq.group == "Parent")].groupby("segment"):
        k = int((g.q9_theme == "Student Learning").sum())
        lo, hi = wilson(k, len(g))
        sl_rows.append(dict(segment=seg + " (parents only)", n=len(g), student_learning=k,
                            pct=round(100 * k / len(g), 1), wilson_lo=lo, wilson_hi=hi))
    pd.DataFrame(sl_rows).to_csv(OUT / "q9_student_learning_by_segment.csv", index=False)

    # --- 3d. ratings: Mann-Whitney, mentioners vs others ---------------------------------------
    rating_cols = [c for c in w.columns if c.startswith("C: ") or c.startswith("V: ")]
    wr = w[["participant_id"] + rating_cols].copy()
    for c in rating_cols:
        wr[c] = pd.to_numeric(wr[c], errors="coerce")
    dr = d[d.group.isin(["Parent", "Non-parent"])].merge(wr, on="participant_id")
    focal = ["C: Student populations have shifted, but school boundaries have not been adjusted to accommodate those changes",
             "C: Partially empty school buildings"]
    mw_rows = []

    def mw(label, flag_a, flag_b, item, family):
        a = dr.loc[flag_a, item].dropna()
        b = dr.loc[flag_b, item].dropna()
        if len(a) < 10 or len(b) < 10:
            return
        u, p = stats.mannwhitneyu(a, b, alternative="two-sided")
        rb = 1 - 2 * u / (len(a) * len(b))  # rank-biserial (negative = group A higher)
        mw_rows.append(dict(family=family, comparison=label, item=item, n_a=len(a), n_b=len(b),
                            mean_a=round(a.mean(), 2), mean_b=round(b.mean(), 2),
                            pct_45_a=round(100 * (a >= 4).mean(), 1), pct_45_b=round(100 * (b >= 4).mean(), 1),
                            median_a=a.median(), median_b=b.median(), rank_biserial_a_minus_b=round(-rb, 3),
                            mw_p=p))

    for item in focal:
        mw("elem-school mentioners vs other writers", dr.any_elem_school, dr.is_writer & ~dr.any_elem_school,
           item, "focal (2 items x 2 comparisons)")
        mw("elem-school mentioners vs all non-mentioners", dr.any_elem_school, ~dr.any_elem_school,
           item, "focal (2 items x 2 comparisons)")
    for item in rating_cols:
        mw("elem-school mentioners vs other writers", dr.any_elem_school, dr.is_writer & ~dr.any_elem_school,
           item, "all 26 items, mentioners vs other writers")
    for s in ELEM:
        c = elem_col(s)
        if d[c].sum() >= 10:
            for item in focal:
                mw(f"{s} mentioners vs other writers", dr[c], dr.is_writer & ~dr[c], item,
                   "per-school (>=10 mentioners) x 2 focal items")
    mwdf = pd.DataFrame(mw_rows)
    mwdf["bh_q_within_family"] = np.nan
    for fam, idx in mwdf.groupby("family").groups.items():
        mwdf.loc[idx, "bh_q_within_family"] = multipletests(mwdf.loc[idx, "mw_p"], method="fdr_bh")[1]
    mwdf.to_csv(OUT / "ratings_mann_whitney.csv", index=False)

    # --- 4. closure candidates vs the emptiest schools ---------------------------------------
    emptiest = table.nsmallest(3, "util_2031_projected_pct").school.tolist()
    cmp_cols = ["school", "closure_candidate", "year_built", "building_age_2026", "adm_2024_25",
                "sapfo_capacity_2025", "util_2024_25_pct", "program_capacity_2026", "util_2031_projected_pct",
                "forecast_2026", "forecast_2031", "forecast_change_2026_2036_pct", "adm_change_2019_2025_pct",
                "adm_change_peak_to_2025_pct", "eds_pct_2024_25", "srts_walk_pct", "srts_walk_pct_adjusted",
                "dli_program", "mentions_total", "mentions_parent", "mentions_per_100_adm", "cooccur_close",
                "cooccur_keep_save_stay", "cooccur_walk"]
    cand = table[table.school.isin(P.CLOSURE_CANDIDATES)][cmp_cols].copy()
    cand["set"] = "closure study (Ephesus, Glenwood, Seawell)"
    emp = table[table.school.isin(emptiest)][cmp_cols].copy()
    emp["set"] = "lowest 2031 projected utilization"
    comp = pd.concat([cand, emp])
    num = [c for c in cmp_cols if c not in ("school", "closure_candidate", "dli_program")]
    means = comp.groupby("set")[num].mean(numeric_only=True).round(1).reset_index()
    means["school"] = "MEAN of set"
    comp = pd.concat([comp, means]).sort_values(["set", "school"])
    comp = comp[["set"] + cmp_cols]
    comp.to_csv(OUT / "candidates_vs_emptiest.csv", index=False)

    # utilization spread across the 11 schools
    spread_rows = []
    for label, col in [("2024-25 ADM / SAPFO capacity", "util_2024_25_pct"),
                       ("2026 forecast / 2026 program capacity", "util_2026_forecast_on_program_cap_pct"),
                       ("2031 projected (study, program capacity)", "util_2031_projected_pct"),
                       ("2036 forecast / 2026 program capacity", "util_2036_forecast_on_program_cap_pct")]:
        x = table[col].astype(float)
        spread_rows.append(dict(measure=label, n_schools=len(x), min=x.min(), min_school=table.loc[x.idxmin(), "school"],
                                max=x.max(), max_school=table.loc[x.idxmax(), "school"], range=round(x.max() - x.min(), 1),
                                mean=round(x.mean(), 1), sd=round(x.std(ddof=1), 1),
                                cv_pct=round(100 * x.std(ddof=1) / x.mean(), 1),
                                n_under_75=int((x < 75).sum()), n_over_100=int((x > 100).sum()),
                                enrollment_weighted_mean=round(float(np.average(x, weights=table.adm_2024_25)), 1)))
    spread = pd.DataFrame(spread_rows)
    spread.to_csv(OUT / "utilization_spread.csv", index=False)

    # --- 5. sentiment co-occurrence (long form) ---------------------------------------------
    sent_rows = []
    for s in ELEM + ["Culbreth MS", "Smith MS", "Phillips MS"]:
        c = elem_col(s)
        tot = int(d[c].sum())
        for sk in SENTIMENT:
            k = int(d[f"{c}~{sk}"].sum())
            sent_rows.append(dict(school=s, mentioners=tot, word_group=sk, regex=SENTIMENT[sk],
                                  cooccurring_respondents=k,
                                  pct_of_mentioners=round(100 * k / tot, 1) if tot else np.nan))
    pd.DataFrame(sent_rows).to_csv(OUT / "sentiment_cooccurrence.csv", index=False)

    # --- group-level mention rates with Wilson CIs ---------------------------------------
    gr = []
    for grp, g in d.groupby("group"):
        gw = g[g.is_writer]
        k = int(gw.any_elem_school.sum())
        lo, hi = wilson(k, len(gw))
        gr.append(dict(group=grp, respondents=len(g), writers=len(gw), writers_pct=round(100 * len(gw) / len(g), 1),
                       writers_naming_elem_school=k, pct_of_writers=round(100 * k / max(1, len(gw)), 1),
                       wilson_lo=lo, wilson_hi=hi,
                       writers_naming_any_school=int(gw.any_school.sum()),
                       writers_mentioning_dli=int(gw["prog: dual language / immersion"].sum()),
                       writers_mentioning_magnet=int(gw["prog: magnet / lottery"].sum())))
    for lang, g in d.groupby(d.english.map({True: "English", False: "Other language"})):
        gw = g[g.is_writer]
        k = int(gw.any_elem_school.sum())
        lo, hi = wilson(k, len(gw))
        gr.append(dict(group=f"sheet: {lang}", respondents=len(g), writers=len(gw),
                       writers_pct=round(100 * len(gw) / len(g), 1),
                       writers_naming_elem_school=k if (k == 0 or k >= 5) else "<5",
                       pct_of_writers=round(100 * k / max(1, len(gw)), 1) if (k == 0 or k >= 5) else "suppressed",
                       wilson_lo=lo if k >= 5 else np.nan, wilson_hi=hi if k >= 5 else np.nan,
                       writers_naming_any_school=int(gw.any_school.sum()) if gw.any_school.sum() >= 5 else "<5",
                       writers_mentioning_dli=int(gw["prog: dual language / immersion"].sum()),
                       writers_mentioning_magnet=int(gw["prog: magnet / lottery"].sum())))
    pd.DataFrame(gr).to_csv(OUT / "mention_rates_by_group.csv", index=False)

    # --- console summary --------------------------------------------------------------------
    pd.set_option("display.width", 250, "display.max_columns", 60)
    print(f"respondents {len(d)}, writers {n_writers}, writers naming an elementary school "
          f"{int(d.any_elem_school.sum())}, any school {int(d.any_school.sum())}")
    print(d.n_elem_schools_mentioned.value_counts().sort_index().to_string())
    print("\n== detection variants"); print(variants.to_string(index=False))
    print("\n== school table (key cols)")
    print(table[["school", "closure_candidate", "is_dli", "adm_2024_25", "util_2024_25_pct", "util_2031_projected_pct",
                 "adm_change_2019_2025_pct", "eds_pct_2024_25", "srts_walk_pct", "mentions_total", "mentions_parent",
                 "mentions_non_parent", "mentions_english", "mentions_other_language", "mentions_per_100_adm",
                 "cooccur_close", "cooccur_keep_save_stay", "cooccur_walk", "cooccur_bus", "cooccur_dual_language"]]
          .to_string(index=False))
    print("\n== correlations"); print(corr.to_string(index=False))
    print("\n== theme co-occurrence, q<0.25 or top by p"); print(co[co.bh_q < 0.25].to_string(index=False))
    print(co.nsmallest(25, "fisher_p").to_string(index=False))
    print("\n== q9"); print(q9_out.to_string()); print(q9_test.to_string(index=False))
    print(pd.DataFrame(sl_rows).to_string(index=False))
    print("\n== ratings MW"); print(mwdf.sort_values(["family", "mw_p"]).to_string(index=False))
    print("\n== candidates vs emptiest"); print(comp.to_string(index=False))
    print("\n== spread"); print(spread.to_string(index=False))
    print("\n== transport"); print(transport.to_string(index=False))
    print("\n== groups"); print(pd.DataFrame(gr).to_string(index=False))


if __name__ == "__main__":
    main()
