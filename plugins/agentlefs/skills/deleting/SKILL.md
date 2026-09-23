---
name: deleting
description: How to delete, restore and permanently erase things in agentleFS (afs) without destroying more than intended. Use whenever a deletion is on the table — removing a document, clearing out a directory, deleting a folder, cleaning up after a migration or a bad ingest; when the user wants something deleted by mistake brought back or undone; when they ask to permanently erase or purge data, for example for a GDPR or other erasure request; and before calling delete_org_doc or erase_org_doc for any reason. Also use to explain why a delete or erase was refused, or why each needs two calls.
---

# Deleting from agentleFS

A delete is reversible: `undo_delete` puts back exactly what one delete removed, sharing
included, from this session or a later one. `erase_org_doc` is the one that is not — it
destroys content and every past version, and nothing brings it back. Reversible still does
not mean harmless: a folder delete takes everything under it, and every person and agent that
relied on it loses it until someone notices.

So the rule for this skill is one sentence: you find out what would be destroyed, a
person decides, and only then do you delete.

## The tool makes you do it in two calls

`delete_org_doc` will not delete on a first call. Call it without
`confirm_token` and it deletes nothing — it returns what *would* go, plus a token:

```
⚠ NOT DELETED YET — this is what would happen.

Target: the entire folder engineering
Files removed: 240
  e.g. engineering/onboarding.md, engineering/runbooks/deploy.md, engineering/adr/0003-folders.md
  …and 237 more not listed here (beyond this sample, or approved by you without a read grant)
Connector: syncs from the GitHub repository acme/platform into engineering — deleting the folder stops that sync.

Reach grants survive a delete, and undo_delete restores the documents and their sharing — it is recoverable, not shredded. A connector is the one thing an undo does NOT bring back: reconnecting it is a decision, not a restoration.
```

`location` decides the shape: a path with a `/` in it names a file or a directory, and a
bare name (`engineering`) names the whole folder. A whole-folder delete also needs
`confirm_delete_folder` set to that same folder name, on both calls — without it the tool
refuses before it previews anything. Repeating the name is deliberate: it is a statement
about which folder, where a boolean would be one careless `true` away.

The preview is not a formality to route around. It is the sentence that prevents the
mistake, and it is addressed to a person, not to you.

## What to do with it

1. **Call once without `confirm_token`.** Never guess a token, never reuse one from
   earlier in the conversation.
2. **Show the person what came back** — in your own words is fine, but keep the file
   count, the target, and any connector line. Those are the whole decision.
3. **Ask, and wait for an answer.** A real question with a real pause. "I'll go ahead
   unless you object" is not asking.
4. **Only then call again with the token** (and `confirm_delete_folder` again, for a whole
   folder).

Spend a token only on the approval of the person who just saw its preview. If you were asked to
"clean up the old folders" and you are three deletes into a list, each one still gets
its own preview and its own answer. Bulk permission is the thing this skill exists to
prevent — the second delete is where the surprise lives.

If they say no, say what you did not delete and stop. Do not offer a narrower delete
unless they ask; the answer to "should this be gone" was no.

## Read the preview properly

- **The file count is the true number.** The permission check counts every file at
  the target, including any you cannot read, and it passes only if you are an approver
  of all of them. Approver includes read, so a preview only ever comes back for a set
  you can read in full; anything gated from you makes the call refuse instead (below).
- **The "not listed" number is not an alarm.** The preview names a short sample, and
  "not listed" is everything past it. Read it as "more than the sample", not "hidden
  from you".
- **The sample is exact, never approximate.** Every path named is a path that will
  actually go. A file that merely shares the prefix — `reports-archive/` when you
  named `reports`, or `open.md.bak` when you named `open.md` — is not in the blast
  radius and will not appear.
- **A connector line changes the decision.** If the folder mirrors a GitHub repo or
  a Drive folder, deleting it here stops that sync. The upstream content survives;
  the organization's access to it through agentleFS does not. Say this plainly —
  people delete folders thinking they are tidying a copy. An undo does not reconnect
  it: `undo_delete` brings back the documents and their sharing, and the sync stays
  stopped until someone connects the source again.
