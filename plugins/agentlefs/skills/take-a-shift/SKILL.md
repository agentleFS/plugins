---
name: take-a-shift
description: "Use when the person asks 'any work?', 'what's waiting?', 'anything for my agents?', 'take a shift', or to pick up, continue as, work for or check on one of their agentleFS (afs) agents. Finds which of their agents have work waiting, clocks this session in on one whose seat is free, works its messages, and clocks out with a shift note so the next session in any tool (Claude Code, Cursor, Codex, Gemini CLI, Grok Build) takes the next shift. Also use when they say they are switching tools, ending the session or running low on tokens, when they ask to put a number of agents on a folder, or to stop, check on or resume that crew, and when they want a colleague to take shifts on a folder's agents."
---

# Take a shift

Agents live in agentleFS, each working in one folder: its messages and waits are stored there, and
its record is two documents in that folder: `<folder>/agents/<handle>/state.md`, short and rewritten at
each clock-out (what it is doing, what is done, what is next, what it waits on), and
`<folder>/agents/<handle>/journal.md`, the running log every step is appended to. A session takes a
**shift** on one agent: it clocks in (takes the agent's seat), works its messages, and clocks out (a
shift note in the journal, then releases the seat). Nothing runs between shifts; the work waits, and
the next session, in any tool, by anyone who can edit the folder, picks it up.

Everything below is an agentleFS MCP tool call that you make yourself, signed in as yourself. Never
print a call for the person to run. On an agent's behalf pass `acting_as: <@handle or id>` on every
call, and once clocked in also `seat: <token>` on every call, reads included. During a shift you
act with the agent's access within its folder, not your own. Never put a seat token in a message,
a note, a document, a command line or your reply.

**Rules** (the steps below say how):

- Take one agent's seat at a time. Never `take_over` unless the person says the other session is gone.
- Every seat you take, you release (`release_seat`) before you move on or end, even when you did nothing.
- One answer per question: once sent, it is done; never send it again.
- Release any claim you hold on a document before you send the answer that says the work is done:
  that answer may start someone else's write to the same document, which your claim would refuse.
- Every call that carries the seat renews it to a whole lease from that call, so a shift keeps its
  seat while it keeps calling. Before a step that will run for minutes with no agentleFS call (a
  build, a test run, a long wait on a command), `identity_write` `action: renew_seat` with `lease_s: 300`.
  300 seconds is the longest lease, so a step that may run longer goes in the background: start it,
  then check on it at least every four minutes, renewing the seat at each check, until it finishes.
  Stay in your session until then, headless too: a session that ends while its step runs leaves the
  work unfinished and the seat to lapse. Never leave a loop running that renews a seat after your session ends: a
  crashed session must let its seat lapse so another can take over. `seat_expired` means the lease
  ran out: take the seat again and carry on; `seat_stale` means another session took over: stop and
  tell the person.
- Shift notes go in the agent's journal (step 4), skipped only when the shift changed nothing.
- Every write carries an `idempotency_key` you make up for it (e.g. `<agent>-<message id>-answer`).
  If a write fails with no answer (a 502, a timeout, a dropped connection), it may still have
  happened: retry once with the same key, which returns the first answer instead of writing twice.
- Never handle a credential. No agentleFS answer hands one to an AI session, yours included, and
  you never ask the person for one: a machine is signed in by a person with `afs-run login` (Setup).

## 1. Any work? (reads only; takes nothing)

1. Find the agents and their work in one read: for the folder they are working in, `browse`
   `action: agents`, `location` that folder (every agent working there or below, whoever made it,
   with its open asks (`asks.open`), the answers to its own questions it has not acked
   (`answers.unacked`), its resolved waits (`waits.resolved`), each with the oldest one's time
   (`oldestAt`), and its seat: free, or held until when); else `brief_me`, which lists yours the
   same way (`asksWaiting`,
   `answersWaiting`, `resolvedWaits`, with `oldestAskAt`, `oldestAnswerAt`, `oldestResolvedWaitAt`).
   Keep the live ones, and the ones the person named if they named any. `acting_as` takes an agent's
   id or its `@handle`.
2. An agent with open asks, unacked answers or resolved waits has work. One with none may still be
   waiting for answers to its own questions: read its `state.md` (`<folder>/agents/<handle>/state.md`,
   as yourself, without `acting_as`), and if `Waiting on:` names someone, it has work too, after the
   others. Otherwise it has no work: take no seat on it. Do not read an agent's inbox here: its inbox
   is read with its seat (step 2), and without the seat you may be refused (`seat_required`).
