---
name: sync-conversation
description: Save the current conversation into agentleFS (afs) as one durable summary document. Use when the thing the user wants saved is this conversation, session or chat itself ("save this session to afs", "sync this chat", "write up what we did here"). Not for a summary document about a topic or a set of decisions (the documents skill), recording a single decision or fact (the truth tool, in shared-truths-and-lessons), or a lesson or dead end (knowledge). Asks where it should land rather than picking a folder.
---

# Sync this conversation to agentleFS

A session ends and everything in it is gone. This turns the conversation into a
document the next agent — or the next person — inherits.

Two rules govern the whole thing:

1. **A summary, not a transcript.** Nobody re-reads a chat log. Write what was
   established and why.
2. **Ask where before writing.** You are about to put the user's words into a
   permissioned store. The destination decides who can read them, so it is the
   user's call each time.

## Step 1 — orient

Call `list_org_folders` with no arguments. This is what the destination choice is
made from, and it is also the connection check.

| Outcome | Do this |
|---|---|
| One or more folders | Continue to Step 2. |
| Empty list | Stop. This credential reaches nothing to write into. Send them to `/agentlefs:connect`. An empty list is not evidence the organization has no content — see the `authorization-model` skill. |
| Error / tools missing | Stop and diagnose with the `connection` skill. Do not paraphrase a 401 as "agentleFS is down". |

## Step 2 — ask where it goes

**There is no default destination.** Ask. agentleFS does not give each member a
private folder of their own, so there is no location that is safe to assume — every
folder in the Step 1 listing is one somebody else may be granted on.

That matters more for a conversation than for most documents: a session contains
half-formed reasoning, dead ends and things said in passing. Landing it somewhere few
people can read and sharing it outward later is a decision the user can still make.
Landing it in a team folder is a decision already made for them. So put the question
to them, and let them weigh it.

Offer:

- **A folder from Step 1** — name the specific reachable folders that plausibly fit,
  and say plainly that anyone granted on that folder will be able to read the
  conversation. If one of them is a folder only they can reach (for example one under
  `users/` bearing their name), say so, but do not pre-select it — only
  `/agentlefs:who-can-see` can tell you who else reaches it.
- **Somewhere else** — let them name the full location.

Write only to a folder you have seen listed or the user named. If nothing in the
listing fits, say so and ask.

Confirm the exact location (folder and file name) back to them before writing. A path is cheap to
get right now and expensive to move later: moving a file re-permissions it.

## Step 3 — read the neighbors

Call `list_org_docs` on the chosen folder. Two things come from this:

- The `type` convention already in use, to match.
- Whether a document for this conversation already exists. If the user is re-syncing
  an ongoing thread, write to the **same path** rather than minting `notes-2.md`.

### Tags are not in that listing

The listing renders one line per file — `- path [type] (asset) title` — and no
tags. Reading a tag convention off it is not possible; an agent that tries will
either invent unrelated tags or quietly skip the matching it was asked to do, with
nothing signalling that the data was never there.

Tags come from opening a neighbor. Pick one or two of the most representative files
from the listing and call `read_org_doc` on them: it reattaches the document's own
frontmatter, so the tags you see are the ones somebody authored on that file.

Copy those, and not the folder's label list from `list_org_folders` with `location` —
that set is *resolved*, meaning it includes labels inherited from the folder and the
directories above it. Restating an inherited label in your own frontmatter converts it
into an authored one, which then survives being removed from the folder. Inherited
labels already apply to your document without being written down.

Tags drive search and carry no authority whatsoever; a mis-tagged file is a file
nobody retrieves, and a well-tagged one grants nobody anything.

### `type` is a fixed list, and a wrong value fails silently

There are exactly seven:

```
meeting-notes | playbook | spec | brand-asset | web-clip | contract | misc
```

Anything else — `conversation`, `session-summary`, whatever reads best — is not
rejected. It is silently coerced to `misc`, with nothing said about it in the write
response, so the document lands in a bucket you did not choose and never find out.

Expect to have nothing to copy from. The folder you are writing into may hold no
documents at all — "match the neighbors" has
no answer there. When that happens, pick from the list above rather than inventing:
`meeting-notes` is the closest bucket for a record of a working session, and `misc`
is the honest choice when it is not.

`tags` are free-form, so put the specifics there.

## Step 4 — compose the document

One conversation, one document. Frontmatter matching the neighbors, then a body
along these lines:

- **What was asked** — the problem in the user's terms, not yours.
- **What was decided or established** — the durable part. Conclusions, and the
  reasoning behind them where the reasoning is not obvious from the outcome.
- **What was tried and rejected**, with why. This is the highest-value section and
  the one most often dropped; it is what stops the next person repeating it.
- **What changed** — files, commands, migrations, config, if any.
- **Open threads** — what is unresolved, and what the next step would be.

Keep it readable in two minutes.

**Strip before writing:**

- Secrets, tokens, API keys, connection strings, credentials of any kind — including
  ones that appeared in tool output rather than in the chat.
- Personal or sensitive information about third parties that has no bearing on the
  conclusion.
- Raw tool dumps, full file contents, and long stack traces. Quote the one line that
  mattered.
- Anything the user asked you not to record. Ask if you are unsure about a passage.

If in doubt about a passage, leave it out and say you did.

## Step 5 — write

Call `write_org_doc` with the confirmed destination split the way the tool takes it:
`folder_path` (the folder names, outermost first, e.g. `["product", "notes"]`), `name`
(the document's file name, ending in `.md`, with no `/` in it) and `content` (the
frontmatter and body from Step 4). A path written as one string — `product/notes/x.md` —
is the location you confirmed with the user, not an argument this tool accepts.

It commits if their grant allows it and is refused if it does not — there is no
staging option and no review queue, so a successful write is live immediately. If it
is refused, say so plainly and say where they could write instead.

## Step 6 — report

State the folder and the full path, and hand over the link the write returned —
the confirmation ends with `— cite: <url>`, and that is the openable half. A commit
hash is not something anyone can click, and a document nobody opens is a document
that may as well not have been written.

The confirmation also says whether it CREATED the document or OVERWROTE one, and
names any directory that did not exist before. Read both back before you report:
"overwrote" on a document you meant to create, or a directory you did not expect to
be new, means you wrote somewhere other than where you meant to — say so rather than
reporting a clean write.

Name what you deliberately left out, and say who can now read it: anyone granted on
the folder it went into. Sharing it further is a separate decision — `share_org_folder`,
through `/agentlefs:share` or the `sharing` skill — and the user's to make.

## Do not

- Do not pick the destination silently. Even when the answer is obvious, ask.
- Do not write a verbatim transcript, and do not paste whole files into the document.
- Do not write secrets, even ones the user pasted themselves.
- Do not invent a folder that did not appear in `list_org_folders`.
- Do not create a second document for a conversation that already has one.
- Do not report a refused write as though it had landed.
- Do not claim you shared it with anyone. Writing is not sharing: it reaches only who
  already reaches the folder, and widening that is a share the user decides on.
- Do not use this for a single decision or a dead end. If the conversation settled one,
  offer to record it as well with `truth` or `knowledge` (the `shared-truths-and-lessons`
  skill), where others can find and contest it.
