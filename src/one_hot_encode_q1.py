"""One-hot encode Q1 (respondent relationship) from the raw CHCCS survey workbook.

Requires Python 3.9+ and openpyxl. CSV output (the default, used by the analysis)
needs nothing else; the optional formatted .xls report also needs LibreOffice.

Usage (from the repo root):
  python src/one_hot_encode_q1.py
      reads  data/raw/CHCCS Community Priorities Asessment (SHARED).xlsx
      writes data/processed/chccs_respondent_relationships.csv
  python src/one_hot_encode_q1.py "raw.xlsx" -o "relationships.xls" \
      --soffice "/Applications/LibreOffice.app/Contents/MacOS/soffice"

This is a standalone Python program; no Codex runtime, JavaScript, intermediate
data export, or AI service is required. Temporary .xlsx files are created and
removed automatically. LibreOffice converts the report and recalculates formulas.

The source workbook's language tabs have a specific structure: English and Karen
contain one response per row; the other six tabs contain adjacent original and
English-translation rows. Chinese puts the translation BEFORE its original.
The program validates that structure instead of counting translation rows twice.

Twelve predefined categories plus Other are encoded as separate binary columns.
Write-ins are kept as one Other selection, even when they contain commas. The
original-language choice takes precedence over its provided English translation.
Participant IDs are generated response IDs, not verified unique-person IDs.
"""

import argparse
import collections
import csv
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import textwrap

try:
    import openpyxl
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.workbook.properties import CalcProperties
except ImportError:
    raise SystemExit("Missing openpyxl. Install it with: python3 -m pip install openpyxl")


CATEGORIES = [
    "Current CHCCS student",
    "CHCCS graduate",
    "Parent of current CHCCS student(s)",
    "Parent of graduated CHCCS student(s)",
    "Parent of school-age children NOT attending CHCCS",
    "Teacher in CHCCS",
    "Administrator in CHCCS",
    "Staff in CHCCS",
    "Teacher, administrator, or school staff who does NOT work in CHCCS",
    "Orange County elected official or staff",
    "Local municipal elected official or staff",
    "Orange County resident",
]
ALL_CATEGORIES = CATEGORIES + ["Other (write-in)"]
ENGLISH_LABELS = {label: index for index, label in enumerate(CATEGORIES)}

# These are the literal non-English labels observed in the attached raw file.
# Indices refer to CATEGORIES; longer labels are always matched first.
NATIVE_LABELS = {
    "Korean": {"CHCCS 학생의 학부모": 2, "CHCCS 학교 선생": 5},
    "Japanese": {
        "現在CHCCSの生徒の保護者": 2, "現在CHCCSの生徒": 0, "Orange County 在住": 11,
    },
    "Arabic": {
        "ولي أمر لطالب حالي في مدارس مدينة تشابل هيل كاربورو": 2,
        "ولي أمر لطالب متخرج من مدارس مدينة تشابل هيل كاربورو": 3,
    },
    "Burmese": {
        "လက်ရှိ CHCCS ကျောင်းသား(များ)၏ မိဘ": 2, "Orange County နေထိုင်သူ": 11,
    },
    "Chinese": {"当前CHCCS学生的家长": 2, "有学龄子女但未就读CHCCS的家长": 4},
    "Spanish": {
        "Padre, madre o tutor de un estudiant actual de CHCCS": 2,
        "Padre, madre o tutor de un estudiante que se graduó de CHCCS": 3,
        "Estudiante actual de CHCCS": 0,
        "Graduado(a) de CHCCS": 1,
        "Maestro(a) en CHCCS": 5,
        "Personal de CHCCS": 7,
        "Residente del Condado de Orange": 11,
    },
}
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "raw" / "CHCCS Community Priorities Asessment (SHARED).xlsx"
DEFAULT_OUTPUT = ROOT / "data" / "processed" / "chccs_respondent_relationships.csv"

HEADERS = [
    "participant_id", "source_sheet", "source_row", "translation_row",
    *ALL_CATEGORIES,
    "options_selected", "more_than_one", "predefined_options_selected",
    "more_than_one_predefined", "original_response", "english_response",
    "other_text_english", "coding_note",
]


def require(condition, message):
    """Validation must still run if Python is invoked with -O."""
    if not condition:
        raise ValueError(message)


