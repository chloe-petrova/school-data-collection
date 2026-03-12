# School Data Collection

A tool that scrapes UK school websites to collect staff contact details, safeguarding leads, age ranges, addresses, and other metadata. It uses Claude Code as the AI agent that reads each school's website and extracts the information.

Data is stored in a local SQLite database and can be viewed through a live web dashboard or a static HTML report.

## What it collects

For each school:
- Headteacher / Principal name and email
- Designated Safeguarding Lead (DSL) name and email
- General contact email
- Pupil age range (e.g. 4–11, 11–16)
- Full postal address
- Whether the school is SEN (Special Educational Needs)
- Whether the school is girls-only, boys-only, or co-educational

If a direct email for the head or safeguarding lead isn't published, it falls back to the best available general contact address.

## Setup

You need [uv](https://docs.astral.sh/uv/) and [Claude Code](https://claude.ai/code) installed.

```bash
# Install Python and dependencies
uv sync

# Install the browser used for scraping
uv run playwright install chromium

# Load the list of 1,155 schools into the database
uv run python load_schools.py
```

## Commands

| Command | What it does |
|---|---|
| `uv run python dashboard.py` | Start the live dashboard at [localhost:5000](http://localhost:5000) |
| `uv run python build_html.py` | Generate a static `results.html` report |
| `uv run python load_schools.py` | Load schools from CSV into the database (safe to re-run) |
| `uv run pytest` | Run all tests |

## How to scrape schools

The scraping is done by an AI agent running inside Claude Code. Each run processes 10 schools.

1. Open Claude Code in this project folder.
2. Copy the contents of `building_docs/agent_prompt.md` and paste it into a new chat.
3. Wait for the agent to finish — it visits each school's website and extracts the data.
4. Repeat as many times as you like. The agent always picks up where it left off.

## Viewing results

**Live dashboard** — run `uv run python dashboard.py` and open [localhost:5000](http://localhost:5000). Shows all processed schools with a summary bar and a Refresh button.

**Static report** — run `uv run python build_html.py` then open `results.html` in your browser.

## How it works

1. A list of schools and their URLs is loaded into a local SQLite database (`schools.db`).
2. An AI agent works through the queue, browsing each school's website autonomously using Playwright.
3. Everything it finds is saved to the database.
4. The dashboard or static report reads from the database and displays the results.

## Project structure

| File | Purpose |
|---|---|
| `server.py` | MCP server with 4 tools the AI agent uses |
| `db.py` | SQLite database schema and connection |
| `load_schools.py` | Loads the school list from CSV into the database |
| `dashboard.py` | Live web dashboard (Flask) |
| `build_html.py` | Static HTML report generator |
| `data_collection/schools.csv` | Source list of 1,155 UK schools |

## Data

`schools.db` is not committed to this repository — it lives on your machine only.
