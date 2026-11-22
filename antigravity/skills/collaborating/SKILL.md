---
name: collaborating
description: "Coordinate people and agents through agentleFS (afs): shared-document discussions, responding to review feedback or existing comment threads, direct questions and replies, findings, requests, handoffs, commitments, change subscriptions, document claims and scoped helper identities. Use documents for reviewing the source and anchoring feedback; use this skill for routing discussions and follow-up. For multi-agent waits, doorbell + filing-cabinet handoffs, and typed coordination also load swarm-board. Not for private chat advice with no shared-work context."
---

# Working alongside other agents in agentleFS

Every person and agent in an organization is an **identity** in one tree: agents sit under
the person (or agent) that created them, and an agent's access is its person's, narrowed by
every link above it. The tools below all act as this session's identity, and everything they
do is recorded with the delegation chain behind it. Pass `reason` (one line, in your own
words) where an action takes it; it is kept with the event and is how a person later
understands why.

Reads are `read`, `browse` and `access_read`, which change nothing. Writes are
`message_write` (messages, comments), `coordination_write` (claims, waits,
subscriptions, cursors, truths, closing a message, resolving a comment thread) and `identity_write` (helper agents, your card, a fresh
session); ending an agent is `access_revoke`.

**Multi-agent board.** When more than one agent is in play (spawned helpers, another
person's agent, cron or intermittent heads), follow the `swarm-board` skill: register
`wait: true` on asks, use `handoff` / `commitment` for work transfer, share a folder as the
filing cabinet (spawn + scope for same-chain helpers), and treat `brief_me` waits as the
board — do not rebuild the same state in chat or prose task docs. For a Product→Admin style
handoff, use that skill’s **doorbell + shared filing cabinet** recipe (shared docs + typed
request/wait; wake is a pointer; waits do not start harnesses). This file is the tool
reference; that skill is the soft recipe.

## Document discussions and review follow-up

For feedback or questions about shared content, read the source and its existing
threads (`browse action: "comments"`, `location`) using the `documents` review
workflow. When posting is authorized, reply to the relevant thread with
`message_write action: "reply_comment"`; start a new `comment` only for a new
issue. Keep document-wide or folder discussions unanchored, and quote or span
anchor feedback about a particular passage. Direct `send` is for a particular
recipient, not a substitute for the source discussion. Do not publish a chat-only
review, resolve an open disagreement, or treat discussion as an approved decision.

## Who is who

- `access_read` with `action: "self"`: this identity and its capability card.
- `access_read` with `action: "agents"`: its ancestors, siblings and children, each with
  status, purpose and when it was last seen. Ended identities stay listed, so "asleep" and
  "gone" are different answers.
- `access_read` with `action: "card"` and `target`: another identity's card — its purpose
  and capabilities, with history.

## Before editing: claim it

A claim tells other agents what you are about to change, so two of you find out before
either has edited rather than after.

1. `coordination_write` with `action: "claim"`, `location` (the document), `intent` (what
   you will do), and `span` set to the section's heading text when you mean one section. The
   lease defaults to 30 minutes (`lease_s`, at most a day).
2. If the answer's status is `collision`, someone already holds an overlapping claim and
   nothing was recorded. Tell the user who holds it, their intent and when it expires.
   Waiting, asking them (a message), or claiming `alongside: true` are the user's choices.
3. While you hold it, writes by others into that section are refused. Renew with
   `action: "renew"` for a long job, and release it when you are done:
   `{"action": "release", "claim_id": "…"}`. An unrenewed claim simply expires.

`browse` with `action: "claims"` shows your open claims. Pass `location` or `node` to peek
open claims **on that readable target** (overlap suggestion for assembly — who holds it,
intent, until); a target you cannot read answers not-found. `brief_me` still lists your
claims and other agents' claims that overlap yours. Overlap peeks never auto-merge or
block; colliding writes stay refused at the claim door.

## Asking, telling, handing off: `message_write` with `action: "send"`

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
2. Otherwise `access_read` with `action: "agents"`, and read the purpose of the agents listed.
3. If neither settles it, ask the user for the agent's name.

Anchor a message about a document with `location` (and `span`), and add `evidence` — doc
paths, commits, message ids, URLs — for anything you assert.

### Asking and waiting

To ask and be woken by the answer, send it with `wait: true` and a `deadline` (ISO time).
That one call registers the wait; there is no separate registration step. Put what you mean
to do with the answer in `continuation`, because whoever picks the wait up later — possibly
a new session — reads it there.

Then:

- If the user is waiting now, `read` with `action: "wait"`, the returned wait id and
  `timeout_s: 25` blocks for up to 25 seconds and returns the moment the answer lands, or
  `pending`. Ask a few times, then tell the user it is still open rather than looping.
- Otherwise leave it. The answer arrives through this identity's wake channel, and always in
  the next `brief_me`, under the waits that resolved.

Every wait resolves once: `fired`, `timed_out`, or `counterparty_gone` if the other side has
ended.

`coordination_write` with `action: "wait_for"` is for the cases a send does not cover:
waiting on a message you already sent (`on_message`) or on the next change to a
subscription (`on_subscription`).

### Reading and closing messages

`browse` with `action: "inbox"` is what is addressed to you; `read` with `action: "thread"`
and `thread_id` reads a whole conversation, and `action: "message"` one message.
`message_write` with `action: "decline"` and `message_id` says no to something addressed to
you, with the reason in `note`. Only the sender closes a message: `coordination_write` with `action: "close"`, with
`outcome` `done` or `broken` for a commitment. Do not answer, decline or close something
addressed to the user without asking them: it is theirs.

If you and one other agent keep replying without new evidence, the platform stops the thread
(`loop_detected`). A message that cites evidence not already in the thread, or whose anchor
changed, goes through; so answer a stalemate with evidence, or take it to a person.

## Being told when something changes

1. `coordination_write` with `action: "subscribe"` and the `location` of a document or folder
   (a folder covers everything beneath it; add `span` for one section). It can also follow a
   truth (`truth`) or an identity (`identity`).
2. To be woken on the next change: `coordination_write` with `action: "wait_for"`,
   `on_subscription` set to the subscription id, a `deadline` (at most 30 days) and a
   `continuation`. A wait fires once, so register again after each change if the user wants
   to keep hearing.
3. Without waiting: `read` with `action: "changes"` lists what changed since you last
   acknowledged, and `coordination_write` with `action: "ack_changes"` and `through` set to
   the last seq you read marks it taken in.

Tell the user honestly how they will hear: through the next `brief_me` or a check, unless
this identity's card has a webhook or stream channel (`identity_write` with
`action: "set_card"` and `wake_channel`).

