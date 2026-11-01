"""Prepare Q9 ("one item to keep top of mind") for the pre-registered chi-square test.

Reads the raw CHCCS workbook, takes each response's Q9 answer (column AG, using
the provided English translation for non-English tabs), maps it to one of the 13
values and then to the four themes fixed in docs/analysis_plan.md, and joins the
parent / non-parent groups built from Q1.

Output:
    data/processed/q9_value_themes.csv   one row per response
"""
import re
import sys
from pathlib import Path

import openpyxl
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from explore_respondent_groups import load as load_groups  # noqa: E402
from one_hot_encode_q1 import DEFAULT_INPUT, read_records  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "processed" / "q9_value_themes.csv"
Q9_COLUMN = 32  # column AG, 0-based

# Theme mapping, exactly as committed in docs/analysis_plan.md.
THEMES = {
    "Student Learning": [
        "Educational excellence (quality & student outcomes)",
        "Student-centered focus",
    ],
    "Money & buildings": [
        "Fiscal responsibility",
        "Maximizing the use of currently available buildings",
        "Long-term planning",
        "Increasing the use of renewable energy districtwide",
    ],
    "Community": [
        "Community engagement & trust building",
        "Collaboration between schools and county leadership",
        "Community partnerships",
    ],
    "Student logistics & well-being": [
        "Minimizing the distance students travel between home and school",
        "School safety",
        "High quality school meal service",
        "Ensuring well-balanced student populations across all school sites",
    ],
}
VALUE_TO_THEME = {value: theme for theme, values in THEMES.items() for value in values}

# Spanish answers that have no English translation row in the workbook.
UNTRANSLATED = {
    "enfoque centrado en los estudiantes": "Student-centered focus",
    "garantizar una distribución equilibrada de la población estudiantil en todas las escuelas":
        "Ensuring well-balanced student populations across all school sites",
}


def normalize(text):
    """Lower-case and fix the wording variants recorded in the source workbook."""
    t = re.sub(r"\s+", " ", str(text or "")).strip().rstrip(".").lower()
    t = t.replace("saftey", "safety")
    t = t.replace("minimize the distance student travel", "minimizing the distance students travel")
    t = re.sub(r"^maximize\b", "maximizing", t)
    t = re.sub(r"^minimize\b", "minimizing", t)
    return t


LOOKUP = {normalize(v): v for v in VALUE_TO_THEME}
LOOKUP.update(UNTRANSLATED)


def classify(text):
    """Return (value, theme). Blank -> Missing; unrecognized write-in -> Other."""
    key = normalize(text)
    if not key:
        return "", "Missing"
    value = LOOKUP.get(key)
    return (value, VALUE_TO_THEME[value]) if value else ("Other (write-in)", "Other")


def read_q9():
    records, _ = read_records(DEFAULT_INPUT)
    book = openpyxl.load_workbook(DEFAULT_INPUT, read_only=True, data_only=True)
    try:
        sheets = {sheet.title: list(sheet.values) for sheet in book}
    finally:
        book.close()
    rows = []
    for r in records:
        sheet = sheets[r["source_sheet"]]
        original = sheet[r["source_row"] - 1][Q9_COLUMN]
        translated = sheet[r["translation_row"] - 1][Q9_COLUMN] if r["translation_row"] else None
        english = translated if translated not in (None, "") else original
        value, theme = classify(english)
        rows.append({
            "participant_id": r["participant_id"],
            "source_sheet": r["source_sheet"],
            "source_row": r["source_row"],
            "q9_original": original or "",
            "q9_english": english or "",
            "q9_value": value,
            "q9_theme": theme,
        })
    return pd.DataFrame(rows)


def main():
    q9 = read_q9()
    q1, flags = load_groups()
    groups = pd.DataFrame({
        "participant_id": q1.participant_id,
        "q1_source_sheet": q1.source_sheet,
        "q1_source_row": q1.source_row,
        "group": "Excluded",
    })
    groups.loc[flags.plan_parent.values, "group"] = "Parent"
    groups.loc[flags.plan_non_parent.values, "group"] = "Non-parent"

    df = q9.merge(groups, on="participant_id", how="left", validate="one_to_one")
    mismatch = (df.source_sheet != df.q1_source_sheet) | (df.source_row != df.q1_source_row)
    if df.group.isna().any() or mismatch.any():
        raise ValueError("Q1 and Q9 records do not line up by participant_id/source row.")
    df = df.drop(columns=["q1_source_sheet", "q1_source_row"])
    df["in_test"] = df.group.isin(["Parent", "Non-parent"]) & df.q9_theme.isin(THEMES)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT, index=False)
    print(f"Saved {OUTPUT.relative_to(ROOT)}: {len(df):,} responses")
    summary = pd.crosstab(df.group, df.q9_theme.where(df.q9_theme.isin(["Other", "Missing"]), "Mapped to a theme"))
    print(summary.to_string())
    print(f"\nIn the test: {df.in_test.sum():,} "
          f"(Parent {(df.in_test & (df.group == 'Parent')).sum():,}, "
          f"Non-parent {(df.in_test & (df.group == 'Non-parent')).sum():,})")


if __name__ == "__main__":
    main()
