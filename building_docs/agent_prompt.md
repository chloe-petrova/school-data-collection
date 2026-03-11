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
8. After each school (whether saved or failed), append the results to `processed.md` in the project root. Use this format:

   ```
   ## School Name
   - **URL**: ...
   - **Head name**: ...
   - **Head email**: ...
   - **Safeguarding lead name**: ...
   - **Safeguarding lead email**: ...
   - **Best contact email**: ...
   - **Age range**: ...
   - **Address**: ...
   - **SEN**: yes / no / unknown
   - **Gender**: girls / boys / co-ed / unknown
   - **Status**: done / failed
   - **Fail reason**: (if failed)
   ```

Work through all 10 schools before stopping. Be thorough but do not visit more than 8 pages per school.
