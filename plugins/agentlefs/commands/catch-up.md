---
description: Catch up on what you have been working on in agentleFS (afs), and pick the thread back up
argument-hint: [topic]
allowed-tools: mcp__plugin_agentlefs_agentlefs__brief_me, mcp__plugin_agentlefs_agentlefs__list_org_folders, mcp__plugin_agentlefs_agentlefs__search, mcp__plugin_agentlefs_agentlefs__search_org_knowledge, mcp__plugin_agentlefs_agentlefs__list_org_docs, mcp__plugin_agentlefs_agentlefs__read_org_doc
---

Work out where the user left off and hand it back to them in a few sentences they can act on.

Focus: `$1` (optional). If `$ARGUMENTS` names a topic, let it steer everything below — it is a far better signal than recency. If it is empty, report on their recent work generally.

## Step 1 - brief, once

Call `mcp__plugin_agentlefs_agentlefs__brief_me` with no arguments. It is keyed to this identity, not this session, so it picks up where the last session stopped.

One call. Read its structured fields:

| Field | What it tells you |
|---|---|
| `claims` | What this identity said it was working on and has not released — the most direct answer to "where was I" |
| `waiting` | Messages addressed to them that are still open — questions, requests, handoffs |
| `approvals` | Access requests waiting on their decision |
| `resolvedWaits` | Answers or changes they were waiting for that have arrived, or waits that timed out |
| `changed` | What other people and agents did near their work (nodes they own, claimed or wrote) since the last acknowledged brief |
| `contested` | Other identities' claims overlapping theirs, truths under debate on their documents, debates they are asked to decide (`toDecide`), and spans gone stale because a truth they cite was superseded |

| Outcome | Do this |
|---|---|
| Any of the above is non-empty | Continue to Step 2. |
| All empty | Nothing has moved near their work since the last acknowledged brief, or they have not worked in the store yet. Say so in one sentence and go to Step 2 anyway — `$1` may still be answerable from the store. |
| `not_an_identity` | This credential has no place in the identity tree. Say so; search still works. |
| Error / tools missing | Stop and diagnose with the `connection` skill. Do not paraphrase a 401 as "agentleFS is down". |

## Step 2 - search, aimed but not fenced

The locations in `claims` and `changed` tell you where this person's work *tends* to live. That is a strong hint and a terrible filter.

If their work is all in `product/` and `$1` is about a deployment runbook, scoping `mcp__plugin_agentlefs_agentlefs__search` to `product` guarantees you miss it — and you will never find out, because a search returning nothing looks exactly like a subject nobody wrote about.

So use it to **interpret** ("the pricing doc" means the one in their folder), to **rank**, and to **go first**. Run at least one search without a folder scope before concluding the store has nothing.

## Step 3 - open two or three documents, then stop

Call `mcp__plugin_agentlefs_agentlefs__read_org_doc` on the ones that match what they asked, not the ones that merely changed most recently. If nothing looks right, say what you found and ask — that is faster for them than watching you open six files that turn out to be wrong.

## Step 4 - report

Lead with where things stand, not with what you did. Three or four sentences, then stop.

Lead with anything in `waiting`, `approvals`, `resolvedWaits` or `contested`: those are somebody else asking for something, an answer they were waiting for, or about to collide with them. Then what they were last working on, anything that looks unfinished, and the obvious next step. Cite documents by path so they can open them. Do not answer or close a request on their behalf without asking.

**Absence is never evidence.** Documents they cannot currently read are filtered out of every field. Empty means "nothing I can reach", never "nothing exists".

## Do not

- Do not describe their role, seniority, or team from where they work. Read locations as places, not as a person.
- Do not pass a folder filter to search based only on the brief.
- Do not call `mcp__plugin_agentlefs_agentlefs__brief_me` repeatedly hunting for a better answer. The one further call worth making is the acknowledgement — `ack_through` set to `cursor.head` — and only once the user has picked the work back up: it moves their cursor, so the next session starts after what you summarized.
- Do not report a thin or empty result as though the organization has written nothing.
- Do not narrate your tool calls. They want to know where things stand.
