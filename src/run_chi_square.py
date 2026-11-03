"""Run the pre-registered test in docs/analysis_plan.md.

Do current CHCCS parents and non-parents differ in which value theme they chose
as the one item to keep top of mind (Q9)?

Steps, all as specified in the analysis plan:
    1. 2 x 4 contingency table (group x theme), "Other" and blank answers excluded
    2. expected-count check (every cell >= 5); if it fails, use the planned exact
       alternative: a Monte Carlo exact p-value from permuting group labels
       (margins fixed), which estimates the exact conditional p-value
    3. Cramer's V with a 95% bootstrap CI (resampling within each group)
    4. post hoc adjusted standardized residuals, Bonferroni-corrected over 8 cells
    5. percentage choosing each theme by group with 95% Wilson CIs
    6. sensitivity power analysis with the final counts
    7. difference between groups in the share choosing Student Learning, with a
       95% Newcombe (Wilson-based) CI; descriptive, not an additional test

Outputs (data/final/): q9_contingency_table.csv, q9_test_results.csv,
q9_residuals.csv, q9_theme_percentages.csv; figure: figures/q9_theme_by_group.png
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, norm
from statsmodels.stats.power import GofChisquarePower
from statsmodels.stats.proportion import confint_proportions_2indep, proportion_confint

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "q9_value_themes.csv"
FINAL = ROOT / "data" / "final"
FIGURES = ROOT / "figures"

GROUPS = ["Parent", "Non-parent"]
THEMES = ["Student Learning", "Money & buildings", "Community", "Student logistics & well-being"]
ALPHA = 0.05
SEED = 510
N_PERMUTATIONS = 100_000
N_BOOTSTRAP = 10_000


def chi_square_stat(table):
    expected = table.sum(1, keepdims=True) * table.sum(0, keepdims=True) / table.sum()
    return ((table - expected) ** 2 / expected).sum()


def cramers_v(table):
    n = table.sum()
    k = min(table.shape)
    return np.sqrt(chi_square_stat(table) / (n * (k - 1)))


def tabulate(group_codes, theme_codes):
    return np.bincount(group_codes * len(THEMES) + theme_codes,
                       minlength=len(GROUPS) * len(THEMES)).reshape(len(GROUPS), len(THEMES))


def monte_carlo_p(group_codes, theme_codes, observed_stat, rng):
    """Share of label permutations with a chi-square statistic at least as large as observed."""
    hits = 0
    labels = group_codes.copy()
    for _ in range(N_PERMUTATIONS):
        rng.shuffle(labels)
        if chi_square_stat(tabulate(labels, theme_codes)) >= observed_stat - 1e-12:
            hits += 1
    return (hits + 1) / (N_PERMUTATIONS + 1)


def bootstrap_v(group_codes, theme_codes, rng):
    """Percentile CI for Cramer's V, resampling respondents within each group."""
    idx_by_group = [np.flatnonzero(group_codes == g) for g in range(len(GROUPS))]
    values = np.empty(N_BOOTSTRAP)
    for b in range(N_BOOTSTRAP):
        sample = np.concatenate([rng.choice(idx, size=len(idx), replace=True) for idx in idx_by_group])
        values[b] = cramers_v(tabulate(group_codes[sample], theme_codes[sample]))
    return np.percentile(values, [2.5, 97.5])


def adjusted_residuals(table):
    n = table.sum()
    row = table.sum(1, keepdims=True) / n
    col = table.sum(0, keepdims=True) / n
    expected = row * col * n
    return (table - expected) / np.sqrt(expected * (1 - row) * (1 - col))