def parse_relationship(text, labels):
    """Consume whole fixed labels; the remaining suffix is ONE write-in.

    Splitting on commas would corrupt the external-educator option, Spanish
    parent labels, and free-text responses that contain commas.
    """
    remaining = (text or "").strip()
    indices = set()
    trailing_separator = False
    ordered = sorted(labels, key=len, reverse=True)
    while remaining:
        match = next((label for label in ordered
                      if remaining.startswith(label)
                      and (len(remaining) == len(label)
                           or remaining[len(label):].startswith(","))), None)
        if match is None:
            break
        indices.add(labels[match])
        remaining = remaining[len(match):]
        if remaining.startswith(","):
            remaining = remaining[1:].strip()
            trailing_separator = not remaining
        else:
            remaining = remaining.strip()
    flags = [int(i in indices) for i in range(len(CATEGORIES))]
    return flags + [int(bool(remaining))], remaining, trailing_separator


def read_records(source):
    book = openpyxl.load_workbook(source, read_only=True, data_only=True)
    records, pairs = [], 0
    known_sheets = {"English", "Karen", *NATIVE_LABELS}
    try:
        require(set(book.sheetnames) == known_sheets,
                "Expected the eight CHCCS language tabs. This script targets the supplied raw workbook layout.")
        for sheet in book:
            rows = list(sheet.values)
            if sheet.title in {"English", "Karen"}:
                originals = [(i, row, None, None) for i, row in enumerate(rows, 1)
                             if i > 1 and any(value is not None for value in row[:34])]
            else:
                originals = []
                first = 5 if sheet.title == "Chinese" else 3
                # Skip genuinely empty trailing formatting rows.
                end = max((i for i, row in enumerate(rows, 1)
                           if any(value is not None for value in row[:34])), default=0)
                for original_row in range(first, end + 1, 2):
                    translation_row = original_row - 1 if sheet.title == "Chinese" else original_row + 1
                    require(translation_row <= len(rows),
                            f"{sheet.title}!A{original_row}: missing adjacent translation row.")
                    original, translated = rows[original_row - 1], rows[translation_row - 1]
                    require(any(isinstance(value, (int, float)) for value in original[2:15]),
                            f"{sheet.title}!A{original_row}: expected numeric ratings on an original row.")
                    require(all(value is None for value in translated[2:29]),
                            f"{sheet.title}!A{translation_row}: expected a translation row with blank rating columns.")
                    originals.append((original_row, original, translation_row, translated))
                    pairs += 1

            for source_row, row, translation_row, translated in originals:
                raw = row[0] or ""
                english = (translated[0] or "") if translated is not None else raw
                require(isinstance(raw, str) and isinstance(english, str),
                        f"{sheet.title}!A{source_row}: relationship must be text.")
                flags, other_original, trailing = parse_relationship(
                    raw, NATIVE_LABELS.get(sheet.title, ENGLISH_LABELS))
                translated_flags, other_english, english_trailing = parse_relationship(english, ENGLISH_LABELS)
                if sheet.title in NATIVE_LABELS:
                    require(not other_original or sheet.title == "Spanish",
                            f"{sheet.title}!A{source_row}: unrecognized native label {other_original!r}; review its mapping.")
                require(flags[-1] == translated_flags[-1],
                        f"{sheet.title}!A{source_row}: original and translated write-ins disagree; review before counting.")
                notes = []
                if flags[:-1] != translated_flags[:-1]:
                    original_categories = "; ".join(c for c, v in zip(CATEGORIES, flags) if v)
                    translated_categories = "; ".join(c for c, v in zip(CATEGORIES, translated_flags) if v)
                    notes.append(
                        f"Original language used: {sheet.title}!A{source_row} selects [{original_categories}]; "
                        f"English translation A{translation_row} selects [{translated_categories}].")
                if trailing or english_trailing:
                    notes.append("Trailing comma with no write-in text. Other not counted because selection cannot be established.")
                if flags[-1]:
                    notes.append("Other inferred from write-in text. Write-in not reassigned to a predefined category.")
                records.append({
                    "participant_id": f"CHCCS-{len(records) + 1:04d}",
                    "source_sheet": sheet.title, "source_row": source_row,
                    "translation_row": translation_row, "flags": flags,
                    "original_response": raw, "english_response": english,
                    "other_text": other_english, "coding_note": " ".join(notes),
                })
    finally:
        book.close()
    require(records, "No response records found.")
    require(len(records) + 1 <= 65536, "The legacy .xls row limit is 65,536. Use .xlsx for a larger dataset.")
    require(len({(r['source_sheet'], r['source_row']) for r in records}) == len(records),
            "The same original source row was counted twice.")
    return records, pairs


