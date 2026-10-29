# Report work on a decision

A decision says what was chosen. An execution report says what someone reports
doing about it. Acceptance is not pickup, progress, completion or authorization
for a separate action. Use this companion only for work within the user's
authorized scope; it does not grant authority to execute a decision.

Keep three kinds of provenance distinct:

- The originating organization comes from the connected AFS organization and the
  API's organization identity. Do not infer it from a folder name or write a
  guessed organization into a companion block.
- The client or harness that **recorded** the decision comes from historical
  recording telemetry, when available and permitted. The current client is not
  evidence of which client made an older record.
- The harness and agent **executing** the work below are author-reported. Name
  the actual harness and agent when known; omit unknown values. Do not backfill
  them from the recording client, a claim owner or the decision's author.

No report means **“No execution recorded”**. It does not prove nobody picked up
the work. Do not fabricate a `not_started` report to fill an empty interface.

## Report meaningful changes

When maintaining an authorized execution report, explicitly record pickup and
material progress, a question or dependency being waited on, a blocker, and
completion when each occurs. Choose the state that the evidence supports:

| State | What the author is reporting |
| --- | --- |
| `not_started` | They explicitly confirm the work has not started. |
| `working` | The identified executor has picked up the work or made progress. |
| `waiting` | Work is waiting for an answer or dependency; summarize what is needed. |
| `blocked` | A blocker prevents progress; summarize the blocker. |
| `completed` | The defined work is complete, with at least one real output or verification reference. |
| `cancelled` | The work was explicitly cancelled; summarize why when known. |

Keep the summary factual: what changed, what is needed next, or what completed.
Use a real execution timestamp for `updatedAt`, not a fabricated historical date.
State is author-reported, not independently verified just because it parses or
appears on the page. Never infer a transition from truth acceptance, a claim or
release, a session ending, or an agent's turn finishing. A commit alone does not
establish deployment, and an open PR alone does not establish completion of work
that requires merge or deployment. Match the report to the actual scope.

## Companion example

Add exactly one `decision-execution` JSON fence to the existing source document,
separate from its `decision-context` and any canonical `mandate-decision` fence.
This example is fictional; replace every value with supported information and
omit optional fields that are unknown. The `decision` must exactly match the
native truth's statement.

```decision-execution
{
  "schema": "agentlefs-decision-execution/v1",
  "decision": "Reuse the original idempotency key for payment retries.",
  "state": "working",
  "harness": "Codex",
  "agent": "Payments implementation agent",
  "updatedAt": "2026-10-28T17:30:00.000Z",
  "summary": "Picked up the retry change; implementation is in progress.",
  "evidence": []
}
```

For a ballot, use `ballotHash` with the exact canonical hash returned by the ballot
helper in place of the native `decision` binding. Do not regenerate hashes from a
summary, put execution fields in the canonical ballot, or treat a hash as proof
of acceptance. An execution report must stay bound to the decision it describes.
Review a report before rebinding it to a replacement decision or ballot.

`schema`, a matching decision binding, `state` and a valid ISO datetime `updatedAt`
with a timezone are
required. `harness`, `agent`, `summary` and `runUrl` are optional. `runUrl`, when
known, must be an actual HTTP or HTTPS link to the run, not a guessed URL. Keep
`evidence` as a list of durable output or verification references. A `completed`
report needs at least one real reference, such as the actual delivered artifact,
merged change or relevant successful check. Do not use this example's text or
made-up evidence to satisfy that requirement.

Keep `harness` and `agent` within 200 characters, `runUrl` within 2,000, and
`decision`, `summary` and individual evidence references within 4,000. Use at most
20 evidence references. A ballot hash is exactly 64 lowercase hexadecimal
characters. Keep the execution block below 128 KiB and its source below 1 MiB.
The API labels a report as coming from the current document; do not insert an
API-generated `source` marker into the authored report.

## Safe update workflow

1. Read the current decision truth and source document. Check the existing report
   and its binding, status and source commit. Reconcile an existing report before
   creating one; do not add a second execution fence.
2. Confirm the factual transition, executor and supporting references from this
   work. Leave unknown history unrecorded. For `waiting` or `blocked`, capture a
   concise question, dependency or blocker in `summary`; sending someone a message
   still requires the user's authorization.
3. Use `doc_update` with `action: "edit"`, the source `location`, exact `old_string`
   and `new_string`, and the read document's `expected_commit`. Replace the existing
   execution block. To insert the first report, replace a unique existing block
   (for example, the complete decision-context fence) with that exact unchanged
   block followed by the execution fence. This guards the insertion and binding
   against concurrent changes. Do not combine `append` with `expected_commit`;
   that combination is unsupported.
   Preserve the rationale, human Q&A and canonical ballot bytes. On a conflict,
   re-read and reconcile; do not overwrite another executor's update.
4. Read back the report and confirm what was saved. If the write's outcome is
   unknown, read before retrying so the document does not gain duplicate blocks.

An execution update changes the source document's version. The Decisions page may
therefore mark the source as changed since the truth was recorded; that does not
mean the decision itself changed. Do not rewrite the rationale, re-accept or
supersede the truth just to remove that indicator or report progress. A genuinely
changed decision follows the ordinary truth or replacement-ballot workflow.
