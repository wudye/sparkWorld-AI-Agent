# Day 12 - Memory, Skills, and Trajectory Systems

## Goal
Understand long-horizon learning components and how they integrate with backend turns.

## Focus Files
- `agent/memory_manager.py`
- `agent/memory_provider.py`
- `agent/skill_commands.py`
- `agent/trajectory.py`
- `trajectory_compressor.py`

## Study Tasks
- Trace when memory is read/written relative to conversation loop.
- Understand skill discovery/execution model and command injection strategy.
- Map trajectory save/compress pipeline and intended downstream usage.

## Hands-on Practice
- Create a data-flow sheet: memory, skills, trajectories, and session coupling points.
- Identify one potential consistency risk and propose mitigation.

## Deliverable
- `notes/day12-learning-systems.md` with integration map.

## Acceptance Criteria
- You can explain why skills are injected as user message context in this architecture.
- You can describe trajectory data value for analysis/training.