def statistics(records):
    counts = [sum(r["flags"][i] for r in records) for i in range(len(ALL_CATEGORIES))]
    return {
        "respondents": len(records),
        "single": sum(sum(r["flags"]) == 1 for r in records),
        "multiple": sum(sum(r["flags"]) > 1 for r in records),
        "missing": sum(sum(r["flags"]) == 0 for r in records),
        "multiple_predefined": sum(sum(r["flags"][:-1]) > 1 for r in records),
        "selections": sum(counts), "counts": counts,
        "by_sheet": collections.Counter(r["source_sheet"] for r in records),
    }


def literal(cell, value):
    """Keep source text as literal text, including any leading '=' character."""
    cell.value = value
    if isinstance(value, str):
        cell.data_type = "s"


def style_header(sheet, row, last_column, height=36):
    for cells in sheet.iter_rows(min_row=row, max_row=row, max_col=last_column):
        for cell in cells:
            cell.fill = PatternFill("solid", fgColor="24435B")
            cell.font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = Border(right=Side(style="thin", color="FFFFFF"))
    sheet.row_dimensions[row].height = height


def fit_rows(sheet, first, last, columns, minimum=24):
    """Estimate wrapped heights without depending on a platform's font tools."""
    for row in range(first, last + 1):
        lines = 1
        for column in columns:
            cell = sheet.cell(row, column)
            if cell.value is None:
                continue
            width = max(10, int(sheet.column_dimensions[get_column_letter(column)].width) - 3)
            count = sum(max(1, len(textwrap.wrap(part, width=width)))
                        for part in str(cell.value).split("\n"))
            lines = max(lines, count)
        sheet.row_dimensions[row].height = max(minimum, min(409, lines * 16 + 8))


