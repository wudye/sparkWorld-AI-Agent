# Day 13 - Testing, Quality Gates, and Regression Control

## Goal
Learn how to validate backend changes with CI-parity mindset.

## Focus Files
- `tests/conftest.py`
- `scripts/run_tests.sh`
- tests around tools, gateway, and agent loop

## Study Tasks
- Understand hermetic test setup (env isolation, timezone, locale, home path behavior).
- Learn why project wrapper script is preferred over direct pytest calls.
- Build a regression checklist for backend changes.

## Hands-on Practice
- Select one backend subsystem and identify existing tests + missing edge cases.
- Draft two new test cases (names + assertions + fixtures) without implementing yet.

## Deliverable
- `notes/day13-testing.md` with subsystem test map and risk checklist.

## Acceptance Criteria
- You can explain common local-vs-CI drift sources in this project.
- You can propose targeted tests before touching backend production code.

