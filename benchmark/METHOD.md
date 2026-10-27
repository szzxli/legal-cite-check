# Benchmark method (v0.1)

## Seed construction (planned, not yet completed live)

1. Bad candidates: use the Charlotin AI Hallucination Cases Database
   only as a **pointer list** to court decisions. For each candidate,
   open the court's own decision and copy the citation exactly as the
   court quotes it. Record the court's finding in your own words, not
   the database's wording. This step is **pending** for v0.1: the seed
   below carries the brief's summaries, marked as such.
2. Real controls: real cases confirmed by a human in CourtListener.
   Also **pending** for the live run; replay fixtures are mock.
3. Keep only citation strings, case names, links, and a one-line
   finding. No brief text, no user data.

## Running

- Replay (no token, no network): `python benchmark/run.py --mode replay`
- Live (token required): `python benchmark/run.py --mode live` with
  `COURTLISTENER_TOKEN` set. Live mode sends only citation strings.
- Auto: `python benchmark/run.py --mode auto` — live if a token is set,
  otherwise replay, and the output says which mode ran.

## Metrics (score.py)

- Catch rate on bad = share labelled `NOT_FOUND` / `INVALID_REPORTER` /
  `MISMATCH`.
- False-alarm rate on real = share labelled with any of those three.
- Coverage = share `NOT_CHECKED` / `RATE_LIMITED`.
- Extraction recall on a hand-annotated paragraph set (future work;
  v0.1 reports the unit-test extraction fixtures instead).
- Report counts per category **with the sample size**, list every miss
  and false alarm by id, version the set (`v0.1 — 2026-10-26`).

## Known limits (must stay in any report of results)

- CourtListener coverage gaps (especially state and unpublished cases)
  can make real cases `NOT_FOUND`.
- The tool does not check propositions or quotes, which is a large
  share of the problems courts describe.
- Name thresholds (85 / 40) are draft values, not calibrated; v0.1 is
  too small to calibrate them.
- The seed's court findings are not yet re-verified against the
  decisions themselves. A seed error is a benchmark error, not a tool
  error — and vice versa.
