---
name: catch-up
description: Catch the user up on their work in agentleFS (afs) — what is waiting on them, what changed near their work, and where they left off. Use when they say "catch me up", "what's waiting on me", "what changed", "what was I working on", "where did I leave off" or "get me up to speed", or when they refer to their own ongoing work in afs ("the pricing thing", "my spec") as though you should already know which document they mean. Not for general questions, coding tasks in the open repository, or a session that has not touched afs.
---

# Catch up on what the user has been working on

A fresh session knows nothing about where this person lives in the store. It can
search, but a store holding several functions' worth of documents will answer
"pricing" from sales, product, finance and engineering at once, and the session
has no way to tell which one this user means.

`brief_me` closes that gap in one call. It is keyed to the identity rather than the
session, so a new session reads the same brief the last one would have, from the
same cursor. It does not answer questions and it does not summarize documents — it
tells you **where to point the tools you already have**, and what is waiting on the
person.

## The shape of a good catch-up

```
brief_me                   ← once
   ↓ read claims, waiting, approvals, changed, contested
search                     ← aimed, but not fenced in
   ↓
read_org_doc               ← two or three, then stop and talk
```

Four to six calls, then a reply. If you are on your seventh call you have stopped
orienting and started excavating.

## Step 1 — brief, once

Call `brief_me` with no arguments. Its structured output has these parts:

| Field | What it is |
|---|---|
| `me` | Who this identity is, where it sits in the organization's tree of people and agents, its capability card |
| `claims` | What it said it was working on and has not released — the most direct answer to "where was I" |
| `waiting` | Messages addressed to it and still open — questions, requests, handoffs |
| `approvals` | Access requests routed to it for a decision |
| `invitations` | Rooms it has been invited to |
| `asked` / `answered` | What it asked of others that is still open, and answers that came back |
| `resolvedWaits` | Waits that fired, timed out or lost their counterparty, each with the note left for whoever picks it up |
| `changed` | What others did near its work — nodes it owns, holds claims on, or wrote — since the last acknowledged brief |
| `contested` | Other identities' claims overlapping its own, truths under debate on its documents, debates it is asked to decide (`toDecide`), and spans gone stale because a truth they cite was superseded |
| `cursor` | Where the brief started (`position`) and where the log is now (`head`) |

One call is the whole budget for this step. If it did not tell you what you hoped,
calling it again will not change that, and the user's own words are a better source
anyway.

## Step 2 — read how much there is before you trust it

A brief with open claims and a dozen changes across several documents is a genuine
picture of where this person is working. A brief with nothing in `claims` and two
items in `changed` is a weak signal — let it break ties and nothing more. All empty
means nothing moved near their work since the last acknowledged brief, or they have
not worked in the store yet; say so in one sentence and search normally rather
than guessing at their work.

Adoption of agentleFS varies enormously — some people put everything in it, some
put in fragments. A confident-sounding account of someone's work built on two
events is worse than admitting you cannot tell, because the user has no way to see
that it was invented.

## Step 3 — let it aim your search, never fence it

This is the step that most often goes wrong, so it is worth being precise about.

The locations in the brief tell you where this person's work *tends* to live. That
is a strong hint and a terrible filter. If their work is all in `product/` and they
ask about a deployment runbook, passing `scope: "product"` to
`search` guarantees you miss it — and you will never find out,
because a search that returns nothing looks exactly like a subject nobody wrote
about.

So:

- **Use it to interpret.** "The pricing doc" means the one in *their* folder.
- **Use it to rank.** A hit in a folder they work in is likelier to be the one they
  meant than an identically-worded hit somewhere they have never been.
- **Use it to go first.** Search their active area before the rest of the store.
- **Do not use it to exclude.** Run at least one search unscoped by folder before
  concluding the store has nothing.

## Step 4 — open two or three documents, then stop

Two or three well-chosen documents is almost always enough to answer or to ask a
good question, and every extra one costs context the user would rather spend on the
actual work. Pick by what the user asked, not by what changed most recently.

## What is waiting on them

Lead with `waiting`, `approvals`, `contested` and `resolvedWaits` when they are
non-empty: they are the parts of the brief that are somebody else asking for
something, an answer the user was waiting for, or about to collide with this
person's work. Deciding an access request is `share` with `action: "approve"` or
`"decline"` and its `request_id`; the `sharing` skill has the rest. Each waiting item is a message and carries its id. `message`
with `action: "thread"` and its `thread_id` reads the conversation; `action: "send"`
with `reply_to` answers it, and `action: "decline"` with `message_id` and a `reason`
says no. Do not
answer or decline one on the user's behalf without asking — it is addressed to
them, not to you.

What the user asked of others and is still open is the brief's `asked`, and
answers that came back since the last acknowledged session are `answered`. Only
the sender closes a message (`action: "close"`), so close one of the user's own
asks once it is settled.

## Acknowledging

When the work is picked up and `changed` has been taken in, call `brief_me` again
with `ack_through` set to `cursor.head`, so the next session starts after it. Not
before: a cursor moved past something nobody read means the next session skips it,
and re-reading is the cheaper failure.

## What the output is not

The brief reports what happened near someone's work. It never says what they
**are**, and neither should you.

Working in `engineering/` does not make someone an engineer. They might be the
founder, a designer who writes specs, a support lead documenting bugs, or someone
covering for a colleague on leave. Read locations as *places*, not as a *person*.
When the user says something that cuts against them, the user is right.

## Reading what is missing

**Recent often means finished.** The thing that changed most recently is frequently
the thing that just wrapped up. Their message says where they are going.

**Absence is never evidence.** Nothing an identity cannot read appears in the brief,
not even as a count. An empty or thin brief means "nothing I can reach", never
"nothing exists". Say it that way.

## Reporting back

Lead with the answer to what they asked. Weave the context in rather than
narrating your process. Cite documents by path so they can open them. If you leaned
on the brief to pick a folder, say so in passing ("looks like this lives in your
`product/` area") so a wrong guess is visible and correctable rather than silent.

## Do not

- Do not call `brief_me` repeatedly hunting for a better answer. One call, then
  move on (plus the one acknowledgement above).
- Do not pass a folder filter to search based only on the brief.
- Do not describe the user's role, seniority, or team from where they work.
- Do not report a thin or empty result as though the organization has written
  nothing — see the `authorization-model` skill on why absence is not evidence.
