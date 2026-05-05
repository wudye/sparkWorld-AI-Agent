# Day 14 - Capstone: Build and Validate a Backend Extension

## Goal
Consolidate all learning by implementing one small but production-quality backend enhancement.

## Suggested Capstone Options
- Add one simple read-only tool (new `tools/*.py` + toolset wiring + tests).
- Add one slash command path (CLI + optional gateway support).
- Improve one reliability guard with test coverage.

## Required Scope
- architecture-aligned implementation
- profile-safe paths where relevant
- tests for success and failure path
- concise docs update (what changed and why)

## Implementation Checklist
- Define change hypothesis and risk level.
- Implement minimal code path.
- Add/adjust tests.
- Run targeted tests then broader suite path.
- Write postmortem notes (tradeoffs, future improvements).

## Deliverable
- `notes/day14-capstone-report.md` including:
  - problem statement
  - design choice
  - file changes
  - test evidence
  - known limitations

## Acceptance Criteria
- Your change is understandable, test-backed, and aligned with registry/config/profile rules.
- You can present the full request-to-persistence flow and explain where your change fits.

