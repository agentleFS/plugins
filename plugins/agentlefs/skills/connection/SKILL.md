---
name: connection
description: How this client signs in to the agentleFS (afs) MCP server, and how to diagnose that connection. Use when agentleFS tools are unavailable, return 401, 404, or auth errors; when the user asks how to set up, sign in to, or authenticate this client with agentleFS; when the connection succeeds but returns no folders; when configuring a self-hosted endpoint; or when setting up headless/CI access. Also use before concluding that agentleFS is broken. Syncing GitHub or Google Drive content into afs is the sources skill, not this one.
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

`build` names the deployed container — the commit sha it was built from, or the release name when one is set, and the literal `"unknown"` on a stack that was built without either (a local `docker compose` run, normally). It is the fact to quote when a deploy looks stale or when two clients disagree about what the server just did: the console answers the same field at `https://agentlefs.com/v1/health`, and the two services deploy separately, so they can name different builds for a few minutes after a release; a difference that lasts longer means one of them did not deploy.

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

That first 401 is the normal trigger for browser sign-in. It is the mechanism, not a fault, so it is not a bug to report or a reason to start debugging. 401s are worth investigating only when they persist *after* a completed browser sign-in.

## Managing the connection in-session

Use the `/mcp` command in Claude Code to inspect status and authenticate. Select `agentlefs` and choose the authenticate option to launch the browser flow. The same command shows whether the server is connected and which tools it exposes.

## Self-hosted deployments

The endpoint is a literal `url` in the plugin's `.mcp.json`. Self-hosted deployments edit that one line, keeping the `/mcp` path. Nothing else needs changing; discovery is relative to whatever host is configured, so a self-hosted deployment advertises its own authorization server through its own `/.well-known/oauth-protected-resource`.

It is deliberately a literal rather than a templated value. Claude Code can interpolate `${user_config.…}` there, but no other agent does: Codex installs the same plugin and reads that string verbatim, producing a server that can never connect and reports no error. A hardcoded URL is correct in every client.

## Signed in, and what that reaches

Everyone who signs in has at least one Organization: their personal one, if they have not created or joined another. A new personal account is the approver of its Organization and reaches everything in it. What a sign-in does not bring is **grants** elsewhere. In a company Organization, a member reaches only what has been shared with them — except an approver of the Organization's root, who reaches all of it — and an agent reaches only its person's access, narrowed by its own scope. A credential with no grants authenticates fine and reaches nothing, which looks like a working connection returning an empty world — and is.

## Headless and CI fallback

For a headless agent that should be its own identity, with narrower access than the person running it, the person's session can create one with `identity` and `action: "spawn"`, passing `bootstrap_key: true` for a long-lived key bound to that child (the `collaborating` skill). It is shown once, and it stops working when the child is retired.

Otherwise, for non-interactive contexts where no browser exists, there is a legacy agent-token path:

| Transport | How |
|---|---|
| HTTP | `Authorization: Bearer afs_…` |
| stdio | `AGENTLEFS_TOKEN` environment variable |

Use this only when genuinely headless. The plugin's committed configuration ships no token. Keep an `afs_` token out of committed files and treat it as a secret supplied by the environment: anyone holding it acts as that agent.

## Verifying a connection

Only a successful tool call proves a working connection. Call `list_org_folders` with no arguments. Completing the browser flow is not proof, and neither is a green status in `/mcp`.

## Symptom to cause

| Symptom | Cause | Fix |
|---|---|---|
| Single 401, then a browser opens | Normal DCR trigger | Nothing. Complete the sign-in. |
| 401 loop that never resolves | Browser flow abandoned, cookies blocked, or a stale registration | Re-run `/mcp` and authenticate again in a normal browser window |
| 401 in CI or a headless shell | No browser for the OAuth flow | Use the `afs_` token path above |
| 404 on every call | Pointed at the console host instead of the MCP host | Use `https://mcp.agentlefs.com/mcp`. `https://agentlefs.com` is the human console and serves no MCP. |
| 404 on a self-hosted deployment | the `url` in `.mcp.json` is missing the `/mcp` path | The path matters, not just the host |
| Connected, zero folders | An empty Organization you approve, "(nothing stored yet …)", or a credential with no grants, "(no folders you can reach …)" | Empty: `/agentlefs:connect` offers to make the first folder. No grants: `share` with `action: "request"` for a folder the user can name, or ask an approver of the Organization |
| Connected, folder looks nearly empty | Content is gated from this principal | Expected. Denied reads exactly like not-found. |
| `how="meaning"` silently searched by text | Deployment has no vector index | Check `vectorIndex` in `/healthz`. Degradation is intentional. |
| Tools are absent from `/mcp` entirely | Plugin not enabled, or the server is unreachable | Check plugin state, then `/healthz` |
| A read errored instead of returning fewer rows | Fail-closed: a truncated allow-set throws | Surface it. The system refused to under-report. |

## Avoid

- Calling a console API endpoint from an agent context. The console API accepts only a browser session, so an OAuth or `afs_` credential gets a 401 every time. For anything needing the cross-principal view, deep-link the person to `https://agentlefs.com`.
- Diagnosing "connected but empty" as a broken connection. It is an authorization outcome, and saying so correctly is the difference between a useful answer and a wasted hour.
- Concluding the store is empty from an empty view. See the `authorization-model` skill.