def plot(pct):
    blue, orange = "#2a78d6", "#eb6834"
    ink, muted, grid = "#0b0b0b", "#52514e", "#e1e0d9"
    fig, ax = plt.subplots(figsize=(10, 5.2), dpi=150)
    y = np.arange(len(THEMES))
    h = 0.36
    for offset, group, color in [(-h / 2, "Parent", blue), (h / 2, "Non-parent", orange)]:
        g = pct[pct.group == group].set_index("theme").loc[THEMES]
        err = np.vstack([g.percent - g.ci_low, g.ci_high - g.percent])
        ax.barh(y + offset, g.percent, height=h * 0.9, color=color,
                label=f"{group}s (n = {int(g.group_n.iloc[0]):,})")
        ax.errorbar(g.percent, y + offset, xerr=err, fmt="none", ecolor=muted, elinewidth=1, capsize=3)
        for yi, v, hi in zip(y + offset, g.percent, g.ci_high):
            ax.text(hi + 1.2, yi, f"{v:.0f}%", va="center", fontsize=9, color=ink)
    ax.set_yticks(y, THEMES, fontsize=10, color=ink)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.xaxis.grid(True, color=grid, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(grid)
    ax.tick_params(axis="x", colors=muted, labelsize=9)
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel("Percent choosing this theme as the one item to keep top of mind (Q9)", color=muted, fontsize=9)
    ax.legend(frameon=False, fontsize=9, loc="lower right")
    fig.suptitle("Top-priority value theme: current CHCCS parents vs. non-parents", x=0.01, ha="left",
                 fontsize=12, color=ink)
    fig.text(0.01, 0.01, "Error bars: 95% Wilson confidence intervals. Write-in and blank answers excluded.",
             fontsize=8, color=muted)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(FIGURES / "q9_theme_by_group.png")


def main():
    rng = np.random.default_rng(SEED)
    df = pd.read_csv(DATA)
    df = df[df.in_test]
    group_codes = df.group.map({g: i for i, g in enumerate(GROUPS)}).to_numpy()
    theme_codes = df.q9_theme.map({t: i for i, t in enumerate(THEMES)}).to_numpy()
    table = tabulate(group_codes, theme_codes)
    n = table.sum()

    # 1-2. Table, expected counts and the test the plan calls for
    stat, p_asymptotic, dof, expected = chi2_contingency(table, correction=False)
    min_expected = expected.min()
    use_exact = min_expected < 5
    if use_exact:
        p_value = monte_carlo_p(group_codes, theme_codes, stat, rng)
        test_used = f"Monte Carlo exact test (chi-square statistic, {N_PERMUTATIONS:,} permutations)"
    else:
        p_value = p_asymptotic
        test_used = "Chi-square test of independence"

    # 3. Effect size
    v = cramers_v(table)
    v_low, v_high = bootstrap_v(group_codes, theme_codes, rng)

    # 4. Post hoc residuals
    z = adjusted_residuals(table)
    z_crit = norm.ppf(1 - ALPHA / table.size / 2)

    # 5. Percentages with Wilson CIs
    pct_rows = []
    for gi, group in enumerate(GROUPS):
        group_n = table[gi].sum()
        for ti, theme in enumerate(THEMES):
            low, high = proportion_confint(table[gi, ti], group_n, alpha=ALPHA, method="wilson")
            pct_rows.append({"group": group, "group_n": group_n, "theme": theme, "count": table[gi, ti],
                             "percent": 100 * table[gi, ti] / group_n, "ci_low": 100 * low, "ci_high": 100 * high})
    pct = pd.DataFrame(pct_rows)

    # 6. Sensitivity power with final counts
    mde_w = float(np.atleast_1d(GofChisquarePower().solve_power(
        nobs=n, n_bins=len(THEMES), alpha=ALPHA, power=0.8))[0])

    # 7. Student Learning difference (parents minus non-parents) with a Newcombe CI
    learn = THEMES.index("Student Learning")
    diff = table[0, learn] / table[0].sum() - table[1, learn] / table[1].sum()
    diff_low, diff_high = confint_proportions_2indep(
        table[0, learn], table[0].sum(), table[1, learn], table[1].sum(),
        method="newcomb", compare="diff", alpha=ALPHA)

    # Save
    FINAL.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    counts = pd.DataFrame(table, index=GROUPS, columns=THEMES)
    exp = pd.DataFrame(expected, index=[f"{g} (expected)" for g in GROUPS], columns=THEMES)
    pd.concat([counts, exp.round(2)]).to_csv(FINAL / "q9_contingency_table.csv")
    results = pd.DataFrame([{
        "test_used": test_used, "n": n, "n_parent": table[0].sum(), "n_non_parent": table[1].sum(),
        "chi_square": round(stat, 3), "df": dof, "p_value": p_value,
        "p_value_asymptotic_chi_square": p_asymptotic, "min_expected_count": round(min_expected, 2),
        "cramers_v": round(v, 3), "cramers_v_ci_low": round(v_low, 3), "cramers_v_ci_high": round(v_high, 3),
        "alpha": ALPHA, "reject_h0": p_value < ALPHA, "min_detectable_v_80pct_power": round(mde_w, 3),
        "learning_diff_pct_points": round(100 * diff, 2), "learning_diff_ci_low": round(100 * diff_low, 2),
        "learning_diff_ci_high": round(100 * diff_high, 2), "seed": SEED,
    }])
    results.to_csv(FINAL / "q9_test_results.csv", index=False)
    resid = pd.DataFrame(z, index=GROUPS, columns=THEMES).round(2)
    resid.to_csv(FINAL / "q9_residuals.csv")
    pct.round(2).to_csv(FINAL / "q9_theme_percentages.csv", index=False)
    plot(pct)

    # Report
    pd.set_option("display.width", 200)
    print("Observed counts:\n", counts.to_string(), "\n")
    print("Expected counts:\n", pd.DataFrame(expected, index=GROUPS, columns=THEMES).round(1).to_string(), "\n")
    print(f"Minimum expected count: {min_expected:.2f} -> {'exact test (planned fallback)' if use_exact else 'chi-square OK'}")
    print(f"Test: {test_used}")
    print(f"Chi-square = {stat:.2f}, df = {dof}, p = {p_value:.4f} (asymptotic chi-square p = {p_asymptotic:.4f})")
    print(f"Cramer's V = {v:.3f}, 95% bootstrap CI [{v_low:.3f}, {v_high:.3f}]")
    print(f"Minimum detectable V at 80% power: {mde_w:.3f}")
    print(f"Student Learning, parents minus non-parents: {100 * diff:.1f} points, "
          f"95% Newcombe CI [{100 * diff_low:.1f}, {100 * diff_high:.1f}]")
    print(f"\nAdjusted standardized residuals (|z| > {z_crit:.2f} is significant after Bonferroni):\n", resid.to_string())
    print("\nPercent choosing each theme:\n",
          pct.pivot(index="theme", columns="group", values="percent").loc[THEMES, GROUPS].round(1).to_string())


if __name__ == "__main__":
    main()
