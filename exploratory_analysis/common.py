"""Shared data loading, groups and plotting style for the exploratory sub-analyses.

Every sub-analysis gets one row per survey response from load_responses(), built from
the raw CHCCS workbook with the same response IDs and group rules as the main project.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import openpyxl
import pandas as pd
from scipy.stats import chi2_contingency

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "src"))
from explore_respondent_groups import load as load_groups  # noqa: E402
from one_hot_encode_q1 import DEFAULT_INPUT, read_records  # noqa: E402

CACHE = HERE / "data" / "processed" / "responses_wide.csv"

THEMES = ["Student Learning", "Money & buildings", "Community", "Student logistics & well-being"]
CHALLENGE_COLS = range(2, 15)   # C-O: 13 challenge ratings
VALUE_COLS = range(16, 29)      # Q-AC: 13 value ratings
TEXT_COLS = {"age": 1, "other_challenges": 15, "other_values": 29, "top3_challenges": 30,
             "top3_values": 31, "additional_thoughts": 33}

# Colors: parents and non-parents match the main project's figures.
BLUE, ORANGE, AQUA, YELLOW, MAGENTA = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"
INK, MUTED, GRID, NEUTRAL = "#0b0b0b", "#52514e", "#e1e0d9", "#52514e"


def short(label):
    """Trim long survey labels for chart axes."""
    for a, b in [(" (quality & student outcomes)", ""), (" across all school sites", ""),
                 (" between home and school", ""), (" districtwide", ""),
                 ("Current school buildings do not fit the modern", "Buildings don't fit modern"),
                 ("Student populations have shifted, but school boundaries have not been adjusted to "
                  "accommodate those changes", "Boundaries not adjusted to population shifts"),
                 (" to current and prospective students", ""), (" (e.g.", " ("), (".", "")]:
        label = label.replace(a, b)
    return label.split(" (")[0] if len(label) > 55 else label


def _cell_text(sheets, record, col):
    sheet = sheets[record["source_sheet"]]
    original = sheet[record["source_row"] - 1][col]
    translated = sheet[record["translation_row"] - 1][col] if record["translation_row"] else None
    value = translated if translated not in (None, "") else original
    return "" if value is None else str(value).strip()


def load_responses(refresh=False):
    """One row per response: groups, age, all ratings, text answers and Q9 theme."""
    if CACHE.exists() and not refresh:
        return pd.read_csv(CACHE, keep_default_na=False, na_values=[""])
    records, _ = read_records(DEFAULT_INPUT)
    book = openpyxl.load_workbook(DEFAULT_INPUT, read_only=True, data_only=True)
    try:
        sheets = {s.title: list(s.values) for s in book}
    finally:
        book.close()
    header = sheets["English"][0]
    ch_names = [str(header[c]).replace("Challenge: ", "").rstrip(".") for c in CHALLENGE_COLS]
    val_names = [str(header[c]).replace("Value: ", "").rstrip(".") for c in VALUE_COLS]

    rows = []
    for r in records:
        orig = sheets[r["source_sheet"]][r["source_row"] - 1]
        row = {"participant_id": r["participant_id"], "source_sheet": r["source_sheet"]}
        for name, c in TEXT_COLS.items():
            row[name] = _cell_text(sheets, r, c)
        for name, c in zip(ch_names, CHALLENGE_COLS):
            row["C: " + name] = orig[c] if isinstance(orig[c], (int, float)) else np.nan
        for name, c in zip(val_names, VALUE_COLS):
            row["V: " + name] = orig[c] if isinstance(orig[c], (int, float)) else np.nan
        rows.append(row)
    df = pd.DataFrame(rows)

    q1, flags = load_groups()
    df["group"] = "Excluded"
    df.loc[flags.plan_parent.values, "group"] = "Parent"
    df.loc[flags.plan_non_parent.values, "group"] = "Non-parent"
    for col in ["parent", "employee", "english", "future_parent", "resident"]:
        df[col] = flags[col].values

    q9 = pd.read_csv(ROOT / "data" / "processed" / "q9_value_themes.csv")[["participant_id", "q9_value", "q9_theme"]]
    df = df.merge(q9, on="participant_id", how="left", validate="one_to_one")
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CACHE, index=False)
    return df


def challenge_cols(df):
    return [c for c in df.columns if c.startswith("C: ")]


def value_cols(df):
    return [c for c in df.columns if c.startswith("V: ")]


def cramers_v(table):
    table = np.asarray(table)
    chi2 = chi2_contingency(table, correction=False)[0]
    return np.sqrt(chi2 / (table.sum() * (min(table.shape) - 1)))


def monte_carlo_chi2(labels, outcome, n_perm=20_000, seed=510):
    """Exploratory permutation p-value for independence of two categorical arrays."""
    rng = np.random.default_rng(seed)
    labels = pd.Categorical(labels)
    outcome = pd.Categorical(outcome)
    lc, oc = labels.codes.copy(), outcome.codes
    k_l, k_o = len(labels.categories), len(outcome.categories)

    def stat(codes):
        t = np.bincount(codes * k_o + oc, minlength=k_l * k_o).reshape(k_l, k_o)
        e = t.sum(1, keepdims=True) * t.sum(0, keepdims=True) / t.sum()
        with np.errstate(divide="ignore", invalid="ignore"):
            return np.nansum((t - e) ** 2 / e)

    observed = stat(lc)
    hits = sum(stat(rng.permutation(lc)) >= observed - 1e-12 for _ in range(n_perm))
    return observed, (hits + 1) / (n_perm + 1)


# ------------------------------------------------------------------ plotting
def style(ax, xlabel):
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="x", colors=MUTED, labelsize=9)
    ax.tick_params(axis="y", length=0, labelsize=9.5, colors=INK)
    ax.set_xlabel(xlabel, color=MUTED, fontsize=9)


def finish(fig, title, note, path):
    fig.suptitle(title, x=0.01, ha="left", fontsize=12, color=INK)
    fig.text(0.01, 0.01, note, fontsize=8, color=MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 0.97))
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def dumbbell(ax, labels, series, xmax=100):
    """series: list of (values, label, color). Draws a connecting line across all series."""
    y = np.arange(len(labels))
    arr = np.vstack([np.asarray(v, dtype=float) for v, _, _ in series])
    for yi in range(len(labels)):
        ax.plot([np.nanmin(arr[:, yi]), np.nanmax(arr[:, yi])], [yi, yi], color=GRID, linewidth=3,
                zorder=1, solid_capstyle="round")
    for v, label, color in series:
        ax.scatter(v, y, s=70, color=color, zorder=3, label=label, edgecolors="white", linewidths=1.5)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlim(-2, xmax)


def grouped_bars(ax, categories, series, xmax=100, fmt="{:.0f}%"):
    """Horizontal grouped bars. series: list of (values, label, color)."""
    y = np.arange(len(categories))
    h = 0.8 / len(series)
    for k, (vals, label, color) in enumerate(series):
        off = (k - (len(series) - 1) / 2) * h
        ax.barh(y + off, vals, height=h * 0.88, color=color, label=label)
        for yi, v in zip(y + off, vals):
            ax.text(v + xmax * 0.01, yi, fmt.format(v), va="center", fontsize=8, color=INK)
    ax.set_yticks(y, categories)
    ax.invert_yaxis()
    ax.set_xlim(0, xmax)
