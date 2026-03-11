# TICKET-009 — Register the MCP server with Claude Code

**Status**: done

---

**Goal**: Add the local server to Claude Code's MCP config so the tools are available in Claude Code sessions.

**Steps**:
1. Register the server using the Claude Code CLI. Because we use `uv`, point at the `uv` binary so it resolves the venv automatically:
   ```
   claude mcp add school-scraper uv --args "run,python,server.py" --cwd "c:/Users/cstow/cm_code/chlobo_is_a_spammer"
   ```
   Check `claude mcp --help` for exact flag syntax — the key point is the command is `uv` with args `run python server.py`, not a direct path to a venv Python binary.
2. Restart Claude Code.
3. Verify with `claude mcp list` — `school-scraper` should appear.

**Acceptance criteria**:
- Inside a Claude Code session, asking "what MCP tools do you have?" shows `get_next_school`, `fetch_page`, `save_result`, and `mark_failed`.
