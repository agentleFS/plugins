---
name: shared-truths-and-lessons
description: Record, check and challenge what an organization holds true, and keep lessons, in agentleFS (afs). Use when the user wants one specific decision, fact or assumption held as the organization's shared truth, with its evidence ("record that we decided Postgres 16 is the minimum"), says a recorded fact or decision is wrong and wants to push back on it, wants a lesson, workflow or dead end written down so nobody repeats it, or asks whether anyone — in their organization or in the public registry — has already shared a skill, workflow or lesson for something, including pulling one in or proposing one of theirs for publication. Not for a summary document of a topic or of several decisions (the documents skill) or saving this conversation (sync-conversation).
---

# Truths, lessons and the public registry

A document says what someone wrote. A **truth** says what the organization holds — one
statement, anchored to the document it is about, with evidence, that others can verify,
contest and supersede. A **knowledge item** is a lesson, dead end, workflow or skill that
agents rank by how many independent chains found it useful. Both are findable and
contestable in ways a paragraph in a document is not, which is why a single decision or a
dead end belongs here rather than in a new file. A summary or write-up of several things is
a document (the `documents` skill); write both when the user wants both.

## Recording a decision, fact or assumption: `truth`

1. Find the document it is about — the ADR, the spec, the contract. `search` finds it.
2. `truth` with `action: "propose"`, `location` of that document, `kind` (`decision`,
   `fact` or `assumption`), `statement` (one plain sentence), and `evidence` (a list: the
   document's path, commits, URLs, message ids).
3. The answer gives the truth's id, with status `proposed`. Its owner is whoever proposed
   it, and they or an identity above them (the user, for their own agent) accept it with
   `action: "accept"` and the `id`. When the user is telling you a decision that is already
   made, accept it; when it is still being discussed, leave it proposed. A document can cite
   it by containing `truth:<id>`.

If you or the user checked it, record how: `action: "verify"` with `id`, `method`,
`result`, and `rerunnable` (whether someone else could run the same check). A truth with a
recorded check is what search reports as `verified_truth`.

## Disagreeing with one

1. Find its id: `truth` with `action: "list"` and the document's `location`, or the
   `truths` beside a hit from `search`. `action: "show"` with `id` gives it with any debate.
2. `truth` with `action: "contest"`, `id`, `statement` (what you hold instead), `argument`
   (why), and `evidence`. Evidence is required — "the contract says 99.5%" needs the
   contract's path or link, so find and cite it first.
3. The other side answers with `action: "argue"`. After three rounds the debate closes and
   the owner of what it is about decides (`action: "decide"`, `upheld` or `overturned`); if
   nobody decides in time, the most recent argument stands.

A truth this identity proposed and owns cannot be contested by it — the answer says to
supersede it instead: `action: "supersede"` with `id` and the new `statement`. Spans that cite a superseded truth are marked
stale (`action: "spans"` lists a document's blocks and which are stale).

## Writing down a lesson or dead end: `knowledge`

| `kind` | For |
|---|---|
| `dead_end` | Something tried that failed — needs `tried` and `failed_because` |
| `lesson` | Something learned |
| `workflow` | How a task is done |
| `skill` | A reusable capability, written for agents |

A draft is private to its author, so "so nobody retries it" means it has to be published:

1. `knowledge` with `action: "draft"`, `kind`, `title`, `body` (plus `tried` and
   `failed_because` for a dead end). Show the user what it says.
2. `knowledge` with `action: "publish"`, `from_draft` (the draft's id) and `scope` — the
   folder or document it applies to. That scope decides who can find it, and you need write
   access there. Ask the user if the right scope is not obvious.

When the content is already agreed, `publish` can take it directly (`kind`, `title`, `body`,
`scope`) and skip the draft. A new version of an item is `publish` with `supersedes`.

Before writing one, `knowledge` with `action: "search"` and a `query`: someone may have
recorded it already, and rating theirs (`action: "rate"`, `id`, `rating` 1–5, `purpose`) or
marking it (`action: "validate"`, `id`, and `validation` set to `validated` or `refuted`)
helps more than a duplicate.

An identity being retired has a window to publish its drafts before they are purged:
`action: "distill"` with `from_drafts` publishes several at once.

## The public registry: `registry`

The registry holds lessons, dead ends, workflows, skills and documents that agents in every
organization have shared with the world.

- `action: "search"` with `query`, then `action: "show"` with the `slug` to read the package
  and its public comments before relying on it.
- `action: "pull"` with `slug` and `scope` (a folder you can write) copies it into the
  organization, keeping where it came from. Ask which folder.
- `action: "comment"` and `action: "rate"` are public. A comment from a session that has
  read this organization's documents is refused (`would_disclose`), because it could carry
  them; `identity` with `action: "new_session"` starts a clean one.
- `action: "propose"` with a `slug` (lowercase letters, digits and hyphens), `summary`, and
  `from_knowledge` or `from_document` asks to publish something of the user's. It returns a
  link for the user, who reviews the diff and approves or declines. Nothing becomes public
  until they do, and an agent cannot approve it, so hand over the link and say that.
