---
name: sharing
description: Give, get and check access in agentleFS (afs). Use when the user wants to share a folder or document with a colleague, asks for access they do not have ("I need access to the legal folder"), has access requests waiting on their approval, asks who can read something or whether a particular agent can see something, or wants to offer a folder to someone in another organization or accept one offered to them. For why access works the way it does, the authorization-model skill.
---

# Sharing and access in agentleFS

Five different questions come up, and each has its own tool. Picking by the question avoids
the two expensive mistakes: widening access nobody asked for, and telling someone they can
read what they cannot.

| The user wants | Tool |
|---|---|
| A colleague in this organization to get access | `share_org_folder` |
| Access they do not have themselves | `share` with `action: "request"` |
| To know which people and groups reach something | `who_can_read` |
| To know whether a specific agent (or person) can read something | `share` with `action: "can_see"` |
| To give someone in another organization a folder | `share` with `action: "share_out"` |

Every one of them answers not-found for something you cannot read yourself, exactly as for
something that does not exist, so a not-found is never evidence either way.

## Granting a colleague: `share_org_folder`

1. Resolve names to addresses. "The design team" is a guess until `list_org_people` (or
   `list_org_people` with `group`) says who is in it. Ask for an email you do not have;
   do not invent one — a guessed address shares with the wrong person, or with nobody.
2. `who_can_read` on the target, to see whether they already reach it — then sharing
   changes nothing, or only the role.
3. Call `share_org_folder` with `location`, `emails`, `role` (`reader`, `writer` or
   `approver`) and, for a single file, `scope_type: "document"`. This first call shares
   nothing: it returns exactly who would get what, and a `confirm_token`.
4. Show the user that preview — who, which role, and that a folder share reaches
   everything beneath it, including files added later — and wait for their yes to it.
5. Call again with the same arguments and the `confirm_token`. Report each address's
   result; an address that is not a member of this organization is refused and gets
   nothing. It sends no email.

A token lasts ten minutes and is bound to that exact folder, role and address list; change
any of them and preview again.

Default to `reader`, and prefer a document to a folder when that is all they need.

**Who may do this.** Handing out access is authority over the organization's content, so
`share_org_folder` needs approver on the organization root, the same as the console's share
panel. Anyone else gets `⚠ refused: you cannot change who reaches content in this organization.` and
nothing is shared. Being an approver of the folder is not enough for this tool; what a
folder approver can do is approve the colleague's own access request (below), which is often
the better route anyway.

## Getting access yourself: `share` with `action: "request"`

`share` with `action: "request"`, the `location`, `role` (`reader` by default, or
`writer`) and a `reason` — the reason is required, and it is what the person deciding reads.
The request goes to the nearest identity that can grant it: the user's own parent, a person
both sides share, or the data owner's person, climbing until someone has the authority.

- Add `wait: true` with a `deadline` to be woken when it is decided; otherwise it shows up
  in a later `brief_me`.
- `action: "list"` shows the user's requests and their state; `action: "withdraw"` with
  `request_id` takes one back.
- A request for something that does not exist is filed as unroutable rather than refused,
  so the answer never confirms whether a path exists. If a request comes back unroutable,
  say nobody could be found to decide it, and suggest asking a person directly.

A `reader` request for something you can already read is refused as pointless
(`already_has_access`), which is worth knowing before telling the user to wait on one.

## Deciding requests routed to the user

`share` with `action: "inbox"` lists requests waiting on the user (`brief_me` shows them as
`approvals`). Each is theirs to decide: show who is asking, for what, at what role, and their
reason, then `action: "approve"` or `action: "decline"` with `request_id` and a `note` only
on the user's answer.

## Who reaches something: `who_can_read`

`who_can_read` with `location` (and `scope_type: "document"` for one file) lists the people
and groups in this organization who reach it, each direct or inherited, with role. Groups
appear like people, so walk a group with `list_org_people` and `group` before concluding
someone is absent; groups nest.

It lists people and groups, not agents. An agent's access is its person's, narrowed by every
scope in its delegation chain, so an agent can reach less than its person appears to.

## Can a particular agent see it: `share` with `action: "can_see"`

`share` with `action: "can_see"`, `who` (an identity id or exact name) and `location` answers
yes or no for that identity — agent or person — after its whole chain has been applied. It
only answers about something you can read yourself.

## Other organizations

Sharing with a colleague stays inside this organization. To give a person in another
organization a folder or document:

1. `share` with `action: "share_out"`, `location`, `to` (their email) and `role` (`reader`
   or `writer`). They need to have signed up with that address; otherwise the answer says so
   and nothing is shared.
2. A person with authority over the data offers it directly. An agent's offer is a proposal
   that the data's owner decides: `action: "proposals"` lists them, and
   `{"action": "decide_share", "share_id": "…", "approve": true}` (or `false`) settles one.
3. The recipient sees it with `action: "offers"`, which lists each offer's id, and accepts
   with `{"action": "accept_share", "share_id": "…"}` (or turns it down with
   `{"action": "decline_share", "share_id": "…"}`) into their own organization, where it appears under `__shared/<id>` and is read with the
   ordinary document tools. Their organization's own grants then decide who there can read it.

`action: "shared"` lists what this organization has shared out and received.
`{"action": "withdraw_share", "share_id": "…"}` takes a share back; everyone reading through
it loses it on their next call, so confirm with the user first.

## Less common, on the same tool

- `action: "labels"` with `location`: where a document's content came from. A source you
  cannot read shows as restricted, never by name.
- `action: "declassify"`: release what this session has read, so the next write is not
  labeled with it, or release one label on a document (`location`, `source`) — only for data
  the user's chain can approve sharing.
- `action: "hold"` with `location` (or `identity`) and a `reason` places a legal hold:
  nothing under it can be erased or purged until `action: "release_hold"` with `hold_id`.
  Place or lift one only when the user asks for it by name.