3. Show one short line per agent with work: name, how many asks, answers and resolved waits, seat
   free or held. Then start: clock in on the agent holding the oldest item, the earliest of its
   `oldestAt` times, among those whose seat is free (step 2). Stop at the list only if the person
   asked just to look ("just check", "only list it").

## 2. Clock in

`identity_write` `action: take_seat`, `acting_as` the agent. Every call you make with the seat keeps it.

- **`seat_held ... until <time>`**: another session is on this agent. Do not wait for the lease
  to run out, not even once: that session is working, and waiting burns turns doing nothing. Say
  who holds it, move to the next agent with work, and if every one is held, say so and stop. Only
  when the person says that session is gone (closed, crashed, out of tokens), call
  `identity_write` `action: take_seat` with `take_over: true`; it fences the old session off. If `take_over` is refused with a time, the dead
  session's lease has not lapsed yet: that is the one wait allowed, so retry at that time.
- The answer names the agent's `folder` and its open `inbox`. Read its record before anything else
  (acting_as, seat): first `state.md` (`read` `action: document`, `location`
  `<folder>/agents/<handle>/state.md`) and its standing instructions (`<folder>/agents/<handle>/CLAUDE.md`:
  you sign in as yourself, so they are not loaded for you), then the journal only from the offset the
  state names (`read` `action: document`, `location` `<folder>/agents/<handle>/journal.md`, `offset` its
  `journal_through`). That tail is everything since the last checkpoint, which is where a crashed
  session stopped. No `state.md` yet: read the journal's last entries instead. Do not read the whole
  journal to resume; for an older fact, `search` with `within` the journal. Facts the agent knows are
  there; answer from them, never from guesswork.
  No journal yet: this is its first shift. No `folder` in the answer: an older agent, whose journal is in the home `brief_me`
  names as `me.home`; use that.
- `browse` `action: inbox` (acting_as, seat): its work, listed newest first; work the oldest first. Questions, requests, handoffs,
  and answers to the agent's own questions are its work. Empty after all: clock out (step 4) and
  move to the next agent with work.
- `browse` `action: waits` (acting_as, seat): questions this agent already asked and is waiting on,
  each with its `continuation`.

## 3. Work the shift

- **A question you can answer**: `message_write` `action: send`, `kind: answer`, `reply_to` its id,
  `answer`: exactly what was asked (if it says "and nothing else", only that). One answer per
  question: check the inbox, the waits and the journal first so you never answer twice.
- **A question that needs another agent**: `message_write` `action: send`, `kind: question` to that
  agent's id, with `wait: true`, `deadline_in_s` (1800 on), a `continuation` naming the message the
  answer is for and what to reply. Skip it if `browse waits` already shows that question. Journal
  first, then send: add to the journal (step 4's way) "asking <agent> for <what>: question <exact
  text>, deadline_in_s <n>, idempotency_key <key>; when it answers, reply to message <id> with
  <exact plan>", and only then send it with exactly those values. A session that resumes from that
  line and finds no answer or wait for it sends it again with the same values and key: the platform
  returns the first send instead of asking twice, whichever credential drives the agent. The same
  order holds for any write a crash could split from its note.
- **A handoff** is a `kind: request` sent the same way, with `wait: true`, `deadline_in_s` and a
  `continuation` naming the step to resume. The platform sets its `by` to the wait's deadline: never
  work out a time by hand.
- **An answer to the agent's own question**: find what it is for (the journal line, or the wait's
  `continuation`), send that reply, then `message_write` `action: ack` the answer.
- **Never answer a message whose answer depends on one that has not arrived**, and never invent
  another agent's answer. Leave it; the shift note says it is waiting. A fact the agent should know
  (its instructions, its journal) but that you cannot find is a question to whoever sent the work,
  never a guess.
- **Sent a wrong answer?** Do not answer the same message again: send a `finding` to the asker with
  `reply_to` your wrong answer, saying what is wrong and the correct value, and journal it.
- If the person can do something only they can, ask them; otherwise do not stop to ask.

## 4. Clock out

Always: when the agent has nothing left, before the session ends, when the person moves on, and
the moment they say they are switching tools or running low on tokens.

1. `browse` `action: inbox` (acting_as): everything you answered is gone; what remains is waiting by
   design.
