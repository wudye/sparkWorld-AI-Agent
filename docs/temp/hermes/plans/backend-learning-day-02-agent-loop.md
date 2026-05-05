# Day 02 - Agent Loop Deep Dive

## Goal
Understand `AIAgent` internals and the full `run_conversation` loop mechanics.

## Focus Files
- `run_agent.py`
- `agent/retry_utils.py`
- `agent/error_classifier.py`

## Study Tasks
- Read constructor parameters and classify them by concern (model, tools, session, platform).
- Trace `run_conversation(...)` lifecycle: message prep, model call, tool branch, final response.
- Analyze iteration control (`max_iterations`, `IterationBudget`, termination conditions).

## Hands-on Practice
- Build a sequence diagram for one turn with two tool calls.
- Locate where interrupts and timeout-like controls are applied.

## Deliverable
- `notes/day02-agent-loop.md` with lifecycle diagram and loop invariants.

## Acceptance Criteria
- You can explain all loop exit paths and what gets returned.
- You can identify at least three failure-handling layers in `AIAgent`.

