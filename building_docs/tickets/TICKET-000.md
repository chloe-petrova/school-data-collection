# TICKET-000 — Prerequisites / local environment setup

**Status**: done

---

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
