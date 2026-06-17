# Subagent SOP (context-saving default)

**Goal:** keep the main thread lean. Raw tool output (logs, file dumps, web crawls, multi-route checks) stays inside subagents. Only their summary returns to the parent.

## Decision triple (run before any task with more than 2 tool calls)

Ask three questions:

1. **Output size.** Will raw tool output exceed about 2 KB and not be needed verbatim downstream?
2. **Branching.** Are there 3 or more independent sub-tasks (parallel searches, parallel verifications)?
3. **Exploration.** Is the path unclear, with multiple approaches to try?

Any YES means dispatch a subagent. All NO means execute directly.

Decide autonomously. Do not ask the user "should I use a subagent". That defeats the purpose.

## Agent-type selection

| Trigger | Type | Tools |
|---|---|---|
| "Where is X / which files reference Y" | `Explore` | Read-only, fast |
| Multi-step verification (URLs, endpoints, routes, files) | `general-purpose` | Full suite |
| API / library / CLI research before implementing | `researcher` | Read + WebFetch + WebSearch |
| Bug with unclear root cause | `debugger` | Systematic isolation |
| Independent second opinion on a diff | `code-reviewer` | Read + Grep + Bash |
| Architecture or strategy before non-trivial implementation | `Plan` | Read-only design |

When the task fits no specialized type, default to `general-purpose`.

## Parallelism rules

- Independent subagents go in a single message with multiple `Agent` tool calls. They run concurrently.
- Sequential work (output of A feeds B) runs serially. Do not fake parallelism.
- Long-running and truly independent work uses `run_in_background: true`. Continue with other work, get notified at completion.
- Cap at 3 to 4 parallel subagents. Beyond that, cold-start overhead beats the gain.

## Defaults

| Situation | Default |
|---|---|
| Codebase sweep across 3 or more files or unknown locations | `Explore` |
| Small, targeted lookups in short reference files | Direct Read |
| Multi-route deploy verification | `general-purpose` with the route list, returns pass/fail per route |
| API or library exploration before implementing | `researcher` first, then direct implementation |
| Multi-agent review or security flows | Their own flows, invoked directly |

## Never use a subagent for

- A single Bash call (`git status`, `ls`, `whoami`).
- A Read of a file you will immediately Edit (you need the raw content in the main context).
- Skill invocations and slash commands (those route through the harness, not the Agent tool).
- Anything where the user wants intermediate visibility. Subagents are blocking, with no live feedback during their run.

## Prompt-writing rules for subagents (they have zero context)

- State the goal in one sentence.
- Hand over exact paths, IDs, URLs, and env var names (never paste secrets into the prompt itself).
- Specify the report format and a length cap ("under 200 words", "pass/fail per route", "diff only").
- Tell them whether to write code or just research.
- For long-running work, end with the explicit deliverable.

## Self-correction

At the end of a turn: if you made more than 5 main-thread tool calls and more than 5 KB of raw output landed in the main context and a subagent could have absorbed it, that was a miss. Note the pattern and refine this SOP if the trigger generalizes.
