# TICKET-001 — Project scaffolding

**Status**: done

---

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
