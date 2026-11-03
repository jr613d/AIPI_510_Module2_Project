"""Exploratory and descriptive figures, done after the Module 2 project's pre-registered test.

None of these are confirmatory tests; the only pre-registered test is in
src/run_chi_square.py. Each figure's footnote says what kind of evidence it is.
See exploratory_analysis/README.md.

Run from the repo root:  python exploratory_analysis/src/make_exploratory_figures.py

Reads (main project, read-only): data/processed/q9_value_themes.csv and the raw survey workbook.

Figures (exploratory_analysis/figures/):
    fig_a_board_vs_survey.png       Board vs. survey respondents (Full Report, pp. 2 and 4)
    fig_b_values_by_group.png       all 13 Q9 values by group
    fig_c_ratings_by_group.png      Q5: % rating each value 4-5, by group

Data written (exploratory_analysis/data/):
    processed/q5_value_ratings.csv
    final/exploratory_q9_values_by_group.csv
    final/exploratory_q5_ratings_by_group.csv
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from explore_respondent_groups import load as load_groups  # noqa: E402
from one_hot_encode_q1 import DEFAULT_INPUT, read_records  # noqa: E402

FIGURES = HERE / "figures"
PROCESSED = HERE / "data" / "processed"
FINAL = HERE / "data" / "final"
MAIN_PROCESSED = ROOT / "data" / "processed"

# Colors: parents and non-parents keep the same colors as Figure 1; "all respondents"
# is neutral ink; the Board takes the next categorical slot (aqua).
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, MUTED, GRID, ALL = "#0b0b0b", "#52514e", "#e1e0d9", "#52514e"
THEMES = ["Student Learning", "Money & buildings", "Community", "Student logistics & well-being"]
Q5_COLUMNS = range(16, 29)  # columns Q-AC: the 13 value ratings


def style(ax, xlabel):
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="x", colors=MUTED, labelsize=9)
    ax.tick_params(axis="y", length=0, labelsize=9.5, colors=INK)
    ax.set_xlabel(xlabel, color=MUTED, fontsize=9)


def finish(fig, title, note, name):
    fig.suptitle(title, x=0.01, ha="left", fontsize=12, color=INK)
    fig.text(0.01, 0.01, note, fontsize=8, color=MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 0.97))
    fig.savefig(FIGURES / name)
    plt.close(fig)


def dumbbell(ax, labels, a, b, a_label, b_label, a_color, b_color, xmax=100):
    y = np.arange(len(labels))
    for yi, va, vb in zip(y, a, b):
        ax.plot([va, vb], [yi, yi], color=GRID, linewidth=3, zorder=1, solid_capstyle="round")
    ax.scatter(a, y, s=70, color=a_color, zorder=3, label=a_label, edgecolors="white", linewidths=1.5)
    ax.scatter(b, y, s=70, color=b_color, zorder=3, label=b_label, edgecolors="white", linewidths=1.5)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlim(-2, xmax)


# ----------------------------------------------------------------- A
def fig_a():
    df = pd.read_csv(HERE / "data" / "raw" / "full_report_board_vs_cpa_transcribed.csv")
    fig, axes = plt.subplots(1, 2, figsize=(13, 6.2), dpi=150)
    panels = [
        ("value", "board_pct_top3", "cpa_pct_top3", "Values: % placing in their top three"),
        ("challenge", "board_pct_rated_4_5", "cpa_pct_rated_4_5", "Challenges: % rating 4 or 5 (of 5)"),
    ]
    for ax, (section, bcol, ccol, sub) in zip(axes, panels):
        d = df[df.section == section].assign(gap=lambda t: t[bcol] - t[ccol]).sort_values("gap", ascending=False)
        dumbbell(ax, d.item, d[bcol], d[ccol], "Board of Education (n = 7)", "Survey respondents (n = 1,463)",
                 AQUA, ALL, xmax=105)
        style(ax, "Percent")
        ax.set_title(sub, loc="left", fontsize=10.5, color=INK)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, frameon=False, fontsize=9.5, ncol=2, loc="upper right", bbox_to_anchor=(0.99, 0.985))
    finish(fig, "The Board weighs money and buildings far more heavily than survey respondents",
           "Descriptive. Source: CHCCS, Priorities & Values Conversations, Fall 2026 (Full Report), pp. 2 and 4. "
           "Sorted by Board-minus-survey gap. With 7 Board members, one member = 14 points.",
           "fig_a_board_vs_survey.png")


# ----------------------------------------------------------------- B: all 13 Q9 values
def q9():
    df = pd.read_csv(MAIN_PROCESSED / "q9_value_themes.csv")
    return df[df.in_test]


def fig_b(df):
    t = (pd.crosstab(df.q9_value, df.group, normalize="columns") * 100)[["Parent", "Non-parent"]]
    counts = pd.crosstab(df.q9_value, df.group)[["Parent", "Non-parent"]]
    t = t.sort_values("Parent", ascending=False)
    out = t.round(1).join(counts.add_suffix("_n"))
    out.to_csv(FINAL / "exploratory_q9_values_by_group.csv")
    labels = [v.replace(" (quality & student outcomes)", "").replace(" across all school sites", "")
              .replace(" between home and school", "") for v in t.index]
    fig, ax = plt.subplots(figsize=(10, 6.4), dpi=150)
    dumbbell(ax, labels, t.Parent, t["Non-parent"],
             f"Parents (n = {counts.Parent.sum():,})", f"Non-parents (n = {counts['Non-parent'].sum():,})",
             BLUE, ORANGE, xmax=62)
    for yi, (p, q) in enumerate(zip(t.Parent, t["Non-parent"])):
        ax.text(max(p, q) + 1.5, yi, f"{p:.0f}% vs {q:.0f}%", va="center", fontsize=8, color=MUTED)
    style(ax, "Percent choosing this value as the single top priority (Q9)")
    ax.legend(frameon=False, fontsize=9, loc="lower right")
    finish(fig, "Educational excellence drives the Learning gap",
           "Descriptive; individual values are too sparse to test. Several non-parent percentages rest on fewer "
           "than 5 people.", "fig_b_values_by_group.png")


# ----------------------------------------------------------------- C: Q5 ratings
def q5_ratings():
    records, _ = read_records(DEFAULT_INPUT)
    book = openpyxl.load_workbook(DEFAULT_INPUT, read_only=True, data_only=True)
    try:
        sheets = {s.title: list(s.values) for s in book}
    finally:
        book.close()
    header = sheets["English"][0]
    values = [str(header[c]).replace("Value: ", "").rstrip(".") for c in Q5_COLUMNS]
    rows = []
    for r in records:
        row = sheets[r["source_sheet"]][r["source_row"] - 1]
        rows.append([r["participant_id"]] + [row[c] if isinstance(row[c], (int, float)) else np.nan for c in Q5_COLUMNS])
    q5 = pd.DataFrame(rows, columns=["participant_id"] + values)
    q1, flags = load_groups()
    group = pd.Series("Excluded", index=q1.index)
    group[flags.plan_parent.values] = "Parent"
    group[flags.plan_non_parent.values] = "Non-parent"
    q5 = q5.merge(pd.DataFrame({"participant_id": q1.participant_id, "group": group}), on="participant_id",
                  validate="one_to_one")
    q5.to_csv(PROCESSED / "q5_value_ratings.csv", index=False)
    return q5, values


def fig_c():
    q5, values = q5_ratings()
    q5 = q5[q5.group.isin(["Parent", "Non-parent"])]
    out = pd.DataFrame({g: {v: (q5.loc[q5.group == g, v].dropna() >= 4).mean() * 100 for v in values}
                        for g in ["Parent", "Non-parent"]})
    ns = {g: int(q5.loc[q5.group == g, values].notna().any(axis=1).sum()) for g in ["Parent", "Non-parent"]}
    out = out.sort_values("Parent", ascending=False)
    out.round(1).to_csv(FINAL / "exploratory_q5_ratings_by_group.csv")
    labels = [v.replace(" (quality & student outcomes)", "").replace(" across all school sites", "")
              .replace(" between home and school", "").replace(" districtwide", "") for v in out.index]
    fig, ax = plt.subplots(figsize=(10, 6.4), dpi=150)
    dumbbell(ax, labels, out.Parent, out["Non-parent"], f"Parents (n = {ns['Parent']:,})",
             f"Non-parents (n = {ns['Non-parent']:,})", BLUE, ORANGE, xmax=105)
    style(ax, "Percent rating this value 4 or 5 out of 5 (Q5)")
    ax.legend(frameon=False, fontsize=9, loc="lower left")
    finish(fig, "Rating every value, non-parents score buildings, balance and finances much higher",
           "Exploratory (not part of the pre-registered test). Q5 rates every value 1-5, so it shows breadth of "
           "support that Q9's single choice hides.", "fig_c_ratings_by_group.png")
    return out


def main():
    for d in (FIGURES, PROCESSED, FINAL):
        d.mkdir(parents=True, exist_ok=True)
    fig_a()
    df = q9()
    fig_b(df)
    d = fig_c()
    print("Q5 % rating 4-5 by group:\n", d.round(1).to_string())


if __name__ == "__main__":
    main()