def build_workbook(source, records, pairs):
    stats = statistics(records)
    book = openpyxl.Workbook()
    summary = book.active
    summary.title = "Summary"
    participants = book.create_sheet("Participants")
    notes = book.create_sheet("Coding notes")
    last = len(records) + 1
    ref = lambda column: f"Participants!${column}$2:${column}${last}"

    # Write the flat data table with a single header row.
    participants.append(HEADERS)
    for row_index, record in enumerate(records, 2):
        values = [record["participant_id"], record["source_sheet"], record["source_row"],
                  record["translation_row"], *record["flags"], None, None, None, None,
                  record["original_response"], record["english_response"], record["other_text"], record["coding_note"]]
        for column, value in enumerate(values, 1):
            literal(participants.cell(row_index, column), value)
        for column, formula in enumerate([
            f"=SUM(E{row_index}:Q{row_index})", f"=IF(R{row_index}>1,1,0)",
            f"=SUM(E{row_index}:P{row_index})", f"=IF(T{row_index}>1,1,0)",
        ], 18):
            participants.cell(row_index, column, formula)

    summary["A2"] = "CHCCS respondent relationships"
    for column, value in enumerate(["Measure", "Respondents", "Share of respondents"], 1):
        summary.cell(4, column, value)
    measures = [
        ("Total response records", f"=COUNTA({ref('A')})"),
        ("Selected exactly one option", f"=COUNTIFS({ref('R')},1)"),
        ("Selected more than one option", f"=SUM({ref('S')})"),
        ("No relationship recorded", f"=COUNTIFS({ref('R')},0)"),
        ("Selected more than one predefined option", f"=SUM({ref('U')})"),
    ]
    for row, (label, formula) in enumerate(measures, 5):
        summary.cell(row, 1, label)
        summary.cell(row, 2, formula)
        summary.cell(row, 3, f"=B{row}/$B$5").number_format = "0.0%"
    summary["A11"] = "More than one includes Other. Category counts overlap."
    for column, value in enumerate(["Relationship category", "Respondents", "Share of respondents",
                                    "Only this category", "With other categories"], 1):
        summary.cell(13, column, value)
    for index, category in enumerate(ALL_CATEGORIES):
        row, column = index + 14, get_column_letter(index + 5)
        summary.cell(row, 1, category)
        summary.cell(row, 2, f"=SUM({ref(column)})")
        summary.cell(row, 3, f"=B{row}/$B$5").number_format = "0.0%"
        summary.cell(row, 4, f"=COUNTIFS({ref(column)},1,{ref('R')},1)")
        summary.cell(row, 5, f"=B{row}-D{row}")
    summary["A28"], summary["B28"] = "Total category selections", "=SUM(B14:B26)"
    for column, value in enumerate(["Source language tab", "Response records", "More than one", "Exactly one"], 1):
        summary.cell(31, column, value)
    for row, name in enumerate(stats["by_sheet"], 32):
        summary.cell(row, 1, name)
        summary.cell(row, 2, f"=COUNTIFS({ref('B')},A{row})")
        summary.cell(row, 3, f"=COUNTIFS({ref('B')},A{row},{ref('S')},1)")
        summary.cell(row, 4, f"=COUNTIFS({ref('B')},A{row},{ref('R')},1)")
    for column, value in enumerate(["Number of options selected", "Respondents", "Share of respondents"], 1):
        summary.cell(41, column, value)
    for value in range(7):
        row = value + 42
        summary.cell(row, 1, value)
        summary.cell(row, 2, f"=COUNTIFS({ref('R')},A{row})")
        summary.cell(row, 3, f"=B{row}/$B$5").number_format = "0.0%"
    summary["A49"] = "7 or more"
    summary["B49"] = f'=COUNTIFS({ref("R")},">=7")'
    summary["C49"] = "=B49/$B$5"
    summary["C49"].number_format = "0.0%"
    summary["A51"] = "Predefined options exclude Other. See Coding notes for treatment of translations."

    methods = [
        ("Source workbook", source.name + "; relationship question in column A of each language tab."),
        ("Source question", "Tell us about you (select all that apply)"),
        ("Scope", "All eight language tabs. One row per original survey response; paired translations are not additional respondents."),
        ("Counting unit", "Response records, not verified unique people. Separate submissions cannot be linked or deduplicated by person because no original participant IDs are provided."),
        ("Translations", f"{pairs} adjacent original/English translation pairs count once. Headers and empty rows are excluded. Chinese translations precede originals; other paired tabs put originals first."),
        ("IDs", "Generated sequential IDs CHCCS-0001 onward, in workbook tab and original row order. Source sheet and row locate each response; translation_row locates its paired translation."),
        ("Encoding", "1 = selected; 0 = not selected. Full literal option labels are consumed whole before separating choices, including option labels containing commas."),
        ("Other write-ins", "Nonempty text after predefined options is one Other selection, even if it contains commas. Write-ins are not reassigned to predefined categories."),
        ("Blank trailing delimiter", "A trailing comma without write-in text does not establish an Other selection. Such rows are preserved and flagged in coding_note. In the supplied raw file this affects English!A277."),
        ("Translation correction", "Original-language selections take precedence. In the supplied raw file, Spanish!A23 says current CHCCS student plus resident; translation A24 incorrectly says parent plus resident. Both texts are preserved and the difference is flagged."),
        ("Multiple selections", "more_than_one includes Other; more_than_one_predefined counts only the twelve fixed categories. Each is a binary indicator per response record."),
        ("Percentages", f"Shares use all {len(records):,} included response records as the denominator. Categories overlap, so category percentages can total more than 100%."),
        ("Original text", "original_response and english_response retain the original source text and provided translations, including discrepancies. Text is written as literal strings, never evaluated as formulas."),
        ("Recalculation", "Binary flag edits update the selection counts and summary formulas in Excel. Text edits do not automatically recode categories. Extend summary ranges if new rows are added."),
    ]
    notes["A2"] = "Coding and source notes"
    for row, (label, value) in enumerate(methods, 4):
        literal(notes.cell(row, 1), label)
        literal(notes.cell(row, 2), value)
    fields = [
        ("participant_id", "Generated response ID; not an ID supplied by the survey platform."),
        ("source_sheet", "Source workbook tab."),
        ("source_row", "Original response row in the source workbook, using 1-based row numbers."),
        ("translation_row", "Paired English translation row; blank for English and Karen."),
        ("E to Q category columns", "Thirteen binary indicators: twelve fixed relationship categories plus Other."),
        ("options_selected", "Sum of all thirteen category flags."),
        ("more_than_one", "1 if options_selected > 1; otherwise 0."),
        ("predefined_options_selected", "Sum of the twelve fixed-option flags, excluding Other."),
        ("more_than_one_predefined", "1 if predefined_options_selected > 1; otherwise 0."),
        ("original_response", "Verbatim response from the original source row."),
        ("english_response", "Verbatim English response or provided English translation."),
        ("other_text_english", "English text remaining after fixed option labels are removed."),
        ("coding_note", "Translation discrepancies, inferred Other choices, and trailing-comma ambiguity."),
    ]
    notes["A20"], notes["B20"] = "Participant field", "Definition"
    for row, (label, value) in enumerate(fields, 21):
        notes.cell(row, 1, label)
        notes.cell(row, 2, value)

    # Formatting is deliberately independent of the values and coding logic.
    for sheet in book:
        sheet.sheet_view.showGridLines = False
        for row in sheet:
            for cell in row:
                cell.font = Font(name="Arial", size=11, color="1F2933")
                cell.alignment = Alignment(vertical="center", horizontal="left" if cell.column == 1 else None)
                if sheet.title == "Summary" and cell.column > 1 and cell.number_format == "General":
                    cell.number_format = "#,##0"
            sheet.row_dimensions[row[0].row].height = 24
    summary.sheet_properties.tabColor = "24435B"
    summary.column_dimensions["A"].width = 78
    for column in "BCDE":
        summary.column_dimensions[column].width = 19
    summary["A2"].font = Font(name="Arial", size=15, bold=True)
    for row, count, height in [(4, 3, 36), (13, 5, 48), (31, 4, 36), (41, 3, 36)]:
        style_header(summary, row, count, height)
    for row in range(14, 27):
        summary.row_dimensions[row].height = 32
        summary.cell(row, 1).alignment = Alignment(vertical="center", wrap_text=True)
        if row % 2 == 0:
            for cell in summary[row][:5]:
                cell.fill = PatternFill("solid", fgColor="F3F6F8")
    for cell in summary[7][:3]:
        cell.fill = PatternFill("solid", fgColor="E8F0F7")
        cell.font = Font(name="Arial", size=11, bold=True)
    for row in (11, 51):
        summary.cell(row, 1).font = Font(name="Arial", size=11, italic=True)

    widths = [19, 16, 15, 15] + [25] * 13 + [25] * 4 + [75, 75, 75, 90]
    for column, width in enumerate(widths, 1):
        participants.column_dimensions[get_column_letter(column)].width = width
    style_header(participants, 1, 25, 116)
    participants.freeze_panes = "E2"
    participants.auto_filter.ref = f"A1:Y{last}"
    for row in participants.iter_rows(min_row=2):
        for cell in row[2:21]:
            cell.number_format = "0"
            cell.alignment = Alignment(horizontal="right", vertical="center")
        for cell in row[21:]:
            cell.alignment = Alignment(vertical="center", wrap_text=True)
        if row[0].row % 2 == 0:
            for cell in row:
                cell.fill = PatternFill("solid", fgColor="F3F6F8")
    fit_rows(participants, 2, last, range(22, 26))
    notes.column_dimensions["A"].width = 34
    notes.column_dimensions["B"].width = 110
    notes["A2"].font = Font(name="Arial", size=15, bold=True)
    for row in range(4, 18):
        notes.cell(row, 1).font = Font(name="Arial", size=11, bold=True)
        notes.cell(row, 2).alignment = Alignment(wrap_text=True, vertical="center")
    for row in range(21, 34):
        for cell in notes[row][:2]:
            cell.alignment = Alignment(wrap_text=True, vertical="center")
    style_header(notes, 20, 2)
    fit_rows(notes, 4, 17, [2])
    fit_rows(notes, 21, 33, [1, 2])
    book.calculation = CalcProperties(calcId=0, fullCalcOnLoad=True, forceFullCalc=True)
    return book, stats


