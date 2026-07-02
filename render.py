"""Generate word-today.js (today's study set as data) from data/words-bank.csv.

New words are appended to data/words-bank.csv (with today's date) before
running this script. word-today.js then exports today's new words plus a
random sample of older words pulled back in for review, as a small
JavaScript data file.

index.html (formerly vocab-today.html, renamed for GitHub Pages) is a
static, hand-maintained page (not generated) that loads word-today.js via
<script src> and renders it client-side. It is not touched by this script —
only word-today.js is regenerated. Rendering the
data via a plain <script src> tag (rather than fetch()) is deliberate: it
still works when the page is opened directly as a file:// URL in Chrome or
Safari, which block fetch() of local files.

Usage:
    python3 render.py [--bank data/words-bank.csv] [--date 2026-07-02] [--review-count 5]
"""

import argparse
import csv
import json
import random
import sys
from datetime import date
from pathlib import Path

COLUMNS = ["date", "word", "pos", "ipa", "en_def", "zh_def", "en_example", "zh_example"]
WORD_FIELDS = ["word", "pos", "ipa", "en_def", "zh_def", "en_example", "zh_example"]


def load_bank(csv_path: Path) -> list[dict]:
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing_columns = [c for c in COLUMNS if c not in (reader.fieldnames or [])]
        if missing_columns:
            raise ValueError(f"{csv_path} is missing required column(s): {missing_columns}")
        return list(reader)


def strip_word(row: dict) -> dict:
    return {field: row[field] for field in WORD_FIELDS}


def render_today_js(rows: list[dict], today: str, review_count: int) -> str:
    new_rows = [row for row in rows if row["date"] == today]
    old_rows = [row for row in rows if row["date"] != today]
    review_rows = random.sample(old_rows, min(review_count, len(old_rows)))

    data = {
        "date": today,
        "newWords": [strip_word(row) for row in new_rows],
        "reviewWords": [strip_word(row) for row in review_rows],
    }
    return f"const TODAY_DATA = {json.dumps(data, ensure_ascii=False, indent=2)};\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bank", default="data/words-bank.csv", type=Path)
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--review-count", default=5, type=int)
    parser.add_argument("--data-output", default="word-today.js", type=Path)
    args = parser.parse_args()

    try:
        rows = load_bank(args.bank)
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    args.data_output.write_text(render_today_js(rows, args.date, args.review_count), encoding="utf-8")
    print(f"Wrote today's study set ({args.date}) to {args.data_output}")


if __name__ == "__main__":
    main()
