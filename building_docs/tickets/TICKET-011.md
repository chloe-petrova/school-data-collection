# TICKET-011 — HTML results viewer

**Status**: done

---

**File**: `build_html.py` (new).

**Goal**: A single Python script that generates a self-contained `results.html` from the SQLite database. Opening the HTML in a browser shows every processed school with all collected data fields.

**Tasks**:
- Query `results` for done schools and `schools_queue` for failed schools (join on URL or use both tables).
- Build a JSON array of all schools with every field from the `processed.md` format: school name, URL, head name, head email, safeguarding lead name, safeguarding lead email, best contact email, age range, address, SEN, gender, status (done/failed), fail reason.
- Embed the JSON inside a single HTML template string. Inline all CSS and JS — no external files.
- JS reads the embedded JSON array and appends a card/row for each school.
- Failed schools must be visually distinct (different background colour or border) with the fail reason displayed.
- Write the output to `results.html` in the project root.
- Add `results.html` to `.gitignore`.
- No new dependencies — stdlib only (`sqlite3`, `json`, `pathlib`).

**Acceptance criteria**:
- `uv run python build_html.py` produces `results.html` in the project root with no errors.
- Opening `results.html` in a browser displays all done and failed schools.
- Each school card shows: name, URL (clickable link), head name, head email, safeguarding lead name, safeguarding lead email, best contact email, age range, address, SEN status, gender type.
- Failed schools are visually distinct and show the fail reason.
- The file is fully self-contained — no external CSS, JS, or network requests.
- `results.html` is in `.gitignore`.
- No new entries in `pyproject.toml` dependencies.
