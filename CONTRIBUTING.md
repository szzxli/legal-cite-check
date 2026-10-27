# Contributing — iron rules

1. **Honest labels, always.** A label claims only what the evidence
   supports. Existence in CourtListener is not support for an argument,
   not quote accuracy, and not good law.
2. **Only downgrade.** Uncertainty moves a label toward the weaker claim,
   never stronger. Missing evidence (rate limit, network error, parse
   doubt) gives RATE_LIMITED / NOT_CHECKED, never NOT_FOUND or MISMATCH.
3. **Never call a user's citation fabricated, fake, or hallucinated.**
   Use the label set in `docs/labels.md`. Those words judge intent and
   provenance; this tool checks existence and name match only.
4. **No user data stored.** The web page keeps text in memory only. The
   CLI sends CourtListener only extracted citation strings by default,
   never brief text. The `--send-full-text` flag stays off by default.
5. **No token ever committed, logged, or printed.** Tokens come from the
   user's own environment / Actions secret only. Tests must assert this.
6. **No commercial use of CourtListener membership data.** See
   `docs/courtlistener-terms.md`. No revenue-positive product, and no
   internal tooling for an organization, may be powered by membership
   API access without a separate Free Law Project agreement.
7. **No posting, promotion, or contacting anyone** on behalf of the
   project without the maintainer's explicit approval.
8. **Verify before claiming.** Anything marked `[UNCONFIRMED]` in
   `VERIFICATION.md` must be checked against a primary source before it
   is presented as fact. Small benchmark numbers are "signals, not rates".
