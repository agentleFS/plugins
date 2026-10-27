---
name: entry-mode-playbooks
description: Soft recipes for unnamed harness entry modes (lost / ui / bug / feature) in agentleFS (afs) — assemble steps, caps, write-back checklist, and done-when. Loaded by proactive-assembly after soft mode inference; skippable and overrideable. Not a console wizard or entry-mode picker. Not for named continue-project or catch-up.
---

# Entry-mode playbooks (soft recipes)

Productized recipes for meet-them entry modes. **`proactive-assembly` loads this skill**
after it soft-infers (or the human overrides) a mode — then runs the matching section
below while building the ask-conditioned context packet.

These are **agent-facing soft recipes**, not user-facing wizards. Never show a mode menu.
If the human says "treat this as a bug," obey and switch sections. Skip the whole skill
when they already named a project (`continue projects/…`) or asked to be caught up.

## Soft modes (same ids as `infer_entry_mode`)

| Mode | Soft signals (examples) |
|---|---|
| `lost` | "don't know what to change", "what should I work on", "where do I start" |
| `ui` | "UI sucks", vague UX judgment without a concrete bug id |
| `bug` | fix / debug / crash / regression / "this bug" |
| `feature` | implement / add / build / ship / "this feature" |

Priority when several match: `lost` → `ui` (UI judgment, not bug language) → `bug` →
`feature`. Override anytime.

## Shared caps (every mode)

Same budget as `proactive-assembly` — do not excavate past it:

| Budget | Limit |
|---|---|
| `search` calls | **1** (optional second unscoped only if a scoped first was empty) |
| `limit` on search | **8** |
| `brief_me` | **0 or 1** |
| Documents `read` before talking | **0–2** |
| Follow links | **0** on the assembly pass |
| Public corpus | **off** |
| Packet sections | **≤3** projects/folders · **≤5** doc/decision citations · **≤3** open asks/waits · **1–2** write-back targets |

## Shared write-back rules

- Targets in the packet are **suggestions** until the session ends — then run the
  **`writeback-loop`** skill (guided checklist; soft recipe, not a wizard) so findings,
  plans, and comments land before stop. Human may say "skip write-back."
- Prefer the substrate humans already edit: **documents, comments, messages** — not a
  private side channel.
- Never invent a folder or project when a reachable match exists.
- After the human concurs on a project/doc, switch to ordinary `projects` / `documents`
  skills; do not re-run these playbooks on every later prompt for the same task.

---

## `lost` — lost in the project

**Intent:** Orient someone who wants to work but has no change in mind. Surface open
threads, briefs, and recent activity; propose a **first change**, not a redesign.

### Assemble steps

1. Confirm mode `lost` (or accept override). Extract product/repo/subsystem nouns only.
2. Call **`brief_me` once** (with `repo` if SessionStart named one). Prefer followed
   projects, waiting items, and recent movement over a cold keyword search.
3. **`search`** once (`limit: 8`) biased to orientation terms: open / brief / next / TODO /
   waiting / "what next", plus any product nouns from the ask.
4. Rank into the packet: projects with open work first; then docs that name next steps;
   then open asks/waits that touch those projects.
5. In the reply, propose **one** concrete first change (or "open this thread") with a
   citation — still a suggestion.

### Caps (mode bias)

- Prefer `brief_me` **on** for this mode (counts as the one allowed call).
- Search terms: orientation + project nouns; avoid inventing feature keywords they did
  not say.
- Packet: lean on **projects + open asks**; keep doc citations ≤5 and prefer briefs /
  AGENTS.md / recent notes.

### Write-back checklist (suggest only)

- [ ] Strongest project's discussion thread, **or** a short note under that folder once
      they pick a direction
- [ ] Not a new top-level doc or a new project
- [ ] Not a truth/decision until they lock a choice

### Done when

- Packet returned with mode `lost`, and either a cited "start here" project/thread **or**
  an explicit thin/empty result framed as a grant boundary — and the human can override
  the mode or dismiss.

---

## `ui` — vague product judgment

**Intent:** Turn "UI sucks / polish the interface" into a **scoped ask** by gathering
UI-related docs, bugs, and prior notes — not by starting a redesign.

