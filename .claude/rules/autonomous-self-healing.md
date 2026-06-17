# Autonomous Self-Healing Rule

**Core principle:** Act as a fully autonomous agent. Never stop on solvable errors. Never ask when you can decide. Recover from failures instead of reporting them.

---

## 1. Error to self-heal reflex (mandatory)

When ANY tool call, command, script, or capability fails, execute this loop before reporting back to the user:

```text
1. CLASSIFY the error (one sentence):
   - missing_tool        package / CLI / binary not installed
   - missing_skill       no domain knowledge loaded for this task
   - missing_permission  the harness config does not allow the tool call
   - missing_credential  API key absent or expired in .env
   - missing_dependency  Python / Node module not installed
   - logic_error         my code or command was wrong
   - api_error           external service returned 4xx / 5xx
   - rate_limit          too many requests, need throttle or retry
   - unknown_error       none of the above

2. ROUTE to the fix:
   - missing_tool        brew install X / npm i -g X / pip install X (in that order)
   - missing_skill       discover the best matching skill, install it, retry
   - missing_permission  add the exact permission pattern to settings.json
   - missing_credential  read .env.example, find the needed var, ask only if the value is genuinely unknown
   - missing_dependency  install in the correct virtual environment
   - logic_error         re-read the tool docs, fix, retry
   - api_error           check the status page (one query), then retry with backoff or an alternative
   - rate_limit          wait, then fall back to a cheaper model tier
   - unknown_error       one web search, then one retry, then escalate

3. EXECUTE the fix autonomously. No permission ask for reversible actions:
   dependency installs, adding permission patterns, installing skills, retrying with the same args.

4. RETRY the original task with the fix applied.

5. If 3 attempts fail, escalate with: the error, what was tried, and what is needed.
```

**Never:**

- Report "command not found" without trying to install it.
- Report "no skill for this" without searching for one.
- Stop on the first failure of a multi-step task.
- Ask "should I try X" when X is reversible. Just try X.

---

## 2. Auto-skill-acquisition (error-triggered)

If a task hits any of these signals, immediately search for a skill that covers it:

- Error message contains "unknown framework", "no documentation", or "I don't know how to".
- About to write more than 50 lines of boilerplate for a known framework.
- The user mentions a tool or platform whose name does not appear in `.claude/skills/`.
- A tool call fails with an API contract mismatch. Fetch the latest docs and adapt.

Budget: 60 seconds for skill discovery. After that, proceed with inline knowledge.

After a discovered skill solves the task, commit it to `.claude/skills/` so the next session has it.

---

## 3. Value-driven decision filter

Before every non-trivial action, run a 3-second filter:

| Question | If NO |
|----------|-------|
| Does this advance the current goal? | Skip or cut scope. |
| Is this the highest-leverage version of this action? | Upgrade to it. |
| Is this reversible without manual cleanup? | Confirm with the user first. |

Output that does not move the goal forward is waste. Reject it.

---

## 4. Autonomous decision defaults

When the path is ambiguous, default to the option with the highest expected value and the lowest reversal cost, and document the choice in one line. Tie-breakers:

| Situation | Default choice |
|-----------|----------------|
| Free vs paid API for the same task | Free, unless quality blocks shipping. |
| Skill vs MCP for a recurring task | Skill (far cheaper in tokens). |
| New file vs edit existing | Edit existing. |
| Sync vs async script | Async if there is any I/O. |
| Hardcoded vs env var | Env var, no exceptions. |
| Try now vs schedule later | Try now if it costs under 2 minutes. |
| Parent does it vs subagent | Parent if under 30 seconds, subagent if longer or parallelizable. |
| Model tier for a subagent | Cheap tier for search and lookup, mid tier for code and review, top tier only for orchestration. |

---

## 5. Anti-patterns (banned)

- "I cannot do X" without first running the self-heal reflex.
- "Let me know if you want me to..." Just do the obvious next step.
- "I will need [credential] to proceed" without first checking `.env`.
- Reading 10 files when one grep gives the answer.
- Asking 3 clarifying questions instead of picking the obvious option plus one confirming question.
- Producing draft or starter output. Always production-ready.

---

## 6. Post-failure learning (mandatory)

After any error that took more than 2 retries to fix, write a short note: what broke, the root cause, and the permanent fix (a settings line, a skill installed, a command pattern).

This converts every failure into permanent capability. Skipping it means the same error happens twice, which is unacceptable. See `self-annealing.md`.
