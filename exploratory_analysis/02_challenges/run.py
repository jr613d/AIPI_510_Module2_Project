"""02: Challenges by group (Q3 ratings and Q7 top three), parents vs. non-parents.

Exploratory. Per-item tests use Benjamini-Hochberg correction across the 13 items in each panel.
Run from the repo root:  python exploratory_analysis/02_challenges/run.py
"""
import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import fisher_exact, mannwhitneyu
from statsmodels.stats.multitest import multipletests

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as c  # noqa: E402

FIG, RES = HERE / "figures", HERE / "results"

# Distinctive phrase for each Q7 option (matched as substrings; one option itself contains a comma).
Q7_KEYS = {
    "Cost of maintaining aging buildings": "aging buildings",
    "School buildings meeting safety codes": "safety codes",
    "Length of commute for students riding buses": "length of commute",
    "Retaining highly effective employees": "retaining highly effective",
    "Partially empty school buildings": "partially empty",
    "Overcrowded school buildings": "overcrowded school",
    "The number of trailers / mobile classrooms": "trailers",
    "Current school buildings do not fit the modern academic program": "modern academic",
    "Current school buildings do not fit the modern operational expectations": "modern operational",
    "Unequal access to specialty programs": "unequal access",
    "Classroom technology updates": "technology updates",
    "Appeal of the district to current and prospective students": "appeal of the district",
    "Student populations have shifted, but school boundaries have not been adjusted to accommodate those changes":
        "boundaries have not",
}


def q3(d):
    rows = []
    for col in c.challenge_cols(d):
        p = d.loc[d.group == "Parent", col].dropna()
        n = d.loc[d.group == "Non-parent", col].dropna()
        u, pval = mannwhitneyu(p, n, alternative="two-sided")
        rows.append({"challenge": col[3:], "parent_pct_4_5": (p >= 4).mean() * 100,
                     "non_parent_pct_4_5": (n >= 4).mean() * 100, "parent_n": len(p), "non_parent_n": len(n),
                     "rank_biserial_pos_nonparents_higher": 1 - 2 * u / (len(p) * len(n)), "p_mannwhitney": pval})
    out = pd.DataFrame(rows)
    out["q_bh"] = multipletests(out.p_mannwhitney, method="fdr_bh")[1]
    return out


def q7(d):
    d = d[d.top3_challenges.fillna("").str.strip() != ""]
    text = d.top3_challenges.fillna("").str.lower()
    rows = []
    for label, key in Q7_KEYS.items():
        chosen = text.str.contains(re.escape(key))
        a = int((chosen & (d.group == "Parent")).sum()); np_ = int((d.group == "Parent").sum())
        b = int((chosen & (d.group == "Non-parent")).sum()); nn = int((d.group == "Non-parent").sum())
        pval = fisher_exact([[a, np_ - a], [b, nn - b]])[1]
        rows.append({"challenge": label, "parent_pct_top3": 100 * a / np_, "non_parent_pct_top3": 100 * b / nn,
                     "parent_n": np_, "non_parent_n": nn, "p_fisher": pval})
    out = pd.DataFrame(rows)
    out["q_bh"] = multipletests(out.p_fisher, method="fdr_bh")[1]
    return out


def plot(r3, r7):
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 6.6), dpi=150)
    for ax, df, pc, nc, xlabel, sub in [
        (axes[0], r3, "parent_pct_4_5", "non_parent_pct_4_5", "Percent rating 4 or 5 (of 5)", "Q3 ratings"),
        (axes[1], r7, "parent_pct_top3", "non_parent_pct_top3", "Percent placing in their top three", "Q7 top three"),
    ]:
        df = df.sort_values(pc, ascending=False)
        labels = [c.short(x) + (" *" if q < 0.05 else "") for x, q in zip(df.challenge, df.q_bh)]
        c.dumbbell(ax, labels, [(df[pc], f"Parents (n = {int(df.parent_n.max()):,})", c.BLUE),
                                (df[nc], f"Non-parents (n = {int(df.non_parent_n.max()):,})", c.ORANGE)], xmax=105)
        c.style(ax, xlabel)
        ax.set_title(sub, loc="left", fontsize=10.5, color=c.INK)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, frameon=False, fontsize=9.5, ncol=2, loc="upper right", bbox_to_anchor=(0.99, 0.985))
    c.finish(fig, "Both groups put staff retention and building safety first; non-parents weigh boundaries and buildings more",
             "Exploratory. * Benjamini-Hochberg q < 0.05 across the 13 items in that panel (Mann-Whitney U for ratings, "
             "Fisher's exact for top three). Not part of the pre-registered test.", FIG / "challenges_by_group.png")


def main():
    RES.mkdir(exist_ok=True)
    df = c.load_responses()
    d = df[df.group.isin(["Parent", "Non-parent"])]
    r3, r7 = q3(d), q7(d)
    r3.round(4).to_csv(RES / "challenge_ratings_q3_by_group.csv", index=False)
    r7.round(4).to_csv(RES / "challenge_top3_q7_by_group.csv", index=False)
    plot(r3, r7)
    pd.set_option("display.width", 220)
    print(r3[["challenge", "parent_pct_4_5", "non_parent_pct_4_5", "rank_biserial_pos_nonparents_higher", "q_bh"]].round(3).to_string(index=False))
    print(r7[["challenge", "parent_pct_top3", "non_parent_pct_top3", "q_bh"]].round(3).to_string(index=False))
    allr = df[df.top3_challenges.fillna("").str.strip() != ""]
    print("Pooled Q7 % (check vs Full Report):",
          {k[:25]: round(100 * allr.top3_challenges.str.lower().str.contains(re.escape(v)).mean())
           for k, v in Q7_KEYS.items()})


if __name__ == "__main__":
    main()
