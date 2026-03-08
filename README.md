# School Data Collection

A locally-run tool that uses an AI agent to automatically browse school websites and collect key contact and profile information.

## What it collects

For each school, the agent finds and records:

- Head teacher name and email
- Safeguarding lead name and email
- School address
- Pupil age range (e.g. 4–18, 11–16)
- Whether the school is SEN or mainstream
- Whether the school is girls-only, boys-only, or co-educational

If a direct email for the head or safeguarding lead isn't published, it falls back to the best available general contact address.

## How it works

1. A list of schools and their URLs is loaded into a local SQLite database (`schools.db`)
2. An AI agent works through the queue, browsing each school's website autonomously
3. Everything it finds is saved to the database for later reference

## Requirements

- Python 3.13
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- A Claude Code session (to run the agent)

## Setup

```bash
# Install dependencies
uv sync

# Download the browser used for scraping
uv run playwright install chromium

# Load the school list into the database
uv run python load_schools.py
```

## Running the agent

Register the MCP server with Claude Code (one-time setup):

```bash
claude mcp add school-scraper uv --args "run,python,server.py" --cwd "path/to/this/repo"
```

Then paste the prompt from `building_docs/agent_prompt.md` into a Claude Code session to start a run.

## Project structure

```
load_schools.py        # Loads schools.csv into the database queue
server.py              # MCP server exposing tools to the AI agent
db.py                  # Database setup and connection
data_collection/       # Source CSV with school names and URLs
building_docs/         # Planning documents and implementation tickets
```

## Data

`schools.db` is not committed to this repository — it lives on your machine only.
