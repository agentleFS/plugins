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
| `collaborating` | Agents message, claim work, wait. |
| `catch-up` | What changed. What wait on you. |
| `sources` | Connect GitHub, Google Drive. |
| `connection` | Fix sign-in trouble. |
| `authorization-model` | Why agent see what it see. |

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
| `read` | Open one thing: doc, message, truth, lesson, package, room, wait. |
| `browse` | List: folders, docs, people, sources, inbox, claims, truths, lessons, more. |
| `access_read` | Who see what. Who you are. What wait for access decision. |
| `brief_me` | What wait on you. What change near your work. |

| Write | Do |
|---|---|
| `doc_create` | New doc or folder. Never overwrite. |
| `doc_update` | Edit, replace, move, restore doc. |
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

Plugin is text and one server. Here all it run, send, fetch.

- **Run:** nothing. No hook. No script. No binary. Skills and commands are text Claude read.
- **Connect:** one server, `https://mcp.agentlefs.com/mcp`. Sign in by OAuth in browser. No token in file.
- **Send to agentleFS:** what each tool call carry. Search words. Docs you save. Messages, comments. Who you share with (email). One-line `reason` on some writes.
- **agentleFS keep:** docs, messages, comments, until deleted. Audit log keep who did what, when, where. Search words: only hash, never words. `reason`: one line, max 200 chars, kept with event.
- **Fetch from agentleFS:** only what your grants let you read.
- **Leave agentleFS:** only when you ask. `access_grant` share out email person in other org. `identity_write` webhook post to URL you give. `registry_write` post public comment, rating, report. `sources_write` connect GitHub or Google.
- **Never:** plugin never read chat history, memory, or files on your machine. No tool ask for chat log.
- **`sync-conversation-summary`:** run only when you ask to save this chat. Claude write short summary, 500 words max, never transcript. Only that summary sent, as one doc, to folder you pick (or folder last summary went).
- **No Slack skill.** Removed. Plugin never call other connector you did not name.

## More

- Docs: https://agentlefs.com/docs/connect
- Privacy: https://agentlefs.com/privacy
- Terms: https://agentlefs.com/terms
- Help: contact@agentlefs.com

MIT.
