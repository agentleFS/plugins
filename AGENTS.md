# agentleFS

agentleFS (afs) is where this person or team keeps the context their AI tools need: how they do
things, decisions and why, runbooks, specs, and notes from their projects. This package connects
your AI tool to it over MCP. Sign-in is in the browser; if the tools answer 401, sign in again
from your tool's MCP menu (in Gemini CLI, `/mcp auth agentlefs`).

## When to use it

- A question about how *this* person or team does something, a past decision, who owns what, or a
  project's notes: look in agentleFS before answering from general knowledge.
- Something worth keeping (a decision, a finding, a runbook): offer to save it.

## How

- Start with `brief_me` to see who you are and what is waiting on you. Driving a persistent or
  intermittent agent, take its seat first (`identity_write` with `action: "take_seat"`) and pass the
  token as `seat` on every call; read the journal it hands back before carrying on.
- **Unnamed work ask** (implement / fix / build / improve UI / lost in project, with no project or
  folder named): before coding, run the `proactive-assembly` skill once — soft-infer entry mode
  (`lost` / `ui` / `bug` / `feature`, no picker), load `entry-mode-playbooks` for that mode
  (skippable/overrideable), and return one ranked, cited context packet (projects, docs/decisions,
  open asks/waits, write-back targets; suggestions only; human filters). If a matched hit has
  another identity's open claim, append one overlap suggestion line (`browse` `claims` with that
  location — suggestion only, never a block). Skip when they already named a project
  (`continue projects/…`) or asked to be caught up. **Before stopping**, if the session assembled
  or produced a durable finding/plan/decision that is still only in chat, run the
  `writeback-loop` skill (guided checklist — soft recipe, not a wizard; human may skip).
- Before handing work to a subagent or other helper, spawn an identity for it
  (`identity_write` with `action: "spawn"` and a narrowed `scope`) and have it act as that agent
  (`acting_as`, or its own credential) — never as you with full grants. The `collaborating` and
  `projects` skills have the steps. **Multi-agent / swarm coordination** uses the `swarm-board`
  skill: typed messages with `wait: true`, rooms across chains, and handoff/commitment kinds as
  the board — not ad-hoc chat or prose task docs. Even under cron, register waits so the next
  `brief_me` sees what resolved.
- Find things with `search` (every hit carries a citation), list them with `browse` and
  `action: "folders"`, and open one with `read` and `action: "document"`. Cite what you used.
- Write with `doc_create` into a folder the user chooses, and change part of a document with
  `doc_update` and `action: "edit"`. Match the frontmatter (type, tags) of the documents beside it.

## Access

Every result is filtered to what this account is granted. A document you cannot read looks exactly
like one that does not exist, so a thin or empty result may be a permission boundary. Say "nothing
I can reach matches", never "your team has not written this down".
