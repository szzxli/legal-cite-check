# legal-cite-check — does the case you cited exist, and is it the case you named?

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
