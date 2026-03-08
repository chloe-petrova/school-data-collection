# Technical Implementation

## Architecture Decision

We will build a local MCP (Model Context Protocol) server in Python. Claude Code connects to this server and uses its tools to do all the work — browsing school websites, reading content, and saving results. Claude Code itself acts as the intelligent agent; the MCP server just gives it hands.

This means:
- No separate AI API key or subscription needed beyond Claude Code
- Everything runs locally on your machine
- Claude Code navigates websites intelligently, not with rigid scraping rules
- Simple to set up and extend

---

## What We Are Building

A Python MCP server that exposes four tools to Claude Code:

1. **get_next_school** — reads the next unprocessed school from the input list and returns its URL
2. **fetch_page** — takes a URL, opens it in a headless browser (Playwright), and returns the page's text content
3. **save_result** — saves the extracted data for one school into the SQLite database
4. **mark_failed** — records that a school could not be processed, with a reason

Claude Code calls these tools in sequence for each school, deciding which pages to visit, what the data means, and when it has found everything it needs.

---

## Step-by-Step Implementation Plan

### Step 1 — Set up the Python project

Create a folder for the project. Inside it, create a virtual environment and install three dependencies: `fastmcp` (the MCP server framework), `playwright` (headless browser), and the standard `sqlite3` library (built into Python, no install needed). Then run the Playwright installer to download the browser binaries.

### Step 2 — Create the SQLite database schema

When the MCP server starts for the first time, it creates two tables:

- **schools_queue** — one row per school, with columns for the URL, status (pending / done / failed), and a timestamp
- **results** — one row per successfully processed school, with columns for: school URL, head name, head email, safeguarding lead name, safeguarding lead email, best contact email (fallback), age range, address, SEN status (yes/no/unknown), gender type (girls/boys/co-ed/unknown), and the date collected

### Step 3 — Load the school list

Before running, populate the `schools_queue` table from the input source. The input will be a CSV file with one school URL per row. A simple one-off script reads the CSV and inserts each URL as a pending row. This only needs to be done once.

### Step 4 — Build the MCP server

Write a single Python file that defines the MCP server and its four tools:

- `get_next_school` queries the database for the next row where status is pending, marks it as in-progress, and returns the URL to Claude Code
- `fetch_page` takes a URL, launches a Playwright browser instance, navigates to the URL, waits for the page to load, and returns the visible text content (not raw HTML — plain text is easier for Claude to read)
- `save_result` takes the school URL and the nine data fields as arguments and writes them to the results table, then marks the school as done in the queue
- `mark_failed` updates the school's status to failed in the queue and records the reason

### Step 5 — Register the MCP server with Claude Code

Add the MCP server to Claude Code's configuration file so that when Claude Code starts, it automatically connects to the local server and the tools become available.

### Step 6 — Prepare the school URL list

Obtain the list of UK independent school URLs. The simplest approach: use a session of Claude Code to visit the source website containing the list of schools, extract the names and find their websites, and write them to a CSV file. This CSV is then loaded into the queue in Step 3.

### Step 7 — Run the agent

Open Claude Code and ask it to process the school queue. Give it a simple instruction like: "Process the next 20 schools from the queue. For each one, fetch the website, navigate to the relevant pages (About, Staff, Safeguarding, Contact), extract the head's name, head's email, safeguarding lead's name, and safeguarding lead's email, then save the result. If you cannot find a specific email, use the best general contact email instead. If the site is unreachable or the data cannot be found, mark it as failed."

Claude Code will then loop through the schools, calling the MCP tools as needed, until the batch is done.

The instruction should ask it to collect: head name, head email, safeguarding lead name, safeguarding lead email, age range, address, SEN status, and gender type.

---

## Data Flow

```
CSV file
  → loaded into SQLite queue (once)
    → Claude Code calls get_next_school
      → Claude Code calls fetch_page (one or more pages per school)
        → Claude Code reads content and extracts data
          → Claude Code calls save_result or mark_failed
            → next school
```

---

## Output

The SQLite database will contain a `results` table that can be exported to CSV at any time for use in Excel, Google Sheets, or any other tool. Each row represents one school with all data points (or the best available fallback where a field cannot be found).

---

## What We Are NOT Building

- No web UI or dashboard
- No scheduling or background daemon
- No authentication or user accounts
- No cloud hosting
- No complex error recovery — failed schools are simply marked and skipped

---

## Dependencies Summary

| Dependency | Purpose |
|---|---|
| Python 3.11+ | Runtime |
| fastmcp | MCP server framework |
| playwright | Headless browser for fetching pages |
| sqlite3 | Local database (built into Python) |
