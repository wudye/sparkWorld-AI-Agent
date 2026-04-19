# Day 11 - TUI Gateway RPC Backend

## Goal
Understand how the Python backend powers the Node/Ink TUI through JSON-RPC.

## Focus Files
- `tui_gateway/entry.py`
- `tui_gateway/server.py`
- `tui_gateway/slash_worker.py`
- `ui-tui/src/gatewayClient.ts`

## Study Tasks
- Map request/response and event streams over stdio JSON-RPC.
- Understand slash command delegation to persistent worker process.
- Identify where approvals/clarifications are bridged between frontend and backend.

## Hands-on Practice
- Build a protocol table: method -> producer -> consumer -> payload.
- Trace one slash command that is handled locally vs remotely.

## Deliverable
- `notes/day11-tui-rpc.md` with protocol map.

## Acceptance Criteria
- You can explain why Python owns tools/session state while TypeScript owns rendering.
- You can identify safe extension points for new RPC methods.

