"""Count survey respondents by relationship (Q1) to plan comparison groups.

Reads ONLY the Q1 relationship file -- no rating columns -- so group sizes can be
examined before the analysis plan is committed.

Outputs:
    data/final/respondent_role_counts.csv      one row per Q1 option
    data/final/candidate_group_sizes.csv       candidate comparison groups + minimum detectable effects
    figures/respondents_by_role.png
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm
from statsmodels.stats.power import TTestIndPower

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "CHCCS_Respondent_Relationships.xls"
FINAL = ROOT / "data" / "final"
FIGURES = ROOT / "figures"

ROLES = {
    "student": "Current CHCCS student",
    "graduate": "CHCCS graduate",
    "parent": "Parent of current CHCCS student(s)",
    "parent_grad": "Parent of graduated CHCCS student(s)",
    "parent_not_chccs": "Parent of school-age children NOT attending CHCCS",
    "teacher": "Teacher in CHCCS",
    "admin": "Administrator in CHCCS",
    "staff": "Staff in CHCCS",
    "educator_elsewhere": "Teacher, administrator, or school staff who does NOT work in CHCCS",
    "county_official": "Orange County elected official or staff",
    "municipal_official": "Local municipal elected official or staff",
    "resident": "Orange County resident",
    "other": "Other (write-in)",
}

# Write-ins describing a child not yet in school (pre-specified keyword rule).
FUTURE_PARENT_PATTERN = r"future|prospective|expect|pregnan|pre-?school|pre-?k|next year|next fall|starting|incoming|will be"


def load():
    df = pd.read_excel(RAW, sheet_name="Participants")
    flags = pd.DataFrame({k: df[v].eq(1) for k, v in ROLES.items()})
    flags["employee"] = flags.teacher | flags.admin | flags.staff
    flags["english"] = df.source_sheet.eq("English")
    flags["future_parent"] = flags.other & df.other_text_english.fillna("").str.contains(
        FUTURE_PARENT_PATTERN, case=False, regex=True)
    return df, flags


def min_detectable_effect(n1, n2, alpha):
    """Smallest Cohen's d (and rank-biserial r) detectable at 80% power, two-sided,
    adjusting sample sizes for Mann-Whitney's ~95.5% efficiency relative to the t-test."""
    d = TTestIndPower().solve_power(nobs1=n1 * 0.955, ratio=n2 / n1, alpha=alpha,
                                    power=0.8, alternative="two-sided")
    d = float(np.atleast_1d(d)[0])
    return d, 2 * norm.cdf(d / np.sqrt(2)) - 1


def role_counts(flags):
    rows = []
    for key, label in ROLES.items():
        sel = flags[key]
        only = sel & (flags[list(ROLES)].sum(axis=1) == 1)
        rows.append({"role": label, "respondents": int(sel.sum()), "only_this_role": int(only.sum())})
    return pd.DataFrame(rows).sort_values("respondents", ascending=False)


def candidate_groups(flags):
    f = flags
    groups = [
        ("Current CHCCS parents vs. CHCCS employees (not current parents)", f.parent, f.employee & ~f.parent),
        ("Current CHCCS parents vs. everyone else", f.parent, ~f.parent),
        ("Current CHCCS parents vs. residents (not current parents)", f.parent, f.resident & ~f.parent),
        ("Current CHCCS parents vs. parents of children not in CHCCS only", f.parent & ~f.parent_not_chccs,
         f.parent_not_chccs & ~f.parent),
        ("Parents who are also CHCCS employees vs. other current parents", f.parent & f.employee,
         f.parent & ~f.employee),
        ("English-language vs. other-language respondents", f.english, ~f.english),
        ("Current CHCCS parents vs. future parents (write-ins)", f.parent, f.future_parent & ~f.parent),
    ]
    rows = []
    for name, a, b in groups:
        n1, n2 = int(a.sum()), int(b.sum())
        row = {"comparison": name, "group_a": n1, "group_b": n2}
        for alpha in (0.05, 0.0125):
            d, r = min_detectable_effect(n1, n2, alpha)
            row[f"mde_d_alpha_{alpha}"] = round(d, 2)
            row[f"mde_rank_biserial_alpha_{alpha}"] = round(r, 2)
        rows.append(row)
    return pd.DataFrame(rows)


def plot(counts, total):
    blue, ink, muted, grid = "#2a78d6", "#0b0b0b", "#52514e", "#e1e0d9"
    c = counts.sort_values("respondents")
    fig, ax = plt.subplots(figsize=(10, 6.2), dpi=150)
    y = np.arange(len(c))
    ax.barh(y, c.respondents, height=0.6, color=blue)
    for yi, (n, only) in zip(y, zip(c.respondents, c.only_this_role)):
        ax.text(n + 12, yi, f"{n:,}  ({only:,} only)", va="center", fontsize=9, color=ink)
    ax.set_yticks(y, [r.replace("school staff who", "school staff\nwho") for r in c.role], fontsize=9, color=ink)
    ax.set_xlim(0, c.respondents.max() * 1.25)
    ax.xaxis.grid(True, color=grid, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(grid)
    ax.tick_params(axis="x", colors=muted, labelsize=9)
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel("Respondents selecting this role", color=muted, fontsize=9)
    fig.suptitle(f"Respondents by relationship to CHCCS (n = {total:,} responses)",
                 x=0.01, ha="left", fontsize=12, color=ink)
    fig.text(0.01, 0.01, "Select-all-that-apply question, so roles overlap and bars sum to more than the total.",
             fontsize=8, color=muted)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(FIGURES / "respondents_by_role.png")


def main():
    FINAL.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    df, flags = load()
    counts = role_counts(flags)
    groups = candidate_groups(flags)
    counts.to_csv(FINAL / "respondent_role_counts.csv", index=False)
    groups.to_csv(FINAL / "candidate_group_sizes.csv", index=False)
    plot(counts, len(df))
    pd.set_option("display.width", 220)
    print(counts.to_string(index=False))
    print()
    print(groups.to_string(index=False))


if __name__ == "__main__":
    main()
