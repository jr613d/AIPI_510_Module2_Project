"""Make the redacted copy of the CHCCS workbook that is committed to the repository.

The district's published workbook includes free-text answers in which some
respondents gave personal details (a home address, an email address, children's
health information tied to a named school). This script blanks the three
open-ended free-text fields on every response row and leaves everything else,
including headers, ratings, top-three picks and Q9, unchanged:

    column P  (Q4)  Other challenges
    column AD (Q6)  Other values
    column AH (Q10) Additional thoughts

The analysis uses only Q1 and Q9, so its results are identical with either copy.

Usage (from the repo root), after downloading the original from
https://www.chccstogether.org/document-library:
  python src/redact_raw_workbook.py
      reads  data/raw/private/CHCCS Community Priorities Asessment (SHARED) - original.xlsx
      writes data/raw/CHCCS Community Priorities Asessment (SHARED).xlsx
"""
import hashlib
from pathlib import Path

import openpyxl

from one_hot_encode_q1 import DEFAULT_INPUT, read_records

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / "data" / "raw" / "private" / "CHCCS Community Priorities Asessment (SHARED) - original.xlsx"
ORIGINAL_SHA256 = "1afc8b9974cae04b0eeb968679f9e3cc4db2dd5a2241320b0340af36d3ae6ea3"
FREE_TEXT_COLUMNS = {"P": 16, "AD": 30, "AH": 34}  # 1-based column numbers


def main():
    digest = hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()
    if digest != ORIGINAL_SHA256:
        print(f"Warning: {ORIGINAL.name} has SHA-256 {digest}, not the expected {ORIGINAL_SHA256}.")

    records, _ = read_records(ORIGINAL)
    book = openpyxl.load_workbook(ORIGINAL)
    blanked = 0
    for r in records:
        sheet = book[r["source_sheet"]]
        for row in filter(None, (r["source_row"], r["translation_row"])):
            for col in FREE_TEXT_COLUMNS.values():
                cell = sheet.cell(row=row, column=col)
                if cell.value not in (None, ""):
                    cell.value = None
                    blanked += 1
    book.save(DEFAULT_INPUT)
    print(f"Blanked {blanked:,} free-text cells across {len(records):,} responses -> {DEFAULT_INPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
