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

## What go where

- One server: `https://mcp.agentlefs.com/mcp`. Sign in by OAuth. No token in file.
- Plugin send: your search words, what you save, what you share. Nothing else.
- Plugin never read chat history. `sync-conversation-summary` send only summary Claude write.
- No hook. No script. No binary. Only text and one server.

## More

- Docs: https://agentlefs.com/docs/connect
- Privacy: https://agentlefs.com/privacy
- Terms: https://agentlefs.com/terms
- Help: contact@agentlefs.com

MIT.