def save_csv(records, output):
    """Write the Participants table as plain CSV, with the derived counts computed here."""
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(HEADERS)
        for r in records:
            flags = r["flags"]
            total, predefined = sum(flags), sum(flags[:-1])
            writer.writerow([
                r["participant_id"], r["source_sheet"], r["source_row"],
                "" if r["translation_row"] is None else r["translation_row"], *flags,
                total, int(total > 1), predefined, int(predefined > 1),
                r["original_response"], r["english_response"], r["other_text"], r["coding_note"],
            ])


def find_soffice(explicit=None):
    if explicit:
        found = shutil.which(explicit) or (str(Path(explicit).expanduser()) if Path(explicit).expanduser().is_file() else None)
        if found:
            return found
        raise ValueError(f"LibreOffice executable not found: {explicit}")
    for command in ("soffice", "libreoffice"):
        found = shutil.which(command)
        if found:
            return found
    candidates = [Path("/Applications/LibreOffice.app/Contents/MacOS/soffice")]
    for key in ("PROGRAMFILES", "PROGRAMFILES(X86)"):
        if os.environ.get(key):
            candidates.append(Path(os.environ[key]) / "LibreOffice/program/soffice.exe")
    for path in candidates:
        if path.is_file():
            return str(path)
    raise ValueError("LibreOffice is needed for .xls output. Install it, or specify its executable with --soffice PATH.")


