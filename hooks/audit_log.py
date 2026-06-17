#!/usr/bin/env python3
"""PostToolUse hook: append-only JSONL audit log of every tool call.

Writes one JSON record per tool invocation to:
    .claude/audit/YYYY-MM-DD.jsonl

Records:
    timestamp, tool_name, file_path (if Edit/Write/Read), command (if Bash, redacted)

For Bash commands, secret-shaped tokens are redacted before logging.
This hook never blocks. It always exits 0. Failures are silent.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
AUDIT_DIR = WORKSPACE / ".claude" / "audit"

# Patterns to redact from logged Bash commands (mirrors pre_edit_secret_scan)
SECRET_PATTERNS = [
    re.compile(r"\bsk-(?:proj-|ant-(?:api03|admin01)-)?[A-Za-z0-9_-]{30,}\b"),
    re.compile(r"\bpat-(?:eu1|na1|na2)-[A-Za-z0-9-]{20,}\b"),
    re.compile(r"\bpplx-[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgh[opsu]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{50,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{15,}\b"),
    re.compile(r"\bsbp_[A-Za-z0-9]{30,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
    re.compile(r"\bBearer\s+[A-Za-z0-9_.+/=-]{20,}\b", re.IGNORECASE),
    re.compile(r"\b\d{9,11}:[A-Za-z0-9_-]{30,}\b"),  # Telegram bot
]


def redact(text: str) -> str:
    if not text:
        return text
    for pat in SECRET_PATTERNS:
        text = pat.sub("<REDACTED>", text)
    return text


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input") or {}

    record = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tool": tool_name,
    }

    # Pick out a small set of useful, non-bulky fields per tool
    if tool_name == "Bash":
        record["command"] = redact(tool_input.get("command", ""))[:500]
        record["description"] = tool_input.get("description", "")[:200]
    elif tool_name in ("Edit", "Write"):
        record["file_path"] = tool_input.get("file_path", "")
    elif tool_name == "Read":
        record["file_path"] = tool_input.get("file_path", "")
    elif tool_name in ("WebFetch", "WebSearch"):
        record["url"] = tool_input.get("url", "")[:200]
        record["query"] = tool_input.get("query", "")[:200]
    else:
        # generic: just record the tool name
        pass

    try:
        AUDIT_DIR.mkdir(parents=True, exist_ok=True)
        log_path = AUDIT_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        with log_path.open("a") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        # Never block the session because of logging issues
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
