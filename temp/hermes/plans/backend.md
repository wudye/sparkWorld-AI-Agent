# Hermes Agent Backend Project Analysis

## 1) Backend Scope and Learning Goal

This report focuses on the Python backend of Hermes Agent:
- core agent loop and model calls
- tool discovery, registration, dispatch, and safety
- session persistence and search
- CLI and gateway orchestration
- extension points for tools, commands, and integrations

If your goal is to learn the project from zero to production-level contribution, use this file as the architecture map and pair it with the 14 day plan files under `plans/`.

## 2) Backend Architecture at a Glance

Primary backend layers:
- Agent runtime: `run_agent.py` (`AIAgent`) drives conversation loop, tool-calling turns, retries, budgets, and usage accounting.
- Tool orchestration: `model_tools.py` + `tools/registry.py` provide schema resolution and safe dispatch into individual tool handlers.
- Tool implementations: `tools/*.py` one module per capability (terminal, web, browser, file, delegate, mcp, etc.).
- Session storage: `hermes_state.py` (`SessionDB`) stores session metadata/messages in SQLite with FTS5 search.
- CLI runtime: `cli.py` + `hermes_cli/*` handle interactive UX, slash commands, config lifecycle, setup flows.
- Messaging gateway: `gateway/run.py` + `gateway/platforms/*` handle Telegram/Discord/Slack/etc and route turns through `AIAgent`.
- Prompt/context internals: `agent/*` handles prompt building, compression, caching, model metadata, memory, and trajectory helpers.

Design style:
- mostly synchronous orchestration for determinism and compatibility
- explicit extension points via registry patterns and command registries
- environment-aware behavior (CLI vs gateway vs profile)
- strong safety rails around dangerous commands and session isolation

## 3) Critical Dependency Chain

Backend dependency chain for tools:
1. `tools/registry.py` (no import dependency on model orchestrator)
2. `tools/*.py` modules self-register via `registry.register(...)` at import time
3. `model_tools.py` calls discovery and exposes API (`get_tool_definitions`, `handle_function_call`)
4. `run_agent.py`/`cli.py`/`gateway/run.py` consume `model_tools.py`

Why this matters:
- adding a tool does not require editing a giant switch statement
- schema + handler metadata stay colocated in each tool file
- registry can enforce anti-shadowing and availability checks centrally

## 4) End-to-End Request and Tool Data Flow

A) User turn enters system:
- CLI path: user text -> `HermesCLI` -> `AIAgent.run_conversation(...)`
- Gateway path: platform event -> `GatewayRunner` -> session routing -> `AIAgent.run_conversation(...)`

B) Agent model loop:
- `AIAgent` builds message stack and tool schema list
- calls model completion API
- if no tool calls: returns assistant text
- if tool calls: executes tools, appends tool results to messages, loops

C) Tool execution pipeline:
- `run_agent.py` invokes `handle_function_call(...)` in `model_tools.py`
- `model_tools.py` resolves entry from registry and dispatches handler
- result is normalized as JSON string and injected back as `tool` role message

D) Persistence:
- session metadata and messages saved via `SessionDB` (`hermes_state.py`)
- text is indexed in FTS5 table for semantic-ish retrieval/search workflows

## 5) Core Module Analysis

## 5.1 `run_agent.py` (`AIAgent`)

Responsibilities:
- run conversation loop with `max_iterations` and `IterationBudget`
- prepare/maintain message history
- integrate tool calling into iterative loop
- manage retries, failover hints, context compression, pricing usage
- coordinate interrupts, spinner callbacks, and output formatting

Important mechanics:
- thread-safe iteration budget with refund semantics (for special tool flows)
- controlled parallel execution decisions for safe vs unsafe tool groups
- guardrails for destructive terminal commands and output redirection patterns
- prompt caching and compression interplay must remain cache-safe

Learning pitfall:
- this file is large; read by feature slice, not linearly.

## 5.2 `model_tools.py`

Responsibilities:
- trigger tool discovery (`discover_builtin_tools`, MCP, plugins)
- provide filtered tool schemas by enabled/disabled toolsets
- bridge sync orchestration with async tool handlers safely
- dispatch function calls to registry with consistent error wrapping

Important mechanics:
- `_run_async(...)` handles async-in-sync correctly for:
  - normal CLI thread
  - worker threads
  - already-running event-loop contexts
- legacy toolset name compatibility map preserves old configs
- process-global last resolved tool names aid downstream tool behavior

## 5.3 `tools/registry.py`

Responsibilities:
- central storage for tool metadata and handlers
- discovery of self-registering tool modules
- provide stable snapshots for concurrent readers
- protect against unsafe tool-name shadowing

Important mechanics:
- import-time AST check detects top-level `registry.register(...)`
- lock-protected mutations with snapshot reads for thread safety
- MCP overwrite rules allowed only for MCP-to-MCP refresh scenarios

## 5.4 `hermes_state.py` (`SessionDB`)

