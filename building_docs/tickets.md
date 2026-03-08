# Implementation Tickets

> **Context**: `schools.csv` already exists in `data_collection/` with 1155 schools (columns: `name, school_url, issc_id`). Step 6 of the technical plan is complete.

---

## TICKET-000 — Prerequisites / local environment setup

**Goal**: Ensure Python and `uv` are installed on the machine before any code is written.

**Why `uv`**: `uv` is a modern Python package and project manager (replaces `pip` + `venv`). It is significantly faster, handles virtual environments automatically, and is now the standard for new Python projects.

### 1. Install Python 3.11+

Check if already installed:
```
python --version
```
If missing or below 3.11, install via winget:
```
winget install Python.Python.3.11
```
After install, close and reopen the terminal. Confirm with `python --version`.

### 2. Install `uv`

```
winget install astral-sh.uv
```
Or via PowerShell if winget is unavailable:
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Confirm with: `uv --version`

### 3. SQLite

No install needed — SQLite ships with Python's standard library.

### 4. Playwright browsers

Playwright itself is installed as a Python package (TICKET-001). The browser binaries are downloaded separately as part of TICKET-001.

**Acceptance criteria**:
- `python --version` shows 3.11 or higher
- `uv --version` runs successfully

---

## TICKET-001 — Project scaffolding

**Goal**: Initialise the `uv` project, install dependencies, and download Playwright browser binaries.

**Tasks**:

```bash
# From the project root (chlobo_is_a_spammer/)
uv init --no-readme       # creates pyproject.toml and .venv automatically
uv add fastmcp playwright # adds deps and installs them into the venv
uv run playwright install chromium  # downloads Chromium browser binary
```

`uv init` creates a `pyproject.toml` (replaces `requirements.txt`) and manages the `.venv` automatically — no manual `python -m venv` or `pip install` needed.

**File layout after this ticket**:
```
chlobo_is_a_spammer/
├── building_docs/
├── data_collection/
│   ├── schools.csv
│   └── scrape_issc.py
├── .venv/
├── pyproject.toml
├── db.py            (TICKET-002)
├── load_schools.py  (TICKET-003)
└── server.py        (TICKET-004 to 008)
```

**Acceptance criteria**:
- `uv run python -c "import fastmcp; import playwright"` runs without error
- `pyproject.toml` exists and lists `fastmcp` and `playwright` as dependencies

---

## TICKET-002 — Database initialisation module (`db.py`)

**Goal**: Create a module that, on import, ensures the SQLite database and both tables exist.

**File**: `db.py` in project root.

**Database file**: `schools.db` in project root (created automatically).

**Schema**:

```sql
CREATE TABLE IF NOT EXISTS schools_queue (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    issc_id     TEXT,
    name        TEXT,
    url         TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'pending',  -- pending | in_progress | done | failed
    fail_reason TEXT,
    queued_at   TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS results (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    school_name             TEXT,
    school_url              TEXT NOT NULL,
    head_name               TEXT,
    head_email              TEXT,
    safeguarding_lead_name  TEXT,
    safeguarding_lead_email TEXT,
    best_contact_email      TEXT,
    age_range               TEXT,
    address                 TEXT,
    is_sen                  TEXT,  -- 'yes' | 'no' | 'unknown'
    gender_type             TEXT,  -- 'girls' | 'boys' | 'co-ed' | 'unknown'
    collected_at            TEXT DEFAULT (datetime('now'))
);
```

**Implementation notes**:
- `db.py` should expose a single `get_conn()` function that returns a `sqlite3.Connection` and calls `init_db()` on first use.
- `init_db()` runs both `CREATE TABLE IF NOT EXISTS` statements.
- Use `check_same_thread=False` on the connection since fastmcp may be async.

**Acceptance criteria**:
- Running `uv run python db.py` creates `schools.db` with both tables visible via `sqlite3 schools.db .schema`.

---

## TICKET-003 — CSV loader script (`load_schools.py`)

**Goal**: One-off script that reads `data_collection/schools.csv` and inserts all schools with a non-empty URL into `schools_queue` as `pending`. Safe to re-run (skips already-queued URLs).

**File**: `load_schools.py` in project root.

**Logic**:
1. Open `data_collection/schools.csv`.
2. For each row: skip if `school_url` is empty or whitespace.
3. Insert into `schools_queue` (`issc_id`, `name`, `url`) using `INSERT OR IGNORE` (add a `UNIQUE` constraint on `url` in the schema, or check existence first).
4. Print a summary: how many inserted, how many skipped (already present or no URL).

**Schema change**: Add `UNIQUE(url)` to `schools_queue` in `db.py` so duplicate loads are safe.

**Acceptance criteria**:
- Running `uv run python load_schools.py` populates `schools_queue` with ~1100+ rows (some source rows have blank URLs — those are skipped).
- Running it a second time inserts 0 new rows.
- `SELECT COUNT(*) FROM schools_queue WHERE status = 'pending';` returns the expected count.

---

## TICKET-004 — MCP tool: `get_next_school`

**File**: `server.py` (started in this ticket, extended in subsequent ones).

**Goal**: Expose a tool that returns the next pending school and atomically marks it `in_progress`.

**Tool signature**:
```python
@mcp.tool()
def get_next_school() -> dict:
    ...
```

**Returns** (as dict):
```json
{
  "id": 42,
  "name": "Example School",
  "url": "https://www.example-school.co.uk"
}
```
Returns `{"id": null, "name": null, "url": null}` if the queue is empty.