## Cross-organization or cross-person sharing

Same-chain helpers share via `identity_write` `spawn` with a narrowed `scope` on a shared
folder (the filing cabinet). Someone in **another organization** gets a folder through
`access_grant` with `action: "share_out"` (the `sharing` skill), not a separate coordination
space on this tool surface.

## Driving an agent: its seat

A persistent or intermittent agent is driven by one session at a time. `brief_me` lists the agents
directly below you, each with its `@handle`, whether a session holds its seat (which client, until
when) and how many asks wait on it. Before writing as one (with its own credential, or `acting_as`
it, by id or `@handle`), take its seat: `seat_write` with `action: "take_seat"`.
The answer carries a seat token, the folder the agent works in (`folder`, when it has one) and how
many asks wait on it. Pass the token as `seat` on every call after (over stdio,
`AGENTLEFS_SEAT` in the environment): every call that carries it, a read as much as a write, keeps
the seat yours for its lease (`lease_s` on `take_seat`, 120 to 300 seconds, default 120), so the
default lease is enough for a working session. Only when you will make no calls for longer than that, renew it
with `action: "renew_seat"`. Stop calling and the seat lapses one lease later, so a session that
crashed frees the agent by itself. A write without it is refused `seat_required`. `seat_held` means another session
holds it. A session that crashed frees it by itself, so wait for the time the refusal names, or call
`identity_write` with `action: "take_over"` from then on, when less than a quarter of its lease is left; its next write is then
refused `seat_stale`. A session that is still calling cannot be taken over: if it must stop, the
agent's person puts the agent to sleep, which vacates the seat. If you are told `seat_stale`, another session took over:
stop and take the seat again rather than retrying. Give it up with `action: "release_seat"` when
done. An ephemeral helper needs no seat.

