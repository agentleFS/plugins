---
name: documents
description: "Find, read, write, edit and review shared documents in agentleFS (afs). Use for team runbooks/specs/notes, document or folder browsing, review feedback, clarification questions, disagreements, and reading or responding to document comments\u2014even when the user does not say comment. Also save topic summaries or this conversation. For recording one shared decision/fact use shared-truths-and-lessons; for team ballots use mandate-ledger. Folder documents (including wiki raw/ sources) belong here; synced GitHub/Drive connections use sources. Not for local repository files or general knowledge."
---

# Documents in agentleFS

Everything here is filtered to what this session may read, and a document you may not
read answers exactly like one that does not exist. So a thin result means "nothing I can
reach", never "nothing exists" — the `authorization-model` skill has the reasoning.

## Finding something

**Use `search` by default.** Each hit carries a citation (`location@commit`, plus `#span`
for a block), when it was committed or last synced, and a trust signal — `verified_truth`,
`stated_truth`, `mirror` or `text` — with any recorded truths about it. That is what you
need to cite an answer and to say how current it is.

| You want | Call |
|---|---|
| Anything on a topic | `search` with `query`: a few key terms |
| Only one folder | `search` with `scope` set to that folder |
| The matching passages inside one document | `search` with `within` set to the document |
| One synced repository or Drive folder | `search` with `source` |
| Related documents and truths around each hit | `search` with `follow` (1–3) |
| Exact wording | `how: "text"`; titles and metadata only: `how: "titles"` |
| Examples from public GitHub (skills, CLAUDE.md, AGENTS.md, cursor rules) | `search` with `scope: "public"` |
| One of those public files, in full | `search` with `scope: "public"` and `within` set to its `owner/repo/path`, or read its `agentlefs://public/` URI; a long file comes in parts, the next one by `offset` |

Run at least one search without a scope before concluding the store has nothing on it.

**Public files are not the team's.** `scope: "public"` searches files strangers published on
GitHub, never the organization's documents, and answers in `public` rather than `hits`. Present
them as outside examples, never as what the team decided. Each hit says what the file would
have an agent do (`capabilities`: `destructive`, `reads_secrets`, `installs`, `shell_pipe`, …)
and under which licence; mention those before suggesting anyone use it. A file whose licence
does not allow it is described with a link, not served. Give the user the hit's `sourceLink`
(the file on GitHub, readable whatever its licence), or its `link` when there is none, to see it
themselves. A folder of the organization's own that is named `public` is `scope: "/public"`.

## Browsing

- `browse` with `action: "folders"` and no other argument: every folder you reach, as a
  tree. `parent` lists what is inside one folder; `location` reports that folder's shape
  (how many files you can read, their types and labels).
- `browse` with `action: "documents"` and `location`: the documents in a folder, optionally
  narrowed by `type` or `label`. Label filters match labels inherited from the folder as well.

## Reading

`read` with `action: "document"` and `location` (or `node`, the id printed beside a
location, which survives a rename). It returns the body, a console link to cite, and the
commit it read at, printed as "(pass as expected_commit to edit safely)". A paged read marks
each part as a part, and the part that ends the document as the last part: either way, read
every part before replacing it with `doc_update` `action: "replace"`. `doc_update`
`action: "edit"` reads the whole document whatever its size, so a part's pin is enough for it. Page a long document with `offset` and `maxBytes` rather
than guessing at the rest. Cite what you opened, not a
search snippet.

## Writing a new document

1. **Ask where it goes.** The folder decides who can read it, so that is the user's call.
   `browse` `action: "folders"` shows the options.
2. `browse` `action: "documents"` on that folder, and `read` on a neighbour or two, to copy
   the frontmatter convention — the listing shows `type` but not tags.
3. `doc_create` with `action: "document"`, `folder_path` (folder names, outermost first, e.g.
   `["handbook", "policies"]`), `name` (end it in `.md` so the console renders it) and
   `content` starting with YAML frontmatter: `type` (one of `meeting-notes`, `playbook`,
   `spec`, `brand-asset`, `web-clip`, `contract`, `misc` — anything else silently becomes
   `misc`), `title`, `summary`, `tags`.
4. Read the confirmation back. It names the folder and any directory it had to create; a
   surprise there means the path was wrong. A document already at that path is refused, never
   overwritten: replacing one is `doc_update`. A new **folder** is the loud one: if the top-level folder does not
   exist yet and you may create folders here, this call starts it and makes you its
   manager, so `new folder "…"` on a path you thought existed means you have created a
   workspace rather than written into one. Hand over the console link it returns.

Where it belongs depends on what it is:

- **A summary or write-up** — of a topic, a meeting, several decisions — is a document, and
  this section is how to write it.
