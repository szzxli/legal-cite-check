# Verification record — checked 2026-10-26

Every item below was checked by this build on 2026-10-26 (America/Los_Angeles)
using public web search / page reads. Nothing from the Grok brief is
treated as confirmed unless it appears here as CONFIRMED with a source.
Items marked UNCONFIRMED remain open and must be resolved before the
claim that depends on them is published as fact.

## CONFIRMED

- **CourtListener citation-lookup endpoint, statuses, limits.**
  Source: https://wiki.free.law/c/courtlistener/help/api/rest/v4/citation-lookup
  (published 2026-04-25, updated 2026-04-27, read 2026-10-26).
  POST `https://www.courtlistener.com/api/rest/v4/citation-lookup/` with
  `Authorization: Token <token>` and form field `text=` (or
  volume/reporter/page). Per-citation `status`: 200 found, 404 not
  found, 400 reporter not recognized, 300 multiple matches, 429 too
  many in one request. Limits: 60 valid citations/minute, 250 citations
  per request, 64,000 characters per text request. Does not look up
  statutes, law journals, `id.`, or `supra`. Cluster objects carry
  `case_name` (shown in the ambiguous-citation example).
- **Throttle key spelling `wait_util`.** Same wiki page: "The JSON object
  will contain a `wait_util` key that uses an ISO-8601 datetime".
  The client also accepts `wait_until` defensively, but `wait_util` is
  the documented spelling.
- **Free Law Project membership API allowed use.**
  Source: https://free.law/membership/allowed-api-usage/ (read 2026-10-26).
  Personal, educational, research, journalistic, exploratory use; solo
  practitioners and firms with ≤5 attorneys welcome; may NOT power a
  revenue-positive commercial product/service/feature; internal tools
  for organizations count as commercial; >5 attorneys need a commercial
  agreement; one person, one account; do not share API keys.
- **Charlotin AI Hallucination Cases Database licence CC BY 4.0.**
  Source: https://www.damiencharlotin.com/hallucinations/ (last updated
  2026-10-25, read 2026-10-26): "Licence CC BY 4.0 — free to reuse,
  including commercially, with attribution. Cite as: AI Hallucination
  Cases Database, Damien Charlotin, https://www.damiencharlotin.com/hallucinations/."
  This corrects the brief's `[UNCONFIRMED]` on the licence. The database
  is still used here only as a pointer to court decisions; seed court
  findings are NOT independently re-verified in this build (see open
  items). Note: the author also sells a commercial checker (PelAIkan);
  this project does not use, copy, or endorse it.
- **eyecite licence BSD-2-Clause.** PyPI project description says
  "available under the permissive BSD license"; Cloudsmith Navigator
  for eyecite lists BSD-2-Clause. (Version caveat below.)
- **rapidfuzz licence MIT.** PyPI project page: "RapidFuzz is licensed
  under the MIT license"; Cloudsmith Navigator for rapidfuzz lists MIT.
  Latest release seen in search: 3.14.6 (2026-08-30).
- **reporters-db licence description (not relied upon).** PyPI pages for
  reporters-db state "available under the permissive BSD license".
  This was NOT treated as sufficient for the data file (see below).

## PARTIALLY CONFIRMED / NOT RELIED UPON

- **reporters-db / courts-db data licences.** PyPI says BSD for the
  package, but whether that covers the generated JSON data file, and
  whether the free.law site's CC BY-ND footer applies to it, was not
  separately confirmed. **Therefore v0.1 does NOT bundle reporters-db
  data.** It ships a small hand-written reporter table
  (`scripts/reporter_table.py` → `web/reporters.json`). Full-dataset
  bundling is an open item requiring a primary-source licence check.
- **CourtListener cluster field set.** `case_name` is confirmed from
  the wiki example. `date_filed` and `absolute_url` are standard
  cluster fields in CourtListener documentation generally, but the
  exact field set of a citation-lookup response was not inspected from
  a live response (no token in this build). The client handles missing
  fields gracefully (empty string) rather than crashing.
- **CourtListener /c/ slug mapping.** Only `us`, `f-appx`, and `sw3d`
  are confirmed from brief/wiki examples. All other reporters fall back
  to the unslugged `/c/<reporter>/<volume>/<page>/` link, which the
  brief reports as redirecting correctly — that redirect claim itself
  is UNCONFIRMED by this build.

## UNCONFIRMED (open items)

1. **eyecite version 2.7.8.** Latest versions seen in search: 2.7.5
   (2025-05-22) and 2.7.6. The brief's "2.7.8 on PyPI on 2026-10-26" was
   NOT confirmed. `pyproject.toml` therefore pins only `eyecite>=2.7`
   as an optional extra, and extraction does not depend on it.
2. **rapidfuzz exact version to pin.** MIT is confirmed; no single
   version is claimed as "the" version. `pyproject.toml` uses
   `rapidfuzz>=3.0` as an optional extra with a pure-Python fallback.
3. **Unauthenticated POST returns 401.** Brief claim; not tested in
   this build (no live request was made, and no token was created or
   used). The client treats 401/403 generically as AuthError.
4. **Exact rate limits for a new free (non-member) account.** The
   citation-lookup throttle (60 valid citations/minute) is confirmed
   above, but general REST defaults (e.g. 5 requests/minute in older
   docs) and any newer lowered defaults for new accounts were not
   reconciled. Do not conflate the two. The live run will reveal the
   effective limits; the client respects HTTP 429 regardless.
5. **Browser CORS for citation-lookup POST.** The brief claims a
   preflight allowing only GET/HEAD/OPTIONS. Search in this build did
   not confirm it. It does not matter for v0.1: the web page is
   call-free by design regardless of what CORS would allow.
6. **Google Scholar search URL form.** The `scholar.google.com/scholar?q=`
   link in the web page is provisional (a manual-check link only) and
   was not confirmed as the best URL form.
7. **Seed court findings (Grobler, Nantongo).** The brief's summaries
   (three nonexistent Kentucky cases; two wrong volume/page numbers)
   have NOT been re-verified against the court decisions in this build.
   Decision URLs are deliberately left null in `seed/bad.jsonl` rather
   than invented. Live verification is the blocker for any accuracy claim.
8. **Name thresholds 85 / 40.** Draft starting values from the brief,
   NOT calibrated. The v0.1 seed (n=11 scored) is too small to
   calibrate. Do not describe them as calibrated.
9. **State-reporter coverage and .docx-in-browser.** Out of scope for
   v0.1; the reporter table covers 13 reporters and the browser accepts
   paste / `.txt` only.
10. **eyecite C-dependency behaviour in the browser (Pyodide).**
    Not applicable to v0.1: the browser uses its own JS extractor.
11. **Repo-name collision re-check at push time.** The parent agent
    reported no exact `szzxli/legal-cite-check` collision and similar
    projects with different names. Re-check immediately before any
    future push; this local build creates no repo and does not push.

## Deliberate deviations from the brief (documented, safety-first)

- **Distinctive-token overlap does not upgrade to VERIFIED.** The
  brief's section 6 can be read as "overlap → VERIFIED". That would let
  a shared surname verify a different case. v0.1 implements the safer
  reading: overlap only blocks MISMATCH (downgrade to CITED). This is
  strictly weaker, consistent with the only-downgrade rule.
- **No reporters-db data bundled** (see partially-confirmed section).
- **Benchmark replay uses mock fixtures**, explicitly labelled, because
  no live run is possible without a user-supplied token. No live run
  is claimed anywhere in this tree.
