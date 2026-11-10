# agentleFS for Antigravity

agentleFS is a shared second brain for any AI with agent permissions. This plugin connects
Antigravity to your team's documents, decisions and projects in agentleFS, so the agent can
search them, read them and cite them, and it only ever sees what you are allowed to see.

## Install

```
agy plugin install https://github.com/agentleFS/plugins/tree/main/antigravity
```

Install this folder, not the repository root. The first agentleFS call opens your browser to sign
in; there is no key to paste. The server is the hosted endpoint, `https://mcp.agentlefs.com/mcp`.

## What it contains

- **The agentleFS MCP server** (`mcp_config.json`): search, read, browse, write and share tools.
  Every tool call goes to the agentleFS server with your sign-in, and every call is recorded in
  your organization's audit trail.
- **Skills** (`skills/`): how to find and cite documents, run projects, record decisions and
  lessons, share access, and recall what earlier sessions saved.

## Memory

Nothing is remembered unless you ask. The `memory` skill recalls what earlier sessions saved and
saves a summary only on request; to make that a habit, add a line such as "At the end of each
session, offer to save a summary to agentleFS." to your own `AGENTS.md`.

## Optional: agentleFS Workflows

This plugin runs nothing on your computer: no hooks, no scripts. The companion plugin in the
mirror's `antigravity-workflows/` folder adds hooks that name your repository and the skills that
can help, and the formatter the `mandate-ledger` skill uses for team ballots:

```
agy plugin install https://github.com/agentleFS/plugins/tree/main/antigravity-workflows
```

## Links

- Documentation: https://agentlefs.com/docs/connect
- Privacy: https://agentlefs.com/privacy
- Terms: https://agentlefs.com/terms
- Support: https://agentlefs.com/support

MIT licensed.
