# Day 04 - Model Metadata, Routing, and Provider Behavior

## Goal
Understand provider-aware model behavior, token constraints, and fallback/routing logic.

## Focus Files
- `agent/model_metadata.py`
- `agent/models_dev.py`
- `agent/smart_model_routing.py`
- `run_agent.py`

## Study Tasks
- Document how context length is inferred, cached, and updated.
- Analyze token estimation utilities and where they influence control flow.
- Map model/provider-specific guidance hooks.

## Hands-on Practice
- Create a matrix: provider -> model -> context handling notes.
- Trace one error path where metadata influences retry/fallback behavior.

## Deliverable
- `notes/day04-model-routing.md` with provider matrix.

## Acceptance Criteria
- You can reason about how model limits affect prompt/tool strategy.
- You can identify where to add support for a new provider model family.

