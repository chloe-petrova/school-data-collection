# TICKET-007 — MCP tool: `mark_failed`

**Status**: done

---

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
