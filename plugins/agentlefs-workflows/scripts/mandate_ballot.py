#!/usr/bin/env python3
"""Format shared AFS/Mandate decision records. Python 3.9+, standard library only.

This is a local formatter: no network, credentials, writes, or acceptance operation.
prepare FILE --folder VERIFIED_FOLDER emits MCP argument objects. The caller must
verify the shared destination through AFS; this formatter cannot check access.
choose FILE OPTION emits a hash-bound choice
statement for a human's already explicit decision. Action ballots are deliberately
left to Mandate's human interface; this helper never constructs launch contracts.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

MAX_BYTES = 128 * 1024
SCHEMA = "mandate-decision/v1"


def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def dump(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def display(value):
    return value.replace("`", "\\`")


def text(value, maximum, field):
    if not isinstance(value, str) or not value.strip() or any(c in value for c in "\r\n\0"):
        raise ValueError(f"{field} must be nonempty single-line text")
    if len(value.encode("utf-16-le")) // 2 > maximum:
        raise ValueError(f"{field} is too long")
    normalized = value.strip().strip("\ufeff").strip()
    if not normalized:
        raise ValueError(f"{field} must be nonempty single-line text")
    return normalized


def normalize(value):
    if not isinstance(value, dict):
        raise ValueError("ballot must be a JSON object")
    allowed = {"schema", "id", "title", "context", "options", "preference", "idempotencyKey", "supersedes"}
    if set(value) - allowed:
        raise ValueError("unexpected ballot fields")
    if value.get("schema", SCHEMA) != SCHEMA:
        raise ValueError("unsupported ballot schema")
    key = value.get("idempotencyKey")
    if not isinstance(key, str) or not re.fullmatch(r"[A-Za-z0-9_.:-]{1,200}", key):
        raise ValueError("idempotencyKey must contain 1–200 letters, numbers, dots, colons, underscores or hyphens")
    decision_id = value.get("id", digest(key)[:32])
    if not isinstance(decision_id, str) or not re.fullmatch(r"[a-f0-9]{32}", decision_id):
        raise ValueError("id must be 32 lowercase hexadecimal characters")
    title = text(value.get("title"), 160, "title")
    context = text(value.get("context"), 2000, "context")
    options = value.get("options")
    if not isinstance(options, list) or not 2 <= len(options) <= 6:
        raise ValueError("ballot needs 2–6 options")
    normalized = []
    for option in options:
        if not isinstance(option, dict) or set(option) - {"id", "summary", "tradeoffs"}:
            raise ValueError("options need id, summary and tradeoffs; action ballots must be handled in Mandate")
        option_id = option.get("id")
        if not isinstance(option_id, str) or not re.fullmatch(r"[a-z][a-z0-9-]{0,40}", option_id):
            raise ValueError("option id must start with a lowercase letter and contain at most 41 letters, numbers or hyphens")
        normalized.append({"id": option_id, "summary": text(option.get("summary"), 500, "summary"), "tradeoffs": text(option.get("tradeoffs"), 800, "tradeoffs")})
    option_ids = {option["id"] for option in normalized}
    if len(option_ids) != len(normalized):
        raise ValueError("option ids must be distinct")
    preference = value.get("preference")
    if preference is not None and (not isinstance(preference, str) or preference not in option_ids):
        raise ValueError("preference must name an option, or be null")
    supersedes = value.get("supersedes")
    if supersedes is not None and (not isinstance(supersedes, str) or not re.fullmatch(r"[a-f0-9]{32}", supersedes) or supersedes == decision_id):
        raise ValueError("supersedes must name a different decision id")
    return {"schema": SCHEMA, "id": decision_id, "title": title, "context": context, "options": normalized, "preference": preference, "idempotencyKey": key, "supersedes": supersedes}


def hashes(ballot):
    """The existing mandate-decision-option/v1 and ballot/v1 line protocol."""
    option_hashes = {}
    lines = ["mandate-decision-ballot/v1", f'title: {ballot["title"]}', f'context: {ballot["context"]}', f'preference: {ballot["preference"] or "none"}', "options:"]
    for option in ballot["options"]:
        statement = "\n".join(["mandate-decision-option/v1", f'title: {ballot["title"]}', f'context: {ballot["context"]}', f'option: {option["id"]}', f'summary: {option["summary"]}', f'tradeoffs: {option["tradeoffs"]}'])
        option_hash = digest(statement)
        option_hashes[option["id"]] = option_hash
        lines.extend([f'- id: {option["id"]}', f'  summary: {option["summary"]}', f'  tradeoffs: {option["tradeoffs"]}', f'  statement: {option_hash}'])
    return digest("\n".join(lines)), option_hashes


def prepare(ballot, folder):
    if not folder or any(not part or part in (".", "..") or part.strip() != part or "\\" in part or "\0" in part for part in folder.split("/")):
        raise ValueError("folder must be a relative slash-separated decision folder")
    ballot_hash, _ = hashes(ballot)
    name = f'decision-{ballot["id"]}.md'
    location = f"{folder}/{name}"
    options = "\n\n".join(f'## Option `{o["id"]}`\n\n{display(o["summary"])}\n\nTradeoffs: {display(o["tradeoffs"])}' for o in ballot["options"])
    canonical = json.dumps(ballot, ensure_ascii=False, indent=2, allow_nan=False).replace("`", "\\u0060")
    content = (f'---\ntype: misc\ntitle: {dump(ballot["title"])}\nsummary: "Team approval request shared by the AgentleFS plugin and Mandate."\ntags: [mandate, decision, approval-request]\n---\n\n'
               f'# {display(ballot["title"])}\n\n{display(ballot["context"])}\n\n'
               f'Proposer preference (not acceptance): {ballot["preference"] or "none"}.\n\n{options}\n\n'
               f'```mandate-decision\n{canonical}\n```\n')
    proposal = {"schema": "mandate-decision-proposal/v1", "decisionId": ballot["id"], "ballotHash": ballot_hash}
    return {"ballot": ballot, "ballotHash": ballot_hash,
            "document": {"action": "document", "folder_path": folder.split("/"), "name": name, "content": content, "idempotency_key": f'mandate-doc-{ballot["id"]}'},
            "proposal": {"action": "propose", "location": location, "kind": "decision", "statement": dump(proposal), "evidence": [location], "idempotency_key": f'mandate-truth-{ballot["id"]}'}}


def choose(ballot, option_id):
    ballot_hash, option_hashes = hashes(ballot)
    if option_id not in option_hashes:
        raise ValueError("chosen option is not on this ballot")
    choice = {"schema": "mandate-decision-choice/v1", "decisionId": ballot["id"], "ballotHash": ballot_hash, "optionId": option_id, "statementHash": option_hashes[option_id]}
    return {"choice": choice, "statement": dump(choice), "idempotency_key": f'mandate-choice-{ballot["id"]}-{option_id}'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("prepare", "choose"))
    parser.add_argument("file", help="JSON ballot file, or - for stdin")
    parser.add_argument("option", nargs="?")
    parser.add_argument("--folder", help="verified existing shared decision folder; required for prepare")
    args = parser.parse_args()
    try:
        if args.file == "-":
            raw = sys.stdin.buffer.read(MAX_BYTES + 1)
        else:
            with Path(args.file).open("rb") as source:
                raw = source.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError("ballot input exceeds 128 KiB")
        ballot = normalize(json.loads(raw))
        if args.operation == "choose" and not args.option:
            raise ValueError("choose requires an option id")
        if args.operation == "prepare" and args.option:
            raise ValueError("prepare takes no option id")
        if args.operation == "prepare" and not args.folder:
            raise ValueError("prepare requires --folder naming the verified shared decision folder")
        result = prepare(ballot, args.folder) if args.operation == "prepare" else choose(ballot, args.option)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    except (OSError, ValueError, UnicodeError, TypeError) as error:
        parser.exit(2, f"Invalid decision record: {error}\n")


if __name__ == "__main__":
    main()
