#!/usr/bin/env python3
"""Validate agentleFS plugin packaging stays aligned across Claude Code, Codex, and Cursor.

Run from anywhere:
  python3 plugins/agentlefs/scripts/validate_plugin_packaging.py
Exit 0 on success; print differences and exit 1 on failure.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # plugins/agentlefs
REPO = ROOT.parents[1]  # repository root


def load(path: Path):
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def fail(message: str, errors: list[str]):
    errors.append(message)


def main() -> int:
    errors: list[str] = []
    claude = load(ROOT / ".claude-plugin" / "plugin.json")
    codex = load(ROOT / ".codex-plugin" / "plugin.json")
    cursor = load(ROOT / ".cursor-plugin" / "plugin.json")
    mcp = load(ROOT / ".mcp.json")
    claude_hooks = load(ROOT / "hooks" / "hooks.json")
    codex_hooks = load(ROOT / "hooks" / "codex-hooks.json")
    cursor_hooks = load(ROOT / "hooks" / "cursor-hooks.json")
    claude_market = load(REPO / ".claude-plugin" / "marketplace.json")
    cursor_market = load(REPO / ".cursor-plugin" / "marketplace.json")

    for label, manifest in (("claude", claude), ("codex", codex), ("cursor", cursor)):
        if manifest.get("name") != "agentlefs":
            fail(f"{label} plugin.json name must be agentlefs", errors)
    versions = {claude.get("version"), codex.get("version"), cursor.get("version")}
    if len(versions) != 1 or None in versions:
        fail(f"plugin versions diverge: claude={claude.get('version')} codex={codex.get('version')} cursor={cursor.get('version')}", errors)

    if "agentlefs" not in mcp.get("mcpServers", {}):
        fail(".mcp.json must declare mcpServers.agentlefs", errors)
    if cursor.get("mcpServers") != "./.mcp.json":
        fail('Cursor plugin.json must set mcpServers to "./.mcp.json" (Cursor auto-discovers mcp.json, not .mcp.json)', errors)
    if cursor.get("hooks") != "./hooks/cursor-hooks.json":
        fail('Cursor plugin.json must point hooks at "./hooks/cursor-hooks.json"', errors)
    if codex.get("hooks") != "./hooks/codex-hooks.json":
        fail('Codex plugin.json must point hooks at "./hooks/codex-hooks.json"', errors)

    # Claude vs Codex: same lifecycle events; only the mcp_tool server name differs.
    if set(claude_hooks.get("hooks", {})) != set(codex_hooks.get("hooks", {})):
        fail("Claude and Codex hooks.json event keys must match", errors)
    claude_dump = json.dumps(claude_hooks, sort_keys=True)
    codex_dump = json.dumps(codex_hooks, sort_keys=True).replace('"server": "agentlefs"', '"server": "plugin:agentlefs:agentlefs"')
    if claude_dump != codex_dump:
        fail("Claude and Codex hook files must match except mcp_tool server naming", errors)

    # Cursor uses camelCase events mapped from the Claude/Codex set (minus mcp_tool-only brief_me).
    expected_cursor = {
        "SessionStart": "sessionStart",
        "UserPromptSubmit": "beforeSubmitPrompt",
        "PostToolUse": "postToolUse",
        "Stop": "stop",
        "PreCompact": "preCompact",
        "SessionEnd": "sessionEnd",
        "SubagentStop": "subagentStop",
    }
    cursor_events = set(cursor_hooks.get("hooks", {}))
    missing = set(expected_cursor.values()) - cursor_events
    if missing:
        fail(f"cursor-hooks.json missing events: {sorted(missing)}", errors)
    if cursor_hooks.get("version") != 1:
        fail("cursor-hooks.json must set version: 1", errors)

    for event in cursor_events:
        for entry in cursor_hooks["hooks"][event]:
            command = entry.get("command", "")
            if "${CURSOR_PLUGIN_ROOT}" not in command:
                fail(f"Cursor hook {event} must use CURSOR_PLUGIN_ROOT: {command}", errors)
            if "mcp_tool" in entry or entry.get("type") == "mcp_tool":
                fail(f"Cursor hooks cannot use mcp_tool entries (host has no such hook type): {event}", errors)

    # Scripts referenced by every host must exist.
    for rel in ("scripts/memory_hooks.py", "scripts/project_hooks.py"):
        if not (ROOT / rel).is_file():
            fail(f"missing {rel}", errors)

    # Marketplaces list the same plugin source.
    for label, market in (("claude", claude_market), ("cursor", cursor_market)):
        plugins = market.get("plugins") or []
        if not any(p.get("name") == "agentlefs" for p in plugins):
            fail(f"{label} marketplace.json must list plugin agentlefs", errors)
        source = next((p.get("source") for p in plugins if p.get("name") == "agentlefs"), None)
        if source not in {"./plugins/agentlefs", "plugins/agentlefs"}:
            fail(f"{label} marketplace agentlefs source must be ./plugins/agentlefs (got {source!r})", errors)

    if "cursor" not in (claude.get("keywords") or []) or "cursor" not in (codex.get("keywords") or []) or "cursor" not in (cursor.get("keywords") or []):
        fail("all host manifests should keep the cursor keyword", errors)

    if errors:
        print("plugin packaging validation failed:")
        for item in errors:
            print(" -", item)
        return 1
    print("plugin packaging validation ok")
    print(f" version={claude.get('version')} hosts=claude,codex,cursor")
    return 0


if __name__ == "__main__":
    sys.exit(main())
