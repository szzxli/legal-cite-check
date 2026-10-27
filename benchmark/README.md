# Benchmark v0.1

Small seed set. All rates are **signals, not rates**: report counts with
sample sizes and list every miss / false alarm by id.

## Status of this seed — read before citing any number

- **Live verification: PENDING.** No CourtListener token was created or
  used for this build, so no live run has happened. Every seed entry's
  court finding is taken from the brief's summary of the Charlotin
  database pointer and has **not** been independently re-verified
  against the court decision in this build.
- **Replay fixtures are MOCK.** `benchmark/recorded/` contains
  hand-written mock payloads shaped like CourtListener responses. They
  are NOT real CourtListener payloads. `recorded/README.md` says so, and
  `run.py --mode replay` labels its output `mode: replay (mock)`.
- Do not quote replay catch rates as real-world accuracy. The replay
  only proves the labelling pipeline behaves as specified on known
  inputs. Real accuracy is unknown until the live run.

## Layout

- `seed/bad.jsonl` — 5 bad-citation candidates (3 Grobler, 2 Nantongo).
- `seed/real.jsonl` — 6 real controls with mock fixtures + 7 pending
  placeholders (one per remaining reporter family) with no fixture.
  Placeholders are counted as `pending`, never as misses.
- `recorded/` — mock fixtures for replay.
- `run.py` — replay (default/auto without token) or live (token set).
- `score.py` — counts, catch rate, false-alarm rate, coverage, misses.
- `results/` — committed replay output from this build.
