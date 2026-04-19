# Day 08 - SessionDB and Persistence

## Goal
Understand session persistence, schema migration, and search behavior in SQLite.

## Focus Files
- `hermes_state.py`
- `gateway/session.py`

## Study Tasks
- Read schema tables (`sessions`, `messages`, FTS5 virtual table and triggers).
- Analyze write path with lock contention strategy and jitter retries.
- Understand session lineage (`parent_session_id`) and split/compression implications.

## Hands-on Practice
- Build an ER-style diagram from schema SQL.
- Walk through one write flow and one query flow.

## Deliverable
- `notes/day08-sessiondb.md` with schema diagram and migration notes.

## Acceptance Criteria
- You can explain why WAL + app-level retry is used.
- You can describe how full-text search gets updated automatically.

