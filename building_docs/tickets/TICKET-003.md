# TICKET-003 — CSV loader script (`load_schools.py`)

**Status**: done

---

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