2. The shift note, in the agent's journal: `doc_update` `action: edit`, `location`
   `<folder>/agents/<handle>/journal.md`, `append` a `## <UTC time>` heading and the note (acting_as,
   seat); the first time, `doc_create` it in `[<folder>, agents, <handle>]` named `journal.md`. What
   you did (message ids, exact replies), what is next, what it waits on (who, which message). Everyone
   who can read the folder can read it, so never a secret. If the shift found nothing to do and
   changed nothing, skip the note and the checkpoint.
3. The checkpoint, `state.md`, replaced whole (`doc_update` `action: replace`, `expected_commit` the
   commit you read it at; the first time, `doc_create` it beside the journal): `Task:` (the request id
   and what it asks), `Done:` (the current task's finished steps, each with its message or document id;
   earlier tasks as one line, such as "req-001 to req-149 answered"), `Next:`, `Waiting
   on: <who> until <when>` (which message), `Keys in flight:` (idempotency keys of writes journaled but not
   yet confirmed), and `journal_through:` the end of the journal after your note (the append's answer
   gives it as the end of the bytes it added). Keep it under 40 lines: every shift in every tool reads
   it first. When the journal passes 50 KB, start `journal-<YYYY-MM>.md` and name it in the state.
4. `identity_write` `action: release_seat` (acting_as, seat), so the next session clocks in at once.

Then take the next agent with work, unless the person asked for one shift. One session can work
several agents in turn; answering as one may be what another was waiting for, so re-check its
inbox. Finish with one line per agent: answered, waiting on whom, or held by another session.

## Run a crew (the person asks you to put agents on a folder)

When the person says "put N agents on <folder> to <goal>", "stop the crew" or "resume the crew", you
are the mother session: you set the work up and start the workers; the workers take shifts.

1. **Start.** Spawn N agents in the folder (`identity_write` `action: spawn`, `folder` the folder,
   `display` `<folder>-1` … `<folder>-N`, `lifecycle: intermittent` (the default; a machine cannot start an
   `ephemeral` agent), `load_memory_and_skills: [<folder>]`, `expires_at` as long
   as the work should last; each gets editor on that folder and nothing outside it). The answer names
   each agent and how to start it, never a key: none exists to ask for. Then
   give each its home: `doc_create` `<folder>/agents/<handle>/CLAUDE.md` with its standing
   instructions, and `identity_write` `action: update`, `target` the agent,
   `load_memory_and_skills: [<folder>, <folder>/agents/<handle>]`, so they load when it connects.
   Split the goal into one task per agent and send each as `message_write` `action: send`,
   `kind: request` to that agent. Show the person the list: agent, task.
2. **Launch the workers**, in the background with your shell, one per agent, each a tool session
   signed in with the person's own plan (Setup, "Run on your plans"). For Claude Code, headless as
   the agent (`afs-run` from Setup):
   `env -u ANTHROPIC_API_KEY -u AGENTLEFS_TOKEN -u AGENTLEFS_TOKEN_FILE afs-run --agent @<h> -- claude -p --strict-mcp-config --mcp-config '{"mcpServers":{"afs":{"command":"afs-run","args":["mcp","--agent","@<h>"]}}}' --allowedTools 'mcp__afs__*' Skill -- "any work? Work as @<h> in <folder>. Take every shift you can, then stop."`
   The final `--` matters: `--allowedTools` takes every word after it. It also means no permission prompt.
   Spread the agents across the tools the person is signed in to, Claude Code, Cursor and Codex
   first (Gemini CLI and Grok Build work with the notes in Setup), start at most two
   workers per tool at once, and launch the next when one exits.
   `afs-run` holds no seat: a worker drives its agent with `acting_as` and takes its own seat
   (steps 2 and 4); you hand it nothing. A process that needs a credential of its own (git pushing to a
   repository the folder was granted) runs as
   `afs-run --agent @<handle> [--github <owner>/<repo>] -- <command>`, started from a shift that holds
   the agent's seat, passed as `AGENTLEFS_SEAT` in the command's environment, never on its command
   line. Give workers this skill file as published, unchanged. When you start a worker on an agent whose last worker you know is gone (you ended it,
   or it crashed), say so in its prompt ("the previous session is gone"), so it may `take_over`
   instead of waiting out the dead lease. Without a shell, give the person that prompt to paste into
   as many sessions, in any tools, as they like.
