---
name: documents
description: Find, browse, read, write and edit the documents a person or team keeps in agentleFS (afs), and comment on them. Use when the user asks what they or their team have written down about something ("what do we have on deploys?"), asks to open or read a stored runbook, spec or note, asks what folders or documents they have, wants a new document saved into afs — including a written summary or write-up of a topic or of several decisions ("save a summary of what we decided on Q4 pricing") — wants a stored document changed (fix a typo, rewrite a paragraph), or wants to leave a comment on one. Not for saving this conversation itself as a record (sync-conversation), recording one decision or fact as shared truth (shared-truths-and-lessons), files in the local repository, or questions of general knowledge.
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
| Anything on a topic | `search` with `query` in the user's own words |
| Only one folder | `search` with `scope` set to that folder |
| The matching passages inside one document | `search` with `within` set to the document |
| One synced repository or Drive folder | `search` with `source` |
| Related documents and truths around each hit | `search` with `follow` (1–3) |
| Exact wording | `how: "text"`; titles and metadata only: `how: "titles"` |

`search_org_knowledge` is the older door to the same content. It returns the matching
passages assembled as prose, per folder, takes `location` (not `scope`), and pages with
`offset`. Unscoped, it sweeps at most twelve folders and says so. Reach for it when you
want the passages themselves as text, or need to page through a long result; otherwise
`search` answers the same question with more to cite.

Run at least one search without a scope before concluding the store has nothing on it.

## Browsing

- `list_org_folders` with no arguments: every folder you reach, as a tree.
  `parent` lists what is inside one folder; `location` reports that folder's shape
  (files you can read, how many are gated from you, types, labels).
- `list_org_docs` with `location`: the documents in a folder, optionally narrowed by
  `type` or `label`. Label filters match labels inherited from the folder as well.

## Reading

`read_org_doc` with `location` (or `node`, the id printed beside a location, which
survives a rename). It returns the body, a console link to cite, and the commit it read
at, printed as "(pass as expected_commit to edit safely)". Page a long document with
`offset` and `maxBytes` rather than guessing at the rest. Cite what you opened, not a
search snippet.

## Writing a new document

1. **Ask where it goes.** The folder decides who can read it, so that is the user's call.
   `list_org_folders` shows the options.
2. `list_org_docs` on that folder, and `read_org_doc` on a neighbour or two, to copy the
   frontmatter convention — the listing shows `type` but not tags.
3. `write_org_doc` with `folder_path` (folder names, outermost first, e.g.
   `["handbook", "policies"]`), `name` (end it in `.md` so the console renders it) and
   `content` starting with YAML frontmatter: `type` (one of `meeting-notes`, `playbook`,
   `spec`, `brand-asset`, `web-clip`, `contract`, `misc` — anything else silently becomes
   `misc`), `title`, `summary`, `tags`.
4. Read the confirmation back. It says whether it CREATED or OVERWROTE the document and
   names the folder and any directory it had to create; any of those being a surprise means
   the path was wrong. A new **folder** is the loud one: if the top-level folder does not
   exist yet and you may create folders here, this call starts it and makes you its
   approver, so `new folder "…"` on a path you thought existed means you have created a
   workspace rather than written into one. Hand over the console link it returns.

Where it belongs depends on what it is:

- **A summary or write-up** — of a topic, a meeting, several decisions — is a document, and
  this section is how to write it.
- **One decision, fact or assumption** the organization should hold, with evidence, is a
  `truth`; **a lesson or dead end** is `knowledge`. Both are in the
  `shared-truths-and-lessons` skill, and both are findable and contestable in ways a
  paragraph is not. A summary that records a decision can offer that as well.
- **This conversation itself**, saved as a record of the session, is the
  `sync-conversation` skill.

`create_org_folder` makes a folder (you become its approver), for starting a project
before anything is in it. `write_org_doc` starts one too when its top-level folder does not
exist — the difference is that this one says so as the intent, instead of as a side effect
of a document you had to invent.

## Changing a document

1. `read_org_doc` first, and keep the commit it printed.
2. `edit_org_doc` with `location`, `old_string` (exact text from the current body),
   `new_string` and `expected_commit`. It changes only that text.
3. If it refuses, nothing was written, and the refusal says why:

| Refusal says | Do this |
|---|---|
| that text is not in the document | Re-read; you copied it wrong or it changed |
| that text appears N times | Include more surrounding text, or pass `replace_all` if every copy should change |
| it is at a different commit than you expected, or was committed by someone else while the edit was in flight | Re-read and re-apply to the new text, rather than forcing yours over theirs |
| the edit removes or breaks the frontmatter | Keep the `---` block intact |
| the section is claimed by another agent | See below |

For a larger rewrite, or when other agents work in the same document, `claim` the section
first so they find out before either of you edits (the `collaborating` skill). A write into
a section someone else has claimed is refused and names the holder. `override_claim` writes
anyway, and is logged where they will see it, so use it only when the user decides to.

A path a connected source mirrors refuses edits: the next sync would overwrite them. Change
it at the source.

Pass an `idempotency_key` you choose on any write you might retry, so a retry after a
timeout is not applied twice.

## Commenting

`comment` puts a note on a document where its readers — people in the console and other
agents — see it, in the same threads people use:

- `action: "add"` with `location`, `body`, and either `quote` (the exact text you mean,
  e.g. step 3's line) or `span` (a block id from `truth` with `action: "spans"`).
- `action: "list"` with `location` to see the threads; `"reply"` and `"resolve"` take
  `thread`.

A comment is for the document's readers. To talk to one particular agent or person, use
`message` instead (the `collaborating` skill).
