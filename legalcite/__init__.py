"""legalcite: check whether a cited case exists in CourtListener and
whether the case name matches. Nothing more.

This package never checks whether a case supports an argument, whether
quotes or pin cites are accurate, or whether a case is still good law.
"""

__version__ = "0.1.0"

DISCLAIMER = (
    "Not legal advice. This tool only checks whether a cited case exists in "
    "CourtListener and whether the case name matches. It does not check "
    "whether the case supports your argument, whether quotes or pin cites "
    "are accurate, or whether the case is still good law. A case marked "
    "NOT FOUND may still exist (CourtListener's coverage is incomplete); "
    "a case marked VERIFIED may still be wrong for your purpose. "
    "Read every case you cite."
)

# Words that must never be used to describe a user's citation.
FORBIDDEN_LABEL_WORDS = ("fabricated", "fake", "hallucinated")
