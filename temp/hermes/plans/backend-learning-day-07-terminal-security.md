i# Day 07 - Terminal Safety and Approval System

## Goal
Master dangerous command detection and approval workflows for CLI and gateway.

## Focus Files
- `tools/approval.py`
- `tools/terminal_tool.py`
- `run_agent.py`

## Study Tasks
- Review command normalization and pattern-matching design.
- Understand per-session approval queues and context-local session key handling.
- Map approval outcomes (once/session/always/deny) and persistence.

## Hands-on Practice
- Prepare a test table: command -> expected danger detection -> expected prompt behavior.
- Analyze how gateway concurrency impacts approval state safety.

## Deliverable
- `notes/day07-terminal-security.md` with policy table.

## Acceptance Criteria
- You can explain the full path from terminal command request to approval decision.
- You can identify which regex patterns protect against self-termination hazards.

