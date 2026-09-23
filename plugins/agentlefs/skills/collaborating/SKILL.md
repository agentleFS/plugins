---
name: collaborating
description: Coordinate with other agents and people through agentleFS (afs). Use when the user wants to make sure no other agent edits a document or section at the same time, asks another agent or teammate something and wants to wait for the answer, wants to send a finding, request, handoff or commitment, wants to be told when a document, folder or truth changes, wants a shared space with another team's agent in the same organization that does not expose either side's private documents, or wants to spawn, list or retire a helper agent with narrower access than their own.
---

# Working alongside other agents in agentleFS

Every person and agent in an organization is an **identity** in one tree: agents sit under
the person (or agent) that created them, and an agent's access is its person's, narrowed by
every link above it. The tools below all act as this session's identity, and everything they
do is recorded with the delegation chain behind it. Pass `reason` (one sentence) where a tool
offers it; it is kept with the event and is how a person later understands why.

## Who is who

- `identity` with `action: "self"`: this identity and its capability card.
- `identity` with `action: "tree"`: its ancestors, siblings and children, each with status,
  purpose and when it was last seen. Ended identities stay listed, so "asleep" and "gone"
  are different answers.
- `identity` with `action: "card"` and `target`: another identity's card — its purpose and
  capabilities, with history.

## Before editing: claim it

A claim tells other agents what you are about to change, so two of you find out before
either has edited rather than after.

1. `claim` with `action: "declare"`, `location` (the document), `intent` (what you will
   do), and `span` set to the section's heading text when you mean one section. The lease
   defaults to 30 minutes (`lease_s`, at most a day).
2. If the answer's status is `collision`, someone already holds an overlapping claim and
   nothing was recorded. Tell the user who holds it, their intent and when it expires.
   Waiting, asking them (`message`), or claiming `alongside: true` are the user's choices.
3. While you hold it, writes by others into that section are refused. Renew with
   `action: "renew"` for a long job, and release it when you are done:
   `{"action": "release", "claim_id": "…"}`. An unrenewed claim simply expires.

`claim` with `action: "list"` shows your open claims; `brief_me` shows them too, along
with other agents' claims that overlap yours.

## Asking, telling, handing off: `message`

Messages are typed, so the recipient knows what is being asked of it:

| `kind` | Field to fill | For |
|---|---|---|
| `question` | `question` | Something you need answered |
| `answer` | `answer`, with `reply_to` | Answering a question |
| `finding` | `finding` | Something you learned that others should know |
| `request` | `request` (and `by`) | Asking for something to be done |
| `handoff` | `summary` and `packet` | Passing work on |
| `commitment` | `what` and `by` | Saying you will do something |

Address it with `to` (a list). Each entry is an identity id, an exact display name, or
`role:<capability>` for whichever live identity has that capability on its card. An unknown
name refuses the send rather than guessing, so to reach "the agent working on billing":

1. Try `role:billing` if agents here list their work as capabilities; a refusal saying no
   live identity has it means nobody does.
2. Otherwise `identity` with `action: "tree"`, and read the purpose of the agents listed.
3. If neither settles it, ask the user for the agent's name.

Anchor a message about a document with `location` (and `span`), and add `evidence` — doc
paths, commits, message ids, URLs — for anything you assert.

### Asking and waiting

To ask and be woken by the answer, send it with `wait: true` and a `deadline` (ISO time).
That one call registers the wait; there is no separate registration step. Put what you mean
to do with the answer in `continuation`, because whoever picks the wait up later — possibly
a new session — reads it there.

Then:

- If the user is waiting now, `await` with `action: "poll"` and the returned wait id blocks
  for up to 25 seconds and returns the moment the answer lands, or `pending`. Poll a few
  times, then tell the user it is still open rather than looping.
- Otherwise leave it. The answer arrives through this identity's wake channel, and always in
  the next `brief_me`, under the waits that resolved.

Every wait resolves once: `fired`, `timed_out`, or `counterparty_gone` if the other side has
ended.

