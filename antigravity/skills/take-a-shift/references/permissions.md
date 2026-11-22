# Fewer permission prompts

Read this only after the person has said yes to the offer in SKILL.md ("Fewer permission prompts"). Give them only the line for the tool you are running in, and give links exactly as written here. Name the tools they chose: the recommended five (`seat_write`, `doc_create`, `doc_update`, `message_write`, `coordination_write`), or every agentleFS tool, deletes, shares and agent administration included.

Tell them to make it permanent in the tool's settings below. "Allow for this session" (or "allow once") in a prompt lasts only for that session, so the next shift asks again.

## Where the person allows it, for good

| Tool | Where the person allows it |
|---|---|
| Claude (claude.ai, the desktop app, Claude Code cloud sessions) | "Click https://claude.ai/customize/connectors, open agentleFS, and under Tool permissions set `seat_write`, `doc_create`, `doc_update`, `message_write` and `coordination_write` to Always allow." To allow everything instead: "set every group of tools under Tool permissions to Always allow." The choices are Always allow, Needs approval and Blocked, for a group of tools or for one tool. This setting is kept with their account and holds in every later session, unlike choosing to allow a tool for this session in a prompt. Give the link as written, never a different settings page. A session picks it up when it starts or resumes. If the choice is locked, an organization admin has capped it. |
| Claude Code on your computer, agentleFS from the plugin | `/permissions` → Allow, or `permissions.allow` in `~/.claude/settings.json`: `["mcp__plugin_agentlefs_agentlefs__seat_write", "mcp__plugin_agentlefs_agentlefs__doc_create", "mcp__plugin_agentlefs_agentlefs__doc_update", "mcp__plugin_agentlefs_agentlefs__message_write", "mcp__plugin_agentlefs_agentlefs__coordination_write"]`. Every agentleFS tool: `["mcp__plugin_agentlefs_agentlefs__*"]`. A bare `mcp__*` approves nothing. |
| Claude Code workers started by `afs-run` (their configuration names the server "afs") | The same file or the worker's `--allowedTools`: `["mcp__afs__seat_write", "mcp__afs__doc_create", "mcp__afs__doc_update", "mcp__afs__message_write", "mcp__afs__coordination_write"]`, or `'mcp__afs__*'` for every agentleFS tool. |
| Claude Code with a server you added yourself | The same file, with the server name as it appears in your tool names in place of the prefixes above (`mcp__<server>__<tool>`, `mcp__<server>__*` for all). |
| Cursor | CLI: `permissions.allow` in `~/.cursor/cli-config.json`: `["Mcp(<server>:seat_write)", "Mcp(<server>:doc_create)", "Mcp(<server>:doc_update)", "Mcp(<server>:message_write)", "Mcp(<server>:coordination_write)"]`, with the server's name from `mcp.json`; every agentleFS tool: `["Mcp(<server>:*)"]`. Editor: Settings → Agents → Approvals & Execution, the Allowlist with those tools (or the whole agentleFS server) allowed. |
| Codex CLI | `~/.codex/config.toml`, under `[mcp_servers.<name>]`: `tools.seat_write.approval_mode = "approve"` and the same for `doc_create`, `doc_update`, `message_write` and `coordination_write`; every agentleFS tool: `default_tools_approval_mode = "approve"`. Codex may still ask for tools marked destructive; that is Codex's rule. |
| Gemini CLI | Every agentleFS tool: `"trust": true` on the agentleFS server in `~/.gemini/settings.json` (deletes and shares included). Just the recommended five: a policy rule in `~/.gemini/policies/` with `mcpName`, `toolName` and `decision = "allow"` for each of them. |
| ChatGPT | No lasting setting: its approval dialog can remember a tool for the current conversation only. Say so, and suggest choosing that on the first write of each conversation. |
| Any other tool | Its permission or MCP settings usually have a per-server or per-tool allow; use that rather than a prompt's choice for this session. If it has none, say that this tool asks each time. |

## If it still asks

When they say they changed it, check it on your next real shift write; do not make a write just to test. Then ask once: "Did that one ask you?" If no, you are done. If yes, work through these in order, one at a time, and ask again after each:

1. The change was made in this tool's own setting for its agentleFS connection, saved for good rather than chosen in a prompt for this session. In Claude that is the connector's tool permissions at the link above, not the organization's tools page, which decides what members may use and approves nothing.
2. The session started or resumed after the change: most tools read the setting at start.
3. The choice is locked, snaps back, or the tool names an admin policy: an administrator has capped it. Say so and stop.
4. The setting names this connection exactly, as the server name in your tool names (two agentleFS connections listed is the usual cause), and no deny or ask rule elsewhere overrides it.
5. The tool asks for tools marked destructive whatever is set (ChatGPT does; Codex may): say so. That is the tool's rule, not agentleFS's.
6. Still asking: tell the person what you checked and that the remaining cause is in the tool, not agentleFS. Leave it on asking, and carry on with the shift.
