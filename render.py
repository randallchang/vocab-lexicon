"""Generate book-data.js from data/words-bank.csv and data/passages.csv.

Reading progress through Mythos accumulates chapter by chapter in
data/passages.csv (see extract_chapter.py for pulling the next chapter's
text out of data/story.pdf). Each word in data/words-bank.csv is tagged
with the source_chapter it came from. This script joins the two into a
single book-data.js data file: every chapter read so far, each with its
own text/analysis/word list. There's no separate review/spaced-repetition
sampling — every chapter stays browsable, so going back and rereading an
earlier chapter's word list is the review.

index.html (static, hand-maintained, not generated) loads book-data.js via
<script src> and renders it client-side, with chapter navigation. It is not
touched by this script — only book-data.js is regenerated. Rendering the
data via a plain <script src> tag (rather than fetch()) is deliberate: it
still works when the page is opened directly as a file:// URL in Chrome or
Safari, which block fetch() of local files.

Usage:
    python3 render.py [--bank data/words-bank.csv] [--passages data/passages.csv]
"""

import argparse
import csv
import json
import sys
from pathlib import Path

BANK_COLUMNS = [
    "date", "word", "pos", "ipa", "en_def", "zh_def",
    "en_example", "en_example_chunks", "zh_example", "source_chapter",
]
WORD_FIELDS = ["word", "pos", "ipa", "en_def", "zh_def", "en_example", "en_example_chunks", "zh_example"]
PASSAGE_COLUMNS = ["order", "part", "chapter", "page_start", "page_end", "text", "analysis_zh"]


def load_bank(csv_path: Path) -> list[dict]:
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing_columns = [c for c in BANK_COLUMNS if c not in (reader.fieldnames or [])]
        if missing_columns:
            raise ValueError(f"{csv_path} is missing required column(s): {missing_columns}")
        return list(reader)


def load_passages(csv_path: Path) -> list[dict]:
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing_columns = [c for c in PASSAGE_COLUMNS if c not in (reader.fieldnames or [])]
        if missing_columns:
            raise ValueError(f"{csv_path} is missing required column(s): {missing_columns}")
        return sorted(reader, key=lambda r: int(r["order"]))


def strip_word(row: dict) -> dict:
    return {field: row[field] for field in WORD_FIELDS}


def render_book_data_js(bank_rows: list[dict], passage_rows: list[dict]) -> str:
    chapters = []
    for p in passage_rows:
        chapter_words = [strip_word(r) for r in bank_rows if r["source_chapter"] == p["chapter"]]
        chapters.append({
            "order": int(p["order"]),
            "part": p["part"],
            "chapter": p["chapter"],
            "pageStart": int(p["page_start"]),
            "pageEnd": int(p["page_end"]),
            "text": p["text"],
            "analysisZh": p["analysis_zh"],
            "words": chapter_words,
        })

    data = {
        "book": "Mythos",
        "author": "Stephen Fry",
        "latestOrder": chapters[-1]["order"] if chapters else None,
        "chapters": chapters,
    }
    return f"const BOOK_DATA = {json.dumps(data, ensure_ascii=False, indent=2)};\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bank", default="data/words-bank.csv", type=Path)
    parser.add_argument("--passages", default="data/passages.csv", type=Path)
    parser.add_argument("--data-output", default="book-data.js", type=Path)
    args = parser.parse_args()

    try:
        bank_rows = load_bank(args.bank)
        passage_rows = load_passages(args.passages)
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    args.data_output.write_text(
        render_book_data_js(bank_rows, passage_rows), encoding="utf-8"
    )
    print(f"Wrote {len(passage_rows)} chapter(s) to {args.data_output}")


if __name__ == "__main__":
    main()
