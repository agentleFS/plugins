"""Advisory decision hooks. No network, credentials, acceptance or execution side effects."""
import json
import os
from pathlib import Path
import re
from datetime import datetime, timezone

# Hook text describes and suggests; it never tells the model to skip asking the user or to act
# without the user's request (plugins/CLAUDE.md, "Hook output").
PICKUP_GUIDANCE = (
    "This concerns a recorded agentleFS decision. If the user wants you to act on it, the mandate-ledger "
    "skill can read the existing ballot, its accepted choice and its execution report (readyForPickup, "
    "state) so the work follows the recorded decision; do not create another ballot or infer an option "
    "from agreement alone. Whether to start, and how far to go, is the user's call; if that is unclear, "
    "ask them. Honor overlapping claims, opt-outs and real blockers, and report the actual status. "
    "Acceptance alone does not authorize work."
)

GUIDANCE = (
    "For a substantive team choice (product, architecture, rollout, pricing, policy), the "
    "mandate-ledger skill can help, and a pending ballot may already cover it, so reuse one rather "
    "than duplicating it. If the user wants the team to weigh in, offer to record a ballot, and record "
    "one only when they agree, in a destination they choose, without broadening access. Routine "
    "edits, personal suggestions and settled facts need no ballot. A pending proposal is not "
    "approval, and an accepted choice is not authorization to start work; when asked, report actual "
    "progress, blockers and completion evidence on the decision's source."
)


def pickup_candidate(prompt):
    """Continuation hint only; it neither determines the option nor authorizes work."""
    text = prompt[:16384].lower()
    if re.search(r"\b(?:don't|do not)\s+(?:start|implement|continue|pick\s+up|execute|launch|proceed|begin)\b|\b(?:not yet|hold off|stop|pause)\b", text):
        return False
    return bool(re.search(r"\bdecision\b.{0,40}\b(?:made|accepted|selected|approved|decided)\b", text)
                or re.search(r"\b(?:start|implement|continue|pick up)\b.{0,60}\b(?:decision|selected option|approved work)\b", text))


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
        # Private local state, never sent; Dev AFS rewrites this environment/default.
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
    if name in ("read", "browse") and args.get("action") in ("document", "truth", "truths"):
        response = event.get("tool_response", event.get("tool_output"))
        if isinstance(response, dict):
            response = json.dumps(response)
        if isinstance(response, str):
            # A bounded hint about a read, never proof of authority or a completed pickup.
            response = response[:1048576].replace('\\"', '"')
            if re.search(r'"readyForPickup"\s*:\s*true', response) or 'mandate-decision-choice/v1' in response:
                observe("pickup_hint", "unconfirmed")
                return PICKUP_GUIDANCE
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
