#!/usr/bin/env python3
"""PreToolUse:Edit|Write hook: block writes that would introduce secrets.

Scans the new content (Edit.new_string or Write.content) against known secret
patterns. Blocks the write if a match is found.

A path allowlist permits files where example tokens legitimately appear
(skill docs, examples, .env.example).

Exit codes:
- 0  allow
- 2  block (the agent sees the stderr message)
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Path allowlist: example and documentation files where tokens may appear.
ALLOWED_PATH_RE = re.compile(
    r"("
    r"\.env\.example$|"
    r"\.mcp\.json\.example$|"
    r"\.claude/skills/.*|"
    r"/examples/|"
    r"CHANGELOG\.md$"
    r")"
)

# Secret patterns (high-precision, low false-positive).
SECRET_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("openai-key", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{32,}\b")),
    ("anthropic-key", re.compile(r"\bsk-ant-(?:api03|admin01)-[A-Za-z0-9_-]{40,}\b")),
    ("hubspot-pat", re.compile(r"\bpat-(?:eu1|na1|na2)-[A-Za-z0-9-]{30,}\b")),
    ("perplexity-key", re.compile(r"\bpplx-[A-Za-z0-9]{32,}\b")),
    ("aha-token", re.compile(r"\b[a-z0-9]{5}_[A-Za-z0-9]{32,}\b")),
    ("manus-key", re.compile(r"\bsk-[A-Za-z0-9_-]{60,}\b")),
    ("github-pat", re.compile(r"\bgh[opsu]_[A-Za-z0-9]{30,}\b")),
    ("github-fine-grained", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{80,}\b")),
    ("supabase-token", re.compile(r"\bsbp_[A-Za-z0-9]{40,}\b")),
    ("telegram-bot-token", re.compile(r"\b\d{9,11}:[A-Za-z0-9_-]{30,}\b")),
    ("stripe-live-secret", re.compile(r"\bsk_live_[A-Za-z0-9]{24,}\b")),
    ("aws-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    ("notion-internal", re.compile(r"\bsecret_[A-Za-z0-9]{40,}\b")),
    ("elevenlabs-key", re.compile(r"\bxi_api_key=[A-Za-z0-9]{40,}\b", re.IGNORECASE)),
    ("private-key-block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
]


def is_path_allowed(path: str) -> bool:
    """True if path is in the allowlist (skill docs, examples, etc.)."""
    return bool(ALLOWED_PATH_RE.search(path))


def scan(text: str) -> list[tuple[str, str]]:
    """Return list of (pattern_name, redacted_match) for any secrets found."""
    findings = []
    for name, pat in SECRET_PATTERNS:
        for m in pat.finditer(text):
            value = m.group(0)
            redacted = value[:6] + "…" + value[-4:] if len(value) > 14 else "<short>"
            findings.append((name, redacted))
    return findings


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        # Malformed input: allow rather than break the session.
        return 0

    tool_input = payload.get("tool_input", {})
    tool_name = payload.get("tool_name", "")

    file_path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""

    # Only scan Edit / Write
    if tool_name == "Edit":
        new_text = tool_input.get("new_string", "") or ""
    elif tool_name == "Write":
        new_text = tool_input.get("content", "") or ""
    else:
        return 0

    if not new_text:
        return 0

    if file_path and is_path_allowed(file_path):
        return 0  # documentation or example: allowed

    findings = scan(new_text)
    if not findings:
        return 0

    # Block. Write a clear message the agent can read on stderr.
    rules = ", ".join(sorted({name for name, _ in findings}))
    print(
        f"BLOCKED: pre_edit_secret_scan detected secret-shaped tokens "
        f"in the proposed write to {file_path or '<unknown>'} (rules: {rules}). "
        f"Move the value to .env and reference it via os.environ[]. Never inline it.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
