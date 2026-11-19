# Fewer permission prompts

Read this only after the person has said yes to the offer in SKILL.md ("Fewer permission prompts"). Give them only the line for the tool you are running in, and give links exactly as written here.

## Where the person allows it

| Tool | Where the person allows it |
|---|---|
| Claude (claude.ai, the desktop app, Claude Code cloud sessions) | "Click https://claude.ai/customize/connectors, open agentleFS, and under its tool permissions set `doc_update` and `doc_create` (and `message_write` if you like) to Always allow." Give the link as written, never a different settings page. A session picks it up when it starts or resumes. Allow rules in a settings file do not override it. If the choice is locked, an organization admin has capped it. |
| Claude Code with its own agentleFS server | `/permissions`, or `permissions.allow` in `~/.claude/settings.json`: `mcp__<server>__doc_update` and the others (`mcp__<server>__*` for every agentleFS tool), with the server name exactly as it appears in your tool names. |
| Cursor | CLI: `permissions.allow` in `~/.cursor/cli-config.json`, e.g. `"Mcp(agentlefs:doc_update)"`. Editor: Settings → Agents → Approvals & Execution, the Allowlist or Auto-review mode, with the agentleFS tools allowed. |
| Codex CLI | `~/.codex/config.toml`, under `[mcp_servers.<name>]`: `tools.doc_update.approval_mode` (or `default_tools_approval_mode` for all of them) set so it does not prompt. Codex may still ask for tools marked destructive; that is Codex's rule. |
| Gemini CLI | `"trust": true` on the agentleFS server in `~/.gemini/settings.json` (every agentleFS tool, deletes and shares included), or a policy rule in `~/.gemini/policies/` with `mcpName`, `toolName` and `decision = "allow"` for just the tools named. |
| ChatGPT | No lasting setting: its approval dialog can remember a tool for the current conversation only. Say so, and suggest choosing that on the first write of each conversation. |
| Any other tool | Its permission or MCP settings usually have a per-server or per-tool allow; otherwise choose "always allow" in its prompt on the first `doc_update`. If it has neither, say that this tool asks each time. |

## If it still asks

When they say they changed it, check it on your next real shift write; do not make a write just to test. Then ask once: "Did that one ask you?" If no, you are done. If yes, work through these in order, one at a time, and ask again after each:

1. The change was made in this tool's own setting for its agentleFS connection. In Claude that is the connector's tool permissions at the link above, not the organization's tools page, which decides what members may use and approves nothing.
2. The session started or resumed after the change: most tools read the setting at start.
3. The choice is locked, snaps back, or the tool names an admin policy: an administrator has capped it. Say so and stop.
4. The setting names this connection exactly, as the server name in your tool names (two agentleFS connections listed is the usual cause), and no deny or ask rule elsewhere overrides it.
5. The tool asks for tools marked destructive whatever is set (ChatGPT does; Codex may): say so. That is the tool's rule, not agentleFS's.
6. Still asking: tell the person what you checked and that the remaining cause is in the tool, not agentleFS. Leave it on asking, and carry on with the shift.
