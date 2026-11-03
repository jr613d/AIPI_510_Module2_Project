"""06: Q9 value themes among parents by age, and by survey language.

Age (Q2) among current parents: 30-39 (mostly younger children), 40-49, and 50+. Parents under
30 are too few to analyze. Language: English vs. the seven other-language versions, all respondents.

Exploratory. Run from the repo root:  python exploratory_analysis/06_age_and_language/run.py
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as c  # noqa: E402

FIG, RES = HERE / "figures", HERE / "results"
AGE_GROUPS = {"30 to 39 years": "30-39", "40 to 49 years": "40-49", "50 to 64 years": "50+", "65+ years": "50+"}
AGE_ORDER = ["30-39", "40-49", "50+"]
AGE_COLORS = ["#6da7ec", "#2a78d6", "#104281"]   # one-hue ordinal ramp (light to dark = younger to older)


def theme_figure(d, col, order, colors, title, note, name, label_fmt):
    d = d[d.q9_theme.isin(c.THEMES)]
    pct = (pd.crosstab(d.q9_theme, d[col], normalize="columns") * 100).loc[c.THEMES, order]
    n = d[col].value_counts().reindex(order)
    stat, p = c.monte_carlo_chi2(d[col], d.q9_theme)
    v = c.cramers_v(pd.crosstab(d[col], d.q9_theme))
    fig, ax = plt.subplots(figsize=(10, 5.4), dpi=150)
    c.grouped_bars(ax, c.THEMES, [(pct[g].values, label_fmt(g, n[g]), colr) for g, colr in zip(order, colors)], xmax=85)
    c.style(ax, "Percent choosing this theme as the single top priority (Q9)")
    ax.legend(frameon=False, fontsize=9, loc="lower right")
    c.finish(fig, title, f"{note} Monte Carlo chi-square p {'< 0.001' if p < 0.001 else f'= {p:.3f}'}, Cramér's V = {v:.2f}.", FIG / name)
    return pct, n, {"chi_square": round(float(stat), 2), "p_monte_carlo": float(p), "cramers_v": round(float(v), 3), "n": int(n.sum())}


def main():
    RES.mkdir(exist_ok=True)
    df = c.load_responses()

    parents = df[df.group == "Parent"].copy()
    parents["age_group"] = parents.age.map(AGE_GROUPS)
    age_counts = parents.age.fillna("(blank)").replace("", "(blank)").value_counts()
    age_counts.to_csv(RES / "parent_age_counts.csv")
    pa = parents.dropna(subset=["age_group"])
    pct_age, n_age, t_age = theme_figure(
        pa, "age_group", AGE_ORDER, AGE_COLORS,
        "Among parents, top priorities by age",
        "Exploratory. Current CHCCS parents; under-30 parents (too few) excluded.",
        "parents_by_age_q9_themes.png", lambda g, n: f"Parents aged {g} (n = {n:,})")
    pct_age.round(1).to_csv(RES / "parents_by_age_q9_themes.csv")

    df["language"] = df.english.map({True: "English", False: "Other language"})
    pct_lang, n_lang, t_lang = theme_figure(
        df, "language", ["English", "Other language"], [c.NEUTRAL, c.AQUA],
        "Top priorities by survey language",
        "Exploratory. All respondents; the 7 other-language versions are pooled (Spanish is about half).",
        "language_q9_themes.png", lambda g, n: f"{g} (n = {n:,})")
    pct_lang.round(1).to_csv(RES / "language_q9_themes.csv")
    lang_detail = df[~df.english].source_sheet.value_counts()
    lang_detail.to_csv(RES / "other_language_counts.csv")

    pd.DataFrame([{"analysis": "parents by age", **t_age}, {"analysis": "language", **t_lang}]).to_csv(
        RES / "tests.csv", index=False)
    print(age_counts.to_string())
    print(pct_age.round(1).to_string(), "\n", t_age)
    print(pct_lang.round(1).to_string(), "\n", t_lang, "\n", lang_detail.to_dict())


if __name__ == "__main__":
    main()
