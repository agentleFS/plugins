---
description: Summarize what this credential can actually reach in agentleFS (afs)
argument-hint: [folder]
allowed-tools: mcp__plugin_agentlefs_agentlefs__list_org_folders
---

Report what **this credential** effectively reaches in agentleFS. Nothing more. This is a self-audit of the current principal's reach, not a report on anyone else's access.

Argument: `$ARGUMENTS` (optional folder to focus on).

## Step 1 - the reachable set

Call `mcp__plugin_agentlefs_agentlefs__list_org_folders` with no arguments. What comes back is the complete set of folders this principal reaches. A folder absent from that list is either not granted to this principal or does not exist, and the two are indistinguishable by design.

An empty list of your OWN folders is three different facts, and the listing says which:

| What it prints | What is true | Do this |
|---|---|---|
| "(nothing stored yet …)" | You own the Organization and it holds nothing | Say so — it is correct here, and only here. Send them to `/agentlefs:connect`. |
| "(no folders you can reach …)" | This credential holds no grants | Say the credential reaches nothing. Do **not** report "the organization has no content": denied is byte-identical to not-found. Send them to `/agentlefs:connect`. |
| "(no folders of your own yet)" followed by "── shared with you ──" | Everything it reaches was shared from another workspace | Do not stop, and do not say it reaches no folders — it reaches every folder in that block. Report those in Step 2, each with the `[share <id>]` printed beside it. |

## Step 2 - per-folder shape

If `$ARGUMENTS` names a folder, call `mcp__plugin_agentlefs_agentlefs__list_org_folders` with that folder and report only it. If Step 1 listed that folder under "── shared with you ──", pass the `share` id printed beside it in the same call.

If `$ARGUMENTS` is empty, orient across everything: call `mcp__plugin_agentlefs_agentlefs__list_org_folders` once per reachable folder to collect each folder's shape — the user's own by location, each shared one by location **and** its `share` id.

**The `share` id is what decides which workspace is answered**, so a shared folder asked about without it is looked for in this user's own workspace, where the path names nothing: the reply is the zeroed shape an absent folder gets (0 readable, 0 gated), which would tell the user they can read nothing in a folder they can read. Cap this at roughly the first 10 folders when there are many, and say plainly that you capped it and which folders you skipped.

Each per-folder call returns: how many files you can read, how many are `denied` (gated from you), a breakdown by type, and the labels present.

## Step 3 - report

Lead with a table, not prose:

| Folder | Readable | Gated | Types | Labels |
|---|---|---|---|---|

Put the user's own folders first, then the shared ones with their counts, marked as shared and with the workspace they came from — a folder shared with you is part of what this credential reaches, and the point of the report is what it reaches.

Then add, in a few lines:

- Total readable files across the folders you checked, and total gated.
- Any folder where the gated count dominates the readable count. That is the most useful signal in the whole report: it means substantial content sits next to what you can see, and you would never encounter it through search.
- Any folder that is fully readable with zero gated files.

## What you must state

Include this, in your own words, every time:

> Denied is byte-identical to not-found. A gated file is invisible, not marked. Where a `denied` count appears it tells you how many files are gated, never which ones or what they are about. Where a listing looks thin, "gated from you" and "does not exist" cannot be distinguished from here.

Also state that labels carry zero authority. They organize content and nothing else. An unlabeled file is not public, and a sensitively-labeled file is not thereby restricted. Access comes only from explicit grants.

## What you must NOT do

- **This command is about THIS credential's reach.** For "who else can see this", route to `/agentlefs:who-can-see`, which calls `who_can_read`. Never guess at anyone else's access.
- **Do not call a console API endpoint.** The console API accepts a Clerk browser session JWT only; this credential would 401.
- **Do not infer a grant from a label, a filename, or a folder name.**
- **Do not describe a thin result as evidence that content does not exist.**
- Do not present the reachable set as the organization's full inventory. It is this principal's view of it.

## If a call errors

The read path is fail-closed on purpose. A truncated allow-set throws rather than quietly returning a subset, so an error is the system refusing to under-report. Surface the error verbatim and do not substitute a partial summary for a complete one.

For the model behind all of this, the `authorization-model` skill has the full picture.
