#!/usr/bin/env bash
# Binary eval: the tool's demo mode runs offline (no API keys) and produces output.
#
# This is the eval-driven loop in its smallest form: a deterministic pass/fail
# check that a tool behaves correctly with zero credentials. The target here is
# a self-contained fixture standing in for the real Sarah AI project
# (https://github.com/msstrategies/sarah-ai), so the check runs anywhere.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT="$HERE/demo_target.py"

[ -f "$SCRIPT" ] || { echo "demo_target.py missing"; exit 1; }

# Must run with no keys, exit cleanly, and emit the banner plus a demo marker.
out="$(APIFY_API_KEY="" OPENROUTER_API_KEY="" ANTHROPIC_API_KEY="" \
  python3 "$SCRIPT" --demo 2>&1)" || { echo "demo run errored"; exit 1; }

echo "$out" | grep -qi "SARAH AI" || { echo "missing banner"; exit 1; }
echo "$out" | grep -qiE "demo|lead" || { echo "missing demo output"; exit 1; }
exit 0
