# anki-eng-training

Despite the directory name, this project does **not** use Anki or any flashcard app anymore (that direction was tried and explicitly rejected by the user as too much hassle). It's a plain-file English vocabulary habit: a static HTML study page driven by a generated JS data file + a CSV data source.

## Theme

History / humanities vocabulary — words that help the user talk about topics like European history, art movements, and culture with more depth ("文青" register). Not general TOEFL/academic argumentation vocabulary (that was the original direction before the pivot).

## Files

- `data/words-bank.csv` — the only source of truth. Columns: `date,word,pos,ipa,en_def,zh_def,en_example,en_example_chunks,zh_example`. One row per word, append-only.
- `render.py` — regenerates `word-today.js` from the CSV. No third-party dependencies (stdlib only).
- `word-today.js` — generated. A plain `const TODAY_DATA = {...}` data file: today's new words + a random sample of older words pulled back in for review (default: 5). Re-running `render.py` reshuffles which old words get pulled and rewrites only this file.
- `index.html` (formerly `vocab-today.html`, renamed for GitHub Pages so it serves at the repo root) — **static, hand-maintained, not generated.** Loads `word-today.js` via `<script src>` and renders the cards client-side (vanilla JS, DOM APIs — no `innerHTML` with interpolated text). Each word/example has a 🔊 button that plays pronunciation via the browser's built-in Web Speech API (`en-GB` voice, no network calls, no API keys). It deliberately uses a `<script src>` tag rather than `fetch()` to load the data, because it also still needs to work when opened directly (`file://`, double-click, Chrome/Safari), where `fetch()` of local files is blocked by CORS but `<script src>` is not. A global 顯示中文/隱藏中文 toggle button (`#toggle-zh`) hides `.def-zh`/`.example-zh` by default (`body.hide-zh`) so the page can double as a self-quiz.
- `project-purpose.md` — short human-facing description of the repo.

`vocab-bank.md` (full cumulative markdown archive) and the old fully-regenerated `vocab-today.md`/`vocab-today.html` were dropped in favor of this static-template + generated-data-file split — the CSV is the only source of truth, and `render.py` should never need to touch `index.html` again.

Never hand-edit `word-today.js` — it's overwritten by `render.py`. `index.html` is the opposite: it's meant to be hand-edited (styling, layout, playback behavior) and is never touched by `render.py`.

### Sentence pause-grouping (斷句)

English example sentences are shown with `/` pause marks between reading chunks, so the user knows where to pause when reading aloud. This is **authored data, not computed code**: the `en_example_chunks` CSV column holds the same sentence as `en_example` but with `/` inserted at chunk boundaries (e.g. `"Marx argued / that the bourgeoisie had accumulated wealth / at the expense / of the industrial working class."`). `index.html` just splits that column on `/` and wraps each `/` in a styled `<span class="pause-mark">` — it does no linguistic analysis itself. The 🔊 play buttons still speak the plain `en_example` field (no slashes) so playback isn't affected.

A rule-based version (`chunkSentence()` doing punctuation + a fixed subordinator/conjunction word list) was tried first and lived in `index.html`, but rule-of-thumb chunking can't reliably handle prepositional-phrase grouping or "pause before the verb if the subject is long" — those need actual reading comprehension. Authoring the chunks by hand (or via an LLM) when each new word is added, using judgment guided by these four rules, produces far more natural breaks:

1. **標點符號**：遇到逗號（,）、句號（.）、分號（;）停頓。
2. **子句連接詞**：在 that, which, because, although 等連接詞前停頓。
3. **介系詞**：在 of, for, to, with 前停頓一下，把這組介系詞片語連在一起唸。
4. **長主詞**：如果句子主詞很長，可以在動詞出現前停頓。

These are guidance for judgment calls, not a mechanical algorithm — e.g. a short subject with an embedded prepositional phrase (`"Scholars of antiquity still debate..."`) usually reads better kept whole than broken at every rule-3 trigger.

## Daily workflow ("今天的單字")

The user drives this — they ask, they don't want it automated/scheduled unless they say otherwise.

1. Pick ~10 new words on the history/humanities theme. Check `data/words-bank.csv` first and avoid words already in it.
2. For each word, write: word, part of speech, IPA, English definition, Chinese definition, an English example sentence (ideally with historical/cultural flavor), a pause-grouped version of that same sentence (`en_example_chunks`, see below), Chinese translation of the example.
   - IPA must be **British (RP)**, not American: non-rhotic (no /r/ before a consonant or word-finally, e.g. `pɑːˈtɪʃən` not `pɑːrˈtɪʃən`), GOAT vowel `əʊ` not `oʊ` (e.g. `kəˈləʊniəlɪzəm` not `kəˈloʊniəlɪzəm`), LOT vowel `ɒ` not `ɑ` (e.g. `bəˈrɒk` not `bəˈrɑk`). When unsure of a specific word's British form, check a dictionary rather than guessing.
3. Append the rows to `data/words-bank.csv` with today's actual date (`YYYY-MM-DD`). Use Python's `csv` module (or equivalent careful quoting) when writing — several fields contain commas.
4. Run `python3 render.py` (defaults to `--date` = today, `--review-count 5`). This overwrites `word-today.js`; open (or refresh) `index.html` in a browser to see it.
5. Summarize what was added in the chat reply; don't just silently write files.

If the user asks to change the review count or theme, that's a judgment call for them — ask, don't assume.
