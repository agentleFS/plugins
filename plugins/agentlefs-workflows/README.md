# agentleFS Workflows

Optional companion to the [agentleFS plugin](../agentlefs/README.md). That plugin connects your
agent to agentleFS and carries the skills and commands, and runs nothing on your computer. This one
adds lifecycle hooks and a helper script, for people who want their agent briefed on their
agentleFS projects automatically.

Install the agentleFS plugin first, then this one from the same marketplace:

```
/plugin marketplace add agentleFS/plugins
/plugin install agentlefs@agentlefs
/plugin install agentlefs-workflows@agentlefs
```

Codex and Cursor list it in the same marketplace. On Codex, review and trust the hooks through
the host's hook controls; installing the plugin does not trust them.

## What it runs

- **Hooks** (`hooks/`), listed below. They need Python 3.9 or newer and install no packages.
- **Scripts** (`scripts/`): `project_hooks.py` and `decision_workflow.py`, which the hooks run,
  and `mandate_ballot.py`, the ballot formatter the `mandate-ledger` skill runs when you ask for
  a team ballot. Standard library only; none of them opens a network connection.

No hook records your prompts, tool calls or replies, and nothing is saved to agentleFS unless you
ask. What the hooks inject only describes and suggests: nothing tells the agent to act without
your request, to skip asking you, or to write to agentleFS unless you ask.

## Hooks

A project is a folder marked as one: its brief is the folder's `AGENTS.md`, its conversation is
the folder's discussion, and whoever can read the folder is a member. The agentleFS plugin's
`projects` skill starts one and runs it; these hooks keep the agent aware of it.

| Event | Hook |
|---|---|
| `SessionStart` | Names the session's git repository (read with `git remote get-url origin`) so the agent can ask `brief_me` for projects that cover it, and says which skills can help: `proactive-assembly` when a task names no project, and `mandate-ledger` for team choices, offering to record a ballot only if you want the team to weigh in. No network call. |
| `UserPromptSubmit` | Two hooks. **(1)** An `mcp_tool` hook calls `brief_me` with `only: "projects"` on **every prompt**, over the session's own agentleFS connection, and adds what moved in your projects to the context (nothing when nothing did). This is a network call to the agentleFS server, and its answer is server-side content. **(2)** A local pattern match on the prompt: when it looks like an unnamed work ask (lost / UI / bug / feature), it suggests a soft entry mode and the `proactive-assembly` packet (skipped when a project is already named); when it looks like a team choice or a decision being made, it adds the `mandate-ledger` note above, and that acting on a decision is your call. No network call; no mode picker. |
| `Stop`, `SubagentStop` | Read from the session's transcript, no network call. An agent that marked a project thread taken and never reported it, or that was offered write-back targets and recorded nothing, is held back **once** (a `decision: block`) with a reminder to tell you and offer to record it. It writes nothing itself, and the second stop always goes through. |
| `PostToolUse` | From the transcript, no network call. A session that coordinates helpers or people through agentleFS twice without a project is told once that it could be one (and to ask you before starting one); multi-agent sends without a wait get one pointer to `swarm-board`. After reading a decision, proposing one, or writing an execution report, a short note about the decision workflow. |

The decision notes also append bounded local diagnostics (event name and outcome, never
content) to `~/.agentlefs/plugin-memory/decision-observations.jsonl` (or under
`AGENTLEFS_MEMORY_HOME`), rotated at 256 KiB. Nothing is sent anywhere.

Claude Code and Codex read separate hook files (`hooks/hooks.json`,
`hooks/codex-hooks.json`) because they name the plugin's server differently in
an `mcp_tool` hook, and Codex alone reads `commandWindows`; the two files are
otherwise the same. On Codex, review and trust the hooks through the host's hook
controls; installing the plugin does not trust them. Cursor reads
`hooks/cursor-hooks.json` (camelCase events, flat `command` hooks, `--platform cursor`):
`sessionStart`, `postToolUse`, `stop` and `subagentStop`. Cursor has no `mcp_tool` hook
type and cannot inject on `beforeSubmitPrompt`, so the per-prompt `brief_me only=projects`
call and the `assemble` suggestion stay Claude/Codex-only; `sessionStart` still names the
repository and the skills. The hooks need Python 3.9 or newer and install no packages.

The Antigravity companion (the mirror's `antigravity-workflows/` folder) carries its own
`hooks.json` with `--platform antigravity`: `SessionStart` runs the session-start hook
and `PreInvocation`, on the first model call of each turn, the prompt hook. Antigravity
has no `mcp_tool` hook, so there is no per-prompt `brief_me` call there; its `PostToolUse`
output is ignored, so there is no nudge; and its `Stop` has no flag saying the agent was
already held once, so the stop reminder is left out rather than risk a loop.

## Links

- Documentation: https://agentlefs.com/docs/connect
- Privacy: https://agentlefs.com/privacy
- Terms: https://agentlefs.com/terms
- Support: https://agentlefs.com/support

MIT licensed.