def save_xls(book, output, executable):
    output.parent.mkdir(parents=True, exist_ok=True)
    # Keep all intermediate files in one private temporary directory.
    with tempfile.TemporaryDirectory(prefix="chccs_relationships_") as temporary:
        folder = Path(temporary).resolve()
        intermediate = folder / (output.stem + ".xlsx")
        converted = folder / "converted"
        converted.mkdir()
        profile = folder / "libreoffice_profile"
        book.save(intermediate)
        result = subprocess.run([
            executable, f"-env:UserInstallation={profile.as_uri()}", "--headless",
            "--convert-to", "xls:MS Excel 97", "--outdir", str(converted), str(intermediate),
        ], capture_output=True, text=True, timeout=180)
        produced = converted / (intermediate.stem + ".xls")
        if result.returncode or not produced.is_file():
            raise RuntimeError("LibreOffice conversion failed:\n" + result.stdout + "\n" + result.stderr)
        require(produced.read_bytes()[:8] == bytes.fromhex("D0CF11E0A1B11AE1"),
                "Output is not a genuine legacy Excel compound document.")
        # Copy to the destination filesystem before an atomic final replacement.
        handle, staged = tempfile.mkstemp(prefix=".chccs_", suffix=".xls", dir=output.parent)
        os.close(handle)
        try:
            shutil.copyfile(produced, staged)
            os.replace(staged, output)
        finally:
            if os.path.exists(staged):
                os.unlink(staged)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", type=Path, nargs="?", default=DEFAULT_INPUT, help="Original CHCCS .xlsx workbook")
    parser.add_argument("-o", "--output", type=Path, default=DEFAULT_OUTPUT,
                        help="Output .csv (default) or formatted .xls report")
    parser.add_argument("--soffice", help="LibreOffice executable, if it is not on PATH")
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing output file")
    args = parser.parse_args(argv)
    source, output = args.input.expanduser().resolve(), args.output.expanduser().resolve()
    try:
        require(source.is_file(), f"Input not found: {source}")
        require(output.suffix.lower() in {".csv", ".xls"}, "The output filename must end in .csv or .xls.")
        require(source != output, "Input and output paths must differ.")
        records, pairs = read_records(source)
        if output.suffix.lower() == ".csv":
            stats = statistics(records)
            save_csv(records, output)
        else:
            require(not output.exists() or args.overwrite, "Output already exists. Choose another filename or add --overwrite.")
            executable = find_soffice(args.soffice)
            book, stats = build_workbook(source, records, pairs)
            save_xls(book, output, executable)
    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, f"Error: {error}\n")
    print(f"Saved: {output}")
    print(f"Response records: {stats['respondents']:,}")
    print(f"Selected more than one option: {stats['multiple']:,} ({stats['multiple']/stats['respondents']:.1%})")
    print(f"Selected more than one predefined option: {stats['multiple_predefined']:,}")
    print(f"Original/translation pairs counted once: {pairs}")
    for category, count in zip(ALL_CATEGORIES, stats["counts"]):
        print(f"  {category}: {count:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