**Logic**:
1. `SELECT id, name, url FROM schools_queue WHERE status = 'pending' ORDER BY id LIMIT 1`
2. If found: `UPDATE schools_queue SET status = 'in_progress' WHERE id = ?`
3. Return the row.

**Acceptance criteria**:
- Calling the tool returns the first pending school and marks it `in_progress` in the DB.
- A second call returns the next pending school (not the same one).
- When queue is empty, returns nulls gracefully.

---

## TICKET-005 — MCP tool: `fetch_page`

**File**: `server.py` (add to existing).

**Goal**: Expose a tool that fetches a URL using Playwright and returns clean visible text content.

**Tool signature**:
```python
@mcp.tool()
async def fetch_page(url: str) -> str:
    ...
```

**Returns**: The visible text content of the page (not raw HTML). On failure, returns an error string starting with `"ERROR:"`.

**Implementation notes**:
- Use `async_playwright` context manager.
- Launch `chromium` in headless mode.
- `page.goto(url, timeout=30000, wait_until="domcontentloaded")`
- Extract text via `page.inner_text("body")` — gives human-readable text without markup noise.
- Strip excessive blank lines (collapse 3+ newlines to 2).
- Truncate output to 15,000 characters to keep Claude's context manageable. Add a note at the end if truncated: `"\n[TRUNCATED — page was longer]"`.
- Catch all exceptions and return `f"ERROR: {type(e).__name__}: {e}"`.
- Set a realistic user-agent string to avoid bot-blocking.

**Acceptance criteria**:
- `fetch_page("https://example.com")` returns readable text containing "Example Domain".
- `fetch_page("https://nonexistent.invalid")` returns a string starting with `"ERROR:"`.
- Output is plain text with no HTML tags.

---

## TICKET-006 — MCP tool: `save_result`

**File**: `server.py` (add to existing).

**Goal**: Expose a tool that saves extracted data for a school and marks it done.

**Tool signature**:
```python
@mcp.tool()
def save_result(
    queue_id: int,
    school_url: str,
    head_name: str,
    head_email: str,
    safeguarding_lead_name: str,
    safeguarding_lead_email: str,
    best_contact_email: str,
    age_range: str,
    address: str,
    is_sen: str,
    gender_type: str,
) -> str:
    ...
```

**Returns**: `"saved"` on success, or an error string on failure.

**Logic**:
1. `INSERT INTO results (...) VALUES (...)`
2. `UPDATE schools_queue SET status = 'done' WHERE id = ?`

**Notes**:
- All fields except `queue_id` and `school_url` may be empty strings if not found. Do not reject them.
- `is_sen` should be `"yes"`, `"no"`, or `"unknown"`. `gender_type` should be `"girls"`, `"boys"`, `"co-ed"`, or `"unknown"`.
- Wrap in a transaction so both writes succeed or both fail.

**Acceptance criteria**:
- After calling `save_result`, the row in `schools_queue` has `status = 'done'` and a matching row exists in `results`.

---

## TICKET-007 — MCP tool: `mark_failed`

**File**: `server.py` (add to existing).

**Goal**: Expose a tool that marks a school as failed with a reason.

**Tool signature**:
```python
@mcp.tool()
def mark_failed(queue_id: int, reason: str) -> str:
    ...
```

**Returns**: `"marked_failed"` on success.

**Logic**:
1. `UPDATE schools_queue SET status = 'failed', fail_reason = ? WHERE id = ?`

**Acceptance criteria**:
- After calling `mark_failed`, the row has `status = 'failed'` and the `fail_reason` column contains the provided reason.

---

## TICKET-008 — Wire up the MCP server entry point

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

---

## TICKET-009 — Register the MCP server with Claude Code

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

---

## TICKET-010 — Write and test the agent run prompt

**Goal**: Produce the standard instruction to paste into Claude Code to run a batch, and verify the end-to-end flow works on a small sample.

**Agent prompt** (save in `building_docs/agent_prompt.md`):

```
Process the next 10 schools from the queue using the school-scraper MCP tools.

For each school:
1. Call get_next_school to get the next URL.
2. Call fetch_page on the school's homepage.
3. Look for links to pages like: About, Staff, Leadership, Safeguarding, Contact, Governors.
4. Call fetch_page on any relevant sub-pages to find:
   - Headteacher / Principal name
   - Headteacher / Principal email
   - Designated Safeguarding Lead (DSL) name
   - DSL email
   - Age range of pupils (e.g. 4–18, 11–16)
   - Full address of the school
   - Whether the school is a Special Educational Needs (SEN) school (yes / no / unknown)
   - Whether the school is girls-only, boys-only, or co-educational (girls / boys / co-ed / unknown)
5. If a specific email is not published, use the best general contact email (e.g. admin@, info@, office@).
6. If you have found all data points (or the best available), call save_result.
7. If the site is unreachable or you cannot find meaningful data after visiting 5+ pages, call mark_failed with a brief reason.

Work through all 10 schools before stopping. Be thorough but do not visit more than 8 pages per school.
```

**Test run**:
- Run the prompt against 5 schools.
- Check `results` table has rows with real data.
- Check `schools_queue` shows those 5 as `done`.

**Acceptance criteria**:
- At least 3 of 5 test schools produce a result row with a non-empty `head_name`.
- No unhandled Python exceptions in the MCP server logs.

---

## Implementation order

```
TICKET-000 → TICKET-001 → TICKET-002 → TICKET-003
                                            ↓
                    TICKET-004, 005, 006, 007 (can be done in one sitting, all in server.py)
                                            ↓
                                      TICKET-008
                                            ↓
                                      TICKET-009
                                            ↓
                                      TICKET-010
```
