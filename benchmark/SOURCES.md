# Sources

- Discovery source for bad candidates: AI Hallucination Cases Database,
  Damien Charlotin, https://www.damiencharlotin.com/hallucinations/
  (CC BY 4.0, with attribution; page last updated 2026-10-25, read
  2026-10-26 — see VERIFICATION.md). Used as a pointer to court
  decisions only. The author also sells a commercial checker
  (PelAIkan); this project does not use, copy, or endorse it, and does
  not contact the author.
- CourtListener citation-lookup documentation:
  https://wiki.free.law/c/courtlistener/help/api/rest/v4/citation-lookup
- CourtListener terms: https://free.law/membership/allowed-api-usage/

## Seed provenance (v0.1, pending live verification)

- Grobler v. Kentucky Housing Corp. (Ky. Ct. App., 2026-10-02):
  brief summary says the court called three Kentucky cases nonexistent.
  Decision URL: not in the brief; to be added when the decision is
  fetched. Do not invent a URL.
- Nantongo v. Nationwide Mortgage Bankers (E.D.N.Y., 2026-09-30):
  brief summary says two citations had wrong volume/page numbers
  pointing to unrelated cases; the court found these were typos, not
  AI. The benchmark tests the citation only, not intent. Decision URL:
  not in the brief; to be added when the decision is fetched.
- Real controls (U.S. / S. Ct.): well-known Supreme Court citations
  used as replay fixtures only. Their live CourtListener status is
  pending the token run; if the live run contradicts a fixture, the
  fixture — not the live result — is what gets corrected.
