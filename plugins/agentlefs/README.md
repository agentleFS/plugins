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

## Connected, but the wrong account or Organization

Working connection can still be wrong Organization or wrong email. No error — store just look almost empty. Same how-to at https://agentlefs.com/docs/connect and in the `connection` skill.

**Organization (same email).** Clear client auth, authenticate again, pick the Organization (Personal included) on the consent page.

**Email.** Clear client auth and authenticate again. On the consent page click **Use another account**, sign in as the intended email, then Allow.

| Client | Steps | Status |
|---|---|---|
| Claude Code | `/mcp` → agentlefs → Clear authentication → Authenticate | Verified |
| Claude Desktop / Claude (web) | Disconnect connector, reconnect | Unverified |
| Codex CLI | `codex mcp login agentlefs` again (or remove server and re-add) | Unverified |
| Codex app | Settings → MCP servers → remove, then Add / Authenticate | Unverified |
| Gemini CLI | `/mcp auth agentlefs` again; sign out in browser if session sticks | Unverified |
| ChatGPT (custom MCP) | Remove plugin, add server with OAuth again | Unverified |
| Cursor | MCP settings → clear auth → re-authenticate | Unverified |

Then `browse` with `action: "folders"` to prove which Organization you reached.

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
| `documents` | Find, read, write, edit and comment on docs; save or re-sync a compact conversation summary. |
| `sharing` | Give access. Ask for access. |
| `deleting` | Delete. Undo. Erase for good. |
| `shared-truths-and-lessons` | Decisions and why: rationale, alternatives, relevant human discussion and evidence in an anchor document, linked to a native AFS truth. Also team facts, lessons and dead ends. No Mandate required. |
| `mandate-ledger` | Create and update team approval requests and decisions in AFS, shared with the AFS-backed Mandate Decisions board. |
| `collaborating` | Agents message, claim work, wait. |
| `swarm-board` | Multi-agent / swarm soft recipes: doorbell + shared filing cabinet, waits, typed handoffs as the board (not ad-hoc chat). |
| `catch-up` | What changed. What wait on you. |
| `proactive-assembly` | Unnamed work ask: soft entry mode + ranked cited context packet (projects, docs, asks, write-back). Suggestions only. |
| `entry-mode-playbooks` | Soft recipes for `lost` / `ui` / `bug` / `feature` (assemble steps, caps, write-back checklist, done-when). Loaded by proactive-assembly; skippable. Not a wizard. |
| `writeback-loop` | Guided write-back before stop: commit findings/docs/comments to suggested targets (soft checklist; human may skip). Product form of auto-writeback. |
| `sources` | Connect GitHub or Google Drive; bind GitHub issues and post safe pointers. |
| `connection` | Fix sign-in trouble. |
| `authorization-model` | Why agent see what it see. |
| `memory` | Recall what earlier sessions saved when it helps. Save a summary or note only when you ask. |
| `projects` | Start a project with other people and their agents. Post, take, report work. Split it across helpers. |

## Memory

Nothing is remembered unless you ask. The plugin has no hooks: nothing records your prompts,
tool calls or replies, and it saves nothing to agentleFS on its own.

- **Recall.** When a task continues earlier work, the `memory` skill can `search` and `read`
  what you saved before (session summaries, notes, truths, lessons) and cite it. Same reach as
  any other read: only what your grants let you see.
- **Save, when you ask.** "Save a summary of this session" writes one compact summary (500
  words at most, never a transcript) to the folder you pick, through the `documents` skill. A
  single decision or a lesson goes through `shared-truths-and-lessons`.
- **Make it routine, if you want.** Add a line to your own `CLAUDE.md` or `AGENTS.md`, for
  example:

  ```
  At the end of each session, offer to save a summary to agentleFS.
  ```

  The agent then offers at the end of each session, and each save is still yours to accept.

## Projects

A project is a folder marked as one: its brief is the folder's `AGENTS.md`, its
conversation is the folder's discussion, and whoever can read the folder is a
member. The `projects` skill starts one and runs it.

## Optional: agentleFS Workflows

This plugin runs nothing on your computer: no hooks, no scripts. A second plugin in the same
marketplace, `agentlefs-workflows`, adds them for people who want them: hooks that name the
session's repository and the skills that can help, brief the agent on what moved in your
projects on each prompt (a `brief_me` call to the agentleFS server), and remind it once before
stopping when a project thread it took is unreported; and the formatter the `mandate-ledger`
skill uses for team ballots. Its README lists every hook, what it injects and every network call.

```
/plugin install agentlefs-workflows@agentlefs
```

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
| `read` | Open one thing: doc, old version of doc, message, truth, lesson, package, wait. |
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
| `message_write` | Message, comment. |
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
| `message`, `comment` | read in `read` / `browse`, write in `message_write` |
| `claim`, `await`, `subscribe`, `truth` | read in `read` / `browse`, write in `coordination_write` |
| `knowledge` | read in `read` / `browse`, write in `knowledge_write` |
| `registry`, `public_context_discussion` | read in `read` / `browse`, write in `registry_write` |
| `connectors` | `browse` action `connectors`, `sources_write` action `vote` |
| `brief_me` `ack_through` | `coordination_write` action `ack_brief` |

## What goes where

The plugin connects to one server and adds skills, commands and agents.

- **Skills and commands:** instructions the agent reads to use the connected server.
- **Runs locally:** nothing. The plugin has no hooks and no scripts; the optional
  `agentlefs-workflows` plugin, a separate install, discloses its own.
- **Connects to:** one server, `https://mcp.agentlefs.com/mcp`. You sign in with OAuth in the
  browser; no token is stored in a file.
- **Sent to agentleFS:** the arguments of each tool call; documents you save; messages and comments; the
  email addresses of people you share with; and a one-line `reason` on some writes.
- **Kept by agentleFS:** documents, messages and comments until you delete them. The audit log
  keeps who did what, when and where. Search words are kept only as a hash, never as text. A
  `reason` is one line of at most 200 characters, kept with its event.
- **Fetched from agentleFS:** only what your grants let you read.
- **Leaves agentleFS:** only when you ask. `access_grant` `share_out` emails a person in another
  organization; `identity_write` `set_card` posts to a webhook URL you give; `registry_write`
  posts a public comment, rating or report; `sources_write` connects GitHub or Google Drive.
- **Memory:** nothing is captured automatically. A session is saved only when you ask, as
  described under Memory above.
- **`documents` (save this conversation):** runs only when you ask to save this chat. The agent
  writes a short summary of at most 500 words, never a transcript, from what is already in its
  context; no tool reads your chat history. Only that summary is sent, as one document, to the
  folder you pick (or the folder your last summary went to).
- **No Slack skill.** The plugin never calls another connector you did not name.

## More

- Docs: https://agentlefs.com/docs/connect
- Privacy: https://agentlefs.com/privacy
- Terms: https://agentlefs.com/terms
- Help: contact@agentlefs.com

MIT.
