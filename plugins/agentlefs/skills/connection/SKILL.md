---
name: connection
description: "How this client signs in to the agentleFS (afs) MCP server, and how to diagnose that connection. Use when agentleFS tools are unavailable, return 401, 404, or auth errors; when the user asks how to set up, sign in to, or authenticate this client with agentleFS; when the connection succeeds but returns no folders or reaches the wrong Organization or email; when configuring a self-hosted endpoint; or when setting up headless/CI access. Also use before concluding that agentleFS is broken. Syncing GitHub or Google Drive content into afs is the sources skill, not this one."
---

# agentleFS connection

## Endpoints

| What | URL |
|---|---|
| MCP server (production) | `https://mcp.agentlefs.com/mcp` |
| Health check | `https://mcp.agentlefs.com/healthz` |
| Console (humans only) | `https://agentlefs.com` |
| Authorization server | `https://clerk.agentlefs.com` |

Healthy `GET /healthz` returns:

```json
{"ok":true,"build":"<40-char commit sha>","vectorIndex":true,"oauth":true,"publicCorpus":true}
```

`vectorIndex: true` means semantic search is available. Without it, `how="meaning"` degrades to text search rather than failing.

`publicCorpus: true` means `search` scope `"public"` (the public GitHub corpus of skills and instruction files) can answer. `false` means every public search answers `not_connected` until the server is deployed with the corpus attached.

`build` names the deployed container — the commit sha it was built from, or the release name when one is set, and the literal `"unknown"` on a stack that was built without either (a local `docker compose` run, normally). It is the fact to quote when a deploy looks stale or when two clients disagree about what the server just did: the console answers the same field at `https://agentlefs.com/v1/health`, and the two services deploy separately, so they can name different builds for a few minutes after a release; a difference that lasts longer means one of them did not deploy.

## The auth flow: OAuth with Dynamic Client Registration

For the normal MCP connection, there is **no token to mint, paste, or store**. The user signs in in a browser and the client registers itself.

Discovery chain:

1. Client sends an unauthenticated `POST /mcp`.
2. Server answers **HTTP 401** with `WWW-Authenticate: Bearer resource_metadata="…/.well-known/oauth-protected-resource"`.
3. Client fetches that `/.well-known/oauth-protected-resource` document on the MCP host.
4. That document points at Clerk as the authorization server, including its `registration_endpoint`.
5. Client registers dynamically at that endpoint, then runs the browser authorization flow.
6. The resulting access token is sent as a bearer on subsequent `POST /mcp` calls.

### The 401 is not an error

That first 401 is the normal trigger for browser sign-in. It is the mechanism, not a fault, so it is not a bug to report or a reason to start debugging. 401s are worth investigating only when they persist *after* a completed browser sign-in.

## Managing the connection in-session

Prefer signing in from a real terminal **before** starting Claude Code, so the session loads an already-authenticated server:

```
claude mcp add --transport http --scope user agentlefs https://mcp.agentlefs.com/mcp
claude mcp login agentlefs
claude
```

`--no-browser` prints the authorization URL instead of opening one — use it over SSH, then paste the redirect URL back when prompted. Do not run `claude mcp login` from an agent tool call: it needs a TTY (`stdin isn't a terminal`).

Inside a session, `/mcp` still inspects status and can authenticate a server the session already loaded. A server added with `claude mcp add` while Claude Code is already running is invisible until restart — prefer the shell sequence above, or restart after a mid-session add.

## Self-hosted deployments

The endpoint is a literal `url` in the plugin's `.mcp.json`. Self-hosted deployments edit that one line, keeping the `/mcp` path. Nothing else needs changing; discovery is relative to whatever host is configured, so a self-hosted deployment advertises its own authorization server through its own `/.well-known/oauth-protected-resource`.

It is deliberately a literal rather than a templated value. Claude Code can interpolate `${user_config.…}` there, but no other agent does: Codex installs the same plugin and reads that string verbatim, producing a server that can never connect and reports no error. A hardcoded URL is correct in every client.

## Signed in, and what that reaches

Everyone who signs in has at least one Organization: their personal one, if they have not created or joined another. A new personal account is the manager of its Organization and reaches everything in it. What a sign-in does not bring is **grants** elsewhere. In a company Organization, a member reaches only what has been shared with them — except a manager of the Organization's root, who reaches all of it — and an agent reaches only its person's access, narrowed by its own scope. A credential with no grants authenticates fine and reaches nothing, which looks like a working connection returning an empty world — and is.

## Signing in with no browser (headless, CI, routines)

### Agents on a remote machine (a server, CI, a box with no browser)

The person signs the machine in once; no key is copied and nothing secret passes through a chat:

1. On the machine, the person runs `afs-run login` (optionally `--folder <path>`). It prints an address (the console's `/device`) and an eight-letter code.
2. In any browser where they are signed in to agentleFS, they open that address, type the code, check what is asking (the machine's name, the folder, where the request came from) and approve it for one folder. Only a person approves: no MCP tool can, an AI client included.
3. The machine stores its own rotating credential in a file only its user can read. From then on, `afs-run --agent @<handle> -- <command>` starts an agent that works in that folder with a short-lived token put only in the command's environment as `AGENTLEFS_TOKEN`, so an MCP configuration that sends that variable as its bearer token works with no long-lived key on disk. A headless worker connects through the stdio bridge `afs-run mcp --agent @<handle>`, here named `afs`, and is started with a shift's writes allowed, or its writes are refused with nobody there to approve them. Allow the five a shift makes (`seat_write`, `doc_create`, `doc_update`, `message_write`, `coordination_write`) and leave `doc_delete`, `access_grant`, `access_revoke` and `identity_write` asking: nobody is there to approve them, so a worker that meets an instruction planted in what it reads cannot erase or share anything on its own. Allow every agentleFS tool instead only if the person asks for that, saying it includes deletes, shares and agent administration.
   - Claude Code: `afs-run --agent @<handle> -- claude -p --strict-mcp-config --mcp-config '{"mcpServers":{"afs":{"command":"afs-run","args":["mcp","--agent","@<handle>"]}}}' --allowedTools 'mcp__afs__seat_write,mcp__afs__doc_create,mcp__afs__doc_update,mcp__afs__message_write,mcp__afs__coordination_write' -- "…"`. The last `--` ends the allow list. Every agentleFS tool, if asked: `--allowedTools 'mcp__afs__*'`.
   - Codex CLI: `afs-run --agent @<handle> -- codex exec -c 'mcp_servers.afs.command="afs-run"' -c 'mcp_servers.afs.args=["mcp","--agent","@<handle>"]' -c 'mcp_servers.afs.tools.seat_write.approval_mode="approve"' "…"`, with the same `-c` for `doc_create`, `doc_update`, `message_write` and `coordination_write`. Every agentleFS tool, if asked: `-c 'mcp_servers.afs.default_tools_approval_mode="approve"'` instead.
   - Cursor: put the same server in the folder's `.cursor/mcp.json` (`{"mcpServers":{"afs":{"command":"afs-run","args":["mcp","--agent","@<handle>"]}}}`) and `"Mcp(afs:seat_write)"`, `"Mcp(afs:doc_create)"`, `"Mcp(afs:doc_update)"`, `"Mcp(afs:message_write)"` and `"Mcp(afs:coordination_write)"` in `permissions.allow` of `~/.cursor/cli-config.json` (every agentleFS tool, if asked: `"Mcp(afs:*)"`), then `afs-run --agent @<handle> -- cursor-agent -p --approve-mcps --trust "…"`. Leave out `--force`, which allows every command, not only agentleFS's.

`afs-run status` says whether the machine is signed in; `afs-run logout`, or Revoke under **Machines** on the console's `/device` page, ends it, and its running agents stop at their next call. A machine lasts 90 days. The launcher is `bin/afs-run` in the agentlefs-workflows plugin, or `https://mcp.agentlefs.com/install/afs-run` checked against `/install/afs-run.sha256`. Never ask the person to paste a code, a key or a token into the conversation: the code is typed in their browser, and nothing else is needed.

### In GitHub Actions

A workflow signs in with no stored secret: the person trusts it on the folder's Access panel in the console (**Trust a GitHub Actions workflow**), the job gets `permissions: id-token: write`, and `AGENTLEFS_TRUST` names the trust (its id, not a secret). `afs-run --agent @<handle> -- <command>` in the job then exchanges the job's GitHub ID token for the agent's short-lived token.

### Agents and clients with no browser of their own

An agent that should be its own identity, with narrower access than its person, is added in the console (a folder's Access panel, **Add an agent**) or spawned with `identity_write action=spawn`. Neither answers a credential: the agent is started with the launcher (`afs-run --agent`) on a machine signed in for its folder, or driven with `acting_as`. No AI session is ever handed a key, the person's own included.

A client that only sends a static header (Cline, a generic HTTP client) is configured with the stdio command `afs-run mcp --agent @<handle>` instead of a URL and a token: it carries the agent's current token on every call, and nothing secret goes in its configuration.

agentleFS no longer accepts long-lived `afs_` keys (or the older `cht_` ones). A call with one answers 401 with how to sign in instead: `afs-run login` for a machine, Add an agent and `afs-run` for an agent, a trust (`AGENTLEFS_TRUST`) for GitHub Actions, and the agentleFS connector or OAuth for a person's client. Prefer OAuth wherever a browser exists. The plugin's committed configuration ships no token; keep it that way.

## Verifying a connection

Only a successful tool call proves a working connection. Call `browse` with `action: "folders"` and nothing else. Completing the browser flow is not proof, and neither is a green status in `/mcp`.

## Symptom to cause

| Symptom | Cause | Fix |
|---|---|---|
| Single 401, then a browser opens | Normal DCR trigger | Nothing. Complete the sign-in. |
| 401 loop that never resolves | Browser flow abandoned, cookies blocked, or a stale registration | Re-run `/mcp` and authenticate again in a normal browser window |
| 401 in CI or a headless shell | No browser for the OAuth flow | SSH with a person at the far end: `claude mcp login agentlefs --no-browser`, then paste the redirect URL back when prompted. Agents the machine starts on its own: sign the machine in once with `afs-run login` and start them with `afs-run --agent` (**Agents on a remote machine** above); a key is refused |
| 404 on every call | Pointed at the console host instead of the MCP host | Use `https://mcp.agentlefs.com/mcp`. `https://agentlefs.com` is the human console and serves no MCP. |
| 404 on a self-hosted deployment | the `url` in `.mcp.json` is missing the `/mcp` path | The path matters, not just the host |
| Connected, zero folders | An empty Organization you approve, "(nothing stored yet …)", or a credential with no grants, "(no folders you can reach …)" | Empty: `/agentlefs:connect` offers to make the first folder. No grants: `access_grant` with `action: "request"` for a folder the user can name, or ask a manager of the Organization |
| Connected, but the wrong account or Organization | Browser session is a different email, or the consent page's Organization was left at its default | See **Switching Organization or email** below. Same email, wrong Organization: clear the client's auth and re-authenticate, then pick the Organization on the consent page, Personal included. Wrong email: on the consent page click **Use another account**, sign in as the intended email, then finish Allow. |
| Connected, folder looks nearly empty | Content is gated from this principal | Expected. Denied reads exactly like not-found. |
| `how="meaning"` silently searched by text | Deployment has no vector index | Check `vectorIndex` in `/healthz`. Degradation is intentional. |
| Tools are absent from `/mcp` entirely | Plugin not enabled / not reloaded, `claude mcp add` ran mid-session, or the server is unreachable | Plugin: `/reload-plugins` (or restart below v2.1.268). Bare `mcp add` inside a session: restart Claude Code — a running session does not re-read MCP config. Then check `/healthz` |
| A read errored instead of returning fewer rows | Fail-closed: a truncated allow-set throws | Surface it. The system refused to under-report. |

## Switching Organization or email

A working connection can still be the wrong one: the wrong Organization under the same email, or a different email entirely. There is no error either way — `browse` just shows that principal's reach, which can look almost empty. The same steps live at https://agentlefs.com/docs/connect and in the plugin README.

**Organization (same email).** Clear the client's stored authentication and authenticate again. On the consent page (`/oauth-consent`), pick the Organization from its picker (`user:org:read`): Personal, then every Organization you belong to. It starts on the Organization active in the console.

**Email.** Clear the client's authentication and authenticate again. On the consent page, click **Use another account**, sign in as the intended email, then Allow. The instance stays single-session, so that button signs out and returns to the same consent URL (the #1267 fallback; multi-session stays off).

### Per client

| Client | Steps | Status |
|---|---|---|
| Claude Code | `/mcp` → agentlefs → Clear authentication → Authenticate | Verified (Fred, 2026-10-17) |
| Claude Desktop / Claude (web) | Disconnect the connector, then reconnect and complete the browser flow | Unverified |
| Codex CLI | Re-run `codex mcp login agentlefs` (for a stuck session, remove the server from Codex's MCP config and add it again) | Unverified |
| Codex app | Settings → MCP servers → remove or disconnect agentlefs, then Add server / Authenticate again | Unverified |
| Gemini CLI | `/mcp auth agentlefs` again — on consent, Use another account if the wrong email is shown | Unverified |
| ChatGPT (custom MCP) | Remove the custom MCP plugin, add the server again with OAuth, complete the browser flow | Unverified |
| Cursor | MCP settings → agentlefs → disconnect / clear auth, then re-authenticate | Unverified |

For an email switch, use **Use another account** on consent rather than signing out of the console first. After either switch, prove the new principal with `browse` action `folders` — only a successful tool call shows what you reached.

## Avoid

- Calling a console API endpoint from an agent context. The console API accepts only a browser session, so an OAuth or agent credential gets a 401 every time. For anything needing the cross-principal view, deep-link the person to `https://agentlefs.com`.
- Diagnosing "connected but empty" as a broken connection. It is an authorization outcome, and saying so correctly is the difference between a useful answer and a wasted hour.
- Concluding the store is empty from an empty view. See the `authorization-model` skill.
- Treating a nearly empty store as "no content" without checking whether this connection is the wrong Organization or email (row above).
