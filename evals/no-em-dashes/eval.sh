#!/usr/bin/env bash
# Binary eval: the repo contains zero em-dashes (U+2014) or en-dashes (U+2013).
# Enforces the AGENTS.md "No em-dashes in any output" rule in the harness itself,
# not just as prose. A non-negotiable that is stated but not enforced is a wish.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python3 - "$ROOT" <<'PY'
import os, sys
root = sys.argv[1]
DASHES = (chr(0x2014), chr(0x2013))
bad = []
for dp, _, fns in os.walk(root):
    if os.sep + ".git" in dp:
        continue
    for fn in fns:
        p = os.path.join(dp, fn)
        try:
            t = open(p, encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        if any(d in t for d in DASHES):
            bad.append(os.path.relpath(p, root))
if bad:
    print("em-dash/en-dash found in:")
    for b in bad:
        print("  ", b)
    sys.exit(1)
sys.exit(0)
PY
