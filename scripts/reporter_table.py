"""Canonical small reporter table for v0.1.

Deliberately NOT the full reporters-db dataset: reporters-db's data-file
licence was not separately confirmed (see VERIFICATION.md), so v0.1
ships only this small hand-written table of reporters used by the
benchmark plus common federal/state reporters. Slugs are only filled
in where confirmed in the brief / CourtListener examples
(us, f-appx, sw3d); other reporters fall back to the unslugged
/c/<reporter>/<volume>/<page>/ link, which the brief reports as
redirecting correctly. Slug mapping for the rest is an open item.
"""

REPORTERS = [
    {"abbreviation": "U.S.", "slug": "us"},
    {"abbreviation": "S. Ct.", "slug": None},
    {"abbreviation": "F.2d", "slug": None},
    {"abbreviation": "F.3d", "slug": None},
    {"abbreviation": "F.4th", "slug": None},
    {"abbreviation": "F. Supp. 2d", "slug": None},
    {"abbreviation": "F. Supp. 3d", "slug": None},
    {"abbreviation": "F. App'x", "slug": "f-appx"},
    {"abbreviation": "S.W.3d", "slug": "sw3d"},
    {"abbreviation": "S.W.2d", "slug": None},
    {"abbreviation": "N.E.3d", "slug": None},
    {"abbreviation": "N.E.2d", "slug": None},
    {"abbreviation": "P.3d", "slug": None},
    {"abbreviation": "P.2d", "slug": None},
    {"abbreviation": "So. 3d", "slug": None},
    {"abbreviation": "So. 2d", "slug": None},
    {"abbreviation": "Cal. Rptr. 3d", "slug": None},
    {"abbreviation": "Cal. Rptr. 2d", "slug": None},
]
