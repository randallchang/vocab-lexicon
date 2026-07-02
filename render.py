"""Generate vocab-bank.md (full archive) and vocab-today.md (today's study set)
from data/words-bank.csv.

New words are appended to data/words-bank.csv (with today's date) before
running this script. vocab-today.md then contains today's new words plus a
random sample of older words pulled back in for review.

Usage:
    python3 render.py [--bank data/words-bank.csv] [--date 2026-07-02] [--review-count 5]
"""

import argparse
import csv
import random
import sys
from datetime import date
from pathlib import Path

COLUMNS = ["date", "word", "pos", "ipa", "en_def", "zh_def", "en_example", "zh_example"]


def load_bank(csv_path: Path) -> list[dict]:
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing_columns = [c for c in COLUMNS if c not in (reader.fieldnames or [])]
        if missing_columns:
            raise ValueError(f"{csv_path} is missing required column(s): {missing_columns}")
        return list(reader)


def render_word_block(row: dict) -> str:
    return (
        f"### {row['word']} /{row['ipa']}/ — {row['pos']}\n"
        f"- **英文定義:** {row['en_def']}\n"
        f"- **中文:** {row['zh_def']}\n"
        f'- *"{row["en_example"]}"*\n'
        f"  {row['zh_example']}\n"
    )


def render_bank_md(rows: list[dict]) -> str:
    dates_newest_first = sorted({row["date"] for row in rows}, reverse=True)
    sections = ["# 單字庫（累積所有學過的單字）\n"]
    for day in dates_newest_first:
        sections.append(f"## {day}\n")
        day_rows = [row for row in rows if row["date"] == day]
        sections.extend(render_word_block(row) for row in day_rows)
    return "\n".join(sections)


def render_today_md(rows: list[dict], today: str, review_count: int) -> str:
    new_rows = [row for row in rows if row["date"] == today]
    old_rows = [row for row in rows if row["date"] != today]
    review_rows = random.sample(old_rows, min(review_count, len(old_rows)))

    sections = [f"# 今日學習（{today}）\n"]
    sections.append("## 新單字\n")
    sections.extend(render_word_block(row) for row in new_rows)
    if review_rows:
        sections.append("## 複習（從單字庫隨機抽選）\n")
        sections.extend(render_word_block(row) for row in review_rows)
    return "\n".join(sections)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bank", default="data/words-bank.csv", type=Path)
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--review-count", default=5, type=int)
    parser.add_argument("--bank-output", default="vocab-bank.md", type=Path)
    parser.add_argument("--today-output", default="vocab-today.md", type=Path)
    args = parser.parse_args()

    try:
        rows = load_bank(args.bank)
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    args.bank_output.write_text(render_bank_md(rows), encoding="utf-8")
    args.today_output.write_text(render_today_md(rows, args.date, args.review_count), encoding="utf-8")
    print(f"Wrote {len(rows)} word(s) to {args.bank_output}")
    print(f"Wrote today's study set ({args.date}) to {args.today_output}")


if __name__ == "__main__":
    main()
