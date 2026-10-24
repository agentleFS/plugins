# agentleFS

Team keep files. Agents read files. agentleFS decide who read what.

One store. People and agents same folders. Each agent see only what its human let it see. No more.

## Get

```
/plugin marketplace add agentleFS/plugins
/plugin install agentlefs@agentlefs
/agentlefs:connect
```

Browser open. Sign in. Done.

## Commands

| Command | Do |
|---|---|
| `/agentlefs:connect` | Sign in. Check it work. |
| `/agentlefs:catch-up` | What you do last time. Pick up. |
| `/agentlefs:seed` | Put what you know in store. Store not empty. |
| `/agentlefs:share` | Share folder by email. Show who get what first. |
| `/agentlefs:who-can-see` | Who see this folder or doc. |
| `/agentlefs:permissions` | What this sign-in can reach. |

## Skills

Claude pick these when need.

| Skill | Do |
|---|---|
| `documents` | Find, read, write, edit docs. Comment. |
| `sync-conversation-summary` | Write short summary of this chat. 500 words max. Never transcript. Go same folder as last time. |
| `sharing` | Give access. Ask for access. |
| `deleting` | Delete. Undo. Erase for good. |
| `shared-truths-and-lessons` | Team facts. Lessons. Dead ends. |
| `mandate-ledger` | Create and update team approval requests and decisions in AFS, shared with the AFS-backed Mandate Decisions board. |
| `collaborating` | Agents message, claim work, wait. |
| `catch-up` | What changed. What wait on you. |
| `sources` | Connect GitHub, Google Drive. |
| `connection` | Fix sign-in trouble. |
| `authorization-model` | Why agent see what it see. |
| `memory` | Set up automatic recall and session capture, check pending saves, or disable it. |
| `projects` | Start a project with other people and their agents. Post, take, report work. Split it across helpers. |

## Automatic memory

Claude Code and local Codex sessions can run the bundled lifecycle hooks. After
you configure a save folder and hook credential, the plugin recalls relevant
memory before each prompt and captures prompts, tool traces, and assistant
responses automatically. Python 3.9 or newer is required; no Python packages are
installed. Hosts without command hooks can continue using the MCP tools and skills.

```sh
# AGENTLEFS_TOKEN is an agent credential supplied by your environment.
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_hooks.py" configure --folder "engineering/memory"
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_hooks.py" status
```

Use the installed plugin's absolute path if your shell has no `CLAUDE_PLUGIN_ROOT`.
On Codex, review and trust the hooks through the host's hook controls; plugin
installation alone does not trust them. The `memory` skill walks through setup.

| Event | Behavior |
|---|---|
| `SessionStart` | Restore the local checkpoint and retry pending saves. |
| `UserPromptSubmit` | Stage the prompt locally and retrieve relevant memory with citations. |
| `PostToolUse` | Stage a bounded tool trace and attempt delivery. |
| `Stop` | Capture the assistant response and attempt delivery. |
| `PreCompact` | Persist a checkpoint for restoration after compaction. |
| `SessionEnd` | Persist the final checkpoint and start a detached delivery attempt. |

Capture starts only after setup. Hooks use the same `AGENTLEFS_URL` and
`AGENTLEFS_TOKEN` conventions as the CLI, with the hosted MCP endpoint as the
default URL. They cannot read the host's OAuth credential store. A token supplied
with `configure --token-stdin` is stored locally with restrictive permissions;
never put a credential in a command argument or a committed file.

Captures are stored as individual documents in the chosen folder. That folder's
existing permissions determine who can read them. The plugin bounds captured
text and redacts common credential formats; this is not a guarantee that every
secret embedded in arbitrary prose can be recognized. Choose a destination whose
audience is appropriate for your conversations.

Pending captures are written locally before network delivery. Failed or refused
saves stay pending, and later hooks or `flush` retry them. Each capture has a
stable document name and idempotency key. A local checkpoint is not a remote-save
acknowledgement, and a detached worker is not guaranteed to survive host shutdown.
Use `status` to check the queue and `flush` to retry it. `disable` stops capture,
recall, and delivery; it does not delete existing local or remote records.
Idle local checkpoints for fully acknowledged sessions expire after 30 days;
pending captures are never removed by that cleanup. Records are isolated by
credential, endpoint, folder, working directory, and host session. After changing
the credential, endpoint, or folder, `status` reports older captures separately
as `pending_other`; restore their original configuration to retry them.

