# Labels

| Label | Meaning | What to do next |
|---|---|---|
| `VERIFIED` | Found in CourtListener and the case name matches. | Still read it: this does not mean it supports your point or is good law. |
| `CITED` | Found in CourtListener; name not compared or only partly matches. | Open the link and confirm the case name and holding. |
| `AMBIGUOUS` | This cite matches more than one case. | Open the candidates and pick the one you meant; add the case name. |
| `MISMATCH` | A case exists at this cite, but it is a different case from the one named. | Likely a wrong volume/page or wrong case; find the correct cite. |
| `NOT_FOUND` | Valid citation format, but CourtListener has no case at this cite. | Find the case in an official reporter or another database before relying on it; if you can't find it anywhere, remove it. |
| `INVALID_REPORTER` | The reporter abbreviation is not a recognized reporter. | Check the abbreviation; the cite may be mistyped or invalid. |
| `RATE_LIMITED` | Not checked: the lookup service asked us to slow down. | Re-run later. |
| `NOT_CHECKED` | Not checked (statute, id./supra, short cite, network error, browser mode). | Check by hand using the links. |

## Mapping from CourtListener

Per-citation API status: 200 → candidate `VERIFIED` (then name
comparison); 300 → `AMBIGUOUS`; 404 → `NOT_FOUND`; 400 →
`INVALID_REPORTER`; 429 → `RATE_LIMITED`; network error / 5xx / no
usable result → `NOT_CHECKED`.

## Name comparison (draft thresholds — NOT calibrated)

Normalize both names (lowercase, strip punctuation, drop `et al.`,
`v.`, `Inc.`, `LLC`, `Corp.`, `Co.`, `the`; expand `Dep't` →
department, `Ass'n` → association, `Comm'n` → commission, `Int'l` →
international, `Nat'l` → national), then token-set similarity
(rapidfuzz if installed, else a documented pure-Python fallback) plus
distinctive-token overlap.

- Score ≥ 85 → `VERIFIED`.
- Score ≤ 40 **and** no distinctive-token overlap → `MISMATCH`.
- Anything in between → `CITED`.
- Status 200 with no case name in the text (bare cite) → `CITED`.

Deliberate safety rule: a shared distinctive token alone never upgrades
to `VERIFIED`; it only blocks `MISMATCH` (downgrading to `CITED`). A
shared surname is not identity. The 85 / 40 thresholds are starting
values from the brief, not calibrated values — the v0.1 benchmark is
too small to calibrate them (see `VERIFICATION.md`).

## Only-downgrade rule

Strength: `VERIFIED` > `CITED` > `AMBIGUOUS`. Problem labels require
positive API evidence. Missing evidence never becomes a problem label.
