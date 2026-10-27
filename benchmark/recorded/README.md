# Recorded fixtures — MOCK, not real CourtListener payloads

Every file in this directory is a hand-written mock shaped like a
CourtListener citation-lookup response. **None of these are real API
responses.** No CourtListener token was used to produce them, and no
live run has happened.

Purpose: let `run.py --mode replay` exercise the labelling pipeline
(status mapping, name comparison, only-downgrade) offline, in CI,
without a token and without network access.

When the live run happens (user-supplied token), live results go to
`benchmark/results/` with `mode: live` and must NOT overwrite these
mock fixtures. If a live result contradicts a mock fixture, the fixture
is wrong — fix the fixture and record the correction, do not hide it.
