# Day 05 - Tool Registry and Discovery

## Goal
Understand self-registering tools architecture and toolset resolution logic.

## Focus Files
- `tools/registry.py`
- `model_tools.py`
- `toolsets.py`
- `tools/*.py` (sample 3-5 tools)

## Study Tasks
- Explain import-time discovery and top-level `registry.register(...)` pattern.
- Map tool metadata fields and why each exists.
- Trace how enabled/disabled toolsets affect schema exposure.

## Hands-on Practice
- Create an inventory table of 10 tools with toolset and requirements.
- Simulate mentally how unknown/legacy toolset names are handled.

## Deliverable
- `notes/day05-tool-registry.md` with tool registration lifecycle.

## Acceptance Criteria
- You can add a new tool without touching a central giant switch.
- You can explain anti-shadowing behavior for conflicting tool names.

