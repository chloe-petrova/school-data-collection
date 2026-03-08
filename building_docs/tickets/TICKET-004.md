# TICKET-004 — MCP tool: `get_next_school`

**Status**: todo

---

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
