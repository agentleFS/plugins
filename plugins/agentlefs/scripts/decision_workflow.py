"""Advisory decision hooks. No network, credentials, acceptance or execution side effects."""
import json
import os
from pathlib import Path
import re
from datetime import datetime, timezone

GUIDANCE = (
    "Use mandate-ledger for substantive team choices: reuse an existing ballot or file one pending "
    "ballot in the established shared destination before presenting alternatives or a recommendation. "
    "Unknown audience/destination: prepare and clarify, never broaden access. Respect opt-outs; "
    "routine edits, personal suggestions and settled facts need no new ballot. A pending proposal "
    "is not approval. Verify human choice and execution authorization separately; report actual "
    "progress, questions/blockers and completion evidence on the same decision source. "
    "Neither truth acceptance nor session exit proves work started or finished."
)


def candidate(prompt):
    """A bounded lexical hint, not a judgement of eligibility or skill selection."""
    text = prompt[:16384].lower()
    if re.search(r"(?:don't|do not|skip|without)\s+(?:\w+\s+){0,2}(?:filing|file|ballots?|decisions?)", text):
        return False
    explicit = re.search(r"\b(?:propose|create|file|make)\b.{0,60}\b(?:decision|ballot)\b", text)
    scope = re.search(r"\b(?:team|architecture|rollout|pricing|policy|product)\b", text)
    choice = re.search(r"\b(?:choose|compare|alternatives|recommend|should we|which approach)\b", text)
    return bool(explicit or (scope and choice))


def observe(observation, outcome):
    """Local, bounded metadata only. Never send host observations to the MCP server."""
    record = {"t": "afs-decision-hook", "source": "command_hook", "observation": observation,
              "outcome": outcome, "skill_application": "unknown",
              "at": datetime.now(timezone.utc).isoformat()}
    try:
        # Same private state boundary as memory; Dev AFS rewrites this environment/default.
        home = Path(os.environ.get("AGENTLEFS_MEMORY_HOME", "~/.agentlefs/plugin-memory")).expanduser()
        home.mkdir(parents=True, exist_ok=True, mode=0o700)
        path = home / "decision-observations.jsonl"
        # Diagnostics are best effort. Rotate at 256 KiB, retaining one prior file.
        if path.exists() and path.stat().st_size > 262144:
            path.replace(home / "decision-observations.previous.jsonl")
        fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(json.dumps(record) + "\n")
    except OSError:
        pass  # Diagnostics never prevent work.


def after_tool(event):
    name = (event.get("tool_name") or "").split("__")[-1].removeprefix("MCP:")
    args = event.get("tool_input")
    if not isinstance(args, dict):
        return None
    if name in ("Read", "read_file"):
        path = args.get("file_path", args.get("path", ""))
        if isinstance(path, str) and path.replace("\\", "/").endswith("/mandate-ledger/SKILL.md"):
            # Even PostToolUse does not prove the agent followed these instructions.
            observe("skill_file_read_attempt", "unconfirmed")
        return None
    if name == "coordination_write" and args.get("action") == "propose" and args.get("kind") == "decision":
        response = event.get("tool_response", event.get("tool_output"))
        if isinstance(response, str):
            try:
                response = json.loads(response)
            except ValueError:
                response = None
        response = response if isinstance(response, dict) else {}
        structured = response.get("structuredContent")
        structured = structured if isinstance(structured, dict) else {}
        truth = structured.get("truth")
        recorded = isinstance(truth, dict) and truth.get("kind") == "decision"
        outcome = "error" if response.get("isError") else "recorded" if recorded else "unconfirmed"
        observe("decision_proposal_result", outcome)
        return (
            "A decision proposal was attempted. Verify the returned truth and canonical source before "
            "calling it filed; reuse on retries. A pending ballot still needs a human choice. " + GUIDANCE
        )
    if name in ("doc_create", "doc_update"):
        for key in ("content", "new_string", "append"):
            content = args.get(key)
            if not isinstance(content, str):
                continue
            for match in re.finditer(r"```decision-execution\s*\n(.*?)\n```", content[:1048576], re.S):
                try:
                    report = json.loads(match.group(1))
                except ValueError:
                    continue
                if isinstance(report, dict) and report.get("schema") == "agentlefs-decision-execution/v1":
                    observe("execution_report_attempt", "unconfirmed")
                    return "Verify the execution report was stored. Its state is author-reported: completion requires evidence for the authorized scope, never just a session ending."
    return None
