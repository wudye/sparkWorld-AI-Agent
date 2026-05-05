# Day 09 - CLI Runtime and Command Dispatch

## Goal
Understand the backend mechanics behind interactive CLI orchestration.

## Focus Files
- `cli.py`
- `hermes_cli/commands.py`
- `agent/skill_commands.py`
- `hermes_cli/config.py`

## Study Tasks
- Map slash command lifecycle: parse -> resolve -> dispatch -> side effects.
- Learn how CLI config is loaded and merged.
- Inspect how skill commands are discovered and executed.

## Hands-on Practice
- Choose one command and trace every function hop.
- Design a hypothetical new command and list exact files to change.

## Deliverable
- `notes/day09-cli-runtime.md` with command dispatch map.

## Acceptance Criteria
- You can add an alias correctly using command registry rules.
- You can explain which config loader is used in CLI mode.

