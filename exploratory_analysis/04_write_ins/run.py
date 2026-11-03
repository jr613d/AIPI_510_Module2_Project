"""04: Themes in the free-text answers.

Codes four free-text fields with transparent keyword rules: other challenges (Q4), other values
(Q6), Q9 write-ins, and additional thoughts (Q10). Keyword coding is rough: it misses synonyms
and can't read context, so counts are approximate. Outputs hold codes and counts, not quotes.

Exploratory. Run from the repo root:  python exploratory_analysis/04_write_ins/run.py
"""
import sys
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as c  # noqa: E402

FIG, RES = HERE / "figures", HERE / "results"
warnings.filterwarnings("ignore", "This pattern is interpreted")

THEME_RULES = {
    "Walking, biking & walk zones": r"\bwalk|\bbik(e|es|ing)\b|safe routes",
    "Keep current students in place / minimize disruption": r"continuity|disrupt|uproot|stabil|grandfather|current school|"
        r"stay(ing)? (at|in)|keep(ing)? (students|kids|children|families)|reassign|moving (students|kids|children)",
    "Neighborhood & community schools": r"neighbou?rhood|community school|close to home|nearby school",
    "Teachers & staff (support, pay, retention)": r"teacher|\bstaff|retain|retention|salar|\bpay\b|educator",
    "Equity & the achievement gap": r"equit|achievement gap|marginali|under[- ]?resourced|low[- ]income|title i|"
        r"segregat|racial|\brace\b|disadvantag",
    "Special programs (dual language, magnet, EC)": r"dual language|immersion|mandarin|magnet|\bec\b|special ed|"
        r"\biep|exceptional|gifted|\baig\b|specialty program",
    "Siblings & keeping families together": r"sibling",
    "Buses, commute & traffic": r"\bbus|busing|transport|commute|traffic|car rider|\bdriv(e|ing)\b",
    "Class size, capacity & crowding": r"class size|capacity|overcrowd|crowd",
    "Screens & classroom technology": r"screen|chromebook|device|ipad|\btech",
    "Trust, transparency & communication": r"trust|transparen|communicat|accountab|honest|listen",
    "Criticism of the survey itself": r"survey|this question|confus|rank(ing)? (these|this)",
    "Housing, growth & enrollment": r"housing|afford|development|enrol",
    "Safety & security": r"safety|\bsafe\b|security|violence",
}
FIELDS = {"other_challenges": "Q4 other challenges", "other_values": "Q6 other values",
          "q9_write_in": "Q9 write-in", "additional_thoughts": "Q10 additional thoughts"}


def main():
    if not c.HAS_FREE_TEXT:
        # Without the original workbook every free-text field is blank, and rerunning
        # would overwrite the committed results with empty codes.
        print("Skipped: needs the original CHCCS workbook in data/raw/private/ (see src/redact_raw_workbook.py).")
        return
    RES.mkdir(exist_ok=True)
    df = c.load_responses()
    q9 = pd.read_csv(c.ROOT / "data" / "processed" / "q9_value_themes.csv")[["participant_id", "q9_english"]]
    df = df.merge(q9, on="participant_id", how="left")
    df["q9_write_in"] = df.q9_english.where(df.q9_theme == "Other", "")
    for f in FIELDS:
        df[f] = df[f].fillna("").astype(str).str.strip()

    # Code each field, then combine to "respondent mentions theme anywhere"
    coded = pd.DataFrame({"participant_id": df.participant_id, "group": df.group})
    field_counts = []
    for f, flabel in FIELDS.items():
        has_text = df[f] != ""
        row = {"field": flabel, "responses_with_text": int(has_text.sum())}
        for theme, rule in THEME_RULES.items():
            hit = has_text & df[f].str.contains(rule, case=False, regex=True)
            coded[f"{f}|{theme}"] = hit
            row[theme] = int(hit.sum())
        field_counts.append(row)
    any_text = (df[list(FIELDS)] != "").any(axis=1)
    mentions = pd.DataFrame({t: coded[[f"{f}|{t}" for f in FIELDS]].any(axis=1) for t in THEME_RULES})
    coded_any = mentions.any(axis=1)

    summary = pd.DataFrame({
        "respondents_mentioning": mentions.sum(),
        "pct_of_writers": mentions[any_text].mean() * 100,
        "parent_pct_of_writers": mentions[any_text & (df.group == "Parent")].mean() * 100,
        "non_parent_pct_of_writers": mentions[any_text & (df.group == "Non-parent")].mean() * 100,
    }).sort_values("respondents_mentioning", ascending=False)
    summary.round(1).to_csv(RES / "write_in_themes.csv")
    pd.DataFrame(field_counts).to_csv(RES / "write_in_themes_by_field.csv", index=False)
    coded.drop(columns=["group"]).to_csv(RES / "write_in_codes_by_response.csv", index=False)

    n_writers = int(any_text.sum())
    n_p = int((any_text & (df.group == "Parent")).sum())
    n_n = int((any_text & (df.group == "Non-parent")).sum())
    fig, ax = plt.subplots(figsize=(11, 6.8), dpi=150)
    c.grouped_bars(ax, list(summary.index),
                   [(summary.parent_pct_of_writers.values, f"Parents who wrote something (n = {n_p:,})", c.BLUE),
                    (summary.non_parent_pct_of_writers.values, f"Non-parents who wrote something (n = {n_n:,})", c.ORANGE)],
                   xmax=45)
    c.style(ax, "Percent of respondents who wrote anything, mentioning this theme in any free-text field")
    ax.legend(frameon=False, fontsize=9, loc="lower right")
    c.finish(fig, "In their own words: what respondents raised beyond the listed options",
             f"Exploratory keyword coding of {n_writers:,} respondents' free text (Q4, Q6, Q9 write-ins, Q10). "
             f"{coded_any[any_text].mean():.0%} of writers matched at least one theme. Counts are approximate.",
             FIG / "write_in_themes.png")
    print(f"writers: {n_writers} (parents {n_p}, non-parents {n_n}); coded share {coded_any[any_text].mean():.2f}")
    print(pd.DataFrame(field_counts)[["field", "responses_with_text"]].to_string(index=False))
    print(summary.round(1).to_string())


if __name__ == "__main__":
    main()