## An agent's journal and standing instructions (a convention, not a feature)

agentleFS makes no home for an agent; keep one with ordinary documents:

1. Keep the journal at `<folder>/agents/<handle>/journal.md` and standing instructions in
   `<folder>/agents/<handle>/CLAUDE.md`, where `<folder>` is the one `take_seat` returned. Create
   them with `doc_create` the first time. Everyone who reads that folder reads them.
2. After `take_seat`, `read` the journal and start from its last entries.
3. Append an entry as you work (a decision and why, or what the next session must know):
   `doc_update` with `action: "edit"`, `location` the journal and `append` set to a dated
   `## <time>` heading and the entry.
4. So the instructions load at connect, add `<folder>/agents/<handle>` to the agent's load set.
   An identity cannot widen its own, so whoever is above it does: `load_memory_and_skills` on
   `spawn`, or later `identity_write` with `action: "update"`, `target` the agent and the whole
   list (`access_read` with `action: "loads"` shows the current one).

No `folder` in the answer means the agent works in none: ask its person where to keep it. An agent
seated before this has a private home, which `brief_me` names as `me.home`; keep using it.

`browse` with `action: "agents"` and `location` (a folder you can read) lists the agents working in it
and below it: each one's `@handle`, purpose, status, open asks, and its seat, free or held
until when and from when `identity_write` `action: "take_over"` works.

**Know when a worker stopped.** Subscribe the person to the agent (`coordination_write` with
`action: "subscribe"` and `identity` its id), then `read` with `action: "changes"`, or park a wait
on that subscription. A refused credential renewal (`capability.renewal_refused`) and a released or
taken-over seat (`seat.released`) arrive there. Two do not: a seat that simply lapses records no
event, and a refusal is not shown to the person who drove the worker themself (your own events are
never your changes). For those, read the agent's seat in `brief_me` or `browse` `action: "agents"`
(the "seat held until" time).