Responsibilities:
- sqlite persistence for sessions and messages
- FTS5 indexing and search triggers
- schema migrations and versioning
- concurrent write contention handling

Important mechanics:
- WAL mode + short sqlite timeout
- application-level jittered retries (`BEGIN IMMEDIATE`) to avoid lock convoy
- periodic passive checkpointing to control WAL growth

## 5.5 `gateway/run.py`

Responsibilities:
- start and manage multi-platform adapters
- maintain session to agent lifecycle
- environment/config bridge for gateway runtime
- async orchestration and long-lived process concerns

Important mechanics:
- CA cert bootstrap for non-standard systems
- config.yaml -> env bridging for terminal/auxiliary/agent/display settings
- controlled AIAgent cache bounds (size + idle TTL)
- gateway safety mode toggles (quiet mode, exec approval)

## 5.6 `hermes_cli/config.py`

Responsibilities:
- canonical config and env paths (profile-aware)
- setup/config editing flows
- managed mode behavior and update command logic
- permission hardening and container-aware exceptions

Important mechanics:
- avoid hardcoded `~/.hermes`; use profile-aware helpers
- strict separation of config.yaml and .env concerns

## 5.7 `tools/approval.py`

Responsibilities:
- detect dangerous commands with robust normalization
- maintain per-session approval state and queues
- support CLI and gateway approval workflows
- persistent allowlist integration

Important mechanics:
- ANSI stripping + Unicode normalization before regex detection
- context-local session keys reduce cross-session race conditions
- broad pattern coverage for shell/script/git/gateway self-termination risks

## 6) Configuration, Profiles, and Runtime Isolation

Configuration sources:
- `HERMES_HOME/config.yaml` for runtime settings
- `HERMES_HOME/.env` for secrets and provider credentials

Profile safety model:
- `HERMES_HOME` is overridden before major imports
- state/config/memory/skills/session data are profile-isolated
- user-facing path strings should use profile-aware display helpers

Operational implication:
- backend features must never hardcode `~/.hermes`
- tests should set both `Path.home()` and `HERMES_HOME` when profile behavior is involved

## 7) Security and Reliability Posture

Security controls:
- dangerous command detection and approval gate
- per-session approval context
- optional redaction and environment controls

Reliability controls:
- iteration budgets and timeout controls
- defensive async bridging for mixed sync/async call stacks
- sqlite lock contention strategy tuned for multi-process access
- fallback env/config loading to avoid hard crash on partial misconfig

Known backend risk areas:
- large monolithic files increase regression surface
- global state (for compatibility features) needs careful isolation in delegated/subagent paths
- long-lived gateway sessions require memory/cache hygiene

## 8) How to Extend the Backend Safely

Add a new tool:
1. implement `tools/<name>.py` with `registry.register(...)`
2. assign a toolset and requirements metadata
3. include toolset in `toolsets.py`
4. add/adjust tests

Add a slash command:
1. add `CommandDef` in `hermes_cli/commands.py`
2. add dispatch in `HermesCLI.process_command()`
3. if needed, add gateway handler in `gateway/run.py`

Add config:
1. update `DEFAULT_CONFIG` in `hermes_cli/config.py`
2. add env metadata to `OPTIONAL_ENV_VARS` if secret/input driven
3. add migrations/version updates when required

## 9) Testing Strategy for Backend Learning

Recommended progression:
- start with focused test files for touched modules
- then run broader area suites
- finish with full-suite run through project wrapper script

What to verify when modifying backend:
- no profile-path regressions
- tool dispatch still deterministic
- gateway and CLI behavior parity for shared commands
- dangerous command approval behavior unchanged unless intentionally updated

## 10) Suggested Reading Order (Mapped to 14 Study Files)

Use these files in order:
1. `plans/backend-learning-day-01-foundations.md`
2. `plans/backend-learning-day-02-agent-loop.md`
3. `plans/backend-learning-day-03-prompt-context.md`
4. `plans/backend-learning-day-04-model-routing.md`
5. `plans/backend-learning-day-05-tool-registry.md`
6. `plans/backend-learning-day-06-tool-execution.md`
7. `plans/backend-learning-day-07-terminal-security.md`
8. `plans/backend-learning-day-08-sessiondb.md`
9. `plans/backend-learning-day-09-cli-runtime.md`
10. `plans/backend-learning-day-10-gateway-core.md`
11. `plans/backend-learning-day-11-tui-gateway-rpc.md`
12. `plans/backend-learning-day-12-memory-skills-trajectories.md`
13. `plans/backend-learning-day-13-testing-quality.md`
14. `plans/backend-learning-day-14-capstone.md`

## 11) Outcome You Should Reach After 14 Days

You should be able to:
- explain full backend request lifecycle from user input to tool result to persisted session
- add one production-ready tool with config, tests, and failure handling
- debug gateway session issues and approval flow behavior
- reason about profile-safe path handling and migration-safe config updates
- submit backend PRs that align with architecture and operational constraints

