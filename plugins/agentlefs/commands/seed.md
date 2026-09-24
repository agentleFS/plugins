---
description: Seed agentleFS (afs) with what you already know about this project, so the store isn't empty
argument-hint: [folder]
allowed-tools: mcp__plugin_agentlefs_agentlefs__list_org_folders, mcp__plugin_agentlefs_agentlefs__list_org_docs, mcp__plugin_agentlefs_agentlefs__read_org_doc, mcp__plugin_agentlefs_agentlefs__write_org_doc, mcp__plugin_agentlefs_agentlefs__create_org_folder
---

Fill a reachable-but-empty agentleFS with durable knowledge about the current project. A new store has working semantic search and nothing to search — this closes that gap in one pass.

Target folder: `$1` (optional). If `$ARGUMENTS` is empty, pick the target in Step 1.

## Step 1 - find a folder you can write to

Call `mcp__plugin_agentlefs_agentlefs__list_org_folders` with no arguments.

| Outcome | Do this |
|---|---|
| One or more folders | If `$1` names one, use it. Otherwise show the list and ask which to write into. |
| "(nothing stored yet …)" | The user is an approver of an empty Organization. Ask what to call a first folder, create it with `mcp__plugin_agentlefs_agentlefs__create_org_folder` (`folder_path` is a list of folder names, e.g. `["acme-platform"]`), and write into it. (A `write_org_doc` into a folder that does not exist now creates it as well, so a mistyped name starts a workspace rather than being refused — ask first, then write.) |
| "(no folders you can reach …)" | This credential holds no grants, so there is nowhere it may write. Stop, say so plainly, and say what fixes it: a folder approver shares one with them. Do not report the Organization as having no content, and do not send them to `/agentlefs:connect`, which will say the same. |

Then call `mcp__plugin_agentlefs_agentlefs__list_org_docs` with `location` set to the chosen folder. It tells you what is already there and the `type` of each document. It does not show tags, so if there are documents, open one or two representative ones with `mcp__plugin_agentlefs_agentlefs__read_org_doc`: that returns each file's own frontmatter, which is the tag convention to copy. (The labels `list_org_folders` reports for a folder include inherited ones, which already apply to anything written there and should not be copied into frontmatter.)

## Step 2 - decide what is worth persisting

Take stock of what you have learned in this session and from the repository in front of you. Good candidates, roughly in descending value:

- Architecture decisions and the reasoning behind them, especially where the reasoning is not obvious from the code.
- Gotchas and non-obvious constraints — the things that cost someone an afternoon.
- Conventions a new teammate would otherwise violate.
- Operational knowledge: how to run it, how to deploy it, what breaks.

**Do not persist** what the code already says plainly, anything already in the store (you listed it in Step 1), secrets or credentials of any kind, or transient state like current branch names and in-flight work.

If you have learned nothing durable yet, write one document describing what this repository is and how to run it. The user ran this command to get something into the store, and one honest orientation doc is more useful to the next session than none.

## Step 3 - write each as its own document

One idea per document. A single dumped file is a file nobody finds.

For each, call `mcp__plugin_agentlefs_agentlefs__write_org_doc` with:

- `folder_path`: the chosen folder as a list of names, outermost first — `["engineering"]`, or `["engineering", "runbooks"]` for a directory inside it;
- `name`: a descriptive file name ending in `.md`, with no `/` in it (folders go in `folder_path`);
- `content`: YAML frontmatter that matches the neighbouring files you read in Step 1 — `type` (one of `meeting-notes`, `playbook`, `spec`, `brand-asset`, `web-clip`, `contract`, `misc`; anything else is silently saved as `misc`), `title`, `summary`, `tags` — then the body.

Tags drive search; they are not access controls. A mis-tagged file is a file nobody retrieves. The confirmation says whether it created or overwrote the document and names any directory it had to create; either one being a surprise means the path was wrong.

The write commits if your grant allows it and is refused if it does not. There is no staging step to choose and no review queue between you and the store, so a successful write is live and agent-visible immediately.

## Step 4 - report

List what you wrote, with folder and path. Name anything you deliberately skipped and why, including anything a refusal stopped you from writing.

Close by telling them the store is now searchable by meaning, and that `/agentlefs:permissions` shows what this credential reaches.

## Do not

- Do not invent knowledge to fill the store. Everything written must be something you actually established from this session or this repository.
- Do not write secrets, tokens, or credentials, even if you found them in the repo.
- Do not write one giant document instead of several small ones.
- Do not report a refused write as though it had landed.
