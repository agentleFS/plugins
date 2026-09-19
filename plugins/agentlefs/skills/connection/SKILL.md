---
name: connection
description: How the agentleFS (afs) MCP connection authenticates, and how to diagnose it. Use when agentleFS tools are unavailable, return 401, 404, or auth errors; when the user asks how to connect, sign in, or authenticate to agentleFS; when a connection succeeds but returns no folders; when configuring a self-hosted endpoint; or when setting up headless/CI access. Also use before concluding that agentleFS is broken.
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
{"ok":true,"build":"<40-char commit sha>","vectorIndex":true,"paths":{"/mcp":"all"},"oauth":true}
```

`vectorIndex: true` means semantic search is available. Without it, `how="meaning"` degrades to text search rather than failing.

`build` names the deployed container — the commit sha it was built from, or the release name when one is set, and the literal `"unknown"` on a stack that was built without either (a local `docker compose` run, normally). It is the fact to quote when a deploy looks stale or when two clients disagree about what the server just did: the console answers the same field at `https://agentlefs.com/v1/health`, and the two services deploy separately, so they can legitimately name different builds for a few minutes and illegitimately for much longer (#840).

## The auth flow: OAuth with Dynamic Client Registration

There is **no token to mint, paste, or store**. The user signs in in a browser and the client registers itself.

Discovery chain:

1. Client sends an unauthenticated `POST /mcp`.
2. Server answers **HTTP 401** with `WWW-Authenticate: Bearer resource_metadata="…/.well-known/oauth-protected-resource"`.
3. Client fetches that `/.well-known/oauth-protected-resource` document on the MCP host.
4. That document points at Clerk as the authorization server, including its `registration_endpoint`.
5. Client registers dynamically at that endpoint, then runs the browser authorization flow.
6. The resulting access token is sent as a bearer on subsequent `POST /mcp` calls.

### The 401 is not an error

**That first 401 is the normal trigger for browser sign-in.** It is the mechanism, not a fault. Never report it as a bug, never start debugging it, and never conclude the server is broken because of it. You should only be concerned if 401s persist *after* a completed browser sign-in.

## Managing the connection in-session

Use the `/mcp` command in Claude Code to inspect status and authenticate. Select `agentlefs` and choose the authenticate option to launch the browser flow. The same command shows whether the server is connected and which tools it exposes.

## Self-hosted deployments

The endpoint is a literal `url` in the plugin's `.mcp.json`. Self-hosted deployments edit that one line, keeping the `/mcp` path. Nothing else needs changing; discovery is relative to whatever host is configured, so a self-hosted deployment advertises its own authorization server through its own `/.well-known/oauth-protected-resource`.

It is deliberately a literal rather than a templated value. Claude Code can interpolate `${user_config.…}` there, but no other agent does: Codex installs the same plugin and reads that string verbatim, producing a server that can never connect and reports no error. A hardcoded URL is correct in every client.

## Signed in, and what that reaches

Everyone who signs in has at least one Organization: their personal one, if they have not created or joined another. A new personal account owns its Organization and reaches everything in it. What a sign-in does not bring is **grants** elsewhere. In a company Organization, a member reaches only what has been shared with them — except an organization admin, who owns the Organization's root and reaches all of it — and an agent token reaches only what it was granted. A credential with no grants authenticates fine and reaches nothing, which looks like a working connection returning an empty world — and is.

## Headless and CI fallback

For non-interactive contexts where no browser exists, there is a legacy agent-token path:

| Transport | How |
|---|---|
| HTTP | `Authorization: Bearer afs_…` |
| stdio | `AGENTLEFS_TOKEN` environment variable |

Use this only when genuinely headless. **The plugin's committed configuration ships no token**, and a `afs_` token must never be written into a committed file. Treat it as a secret supplied by the environment.

## Verifying a connection

Only a successful tool call proves a working connection. Call `list_org_folders` with no arguments. Completing the browser flow is not proof, and neither is a green status in `/mcp`.

## Symptom to cause

| Symptom | Cause | Fix |
|---|---|---|
| Single 401, then a browser opens | Normal DCR trigger | Nothing. Complete the sign-in. |
| 401 loop that never resolves | Browser flow abandoned, cookies blocked, or a stale registration | Re-run `/mcp` and authenticate again in a normal browser window |
| 401 in CI or a headless shell | No browser for the OAuth flow | Use the `afs_` token path above |
| 404 on every call | Pointed at the console host instead of the MCP host | Must be `https://mcp.agentlefs.com/mcp`. `https://agentlefs.com` is the human console and serves no MCP. |
| 404 on a self-hosted deployment | the `url` in `.mcp.json` is missing the `/mcp` path | The path matters, not just the host |
| Connected, zero folders | An empty Organization you own, "(nothing stored yet …)", or a credential with no grants, "(no folders you can reach …)" | Own it: `/agentlefs:connect` offers to make the first folder. No grants: ask a folder owner to share one |
| Connected, folder looks nearly empty | Content is gated from this principal | Expected. Denied is byte-identical to not-found. |
| `how="meaning"` silently searched by text | Deployment has no vector index | Check `vectorIndex` in `/healthz`. Degradation is intentional. |
| Tools are absent from `/mcp` entirely | Plugin not enabled, or the server is unreachable | Check plugin state, then `/healthz` |
| `registry_*` tools missing | Off unless the deployment sets `REGISTRY_TOOLS=on` | Expected. Never rely on them. |
| A read errored instead of returning fewer rows | Fail-closed: a truncated allow-set throws | Surface it. The system refused to under-report. |

## Never do this

- **Never call a console API endpoint from an agent context.** The console API (`apps/api/src/server.ts`) authenticates with a Clerk browser session JWT only. An OAuth or `afs_` credential gets 401 every time. For anything needing the cross-principal view, deep-link the human to `https://agentlefs.com`.
- Never diagnose "connected but empty" as a broken connection. It is an authorization outcome, and saying so correctly is the difference between a useful answer and a wasted hour.
- Never conclude the store is empty from an empty view. See the `authorization-model` skill.
