# TICKET-002 — Database initialisation module (`db.py`)

**Status**: done

---

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
