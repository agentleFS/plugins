---
description: Seed agentleFS (afs) with what you already know about this project, so the store isn't empty
argument-hint: [folder]
allowed-tools: mcp__plugin_agentlefs_agentlefs__list_org_folders, mcp__plugin_agentlefs_agentlefs__list_org_docs, mcp__plugin_agentlefs_agentlefs__write_org_doc, mcp__plugin_agentlefs_agentlefs__create_org_folder
---

Fill a reachable-but-empty agentleFS with durable knowledge about the current project. A new store has working semantic search and nothing to search — this closes that gap in one pass.

Target folder: `$1` (optional). If `$ARGUMENTS` is empty, pick the target in Step 1.

## Step 1 - find a folder you can write to

Call `mcp__plugin_agentlefs_agentlefs__list_org_folders` with no arguments.

| Outcome | Do this |
|---|---|
| One or more folders | If `$1` names one, use it. Otherwise show the list and ask which to write into. |
| "(nothing stored yet …)" | The user owns an empty Organization. Ask what to call a first folder, create it with `mcp__plugin_agentlefs_agentlefs__create_org_folder`, and write into it. |
| "(no folders of your own yet)" followed by shared folders | Everything this credential reaches was shared with it from another workspace. Show the shared folders and ask which to write into. Skip any marked `(read-only)`. **Also offer to create a folder of their own** with `mcp__plugin_agentlefs_agentlefs__create_org_folder`: this message does not rule out that they own an empty Organization (the listing prints it whenever any share is present), and knowledge about their own project usually belongs in their own workspace rather than someone else's. That call can come back `⚠ refused: you cannot create folders in this organization` — creating one is an owner's action, and a member of a company Organization is not refused in error and cannot retry their way past it. Say that plainly, keep going with the shared folder they picked, and point them at an owner (or their own personal Organization) for a folder of their own. Note the chosen folder's `[share <id>]` — every later call on it must pass that id as `share`, or it resolves in this user's own workspace instead and finds nothing. |
| "(no folders you can reach …)" | This credential holds no grants, so there is nowhere it may write. Stop, say so plainly, and say what fixes it: a folder owner shares one with them. Do not report the Organization as having no content, and do not send them to `/agentlefs:connect`, which will say the same. |

Then call `mcp__plugin_agentlefs_agentlefs__list_org_docs` on the chosen folder (with `share` if it came from the shared block). Two reasons: it tells you whether the store is actually empty, and it shows you the `type` and label conventions already in use.

## Step 2 - decide what is worth persisting

Take stock of what you have learned in this session and from the repository in front of you. Good candidates, roughly in descending value:

- Architecture decisions and the reasoning behind them, especially where the reasoning is not obvious from the code.
- Gotchas and non-obvious constraints — the things that cost someone an afternoon.
- Conventions a new teammate would otherwise violate.
- Operational knowledge: how to run it, how to deploy it, what breaks.

**Do not persist** what the code already says plainly, anything already in the store (you listed it in Step 1), secrets or credentials of any kind, or transient state like current branch names and in-flight work.

**If you have genuinely learned nothing durable yet, write exactly one document** describing what this repository is and how to run it. An empty store is the failure mode this command exists to fix; one honest orientation doc beats zero documents.

## Step 3 - write each as its own document

One idea per document. A single dumped file is a file nobody finds.

For each, call `mcp__plugin_agentlefs_agentlefs__write_org_doc` with the chosen folder (and its `share` id, if it is a shared one), a descriptive path, and frontmatter that **matches the neighboring files you listed in Step 1** — `type` and `tags` especially. Tags drive search; they are not access controls. A mis-tagged file is a file nobody retrieves.

The write commits if your grant allows it and is refused if it does not. There is no staging step to choose and no review queue between you and the store, so a successful write is live and agent-visible immediately.

## Step 4 - report

List what you wrote, with folder and path. Name anything you deliberately skipped and why, including anything a refusal stopped you from writing.

Close by telling them the store is now searchable by meaning, and that `/agentlefs:permissions` shows what this credential reaches.

## Do not

- Do not invent knowledge to fill the store. Everything written must be something you actually established from this session or this repository.
- Do not write secrets, tokens, or credentials, even if you found them in the repo.
- Do not write one giant document instead of several small ones.
- Do not report a refused write as though it had landed.
