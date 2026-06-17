#!/usr/bin/env python3
"""Self-contained demo target for the sarah-ai eval.

This is a minimal stand-in for the real Sarah AI tool
(https://github.com/msstrategies/sarah-ai). It exists so the eval in this
public repo is runnable end to end without any private code or credentials.

The pattern it demonstrates is the important part: any agent-facing tool
should have a `--demo` mode that runs fully offline (no API keys), exits
cleanly, and emits deterministic output. That makes the tool testable in
a binary eval, which is what `eval.sh` checks.
"""
from __future__ import annotations

import argparse
import os
import sys


def run_demo() -> int:
    print("SARAH AI (demo mode)")
    print("-" * 40)
    # Deterministic, offline output. No network, no API keys.
    sample_leads = [
        {"name": "Acme Realty", "status": "qualified", "score": 87},
        {"name": "Harbor Homes", "status": "nurture", "score": 61},
        {"name": "Summit Properties", "status": "qualified", "score": 92},
    ]
    for lead in sample_leads:
        print(f"lead: {lead['name']:<20} status={lead['status']:<10} score={lead['score']}")
    print("-" * 40)
    print(f"processed {len(sample_leads)} leads in demo mode")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Sarah AI demo target")
    parser.add_argument("--demo", action="store_true", help="run offline demo mode")
    args = parser.parse_args()

    if args.demo:
        return run_demo()

    # Live mode would require credentials. This fixture refuses to pretend.
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("live mode needs OPENROUTER_API_KEY; run with --demo for offline mode", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
