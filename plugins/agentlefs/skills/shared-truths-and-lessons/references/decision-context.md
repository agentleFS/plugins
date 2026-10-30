# A readable decision record

Use this companion format when the user wants a decision and its explanation on the
native AFS Decisions page. It also works alongside a Mandate ballot. Native decision
truths do not require a ballot or Mandate. The document supplies the explanation;
the anchored truth supplies the authoritative proposed, accepted, contested or
superseded status. Explanation text alone never establishes approval.

For who is doing the work and its reported progress, use the separate
[execution report](decision-execution.md). Keep organizational origin, recording
client provenance and author-reported execution identity distinct; do not infer
execution status from the decision's acceptance.
For a selected approach explicitly handed off as bounded work, use the
[decision pickup workflow](decision-pickup.md); acceptance alone is not pickup.

## Destination and scope

Use the organization authenticated by the current AFS connection. Do not infer an
organization from the local repository, a browser tab or another environment, and
do not copy records between environments without authorization.

Prefer an existing authorized project document or decision folder close to the
work. The native Decisions page aggregates reachable decision truths across their
source folders, so a central `mandate/decisions` folder is optional. This does not
change access: a reader still needs access to each source. A request to record a
decision does not automatically authorize a new folder or wider sharing. Check for
an existing record first and retain its identity when updating it.

## Capture the story people need

- **Title:** a short, specific choice, such as “Reuse the payment idempotency key”.
- **Question:** the problem the choice answers. Keep this separate from a person's
  actual question in the discussion.
- **Summary:** one or two sentences explaining the outcome and why it matters.
- **Decision:** the chosen approach, or the proposed approach if still pending.
- **Rationale:** the explicit reasons supported by the discussion or evidence.
- **Alternatives:** options actually considered, their tradeoffs, and, when known,
  why they were declined. Do not invent a comparison to fill this section.
- **Human questions:** selected relevant questions and clarifications, with answers
  only when recorded. Attribute actual speakers when known. Identify faithful
  paraphrases in the prose; do not present them as verbatim quotes.
- **Constraints:** requirements and limits that shaped the choice. Label assumptions.
- **Revisit when:** concrete changes or unresolved questions that could reopen it.
- **Decided by:** the actual human or delegated agent who made the choice. Omit for
  a pending choice or when unknown; an agent recommendation is not human approval.

Keep evidence links and dates in the surrounding Markdown and the truth's evidence
list. Record concise explicit rationale, not hidden chain-of-thought, private raw
transcripts, credentials or unrelated personal details. Missing information stays
missing: use empty arrays or omit optional fields, and say “not recorded” in prose
when useful. An unanswered question has no `answer` field.

## Document template

Prefer one logical decision per document when creating a new structured record.
Keep the explanation readable as ordinary Markdown and include exactly one
`decision-context` JSON fence for the UI. Existing ADR/spec conventions can remain;
add the companion fence when they describe one decision. A multi-decision source
can retain its prose without claiming one shared context block describes every truth.

The example below is fictional. Replace its content with supported facts; do not
save the example as a real decision. Match the destination's frontmatter conventions.

````markdown
---
title: Reuse the payment idempotency key
type: spec
tags: [decision, payments]
---

# Reuse the payment idempotency key

## Outcome

Use the same key when retrying a payment request. The accepted decision truth
anchored here records the choice; this explanation is not a separate approval.

## Why

Retries represent the same logical payment and must not create another charge.
Generating a fresh key for every attempt was considered and declined because it
would treat a retry as a new payment.

## Human questions

Paraphrased from the recorded discussion:

- Product owner: Can a timeout cause another charge?
- Payments engineer: Reusing the key lets the provider recognize the same request.

## Evidence and follow-up

Add the real source links, date, and conditions for revisiting here.

```decision-context
{
  "schema": "agentlefs-decision-context/v1",
  "title": "Reuse the payment idempotency key",
  "question": "How should retries avoid creating another charge?",
  "summary": "Retry the same logical payment with the same key to avoid duplicate charges.",
  "decision": "Reuse the original idempotency key for payment retries.",
  "rationale": [
    "A timeout does not establish that the original payment failed."
  ],
  "alternatives": [
    {
      "title": "Generate a fresh key for every attempt",
      "tradeoffs": "Each attempt is independent but may create another charge.",
      "whyNotChosen": "A retry must preserve the identity of the original payment."
    }
  ],
  "humanQuestions": [
    {
      "question": "Can a timeout cause another charge?",
      "answer": "Reusing the key lets the provider recognize the same request.",
      "askedBy": "Product owner",
      "answeredBy": "Payments engineer"
    }
  ],
  "constraints": ["A retry must represent the same logical payment."],
  "revisitWhen": ["The provider changes its idempotency guarantees."],
  "decidedBy": "Product owner"
}
```
````

`schema` is required. For a native record, `decision` must exactly match the
anchored truth's statement for the structured explanation to appear. For a ballot
companion, `ballotHash` must bind to the canonical ballot as described below.
Other strings are optional; the arrays may be empty. Each
alternative needs `title`; `tradeoffs` and `whyNotChosen` are optional. Each human
question needs `question`; `answer`, `askedBy` and `answeredBy` are optional. Do not
add a second context fence to revise the first: update the existing block with the
read document's `expected_commit`. Keep the prose and structured explanation aligned.

Keep `title` and `decidedBy` within 200 characters, alternative titles within 500,
speaker names within 200, and other strings within 4,000. Use at most 20 entries
per list, except human questions, which allows 30. Keep the block below 128 KiB
and its source document below 1 MiB so the UI can read the structured explanation.
These limits are ceilings, not a target length.

## Native truth and ballot handling

For a native decision, set `decision` to the exact plain-sentence statement of its
decision truth. The UI uses that match to keep one decision's explanation from being
attached to a different or superseded choice in the same document. After saving the
context, propose that statement anchored to the document, with durable evidence
references. Accept it only when the choice
has already been made within the user's authorized scope; leave an open choice
proposed. Return the document link and truth status. Do not edit the source just to
insert its new truth id afterward, which immediately changes its recorded version.

For a Mandate team ballot, this is a **separate companion fence** alongside the
canonical `mandate-decision` block. Do not put these fields inside the canonical
ballot, change the canonical hash protocol, or replace its hash-bound choice truth
with a plain accepted statement. A recommendation is not a selected option. Use
the Mandate ledger workflow to record an explicit choice against the exact ballot.
Set the companion's optional `ballotHash` to the canonical ballot hash returned by
the ballot helper. This binds its rationale and questions to that ballot version;
it never selects an option. If the canonical ballot changes, review the explanation
before updating that hash. A mismatched explanation is not rendered as context for
the changed ballot. The chosen approach always comes from a verified choice truth,
even if the companion's `decision` field recommends something else.

When recording a choice, preserve the distinction between contextual clarification
and a material change to the ballot. Adding an explanation does not grant approval
for changed options or scope. A changed source may appear as changed context on the
Decisions page; re-read the truth and document before explaining its current state.
