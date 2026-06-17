#!/usr/bin/env bash
# Binary eval runner. Iceberg coverage: "eval-driven loops".
# Convention: each skill/tool gets evals/<name>/eval.sh that exits 0 (pass) or non-zero (fail).
#
# Usage:
#   evals/run_evals.sh            # run all evals
#   evals/run_evals.sh sarah-ai   # run one
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EVAL_DIR="$ROOT/evals"
target="${1:-}"
pass=0; fail=0; failed=()

for ev in "$EVAL_DIR"/*/eval.sh; do
  [ -f "$ev" ] || continue
  name="$(basename "$(dirname "$ev")")"
  [ -n "$target" ] && [ "$target" != "$name" ] && continue
  if bash "$ev" >/dev/null 2>&1; then
    echo "PASS  $name"; pass=$((pass+1))
  else
    echo "FAIL  $name"; fail=$((fail+1)); failed+=("$name")
  fi
done

echo "----------------------------------------"
echo "pass=$pass fail=$fail"
if [ "$fail" -gt 0 ]; then echo "failed: ${failed[*]}"; exit 1; fi
exit 0
