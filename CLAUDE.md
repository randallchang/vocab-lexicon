# anki-eng-training

Despite the directory name, this project does **not** use Anki or any flashcard app anymore (that direction was tried and explicitly rejected by the user as too much hassle). It's a plain-file English vocabulary habit: a static HTML study page driven by a generated JS data file + a CSV data source.

## Theme

History / humanities vocabulary — words that help the user talk about topics like European history, art movements, and culture with more depth ("文青" register). Not general TOEFL/academic argumentation vocabulary (that was the original direction before the pivot).

## Files

- `data/words-bank.csv` — the only source of truth. Columns: `date,word,pos,ipa,en_def,zh_def,en_example,zh_example`. One row per word, append-only.
- `render.py` — regenerates `word-today.js` from the CSV. No third-party dependencies (stdlib only).
- `word-today.js` — generated. A plain `const TODAY_DATA = {...}` data file: today's new words + a random sample of older words pulled back in for review (default: 5). Re-running `render.py` reshuffles which old words get pulled and rewrites only this file.
- `index.html` (formerly `vocab-today.html`, renamed for GitHub Pages so it serves at the repo root) — **static, hand-maintained, not generated.** Loads `word-today.js` via `<script src>` and renders the cards client-side (vanilla JS, DOM APIs — no `innerHTML` with interpolated text). Each word/example has a 🔊 button that plays pronunciation via the browser's built-in Web Speech API (`en-GB` voice, no network calls, no API keys). It deliberately uses a `<script src>` tag rather than `fetch()` to load the data, because it also still needs to work when opened directly (`file://`, double-click, Chrome/Safari), where `fetch()` of local files is blocked by CORS but `<script src>` is not.
- `project-purpose.md` — short human-facing description of the repo.

`vocab-bank.md` (full cumulative markdown archive) and the old fully-regenerated `vocab-today.md`/`vocab-today.html` were dropped in favor of this static-template + generated-data-file split — the CSV is the only source of truth, and `render.py` should never need to touch `index.html` again.

Never hand-edit `word-today.js` — it's overwritten by `render.py`. `index.html` is the opposite: it's meant to be hand-edited (styling, layout, playback behavior) and is never touched by `render.py`.

## Daily workflow ("今天的單字")

The user drives this — they ask, they don't want it automated/scheduled unless they say otherwise.

1. Pick ~20 new words on the history/humanities theme. Check `data/words-bank.csv` first and avoid words already in it.
2. For each word, write: word, part of speech, IPA, English definition, Chinese definition, an English example sentence (ideally with historical/cultural flavor), Chinese translation of the example.
   - IPA must be **British (RP)**, not American: non-rhotic (no /r/ before a consonant or word-finally, e.g. `pɑːˈtɪʃən` not `pɑːrˈtɪʃən`), GOAT vowel `əʊ` not `oʊ` (e.g. `kəˈləʊniəlɪzəm` not `kəˈloʊniəlɪzəm`), LOT vowel `ɒ` not `ɑ` (e.g. `bəˈrɒk` not `bəˈrɑk`). When unsure of a specific word's British form, check a dictionary rather than guessing.
3. Append the rows to `data/words-bank.csv` with today's actual date (`YYYY-MM-DD`). Use Python's `csv` module (or equivalent careful quoting) when writing — several fields contain commas.
4. Run `python3 render.py` (defaults to `--date` = today, `--review-count 5`). This overwrites `word-today.js`; open (or refresh) `index.html` in a browser to see it.
5. Summarize what was added in the chat reply; don't just silently write files.

If the user asks to change the review count or theme, that's a judgment call for them — ask, don't assume.
