# agentleFS Workflows for Antigravity

Optional companion to the agentleFS plugin for Antigravity (the mirror's `antigravity/` folder).
That plugin connects Antigravity to agentleFS and carries the skills, and runs nothing on your
computer. This one adds lifecycle hooks and a helper script.

## Install

Install the agentleFS plugin first, then this folder:

```
agy plugin install https://github.com/agentleFS/plugins/tree/main/antigravity
agy plugin install https://github.com/agentleFS/plugins/tree/main/antigravity-workflows
```

## What it contains

- **Lifecycle hooks** (`hooks.json`), listed below.
- **Scripts** (`scripts/`): the Python 3.9+ hook scripts, and `mandate_ballot.py`, the formatter
  the `mandate-ledger` skill runs when you ask for a team ballot. Standard library only; none of
  them opens a network connection.

## Hooks

The hooks run `python3` on the scripts above, from the plugin folder. Their text only describes
and suggests: nothing tells the agent to act without your request, to skip asking you, or to write
to agentleFS unless you ask.

| Event | Hook | Network |
|---|---|---|
| `SessionStart` | Names the workspace's git repository (read with `git remote get-url origin`) and the skills that can help: `proactive-assembly` when a task names no project, `mandate-ledger` for team choices, offering a ballot only if you want the team to weigh in. | None |
| `PreInvocation` (first model call of a turn) | When your prompt looks like an unnamed work ask, suggests a soft entry mode and the `proactive-assembly` context packet; when it looks like a team choice or a decision being made, adds the `mandate-ledger` note, and that acting on a decision is your call. | None |

No hook records your prompts, tool calls or replies, and nothing is saved to agentleFS unless you
ask.

The decision notes also append bounded local diagnostics (event name and outcome, never content)
to `~/.agentlefs/plugin-memory/decision-observations.jsonl`. Nothing is sent anywhere.

Compared with the Claude Code plugin, three hooks are left out: Antigravity has no MCP-tool hook,
so there is no per-prompt project briefing; its `PostToolUse` output is ignored, so there is no
project nudge; and its `Stop` has no flag saying the agent was already held once, so there is no
stop reminder.

## Links

- Documentation: https://agentlefs.com/docs/connect
- Privacy: https://agentlefs.com/privacy
- Terms: https://agentlefs.com/terms
- Support: https://agentlefs.com/support

MIT licensed.
