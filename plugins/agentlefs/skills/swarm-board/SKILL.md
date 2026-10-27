---
name: swarm-board
description: Soft recipes so multi-agent or swarm work coordinates on agentleFS (afs) waits, rooms, and typed messages — the board — instead of ad-hoc chat, prose task docs, or notebook locks. Use when spawning helpers, asking other agents, handing work off, waiting for a reply or a doc change, or opening a shared room across chains. Especially under cron or intermittent heads, where waits were historically unused. Soft recipe, not a console wizard. Complements collaborating (primitives) and projects (folder briefs).
---

# Swarm board (waits / rooms / typed messages)

Primitives already ship (`message_write`, `await` / `wait_for`, rooms). The gap this skill
closes is **habit**: multi-agent work that rebuilds coordination in chat, notebooks, or
prose task state machines instead of the durable board. Soft recipe only — no wizard, no
new console UI, no hosted harness wake (that path is out of scope).

Load this when you are coordinating **more than one agent** (or an agent and a person who
will answer later). The `collaborating` skill has the tool shapes; this skill says **which
recipe to run and when**.

## When to run

Run (or re-check) when **any** of these hold:

1. You are about to `identity_write` `spawn` a helper, or you already did and will ask it
   something / hand it work.
2. You will send a `question`, `request`, or `handoff` to another agent or person and care
   about the answer or completion across this session or the next cron wake.
3. Agents from **different chains** (different people) need a shared place without seeing
   each other's private folders — a room.
4. A PostToolUse hook named this skill after coordinating without a wait or room.

**Skip** when:

- Solo work on one document with a claim — `collaborating` claim/release is enough.
- Pure human chat with no other agent and no deferred answer.
- The human said to stay in GitHub issues / local chat only for this task.

## Caps

| Budget | Limit |
|---|---|
| Open waits you register per turn | **1–3** (prefer one clear `continuation` each) |
| Room creates | **0–1** per effort; invite only who must share |
| Broadcast findings to N agents | Prefer **one** handoff/request to the right identity, not N inbox copies |
| Prose "board" docs (status.md, notebook locks) | **Do not invent** when messages/waits cover the same fact |
| Hook retries | **Once** per session (`swarm-board` mark) |

## Soft recipes

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

### 3. Cross-chain shared space (room)

Same-chain helpers share grants via spawn; **different people's agents** need a room so
nothing private leaks.

1. `message_write` `action: "create_room"`, `name`, `invite` (ids or exact names in **this**
   org only).
2. Invitees `join`; talk with `to: ["room:<id>"]`; `move_in` only what should be shared.
3. Outside the org → folder `share_out` (`sharing` skill), not a room.

### 4. Watch a document or folder

1. `coordination_write` `subscribe` on `location` (or `room_id` / `truth` / `identity`).
2. `coordination_write` `wait_for` with `on_subscription`, `deadline`, `continuation`.
3. Re-register after each fire if they still want the next change.

### 5. Board check on every intermittent wake

At the start of a cron / seat take / new session that continues multi-agent work:

1. `brief_me` (waits, asks, commitments) — treat resolved waits as the board, not optional
   colour.
2. `browse` `action: "inbox"` / `"waits"` / `"rooms"` if the brief is thin.
3. Act on fired waits via their `continuation`; do not rebuild status from prose alone.

## What not to do

- Do not rebuild a task state machine in markdown when a typed message + wait would hold
  the same state (swarm dogfood lesson: waits/rooms unused under cron).
- Do not broadcast the same finding to every agent as a substitute for one handoff or a
  room thread.
- Do not invent `running:` notebook locks or pull-only `status.md` as the human channel —
  ask the **person** identity with `wait: true` when a decision is needed.
- Do not promise a harness auto-wake from a wait (product: notify the person / next
  `brief_me`, not hosted head start).
- Do not open a console coordination wizard or mode picker.

## Done when

One of: a wait or room (or handoff/commitment) is on the board for every open
cross-agent dependency; or you stated clearly that this turn stays single-agent / human
chat only; or the human overrode the recipe.
