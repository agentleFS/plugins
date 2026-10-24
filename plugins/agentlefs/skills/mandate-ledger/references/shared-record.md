# AFS shared decision record, version 1

The document contains exactly one block with this fence (the content is JSON,
not YAML). Keep human-readable context outside it. Use the same decision folder
in the plugin and Mandate's `MANDATE_DECISION_FOLDER` configuration.
Confirm that this folder already exists and the intended reviewers can read it
before filing. The conventional `mandate/decisions` path is not a default grant
or permission to create a workspace. The formatter requires an explicit
`--folder <verified-shared-folder>` for `prepare`; it cannot check existence or
sharing. Do not pass its generated `doc_create` arguments to AFS until the skill's
destination/access checks are complete.

```mandate-decision
{
  "schema": "mandate-decision/v1",
  "id": "0123456789abcdef0123456789abcdef",
  "title": "Choose a rollout scope",
  "context": "The team needs to decide the pilot scope.",
  "options": [
    {"id": "internal", "summary": "Internal pilot", "tradeoffs": "Narrower feedback"},
    {"id": "customer", "summary": "One customer pilot", "tradeoffs": "More coordination"}
  ],
  "preference": "internal",
  "idempotencyKey": "unique-key-for-this-logical-ballot",
  "supersedes": null
}
```

`id` is 32 lowercase hex characters. A UUID without hyphens is suitable. The
formatter derives an id from the idempotencyKey if omitted. `idempotencyKey` is
1–200 letters, digits, dots, colons, underscores or hyphens. Never reuse it for a
changed ballot. `supersedes` is null or another decision id. A replacement retires
the previous ballot; it does not approve the new choice.

Title/context are single-line text, at most 160/2000 UTF-16 code units. There are
2–6 options with unique ids starting with a lowercase letter followed by letters,
digits or hyphens, at most 41 characters. Summary/tradeoffs are single-line text,
at most 500/800 UTF-16 code units. `preference` is null or one option id; it is
never acceptance. The helper supports actionless ballots only. Preserve unfamiliar
launch-action data and use Mandate's human interface for those records.

Create a proposed truth of kind decision on the document. Its statement is JSON:

```json
{"schema":"mandate-decision-proposal/v1","decisionId":"0123456789abcdef0123456789abcdef"}
```

The formatter additionally supplies the computed `ballotHash`; Mandate validates
it when present. A document with no proposed decision truth is incomplete.

After explicit human selection, supersede that proposal truth with this JSON
statement (actual hashes come from the formatter, not the placeholders below):

```json
{"schema":"mandate-decision-choice/v1","decisionId":"0123456789abcdef0123456789abcdef","ballotHash":"<64 lowercase hex characters>","optionId":"internal","statementHash":"<64 lowercase hex characters>"}
```

AFS supersession produces an accepted successor truth anchored to the same
document. Mandate recomputes both hashes from the document before trusting the
choice. Editing canonical ballot content afterward invalidates the old choice.
An arbitrary accepted prose truth does not select an option. Malformed records,
missing truths, contested choices or hash mismatches cannot authorize execution.

The Python formatter outputs only data. Pass its `document` object to `doc_create`
and `proposal` object to `coordination_write` through the authenticated MCP tools.
For a choice, pass its `statement` and `idempotency_key` to `coordination_write`
with the original truth's id and `action: "supersede"`; include evidence yourself.
Never copy sample ids, preferences or choices into real work without establishing
what the human actually requested.
