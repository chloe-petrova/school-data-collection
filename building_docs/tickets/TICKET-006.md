# TICKET-006 — MCP tool: `save_result`

**Status**: done

---

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
