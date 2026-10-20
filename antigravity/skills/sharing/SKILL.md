---
name: sharing
description: Give, get and check access in agentleFS (afs). Use when the user wants to share a folder or document with a colleague, asks for access they do not have ("I need access to the legal folder"), has access requests waiting on their approval, asks who can read something or whether a particular agent can see something, or wants to offer a folder to someone in another organization or accept one offered to them. For why access works the way it does, the authorization-model skill.
---

# Sharing and access in agentleFS

Five different questions come up, and each has its own action. Picking by the question avoids
the two expensive mistakes: widening access nobody asked for, and telling someone they can
read what they cannot.

Reading access is `access_read`, which changes nothing and runs without a prompt. Giving or
asking for access is `access_grant`, and taking it back is `access_revoke`; both are marked
destructive, so the user's client asks before each call.

| The user wants | Call |
|---|---|
| A colleague in this organization to get access | `access_grant` with `action: "share"` |
| Access they do not have themselves | `access_grant` with `action: "request"` |
| To know which people and groups reach something | `access_read` with `action: "who_can_read"` |
| To know whether a specific agent (or person) can read something | `access_read` with `action: "can_see"` |
| To give someone in another organization a folder | `access_grant` with `action: "share_out"` |

Every one of them answers not-found for something you cannot read yourself, exactly as for
something that does not exist, so a not-found is never evidence either way.

## Granting a colleague: `access_grant` with `action: "share"`

1. Resolve names to addresses. "The design team" is a guess until `browse` with
   `action: "people"` (and `group` for one group) says who is in it. Ask for an email you do
   not have; do not invent one — a guessed address shares with the wrong person, or with nobody.
2. `access_read` with `action: "who_can_read"` on the target, to see whether they already
   reach it — then sharing changes nothing, or only the role.
3. Call `access_grant` with `action: "share"`, `location`, `emails`, `role` (`viewer`,
   `editor` or `manager`) and, for a single file, `scope_type: "document"`. This first call
   shares nothing: it returns exactly who would get what, and a `confirm_token`.
4. Show the user that preview — who, which role, and that a folder share reaches
   everything beneath it, including files added later — and wait for their yes to it.
5. Call again with the same arguments and the `confirm_token`. Report each address's
   result; an address that is not a member of this organization is refused and gets
   nothing. It sends no email.

A token lasts ten minutes and is bound to that exact folder, role and address list; change
any of them and preview again.

Default to `viewer`, and prefer a document to a folder when that is all they need.

**Who may do this.** As in Google Drive: a manager of the folder or document, or of a folder
above it, may share it as anything; an editor there may share it as `viewer` or `editor`, unless
its owner or a manager turned off "Editors can change permissions and share" (`access_read`
with `action: "settings"` says whether it is on; `access_grant` with `action: "set_settings"`
changes it). Only a manager can make someone a manager. That is the same rule in the console's
share panel and the SDK. Anyone else gets
`⚠ refused: sharing this needs manager on it or a folder above it, …` and nothing is shared. Someone who does not approve it can still help: they
can ask to become a manager (`access_grant` with `action: "request"` and `role: "manager"`,
below), or the colleague can request access themselves, and either request reaches whoever
does approve it.

## Getting access yourself: `access_grant` with `action: "request"`

`access_grant` with `action: "request"`, the `location`, `role` (`viewer` by default, `editor`,
or `manager` to share it and decide others' requests; approving gives the same role to every
agent you work under that lacks it, so ask for the smallest role the job needs) and a `reason`
— the reason is what the person deciding reads, one line, in your words.
The request goes to the nearest identity that can grant it: the user's own parent, a person
both sides share, or the data owner's person, climbing until someone has the authority.

- Add `wait: true` with a `deadline` to be woken when it is decided; otherwise it shows up
  in a later `brief_me`.
- `access_read` with `action: "my_requests"` shows the user's requests and their state;
  `access_revoke` with `action: "withdraw"` and `request_id` takes one back.
- A request for something that does not exist is filed as unroutable rather than refused,
  so the answer never confirms whether a path exists. If a request comes back unroutable,
  say nobody could be found to decide it, and suggest asking a person directly.

A request for a role you already hold, or one below it (manager implies editor, editor implies
viewer), is refused as pointless (`already_has_access`), which is worth knowing before telling
the user to wait on one.

## Deciding requests routed to the user

`access_read` with `action: "requests"` lists requests waiting on the user (`brief_me` shows
them as `approvals`). Each is theirs to decide: show who is asking, for what, at what role,
and their reason, and anyone in `alsoGains`: the agents the requester works under that
approving also gives the role to, since an agent never holds more than those above it. Say
that part plainly, because a manager request can make an agent that was only reading a manager
too. Then `access_grant` with `action: "approve"` or `action: "decline"`, `request_id` and a
`note`, only on the user's answer.

## Who reaches something: `access_read` with `action: "who_can_read"`

`action: "who_can_read"` with `location` (and `scope_type: "document"` for one file) lists the
people and groups in this organization who reach it, each direct or inherited, with role.
Groups appear like people, so walk a group with `browse` `action: "people"` and `group` before
concluding someone is absent; groups nest.

It lists people and groups, not agents. An agent's access is its person's, narrowed by every
scope in its delegation chain, so an agent can reach less than its person appears to.

## Can a particular agent see it: `access_read` with `action: "can_see"`

`action: "can_see"`, `who` (an identity id or exact name) and `location` answers yes or no for
that identity — agent or person — after its whole chain has been applied. It only answers
about something you can read yourself.

## Other organizations

Sharing with a colleague stays inside this organization. To give a person in another
organization a folder or document:

1. `access_grant` with `action: "share_out"`, `location`, `to` (their email) and `role`
   (`viewer` or `editor`). They need to have signed up with that address; otherwise the
   answer says they were invited instead.
2. A person with authority over the data offers it directly. An agent's offer is a proposal
   that the data's owner decides in the console: `access_read` with `action: "proposals"`
   lists them so you can tell their person.
3. The recipient sees it with `access_read` `action: "offers"`, which lists each offer's id,
   and accepts with `access_grant` `{"action": "accept_share", "share_id": "…"}` (or turns it
   down with `{"action": "decline_share", "share_id": "…"}`) into their own organization,
   where it appears under `__shared/<id>` and is read with the ordinary document tools. Their
   organization's own grants then decide who there can read it.

`access_read` with `action: "shared"` lists what this organization has shared out and
received. `access_revoke` with `{"action": "withdraw_share", "share_id": "…"}` takes a share
back; everyone reading through it loses it on their next call, so confirm with the user first.

## Less common

- `access_read` with `action: "labels"` and `location`: where a document's content came from.
  A source you cannot read shows as restricted, never by name.
- `access_grant` with `action: "declassify"`: release what this session has read, so the next
  write is not labeled with it, or release one label on a document (`location`, `source`) —
  only for data the user's chain can approve sharing.
- `access_grant` with `action: "hold"` and `location` (or `identity`) and a `reason` places a
  legal hold: nothing under it can be erased or purged until `access_revoke` with
  `action: "release_hold"` and `hold_id`. Place or lift one only when the user asks for it by
  name.
