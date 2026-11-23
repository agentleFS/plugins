# Basic tools, always approved

Read this only after the person has answered the question in SKILL.md ("Basic tools, always
approved") with the basic set or with every tool. Give them only the line for the tool you are
running in, and give links exactly as written here. You never change the setting yourself: they
make it, in their tool's own settings.

**The basic set**, nine tools: the reads `read`, `browse`, `search` and `brief_me`, and the routine
writes `seat_write`, `doc_create`, `doc_update`, `message_write` and `coordination_write`. These stay
asking: `doc_delete`, `access_grant`, `access_revoke` and `identity_write` (agent administration,
including `take_over`). **Every tool** includes those four too: deletes, shares and agent
administration.

Tell them to make it permanent in the settings below. "Allow for this session" (or "allow once") in
a prompt lasts only for that session, so the next shift asks again.

## Where the person allows it, for good

| Tool | Where the person allows it |
|---|---|
| Claude (claude.ai, the desktop app, Claude in a browser, Claude Code cloud sessions: the agentleFS connector) | "Open https://claude.ai/settings/connectors (if that does not list connectors, https://claude.ai/customize/connectors, the address Claude's help centre gives), open agentleFS, and under its tool permissions set the read-only tools and `seat_write`, `doc_create`, `doc_update`, `message_write` and `coordination_write` to Always allow; leave `doc_delete`, `access_grant`, `access_revoke` and `identity_write` on Needs approval." Every tool instead: "set every group of tools to Always allow" (deletes, shares and agent administration included). The choices are Always allow, Needs approval and Blocked, for a group of tools or for one tool. The setting is kept with their account and holds in every later conversation; a session picks it up when it starts. If a choice is locked, an organization owner has capped it under Organization settings → Connectors, which a member cannot override. |
| Claude Code on your computer, agentleFS from the plugin | `/permissions` → Allow, or `permissions.allow` in `~/.claude/settings.json`: `["mcp__plugin_agentlefs_agentlefs__read", "mcp__plugin_agentlefs_agentlefs__browse", "mcp__plugin_agentlefs_agentlefs__search", "mcp__plugin_agentlefs_agentlefs__brief_me", "mcp__plugin_agentlefs_agentlefs__seat_write", "mcp__plugin_agentlefs_agentlefs__doc_create", "mcp__plugin_agentlefs_agentlefs__doc_update", "mcp__plugin_agentlefs_agentlefs__message_write", "mcp__plugin_agentlefs_agentlefs__coordination_write"]`. Every tool: `["mcp__plugin_agentlefs_agentlefs__*"]`. A bare `mcp__*` approves nothing. |
| Claude Code workers started by `afs-run` (their configuration names the server "afs") | The worker's `--allowedTools`, ended by `--`: `--allowedTools 'mcp__afs__read,mcp__afs__browse,mcp__afs__search,mcp__afs__brief_me,mcp__afs__seat_write,mcp__afs__doc_create,mcp__afs__doc_update,mcp__afs__message_write,mcp__afs__coordination_write' --`, or the same names in `~/.claude/settings.json`. Every tool: `'mcp__afs__*'`. Headless, a tool not on the list is refused, reads included: there is nobody to ask. |
| Claude Code with a server you added yourself | The same file, with the server name as it appears in your tool names in place of the prefixes above (`mcp__<server>__<tool>`, `mcp__<server>__*` for every tool). |
| Codex CLI | `~/.codex/config.toml`, under `[mcp_servers.<name>]`: `tools.read.approval_mode = "approve"`, and the same line for `browse`, `search`, `brief_me`, `seat_write`, `doc_create`, `doc_update`, `message_write` and `coordination_write`. Headless, the same as `-c 'mcp_servers.<name>.tools.<tool>.approval_mode="approve"'`. Every tool: `default_tools_approval_mode = "approve"`. |
| Cursor CLI | `permissions.allow` in `~/.cursor/cli-config.json` (or the project's `.cursor/cli.json`): `["Mcp(<server>:read)", "Mcp(<server>:browse)", "Mcp(<server>:search)", "Mcp(<server>:brief_me)", "Mcp(<server>:seat_write)", "Mcp(<server>:doc_create)", "Mcp(<server>:doc_update)", "Mcp(<server>:message_write)", "Mcp(<server>:coordination_write)"]`, with the server's name from `mcp.json`; every tool: `["Mcp(<server>:*)"]`. Headless, add `--approve-mcps`, which approves the server, not its tools. Never `--force`: it allows every command, not only agentleFS's. |
| Cursor editor | Cursor asks before MCP tools by default and runs allowlisted ones at once; its documentation does not name where a person allowlists one tool, so this is not verified. If its prompt offers a lasting allow, choose that rather than this session. |
| Gemini CLI | The basic set: a policy file in `~/.gemini/policies/` (any name ending `.toml`), one rule per tool: `[[rule]]`, `mcpName = "agentlefs"`, `toolName = "seat_write"` (the bare tool name), `decision = "allow"`, `priority = 200`, repeated for each of the nine. Every tool: `"trust": true` on the agentleFS server in `~/.gemini/settings.json`, which skips every confirmation for it. |
| Grok Build | `~/.grok/config.toml`: `[permission]` with `allow = ["MCPTool(agentlefs__read)", "MCPTool(agentlefs__browse)", "MCPTool(agentlefs__search)", "MCPTool(agentlefs__brief_me)", "MCPTool(agentlefs__seat_write)", "MCPTool(agentlefs__doc_create)", "MCPTool(agentlefs__doc_update)", "MCPTool(agentlefs__message_write)", "MCPTool(agentlefs__coordination_write)"]`, with the server's name from `grok mcp add`. Every tool: `["MCPTool(agentlefs__*)"]`. Grok also reads `permissions.allow` from `~/.claude/settings.json` in the `mcp__<server>__<tool>` form. From xAI's Grok Build documentation; not yet run here. |
| Antigravity | CLI: `permissions.allow` in `~/.gemini/antigravity-cli/settings.json`: `["mcp(agentlefs/read)", "mcp(agentlefs/browse)", "mcp(agentlefs/search)", "mcp(agentlefs/brief_me)", "mcp(agentlefs/seat_write)", "mcp(agentlefs/doc_create)", "mcp(agentlefs/doc_update)", "mcp(agentlefs/message_write)", "mcp(agentlefs/coordination_write)"]`; every tool: `["mcp(agentlefs/*)"]`. The app sets a preset under Settings → General → Global Permissions; its documentation does not name a per-tool allow there, so that is not verified. |
| ChatGPT | No lasting setting. Reads run without asking; a write asks, and choosing to remember the approval lasts only for the current conversation (a new one, or a refresh, asks again). Say so, and suggest remembering it on the first write of each conversation. |
| Any other tool | Its permission or MCP settings usually have a per-server or per-tool allow; use that rather than a prompt's choice for this session. If you cannot find one, say that this tool asks each time; never guess a setting's name. |

## If it still asks

When they say they changed it, check it on your next real shift write; do not make a write just to test. Then ask once: "Did that one ask you?" If no, you are done. If yes, work through these in order, one at a time, and ask again after each:

1. The change was made in this tool's own setting for its agentleFS connection, saved for good rather than chosen in a prompt for this session. In Claude that is the connector's tool permissions at the link above, not the organization's connectors page, which an owner uses to cap what members may allow.
2. The session started or resumed after the change: most tools read the setting at start.
3. The choice is locked, snaps back, or the tool names an admin policy: an administrator has capped it. Say so and stop.
4. The setting names this connection exactly, as the server name in your tool names (two agentleFS connections listed is the usual cause), and no deny or ask rule elsewhere overrides it.
5. The tool asks for tools marked destructive whatever is set (ChatGPT does; Codex may): say so. That is the tool's rule, not agentleFS's.
6. Still asking: tell the person what you checked and that the remaining cause is in the tool, not agentleFS. Leave it on asking, and carry on with the shift.
