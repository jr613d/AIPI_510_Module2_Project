"""Additional figures of the pre-registered result (no new analysis).

Run after run_chi_square.py. Reads its outputs and writes:
    figures/q9_pooled_vs_groups.png   theme shares: all respondents pooled vs. parents vs. non-parents
    figures/q9_residuals_heatmap.png  post hoc adjusted standardized residuals
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "figures"
DATA = ROOT / "data" / "processed" / "q9_value_themes.csv"
RESIDUALS = ROOT / "data" / "final" / "q9_residuals.csv"

THEMES = ["Student Learning", "Money & buildings", "Community", "Student logistics & well-being"]
BLUE, ORANGE = "#2a78d6", "#eb6834"          # parents, non-parents (as in q9_theme_by_group.png)
INK, MUTED, GRID, ALL = "#0b0b0b", "#52514e", "#e1e0d9", "#52514e"
Z_CRIT = 2.73                                  # Bonferroni over 8 cells, from the analysis plan


def finish(fig, title, note, name):
    fig.suptitle(title, x=0.01, ha="left", fontsize=12, color=INK)
    fig.text(0.01, 0.01, note, fontsize=8, color=MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 0.97))
    fig.savefig(FIGURES / name)
    plt.close(fig)


def pooled_vs_groups():
    df = pd.read_csv(DATA)
    df = df[df.in_test]
    groups = [("All respondents, pooled", df, ALL),
              ("Parents", df[df.group == "Parent"], BLUE),
              ("Non-parents", df[df.group == "Non-parent"], ORANGE)]
    fig, ax = plt.subplots(figsize=(10, 5.4), dpi=150)
    y = np.arange(len(THEMES))
    h = 0.26
    for k, (name, sub, color) in enumerate(groups):
        share = sub.q9_theme.value_counts(normalize=True).reindex(THEMES).fillna(0) * 100
        off = (k - 1) * h
        ax.barh(y + off, share.values, height=h * 0.88, color=color, label=f"{name} (n = {len(sub):,})")
        for yi, v in zip(y + off, share.values):
            ax.text(v + 0.8, yi, f"{v:.0f}%", va="center", fontsize=8.5, color=INK)
    ax.set_yticks(y, THEMES)
    ax.invert_yaxis()
    ax.set_xlim(0, 85)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="x", colors=MUTED, labelsize=9)
    ax.tick_params(axis="y", length=0, labelsize=9.5, colors=INK)
    ax.set_xlabel("Percent choosing this theme as the single top priority (Q9)", color=MUTED, fontsize=9)
    ax.legend(frameon=False, fontsize=9, loc="lower right")
    finish(fig, "Pooled results look like the parents' results",
           "Analytic sample of the pre-registered test. Parents are 93% of it, so the pooled distribution nearly "
           "matches theirs.", "q9_pooled_vs_groups.png")


def residuals_heatmap():
    z = pd.read_csv(RESIDUALS, index_col=0).loc[["Parent", "Non-parent"], THEMES]
    cmap = LinearSegmentedColormap.from_list("div", ["#e34948", "#f0efec", "#2a78d6"])
    fig, ax = plt.subplots(figsize=(10, 3.6), dpi=150)
    ax.imshow(z.values, cmap=cmap, norm=TwoSlopeNorm(vmin=-5, vcenter=0, vmax=5), aspect="auto")
    for i in range(z.shape[0]):
        for j in range(z.shape[1]):
            v = z.values[i, j]
            sig = abs(v) > Z_CRIT
            ax.text(j, i, f"{v:+.2f}" + ("*" if sig else ""), ha="center", va="center",
                    fontsize=12, fontweight="bold" if sig else "normal", color=INK)
    ax.set_xticks(range(len(THEMES)), [t.replace(" & well-being", "\n& well-being") for t in THEMES],
                  fontsize=9.5, color=INK)
    ax.set_yticks([0, 1], ["Parents", "Non-parents"], fontsize=10, color=INK)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    finish(fig, "Only the Student Learning cells pass the post hoc cutoff",
           f"Adjusted standardized residuals from the pre-registered test. * |z| > {Z_CRIT} (Bonferroni over 8 cells). "
           "Blue = chosen more often than expected; red = less often.", "q9_residuals_heatmap.png")


def main():
    FIGURES.mkdir(exist_ok=True)
    pooled_vs_groups()
    residuals_heatmap()
    print("Saved figures/q9_pooled_vs_groups.png and figures/q9_residuals_heatmap.png")


if __name__ == "__main__":
    main()
