"""05: Rating patterns and survey quality.

How often did respondents rate nearly everything 5 ("ceiling") or give every item the same
rating ("straight-lining")? Both compress differences between groups and connect to respondents'
complaints that the survey was confusing. Also checks whether these respondents chose differently
on Q9.

Exploratory. Run from the repo root:  python exploratory_analysis/05_rating_patterns/run.py
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as c  # noqa: E402

FIG, RES = HERE / "figures", HERE / "results"


def patterns(df, cols, prefix):
    r = df[cols]
    answered = r.notna().sum(axis=1)
    complete = answered == len(cols)
    return pd.DataFrame({
        f"{prefix}_answered": answered,
        f"{prefix}_n5": (r == 5).sum(axis=1),
        f"{prefix}_mean": r.mean(axis=1),
        f"{prefix}_straightline": complete & (r.nunique(axis=1) == 1),
        f"{prefix}_all5": complete & (r == 5).all(axis=1),
    })


def main():
    RES.mkdir(exist_ok=True)
    df = c.load_responses()
    p = pd.concat([df[["participant_id", "group", "q9_theme"]],
                   patterns(df, c.value_cols(df), "values"), patterns(df, c.challenge_cols(df), "challenges")], axis=1)
    p.drop(columns=["q9_theme"]).to_csv(RES / "rating_patterns_by_response.csv", index=False)

    rows = []
    for name, g in [("All responses", p), ("Parents", p[p.group == "Parent"]), ("Non-parents", p[p.group == "Non-parent"])]:
        for prefix in ["values", "challenges"]:
            done = g[g[f"{prefix}_answered"] == 13]
            rows.append({"group": name, "grid": prefix, "complete_grids": len(done),
                         "pct_all_same": 100 * done[f"{prefix}_straightline"].mean(),
                         "pct_all_5": 100 * done[f"{prefix}_all5"].mean(),
                         "pct_10plus_5s": 100 * (done[f"{prefix}_n5"] >= 10).mean(),
                         "median_5s": done[f"{prefix}_n5"].median(),
                         "mean_rating": done[f"{prefix}_mean"].mean()})
    summary = pd.DataFrame(rows)
    summary.round(2).to_csv(RES / "rating_pattern_summary.csv", index=False)

    d = p[p.group.isin(["Parent", "Non-parent"]) & (p.values_answered == 13)]
    u, pval = mannwhitneyu(d.loc[d.group == "Parent", "values_n5"], d.loc[d.group == "Non-parent", "values_n5"])

    # Do heavy-5 raters choose differently on Q9? (all respondents with a theme)
    t = p[p.q9_theme.isin(c.THEMES) & (p.values_answered == 13)].copy()
    t["rater"] = np.where(t.values_n5 >= 10, "Rated 10+ values a 5", "Rated fewer than 10 a 5")
    q9_by_rater = (pd.crosstab(t.q9_theme, t.rater, normalize="columns") * 100).loc[c.THEMES]
    q9_by_rater.round(1).to_csv(RES / "q9_theme_by_rating_style.csv")
    stat, p_rater = c.monte_carlo_chi2(t.rater, t.q9_theme)

    fig, ax = plt.subplots(figsize=(10, 5.2), dpi=150)
    bins = np.arange(0, 14)
    width = 0.4
    for k, (g, col) in enumerate([("Parent", c.BLUE), ("Non-parent", c.ORANGE)]):
        s = d.loc[d.group == g, "values_n5"]
        share = s.value_counts(normalize=True).reindex(bins, fill_value=0) * 100
        ax.bar(bins + (k - 0.5) * width, share.values, width=width * 0.9, color=col,
               label=f"{'Parents' if g == 'Parent' else 'Non-parents'} (n = {len(s):,}; median {s.median():g})")
    ax.set_xticks(bins)
    ax.yaxis.grid(True, color=c.GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(c.GRID)
    ax.tick_params(colors=c.MUTED, labelsize=9)
    ax.set_xlabel("Number of the 13 values rated 5 (highest priority)", color=c.MUTED, fontsize=9)
    ax.set_ylabel("Percent of respondents", color=c.MUTED, fontsize=9)
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    allv = summary[(summary.group == "All responses") & (summary.grid == "values")].iloc[0]
    c.finish(fig, "Non-parents give more 5s overall, so part of their higher ratings may be rating style",
             f"Exploratory. All responses: {allv.pct_all_5:.1f}% rated all 13 values a 5; {allv.pct_10plus_5s:.0f}% rated 10 or more a 5. "
             f"Parents vs. non-parents, number of 5s: Mann-Whitney p {'< 0.001' if pval < 0.001 else f'= {pval:.3f}'}.",
             FIG / "values_rated_5.png")

    pd.set_option("display.width", 200)
    print(summary.round(1).to_string(index=False))
    print(f"MWU number of 5s parents vs non-parents: p={pval:.4f}")
    print(q9_by_rater.round(1).to_string(), f"\nMonte Carlo p={p_rater:.4f}, n={len(t)}")


if __name__ == "__main__":
    main()