- **Everyone who could reach it loses it until it is undone.** The grants themselves survive
  the delete, which is why `undo_delete` brings the folder back shared as it was. Do
  not re-share after an undo: the access never went away, and a second share mints grants
  nobody asked for.

## When it refuses

| What you see | What it means | What to do |
|---|---|---|
| `not permitted: N items here can't be deleted with your access — …` | Deleting needs **approver** on every item it would remove, including items you cannot read. You are not an approver of all of them. Deletion is all-or-nothing on purpose — a partial delete is the worst outcome available. | Stop and report which items blocked it. The named ones are ones you can read; the rest are counted, not named, so there is no way to find out what they are. An approver of all of it can delete it. Look for no other route: the refusal is the answer. |
| `deleting the whole folder needs confirm_delete_folder set to exactly "…"` | A bare folder name was passed without the confirmation field. | Pass `confirm_delete_folder` with that exact name if a whole-folder delete is what the person wants; otherwise name the file or directory inside it. |
| `this folder changed since that confirmation was issued` | Someone wrote to the folder between your preview and your confirm, so the numbers the person approved are stale. | Re-preview, show the person what changed, ask again. Do not re-confirm on the old answer. |
| `that confirmation has expired` | More than ten minutes passed. | Re-preview. If the delay was because the person is still deciding, that is the system working. |

## Undoing a delete, and the one that cannot be undone

A delete can be undone. `undo_delete` with the same `location` restores exactly what
that one delete removed, at the version it had, with its sharing intact — except a folder's
connector, which stays disconnected. When you undo a folder delete whose preview named a
connector, say that the sync did not come back. Offer it straight
away when a delete turns out to be a mistake. Undoing twice is harmless: the second call finds
nothing left to restore and says so. A document that was deleted before it ever had content
cannot be restored, and is reported separately rather than brought back empty.

Nothing lists past deletes, so keep the delete's reply — its location and commit — in your
answer. That is what makes a later undo easy to aim.

## Erasing, for an erasure request

`erase_org_doc` is different: it destroys content, every past version, comments and the name,
and nothing brings it back, `undo_delete` included. Use it only for a genuine erasure
request — someone asking that their data be removed — and prefer `delete_org_doc` for tidying.

It takes the same two calls, for a stronger reason:

1. `erase_org_doc` with `location` (or `node`) and no `confirm_token`. Nothing is erased.
   The answer lists what would stop existing — how many nodes, how many of them documents —
   and, under LEFT BEHIND, anything you are not an approver of. Erasing needs approver, and
   unlike a delete it does not refuse the whole set: what you approve is erased and the rest
   is left and reported, so a folder can come back partly done.
2. Show the person that list and say plainly what the erase does and does not do:
   - the content, every version, the comments and the names leave the live service at once,
     and nothing in the service brings them back;
   - anything under LEFT BEHIND survives, and someone who approves it has to erase it;
   - two records survive, on purpose, because an erasure has to be provable afterwards: the
     audit record says something was erased, where it was, by whom and when, but not what it
     said; and one row per erased item notes that something of that kind existed and who
     owned it, with neither its name nor its path;
   - backups are the caveat on "gone": erased content can sit in a backup that has not rotated
     out for up to about ninety days, and restoring one after a failure would bring it back;
   - copies outside this store — the repository or Drive folder a mirror syncs from,
     anything someone exported — are untouched, so an erasure request has to reach those
     too.
3. Only on their explicit yes, call again with the `confirm_token`. It lasts ten minutes and
   is bound to the previewed set; if anything under it changed, the erase is refused and you
   preview again.

`⚠ refused: legal_hold` means someone placed a legal hold over it, and nothing was erased.
That is deliberate: a hold exists so data under investigation cannot be destroyed. Say so and
who can release it (whoever placed it); do not look for a way around it.

You also cannot delete `.permissions.json`, and you cannot delete a file a connector
mirrors — that content is a mirror, and the next sync would bring it back anyway.
Change it at the source.
