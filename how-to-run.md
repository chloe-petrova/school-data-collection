# How to run the school scraper

This project scrapes UK school websites to collect staff contact details (headteacher, safeguarding lead), age ranges, addresses, and other metadata. It stores everything in a local database. You can view results through a live web dashboard or a static HTML report.

---

## First-time setup

Every command below uses `uv`, a tool that manages Python and project dependencies. It isn't on the default PATH, so you first need to tell your terminal where to find it. Run this once each time you open a new terminal:

```bash
UV=/c/Users/cstow/AppData/Local/Microsoft/WinGet/Links/uv.exe
```

Then follow these steps in order:

1. **Install Python 3.13** (only needed once):
   ```bash
   $UV python install 3.13
   ```

2. **Install project dependencies** (libraries the code needs):
   ```bash
   $UV sync
   ```

3. **Install the Chromium browser** (used behind the scenes to load school websites):
   ```bash
   $UV run playwright install chromium
   ```

4. **Load schools into the database** (reads the CSV of 1,155 schools and queues them up). Safe to re-run — it won't create duplicates:
   ```bash
   $UV run python load_schools.py
   ```

Setup is done. You're ready to start scraping.

---

## Command reference

| Command | What it does |
|---|---|
| `$UV run python dashboard.py` | Starts the live dashboard at [localhost:5000](http://localhost:5000). See results update in real time. |
| `$UV run python build_html.py` | Generates a static `results.html` file — open it in your browser to see results. |
| `$UV run python load_schools.py` | Loads schools from the CSV file into the database queue. Safe to re-run. |
| `$UV run pytest` | Runs the automated tests to check everything still works. |
| `$UV run python server.py` | Starts the MCP server manually (you normally don't need to do this — Claude Code starts it automatically). |

---

## How to scrape more schools

Each run processes 10 schools. To keep going:

1. Open **Claude Code** in this project folder.
2. Open the file `building_docs/agent_prompt.md` and copy its entire contents.
3. Paste it into a new Claude Code chat.
4. Wait for the agent to finish — it will work through 10 schools, visiting each website and collecting data.
5. When it's done, check the dashboard or regenerate the HTML report to see the new results.

Repeat steps 2–5 as many times as you like. The agent picks up where it left off — it always grabs the next unprocessed school from the queue.

---

## How to view results

### Option A: Live dashboard (recommended)

Run this in your terminal:

```bash
$UV run python dashboard.py
```

Then open [localhost:5000](http://localhost:5000) in your browser. You'll see a summary bar (how many schools are pending, done, and failed) and a card for each processed school. Click **Refresh** to update the data without reloading the page.

You can leave the dashboard running while the agent scrapes — just hit Refresh to see new results as they come in.

### Option B: Static HTML report

If you prefer a single file you can share or open offline:

```bash
$UV run python build_html.py
```

Then open `results.html` in your browser. On Windows you can double-click the file, or run:

```bash
start results.html
```

Both options show the same data. Failed schools (ones where the website was unreachable or had no useful data) are highlighted in red with a reason.

---

## How to check progress

The dashboard shows pending/done/failed counts at the top of the page. If you want a quick check from the terminal without opening a browser, run:

```bash
$UV run python -c "
import sqlite3
conn = sqlite3.connect('schools.db')
rows = conn.execute('SELECT status, COUNT(*) FROM schools_queue GROUP BY status').fetchall()
for status, count in rows:
    print(f'{status}: {count}')
"
```

This prints something like:

```
done: 5
failed: 3
pending: 1147
```

---

## Troubleshooting

**"No module named playwright"** or similar import errors
— Run `$UV sync` to reinstall dependencies.

**"Executable `chromium` not found"** or browser launch errors
— Run `$UV run playwright install chromium` to reinstall the browser.

**"no such table: schools_queue"**
— The database hasn't been created yet. Run `$UV run python load_schools.py` to set it up.

**`results.html` is empty or shows 0 schools**
— No schools have been processed yet. Run the agent first (see "How to scrape more schools" above).

**`$UV` doesn't work / "command not found"**
— You need to set the shortcut each time you open a new terminal:
```bash
UV=/c/Users/cstow/AppData/Local/Microsoft/WinGet/Links/uv.exe
```
