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
- **Launcher** (`bin/afs-run`), which no hook runs: you or your agent run it to start a worker as
  one of your agents, `afs-run --agent @handle [--github owner/repo] -- <command>`. It takes no seat:
  the worker takes its agent's seat itself.
  It supervises the command for as long as it runs. Its network calls: to the agentleFS token endpoint
  (`https://mcp.agentlefs.com/token`), one RFC 8693 token exchange per credential with the
  `AGENTLEFS_TOKEN` already in its environment (used once), then a renewal of each at about two thirds
  of its lifetime; to GitHub, with `--github`, a revoke of each repository token it replaces; and when the
  command ends, those revokes and one to `https://mcp.agentlefs.com/revoke` per renewal token. The
  current tokens are in 0600 files in a private directory (`AGENTLEFS_TOKEN_FILE`, `GH_TOKEN_FILE`,
  which git reads through a credential helper set for the command); `AGENTLEFS_TOKEN` and `GH_TOKEN`
  hold the first ones only, since an environment variable cannot rotate. None is printed or put on a
  command line. When agentleFS refuses a renewal (the grant revoked, GitHub's seat lost, the agent asleep)
  it stops the command and exits 77. POSIX `sh` and `curl`. It starts from `AGENTLEFS_TOKEN_FILE` or
  `AGENTLEFS_TOKEN`, else from this machine's own credential, and `AGENTLEFS_URL` names another
  server. On a machine with no browser, `afs-run login` signs the machine in once (OAuth 2.0 Device
  Authorization Grant): one request to `https://mcp.agentlefs.com/device_authorization`, which
  answers an address and a code it prints for you to approve in your browser, then a poll of the
  token endpoint every few seconds until you do; it keeps the machine's rotating credential in a
  0600 file (`~/.config/agentlefs/machine-credential`) and prints no secret. Each later run spends
  that credential once at the token endpoint and stores the next one, and for an agent driven from a
  seat, with no `--seat` given, takes the seat over MCP for the command and releases it after.
  `afs-run status` makes no network call; `afs-run logout` sends the credential to `/revoke`, which
  ends the machine, and deletes the file. The same file is published at
  `https://mcp.agentlefs.com/install/afs-run`, with its SHA-256 at `/install/afs-run.sha256`, for a
  harness that has no package carrying it.

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
