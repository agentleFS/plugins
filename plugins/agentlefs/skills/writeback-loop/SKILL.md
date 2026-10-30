---
name: writeback-loop
description: Before stopping an unnamed or lightly named agentleFS (afs) harness session that assembled context or produced durable findings, run a guided write-back checklist — commit docs/comments/messages/truths to the suggested targets (or an agreed folder) using existing MCP write tools. Soft recipe, not a wizard; human can skip. Product form of VF-auto-writeback. Not for sessions that already wrote back, pure chat with nothing durable, or when the human said not to record.
---

# Write-back loop (guided, soft recipe)

Meet-them lasting value: **update the system** so the next person or head picks up from
the record, not from a dead chat. Tools already exist (`doc_create` / `doc_update`,
`message_write`, truths via `coordination_write`, `documents` (save this conversation)). This
skill is the **habit** — a guided checklist before stop, not a new write API and not a
console wizard.

Assembly and `entry-mode-playbooks` **suggest** write-back targets. This skill makes
those suggestions into commits (or an explicit skip) before the session ends.

## When to run

Run once near the end of a turn / before you would stop when **any** of these hold:

1. You returned an ask-conditioned **context packet** (or the Stop hook named this skill).
2. The session produced something durable (a finding, plan, decision, scoped ask, fix
   note) that still lives only in chat.
3. Playbooks listed write-back checklist items you have not acted on.

**Skip** (do not nag) when:

- The human said not to record / "skip write-back" / "nothing durable."
- You already wrote the durable outcome this turn (`doc_create` / `doc_update`, a
  finding/comment/`request` message, a truth, or `documents` (save this conversation)).
- The turn was pure Q&A / orientation with **no** finding, plan, or decision to keep.
- You are mid-flight and the human clearly wants another coding step first — finish that,
  then run this before the real stop.

A Stop / SubagentStop hook may send you back once with this checklist. Treat that as the
signal to run the steps below (or say plainly you are skipping and why), not as a loop.

## HITL (always)

- **Suggestion-first, then write.** Prefer the packet's **Suggested write-back** paths.
  If none fit, ask once for a folder/doc, or use `documents` (save this conversation) when the
  durable thing *is* the conversation.
- **Never silent dump.** Do not paste the whole chat. Do not invent a new top-level
  folder or project when a reachable match exists.
- **Human override wins.** "Don't save" / "skip write-back" ends the loop immediately.
- **No picker UI.** Soft mode from assembly/playbooks; switch if they say "treat as bug."

## Caps

| Budget | Limit |
|---|---|
| Write targets this stop | **1–2** (same as the packet) |
| New documents | Prefer **edit / comment / finding** on an existing home; create only when the playbook says so and the human concurs |
| Transcript / dump | **Never** — compact finding/plan/decision only |
| Truths / knowledge | Only when they locked a fact or want a lesson; not by default |
| Hook retries | **Once** — second stop is the answer (wrote, skipped, or unfinished with reason) |

## Soft mode → what to write

Reuse `entry-mode-playbooks` write-back checklists. Short form:

| Mode | Prefer writing | Avoid |
|---|---|---|
| `lost` | Short note or discussion comment under the chosen project once they picked a direction | New project; truth before a choice |
| `ui` | Scoped ask or finding (comment) on the matched UI doc/folder | Inventing a "UI redesign" project |
| `bug` | Finding / comment on the matched bug/spec (or `message_write` `kind: "finding"`) | Truth dump before the fix path is clear |
| `feature` | Plan/design note in the matched feature folder | Registry publish; org-wide misc doc |

If mode is unclear, default to: one comment or finding on the strongest packet target, or
ask which target.

## Steps

1. **Inventory.** From this session: packet write-back targets (if any), mode, and what is
   durable (finding, plan, decision, open thread). If nothing durable → say so and stop
   (that *is* completing the loop).
2. **Pick home.** First of: human-named path → packet suggested target they concurred with
   → last place you already wrote this session → ask once.
3. **Choose substrate** (documents / comments / messages — meet-them substrate):
   - Anchored discussion → `message_write` `action: "comment"` (or reply on an open thread).
   - Standalone finding / request to a person or agent → `message_write` `action: "send"`
     with `kind: "finding"` or `"request"`.
   - Spec/plan/note body → `doc_update` edit, or `doc_create` into the agreed folder.
   - Locked decision → `shared-truths-and-lessons` / `coordination_write` propose (not by
     default on every stop).
   - Whole-session residue with no better home → `documents` (save this conversation) skill.
4. **Write** with the ordinary tools. Match neighbors' frontmatter when creating a doc.
   Cite paths in your reply.
5. **Report.** Path or message id + cite link. Name anything you left out on purpose.
   If a write was refused, say so — do not claim it landed.
6. **Done when** one of: durable write committed; human skipped; or you stated clearly
   there was nothing durable to write.

## What not to do

- Do not auto-write secrets, raw tool dumps, or full transcripts.
- Do not open an entry-mode menu or a write-back wizard UI.
- Do not re-run `proactive-assembly` just to write back — use the targets you already have.
- Do not treat a refused grant as "afs is down"; see `authorization-model` / `connection`.
- Do not block the human from stopping after one guided pass — second stop always proceeds.
