# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

@building_docs/CONTRIBUTING.md

## Project intent and architecture

See @building_docs/intent.md and @building_docs/technical_implementation.md.

## Implementation tickets

See @building_docs/tickets_index.md for status and build order. Individual tickets are in `building_docs/tickets/`.

`schools.csv` already exists — Step 6 of the technical plan is complete. All other tickets are `todo`.

## Package manager

This project uses `uv`. All Python commands go through `uv run`.

```bash
uv add fastmcp playwright          # install deps
uv run playwright install chromium # download browser binaries
uv run python server.py            # run the MCP server
uv run python load_schools.py      # one-off: load CSV into SQLite queue
```

## MCP server registration

```bash
claude mcp add school-scraper uv --args "run,python,server.py" --cwd "c:/Users/cstow/cm_code/chlobo_is_a_spammer"
```

Verify: `claude mcp list` — should show `school-scraper` with tools `get_next_school`, `fetch_page`, `save_result`, `mark_failed`.

## Running the agent

Paste the prompt from @building_docs/agent_prompt.md into a Claude Code session (created in TICKET-010).
