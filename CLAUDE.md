# anki-eng-training

Despite the directory name, this project does **not** use Anki or any flashcard app anymore (that direction was tried and explicitly rejected by the user as too much hassle). It's a plain-file English vocabulary habit: markdown notes + a CSV data source.

## Theme

History / humanities vocabulary — words that help the user talk about topics like European history, art movements, and culture with more depth ("文青" register). Not general TOEFL/academic argumentation vocabulary (that was the original direction before the pivot).

## Files

- `data/words-bank.csv` — the only source of truth. Columns: `date,word,pos,ipa,en_def,zh_def,en_example,zh_example`. One row per word, append-only.
- `render.py` — regenerates the two markdown outputs from the CSV. No third-party dependencies (stdlib only).
- `vocab-bank.md` — generated. Full cumulative archive of every word ever learned, grouped by date, newest first.
- `vocab-today.md` — generated. Today's new words + a random sample of older words pulled back in for review (default: 5). Re-running `render.py` reshuffles which old words get pulled.
- `project-purpose.md` — short human-facing description of the repo.

Never hand-edit `vocab-bank.md` or `vocab-today.md` directly — they're overwritten by `render.py`.

## Daily workflow ("今天的單字")

The user drives this — they ask, they don't want it automated/scheduled unless they say otherwise.

1. Pick ~20 new words on the history/humanities theme. Check `data/words-bank.csv` first and avoid words already in it.
2. For each word, write: word, part of speech, IPA, English definition, Chinese definition, an English example sentence (ideally with historical/cultural flavor), Chinese translation of the example.
3. Append the rows to `data/words-bank.csv` with today's actual date (`YYYY-MM-DD`). Use Python's `csv` module (or equivalent careful quoting) when writing — several fields contain commas.
4. Run `python3 render.py` (defaults to `--date` = today, `--review-count 5`). This overwrites `vocab-bank.md` and `vocab-today.md`.
5. Summarize what was added in the chat reply; don't just silently write files.

If the user asks to change the review count or theme, that's a judgment call for them — ask, don't assume.
