#!/usr/bin/env python3
"""Project hooks for agentleFS shared projects. Python 3.9+, standard library only.

No network call and no credential: anything that needs agentleFS goes through the agent's own MCP
connection (an `mcp_tool` hook, or the agent's next call). This script only reads what the host
hands it on stdin and the session's own transcript (docs/design/shared-projects.md, "Hooks").

  session-start  names the session's repository, so the agent can ask `brief_me` with `repo`
                 for the projects that cover it.
  stop           a session or subagent that took a project thread's work on (`reply_comment`
                 with status=taken) and has not reported it (status=reported) is sent back once
                 to report before it stops.
  nudge          a session that coordinates work through agentleFS without a project (it spawns
                 helpers, asks agents or people for work, or posts on a folder, twice or more, and
                 never starts one) is told once that the work could be a project.
"""
import json
import os
import re
import subprocess
import sys

MAX_INPUT = 1024 * 1024
MAX_TRANSCRIPT = 64 * 1024 * 1024


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


def emit(value):
    sys.stdout.write(json.dumps(value))
    sys.stdout.flush()


def session_start(event):
    cwd = event.get("cwd") or os.getcwd()
    try:
        out = subprocess.run(["git", "-C", cwd, "remote", "get-url", "origin"], capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return
    repo = normalize_repo(out.stdout) if out.returncode == 0 else None
    if not repo:
        return
    emit({
        "hookSpecificOutput": {
            "hookEventName": event.get("hook_event_name") or "SessionStart",
            "additionalContext": (
                "This session's repository is " + repo + ". If an agentleFS project covers it, call brief_me with "
                "repo set to " + repo + " to read the project's brief (its folder's AGENTS.md) and its open work before you start."
            ),
        }
    })


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
                # mcp__agentlefs__message_write, or the bare tool name.
                if not (name == "message_write" or name.endswith("__message_write")):
                    continue
                if args.get("action") != "reply_comment" or not isinstance(args.get("thread"), str):
                    continue
                if args.get("status") == "taken":
                    open_threads[args["thread"]] = True
                elif args.get("status") == "reported":
                    open_threads.pop(args["thread"], None)
    return list(open_threads)


# Calls that coordinate work between agents or people: what a project is for.
COORDINATING = (
    lambda name, args: name.endswith("identity_write") and args.get("action") == "spawn",
    lambda name, args: name.endswith("message_write") and args.get("action") == "send" and args.get("kind") in ("request", "handoff", "commitment"),
    lambda name, args: name.endswith("message_write") and args.get("action") == "comment",
)
NUDGE_MARK = "could be run as an agentleFS project"


def is_tool(name, tool):
    return name == tool or name.endswith("__" + tool)


PROJECT_ACTIONS = ("start_project", "end_project", "route_project")


def nudge(event):
    name = event.get("tool_name") or ""
    args = event.get("tool_input") if isinstance(event.get("tool_input"), dict) else {}
    if not any(c(name, args) for c in COORDINATING) or not (is_tool(name, "message_write") or is_tool(name, "identity_write")):
        return
    path = event.get("agent_transcript_path") or event.get("transcript_path")
    if not path or not os.path.isfile(path) or os.path.getsize(path) > MAX_TRANSCRIPT:
        return
    count = 0
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            # Told once per session; and a session already using projects needs no telling.
            if NUDGE_MARK in line:
                return
            for tool, targs in tool_calls(line):
                if is_tool(tool, "coordination_write") and targs.get("action") in PROJECT_ACTIONS:
                    return
                if any(c(tool, targs) for c in COORDINATING):
                    count += 1
    # The current call may not be in the transcript yet; it counts either way.
    if count + 1 < 2:
        return
    emit({
        "hookSpecificOutput": {
            "hookEventName": event.get("hook_event_name") or "PostToolUse",
            "additionalContext": (
                "This work " + NUDGE_MARK + ": it is coordinating helpers or other people through agentleFS. If it will "
                "continue across sessions or people, coordination_write with action start_project on its folder marks the folder a "
                "project, with a brief in its AGENTS.md, briefings for everyone following it, and its work tracked by "
                "state. Ask your person before starting one; the projects skill says how."
            ),
        }
    })


def stop(event):
    # Sent back once: a second stop in a row is the agent's answer, and blocking again would loop.
    if event.get("stop_hook_active"):
        return
    path = event.get("agent_transcript_path") or event.get("transcript_path")
    threads = unreported(path)
    if not threads:
        return
    emit({
        "decision": "block",
        "reason": (
            "You took on agentleFS project work and have not reported it: thread "
            + ", ".join(threads)
            + ". Before stopping, reply on each with message_write action=reply_comment, status=reported and "
            "link set to what you made (or say plainly that it is unfinished, and why), so the people and agents "
            "following the project see it."
        ),
    })


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    event = read_input()
    try:
        if command == "session-start":
            session_start(event)
        elif command == "stop":
            stop(event)
        elif command == "nudge":
            nudge(event)
    except Exception:  # A hook must never break the session it runs in.
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
