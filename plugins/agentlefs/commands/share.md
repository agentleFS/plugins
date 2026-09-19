---
description: Share an agentleFS (afs) folder or document by email or link — shows exactly who gets what, and shares only after you say yes
argument-hint: [folder-or-path]
allowed-tools: mcp__plugin_agentlefs_agentlefs__list_org_folders, mcp__plugin_agentlefs_agentlefs__list_org_docs, mcp__plugin_agentlefs_agentlefs__who_can_read
---

Help the user share `$1` with someone. Your job is to get the decision right, show its blast radius, and share **only after they say yes** to the exact preview.

The share tools are deliberately left out of this command's pre-approved tools, so Claude Code also asks the user before each share call. That prompt is a second guard, not a substitute for asking them yourself.

Target: `$1` (a `location` — a full path from the workspace root, naming either a folder like `product` or a single document like `product/runbooks/deploy.md`). If `$ARGUMENTS` is empty, call `mcp__plugin_agentlefs_agentlefs__list_org_folders` with no arguments, show the reachable folders, and ask which one they mean.

## Step 1 - orient on what the recipient would get

Do this first. Sharing decisions go wrong because the sharer does not know how much is under the thing they are sharing.

- For a folder: call `mcp__plugin_agentlefs_agentlefs__list_org_folders` with that folder. Report how many files are there, the type breakdown, and the labels.
- For a single document: call `mcp__plugin_agentlefs_agentlefs__list_org_docs` with the document's `location` to confirm it exists and is the intended file.

Then state the blast radius explicitly: **grants cascade down the folder tree.** A grant on a folder reaches every descendant of that folder, including subdirectories and files added later. A grant scoped to one document reaches only that document.

Say the number out loud. "Sharing `engineering/` at view gives them all 240 files under it, including anything added tomorrow" is the sentence that prevents the mistake.

One caveat to state honestly: the counts you can see are **your** counts. If the folder holds files gated from you, the total is larger than what you reported. Say so rather than presenting your view as the complete inventory.

## Step 2 - choose the role

Three roles are offered outward. The console labels them view / edit / manage.

| Console label | Role | Grants | Use when |
|---|---|---|---|
| view | `reader` | read and search the content | the default; the recipient needs to know, not change |
| edit | `writer` | read plus write and edit documents | the recipient maintains the content |
| manage | `owner` | ownership of the scope, and satisfies the writer bar | the recipient is accountable for it |

Guidance to give:

- Default to view. Escalate only on a stated need.
- **One ladder: `reader` < `writer` < `owner`.** Each rung contains the one below it, so an owner reads and writes everything at or below what it owns, and additionally grants and revokes there. Treat manage as "accountable for it, and can change it".
- The ladder is stated once, in `openfga/model.fga`, and there is no app-layer fold — asking the engine for `writer` already returns allow for an owner, so the console and MCP cannot give different answers. This guidance used to say `owner ⇏ writer` and that the authority layer folded it; that was the pre-#219 model.
- There are three roles and no others. `proposer` and `member` are retired, and neither was ever granted to anyone.

Pick the narrowest scope that does the job. A document-scoped grant is almost always safer than a folder-scoped one, and re-sharing a second document later is cheap.

## Step 3 - see who already reaches it

Call `mcp__plugin_agentlefs_agentlefs__who_can_read` on the target. If the recipient already reaches it (directly, inherited, or through a group), say so: sharing again changes nothing, or changes only the role.

## Step 4 - preview, ask, then share

The two tools do NOT work the same way, and the difference decides when you ask.

**By email — `share_org_folder`, TWO calls.** Pass `location`, `emails` and `role` (`reader` / `writer` / `owner`; add `scope_type: "document"` for one file). The first call **previews and shares nothing**; only a second call carrying its `confirm_token` shares. Someone in this Organization gets an ordinary grant; anyone else finds it under "Shared with me"; a stranger is invited to sign up. It sends real email.

1. Make the preview call now, without asking first. It shares nothing, and its reply is the preview you are about to show — asking before it means asking the user to approve something they have not seen.
2. Show the user the preview in plain words: who, what role, how many files it reaches (from Step 1), and that it cascades.
3. **Ask. Wait for an explicit yes to THAT preview.** "Share it" before the preview is not a yes to the preview.
4. On yes, call again with the `confirm_token`. On anything else, stop — nothing was shared.
5. Report what the tool returned, and confirm with `mcp__plugin_agentlefs_agentlefs__who_can_read`.

A token expires after ten minutes, and it is refused if the folder, the role or the address list changed since the preview; either way, preview again and ask again.

**By link — `create_org_share_link`, ONE call, and it mints the link immediately.** There is no preview and no `confirm_token`, so the user's yes comes BEFORE the only call. Describe the link you would make — target, role, and whether it is open (no `emails`: anyone holding the link can claim `role`, so it is a credential — safe to forward, not to post) or restricted (`emails`: only those addresses can) — get an explicit yes, then call it once. The link is returned exactly once; hand it over and do not repeat it elsewhere.

**If a share tool refuses with "you cannot change who reaches content"**, nothing was shared, and the console will refuse for the same reason. Handing out access is authority over the whole Organization, not over the folder, so owning the folder does not help in either place. Say that plainly, and name the move: ask an owner of the Organization to share it, or to make you an owner of the Organization. The same refusal and the same answer apply to `create_org_share_link` and `revoke_org_share`.

**Taking a share back.** For someone OUTSIDE the Organization, `revoke_org_share` with the email as `who_can_read` prints it. Grants held by members of this Organization can be inherited from a parent folder, so change those in the console, where you can see where each grant actually lives.

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
