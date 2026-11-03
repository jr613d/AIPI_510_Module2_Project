"""03: Parents who work for CHCCS vs. other parents vs. non-parent staff.

The main result compares parents with non-parents, but 87 of the 98 non-parents work for
CHCCS, so "parent" and "staff" are confounded. Comparing parents who also work for CHCCS
with other parents holds parenthood constant. If parent-staff look like other parents, the
main gap is about being a parent; if they look like non-parent staff, it's about the job.

Exploratory. Run from the repo root:  python exploratory_analysis/03_parent_staff/run.py
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as c  # noqa: E402

FIG, RES = HERE / "figures", HERE / "results"
GROUPS = ["Other parents", "Parents who work for CHCCS", "Non-parent CHCCS staff"]
COLORS = [c.BLUE, c.AQUA, c.ORANGE]


def assign(df):
    g = pd.Series(pd.NA, index=df.index, dtype="object")
    g[(df.group == "Parent") & ~df.employee] = GROUPS[0]
    g[(df.group == "Parent") & df.employee] = GROUPS[1]
    g[(df.group == "Non-parent") & df.employee] = GROUPS[2]
    return df.assign(sub=g).dropna(subset=["sub"])


def themes(d):
    d = d[d.q9_theme.isin(c.THEMES)]
    pct = (pd.crosstab(d.q9_theme, d["sub"], normalize="columns") * 100).loc[c.THEMES, GROUPS]
    n = d["sub"].value_counts().reindex(GROUPS)
    tests = []
    for a, b in [(GROUPS[1], GROUPS[0]), (GROUPS[1], GROUPS[2])]:
        s = d[d["sub"].isin([a, b])]
        stat, p = c.monte_carlo_chi2(s["sub"], s.q9_theme)
        tests.append({"comparison": f"{a} vs. {b}", "n": len(s), "chi_square": round(stat, 2),
                      "p_monte_carlo": round(p, 4),
                      "cramers_v": round(c.cramers_v(pd.crosstab(s["sub"], s.q9_theme)), 3)})
    return pct, n, pd.DataFrame(tests)


def ratings(d, cols):
    return pd.DataFrame({g: {col[3:]: (d.loc[d["sub"] == g, col].dropna() >= 4).mean() * 100 for col in cols}
                         for g in GROUPS})


def plot_themes(pct, n, tests):
    fig, ax = plt.subplots(figsize=(10, 5.6), dpi=150)
    c.grouped_bars(ax, c.THEMES, [(pct[g].values, f"{g} (n = {n[g]:,})", col) for g, col in zip(GROUPS, COLORS)],
                   xmax=85)
    c.style(ax, "Percent choosing this theme as the single top priority (Q9)")
    ax.legend(frameon=False, fontsize=9, loc="lower right")
    t = tests.set_index("comparison")
    note = ("Exploratory. Monte Carlo chi-square, parent-staff vs. other parents: p = "
            f"{t.iloc[0].p_monte_carlo:.3f}, V = {t.iloc[0].cramers_v:.2f}; vs. non-parent staff: p = "
            f"{t.iloc[1].p_monte_carlo:.3f}, V = {t.iloc[1].cramers_v:.2f}. Groups this small (76 and 83) give wide uncertainty.")
    c.finish(fig, "Parents who work for CHCCS: closer to other parents, or to staff?", note,
             FIG / "parent_staff_q9_themes.png")


def plot_ratings(r, n, title, xlabel, name):
    r = r.sort_values(GROUPS[0], ascending=False)
    fig, ax = plt.subplots(figsize=(11, 7.0), dpi=150)
    c.dumbbell(ax, [c.short(x) for x in r.index],
               [(r[g], f"{g} (n = {n[g]:,})", col) for g, col in zip(GROUPS, COLORS)], xmax=105)
    c.style(ax, xlabel)
    h, l = ax.get_legend_handles_labels()
    fig.legend(h, l, frameon=False, fontsize=9, ncol=3, loc="upper right", bbox_to_anchor=(0.99, 0.95))
    c.finish(fig, title, "Exploratory; not tested item by item.", FIG / name)


def main():
    RES.mkdir(exist_ok=True)
    d = assign(c.load_responses())
    n_all = d["sub"].value_counts().reindex(GROUPS)
    pct, n, tests = themes(d)
    pct.round(1).to_csv(RES / "q9_themes_by_subgroup.csv")
    tests.to_csv(RES / "q9_theme_tests.csv", index=False)
    rv = ratings(d, c.value_cols(d)); rv.round(1).to_csv(RES / "q5_values_pct_4_5_by_subgroup.csv")
    rc = ratings(d, c.challenge_cols(d)); rc.round(1).to_csv(RES / "q3_challenges_pct_4_5_by_subgroup.csv")
    plot_themes(pct, n, tests)
    plot_ratings(rv, n_all, "Value ratings: where do parents who work for CHCCS fall?",
                 "Percent rating this value 4 or 5 out of 5 (Q5)", "parent_staff_value_ratings.png")
    plot_ratings(rc, n_all, "Challenge ratings: where do parents who work for CHCCS fall?",
                 "Percent rating this challenge 4 or 5 out of 5 (Q3)", "parent_staff_challenge_ratings.png")
    print(pct.round(1).to_string(), "\n", n.to_dict(), "\n", tests.to_string(index=False))
    # Where parent-staff sit between the two reference groups (0 = like other parents, 1 = like non-parent staff)
    for name, r in [("values", rv), ("challenges", rc)]:
        gap = r[GROUPS[2]] - r[GROUPS[0]]
        big = gap.abs() >= 10
        pos = ((r[GROUPS[1]] - r[GROUPS[0]]) / gap)[big]
        print(f"{name}: items with >=10-pt parent/staff gap: {int(big.sum())}; median position of parent-staff = {np.median(pos):.2f}")
        print(r.loc[big].round(1).to_string())


if __name__ == "__main__":
    main()
