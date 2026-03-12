# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

@building_docs/CONTRIBUTING.md

## What this is

A local Python MCP server that lets Claude Code scrape UK school websites for staff contacts and metadata. SQLite for storage, Playwright for headless browsing.

## Commands

`uv` is not on the bash PATH. Always use the full path:

```bash
UV=/c/Users/cstow/AppData/Local/Microsoft/WinGet/Links/uv.exe

$UV run pytest                    # all 17 tests
$UV run pytest -k <name>          # single test
$UV run python server.py          # start MCP server
$UV run python load_schools.py    # load CSV into queue (idempotent)
$UV run python dashboard.py       # live dashboard on localhost:5000
$UV run python build_html.py      # generate static results.html
$UV add <package>                 # add dependency
$UV run playwright install chromium  # reinstall browser binaries
```

## Architecture

- **`server.py`** — MCP server (`FastMCP("school-scraper")`). Four tools: `get_next_school`, `fetch_page`, `save_result`, `mark_failed`. Internal helpers prefixed `_` accept a `conn` arg for testability.
- **`db.py`** — SQLite schema + singleton connection (`get_conn()`). Two tables: `schools_queue` (work queue with status pending/in_progress/done/failed) and `results` (scraped data: 10 fields + timestamp). Auto-creates `schools.db` on first call.
- **`load_schools.py`** — One-off CSV loader. Reads `data_collection/schools.csv` (1155 schools) into `schools_queue`. Uses `INSERT OR IGNORE` so re-runs are safe.
- **`build_html.py`** — Generates a self-contained `results.html` from the database. Stdlib only.
- **`dashboard.py`** — Flask app serving a live dashboard at `localhost:5000`. Three routes: `/` (HTML page), `/api/schools` (JSON), `/api/stats` (JSON). Imports `_fetch_schools` from `build_html.py`.
- **`test_server.py`** / **`test_load_schools.py`** / **`test_dashboard.py`** — pytest suite. Server tests use in-memory SQLite. `fetch_page` tests are async (`pytest-asyncio`). Dashboard tests use Flask's test client.

## MCP registration

Already configured in `.mcp.json`. Verify: `claude mcp list` should show `school-scraper`.

## Running the agent

Paste the prompt from @building_docs/agent_prompt.md into a Claude Code session.
