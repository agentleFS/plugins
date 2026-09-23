---
name: authorization-model
description: How agentleFS (afs) decides what a person or agent may read. Use when reasoning about afs access, grants, roles, cascade, groups or an agent's delegated scope; when a search or listing came back thinner than expected and you need to tell missing content from gated content; when explaining why someone or some agent cannot see a document; or when about to state who can or cannot see something. For carrying out a share, an access request or a who-can-see check, the sharing skill.
---

# agentleFS authorization

Retrieval is authorization-filtered. An agent sees exactly what its principal is granted,
and the filter is applied inside the query rather than bolted on afterward.

## The decision

A credential (an OAuth access token or an `afs_` token) resolves to one principal in one
Organization. That principal's grants — and, for an agent, its delegation chain — are the
entire input. Nothing in the request adds authority: not the folder name, not a label, not
the query, not a flag. Same principal, same answer.

Content access is decided by relationship-based grants in one engine (OpenFGA). There is
no second axis and no separate policy service.

## Grants

A grant says "subject holds `role` on scope".

| Field | Values |
|---|---|
| subject | a person (or other principal) or a group |
| role | `reader`, `writer`, `approver` |
| scope | the Organization root, a folder, or a document |

Breadth comes from where a grant sits, not from a second vocabulary. An approver of the
Organization's root reaches the whole Organization; a folder approver reaches that subtree.
There is no separate `admin` role.

Nothing is readable by default. Ungranted is ungranted: there is no ambient read, no public
tier, no fallback that opens content up.

### Cascade and nesting

- Grants cascade down the folder tree. A grant on a folder reaches every descendant,
  including files created later.
- A grant is **granted-here** (made directly on this scope) or **inherited** (arriving from
  an ancestor). `who_can_read` marks which.
- Groups nest. A grant to a group reaches its members, and a group can contain groups, so a
  principal may reach a file through several hops. Resolution is live, not snapshotted.

### Roles

One ladder: `reader` < `writer` < `approver`. Each rung contains the one below it, so an
approver reads and writes everything at or below where its grant sits. The console shows
`approver` as **Approver**: can share and manage access, and edit.

`approver` additionally carries what the ladder alone does not express — deciding access
requests, deleting, erasing and renaming — bounded to the subtree the grant sits on. Many
principals may hold it on the same node. Handing a member a new grant directly is the one
exception to "bounded to the subtree": `share_org_folder` and the console's share panel both
ask for approver on the Organization's root, so a folder approver's route is approving the
requests that reach them (`share` with `action: "request"` and `"approve"`).

**Owner is not a role.** Every document and folder has exactly one owner — the identity that
created it, or whoever it was reassigned to. Ownership says whose a thing is, and it is who
decides a debate or a proposal about it; it grants no access on its own and is not a rung of
the ladder. If you see `owner` used as a grant role, it is an old name for `approver`. (A
group also has an owner — who manages its membership — which is a third, unrelated thing.)

There are three roles and no others.

## Agents carry a scope, not a grant

