# GitHub issue ↔ AFS bridge

First-class **issue ↔ node** link beyond F14 file mirrors. State stays on the AFS tape; the issue gets only a **safe pointer**.

## Bind

```
sources_write action=bind_issue issue="https://github.com/owner/repo/issues/N" location="project/folder-or-doc"
```

Or `owner/repo#N`. Needs read on the folder/document. Returns `pointer_url` + `pointer_body`.

## Resolve both ways

```
browse action=github_issues issue="owner/repo#N"          # → node
browse action=github_issues location="project/folder"     # → issues
```

## Post the pointer (required after bind)

Never post ACL-gated prose or document bodies to GitHub.

Post **only** `pointer_body` on the issue — bare `/d/<id>` link, no titles, no document text, no summaries of grant-gated content. GitHub readers may be wider than AFS grants.

```bash
gh issue comment N --repo OWNER/REPO --body "$POINTER_BODY"
```

Or paste `pointer_body` in the GitHub UI. Do **not** auto-paste AFS prose onto public issues.

App auto-comment (`issues:write`) is deferred with connector deepen; until then agents/humans post the returned pointer.

## Unbind

```
sources_write action=unbind_issue issue="owner/repo#N"
```

## Out of scope

- Full issue ↔ AFS comment mirroring
- Dumping assembly packets or doc bodies onto GitHub
- Leaving GitHub as the workflow (meet-them: complement issues, don’t replace them)
