# TICKET-010 — Write and test the agent run prompt

**Status**: todo

---

**Goal**: Produce the standard instruction to paste into Claude Code to run a batch, and verify the end-to-end flow works on a small sample.

**Agent prompt** (save in `building_docs/agent_prompt.md`):

```
Process the next 10 schools from the queue using the school-scraper MCP tools.

For each school:
1. Call get_next_school to get the next URL.
2. Call fetch_page on the school's homepage.
3. Look for links to pages like: About, Staff, Leadership, Safeguarding, Contact, Governors.
4. Call fetch_page on any relevant sub-pages to find:
   - Headteacher / Principal name
   - Headteacher / Principal email
   - Designated Safeguarding Lead (DSL) name
   - DSL email
   - Age range of pupils (e.g. 4–18, 11–16)
   - Full address of the school
   - Whether the school is a Special Educational Needs (SEN) school (yes / no / unknown)
   - Whether the school is girls-only, boys-only, or co-educational (girls / boys / co-ed / unknown)
5. If a specific email is not published, use the best general contact email (e.g. admin@, info@, office@).
6. If you have found all data points (or the best available), call save_result.
7. If the site is unreachable or you cannot find meaningful data after visiting 5+ pages, call mark_failed with a brief reason.

Work through all 10 schools before stopping. Be thorough but do not visit more than 8 pages per school.
```

**Test run**:
- Run the prompt against 5 schools.
- Check `results` table has rows with real data.
- Check `schools_queue` shows those 5 as `done`.

**Acceptance criteria**:
- At least 3 of 5 test schools produce a result row with a non-empty `head_name`.
- No unhandled Python exceptions in the MCP server logs.
