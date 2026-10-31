#!/usr/bin/env python3
"""Project hooks for agentleFS shared projects. Python 3.9+, standard library only.

No network call and no credential: anything that needs agentleFS goes through the agent's own MCP
connection (an `mcp_tool` hook, or the agent's next call). This script only reads what the host
hands it on stdin and the session's own transcript (docs/design/shared-projects.md, "Hooks").

  session-start  names the session's repository, so the agent can ask `brief_me` with `repo`
                 for the projects that cover it, and reminds it to run proactive-assembly when
                 the first task names no project.
  assemble       on UserPromptSubmit, when the prompt looks like an unnamed work ask (lost / UI /
                 bug / feature), infers an entry mode and injects a reminder to return a ranked,
                 cited context packet (suggestions only). Skips when a project is already named.
                 No network call; no mode picker.
  stop           a session or subagent that took a project thread's work on (`reply_comment`
                 with status=taken) and has not reported it (status=reported) is sent back once
                 to report before it stops. Else, when assembly/playbooks suggested write-back
                 and nothing durable was written, sends the agent back once with the guided
                 writeback-loop checklist (soft recipe; human may skip).
  nudge          a session that coordinates work through agentleFS without a project (it spawns
                 helpers, asks agents or people for work, or posts on a folder, twice or more, and
                 never starts one) is told once that the work could be a project. The same pass tips
                 once toward swarm-board when multi-agent spawn/ask traffic has no wait or room.

`--platform cursor` selects Cursor's output envelope (additional_context / followup_message);
the default remains Claude/Codex's hookSpecificOutput / decision block.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from decision_workflow import GUIDANCE as DECISION_GUIDANCE, PICKUP_GUIDANCE, pickup_candidate, candidate as decision_candidate, after_tool as decision_after_tool, observe as decision_observe

MAX_INPUT = 1024 * 1024
MAX_TRANSCRIPT = 64 * 1024 * 1024
PLATFORMS = ("claude", "cursor")

# Work-task verbs that often arrive without a project pointer (build-list #1 / F22 / VF-ask-assembly).
TASK_VERBS = re.compile(
    r"\b(implement|build|fix|add|ship|refactor|wire|migrate|prototype|create|finish|"
    r"complete|debug|patch|restore|harden|improve|polish|redesign)\b",
    re.I,
)
# Lost-in-project / vague UI phrasing (meet-them entry modes) — may lack a classic work verb.
LOST_ASK = re.compile(
    r"(?:"
    r"\bdon'?t\s+know\s+what\s+to\s+(?:change|work\s+on|do)\b"
    r"|\bnot\s+sure\s+what\s+to\s+(?:change|work\s+on|do)\b"
    r"|\bwhat\s+should\s+i\s+(?:work\s+on|change|do)\b"
    r"|\bwhere\s+(?:do|should)\s+i\s+start\b"
    r"|\blost\s+in\s+(?:the\s+)?(?:project|codebase|repo)\b"
    r"|\bno\s+idea\s+what\s+to\s+(?:change|work\s+on)\b"
    r")",
    re.I,
)
UI_ASK = re.compile(
    r"(?:"
    r"\b(?:ui|ux|interface|frontend)\b.{0,40}\b(?:suck|sucks|ugly|bad|awful|terrible|broken)\b"
    r"|\b(?:suck|sucks|ugly|bad|awful|terrible)\b.{0,40}\b(?:ui|ux|interface|frontend)\b"
    r"|\b(?:improve|polish|redesign|cleanup|clean\s+up)\b.{0,40}\b(?:ui|ux|interface|frontend)\b"
    r"|\b(?:ui|ux|interface|frontend)\b.{0,40}\b(?:improve|polish|redesign|cleanup|clean\s+up)\b"
    r")",
    re.I,
)
BUG_ASK = re.compile(
    r"\b(bug|fix|debug|crash|regress(?:ion)?|broken|failing|failure|error|patch|hotfix)\b",
    re.I,
)
FEATURE_ASK = re.compile(
    r"\b(implement|add|build|ship|feature|create|prototype|wire|migrate|finish|complete|"
    r"harden|refactor)\b",
    re.I,
)
# Already on the named continue-project / catch-up path — do not assemble again.
NAMED_PROJECT = re.compile(
    r"(?:"
    r"\bcontinue\s+projects/"
    r"|projects/[A-Za-z0-9._-]+"
    r"|\bin\s+(?:the\s+)?[\w./-]+\s+project\b"
    r"|\bon\s+(?:the\s+)?[\w./-]+\s+project\b"
    r"|/agentlefs:catch-up"
    r"|\bcatch\s+me\s+up\b"
    r"|\bcontinue\s+[\w./-]+/"
    r")",
    re.I,
)
ASSEMBLE_MARK = "proactive-assembly"
PLAYBOOKS_MARK = "entry-mode-playbooks"
WRITEBACK_MARK = "writeback-loop"
# Explicit human/agent skip strings — second stop also clears via stop_hook_active.
WRITEBACK_SKIP = re.compile(
    r"(?:"
    r"\bskip write-?back\b"
    r"|\bnothing durable\b"
    r"|\bdon'?t (?:save|record|write)\b"
    r"|\bdo not (?:save|record|write)\b"
    r")",
    re.I,
)
# Text the assembly skill / assemble hook leaves when write-back was in play.
# Deliberately stronger than bare skill names (SessionStart also names those).
ASSEMBLY_WRITEBACK_HINTS = (
    "Ask-conditioned context packet",
    "Suggested write-back",
    "suggested write-back",
    "write-back targets",
    "write-back checklist",
)


def normalize_repo(raw):
    """One spelling per repository: host/owner/name, lower case. Mirrors core normalizeRepo."""
    s = (raw or "").strip()
    if not s:
        return None
    s = re.sub(r"^[a-z][a-z0-9+.-]*://", "", s, flags=re.I)
    s = re.sub(r"^[^@/]+@", "", s)
    s = re.sub(r"^([^/:]+):(?!\d+/)", r"\1/", s)
    s = re.sub(r":\d+/", "/", s)
    s = re.sub(r"/+$", "", s)
    s = re.sub(r"\.git$", "", s, flags=re.I).lower()
    parts = [p for p in s.split("/") if p]
    if len(parts) == 2:
        return "github.com/" + parts[0] + "/" + parts[1]
    if len(parts) < 3 or "." not in parts[0]:
        return None
    return "/".join(parts)


def read_input():
    data = sys.stdin.read(MAX_INPUT + 1)
    if len(data) > MAX_INPUT:
        return {}
    try:
        value = json.loads(data or "{}")
    except ValueError:
        return {}
    return value if isinstance(value, dict) else {}


def normalize_event(event):
    """Fill Cursor common fields into the keys the rest of this script reads."""
    if not isinstance(event, dict):
        return {}
    out = dict(event)
    if not out.get("cwd"):
        roots = out.get("workspace_roots")
        if isinstance(roots, list) and roots and isinstance(roots[0], str):
            out["cwd"] = roots[0]
        elif os.environ.get("CURSOR_PROJECT_DIR"):
            out["cwd"] = os.environ["CURSOR_PROJECT_DIR"]
    if not out.get("transcript_path") and os.environ.get("CURSOR_TRANSCRIPT_PATH"):
        out["transcript_path"] = os.environ["CURSOR_TRANSCRIPT_PATH"]
    # Cursor stop: loop_count > 0 means a prior followup already ran (same as stop_hook_active).
    if not out.get("stop_hook_active") and isinstance(out.get("loop_count"), int) and out["loop_count"] > 0:
        out["stop_hook_active"] = True
    if isinstance(out.get("tool_input"), str):
        try:
            parsed = json.loads(out["tool_input"])
        except ValueError:
            parsed = None
        if isinstance(parsed, dict):
            out["tool_input"] = parsed
    return out


def emit(value):
    sys.stdout.write(json.dumps(value))
    sys.stdout.flush()


def emit_context(text, event_name, platform):
    if platform == "cursor":
        emit({"additional_context": text})
    else:
        emit({
            "hookSpecificOutput": {
                "hookEventName": event_name,
                "additionalContext": text,
            }
        })


def emit_followup(reason, platform):
    if platform == "cursor":
        # Native Cursor stop / subagentStop follow-up (cursor.com/docs/hooks).
        emit({"followup_message": reason})
    else:
        emit({"decision": "block", "reason": reason})


def session_start(event, platform="claude"):
    cwd = event.get("cwd") or os.getcwd()
    parts = []
    try:
        out = subprocess.run(["git", "-C", cwd, "remote", "get-url", "origin"], capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        out = None
    repo = normalize_repo(out.stdout) if out is not None and out.returncode == 0 else None
    if repo:
        parts.append(
            "This session's repository is " + repo + ". If an agentleFS project covers it, call brief_me with "
            "repo set to " + repo + " to read the project's brief (its folder's AGENTS.md) and its open work before you start."
        )
    parts.append(
        "If the first task names no agentleFS project or folder, follow the " + ASSEMBLE_MARK
        + " skill before coding: infer entry mode (lost/ui/bug/feature), load "
        + PLAYBOOKS_MARK + " for that mode, return one ranked cited "
        "context packet (suggestions only; human filters)."
    )
    parts.append("Read pending team ballots in the existing brief_me briefing; do not duplicate them. " + DECISION_GUIDANCE)
    emit_context(
        " ".join(parts),
        event.get("hook_event_name") or "SessionStart",
        platform,
    )


def prompt_text(event):
    for key in ("prompt", "user_prompt", "content", "text"):
        value = event.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return ""


def looks_like_unnamed_task(prompt):
    """True when the prompt is a work ask and does not already name a project/folder."""
    if not isinstance(prompt, str) or len(prompt.strip()) < 12:
        return False
    if NAMED_PROJECT.search(prompt):
        return False
    return bool(TASK_VERBS.search(prompt) or LOST_ASK.search(prompt) or UI_ASK.search(prompt))


def infer_entry_mode(prompt):
    """Soft heuristic for lost / ui / bug / feature — never a user-facing picker.

    Order matches meet-them / four-features §3: lost and vague UI before generic bug/feature
    verbs. Ambiguous prompts default to feature when a work verb is present, else bug only
    when bug language is present.
    """
    if not isinstance(prompt, str):
        return "feature"
    if LOST_ASK.search(prompt):
        return "lost"
    if UI_ASK.search(prompt) and not BUG_ASK.search(prompt):
        return "ui"
    if BUG_ASK.search(prompt) and not FEATURE_ASK.search(prompt):
        return "bug"
    if BUG_ASK.search(prompt) and re.search(r"\b(bug|crash|regress(?:ion)?|hotfix)\b", prompt, re.I):
        return "bug"
    if FEATURE_ASK.search(prompt) or TASK_VERBS.search(prompt):
        return "feature"
    if UI_ASK.search(prompt):
        return "ui"
    return "feature"


def assemble(event, platform="claude"):
    """Remind the agent to return an ask-conditioned context packet on an unnamed work ask.

    No network: only pattern-match the prompt the host handed us. Infers a soft entry mode
    (lost/ui/bug/feature) for the skill's packet recipe — never a mode wizard. Cursor's
    beforeSubmitPrompt cannot inject context, so hosts that cannot inject should not wire
    this command.
    """
    prompt = prompt_text(event)
    decision_tip = ""
    if pickup_candidate(prompt):
        decision_observe("pickup_candidate_hint", "unconfirmed")
        emit_context(PICKUP_GUIDANCE, event.get("hook_event_name") or "UserPromptSubmit", platform)
        return  # A continuation of an existing decision, not a new unnamed project.
    elif decision_candidate(prompt):
        decision_observe("candidate_hint", "unconfirmed")
        decision_tip = DECISION_GUIDANCE + " "
    if not looks_like_unnamed_task(prompt):
        if decision_tip:
            emit_context(decision_tip, event.get("hook_event_name") or "UserPromptSubmit", platform)
        return
    mode = infer_entry_mode(prompt)
    emit_context(
        decision_tip + "This prompt names no agentleFS project. Before coding, run " + ASSEMBLE_MARK
        + " in mode `" + mode + "` (soft guess — override if wrong; no picker): load "
        + PLAYBOOKS_MARK + " for that mode (assemble steps, caps, write-back checklist, "
        "done-when; skippable), then return one ranked, cited, permission-bound context "
        "packet — projects/folders, docs/decisions, open asks/waits, suggested write-back "
        "targets. Caps: search limit ≤8, ≤5 doc citations, ≤3 projects, ≤3 open asks; "
        "optional brief_me once. Suggestions only — cite paths; let the human filter. "
        "If a matched folder/doc has another identity's open claim, append one overlap "
        "suggestion line (browse claims with that location; suggestion only, never a block). "
        "Skip further assembly once a project is confirmed. The " + ASSEMBLE_MARK
        + " skill has the packet shape; " + PLAYBOOKS_MARK + " has the mode recipe.",
        event.get("hook_event_name") or "UserPromptSubmit",
        platform,
    )


def tool_calls(line):
    """Every (name, arguments) a transcript line records, in Claude Code's or Codex's shape."""
    try:
        entry = json.loads(line)
    except ValueError:
        return
    stack = [entry]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            name = node.get("name")
            args = node.get("input", node.get("arguments"))
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except ValueError:
                    args = None
            if isinstance(name, str) and isinstance(args, dict):
                yield name, args
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)


def unreported(path):
    """Threads this transcript took on with status=taken and has not since reported."""
    if not path or not os.path.isfile(path) or os.path.getsize(path) > MAX_TRANSCRIPT:
        return []
    open_threads = {}
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            for name, args in tool_calls(line):
                # The plugin's server under any host's prefix: mcp__plugin_agentlefs_agentlefs__message_write,
                # mcp__agentlefs__message_write, MCP:message_write, or the bare tool name.
                if not is_tool(name, "message_write"):
                    continue
                if args.get("action") != "reply_comment" or not isinstance(args.get("thread"), str):
                    continue
                if args.get("status") == "taken":
                    open_threads[args["thread"]] = True
                elif args.get("status") == "reported":
                    open_threads.pop(args["thread"], None)
    return list(open_threads)


def is_durable_write(name, args):
    """True when this tool call is a durable write-back onto the meet-them substrate."""
    if is_tool(name, "doc_create") or is_tool(name, "doc_update"):
        return True
    if is_tool(name, "knowledge_write"):
        return True
    if is_tool(name, "coordination_write") and args.get("action") in (
        "propose",
        "decide",
        "contest",
        "settle",
    ):
        return True
    if is_tool(name, "message_write"):
        action = args.get("action")
        if action in ("comment",):
            return True
        if action == "send" and args.get("kind") in (
            "finding",
            "request",
            "handoff",
            "commitment",
            "answer",
        ):
            return True
        if action == "reply_comment" and args.get("status") == "reported":
            return True
    return False


def needs_guided_writeback(path):
    """True when assembly/playbooks suggested write-back and nothing durable was written.

    No network: transcript text + tool calls only. Explicit skip phrases clear it; the Stop
    hook also clears on the second stop via stop_hook_active.
    """
    if not path or not os.path.isfile(path) or os.path.getsize(path) > MAX_TRANSCRIPT:
        return False
    saw_assembly = False
    wrote = False
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if WRITEBACK_SKIP.search(line):
                return False
            # Already told once this session (follow-up reason or skill name in chat).
            if WRITEBACK_MARK in line and ("Before stopping" in line or "guided write-back" in line):
                return False
            if any(hint in line for hint in ASSEMBLY_WRITEBACK_HINTS):
                saw_assembly = True
            for name, args in tool_calls(line):
                if is_durable_write(name, args):
                    wrote = True
                if is_tool(name, "search") or is_tool(name, "brief_me"):
                    # Assembly tools alone are weak; require a write-back hint elsewhere,
                    # unless the assemble hook / skill already left a marker on this line set.
                    pass
    return saw_assembly and not wrote


# Calls that coordinate work between agents or people: what a project is for.
COORDINATING = (
    lambda name, args: tool_suffix(name) == "identity_write" and args.get("action") == "spawn",
    lambda name, args: tool_suffix(name) == "message_write" and args.get("action") == "send" and args.get("kind") in ("request", "handoff", "commitment"),
    lambda name, args: tool_suffix(name) == "message_write" and args.get("action") == "comment",
)
NUDGE_MARK = "could be run as an agentleFS project"
# Multi-agent board (F23): spawn or ask/handoff without wait/room — tip swarm-board once.
BOARD_MARK = "swarm-board"
BOARD_KINDS = ("question", "request", "handoff", "commitment")


def tool_suffix(name):
    """Bare tool name after Claude mcp__…__, Cursor MCP:, or a plain name."""
    if not isinstance(name, str):
        return ""
    if name.startswith("MCP:"):
        return name[4:]
    if "__" in name:
        return name.rsplit("__", 1)[-1]
    return name


def is_tool(name, tool):
    return tool_suffix(name) == tool


PROJECT_ACTIONS = ("start_project", "end_project", "route_project")


def is_board_coordinating(name, args):
    """Spawn or a typed ask/handoff — the multi-agent traffic swarm-board covers."""
    if is_tool(name, "identity_write") and args.get("action") == "spawn":
        return True
    return (
        is_tool(name, "message_write")
        and args.get("action") == "send"
        and args.get("kind") in BOARD_KINDS
    )


def is_board_primitive(name, args):
    """A wait or room already on the board — no swarm-board tip needed."""
    if is_tool(name, "message_write"):
        if args.get("action") == "send" and args.get("wait") is True:
            return True
        if args.get("action") in ("create_room", "join", "invite"):
            return True
    if is_tool(name, "coordination_write") and args.get("action") == "wait_for":
        return True
    if is_tool(name, "read") and args.get("action") == "wait":
        return True
    return False


def scan_nudge_transcript(path):
    """One pass: project-nudge and board-nudge facts from the transcript."""
    project_told = False
    board_told = False
    has_project = False
    has_board_primitive = False
    coordinating = 0
    board_coordinating = 0
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if NUDGE_MARK in line:
                project_told = True
            if BOARD_MARK in line:
                board_told = True
            for tool, targs in tool_calls(line):
                if is_tool(tool, "coordination_write") and targs.get("action") in PROJECT_ACTIONS:
                    has_project = True
                if is_board_primitive(tool, targs):
                    has_board_primitive = True
                if any(c(tool, targs) for c in COORDINATING):
                    coordinating += 1
                if is_board_coordinating(tool, targs):
                    board_coordinating += 1
    return {
        "project_told": project_told,
        "board_told": board_told,
        "has_project": has_project,
        "has_board_primitive": has_board_primitive,
        "coordinating": coordinating,
        "board_coordinating": board_coordinating,
    }


def nudge(event, platform="claude"):
    decision_tip = decision_after_tool(event)
    if decision_tip:
        emit_context(decision_tip, event.get("hook_event_name") or "PostToolUse", platform)
        return
    name = event.get("tool_name") or ""
    args = event.get("tool_input") if isinstance(event.get("tool_input"), dict) else {}
    if not (is_tool(name, "message_write") or is_tool(name, "identity_write")):
        return
    current_coords = any(c(name, args) for c in COORDINATING)
    current_board = is_board_coordinating(name, args)
    if not current_coords and not current_board:
        return
    path = event.get("agent_transcript_path") or event.get("transcript_path")
    if not path or not os.path.isfile(path) or os.path.getsize(path) > MAX_TRANSCRIPT:
        return
    scan = scan_nudge_transcript(path)
    # Current call may not be in the transcript yet.
    coordinating = scan["coordinating"] + (1 if current_coords else 0)
    board_coordinating = scan["board_coordinating"] + (1 if current_board else 0)
    if current_board and is_board_primitive(name, args):
        scan["has_board_primitive"] = True

    parts = []
    # Board tip first (F23): multi-agent traffic without wait/room — soft recipe, once.
    if (
        current_board
        and not scan["board_told"]
        and not scan["has_board_primitive"]
        and board_coordinating >= 2
        and not (current_board and args.get("wait") is True)
    ):
        parts.append(
            "This session is coordinating agents without a wait or room on the board. Follow the "
            + BOARD_MARK
            + " skill: send asks with wait=true and a continuation (even under cron — next brief_me "
            "sees what resolved), use handoff/commitment for work transfer, and create_room when "
            "chains differ. Do not rebuild the board in chat or prose task docs."
        )
    if (
        current_coords
        and not scan["project_told"]
        and not scan["has_project"]
        and coordinating >= 2
    ):
        parts.append(
            "This work " + NUDGE_MARK + ": it is coordinating helpers or other people through agentleFS. If it will "
            "continue across sessions or people, coordination_write with action start_project on its folder marks the folder a "
            "project, with a brief in its AGENTS.md, briefings for everyone following it, and its work tracked by "
            "state. Ask your person before starting one; the projects skill says how."
        )
    if not parts:
        return
    emit_context(
        " ".join(parts),
        event.get("hook_event_name") or "PostToolUse",
        platform,
    )


def stop(event, platform="claude"):
    # Sent back once: a second stop in a row is the agent's answer, and blocking again would loop.
    if event.get("stop_hook_active"):
        return
    path = event.get("agent_transcript_path") or event.get("transcript_path")
    threads = unreported(path)
    if threads:
        emit_followup(
            "You took on agentleFS project work and have not reported it: thread "
            + ", ".join(threads)
            + ". Before stopping, reply on each with message_write action=reply_comment, status=reported and "
            "link set to what you made (or say plainly that it is unfinished, and why), so the people and agents "
            "following the project see it.",
            platform,
        )
        return
    if not needs_guided_writeback(path):
        return
    emit_followup(
        "Before stopping, run guided write-back (" + WRITEBACK_MARK + " skill): commit any durable "
        "finding, plan, comment, or decision to the packet's suggested write-back targets (or an "
        "agreed folder) via doc_create/doc_update, message_write, or a truth — soft checklist, not a "
        "wizard. For decision work, reconcile the pending ballot or accepted source and report actual "
        "progress/blockers; only mark completed with evidence for the authorized scope. "
        "Prefer documents/comments/messages humans already edit. If nothing durable or the "
        "human said skip write-back, say so plainly and stop. Caps: 1–2 targets; no transcript dump.",
        platform,
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("session-start", "assemble", "stop", "nudge"))
    parser.add_argument("--platform", choices=PLATFORMS, default="claude",
                        help="Host output envelope: claude or cursor.")
    args = parser.parse_args(argv)
    event = normalize_event(read_input())
    try:
        if args.command == "session-start":
            session_start(event, args.platform)
        elif args.command == "assemble":
            assemble(event, args.platform)
        elif args.command == "stop":
            stop(event, args.platform)
        elif args.command == "nudge":
            nudge(event, args.platform)
    except Exception:  # A hook must never break the session it runs in.
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
