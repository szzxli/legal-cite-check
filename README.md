# legal-cite-check — does the case you cited exist, and is it the case you named?
Live web tool: https://szzxli.github.io/legal-cite-check/

> **Not legal advice. This tool only checks whether a cited case exists in CourtListener and whether the case name matches. It does not check whether the case supports your argument, whether quotes or pin cites are accurate, or whether the case is still good law. A case marked NOT FOUND may still exist (CourtListener's coverage is incomplete); a case marked VERIFIED may still be wrong for your purpose. Read every case you cite.**

**Try it in your browser:** the GitHub Pages site (paste text; nothing leaves your browser). The browser page only extracts citations and shows manual-check links — it does not call CourtListener.

## What it checks / what it doesn't

Checks, for each full case citation in a brief, motion, or letter:

- whether a case exists at that volume / reporter / page in CourtListener;
- whether the case name written in the text matches the case at that cite.

It does NOT check: whether the case supports your proposition, quote
accuracy, pin cites, good-law / overruled status (that needs a citator),
statutes, regulations, law reviews, or `id.` / `supra` / short-form cites
(those are labelled `NOT_CHECKED`).

Target users, in order: US pro se litigants, solo and small-firm lawyers
(≤5 attorneys), law-school clinics and legal-aid volunteers.

## Labels (and what to do next)

See `docs/labels.md`. In short: `VERIFIED` (found, name matches),
`CITED` (found, name not compared or only partly matches), `AMBIGUOUS`
(more than one match), `MISMATCH` (a different case sits at this cite),
`NOT_FOUND` (valid format, no case at this cite in CourtListener),
`INVALID_REPORTER`, `RATE_LIMITED`, `NOT_CHECKED`. Uncertainty only ever
downgrades a label, never upgrades it. This tool never describes a user's
citation as fabricated, fake, or hallucinated.

## Full check with CourtListener (CLI)

```bash
pip install .
python -m legalcite check brief.md --md report.md --json report.json --html report.html
python -m legalcite check brief.md --fail-on not_found,invalid_reporter,mismatch
```

Exit 1 if any citation has a `--fail-on` label, 0 otherwise, 2 on usage
error. Without a token, every citation is `NOT_CHECKED` (extraction
only) — that is not a crash.

Optional extras: `pip install .[rapidfuzz]` for rapidfuzz name matching
(a pure-Python fallback is built in); `pip install .[eyecite]` plus
`LEGALCITE_USE_EYECITE=1` to try eyecite first, with regex fallback.

## GitHub Action

```yaml
on: [pull_request]
permissions: { contents: read }
jobs:
  cites:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: szzxli/legal-cite-check@main
        with: { files: "briefs/**/*.md" }
        env: { COURTLISTENER_TOKEN: "${{ secrets.COURTLISTENER_TOKEN }}" }
```

## Your CourtListener token and its terms

The CLI and Action use **your own free token** from the environment
variable / Actions secret `COURTLISTENER_TOKEN`. It is masked in Actions
and never printed, logged, cached, or included in reports or artifacts.
By default the CLI sends CourtListener **only the extracted citation
strings**, never your brief text (`--send-full-text` is off by default).

CourtListener membership API access is for personal, educational,
research, journalistic, and exploratory use; solo practitioners and
firms with ≤5 attorneys are welcome. It may **not** power a
revenue-positive commercial product, and internal tools for
organizations count as commercial. Large firms and organizations need
their own agreement with Free Law Project. Read the terms before use:
https://free.law/membership/allowed-api-usage/ — see also
`docs/courtlistener-terms.md`. No commercial use until a separate
agreement is signed.

## Accuracy (benchmark v0.1)

See `benchmark/`. The v0.1 seed is small (5 bad-citation candidates +
6 real controls with mock fixtures + 7 pending placeholders), so all
rates are **signals, not rates**: counts are reported with sample sizes
and every miss / false alarm is listed by id. The live benchmark has
**not** been run: it is blocked pending a user-supplied
`COURTLISTENER_TOKEN` (no token was created or used for this build).
Replay results in `benchmark/results/` use clearly-labelled MOCK
fixtures, not real CourtListener payloads.

Known limits: CourtListener coverage gaps (especially state and
unpublished cases) can make real cases `NOT_FOUND`; the tool does not
check propositions or quotes, which is a large share of the problems
courts describe.

## Privacy

See `docs/privacy.md`. Web page: text in memory only, no localStorage of
brief text, no API calls, GoatCounter page views only. CLI: reports are
written only where you ask; default request body is citation strings only.

## Credits

CourtListener / Free Law Project; eyecite (BSD-2-Clause); reporter table
in `web/reporters.json` is a small hand-written table (see
`VERIFICATION.md` — the full reporters-db dataset was not bundled).
Benchmark discovery source: AI Hallucination Cases Database, Damien
Charlotin (CC BY 4.0, with attribution) — used as a pointer to court
decisions only; seed findings are pending live verification.

## License

MIT. See `LICENSE`.
## v2 (local-only prototype): trilingual web UI + opinion translation viewer

**Status: v2 is deployed on GitHub Pages (see Live web tool link above).**

New in v2:

- Web UI language switcher (English / Espa\u00f1ol / \u4e2d\u6587) in `web/`:
  all UI strings, result-label explanations, help text, and the
  disclaimer are translated (`web/i18n.js`). Every language carries
  exactly the same set of UI keys (enforced by
  `web/tests/test_i18n_translate.js`). The English disclaimer is
  authoritative; Spanish and Chinese disclaimers are marked as
  translations. Label codes (`VERIFIED`, `NOT_CHECKED`, ...) never change.
- Opinion translation viewer on the same page: paste opinion text, split
  by paragraph, with an original-vs-translation side-by-side view and a
  prominent machine-translation warning in all 3 languages. The
  **original text prevails** and the translation is **not legal advice**.
- CLI `--lang en|es|zh`: translates report headings only; the English
  disclaimer in every report stays authoritative.

What is NEVER translated (verbatim preservation, `web/translate.js`):

- case names, full citations, reporter abbreviations, and numbers.
  They are masked out (placeholders) before any text leaves the browser
  and restored verbatim afterwards, reusing the citation patterns in
  `web/extract.js`. A node test proves protected spans survive a
  translation round trip unchanged.

Machine-translation limits (read before relying on any translation):

- Translation is **OFF by default**: there is no default endpoint, no
  shipped key, and no paid service. The page translates nothing locally.
  To enable it, the user enters their own LibreTranslate-compatible
  `/translate` URL; that pasted opinion text is then sent to that
  endpoint (and only there). With no endpoint configured, the page says
  so clearly instead of inventing translated text.
- v2 assumes the pasted opinion is in English. Legal machine
  translation can mistranslate holdings, negations, and conditions;
  Spanish output is generally stronger than Chinese for legal English,
  but neither is reliable for a filing decision. Always read the
  original. This viewer does not fetch opinions from CourtListener
  itself \u2014 the user pastes the text.
- No server, no cost, no token: v2 adds no backend and no
  CourtListener token use. Web citation checking still makes no API
  calls; the only network call v2 can ever make is the user's own
  translation endpoint, only when they configure one.

### Query auto-translation (v2 behaviour)

On a Chinese or Spanish UI, clicking search automatically translates the
query to English and then searches the English query -- the user never
has to translate by hand. The search panel and the results area both keep
two lines: the original query and the auto-translated English query.
The English query is editable: if the user spots a mistranslation, they
edit the English query and click "Search with this English query" to
re-search without re-translating. On an English UI no translation is
applied. Citation-format content (volume, reporter abbreviation, page)
and numbers are masked before translation and restored verbatim, so
`347 U.S. 483 (1954)` can never come back as a translated or renumbered
cite. Query translation shares the opinion viewer's user-supplied
LibreTranslate-compatible endpoint setting (source = UI language,
target = English). If no endpoint is configured, or translation fails,
the page says so plainly, generates no English query, claims no English
search, and runs citation extraction on the original query only -- a
fake or guessed translation is never used as a search query.
