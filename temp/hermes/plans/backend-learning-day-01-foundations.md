# Day 01 - Foundations and Project Orientation

## Goal
Build a complete mental map of the backend repository structure, runtime modes, and major execution paths.

## Focus Files
- `README.md`
- `AGENTS.md`
- `run_agent.py`
- `cli.py`
- `gateway/run.py`

## Study Tasks
- Identify all backend entry points (`hermes`, CLI, gateway, batch).
- Draw a one-page architecture map with layer boundaries.
- List key runtime contexts: CLI, messaging gateway, TUI backend.

## Hands-on Practice
- Trace one user request path in CLI mode from command to model response.
- Record every module touched in order.

## Deliverable
- `notes/day01-architecture-map.md` with a diagram and 15+ bullet observations.

## Acceptance Criteria
- You can explain why `run_agent.py` is core but not the only backend entry.
- You can describe the role of `model_tools.py`, `toolsets.py`, and `tools/registry.py` in one paragraph.

