# TICKET-008 — Wire up the MCP server entry point

**Status**: todo

---

**File**: `server.py` (finalise).

**Goal**: Make `server.py` a complete, runnable MCP server.

**Tasks**:
- Import `fastmcp` and create the server: `mcp = FastMCP("school-scraper")`
- Import `db`. The DB is initialised lazily via `db.get_conn()` on first tool call, so it is ready before any query runs without side effects at import time.
- Add `if __name__ == "__main__": mcp.run()` at the bottom.
- Confirm all four tools from TICKET-004 to TICKET-007 are registered.

**Acceptance criteria**:
- `uv run python server.py` starts without errors and prints something like `MCP server running` or similar fastmcp output.
- The server responds to the MCP `list_tools` call with all four tools listed.