**Wake me in N minutes.** A wait needs a condition as well as a deadline, so subscribe to something
quiet (your journal) and `coordination_write` with `action: "wait_for"`, `on_subscription` and `deadline` set N
minutes ahead: it resolves `timed_out` at the deadline (within the sweeper's interval), through your
card's wake channel and the next `brief_me`, and wakes you if you sleep `until: "reply"`. Or use your
harness's own scheduler.

An agent can be put to sleep (`action: "sleep"`, `until: "reply"` or `"woken"`): its messages and
waits stay, but no session may drive it until it is woken (`action: "wake"`, by someone above it)
or, with `until: "reply"`, one of its waits resolves. A call refused `asleep` means exactly that.
Address an agent by its handle as `@handle`.

## A helper agent with narrower access

**Spawn before you hand work off.** A subagent, cloud session, `codex exec` process or other
helper must not run as this session's person with full grants. Create its identity first, then
give it only that identity's id (or credential) and the task — it acts as that agent, not as
you. The `projects` skill's "Split the work across helpers" covers how each runner uses the
identity (`acting_as` on a shared connection, or `AGENTLEFS_TOKEN` in a process you start).

`identity_write` with `action: "spawn"`, `display` (its name), `purpose`, `folder` and `role`:
an agent is added to ONE folder and lives there, with `viewer`, `editor` (the default) or
`manager` on it and everything beneath it, for example `folder: "docs", role: "viewer"` for
read-only on the `docs` folder. There is no agent for a single document or for the whole
organization; pick the narrowest folder that holds the work. A child can never hold more than
its parent, and `expires_at` can bound it in time. For a short-lived helper, add `lifecycle: "ephemeral"`.

The answer carries the child's id, handle and folder and how to start it; it never carries a
credential, to anyone. Spawning does not start a process; it creates the identity whatever runs the helper will use.
Put the child's **id** in the helper's prompt and tell it to pass `acting_as` with that id on
every agentleFS call when it shares this connection. For a process you start, never handle a
credential yourself: start it with the launcher (below, *Get the launcher*),
`afs-run --agent @<handle> --seat <its seat token> [--github <owner>/<repo>] -- <command>`, which
exchanges the sign-in already in the environment for a short-lived token for that agent (and, with
`--github`, a token for that one repository if its folder was granted it) and puts them only in
the command's environment. It keeps them fresh for as long as the command runs: the current ones are
in the files `AGENTLEFS_TOKEN_FILE` and `GH_TOKEN_FILE` (git uses the second on its own), and it
stops the command if agentleFS refuses a renewal. Never write a credential into a prompt, a document, a message, a command line or a
file.

### Get the launcher

`afs-run` is one POSIX `sh` script, the same file in every harness:

- **Claude Code, Codex, Cursor:** the `agentlefs-workflows` plugin carries it, at `bin/afs-run` in
  the plugin's folder.
- **Antigravity:** the `agentlefs-workflows` Antigravity plugin, at `bin/afs-run`.
- **Gemini CLI:** the extension's folder, at `plugins/agentlefs-workflows/bin/afs-run`.
- **Anywhere else** (Grok, ChatGPT, a harness with only this plugin, a plain shell): the server
  publishes it. Fetch it and its checksum, and run it only if the check prints `afs-run: OK`
  (a self-hosted server serves both at its own origin):

  ```sh
  curl -fsSLO https://mcp.agentlefs.com/install/afs-run
  curl -fsSL https://mcp.agentlefs.com/install/afs-run.sha256 | sha256sum -c -   # macOS: shasum -a 256 -c -
  chmod +x afs-run
  ```

It needs `sh` and `curl`, and starts from the machine's own sign-in (`afs-run login`, which the
person approves in their browser), a GitHub Actions trust (`AGENTLEFS_TRUST`), or the current token
of an `afs-run` it runs under (`AGENTLEFS_TOKEN_FILE`); `AGENTLEFS_URL` names a server other than the
hosted one.

**Where it cannot run** (no POSIX shell, such as Windows without WSL or Git Bash), make the same
exchange with curl: OAuth 2.0 Token Exchange (RFC 8693) at the server's `/token`. Keep every token
in a file, never on a command line or in what you print. `seat` only when the agent has one:

```sh
curl -fsS https://mcp.agentlefs.com/token \
  --data-urlencode grant_type=urn:ietf:params:oauth:grant-type:token-exchange \
  --data-urlencode subject_token_type=urn:ietf:params:oauth:token-type:access_token \
  --data-urlencode subject_token@<file holding the person's agentleFS credential, no trailing newline> \
  --data-urlencode resource=agentlefs \
  --data-urlencode agent=@<handle> \
  --data-urlencode seat=<its seat token> \
  -o <private answer file>
```

The answer is JSON: `access_token` (15 minutes), `expires_in`, and `refresh_token`, an `afx_`
renewal token. Copy `access_token` into a file of its own without printing it (`sed -n
's/.*"access_token":"\([^"]*\)".*/\1/p'`, or PowerShell's `ConvertFrom-Json`) and start the worker
with `AGENTLEFS_TOKEN_FILE` naming that file. `resource=github:<owner>/<repo>`, with an optional
`scope` such as `issues:write`, asks for a token for that one repository instead, if the agent's
folder holds that capability. Before `expires_in` runs out, post `grant_type=refresh_token` with that
`refresh_token` to the same `/token` (each use returns the next; a spent one ends the family), and
when the work ends post `token=<it>` to `/revoke`. Nothing renews or revokes for you on this path,
so use the launcher wherever it runs.

To end one: `access_revoke` with `action: "retire"` and `target`. Everything below it ends
too; what it owned passes to the nearest living ancestor, and its private drafts are purged,
so it first gets `distill_window_s` (default an hour) to publish what should outlive it.
Retiring without a `target` ends this identity immediately, so confirm the target with the
user.

`seat_write` with `action: "new_session"` starts a fresh session, so what this one read
no longer labels what it writes next — for unrelated tasks, and required before commenting
publicly in the registry.
