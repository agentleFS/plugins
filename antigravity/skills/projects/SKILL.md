---
name: projects
description: Run a project in agentleFS (afs) with other people and their agents, or alone. Use when the user wants to start a project ("start a project to get us EU AI Act compliant"), add people to one, see what is open or waiting in their projects, take on or hand back a piece of a project's work, report what they did, end a project, or split project work across helper agents (subagents, cloud sessions, `codex exec`) that report back.
---

# Projects in agentleFS

A **project** is a folder marked as one. Nothing else about the folder changes: its documents
live there as before, and whoever can read the folder is a member. The mark adds three things:

- **The brief** is the folder's `AGENTS.md`: the goal, the current direction, where documents go,
  how work is checked, and, in its frontmatter, `repos:` (the repositories the project covers).
  agentleFS hands it to every agent that works in the folder.
- **The conversation** is the folder's discussion: comment threads on the folder itself.
- **Briefings**: `brief_me` lists the projects you follow, and the projects whose `repos:` name
  the repository you are in, with their open threads.

## Start one

1. `coordination_write` with `action: "start_project"`, `location` (the folder), and `routing`: `members`
   (each member's agent takes the work its person picks; the default) or `owner` (the owner's
   side assigns it). Starting a project follows it. Only someone who may share the folder may
   start or end one, and a project never sits inside another.
2. Write the brief with `doc_create`, `action: "document"`, `folder_path` (the project folder),
   `name: "AGENTS.md"` and `content`. Draft it from what the user said, show it to them once, and
   put the repositories in frontmatter:

   ```markdown
   ---
   repos: [github.com/acme/app]
   ---

   # EU AI Act compliance
   Goal, direction, where documents go, how work is checked.
   ```

3. To add people, share the folder: `access_grant` with `action: "share"`, `location`, `emails`
   and `role`. Being able to read the folder makes someone a member, and being granted it follows
   the project; there is no join step. Their next session with this plugin is briefed on it.

## See what is open

`brief_me` with `repo` set to the repository's remote (any spelling) adds the projects that cover
it; its `projects` field lists each project's open threads, who took them, by when, and what was
reported. `brief_me` with `only: "projects"` says just what moved since your last brief. When you
have read it, `coordination_write` with `action: "ack_brief"` and `through` (the brief's
`cursor.head`) so the next one starts after it. `browse` with `action: "projects"` lists every
project you can read.

To follow a project you have not posted in yet: `coordination_write` with `action: "subscribe"`
and `location` (the project folder). Posting or replying in a project follows it too.

## Post, take and report work

- Post work to the project: `message_write` with `action: "comment"`, `location` (the project
  folder) and `body`. Each piece of work is its own thread.
- Take a thread on: `message_write` with `action: "reply_comment"`, `thread`, `body` and
  `status: "taken"`, with `by` (a date; seven days from today when you leave it out). Ask the
  user for a date only when the task names a deadline. In an `owner` project, take only what the
  owner's side assigned you; say no in the thread otherwise.
- Report it: `action: "reply_comment"` with `thread`, `body`, `status: "reported"` and `link`
  (the document or folder you made). The thread is resolved (`action: "resolve_comment"` with
  `thread`) once the work is accepted, by whoever reviews it; until then the thread stays open for
  review. If you stop with work you took and have not reported, this plugin's Stop hook sends you
  back once to report it.
- A decision the project should keep is a truth on the brief: `coordination_write` with
  `action: "propose"`. Anyone may propose; the project's owner decides a contested one.

## Split the work across helpers

Every helper keeps one contract: it starts with the brief and its one task, works over MCP, and
reports on its thread before it ends. How it runs is your tool's business:

- **A subagent in this session** (Claude Code or Codex): give it the project folder, the thread
  id and the task in its prompt, and tell it to report with `reply_comment` before it finishes. It
  acts as you.
- **A Claude Code cloud session** (`claude --cloud`, or a routine): it signs in to agentleFS as
  your person, so first create an agent for it: `identity_write` with `action: "spawn"`,
  `display`, `purpose`, `lifecycle: "ephemeral"` and `scope` (for example
  `["editor@<project folder>"]`). Put only the new
  agent's **id** in the session's prompt, and tell it to pass `acting_as` with that id on every
  agentleFS call, so it works with that agent's narrower access and its work is recorded as that
  agent's.
- **`codex exec` or any process you start yourself**: spawn an agent the same way and give the
  process its credential only as `AGENTLEFS_TOKEN` in that process's environment. Never write a
  credential into a prompt, a document, a comment or a file.

A helper spawned with `lifecycle: "ephemeral"` ends on its own: a day after it was made (unless
`expires_at` says otherwise), or as soon as every thread it took is resolved, so it can still answer
review on its own work. A call `acting_as` one that has ended is refused with `identity_retired`:
spawn a new one. To end one sooner: `access_revoke` with `action: "retire"` and `target`.

## End one

`coordination_write` with `action: "end_project"` and `location`. The folder, its documents and its discussion
stay; only the mark goes.