The lifecycle follows [Cognee's plugin](https://github.com/topoteretes/cognee-integrations/blob/main/integrations/claude-code/hooks/hooks.json),
with an AgentleFS implementation using the existing MCP tools. No Cognee service
or additional model provider is required. These executable hooks are intended for
local plugin installations; OpenAI's public plugin directory currently excludes
packages with hooks, and cloud orchestration does not run these command hooks.

## Projects

A project is a folder marked as one: its brief is the folder's `AGENTS.md`, its
conversation is the folder's discussion, and whoever can read the folder is a
member. The `projects` skill starts one and runs it. Four hooks keep agents on
it, with no setup and no credential of their own:

| Event | Hook |
|---|---|
| `SessionStart` | Name the session's git repository, so the agent can ask `brief_me` for the projects that cover it. No network call. |
| `UserPromptSubmit` | Call `brief_me` with `only: "projects"` over the session's own agentleFS connection, and add what moved in its projects. Nothing when nothing did. |
| `Stop`, `SubagentStop` | An agent that took a project thread on and did not report it is sent back once to report. Read from the session's transcript; no network call. |
| `PostToolUse` | A session that coordinates helpers or other people through agentleFS (spawning, asking for work, posting on a folder) twice without a project is told once that it could be one. From the transcript; no network call. |

Claude Code and Codex read separate hook files (`hooks/hooks.json`,
`hooks/codex-hooks.json`) because they name the plugin's server differently in
an `mcp_tool` hook; the two files are otherwise the same.

## Agents

| Agent | Do |
|---|---|
| `context-researcher` | Answer from team docs. Cite source. |
| `access-reviewer` | Look what credential reach. Read only. |

## Tools

Sixteen tools. Each one only read, or only write. Read tools never ask before run.

| Read | Do |
|---|---|
| `search` | Find. Every hit cite source. `scope: "public"` look in public GitHub files. |
| `read` | Open one thing: doc, old version of doc, message, truth, lesson, package, room, wait. |
| `browse` | List: folders, docs, doc versions, people, sources, inbox, claims, truths, lessons, more. |
| `access_read` | Who see what. Who you are. What wait for access decision. |
| `brief_me` | What wait on you. What change near your work. |

| Write | Do |
|---|---|
| `doc_create` | New doc or folder. Never overwrite. |
| `doc_update` | Edit, replace, move, undelete doc, roll doc back to old version. |
| `doc_delete` | Delete (can undo) or erase (forever). Two calls, preview first. |
| `access_grant` | Share, ask access, decide access, share to other org. |
| `access_revoke` | Take access back. Retire agent. |
| `identity_write` | Make helper agent. Set card. New session. |
| `message_write` | Message, comment, room. |
| `coordination_write` | Claim, wait, subscribe, mark read, truths. |
| `knowledge_write` | Lessons, dead ends. Draft, publish. |
| `registry_write` | Public registry, public context reports. Public! |
| `sources_write` | Connect GitHub, Drive. Vote for connector. |

### Renamed in 0.4

Old tool name gone. New name, same work.

| Old | New |
|---|---|
| `list_org_folders` | `browse` action `folders` |
| `list_org_docs` | `browse` action `documents` |
| `read_org_doc` | `read` action `document` |
| `search_org_knowledge` | `search` |
| `write_org_doc` | `doc_create` action `document` (new), `doc_update` action `replace` (overwrite) |
| `edit_org_doc` | `doc_update` action `edit` |
| `move` | `doc_update` action `move` |
| `undo_delete` | `doc_update` action `restore` |
| `create_org_folder` | `doc_create` action `folder` |
| `delete_org_doc` / `erase_org_doc` | `doc_delete` action `delete` / `erase` |
| `share_org_folder` | `access_grant` action `share` |
| `who_can_read` | `access_read` action `who_can_read` |
| `list_org_people` / `list_org_sources` | `browse` action `people` / `sources` |
| `connect_org_source` / `add_org_source` | `sources_write` action `connect` / `sync` |
| `share` | read actions in `access_read`, give in `access_grant`, take back in `access_revoke` |
| `identity` | `access_read` (self, agents, card), `identity_write` (spawn, set_card, new_session), `access_revoke` (retire) |
| `message`, `comment`, `room` | read in `read` / `browse`, write in `message_write` |
| `claim`, `await`, `subscribe`, `truth` | read in `read` / `browse`, write in `coordination_write` |
| `knowledge` | read in `read` / `browse`, write in `knowledge_write` |
| `registry`, `public_context_discussion` | read in `read` / `browse`, write in `registry_write` |
| `connectors` | `browse` action `connectors`, `sources_write` action `vote` |
| `brief_me` `ack_through` | `coordination_write` action `ack_brief` |

## What go where

The plugin connects to one server and includes skills, commands, and optional memory hooks.

- **Skills and commands:** instructions the agent reads to use the connected server.
- **Run:** Python lifecycle hooks when the host supports and trusts them. Memory capture and recall require setup.
- **Connect:** one server, `https://mcp.agentlefs.com/mcp`. Sign in by OAuth in browser. No token in file.
- **Send to agentleFS:** tool-call arguments, including configured automatic memory captures and recall queries. Docs you save. Messages, comments. Who you share with (email). One-line `reason` on some writes.
- **agentleFS keep:** docs, messages, comments, until deleted. Audit log keep who did what, when, where. Search words: only hash, never words. `reason`: one line, max 200 chars, kept with event.
- **Fetch from agentleFS:** only what your grants let you read.
- **Leave agentleFS:** only when you ask. `access_grant` share out email person in other org. `identity_write` webhook post to URL you give. `registry_write` post public comment, rating, report. `sources_write` connect GitHub or Google.
- **Local memory:** configured hooks keep pending captures and checkpoints on your machine and may read the host-provided transcript to recover an assistant response. Ordinary MCP tools do not fetch your local chat history.
- **`sync-conversation-summary`:** run only when you ask to save this chat. Claude write short summary, 500 words max, never transcript. Only that summary sent, as one doc, to folder you pick (or folder last summary went).
- **No Slack skill.** Removed. Plugin never call other connector you did not name.

## More

- Docs: https://agentlefs.com/docs/connect
- Privacy: https://agentlefs.com/privacy
- Terms: https://agentlefs.com/terms
- Help: contact@agentlefs.com

MIT.
