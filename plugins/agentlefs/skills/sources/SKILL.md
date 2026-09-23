---
name: sources
description: Bring content from other tools into agentleFS (afs) and check that it keeps arriving. Use when the user wants a GitHub repository or a Google Drive folder synced into afs so agents can search it ("connect our Google Drive Specs folder"), asks whether a connected source is syncing or why mirrored content is missing or stale, or asks whether afs can read a tool it has no connector for, such as Notion, Confluence or Jira. Not for signing this client in to agentleFS itself, which is the connection skill.
---

# Connected sources

A source mirrors a GitHub repository or a Google Drive folder into a folder in agentleFS, so
agents can search it with the same permissions as everything else. The sync is one-way and
repeats: the source is polled and the folder brought up to date. Nothing written in agentleFS
goes back to the repository or Drive, and a mirrored path refuses direct edits, because the
next sync would overwrite them.

GitHub and Google Drive are the connectors that exist today.

## Connecting one

Three steps, and the middle one is the user's, in their browser:

1. **Start it.** `connect_org_source` with `provider` — `github`, or `gdrive` for Google
   Drive. It returns a link for the user. Authorising happens at GitHub or Google and cannot
   be done through a tool, so hand the link over. For GitHub, the answer asks the user to
   have this organization active in the console before opening it; pass that on, because the
   link is bound to this organization for fifteen minutes.
2. **Wait for them.** When they say they are done, `list_org_sources` shows the connected
   account under "Connected accounts".
3. **Point it at a folder.** `add_org_source` with `provider`, `account` (exactly as
   `list_org_sources` printed it), `location` (the destination folder, which you must be able
   to write; `create_org_folder` makes one), and either:
   - GitHub: `repo_owner` and `repo_name`, and `branch` if not the default; or
   - Google Drive: `folder_id`, the id of the Drive folder. It is the last part of the
     folder's URL, after `/folders/`; ask the user to paste the URL if they have not.

   Ask which folder it should land in: the destination's grants decide who can read the
   mirror, and a source's own permissions, where recorded, cap them further.

Then `list_org_sources` again in a moment: a new source says it has not completed a sync
yet, then shows when it last synced, or `FAILING` with the error. Say which. If the account
is already connected (step 2 already lists it), skip straight to step 3.

`connect_org_source` and `add_org_source` refuse with `⚠ refused: you cannot manage connections in this organization.`
and nothing is started. Any member of the organization may connect a source, so this refusal
means the call reached the server without an identity it recognises in this organization.
Check the connection (the `connection` skill) rather than asking anyone for more access.

## When mirrored content looks missing or stale

`list_org_sources` answers whether the source ran and failed, never ran, or is current. A
`search` hit from a mirror carries its sync lag in its freshness, and `search` with `source`
searches one mirror alone.

Deleting a mirrored folder stops its sync, and undoing that delete does not reconnect it —
the `deleting` skill covers this.

## A tool with no connector

When the user asks about content kept in a tool agentleFS cannot mirror (Notion, Confluence,
Jira, and so on):

1. `connectors` with `action: "list"` shows the connectors that exist and how many people
   have asked for each one that does not.
2. If theirs is absent, say plainly that agentleFS cannot read it, and offer to record the
   request: `connectors` with `action: "vote"`, `connector` (the product's name) and `why`
   (what they would do with it). One vote counts per person, shared with all their agents,
   so voting again replaces theirs rather than adding one.
3. If some of that content was exported or copied into agentleFS, a `search` may still find
   it; say that it would be a copy, as current as whenever it was made.
