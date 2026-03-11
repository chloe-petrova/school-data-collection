# Implementation Tickets

> **Context**: `schools.csv` already exists in `data_collection/` with 1155 schools (columns: `name, school_url, issc_id`). Step 6 of the technical plan is complete.

Individual ticket files are in `building_docs/tickets/`.

---

## Ticket index

| Ticket | Title | Status |
|---|---|---|
| [TICKET-000](tickets/TICKET-000.md) | Prerequisites / local environment setup | done |
| [TICKET-001](tickets/TICKET-001.md) | Project scaffolding | done |
| [TICKET-002](tickets/TICKET-002.md) | Database initialisation module (`db.py`) | done |
| [TICKET-003](tickets/TICKET-003.md) | CSV loader script (`load_schools.py`) | done |
| [TICKET-004](tickets/TICKET-004.md) | MCP tool: `get_next_school` | done |
| [TICKET-005](tickets/TICKET-005.md) | MCP tool: `fetch_page` | todo |
| [TICKET-006](tickets/TICKET-006.md) | MCP tool: `save_result` | done |
| [TICKET-007](tickets/TICKET-007.md) | MCP tool: `mark_failed` | done |
| [TICKET-008](tickets/TICKET-008.md) | Wire up the MCP server entry point | done |
| [TICKET-009](tickets/TICKET-009.md) | Register the MCP server with Claude Code | todo |
| [TICKET-010](tickets/TICKET-010.md) | Write and test the agent run prompt | todo |

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