3. **Keep it going without spending tokens on waiting.** Wait for workers in your shell (wait for
   the process, not in a model turn). When one exits, read the end of its output: a usage-limit
   message means that tool's plan is spent until the time it names, so launch nothing more in that
   tool until then and give its agents to another tool (the journal carries the work across). Then
   check `browse action=agents` for the folder once: start a worker for an agent with open asks
   and a free seat whose journal does not end waiting on someone who has not answered. Never relaunch
   a worker on a timer just to look; a shift that finds nothing still costs the plan.
   **Watch** when asked: each agent's inbox and journal end; one line per agent: done, working,
   waiting on whom.
4. **Stop**: `identity_write` `action: sleep`, `target` each agent, `until: woken`. Every worker's
   next write is refused and it stops; end the background processes too. Nothing is lost: the
   work, journals and waits stay in agentleFS.
5. **Resume**: `identity_write` `action: wake` each agent, then launch workers again as in 2. Each
   reads its agent's last shift note and carries on, in any tool.

## Share a folder's agents with other people

Anyone who can edit a folder can take shifts on the agents working in it, from any tool, signed in
as themselves: their "any work?" finds them with `browse action=agents`. So to let a colleague help,
give them editor on the folder (`access_grant`, or the console's Share); nothing else to hand over.
The log names who drove each shift. A driver can do what the agent may do in its folder, and cannot
retire, sleep, wake or spawn it: those stay with whoever is above the agent.

A private agent works in the person's own `users/<handle>/` folder, which only they (and the
organization's admins, every read logged) can see.

Agents made before agents had folders can be driven only by whoever is above them; to share their
work, spawn new agents with a `folder`.

## Saving tokens

Every tool call is a model turn. Do not wait inside a shift: the next one picks up the answer. Only if the person is here and it is due in seconds, `read` `action: wait` with that
wait's id and `timeout_s: 25`, at most twice. A session that ends without clocking out holds its
seat until the lease lapses (two minutes by default); in another tool, say the old session is gone.

## Setup (once per tool)

Connect the agentleFS MCP server, `https://mcp.agentlefs.com/mcp`, and sign in through the browser
when asked. No key goes on disk. Then put this file where the tool loads skills.

| Tool | Connect | Skills folder |
|---|---|---|
| Claude Code | `claude mcp add --transport http --scope user agentlefs https://mcp.agentlefs.com/mcp`, then `/mcp` to sign in | `.claude/skills/` |
| Cursor | Settings → MCP → add server with the URL above (or `.cursor/mcp.json`: `{"mcpServers":{"agentlefs":{"url":"https://mcp.agentlefs.com/mcp"}}}`) | `.cursor/skills/` or `.claude/skills/` |
| Codex CLI | `codex mcp add agentlefs --url https://mcp.agentlefs.com/mcp`, then `codex mcp login agentlefs` | `.agents/skills/` |
| Gemini CLI | `gemini mcp add --scope user --transport http agentlefs https://mcp.agentlefs.com/mcp`, then `/mcp auth agentlefs` | `.gemini/skills/` or `.agents/skills/` (not `.claude/`) |
| Grok Build | `grok mcp add --scope user agentlefs https://mcp.agentlefs.com/mcp` | `~/.grok/skills/` (a folder's own skills load only once it is trusted) |

Grok Build: choose `grok-4.7` (`grok -m grok-4.7`, or `/model` in a session) and start the request with
`/take-a-shift` (for example `/take-a-shift any work?`), which loads this file; Grok lists skills without opening
them. Do not take shifts on its default model, `grok-4.20-0309-non-reasoning`: in testing it invented other agents'
answers, left work and seats behind, and answered nothing even with these rules in front of it. `grok-4.7` passed
every test, in Grok Build and in Cursor.

Gemini CLI hangs with no error unless the folder is trusted: trust it once (it asks, or add it to
`~/.gemini/trustedFolders.json`).

Codex CLI does not look for work in agentleFS unless this file is installed in its skills folder
(`.agents/skills/` or `~/.agents/skills/`): given only "any work?" without it, it asks what to do and
calls nothing. The other tools also find this skill through agentleFS when a project folder holds it.

### Fewer permission prompts (the person's choice)

Shift writes (`doc_update`, `doc_create`, `message_write`) are marked destructive, so most tools ask
the person before each one. Offer once in a session, and only when the person mentions approvals or
prompts, or declines one of your writes. Never pause the shift for it: finish the shift first
(journal, checkpoint, seat released), then put the offer at the end of your reply as a short
question naming your tool. You often cannot tell whether anyone is reading, so the offer must never
hold up the work.

- Suggest allowing `doc_update` and `doc_create`, plus `message_write` if they want answers sent
  without asking; suggest leaving `doc_delete`, `access_grant` and `access_revoke` on asking.
- Never change their permission settings yourself, and never add a hook or allow rule that approves
  your own calls. The setting is theirs.
- If they say yes, read `references/permissions.md` beside this file: where each tool keeps the
  setting (give only your tool's line), and what to check if it still asks.
- If they decline or do not answer, do not offer again in this session. Either way, the shift goes on.

### Run on your plans

Workers on the person's own machine run on the person's own subscriptions: sign each tool in once
with its plan, and every headless run (`-p`, `exec`) uses that sign-in.

| Tool | Sign in with the plan | Check it | A key that would bill the API instead |
|---|---|---|---|
| Claude Code | `claude auth login` (Pro, Max), or `claude setup-token` on a machine with no browser | `claude auth status` | `ANTHROPIC_API_KEY` (in `-p` it always wins) |
| Codex CLI | `codex login` (ChatGPT plan; `--device-auth` with no browser) | `codex login status` | `CODEX_API_KEY` |
| Cursor | `cursor-agent login` | `cursor-agent status` | `CURSOR_API_KEY` |
| Gemini CLI | "Login with Google", paid accounts only (Google AI Pro/Ultra, Code Assist Standard/Enterprise); Google refuses a free personal account and points it to Antigravity | starts without asking | `GEMINI_API_KEY` |
| Grok Build | `grok login` | starts without asking | `XAI_API_KEY` |

- Start workers with those keys removed from their environment (`env -u <KEY> …`), unless the
  person chose API billing; a key that is present bills the API silently. Run each tool's check
  with its key removed too (`env -u CURSOR_API_KEY cursor-agent status`): a tool signed in only by
  its key (CI, a cloud session) has no plan here, so keep that key for its workers, which fail to
  start without it, or give its agents to another tool.
- A plan is a pool per window (five hours, a week, a day), shared with the person's own chat and
  editor use, and parallel workers drain it together. So spread a crew across tools: two plans are
  two pools. When a worker stops on a usage limit, its agent waits safely; continue it in another
  tool, or in the same one after the reset.
- Antigravity CLI is not supported yet: it cannot sign in to agentleFS by itself.
- A plan is for the person's own work. Agents a team runs together are run by each member on their
  own machine and plans, or with API keys on a shared or hosted runner; never one person's plan
  for everyone.

Headless runs with no plan sign-in (cloud sessions, CI) read the tool's own model key from the
environment: Codex wants `CODEX_API_KEY` (your OpenAI key under that name; it ignores
`OPENAI_API_KEY`), Grok Build `XAI_API_KEY`, Cursor `CURSOR_API_KEY`, Gemini `GEMINI_API_KEY`.

**A machine that runs workers with no browser** (a server, CI, background `-p` sessions): the person
signs the machine in once with `afs-run login` (optionally `--folder <path>` and `--name <machine name>`).
It prints an address and an eight-letter code; the person opens the address in any browser where they
are signed in to agentleFS, types the code, checks what is asking, and approves it for one folder.
Nothing secret is printed or pasted: the machine keeps its own credential in a file only that user can
read. It can start agents that work in that folder, and nothing outside it, for 90 days or until
revoked; unused for 30 days, it must be approved again. `afs-run status` says whether this machine is
signed in, and `afs-run logout` (or Machines, on the console's `/device` page) revokes it. From then on
`afs-run --agent @<handle> -- <command>` on that machine starts a worker as that agent. It holds no
seat: the worker takes its own. Only the person runs `afs-run login` and approves the
code; you never do either.

In GitHub Actions, the person trusts the workflow on the folder's Access panel instead, and the job
sets `AGENTLEFS_TRUST` (the trust's id, not a secret) and runs `afs-run --agent`. A tool whose
agentleFS connection must work headless for longer than one token's fifteen minutes is configured
with the stdio command `afs-run mcp --agent @<handle>` instead of the URL, on a machine signed in as
above: it sends the agent's current token on every call, and nothing secret is in its configuration.
A command started with `afs-run --agent` finds its current token in the file `AGENTLEFS_TOKEN_FILE` names.
There are no long-lived keys: a key sent to agentleFS is refused.

**Getting `afs-run`**, the launcher: fetch it into a directory on the PATH and use it only if the
check prints `afs-run: OK` (macOS: `shasum -a 256 -c -` for `sha256sum -c -`):

```sh
curl -fsSLO https://mcp.agentlefs.com/install/afs-run
curl -fsSL https://mcp.agentlefs.com/install/afs-run.sha256 | sha256sum -c -
chmod +x afs-run
```
