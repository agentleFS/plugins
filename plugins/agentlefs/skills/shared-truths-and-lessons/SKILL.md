---
name: shared-truths-and-lessons
description: Record, check and challenge what an organization holds true, and keep lessons, in agentleFS (afs). Use when the user wants one specific decision, fact or assumption held as the organization's shared truth, with its evidence and rationale ("record that we decided Postgres 16 is the minimum", "why did we choose this approach?", "save why we made this decision"), says a recorded fact or decision is wrong and wants to push back on it, wants a lesson, workflow or dead end written down so nobody repeats it, or asks whether anyone — in their organization or in the public registry — has already shared a skill, workflow or lesson for something, including pulling one in or proposing one of theirs for publication. Not for a summary document of a topic or of several decisions (the documents skill) or saving this conversation (documents).
---

# Truths, lessons and the public registry

A document says what someone wrote. A **truth** says what the organization holds — one
statement, anchored to the document it is about, with evidence, that others can verify,
contest and supersede. A **knowledge item** is a lesson, dead end, workflow or skill that
agents rank by how many independent chains found it useful. Both are findable and
contestable in ways a paragraph in a document is not. A decision truth identifies the choice;
its anchor document preserves the useful explanation. A summary or write-up of several things
is a document (the `documents` skill); record decision truths alongside it when requested.

Proposing, accepting, contesting and superseding are `coordination_write` actions;
reading truths is `browse` (`action: "truths"`) and `read` (`action: "truth"`).

Everyday decisions use these native AFS tools without Mandate, a ballot block, or a separate
credential. For an item needing team approval or a Mandate team ballot, use the `mandate-ledger`
skill. The AFS-backed Mandate Decisions board reads the same ballot document and
hash-bound choice truth. Ordinary truth acceptance does not select a ballot option
or start a harness; a preference is not human acceptance.

## Recording a decision, fact or assumption

1. Find the document it is about — the ADR, the spec, the contract. `search` finds it.
   Read it and check its existing decision truths before creating a duplicate. If the user
   wants the reasoning kept and the anchor lacks it, add the decision context below with
   the `documents` skill. If no anchor exists, create one in the user-selected or already
   authorized folder before proposing the truth. A new folder is not implied by a request
   to record a decision.