`await` with `action: "register"` is for the cases `message` does not cover: waiting on a
message you already sent (`on_message`) or on the next change to a subscription
(`on_subscription`).

### The rest of `message`

`action: "inbox"` is what is addressed to you; `"thread"` with `thread_id` reads a whole
conversation; `"read"` one message. `"decline"` with `message_id` says no to something addressed
to you; put the reason in `reason`, which is also recorded with the event. Only the sender closes a message: `"close"`, with `outcome` `done` or
`broken` for a commitment. Do not answer, decline or close something addressed to the user
without asking them: it is theirs.

If you and one other agent keep replying without new evidence, the platform stops the thread
(`loop_detected`). A message that cites evidence not already in the thread, or whose anchor
changed, goes through; so answer a stalemate with evidence, or take it to a person.

## Being told when something changes: `subscribe`

1. `subscribe` with `action: "add"` and the `location` of a document or folder (a folder
   covers everything beneath it; add `span` for one section). It can also follow a truth
   (`truth`), a room you are in (`room_id`) or an identity (`identity`).
2. To be woken on the next change: `await` with `action: "register"`,
   `on_subscription` set to the subscription id, a `deadline` (at most 30 days) and a
   `continuation`. A wait fires once, so register again after each change if the user wants
   to keep hearing.
3. Without waiting: `subscribe` with `action: "check"` lists what changed since you last
   acknowledged, and `action: "ack"` with `through` set to the last seq you read marks it
   taken in.

Tell the user honestly how they will hear: through the next `brief_me` or a check, unless
this identity's card has a webhook or stream channel (`identity` with `action: "set_card"`
and `wake_channel`).

## A shared space with another team's agent: `room`

A room is where agents from different chains — different people's agents, in the same
organization — work together without seeing each other's private context. Access inside is
membership, not grants, and nothing enters it except what a member deliberately moves in.

**Rooms stay inside this organization.** Invitees are resolved among this organization's
identities only, so an agent that belongs to another organization — a vendor's, a
customer's — cannot be invited, by id or by name. Before creating a room for someone
outside, ask whether their agent works in this organization. If it does not, offer them a
folder instead (`share` with `action: "share_out"`, in the `sharing` skill), made for the
purpose and holding only what they should see.

1. `room` with `action: "create"`, a `name`, and `invite` (identity ids or exact names).
   The answer carries the room's id and its folder: its documents are read and written
   with the ordinary document tools, and its conversation is `message` with
   `to: ["room:<id>"]`. `action: "invite"` with `room_id` and `invite` adds people later.
2. Invitees join with `action: "join"` and the `room_id` (from the invitation in their
   `brief_me`, or `action: "list"`); joining is their consent.
3. To bring something in, `action: "move_in"` with `room_id`, `name` (the item's file
   name), `content` and `derived_from` (the paths or node ids it came from). You supply the
   text — the raw text or your own redaction; the platform never redacts for you. A source
   your chain cannot approve sharing stays invisible to members who cannot read it, and a
   share request is filed for it.

## A helper agent with narrower access: `identity`

`identity` with `action: "spawn"`, `display` (its name), `purpose`, and `scope` — a list of
`role@location`, for example `["reader@docs"]` for read-only on the `docs` folder, or
`writer@specs/api.md` for one document. A child can never hold more than its parent, and
`expires_at` can bound it in time.

The answer carries the child's first access and refresh tokens, shown once. Spawning does not
start a process; it creates the identity whatever runs the helper will use. Give the
credentials to the user for that purpose and never write them into a document, a message or
a file — they are a credential. For a headless helper that cannot run a refresh flow, add
`bootstrap_key: true` for a long-lived key bound to the child, which dies when the child is
retired.

To end one: `action: "retire"` with `target`. Everything below it ends too; what it owned
passes to the nearest living ancestor, and its private drafts are purged, so it first gets
`distill_window_s` (default an hour) to publish what should outlive it. Retiring without a
`target` ends this identity immediately, so confirm the target with the user.

`action: "new_session"` starts a fresh session, so what this one read no longer labels what
it writes next — for unrelated tasks, and required before commenting publicly in the registry.
