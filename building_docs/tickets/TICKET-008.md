# TICKET-008 — Wire up the MCP server entry point

**Status**: done

---

**File**: `server.py` (finalise).

**Goal**: Make `server.py` a complete, runnable MCP server.

**Tasks**:
- Import `fastmcp` and create the server: `mcp = FastMCP("school-scraper")`
- Import `db` and call `db.init_db()` at module load time so the DB is ready before any tool is called.
- Add `if __name__ == "__main__": mcp.run()` at the bottom.
- Confirm all four tools from TICKET-004 to TICKET-007 are registered.

**Acceptance criteria**:
- `uv run python server.py` starts without errors and prints something like `MCP server running` or similar fastmcp output.
- The server responds to the MCP `list_tools` call with all four tools listed.
