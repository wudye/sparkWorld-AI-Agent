# Day 06 - Tool Dispatch and Async Bridging

## Goal
Understand safe execution of sync/async tools across CLI, gateway, and worker-thread contexts.

## Focus Files
- `model_tools.py`
- `run_agent.py`
- `tools/terminal_tool.py`
- `tools/delegate_tool.py`

## Study Tasks
- Read `_run_async(...)` branch logic and event loop management strategy.
- Trace `handle_function_call(...)` to registry dispatch and result wrapping.
- Analyze parallel vs sequential tool execution decisions.

## Hands-on Practice
- Build a small decision tree for tool execution context.
- Identify potential deadlock/race points and how code mitigates them.

## Deliverable
- `notes/day06-tool-execution.md` with execution flowchart.

## Acceptance Criteria
- You can explain why `asyncio.run()` per call is unsafe in this architecture.
- You can describe when worker-thread loops are used and why.

