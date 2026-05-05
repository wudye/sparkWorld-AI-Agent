# Day 10 - Gateway Core and Multi-Platform Lifecycle

## Goal
Understand gateway orchestration, platform adapters, and long-lived process constraints.

## Focus Files
- `gateway/run.py`
- `gateway/platforms/*`
- `gateway/session.py`

## Study Tasks
- Trace startup lifecycle and platform adapter initialization.
- Understand config.yaml to env bridging and runtime side effects.
- Analyze session-to-agent cache behavior and eviction policy.

## Hands-on Practice
- Draw a message lifecycle from platform event to assistant reply.
- Identify where to add a new platform-specific command handling branch.

## Deliverable
- `notes/day10-gateway-core.md` with gateway lifecycle chart.

## Acceptance Criteria
- You can explain why gateway must handle cert/env/bootstrap before adapters.
- You can describe agent cache cap and idle eviction intent.