An agent's access is computed, never copied: its root person's grants, cut down to the scope
of every link in its delegation chain (`identity` with `action: "spawn"` sets a child's
scope as `role@location`, never wider than its parent's). So an agent can reach much less
than its person, and a grant listing cannot show that. `who_can_read` lists the people and
groups whose grants reach something; whether one particular agent can read it is `share`
with `action: "can_see"`, which applies the whole chain.

Two more things narrow what an identity reads: a **room** is decided by membership rather
than grants, and a document mirrored from a connected source is capped by that source's own
recorded permissions, whatever is granted above it.

## Fail-closed

The read path refuses to under-report. If the set of things a principal may read is too
large to apply in full, the read errors rather than filtering on a subset and returning a
partial answer that looks complete. An error there is the system declining to silently show
you less than your grants allow. Surface it rather than papering over it with a partial
summary.

## Denied reads exactly like not-found

This is the idea the rest depends on: there is no existence oracle.

- A path you cannot read returns not-found, worded identically to a path that does not exist.
- A folder you do not reach is simply absent from `list_org_folders`. No count, no marker,
  no placeholder.
- An empty search says it cannot settle the question, not that nothing exists.
- The empty-listing text is deliberately the same for "nothing here" and "nothing for you".

### Reading a thin result

| What you observe | What it means | What it does not mean |
|---|---|---|
| Empty folder list | This principal reaches no folders | The org has no content |
| `not found: path` | Gated from you, or absent. Cannot distinguish. | The file does not exist |
| Search returns nothing | Nothing matched in what you can read | The org has written nothing on it |
| `12 gated from you` in a folder's shape | 12 files are gated from you | Anything about their names, paths, or subject matter |

The one place a count shows through is `list_org_folders` with `location` set to a folder,
which reports readable versus gated. That is a count only. It never identifies a gated file.

Report a thin result as "nothing I can reach matches", and note that gated content is
invisible from here, rather than as evidence of absence.

## One decider, for the console as well as for content

Console actions resolve through the same ladder: anything above a small read-only floor needs
approver on the Organization's root, the node every folder hangs off. So "may you use this
console action" and "may you read this file" are the same kind of question asked about
different objects. An approver of the root therefore reaches every file in the Organization,
deliberately, because that is what being an approver of the root means.

## Labels carry no authority

Labels (tags) are organization and discovery metadata. No authorization decision reads them.

- "Unlabeled" says nothing about access.
- A sensitive-sounding label restricts nothing.
- Filtering by label narrows what you already reach; it never widens it.

Labels inherit from a folder or directory for discovery, so a folder's label surfaces
everything inside it in a label-filtered listing. That is a search convenience, not an
access rule.

## Common misconceptions

**Untagged content is readable by everyone.** It is not. Grants and group membership are the
only axis; untagged content is ungranted, therefore invisible.

**A policy file or sidecar decides some of this.** Nothing does besides the grant engine. If
you find yourself explaining a denial in terms of a policy file, the model you are using is
out of date.

**An empty result proves nothing exists.** See above. This is the mistake the system is
built to keep you from making.

**An agent can read the audit trail.** No agent tool reads it, by design, so a token holder
cannot audit a whole Organization.

Who reaches something, though, is answerable: `who_can_read` on a folder or document you
reach names the people and groups in the Organization (direct or inherited, with role). It
names people, never their content, and for a scope you cannot reach it answers not-found.
Nobody outside the Organization holds a grant in it; the one way content crosses is a share
offered to another organization and accepted there as a mount (`share` with
`action: "share_out"`), which `share` with `action: "shared"` lists.

**The role that shares cannot itself read.** It can. The sharing role is the top of the
ladder: an approver reads and writes everything beneath it.

**The owner of a folder is whoever holds the top grant on it.** Many principals may hold
`approver` on a node, and it inherits down the tree; a node has exactly one owner, and
ownership is not access. Keep the two words apart.

## Consequences for how you work

- Say you could not reach a document, rather than that it does not exist.
- Infer nothing about access from a name, path, or label.
- Name who can see something only when a tool returned it. `who_can_read` answers "which
  people and groups reach this?", `list_org_people` with `group` answers who is in a group,
  and `share` with `action: "can_see"` answers whether one identity, agent or person, can
  read it. For everything one person reaches, the console's **Permission management →
  People** page lists it.
- When the user lacks access they need, the move is `share` with `action: "request"` and a
  reason, which routes to someone who can grant it — not a guess at who to email.
- Do not call a console API endpoint from an agent context. It accepts only a browser
  session, so an OAuth or `afs_` credential gets a 401 every time.
- A write is authorized or it is refused; there is no staging or review state in between. A
  successful `write_org_doc` is live immediately, and who can then read it is decided by the
  grants on the path, not by anything the writer sets.
