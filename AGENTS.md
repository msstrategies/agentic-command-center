# AGENTS.md

Portable agent instructions for this workspace. Works across any agent tool (Claude Code, Cursor, Codex, Windsurf). The detailed instructions live in `.claude/rules/`; this file is the short, tool-agnostic summary.

## What this workspace is

A skill-driven agentic engineering workspace. Skills are the primary unit of capability, specialized agents handle isolated roles, and deterministic scripts do the mechanical work so the model focuses on decisions.

## How to work here

- **Operating mode: autonomous.** Self-heal every solvable error (install, permission, credential, retry) before reporting. 3 attempts, then escalate. See `.claude/rules/autonomous-self-healing.md`.
- **Skills first** (`.claude/skills/`). Match the request to a skill before writing anything from scratch.
- **Specialized roles** live in `.claude/agents/`. Use the conductor agent to route multi-step tasks.
- **Push complexity into scripts.** Errors compound; deterministic code is testable.
- **Binding rules auto-load** from `.claude/rules/`. Read them before non-trivial work.

## Hard conventions (non-negotiable)

- **No em-dashes** in any output. Use a hyphen, a period, parentheses, or a comma.
- **Never hardcode secrets.** Always reference `.env` (gitignored). Never commit or publish `.env`.
- **Idempotent scripts only.**
- **Production quality only.** No drafts, placeholders, or `[NAME]` tokens in final output.
- **Package age guard:** never install a dependency first or last published within 14 days. See `.claude/rules/package-age-guard.md`.
- **Evidence before claims:** run the verification command before saying anything passes. See the `verification-before-completion` skill.

## Pointers

- Binding rules: `.claude/rules/*.md`
- Skills: `.claude/skills/*/SKILL.md`
- Agents: `.claude/agents/*.md`
- Evals: `evals/run_evals.sh`
- Guardrail hooks: `hooks/`
