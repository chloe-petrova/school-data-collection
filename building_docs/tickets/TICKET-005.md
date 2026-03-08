# TICKET-005 — MCP tool: `fetch_page`

**Status**: todo

---

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
