# Day 03 - Prompt, Context, and Compression

## Goal
Master how system/user/tool context is assembled, cached, and compressed without breaking behavior.

## Focus Files
- `agent/prompt_builder.py`
- `agent/context_compressor.py`
- `agent/prompt_caching.py`
- `run_agent.py`

## Study Tasks
- Catalog all prompt components and where each is injected.
- Understand cache-sensitive constraints during long conversations.
- Trace context compression trigger, output, and reintegration.

## Hands-on Practice
- Compare pre-compression and post-compression message stacks conceptually.
- Write a checklist of "do not break" prompt caching assumptions.

## Deliverable
- `notes/day03-prompt-context.md` with prompt assembly table.

## Acceptance Criteria
- You can explain why certain mid-conversation context changes are disallowed.
- You can describe compression as a controlled exception path.

