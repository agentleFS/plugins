# agentleFS plugins

Plugins that connect AI coding agents to [agentleFS](https://agentlefs.com), a
permissioned org-context store. Your agent reaches what you are granted and nothing
else, and the authorization filter runs inside the query rather than as an
afterthought.

> **Generated repo.** Published from the agentleFS source repo on release. Do not
> open PRs here, edits are overwritten by the next publish. File issues at
> [agentlefs.com](https://agentlefs.com).

## Why bother

Your agent already knows how software works. It knows nothing about **how your company
works** - why you picked Postgres over Dynamo, who owns the billing service, what the
last postmortem concluded. Ask it today and you get confident generic advice, or an
apology about not having access to your internal docs.

agentleFS is where that knowledge lives, filtered to what you're actually granted. The
plugin is what makes your agent reach for it unprompted, and - just as importantly - what
stops it from telling you "your org never documented this" when the honest answer is "I
can't see that."

## Claude Code and Claude Desktop (2 steps, about a minute)

**1. Add the marketplace and install.**

```
/plugin marketplace add agentleFS/plugins
/plugin install agentlefs@agentlefs
```

**No restart, on Claude Code v2.1.268 or later.** Closing the `/plugin` menu runs
`/reload-plugins` for you, and that connects the plugin's MCP server in the session you
are already in. If you installed from a shell instead — `claude plugin install …`, or an
agent doing it for you — the menu never opened, so type `/reload-plugins` yourself.

Below v2.1.268, and in Claude Desktop, restart instead: the reload does not connect
plugin MCP servers in a session without an interactive terminal, which includes the
desktop app, the Agent SDK and `-p`.

**2. Connect.**

```
/agentlefs:connect
```

A browser window opens. Sign in. That's it.

**There is no token to mint or paste.** Auth is OAuth with dynamic client registration,
so the client registers itself and this repo ships no credential of any kind.

> **You'll see an HTTP 401 first, and that's normal.** The 401 carries the header that
> *triggers* the browser sign-in - it's the mechanism working, not a failure. Don't debug it.

Once you're in, `/agentlefs:connect` verifies with a real call and tells you which state
you're in: connected and granted, connected but reaching nothing, or not signed in. Those
three need completely different fixes.

### Fill an empty store: `/agentlefs:seed`

New store with nothing in it? Semantic search works, but it has nothing to search.
Run **`/agentlefs:seed`** — it asks where to write, then fills the store from what
your agent already learned about your project. Prefer the command over pasting the
prompt by hand.

If you are not on Claude Code (no slash commands), paste this instead:

```
Use agentleFS as our team's long-term memory. Call browse with action folders to
see what I reach. Then take everything you've learned about this project -
architecture decisions, gotchas, conventions, anything a new teammate would need -
and write each as its own doc with doc_create. Match the frontmatter (type + tags) of
neighboring files so they're findable. If you've genuinely learned nothing yet,
write one short doc capturing what this repo is and how to run it, so the store
isn't empty. Tell me what you wrote and where.
```

### Copy-paste: make it a habit

```
From now on, check agentleFS before answering anything about how *we* do things,
and write durable conclusions back with doc_create so the next session inherits
them. If a search comes back thin, say it may be a permission boundary rather than
telling me nothing exists.
```

| Command | Answers |
|---------|---------|
| `/agentlefs:connect` | Get me connected, and tell me why I see nothing |
| `/agentlefs:permissions` | What does *this* credential actually reach? |
| `/agentlefs:share` | What am I about to share with a colleague, and how far does it cascade? |
| `/agentlefs:who-can-see` | Who can see this — and can a particular agent? |
| `/agentlefs:catch-up` | What was I working on, and what's the next step? |
| `/agentlefs:seed` | The store is empty - fill it from what the agent already learned |

Also included, and triggered by what you ask rather than by a slash command:

| Skill | Fires when |
|---|---|
| `documents` | You ask what your team has written down, or want a doc opened, saved, edited or commented on — with the typed search that cites every hit; also save or re-sync a compact summary of this conversation |
| `catch-up` | You ask to be caught up, or refer to ongoing work as though the agent should already know — the same ground as `/agentlefs:catch-up`, without having to ask for it |
| `proactive-assembly` | An implement/fix/build/UI/lost ask names no project — soft entry mode + ranked cited context packet (projects, docs, asks, write-back), suggestions only |
| `entry-mode-playbooks` | Soft recipes for lost / ui / bug / feature (assemble steps, caps, write-back checklist, done-when); loaded by proactive-assembly; skippable — not a wizard |
| `writeback-loop` | Guided write-back before stop — commit findings/docs/comments to suggested targets (soft checklist; human may skip) |
| `collaborating` | Another agent is involved: claiming a section before editing, asking and waiting for an answer, being told when a doc changes, a shared room with another team's agent, or a helper agent with narrower access |
| `swarm-board` | Multi-agent / swarm work should use waits, rooms, and typed handoffs as the board — soft recipes (especially under cron), not ad-hoc chat |
| `shared-truths-and-lessons` | Record everyday decisions with their rationale, alternatives, relevant attributed human discussion and evidence, without Mandate. Also contest facts, keep lessons and dead ends, or find public skills. |
| `mandate-ledger` | Create and update team approval requests and decisions in AFS, shared with the AFS-backed Mandate Decisions board. |
| `sharing` | You share something, need access you lack, have requests to approve, ask who (or which agent) can see something, or offer a folder to another organization |
| `sources` | You want a GitHub repo or Drive folder synced in, a sync checked, or a vote cast for a connector that does not exist yet; also bind GitHub issues and post safe pointers |
| `deleting` | Something is about to be removed, restored or permanently erased, and the blast radius needs saying out loud first |
| `authorization-model` | Anything turns on who can read what, or a result comes back thinner than expected |
| `connection` | The tools are missing, returning 401, or connected but reaching nothing |
| `memory` | You want automatic recall and session capture set up, checked, or turned off |
| `projects` | You want to start a project, see what is open, take or report work, or split it across helpers |

Plus two agents: `context-researcher` for grounded retrieve-and-cite work, and
`access-reviewer` for read-only access review — read-only by tool allowlist rather than
by instruction.

**Self-hosted?** The marketplace plugin hardcodes `https://mcp.agentlefs.com/mcp`,
so installing it against your own deployment would connect to the hosted host and
show an empty workspace you cannot explain. Use `claude mcp add` with your
endpoint instead:

```
claude mcp add --transport http --scope user agentlefs https://<your-mcp-host>/mcp
```

A local checkout can still load `claude --plugin-dir` after you edit the one
literal URL line in `plugins/agentlefs/.mcp.json` (kept literal on purpose —
`${…}` interpolation is not portable across agents and produced a server that
silently never connected).

## Codex

Same package, same marketplace, same browser sign-in. Codex registers a marketplace
from the SHELL and installs from inside the session, which is the one step people
expect to work the other way round.

**1. Add the marketplace** in a terminal:

```
codex plugin marketplace add agentleFS/plugins
```

**2. Install it.** In the CLI, start `codex` and run `/plugins` to open the plugin
browser, then install **agentleFS** from the agentleFS marketplace. In Codex in the
ChatGPT desktop app, restart the app first - it reads its marketplace sources at
startup - then install from the Plugins directory.

**3. Sign in** when Codex asks. A browser window opens, and there is no token to paste
here either.

What Codex loads from the package is `skills/` and the MCP server. The `commands/` and
`agents/` directories are Claude Code artifacts and are simply not read - they ship in
the same directory because one package serves both ecosystems, not because Codex has
them. `codex mcp list` will not show the server, and that is not a failed install: a
plugin-provided server is launched by the plugin rather than configured as an
`[mcp_servers.*]` entry in `config.toml`.

**The ChatGPT web and mobile apps are a different path.** They install from the
universal public plugin directory, which is a submission-and-review process rather
than a repository you can add, so a marketplace does not reach them. Until agentleFS is
listed there, add the server URL yourself: at chatgpt.com/plugins choose "+", then
"Create custom MCP server". Your workspace's plan and admin settings decide whether that
option is offered.

## Gemini CLI

The same repository is a Gemini CLI extension: `gemini-extension.json` at its root points
Gemini at the hosted server.

```
gemini extensions install https://github.com/agentleFS/plugins
```

Start `gemini`; the first call to the server gets a 401, and Gemini discovers the sign-in,
registers itself and opens a browser. If it does not, run `/mcp auth agentlefs`. Sign-in needs
a browser on the same machine, so it does not work in a headless session; use a bearer token
there (below). Gemini loads the MCP server only: the skills, commands and agents above are
Claude Code and Codex artifacts.

## Antigravity

The `antigravity/` folder is an Antigravity plugin: the hosted server plus the same skills.

```
agy plugin install https://github.com/agentleFS/plugins/tree/main/antigravity
```

Antigravity signs in on the first call through the browser, as Gemini does. Install the folder,
not the repository root: from the root, Antigravity reads `gemini-extension.json` and gets the
server without the skills.

## Cursor

Same package, same marketplace repository, same browser sign-in. Cursor reads
`.cursor-plugin/plugin.json` and the root `.cursor-plugin/marketplace.json`, and loads
the shared `skills/`, `agents/`, `commands/` and `.mcp.json`. Lifecycle hooks live in
`hooks/cursor-hooks.json` (Cursor's camelCase schema); they capture memory and name the
session's repository. Two Claude/Codex behaviours have no Cursor equivalent today:
`mcp_tool` project briefs on each prompt, and injecting recalled memory into
`beforeSubmitPrompt` (that hook can only allow or block).

**1. Add the marketplace.** In Cursor, open **Dashboard → Plugins & MCPs → Team Marketplaces →
Add Marketplace → Import from Repo**, and paste:

```
https://github.com/agentleFS/plugins
```

Or, for a local checkout of this repository, open **Customize → Plugins** and install from
the working tree (Cursor also loads plugins under `~/.cursor/plugins/local`).

**2. Install agentleFS** from that marketplace and enable it for the project or user.

**3. Sign in** when Cursor prompts for the agentlefs MCP server. A browser window opens;
there is no token to paste.

The official Cursor Marketplace listing is a separate, reviewed submission at
[cursor.com/marketplace/publish](https://cursor.com/marketplace/publish). Until it is listed
there, the GitHub marketplace above is the install path. The bare MCP URL still works as a
custom connector if you prefer that over the plugin.

## Other agents

agentleFS is a plain MCP server, so any MCP-capable client can connect to
`https://mcp.agentlefs.com/mcp` today - OAuth for humans, or a `afs_` bearer
token for headless and CI use. VS Code and Cline take that URL; ChatGPT takes
it as a custom MCP server; Meta's Muse connects when you ask for it in a chat on muse.ai.

**If your client doesn't do OAuth, you need a bearer token.** Many desktop clients
send only the headers you configure and never walk the discovery chain, so they get
the initial 401 and report "startup failed." Mint a token and set one header:

| Field | Value |
|---|---|
| URL | `https://mcp.agentlefs.com/mcp` |
| Header name | `Authorization` |
| Header value | `Bearer afs_...` |

Scope it by minting against a narrow principal - a token in a desktop app's config
carries that principal's roles, and it's revocable if the config ever leaks.

## The one thing worth knowing

**Denied is byte-identical to not-found.** agentleFS exposes no existence oracle: a
document you cannot read answers exactly like a document that does not exist, and a
folder you do not reach is simply absent. That is deliberate - the alternative leaks
the shape of what you cannot see.

The practical consequence is that **a thin result is usually a permission boundary,
not a bug**. Every command and skill here states that rule, because it is the single
most misread behavior in the product. If a search comes back empty, the honest reading
is "nothing I can reach matches", never "the organization has not written this down".

## License

MIT
