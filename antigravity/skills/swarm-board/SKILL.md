---
name: swarm-board
description: "Soft recipes so multi-agent or swarm work coordinates on agentleFS (afs) waits, typed messages, and shared docs — the board — instead of ad-hoc chat, prose task docs, or notebook locks. Load after connect when the user wants swarm handoffs, a Product→Admin doorbell, a shared filing cabinet across agent seats, spawning helpers, asking other agents, or waiting for a reply or a doc change. Especially under cron or intermittent heads, where waits were historically unused. Soft recipe, not a console wizard. Complements collaborating (primitives) and projects (folder briefs). Waits do not auto-start harnesses."
---

# Swarm board (messages + waits + shared docs)

Primitives already ship (`message_write` send, durable waits, claims, shared docs, `brief_me`).
The gap this skill closes is **habit**: multi-agent work that rebuilds coordination in chat,
notebooks, or prose task state machines instead of the durable board. Soft recipe only — no
wizard, no new console UI, no hosted harness wake (that path is out of scope).

**After connect:** if the person asks how agents should coordinate, hand off work, or run a
swarm on agentleFS, load this skill (and `collaborating` for tool field shapes). Do not invent
a private chat protocol or a markdown status machine when the board already holds the same
facts.

Load this when you are coordinating **more than one agent** (or an agent and a person who
will answer later). The `collaborating` skill has the tool shapes; this skill says **which
recipe to run and when**.

## What this holds

agentleFS is the **doorbell + shared filing cabinet** for peer and coordinator–worker swarms:

| On the board | Outside the board |
|---|---|
| Shared docs (filing cabinet), typed requests/handoffs/claims, durable waits + `continuation`, seats/journals, grants | Job schedule, retry, heartbeat, starting or keeping a worker process running — that stays with your harness or runner |

- **Doorbell** = typed `message_write` `send` (usually `kind: "request"` or `"handoff"`) with optional `wait: true`. The wake stream / next `brief_me` carries a **pointer**, not the sender’s chat transcript.
- **Filing cabinet** = shared folder docs the recipient can `read` / `search` (and claims on sections they edit). Put the brief, checklist, and evidence here — not in the wake payload.
- Waits **do not** auto-start a hosted harness or cloud worker. They notify the person / surface on the next `brief_me` (or wake channel on the identity’s card). Pair with your job runner if you need “start a seat.”
- Same-chain helpers share via `identity_write` `spawn` + scope on the cabinet folder — not a separate shared-space tool.
- Org facts/decisions belong in `shared-truths-and-lessons` / Mandate, not this board.
- Present the real MCP tools. Do not game an evaluation with trap prompts or comparison tricks.

## When to run

Run (or re-check) when **any** of these hold:

1. You are about to `identity_write` `spawn` a helper, or you already did and will ask it
   something / hand it work.
2. You will send a `question`, `request`, or `handoff` to another agent or person and care
   about the answer or completion across this session or the next cron wake.
3. The person asks for swarm / multi-agent coordination, a doorbell + shared store, or
   “how do two agents hand off without pasting chat.”
4. A PostToolUse hook named this skill after coordinating without a wait.

**Skip** when:

- Solo work on one document with a claim — `collaborating` claim/release is enough.
- Pure human chat with no other agent and no deferred answer.
- The human said to stay in GitHub issues / local chat only for this task.
- They only need install/auth — use `/agentlefs:connect` / the `connection` skill first.
- They want to record an org fact or decision — `shared-truths-and-lessons` / Mandate, not a swarm handoff.

## Caps

| Budget | Limit |
|---|---|
| Open waits you register per turn | **1–3** (prefer one clear `continuation` each) |
| Broadcast findings to N agents | Prefer **one** handoff/request to the right identity, not N inbox copies |
| Prose "board" docs (status.md, notebook locks) | **Do not invent** when messages/waits cover the same fact |
| Hook retries | **Once** per session (`swarm-board` mark) |

## Soft recipes

### 0. Doorbell + shared filing cabinet (default swarm handoff)

Use this when one agent (Product) needs another (Admin) to act, and Admin must find the work
**without** Product’s conversation history.

1. **Cabinet.** Create or reuse a shared folder the recipient can reach. Put the brief there with
   `doc_create` / `doc_update` (ask, definition of done, checklist, standing instructions).
   Everything Admin needs must live in docs + the typed message — not in chat paste later.