- **One decision, fact or assumption** the organization should hold, with evidence, is a
  truth; **a lesson or dead end** is knowledge. Both are in the
  `shared-truths-and-lessons` skill, and both are findable and contestable in ways a
  paragraph is not. For a decision teammates need to understand later, preserve the
  concise context, rationale, alternatives/tradeoffs, relevant attributed human questions
  and answers, evidence, and revisit conditions in its anchor document, then link its
  decision truth. Use `shared-truths-and-lessons` for that workflow; Mandate is only
  needed for its separate team ballot flow. Never save hidden chain-of-thought or copy
  a raw private session into a shared document. A summary that records a decision can
  offer the truth as well.
- **This conversation itself**, saved as a record of the session: follow
  [Save this conversation](references/conversation-summary.md). Load that workflow before
  writing: preserve its destination reuse, 500-word limit, secret stripping, and re-sync rules.

`doc_create` with `action: "folder"` makes a folder (you become its manager), for starting
a project before anything is in it. `action: "document"` starts one too when its top-level
folder does not exist — the difference is that this one says so as the intent, instead of as
a side effect of a document you had to invent.

## Changing a document

1. `read` it first, and keep the commit it printed.
2. `doc_update` with `action: "edit"`, `location`, `old_string` (exact text from the current
   body), `new_string` and `expected_commit`. It changes only that text. `action: "replace"`
   with `location` and `content` replaces the whole document; `action: "move"` renames or
   moves it, keeping its id and history.
3. If it refuses, nothing was written, and the refusal says why:

| Refusal says | Do this |
|---|---|
| that text is not in the document | Re-read; you copied it wrong or it changed |
| that text appears N times | Include more surrounding text, or pass `replace_all` if every copy should change |
| it is at a different commit than you expected, or was committed by someone else while the edit was in flight | Re-read and re-apply to the new text, rather than forcing yours over theirs |
| the edit removes or breaks the frontmatter | Keep the `---` block intact |
| the section is claimed by another agent | See below |

To ADD a line or an entry at the end (a log line, a decision, a finding), do not replace the
last entry with itself plus yours: pass `append` with the text, and `section` with a heading's
text ("Log" for `## Log`) to add it at the end of that section rather than of the document.
It needs no `old_string` and no `expected_commit`: it lands after whatever is there when it
commits, so several agents appending at once all land, in order. The answer names the commit
and the byte range it added. A `section` no heading has, or that two headings have, is refused.

For a larger rewrite, or when other agents work in the same document, claim the section
first (`coordination_write` `action: "claim"`) so they find out before either of you edits
(the `collaborating` skill). A write into
a section someone else has claimed is refused and names the holder. `override_claim` writes
anyway, and is logged where they will see it, so use it only when the user decides to.

A path a connected source mirrors refuses edits: the next sync would overwrite them. Change
it at the source.

Pass an `idempotency_key` you choose on any write you might retry, so a retry after a
timeout is not applied twice.

## Reviewing and commenting

For “review this proposal,” “give feedback on this spec,” or “respond to their
feedback,” read the source **and** `browse action: "comments"` with its `location`.
Existing questions, unresolved issues and relevant earlier replies are part of
that review context. Use the existing thread for the same issue rather than
posting a duplicate root comment.

When the request authorizes shared feedback, use `message_write`:

- `action: "comment"`, `location` and `body` for a new issue, clarification
  question, disagreement or general discussion on a document **or folder**.
  Anchor passage-specific feedback with `quote` (exact source text) or `span`
  (a block id from `browse action: "spans"`). Both are optional for general
  document/folder discussion; never invent a quote or attach it to unrelated text.
- `action: "reply_comment"`, `thread` and `body` to answer or continue a thread.
  When reporting a fix, explain what changed and link the relevant evidence.
- `action: "resolve_comment"` and `thread` only when the issue has been addressed
  or explicitly closed, and resolving is authorized. Posting a reply or changing
  some text does not establish resolution; unresolved disagreement stays open.

A review request alone does not authorize publishing feedback. If posting is not
in scope, present the review in chat or draft the comments. Respect instructions
such as “review only” or “do not post.” Comments are visible to the source's
readers; do not copy private chat, credentials or hidden reasoning into them.
If the source or intended audience is unclear, identify it before posting.

Use a document's discussion for feedback its readers should see. Use a direct
message for a particular recipient (`message_write action: "send"`, the
`collaborating` skill). Editing the source is a separate task: comments do not
silently authorize rewriting it. A decision comment is discussion, not a formal
ballot, human acceptance or authorization to execute work.

## Save this conversation

For "save this chat", "sync this session", or a record of this conversation, read
[the conversation-summary workflow](references/conversation-summary.md) and follow it.
Save one compact summary, never a transcript; reuse this user’s previous destination
when established, and update the same document on re-sync. Ask only when no destination
is established. Keep the workflow’s frontmatter, privacy, and reporting rules.
