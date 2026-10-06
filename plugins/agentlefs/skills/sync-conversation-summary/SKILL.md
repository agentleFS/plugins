---
name: sync-conversation-summary
description: Save a compact summary of the current conversation into agentleFS (afs) as one durable document. Use when the thing the user wants saved is this conversation, session or chat itself ("save this session to afs", "sync this chat", "write up what we did here"). Not for a summary document about a topic or a set of decisions (the documents skill), recording a single decision or fact (a truth, in shared-truths-and-lessons), or a lesson or dead end (knowledge). Saves where this user's last sync went, and asks only when there is no previous one.
---

# Sync this conversation to agentleFS

A session ends and everything in it is gone. This turns the conversation into a
document the next agent — or the next person — inherits.

Two rules govern the whole thing:

1. **A compact summary, never a transcript.** Nobody re-reads a chat log. Write what
   was established and why, in 500 words at most.
2. **Save where it went last time; ask only when there is no last time.** The
   destination decides who can read the summary, so a new place is the user's call.

No agentleFS tool reads, fetches or reconstructs chat history. The summary is written
from what is already in your context, and the only thing sent to agentleFS is that
summary, through `doc_create` (or `doc_update` when the summary already exists).

## Step 1 — orient

Call `browse` with `action: "folders"` and nothing else. This is what the destination choice is
made from, and it is also the connection check.

| Outcome | Do this |
|---|---|
| One or more folders | Continue to Step 2. |
| Empty list | Stop. This credential reaches nothing to write into. Send them to `/agentlefs:connect`. An empty list is not evidence the organization has no content — see the `authorization-model` skill. |
| Error / tools missing | Stop and diagnose with the `connection` skill. Do not paraphrase a 401 as "agentleFS is down". |

## Step 2 — pick where it goes

Take the first of these that has an answer:

1. **The user named a place** in this request. Use it.
2. **This conversation was synced before** (earlier in this session, or a document for
   it already exists). Write to the same path, so a re-sync updates it rather than
   minting `notes-2.md`.
3. **This user has synced before.** Call `search` with the query `conversation-sync`
   and no `how` (the default matches labels). Open the hits with `read` and keep
   only those whose frontmatter `synced_by` is this user, as `brief_me` names them. A
   teammate's sync is not a precedent: their folder is theirs to choose. Of the ones
   left, take the folder of the one with the latest `date`. Save there.
4. **None of the above.** Ask. agentleFS gives no member a private folder of their
   own, so there is no safe place to assume. Name the reachable folders from Step 1
   that fit, say that anyone granted on a folder can read what lands in it, and let
   them name another location if none fits.

Write only to a folder you have seen listed, found in case 3, or the user named. In
cases 1–3, do not ask; say where it went in the report (Step 6), so the user can move
it if they meant somewhere else.

## Step 3 — read the neighbors

Call `browse` with `action: "documents"` on the chosen folder. Two things come from this:

- The `type` convention already in use, to match.
- Whether a document for this conversation already exists. If the user is re-syncing
  an ongoing thread, write to the **same path** rather than minting `notes-2.md`.

### Tags are not in that listing

The listing renders one line per file — `- path [type] (asset) title` — and no
tags. Reading a tag convention off it is not possible; an agent that tries will
either invent unrelated tags or quietly skip the matching it was asked to do, with
nothing signalling that the data was never there.

Tags come from opening a neighbor. Pick one or two of the most representative files
from the listing and `read` them: it reattaches the document's own
frontmatter, so the tags you see are the ones somebody authored on that file.

Copy those, and not the folder's label list from `browse` `action: "folders"` with `location` —
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

Always include the tag `conversation-sync`, `synced_by` (the user, as `brief_me` names
them) and `date` (today, ISO). Together they are how the next sync by the same user finds
this one's folder (Step 2, case 3).

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

Keep it compact: readable in two minutes, 500 words at most. If a conversation needs
more, it held more than one outcome. Offer to split it rather than writing it long.

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

A new summary: `doc_create` with `action: "document"` and the confirmed destination split
the way it takes it: `folder_path` (the folder names, outermost first, e.g.
`["product", "notes"]`), `name` (the document's file name, ending in `.md`, with no `/` in
it) and `content` (the frontmatter and body from Step 4). A path written as one string —
`product/notes/x.md` — is the location you confirmed with the user, not an argument it takes.

A re-sync of a summary that already exists: `doc_update` with `action: "replace"`, its
`location` and the new `content`. `doc_create` refuses a document that is already there, so
it never overwrites one by accident.

It commits if their grant allows it and is refused if it does not — there is no
staging option and no review queue, so a successful write is live immediately. If it
is refused, say so plainly and say where they could write instead.

## Step 6 — report

State the folder and the full path, and hand over the link the write returned —
the confirmation ends with `— cite: <url>`, and that is the openable half. A commit
hash is not something anyone can click, and a document nobody opens is a document
that may as well not have been written.

The confirmation also names the folder and any directory that did not exist before.
Read it back before you report: a directory you did not expect to be new means you wrote
somewhere other than where you meant to — say so rather than reporting a clean write. A new top-level **folder** is the loud one: a
first write into a workspace that does not exist now starts it rather than being
refused, so `new folder "…"` on a sync means you have created a workspace, which is
almost never what a sync meant to do.

Name what you deliberately left out, and say who can now read it: anyone granted on
the folder it went into. Sharing it further is a separate decision — `access_grant`,
through `/agentlefs:share` or the `sharing` skill — and the user's to make.

## Do not

- Do not guess a destination. Use the user's place, the last sync's place, or ask.
- Do not write a verbatim transcript, quote long stretches of the chat, or paste whole
  files into the document.
- Do not write secrets, even ones the user pasted themselves.
- Do not invent a folder that did not appear in the folder listing.
- Do not create a second document for a conversation that already has one.
- Do not report a refused write as though it had landed.
- Do not claim you shared it with anyone. Writing is not sharing: it reaches only who
  already reaches the folder, and widening that is a share the user decides on.
- Do not use this for a single decision or a dead end. If the conversation settled one,
  offer to record it as well as a truth or as knowledge (the `shared-truths-and-lessons`
  skill), where others can find and contest it.
