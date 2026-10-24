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
- Find things with `search` (every hit carries a citation), list them with `browse` and
  `action: "folders"`, and open one with `read` and `action: "document"`. Cite what you used.
- Write with `doc_create` into a folder the user chooses, and change part of a document with
  `doc_update` and `action: "edit"`. Match the frontmatter (type, tags) of the documents beside it.

## Access

Every result is filtered to what this account is granted. A document you cannot read looks exactly
like one that does not exist, so a thin or empty result may be a permission boundary. Say "nothing
I can reach matches", never "your team has not written this down".
