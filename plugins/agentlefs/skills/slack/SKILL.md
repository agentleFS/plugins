---
name: slack
description: Work across agentleFS (afs) and Slack together. Use when the user asks to tell, ping, message, or notify someone in Slack about an agentleFS document or folder ("tell Bob in Slack the doc needs a look"); when they ask for the latest on a topic, a project, or what was decided and the answer may be split between written docs and Slack conversation; or when they want a Slack thread's outcome saved into agentleFS. Needs Slack's own MCP server connected in this client alongside agentleFS.
---

# agentleFS and Slack together

agentleFS holds what was written down. Slack holds what was said. A person asking
"what's the latest on X" usually means both, and a person asking you to "tell Bob about
the doc" is asking you to use both — the doc from one, the message through the other.

**agentleFS does not read Slack.** There is no copy of Slack in agentleFS and no
Slack tool on the agentleFS server. Slack reaches this session only through Slack's own
MCP server, connected in this client with the user's own Slack sign-in, and Slack
decides what that sign-in may see — the same channels, private channels and DMs the
user sees in Slack, nothing more. That is deliberate (decided 2026-09-19): Slack's API
terms bar third-party apps from keeping copies of Slack data, and a live read with the
person's own permissions is the only version that is both allowed and exactly right.

So each system enforces its own permissions, and you never move content from one to
the other without the user deciding where it goes.

## Step 0 — is Slack here?

Look at your tools. Slack's MCP server, when connected, adds tools for searching Slack,
reading channels and threads, and sending messages.

| What you see | Do this |
|---|---|
| Slack tools and agentleFS tools | Continue. |
| agentleFS tools only | Say Slack is not connected in this client, and send them to the agentleFS console's home page, **Set up Slack for your AI**, which has the setup for their client. Answer from agentleFS alone if that still helps, and say the Slack half is missing. |
| Slack tools only | agentleFS is not connected. Use the `connection` skill. |

Never paraphrase a missing Slack connection as "nothing in Slack about this".

## "Tell <person> in Slack about <doc>"

The failure this prevents: a message that sends someone a link they cannot open. It
reads as a broken product to them and as a done job to the user.

1. **Find the doc.** `search_org_knowledge` or `read_org_doc`, until you hold its exact
   location. If two docs plausibly match, ask which.
2. **Check whether that person can read it.** `who_can_read` on the doc's location with
   `scope_type` `document` (or the folder, for a folder). Its answer is a roster, not a
   yes or no, and three things about it decide how you read it:

   - **People inside the organization are listed by display name, never by email.**
     So matching the Slack person to a line is a name match in the common case — say
     so when you report it.
   - **Groups are listed in the same shape as people.** "Engineering — reader" is a
     group, and Bob may read through it without his name appearing anywhere. When a
     name on the roster could be a group, call `list_org_people` with that group to
     see its members before concluding anything. A member marked "nested group" is
     another group: walk it too, until no unexplored group is left — groups nest at
     any depth, and that call lists one level.
   - **Nobody outside the organization is ever on it.** Sharing does not cross
     Organizations, so a Slack person who is not a member cannot open the doc whatever
     the roster says.

3. **Act on the answer:**

   | Result | Do this |
   |---|---|
   | They are listed by name, or are a member of a listed group | Send the message. |
   | Nobody on the roster is them, and every listed group — nested ones included — has been walked to the bottom | Stop before sending. Tell the user "<person> can't open that doc", and offer to share the folder with them first (`share_org_folder`) — which changes who can read it, so it needs the user's yes, not yours, and reaches them only if they are a member of this organization. |
   | You cannot tell — `not found`, a refusal, a group whose members you cannot list, a roster of bare ids with no names, or no confident name match | Say which, and ask whether to send anyway. Never offer a new grant on an answer you could not read: widening access to fix a problem that may not exist is the one mistake here that outlives the message. |

4. **Send it** through Slack's tools, to the person or channel the user named. Include
   the doc's title, a one-line reason, and its location in agentleFS. Show the user the
   exact text before sending when they did not dictate it — a Slack message is outward
   and cannot be versioned back the way a doc edit can.

## "What's the latest on <topic>?"

1. Search both, with the user's words: `search_org_knowledge`, and Slack's search.
2. Read the top few hits on each side before answering. A title is not an answer.
3. Answer in one merged account, ordered by date, and mark each claim's source —
   the doc's location, or the Slack channel and date. When the two disagree, say so and
   give both; a newer Slack message often supersedes an older doc, and nobody updated
   the doc.

If only one side has anything, say which side was empty. "Nothing in Slack" and "Slack
not connected" are different answers.

## Saving a Slack outcome into agentleFS

When a thread settles something, the user may want it kept. Write a **summary in your
own words** — the decision, why, who was involved, a link to the thread — never a
pasted transcript and never a bulk export of channel history.

Two reasons, both firm:

- **The destination decides who can read it**, and a private channel's contents moved
  into a shared folder reach people the channel never included. Ask where it goes, the
  same way the `sync-conversation` skill does, with no default folder.
- **Slack's terms bar keeping copies of Slack data.** A person deciding to write down
  what was decided is their own note; an agent mirroring messages is a copy.

Then `write_org_doc` it.