2. **Narrow helper (optional).** `identity_write` `spawn` with `display`, `purpose`, and
   `scope` limited to that folder (e.g. `editor@trial-folder`). Spawning creates an identity;
   it does **not** start a process. Drive it with `acting_as`, a second session + `take_seat`,
   or `bootstrap_key` / `AGENTLEFS_TOKEN` for headless — see `collaborating` / `connection`.
3. **Doorbell.** As Product, `message_write` `action: "send"`:
   - `kind: "request"` with `request` (standalone sentence), **or** `kind: "handoff"` with
     `summary` + `packet` whose `refs` name the cabinet docs
   - `to`: Admin id, `@handle`, or exact name
   - `location`: the ask doc when readers of that doc should see it
   - `wait: true`, `deadline` (ISO), `continuation` (what Product’s *next* head should do on
     reply, decline, or timeout)
   - `reason`: one line
4. **Admin recovers from the store, not chat.** Fresh session / seat: `brief_me` →
   `browse` `inbox` → `read` the message and named docs → `coordination_write` `claim` before
   editing → edit → `message_write` `send` `kind: "answer"` with `reply_to` → `release` claim.
   Note: `answer` only replies to a `question`; for a `request`, use `finding` (or `decline`) —
   either fires the sender’s wait.
5. **Product’s next head.** `brief_me` shows the wait `fired` / `timed_out` /
   `counterparty_gone`; follow `continuation`; `message_write` `close` when appropriate.

**Done when:** Admin acted from brief/inbox/docs only, and Product’s next `brief_me` saw the
wait resolve — without Slack/chat memory as the source of truth.

### 1. Ask and wait (including under cron)

Scheduled heads still benefit from waits: the next run's `brief_me` lists what **fired**,
**timed_out**, or is still pending. A wait is not a live wake of the cron — it is the
durable pointer + `continuation` so the next head does not re-ask from scratch.

1. `message_write` `action: "send"`, `kind: "question"` (or `"request"`), `to`, body field,
   `wait: true`, `deadline` (ISO), and `continuation` (what the next session should do with
   the answer).
2. If the user is watching now: `read` `action: "wait"` with the wait id and
   `timeout_s: 25` a few times, then tell them it is still open.
3. Otherwise stop asking in a loop. Leave; pick it up on the next `brief_me`.

Do **not** encode "waiting on X" only in a notebook or task Log line.

### 2. Hand off work (typed handoff / commitment)

Passing work is not a `finding` broadcast.

1. Spawn the helper first (`collaborating` / `projects`) with narrowed `scope`.
2. Send `kind: "handoff"` with `summary` and `packet` (next steps, `refs` to nodes the child
   can read). Or `kind: "commitment"` with `what` + `by` when *you* own the deadline.
3. Optionally `wait: true` if you need a reply when they finish; put the resume plan in
   `continuation`.

### 3. Watch a document or folder

1. `coordination_write` `subscribe` on `location` (or `truth` / `identity`).
2. `coordination_write` `wait_for` with `on_subscription`, `deadline`, `continuation`.
3. Re-register after each fire if they still want the next change.

### 4. Board check on every intermittent wake

At the start of a cron / seat take / new session that continues multi-agent work:

1. `brief_me` (waits, asks, commitments) — treat resolved waits as the board, not optional
   colour.
2. `browse` `action: "inbox"` / `"waits"` if the brief is thin.
3. Act on fired waits via their `continuation`; do not rebuild status from prose alone.

## What not to do

- Do not rebuild a task state machine in markdown when a typed message + wait would hold
  the same state (swarm dogfood lesson: waits unused under cron until the recipe).
- Do not broadcast the same finding to every agent as a substitute for one handoff.
- Do not invent `running:` notebook locks or pull-only `status.md` as the human channel —
  ask the **person** identity with `wait: true` when a decision is needed.
- Do not promise a harness auto-wake from a wait (product: notify the person / next
  `brief_me`, not hosted head start). Use the board for shared brief + typed ask; keep
  process start/retry with your runner.
- Do not open a console coordination wizard or mode picker.
- Do not use trap prompts or comparison one-pagers to force a “yes” in an evaluation —
  demonstrate real MCP tools only.
- Do not treat contested truths or Home pins as swarm coordination — wrong tools for a handoff.

## Done when

One of: a wait (or handoff/commitment) is on the board for every open cross-agent dependency;
or you stated clearly that this turn stays single-agent / human chat only; or the human
overrode the recipe. For recipe 0, also: Admin recovered from `brief_me`/docs, and Product’s
next brief saw the wait resolve.