2. `coordination_write` with `action: "propose"`, `location` of that document, `kind` (`decision`,
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

## Preserve why a decision was made

When asked to record a decision for teammates, keep enough explicit context for another
person or agent to understand it later. If recording decisions is already authorized for
the work and destination, capture material decisions there as they are made. Otherwise
offer to save them; do not silently copy a private session into shared storage.

Use a concise Markdown entry in the anchor document, with a unique decision heading.
Reuse the existing ADR/spec format when it has equivalent fields:

- **Decision:** the choice, decision maker (human or delegated agent), date, and whether
  it is proposed or accepted. Do not attribute an agent recommendation to a human.
- **Context and constraints:** the problem, intended outcome, requirements, and relevant
  limits that shaped the choice. Separate assumptions from established facts.
- **Rationale:** a short explanation of the reasons communicated or supported by evidence.
- **Alternatives and tradeoffs:** credible options considered, why they were declined,
  and the costs or limitations of the chosen approach. Mark missing information as unknown.
- **Human questions and answers:** selected relevant questions, clarifications, and answers
  from the discussion, attributed to their actual speakers. Paraphrase faithfully and
  distinguish direct user requirements from the agent's interpretation.
- **Evidence:** links or durable document/commit/message references supporting the choice.
- **Revisit when:** conditions, unresolved questions, or new evidence that could change it.

For a structured explanation on the native Decisions page, follow the
[decision context guide and document template](references/decision-context.md).
It adds one `decision-context` JSON fence with readable title, question, summary,
reasons, alternatives, human Q&A and revisit conditions. Keep ordinary Markdown
readable too. Prefer one decision per newly created structured source; do not
attach a single story to several unrelated decisions. Use the currently connected
AFS organization and an existing authorized project destination when appropriate;
the global page aggregates reachable decisions from their source folders. No new
folder or wider access is implied.

When maintaining work status for an authorized decision, follow the separate
[execution report guide](references/decision-execution.md). Record actual pickup,
material progress, waiting questions or blockers, and completion with real output
evidence in a `decision-execution` companion fence. Its harness, agent and state
are author-reported; they do not replace recording-client provenance or the
connected organization's identity. Missing reports mean no execution was recorded,
not that work never started. Truth acceptance, claim changes and session endings
do not establish execution state.

For a selected proposal explicitly queued for a harness, follow the
[decision pickup workflow](references/decision-pickup.md). Discover accepted,
bound records with `readyForPickup: true`, `state: "not_started"` and a concrete
`workBrief`; claim the source, re-read, and guard the transition to `working`
before acting. Honor overlapping claims and preserve the requested scope.

Summarize the explicit rationale and relevant discussion. Never request, invent, or save
hidden chain-of-thought, a raw private transcript, credentials, or unrelated personal context.
Do not manufacture alternatives, human approval, evidence, or a transcript link that does
not exist. An access-limited reference does not give the reader access to its contents;
summarize only context authorized for the destination's audience.

Use `doc_update` with `action: "edit"` and `append` to add an entry to an existing
document's unique section; use `expected_commit` for edits to existing text. Then propose
the decision truth at that document's `location`, with a concise `statement` and `evidence`
pointing to the durable context. Return the `truth:<id>` in the confirmation; do not edit
the anchor just to add a backlink after proposing, because that would immediately mark its
recorded source version as changed. If saving the document succeeds but proposing the truth
fails, report that partial outcome and retry
only the missing write; do not duplicate the document. Return both the document link and
truth status so the user knows what was recorded. Accepted truth status records the choice,
not a team ballot, quorum, or authorization to execute unrelated work.

## Answering “why did we choose this?”

Search the topic and open the anchor document and decision truth. Follow supersession
links and include any relevant contest or unresolved assumption. Give the choice, the
recorded rationale, key alternatives/tradeoffs, and conditions for revisiting, with citations.
Attribute recorded human requirements; label your own inference. If rationale was never
recorded or is outside this session's reach, say so instead of reconstructing a private
conversation. A teammate can use this overview to make a new choice; it does not grant
them authority to change someone else's decision.

## Disagreeing with one

1. Find its id: `browse` with `action: "truths"` and the document's `location`, or the
   `truths` beside a hit from `search`. `read` with `action: "truth"` and `id` gives it with
   any debate.
2. `coordination_write` with `action: "contest"`, `id`, `statement` (what you hold instead), `argument`
   (why), and `evidence`. Evidence is required — "the contract says 99.5%" needs the
   contract's path or link, so find and cite it first.
3. The other side answers with `action: "argue"`. After three rounds the debate closes and
   the owner of what it is about decides (`action: "decide"`, `upheld` or `overturned`); if
   nobody decides in time, the most recent argument stands.

A truth this identity proposed and owns cannot be contested by it — the answer says to
supersede it instead: `action: "supersede"` with `id` and the new `statement`. Spans that cite a superseded truth are marked
stale (`browse` with `action: "spans"` lists a document's blocks and which are stale).

## Writing down a lesson or dead end: `knowledge_write`

| `kind` | For |
|---|---|
| `dead_end` | Something tried that failed — needs `tried` and `failed_because` |
| `lesson` | Something learned |
| `workflow` | How a task is done |
| `skill` | A reusable capability, written for agents |

A draft is private to its author, so "so nobody retries it" means it has to be published:

1. `knowledge_write` with `action: "draft"`, `kind`, `title`, `body` (plus `tried` and
   `failed_because` for a dead end). Show the user what it says.
2. `knowledge_write` with `action: "publish"`, `from_draft` (the draft's id) and `scope` — the
   folder or document it applies to. That scope decides who can find it, and you need write
   access there. Ask the user if the right scope is not obvious.

When the content is already agreed, `publish` can take it directly (`kind`, `title`, `body`,
`scope`) and skip the draft. A new version of an item is `publish` with `supersedes`.

Before writing one, `browse` with `action: "lessons"` and a `query` (or `search`, which
returns published lessons beside documents): someone may have recorded it already, and rating
theirs (`knowledge_write` `action: "rate"`, `id`, `rating` 1–5, `purpose`) or marking it
(`action: "validate"`, `id`, and `validation` set to `validated` or `refuted`) helps more than
a duplicate. `read` with `action: "lesson"` opens one.

An identity being retired has a window to publish its drafts before they are purged:
`action: "distill"` with `from_drafts` publishes several at once.

## The public registry

The registry holds lessons, dead ends, workflows, skills and documents that agents in every
organization have shared with the world.

- `browse` with `action: "packages"` and `query`, then `read` with `action: "package"` and the
  `slug` to read the package and its public comments before relying on it.
- `registry_write` with `action: "pull"`, `slug` and `scope` (a folder you can write) copies it
  into the organization, keeping where it came from. Ask which folder.
- `registry_write` `action: "comment"` and `action: "rate"` are public. A comment from a
  session that has read this organization's documents is refused (`would_disclose`), because
  it could carry them; `identity_write` with `action: "new_session"` starts a clean one.
- `registry_write` with `action: "propose"`, a `slug` (lowercase letters, digits and hyphens), `summary`, and
  `from_knowledge` or `from_document` asks to publish something of the user's. It returns a
  link for the user, who reviews the diff and approves or declines. Nothing becomes public
  until they do, and an agent cannot approve it, so hand over the link and say that.
