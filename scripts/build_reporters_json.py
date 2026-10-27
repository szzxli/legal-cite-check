"""Generate web/reporters.json from scripts/reporter_table.py and sync
the embedded REPORTERS block in web/extract.js (between the GENERATED
markers). Do not hand-edit web/reporters.json or that block.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from reporter_table import REPORTERS  # noqa: E402


def main():
    out = ROOT / "web" / "reporters.json"
    out.write_text(json.dumps({"reporters": REPORTERS}, indent=2) + "\n", encoding="utf-8")
    js = ROOT / "web" / "extract.js"
    text = js.read_text(encoding="utf-8")
    # `var` (not const) so Node tests can eval this file and see REPORTERS.
    block = "var REPORTERS = " + json.dumps(REPORTERS, indent=2) + ";"
    new, n = re.subn(
        r"/\* BEGIN GENERATED REPORTERS \*/.*?/\* END GENERATED REPORTERS \*/",
        "/* BEGIN GENERATED REPORTERS */\n" + block + "\n/* END GENERATED REPORTERS */",
        text, flags=re.S)
    if n != 1:
        raise SystemExit("extract.js GENERATED markers not found exactly once")
    js.write_text(new, encoding="utf-8")
    print(f"wrote {out} and synced extract.js ({len(REPORTERS)} reporters)")


if __name__ == "__main__":
    main()
