---
description: Answer who can see an agentleFS (afs) folder or document — the people and groups who reach it, and what you can see yourself
argument-hint: [folder-or-path]
allowed-tools: mcp__plugin_agentlefs_agentlefs__list_org_folders, mcp__plugin_agentlefs_agentlefs__list_org_docs, mcp__plugin_agentlefs_agentlefs__search, mcp__plugin_agentlefs_agentlefs__who_can_read, mcp__plugin_agentlefs_agentlefs__list_org_people
---

Answer "who can see `$1`". The answer has two halves: who else reaches it (a real tool answers that), and what you can see of it yourself. Keep them separate, and keep both to what a tool returned.

Target: `$1`. If `$ARGUMENTS` is empty, call `mcp__plugin_agentlefs_agentlefs__list_org_folders` with no arguments, list the reachable folders, and ask which one they mean. If `$1` is a folder name rather than a path, call `mcp__plugin_agentlefs_agentlefs__list_org_folders` with no arguments and match it there, because `search` indexes documents, not folders. That listing stops four levels deep without saying so, so if nothing matches, call it again with `parent` set to the closest folder that did appear before concluding it is not there. If it is a document name, find its path with `mcp__plugin_agentlefs_agentlefs__search` and `how: "titles"`, so a document that only mentions the name does not win; if several titles match, say which one you took. Use either only to resolve the location, never for the counts in Part 1, which come from the listing.

## Part 1 - what you can see yourself

Call `mcp__plugin_agentlefs_agentlefs__list_org_folders` with `location` set to the folder (for a document, the folder that holds it). `location` returns the folder's shape; `parent` would list its subfolders instead. For a specific document, also call `mcp__plugin_agentlefs_agentlefs__list_org_docs` with `location` set to the folder that holds it (for `product/runbooks/deploy.md`, `product/runbooks`) and check the document is listed — `list_org_docs` lists a folder, and a document's own path finds nothing.

Report:

- How many files in this folder you can read.
- How many are gated from you.
- The type and label breakdown.

This is a fact about your own principal, established by a real call. Present it as such.

The gated count is the interesting number. It tells you how many files sit in this folder that you cannot see, and nothing else. Not their names, not their paths, not their subject matter. Do not speculate about them.

## Part 2 - who else can see it

Call `mcp__plugin_agentlefs_agentlefs__who_can_read` with the `location` (and `scope_type: "document"` for a single file). It names the people and groups in this Organization who reach it, each marked **direct** (granted here) or **inherited** (from an ancestor folder), with their role. Nobody outside the Organization holds a grant on it; if it was offered to another organization, `share` with `action: "shared"` lists that.

**If the question is about an agent** ("can the reviewer agent see drafts?"), `who_can_read` is the wrong tool: agents carry a scope cut down from their person's grants rather than grants of their own, so they are not on that list. Ask `share` with `action: "can_see"`, `who` (the agent's id or exact name) and `location`; it answers yes or no after the agent's whole delegation chain is applied, and only about something you can read yourself. Claude Code asks before that call, because the same tool can also change access.

It names people, never their content. It answers only for a scope you reach yourself: for one you do not, it answers not-found, exactly as for a scope that does not exist — so a not-found here is not evidence of anything.

Present the list as the tool returned it. Do not add, merge or guess at names.

For what the tool does not answer, send the human to `https://agentlefs.com` and name the screen:

| Question | Console screen |
|---|---|
| What does a specific person reach? | **Permission management → People**, then open the person: their Access section lists each scope, direct or through a group |
| Who is in a group? | **Permission management → Groups** |
| Change a grant | **Manage access** on the folder or file (its "Shared with" list) |

## Explain how to read the answer

Give the user these three ideas, because a list of who reaches something is misleading without them:

- **Granted-here versus inherited.** A grant made directly on this scope shows as granted-here. One arriving from an ancestor folder shows as inherited. Removing an inherited grant means finding the ancestor it was made on; there is nothing to remove here.
- **Cascade.** Grants flow down the folder tree. Someone with a grant three levels up reaches this file without ever appearing to have been given it directly. `who_can_read` marks that as inherited.
- **Group nesting.** A grant to a group reaches its members, and groups nest, so a person can reach a file through a group inside a group. `mcp__plugin_agentlefs_agentlefs__list_org_people` with `group` walks one level at a time; a raw grant list does not resolve it.

Also worth stating: console actions and file reads are decided by the same engine and the same ladder. Console actions above a small read-only floor need approver on the Organization's root, and an approver of the root reaches every file in the Organization, because that is what the role means there. A folder approver reaches only that folder's subtree.

## Do not

- Guess at a name. "Probably the engineering team" or "likely whoever owns this folder" reads as a finding; if it did not come from a tool result, leave it out.
- Call a console API endpoint. It accepts only a browser session, so this credential would get a 401; `who_can_read` is the route.
- Present your own reach as the full picture. Other principals may reach far more than you, or far less, and you cannot see which.
- Infer access from labels. Labels carry no authority; an unlabeled file is not public.
- Read a thin result as "nothing exists here." Denied reads exactly like not-found, so a folder that looks nearly empty to you may be full of content gated from you.

## Shape of the answer

1. Who else reaches it, from `who_can_read`: direct or inherited, with role.
2. What you can see yourself, with real numbers from the calls you made.
3. For everything one person reaches, the console's **Permission management → People** page.
