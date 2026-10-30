---
name: proactive-assembly
description: When a coding or continue-work ask names no agentleFS (afs) project or folder ("implement this feature", "fix the auth bug", "UI sucks", "don't know what to change"), before coding infer a soft entry mode (lost / ui / bug / feature) and return one ranked, cited, permission-bound context packet — candidate projects/folders, docs/decisions, open asks/waits, suggested write-back targets. Suggestions only; capped; same reach as search/read. Skip when the user already named a project (continue-project). Not for catch-up, general Q&A, or when a project pointer is already present.
---

# Proactive assembly (ask-conditioned context packet)

Today's continue-project path works when the user **names** a project or folder. This skill
covers the gap: an open-ended or lightly named ask with **no pointer**. Before coding,
assemble a thin, permission-bound **context packet** conditioned on the ask — do not wait
for the human to invoke search, and do not show a mode picker.

Results are **suggestions, not facts**. Cite paths. Let the human pick or dismiss. Never
treat a thin or empty result as "the org has nothing"; absence may be a grant boundary
(see `authorization-model`). Same egress as `search` / `read` / `brief_me` — never invent
hits or surface what you cannot reach.

## When to run (always-on)

Run this once at the start of a turn when **all** of these hold:

1. The user stated a work ask (implement / fix / build / improve UI / lost in project / …).
2. They did **not** name an agentleFS project, folder path, or `continue …` pointer.
3. You have not already assembled for this task in this session.

**Skip** (use the named path instead) when any of these hold:

- The prompt names a project or folder (`continue projects/…`, `projects/<name>`, "in the X
  project", an afs path they clearly mean as the work home).
- They asked to be caught up (`catch-up` skill / `/agentlefs:catch-up`) — that is a different
  brief-first path.
- The task is general knowledge, pure chat, or already mid-flight after a confirmed project.

A SessionStart or UserPromptSubmit hook may already have nudged you (and may name a soft
mode); treat that as the signal to run the steps below, not as the assembly itself.

## Soft entry mode (no wizard)

Infer **one** mode from the prompt. If the hook already named a mode, start from that and
override when the ask clearly disagrees. If the human says "treat this as a bug," obey.
Never ask them to pick from a menu.

| Mode | Soft signals (examples) |
|---|---|
| `lost` | "don't know what to change", "what should I work on", "where do I start", lost in project |
| `ui` | "UI sucks", "polish the interface", vague UX judgment without a concrete bug id |
| `bug` | fix / debug / crash / regression / "this bug" |
| `feature` | implement / add / build / ship / "this feature" (default for other work verbs) |

Priority when several match: `lost` → `ui` (when UI judgment and not bug language) → `bug` →
`feature`.

## Caps (latency and junk)

| Budget | Limit |
|---|---|
| `search` calls | **1** (optionally a second unscoped only if the first was folder-scoped and empty) |
| `limit` on search | **8** |
| `brief_me` | **0 or 1** — once for identity / waiting / project orientation; prefer `only: "projects"` when the session already named a repo and you only need movement |
| Overlap peeks (`browse` `claims` + location) | **0–3** matched hits only |
| Documents `read` before talking | **0–2** — titles/excerpts from search are usually enough |
| Follow links (`follow`) | **0** on the assembly pass |
| Public corpus | **off** — do not mix `scope: "public"` into this pass |
| Packet sections | **≤3** projects/folders · **≤5** doc/decision citations · **≤3** open asks/waits · **1–2** write-back targets |

Stop after one packet. Do not excavate.

## Context packet (return this once, before coding)

Present **one** short block labeled clearly, for example:

> **Ask-conditioned context packet** (suggestions, not facts · mode: `bug`):

Then these sections, in order — omit a section only when truly empty after the capped pass:

1. **Projects / folders** — path + one-line why it might match (citation or brief_me project).
2. **Docs / decisions / prior work** — path or citation + kind (spec / decision / bug note /
   lesson / truth). Rank by relevance to the ask, not by recency alone.
3. **Open asks / waits** — from `brief_me` (and inbox/waits only if brief already pointed
   there): only items that touch the topic; cite message/thread ids the tools gave you.
4. **Suggested write-back** — 1–2 places a finding, plan, or comment should land if work
   continues (folder or doc path). Suggestion only — do not write yet.
5. **Overlap** (optional, ≤1 line) — if a matched hit has another identity's open claim
   (see Steps), append one labeled suggestion line. Never a block or auto-merge.

Ask which to open, or proceed with the strongest match only after the human concurs — or
if they already said "just pick one," name the pick and cite it. After a project is
confirmed, switch to the ordinary `projects` / `documents` path. Do not keep re-assembling
on every later prompt for the same task.

## Steps

1. **Infer mode** (`lost` / `ui` / `bug` / `feature`) from the ask (and the hook hint).
2. **Load `entry-mode-playbooks`** for that mode (skippable / overrideable — if the human
   says "treat this as a bug," switch sections). Follow that section's assemble steps,
   caps bias, write-back checklist, and done-when. Do not invent a parallel recipe here.
3. **Extract key terms** (feature name, bug symptom, UI surface, subsystem). Drop filler.
   Bias terms with the loaded playbook.
4. **`search`** with those terms, `limit: 8`, no folder scope. Prefer `how: "auto"`. Every hit
   you can see is already filtered by `effective()` reach.
5. Optionally **`brief_me`** once (with `repo` if SessionStart named one) for followed
   projects and waiting/asks that may touch the topic — required sooner when the playbook
   says so (`lost`).
6. **Overlap peek (F21, claim-only first slice):** for up to **3** search hits that name a
   folder or document (`location` or `node`), call `browse` with `action: "claims"` and that
   `location`/`node`. If another identity holds an **open claim** there, append **one**
   suggestion line to the packet (who, where, intent, until). Same egress as search/read —
   a hit you cannot read never returns claims. **Suggestion only:** never auto-merge, never
   refuse the user's task, never treat silence as "nobody is working." Skip the peek when
   search returned nothing. Title similarity / similar findings / ML ranking are deferred.
7. **Rank and cap** into the packet sections above. Prefer fewer cited hits over a long dump.
8. Present the packet (including any overlap line); get concurrence before heavy reads or writes.

## Mode recipes live in `entry-mode-playbooks`

Do **not** expand mode recipes in this skill. Soft mode ids stay here for inference and
packet labeling; assemble bias, write-back checklist, and done-when live in
`entry-mode-playbooks` (`lost` / `ui` / `bug` / `feature`). That skill is skippable and
overrideable — never a picker.

## What not to do

- Do not invent projects or claim certainty from ranking alone.
- Do not widen beyond what search / brief_me returned; do not dump full document bodies.
- Do not run this on every trivial prompt — only unnamed / lightly named work asks.
- Do not show an entry-mode picker or wizard; soft inference + override only.
- Do not treat an overlap suggestion as a hard stop, merge, or write refusal — claims already
  refuse colliding writes at the door; this line is notice only.
- Do not auto-write the packet into afs during assembly; targets stay suggestions until
  work produces something durable — then run **`writeback-loop`** before stop (guided
  checklist; human may skip). A Stop hook may remind once.
- Do not store new memories until work is underway and the user wants them kept
  (`writeback-loop` / `documents` (save this conversation) / `memory` / ordinary `doc_create`
  into the chosen folder).