### Assemble steps

1. Confirm mode `ui` (switch to `bug` if they name a crash/regression/failing test).
2. Extract UI surface nouns (settings, nav, editor, mobile, …) plus judgment words only
   as filters, not as search queries alone.
3. **`search`** once biased to UI / UX / frontend / design / polish / interface, plus
   surface nouns. Prefer specs, bug notes, prior UI decisions.
4. Optional **`brief_me`** once if a followed project is clearly UI-facing or the session
   named a frontend repo.
5. In the packet, add one line that **scopes the judgment** into a candidate ask
   ("polish X based on Y doc") — still a suggestion until they concur.

### Caps (mode bias)

- Bias hits toward frontend/UX artifacts; demote unrelated backend truths unless they
  cite the same surface.
- Doc citations ≤5; write-back targets ≤2 and must be existing UI docs/folders when any
  match.

### Write-back checklist (suggest only)

- [ ] Scoped ask or finding on the matched UI doc/folder (comment preferred)
- [ ] Avoid inventing a new "UI redesign" project unless none exists in reach
- [ ] If they later lock a product decision, suggest a truth — not during assembly

### Done when

- Packet returned with mode `ui`, including at least one cited UI-related hit **or** a
  clear empty/thin framing, plus a suggested scoped ask the human can accept, narrow, or
  override (including "treat as bug/feature").

---

## `bug` — concrete failure

**Intent:** Find related failures, truths, and prior fixes; suggest where to **file the
finding** — then stop assembling and let them debug.

### Assemble steps

1. Confirm mode `bug`. Extract symptom, subsystem, error text, and any id/URL they gave.
2. **`search`** once biased to fail / crash / regression / bug / fix / error + symptom
   nouns. Prefer bug notes, prior fixes, contested truths, postmortems.
3. Optional **`brief_me`** once for open asks/waits that mention the same failure.
4. Rank failures and prior fixes above generic feature specs.
5. Suggest **one** write-back home for a finding (doc or thread), not a fix plan dump.

### Caps (mode bias)

- Prefer failure-shaped hits; keep ≤5 citations.
- Do not open a debate or propose a truth during assembly unless they asked to record a
  fact.

### Write-back checklist (suggest only)

- [ ] Finding or comment on the matched bug/spec doc (or project discussion)
- [ ] Message (`finding` / `request`) only if a person/agent is clearly the right owner
- [ ] Truths only when the human wants a recorded fact after the fix path is clear

### Done when

- Packet returned with mode `bug`, cited related failure/prior-fix context (or thin
  empty), and a suggested finding home — human may override mode or skip write-back.

---

## `feature` — add / build / ship

**Intent:** Find prior implementations and decisions for the named capability; suggest
where to **write the plan**.

### Assemble steps

1. Confirm mode `feature` (default for other work verbs when not lost/ui/bug).
2. Extract capability nouns (feature name, area, user-facing outcome).
3. **`search`** once biased to the capability + prior / decision / spec / design /
   implement. Prefer specs, decisions, prior implementation notes.
4. Optional **`brief_me`** once for projects that already cover the capability.
5. Suggest a plan/design landing spot under the matched folder — not a new org-wide doc.

### Caps (mode bias)

- Prefer specs/decisions/implementations for the named capability; ≤5 citations.
- Write-back ≤2 targets inside matched feature folders when any exist.

### Write-back checklist (suggest only)

- [ ] Plan or design note in the matched feature folder (doc_create / edit after concur)
- [ ] Decision / truth only when they lock a choice
- [ ] Do not publish a registry lesson from the assembly pass

### Done when

- Packet returned with mode `feature`, cited prior art/decisions (or thin empty), and a
  suggested plan home — human may override mode ("this is a bug") or dismiss.

---

## What not to do

- Do not present a picker, wizard, or forced mode confirmation UI.
- Do not treat soft inference as authoritative when the human overrides.
- Do not auto-write, auto-claim, or auto-start a project from these recipes.
- Do not mix `scope: "public"` into the assembly pass.
- Do not re-run the playbook after a project is confirmed for the same task.
