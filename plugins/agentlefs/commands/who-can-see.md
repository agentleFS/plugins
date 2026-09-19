---
description: Answer who can see an agentleFS (afs) folder or document — the people and groups who reach it, and what you can see yourself
argument-hint: [folder-or-path]
allowed-tools: mcp__plugin_agentlefs_agentlefs__list_org_folders, mcp__plugin_agentlefs_agentlefs__list_org_docs, mcp__plugin_agentlefs_agentlefs__who_can_read
---

Answer "who can see `$1`". The answer has two halves: who ELSE reaches it (a real tool answers that), and what YOU can see of it. Keep them separate, and never let either drift into speculation.

Target: `$1`. If `$ARGUMENTS` is empty, call `mcp__plugin_agentlefs_agentlefs__list_org_folders` with no arguments, list the reachable folders, and ask which one they mean.

## Part 1 - what YOU can see (answerable now)

Call `mcp__plugin_agentlefs_agentlefs__list_org_folders` with the folder. For a specific document, also call `mcp__plugin_agentlefs_agentlefs__list_org_docs` with the document's full `location`.

Report:

- How many files in this folder you can read.
- How many are `denied`, meaning gated from you.
- The type and label breakdown.

This is a fact about **your** principal, established by a real call. Present it as such.

The gated count is the interesting number. It tells you how many files sit in this folder that you cannot see, and nothing else. Not their names, not their paths, not their subject matter. Do not speculate about them.

## Part 2 - who ELSE can see it

Call `mcp__plugin_agentlefs_agentlefs__who_can_read` with the `location` (and `scope_type: "document"` for a single file). It names:

- **people and groups inside this Organization** who reach it, each marked **direct** (granted here) or **inherited** (from an ancestor folder), with their role;
- **people outside the Organization** who hold a share on it, by the email it was shared with.

It names people, never their content. It answers only for a scope **you** reach yourself: for one you do not, it answers not-found, exactly as for a scope that does not exist — so a not-found here is not evidence of anything.

Present the list as the tool returned it. Do not add, merge or guess at names.

For what the tool does not answer, send the human to `https://agentlefs.com` and name the screen:

| Question | Console screen |
|---|---|
| What exactly can a specific person or group see, file by file? | the **reach lens** ("View as") on the Files tree |
| Who is in a group, and what does the group reach? | **Groups** |
| Change a grant held by someone inside the Organization | the **"Shared with"** list on the folder or file |

To take back a share given to someone OUTSIDE the Organization, `/agentlefs:share` covers it with `revoke_org_share`.

## Explain how to read the answer

Give the user these three ideas, because a list of who reaches something is misleading without them:

- **Granted-here versus inherited.** A grant made directly on this scope shows as granted-here. One arriving from an ancestor folder shows as inherited. Removing an inherited grant means finding the ancestor it was made on; there is nothing to remove here.
- **Cascade.** Grants flow down the folder tree. Someone with a grant three levels up reaches this file without ever appearing to have been given it directly. `who_can_read` marks that as inherited.
- **Group nesting.** A grant to a group reaches its members, and groups nest, so a person can reach a file through a group inside a group. The reach lens resolves this; a raw grant list does not.

Also worth stating: console tools and file reads are different questions, but not different engines. There is no separate policy engine — both resolve through the same OpenFGA ladder. Console actions above a small read-only floor require ownership of the **tenant root**, and owning the root does reach every file in the workspace, because that is what owning the root means. A folder-scope owner reaches only their subtree.

## What you must NOT do

- **Never guess at a name.** Do not say "probably the engineering team" or "likely whoever owns this folder." If you do not have it from a tool result, you do not have it.
- Do not call any console API endpoint. No `/api/reach/grants`, no `/api/share/summary`, no `/api/folders/reach`. Every one would 401; `who_can_read` is the route.
- Do not present your own reach as the full picture. Other principals may reach far more than you, or far less, and you cannot see which.
- Do not infer access from labels. Labels carry zero authority; an unlabeled file is not public.
- Do not read a thin result as "nothing exists here." **Denied is byte-identical to not-found.** A folder that looks nearly empty to you may be full of content gated from you.

## Shape of the answer

1. Who else reaches it, from `who_can_read`: inside the Organization (direct or inherited, with role), and outside it.
2. What you can see yourself, with real numbers from the calls you made.
3. For a file-by-file view of one person's access, the console's reach lens.
