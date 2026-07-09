"""Print the next unread Mythos chapter's text, ready to turn into a passages.csv row.

Finds the next chapter after whatever's already in data/passages.csv (by
`order`), pulls its page range from data/mythos-toc.csv, and extracts the
raw text from data/story.pdf via `pdftotext -layout`. It does not pick
vocabulary or write analysis — that stays a judgment call made when
authoring the passages.csv/words-bank.csv rows, same as word selection
always has been.

Requires poppler's pdftotext (`brew install poppler`).

Usage:
    python3 extract_chapter.py [--toc data/mythos-toc.csv] [--passages data/passages.csv] [--pdf data/story.pdf]
"""

import argparse
import csv
import subprocess
import sys
from pathlib import Path

TOC_COLUMNS = ["order", "part", "chapter", "page_start", "page_end"]
PASSAGE_COLUMNS = ["order", "part", "chapter", "page_start", "page_end", "text", "analysis_zh"]


def load_toc(csv_path: Path) -> list[dict]:
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = [c for c in TOC_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"{csv_path} is missing required column(s): {missing}")
        return sorted(reader, key=lambda r: int(r["order"]))


def load_passages(csv_path: Path) -> list[dict]:
    if not csv_path.exists():
        return []
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def extract_pages(pdf_path: Path, page_start: int, page_end: int) -> str:
    result = subprocess.run(
        ["pdftotext", "-f", str(page_start), "-l", str(page_end), "-layout", str(pdf_path), "-"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def clean_chapter_text(raw_text: str, chapter_title: str) -> str:
    """Reflow pdftotext -layout's print-width hard wrapping into paragraphs.

    pdftotext -layout breaks every line at the PDF's page width, not at
    paragraph boundaries, so the raw output has one line per printed line.
    A new paragraph in this book is marked by a 3+ space indent on the
    first line; continuation lines have no leading indent. Blank lines are
    just page-boundary artifacts and carry no meaning.
    """
    lines = raw_text.split("\n")
    if lines and lines[0].strip() == chapter_title:
        lines = lines[1:]

    paragraphs: list[str] = []
    current: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        leading_spaces = len(line) - len(line.lstrip(" "))
        if leading_spaces >= 3 and current:
            paragraphs.append(" ".join(current))
            current = []
        current.append(stripped)
    if current:
        paragraphs.append(" ".join(current))

    return "\n\n".join(paragraphs)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--toc", default="data/mythos-toc.csv", type=Path)
    parser.add_argument("--passages", default="data/passages.csv", type=Path)
    parser.add_argument("--pdf", default="data/story.pdf", type=Path)
    args = parser.parse_args()

    try:
        toc = load_toc(args.toc)
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    passages = load_passages(args.passages)
    last_order = max((int(p["order"]) for p in passages), default=0)
    next_order = last_order + 1

    next_chapter = next((row for row in toc if int(row["order"]) == next_order), None)
    if next_chapter is None:
        print(f"No chapter with order {next_order} in {args.toc} — book finished ({len(toc)} chapters read).")
        return

    page_start = int(next_chapter["page_start"])
    page_end = int(next_chapter["page_end"])
    raw_text = extract_pages(args.pdf, page_start, page_end)
    cleaned_text = clean_chapter_text(raw_text, next_chapter["chapter"])

    print(f"order: {next_chapter['order']}")
    print(f"part: {next_chapter['part']}")
    print(f"chapter: {next_chapter['chapter']}")
    print(f"pages: {page_start}-{page_end}")
    print("--- text ---")
    print(cleaned_text)


if __name__ == "__main__":
    main()
