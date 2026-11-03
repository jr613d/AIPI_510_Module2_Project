"""01: Values by group, and the Board vs. survey respondents.

Run from the repo root:  python exploratory_analysis/01_values_and_board/run.py
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as c  # noqa: E402

FIG, RES = HERE / "figures", HERE / "results"


def board_vs_survey():
    df = pd.read_csv(c.HERE / "data" / "raw" / "full_report_board_vs_cpa_transcribed.csv")
    fig, axes = plt.subplots(1, 2, figsize=(13, 6.2), dpi=150)
    panels = [("value", "board_pct_top3", "cpa_pct_top3", "Values: % placing in their top three"),
              ("challenge", "board_pct_rated_4_5", "cpa_pct_rated_4_5", "Challenges: % rating 4 or 5 (of 5)")]
    for ax, (section, bcol, ccol, sub) in zip(axes, panels):
        d = df[df.section == section].assign(gap=lambda t: t[bcol] - t[ccol]).sort_values("gap", ascending=False)
        c.dumbbell(ax, d.item, [(d[bcol], "Board of Education (n = 7)", c.AQUA),
                                (d[ccol], "Survey respondents (n = 1,463)", c.NEUTRAL)], xmax=105)
        c.style(ax, "Percent")
        ax.set_title(sub, loc="left", fontsize=10.5, color=c.INK)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, frameon=False, fontsize=9.5, ncol=2, loc="upper right", bbox_to_anchor=(0.99, 0.985))
    c.finish(fig, "The Board weighs money and buildings far more heavily than survey respondents",
             "Descriptive. Source: CHCCS, Priorities & Values Conversations, Fall 2026 (Full Report), pp. 2 and 4. "
             "Sorted by Board-minus-survey gap. With 7 Board members, one member = 14 points.",
             FIG / "board_vs_survey.png")


def values_q9(df):
    d = df[df.group.isin(["Parent", "Non-parent"]) & df.q9_theme.isin(c.THEMES)]
    pct = (pd.crosstab(d.q9_value, d.group, normalize="columns") * 100)[["Parent", "Non-parent"]]
    n = pd.crosstab(d.q9_value, d.group)[["Parent", "Non-parent"]]
    pct = pct.sort_values("Parent", ascending=False)
    pct.round(1).join(n.add_suffix("_n")).to_csv(RES / "values_by_group_q9.csv")
    fig, ax = plt.subplots(figsize=(10, 6.4), dpi=150)
    c.dumbbell(ax, [c.short(v) for v in pct.index],
               [(pct.Parent, f"Parents (n = {n.Parent.sum():,})", c.BLUE),
                (pct["Non-parent"], f"Non-parents (n = {n['Non-parent'].sum():,})", c.ORANGE)], xmax=62)
    for yi, (p, q) in enumerate(zip(pct.Parent, pct["Non-parent"])):
        ax.text(max(p, q) + 1.5, yi, f"{p:.0f}% vs {q:.0f}%", va="center", fontsize=8, color=c.MUTED)
    c.style(ax, "Percent choosing this value as the single top priority (Q9)")
    ax.legend(frameon=False, fontsize=9, loc="lower right")
    c.finish(fig, "Educational excellence drives the Learning gap",
             "Descriptive; individual values are too sparse to test. Several non-parent percentages rest on fewer "
             "than 5 people.", FIG / "values_by_group_q9.png")


def value_ratings_q5(df):
    d = df[df.group.isin(["Parent", "Non-parent"])]
    cols = c.value_cols(d)
    pct = pd.DataFrame({g: {col[3:]: (d.loc[d.group == g, col].dropna() >= 4).mean() * 100 for col in cols}
                        for g in ["Parent", "Non-parent"]}).sort_values("Parent", ascending=False)
    pct.round(1).to_csv(RES / "value_ratings_by_group_q5.csv")
    ns = {g: int(d.loc[d.group == g, cols].notna().any(axis=1).sum()) for g in ["Parent", "Non-parent"]}
    fig, ax = plt.subplots(figsize=(10, 6.4), dpi=150)
    c.dumbbell(ax, [c.short(v) for v in pct.index],
               [(pct.Parent, f"Parents (n = {ns['Parent']:,})", c.BLUE),
                (pct["Non-parent"], f"Non-parents (n = {ns['Non-parent']:,})", c.ORANGE)], xmax=105)
    c.style(ax, "Percent rating this value 4 or 5 out of 5 (Q5)")
    ax.legend(frameon=False, fontsize=9, loc="lower left")
    c.finish(fig, "Rating every value, non-parents score buildings, balance and finances much higher",
             "Exploratory (not part of the pre-registered test). Q5 rates every value 1-5, so it shows breadth of "
             "support that Q9's single choice hides.", FIG / "value_ratings_by_group_q5.png")


def main():
    RES.mkdir(exist_ok=True)
    df = c.load_responses()
    board_vs_survey()
    values_q9(df)
    value_ratings_q5(df)
    print("01 done")


if __name__ == "__main__":
    main()
