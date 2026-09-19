---
name: deleting
description: How to delete something from agentleFS (afs) without destroying more than intended. Use whenever a deletion is on the table — removing a document, clearing out a directory, deleting a folder, cleaning up after a migration or a bad ingest — and before calling delete_org_doc for any reason. Also use to explain why a delete was refused, or why deletion needs two calls.
---

# Deleting from agentleFS

A delete is reversible from this session: `undo_delete` puts back exactly what one delete
removed, sharing included. `erase_org_doc` is the one that is not — it destroys content and
every past version, and nothing brings it back. Reversible still does not mean harmless: a
folder delete takes everything under it, including items you cannot see, and every agent
that relied on them loses them until someone notices.

So the rule for this skill is one sentence: **you find out what would be destroyed,
a human decides, and only then do you delete.**

## The tool makes you do it in two calls

`delete_org_doc` will not delete on a first call. Call it without
`confirm_token` and it deletes nothing — it returns what *would* go, plus a token:

```
⚠ NOT DELETED YET — this is what would happen.

Target: the entire folder engineering
Files removed: 240
  e.g. onboarding.md, runbooks/deploy.md, adr/0003-folders.md
  …and 232 more not listed here (beyond this sample, or owned by you without a read grant)
Connector: syncs from the GitHub repository acme/platform into engineering — deleting the folder stops that sync.

Reach grants survive a delete, and undo_delete restores the documents and their sharing — it is recoverable, not shredded. A connector is the one thing an undo does NOT bring back: reconnecting it is a decision, not a restoration.
```

This is not a formality to route around. It is the sentence that prevents the
mistake, and it is addressed to a person, not to you.

## What to do with it

1. **Call once without `confirm_token`.** Never guess a token, never reuse one from
   earlier in the conversation.
2. **Show the person what came back** — in your own words is fine, but the file
   count, the connector, and the "you cannot see" number must survive the retelling.
   Those three are the whole decision.
3. **Ask, and wait for an answer.** A real question with a real pause. "I'll go ahead
   unless you object" is not asking.
4. **Only then call again with the token.**

**Never spend a token the same person did not just approve.** If you were asked to
"clean up the old folders" and you are three deletes into a list, each one still gets
its own preview and its own answer. Bulk permission is the thing this skill exists to
prevent — the second delete is where the surprise lives.

If they say no, say what you did not delete and stop. Do not offer a narrower delete
unless they ask; the answer to "should this be gone" was no.

## Read the preview properly

- **The file count includes files you cannot see.** If the target holds content
  gated from you, the number is still the true number — the gate counts every file
  at HEAD. That is why a preview can say 240 when you can list 237.
- **The "not listed" number is not an alarm.** Owning a folder does not by itself
  grant you read access to what is in it, so the commonest caller — an admin who
  owns the folder — sees a small sample and a large remainder. That means "you own
  these and hold no read grant", not "these are hidden from you".
- **The sample is exact, never approximate.** Every path named is a path that will
  actually go. A file that merely shares the prefix — `reports-archive/` when you
  named `reports`, or `open.md.bak` when you named `open.md` — is not in the blast
  radius and will not appear.
- **A connector line changes the decision.** If the folder mirrors a GitHub repo or
  a Drive folder, deleting it here stops that sync. The upstream content survives;
  the organization's access to it through agentleFS does not. Say this out loud —
  people delete folders thinking they are tidying a copy. **An undo does not reconnect
  it**: `undo_delete` brings back the documents and their sharing, and the sync stays
  stopped until someone connects the source again.
- **Everyone who could reach it loses it until it is undone.** The grants themselves survive
  the delete, which is why `undo_delete` brings the folder back shared as it was. Do
  not re-share after an undo: the access never went away, and a second share mints grants
  nobody asked for.

## When it refuses

| What you see | What it means | What to do |
|---|---|---|
| `not permitted: N items here can't be deleted with your access — …` | Deleting needs **owner** on every item it would remove, including items you cannot see. You do not own all of them. Deletion is all-or-nothing on purpose — a partial delete is the worst outcome available. | Stop and report which items blocked it. The named ones are ones you can read; any remainder is counted, not named, and you cannot find out what they are. An owner of the folder deletes it, or grants ownership first. Do not look for another route. |
| `this folder changed since that confirmation was issued` | Someone wrote to the folder between your preview and your confirm, so the numbers the person approved are stale. | Re-preview, show the person what changed, ask again. Do not re-confirm on the old answer. |
| `that confirmation has expired` | More than ten minutes passed. | Re-preview. If the delay was because the person is still deciding, that is the system working. |

## Undoing a delete, and the one that cannot be undone

**A delete can be undone.** `undo_delete` with the same `location` restores exactly what
that one delete removed, at the version it had, with its sharing intact — except a folder's
connector, which stays disconnected. When you undo a folder delete whose preview named a
connector, say that the sync did not come back. Offer it straight
away when a delete turns out to be a mistake. Undoing twice is harmless: the second call finds
nothing left to restore and says so. A document that was deleted before it ever had content
cannot be restored, and is reported separately rather than brought back empty.

There is no tool that lists what was deleted, so **keep the delete's reply** — its location
and commit — in your answer. That is what makes a later undo easy to aim.

`erase_org_doc` is different: it destroys content, every past version, comments and the name,
and **nothing** brings it back, `undo_delete` included. Use it only for a genuine erasure
request, and prefer `delete_org_doc` for tidying.

You also cannot delete `.permissions.json`, and you cannot delete a file a connector
mirrors — that content is a mirror, and the next sync would bring it back anyway.
Change it at the source.
