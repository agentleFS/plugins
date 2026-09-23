---
description: Share an agentleFS (afs) folder or document with members of your Organization by email — shows exactly who gets what, and shares only after you say yes
argument-hint: [folder-or-path]
allowed-tools: mcp__plugin_agentlefs_agentlefs__list_org_folders, mcp__plugin_agentlefs_agentlefs__list_org_docs, mcp__plugin_agentlefs_agentlefs__who_can_read
---

Help the user share `$1` with someone in their Organization. Your job is to get the decision right, show its blast radius, and share **only after they say yes** to the exact preview.

Sharing reaches **members of this Organization only**. There is no way to share with someone outside it, by email or by link: an address that does not belong to a member is refused and nothing is shared. If the user wants someone outside to have access, that person has to be invited to the Organization first, by a person who manages it, in the console.

The share tool is deliberately left out of this command's pre-approved tools, so Claude Code also asks the user before each share call. That prompt is a second guard, not a substitute for asking them yourself.

Target: `$1` (a `location` — a full path from the workspace root, naming either a folder like `product` or a single document like `product/runbooks/deploy.md`). If `$ARGUMENTS` is empty, call `mcp__plugin_agentlefs_agentlefs__list_org_folders` with no arguments, show the reachable folders, and ask which one they mean.

## Step 1 - orient on what the recipient would get

Do this first. Sharing decisions go wrong because the sharer does not know how much is under the thing they are sharing.

- For a folder: call `mcp__plugin_agentlefs_agentlefs__list_org_folders` with that folder. Report how many files are there, the type breakdown, and the labels.
- For a single document: call `mcp__plugin_agentlefs_agentlefs__list_org_docs` with the document's `location` to confirm it exists and is the intended file.

Then state the blast radius explicitly: **grants cascade down the folder tree.** A grant on a folder reaches every descendant of that folder, including subdirectories and files added later. A grant scoped to one document reaches only that document.

Say the number out loud. "Sharing `engineering/` at view gives them all 240 files under it, including anything added tomorrow" is the sentence that prevents the mistake.

One caveat to state honestly: the counts you can see are **your** counts. If the folder holds files gated from you, the total is larger than what you reported. Say so rather than presenting your view as the complete inventory.

## Step 2 - choose the role

Three roles are offered. The console labels them Reader / Editor / Approver.

| Console label | Role | Grants | Use when |
|---|---|---|---|
| Reader | `reader` | read and search the content | the default; the recipient needs to know, not change |
| Editor | `writer` | read plus write and edit documents | the recipient maintains the content |
| Approver | `approver` | can share and manage access at and below the scope, and edit | the recipient decides who else gets in |

Guidance to give:

- Default to Reader. Escalate only on a stated need.
- **One ladder: `reader` < `writer` < `approver`.** Each rung contains the one below it, so an approver reads and writes everything at or below where the grant sits, and additionally grants, revokes, deletes and erases there. Treat Approver as "decides who else gets in, and can change it".
- `approver` was called `owner` until September 2026; it is the same authority under a new name. "Owner" now means only the single owner every document and folder has, which is not a role you can share.
- The ladder is stated once, in `openfga/model.fga`, and there is no app-layer fold — asking the engine for `writer` already returns allow for an approver, so the console and MCP cannot give different answers. This guidance used to say `owner ⇏ writer` and that the authority layer folded it; that was the pre-#219 model.
- There are three roles and no others. `proposer` and `member` are retired, and neither was ever granted to anyone.

Pick the narrowest scope that does the job. A document-scoped grant is almost always safer than a folder-scoped one, and re-sharing a second document later is cheap.

## Step 3 - see who already reaches it

Call `mcp__plugin_agentlefs_agentlefs__who_can_read` on the target. If the recipient already reaches it (directly, inherited, or through a group), say so: sharing again changes nothing, or changes only the role.

## Step 4 - preview, ask, then share

**`share_org_folder`, TWO calls.** Pass `location`, `emails` and `role` (`reader` / `writer` / `approver`; add `scope_type: "document"` for one file). The first call **previews and shares nothing**; only a second call carrying its `confirm_token` shares. Each address that belongs to a member of this Organization gets an ordinary grant; any other address is refused with "not a member of this organization", and nothing is shared with it. It sends no email.

1. Make the preview call now, without asking first. It shares nothing, and its reply is the preview you are about to show — asking before it means asking the user to approve something they have not seen.
2. Show the user the preview in plain words: who, what role, how many files it reaches (from Step 1), and that it cascades.
3. **Ask. Wait for an explicit yes to THAT preview.** "Share it" before the preview is not a yes to the preview.
4. On yes, call again with the `confirm_token`. On anything else, stop — nothing was shared.
5. Report what the tool returned, per address — including any address it refused as not a member — and confirm with `mcp__plugin_agentlefs_agentlefs__who_can_read`.

A token expires after ten minutes, and it is refused if the folder, the role or the address list changed since the preview; either way, preview again and ask again.

**If a share tool refuses with "you cannot change who reaches content"**, nothing was shared, and the console will refuse for the same reason. Handing out access is authority over the whole Organization, not over the folder, so being an approver of the folder does not help in either place. Say that plainly, and name the move: ask an approver of the Organization to share it, or to make you an approver of the Organization.

**Taking a share back.** Grants can be inherited from a parent folder, so change them in the console, where you can see where each grant actually lives.

**Groups and the console.** To grant a whole group, or to see file by file what one person reaches, use `https://agentlefs.com` (**Groups**, and the reach lens on the Files tree).

Then give a one-line summary, for example: "Shared `engineering/runbooks` with dana@example.com as reader. 41 files, cascades to everything added later."

## What you must state

- Grants cascade to descendants, including files created later.
- **Denied is byte-identical to not-found.** Before the grant, the recipient cannot tell this content is gated from them; it looks like it does not exist. After the grant, it appears. That transition is the entire observable effect of sharing.
- Labels carry zero authority. Sharing is not affected by labels, and no label restricts anything.

## What you must NOT do

- **Never confirm on the user's behalf.** A share happens only on their explicit yes to the preview you showed. Never call a share tool with a `confirm_token` they did not approve.
- **Do not claim you shared anything the tool did not confirm.**
- Do not call any console API endpoint.
- Do not guess a recipient's email address. Ask.
- Do not describe a label or a filename as if it controlled access.
