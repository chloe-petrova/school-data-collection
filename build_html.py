"""Generate a self-contained results.html from the SQLite database."""

import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "schools.db"
OUTPUT_PATH = Path(__file__).parent / "results.html"


def _fetch_schools(conn):
    """Return a list of dicts for all done and failed schools."""
    conn.row_factory = sqlite3.Row

    done = conn.execute("""
        SELECT
            q.name   AS school_name,
            r.school_url,
            r.head_name,
            r.head_email,
            r.safeguarding_lead_name,
            r.safeguarding_lead_email,
            r.best_contact_email,
            r.age_range,
            r.address,
            r.is_sen,
            r.gender_type,
            'done'   AS status,
            NULL     AS fail_reason
        FROM results r
        LEFT JOIN schools_queue q ON q.url = r.school_url
    """).fetchall()

    failed = conn.execute("""
        SELECT
            name        AS school_name,
            url         AS school_url,
            NULL        AS head_name,
            NULL        AS head_email,
            NULL        AS safeguarding_lead_name,
            NULL        AS safeguarding_lead_email,
            NULL        AS best_contact_email,
            NULL        AS age_range,
            NULL        AS address,
            NULL        AS is_sen,
            NULL        AS gender_type,
            'failed'    AS status,
            fail_reason
        FROM schools_queue
        WHERE status = 'failed'
    """).fetchall()

    return [dict(row) for row in done] + [dict(row) for row in failed]


HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>School Scraper Results</title>
<style>
  *, *::before, *::after { box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    margin: 0; padding: 24px; background: #f5f5f5; color: #1a1a1a;
  }
  h1 { margin: 0 0 8px; }
  .summary { color: #555; margin-bottom: 24px; }
  .cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 16px; }
  .card {
    background: #fff; border: 1px solid #ddd; border-radius: 8px;
    padding: 16px; overflow-wrap: break-word;
  }
  .card.failed {
    background: #fff5f5; border-color: #e53e3e;
  }
  .card h2 { margin: 0 0 8px; font-size: 1.1rem; }
  .card a { color: #2563eb; }
  .field { margin: 4px 0; font-size: 0.9rem; }
  .field .label { font-weight: 600; }
  .badge {
    display: inline-block; padding: 2px 8px; border-radius: 4px;
    font-size: 0.8rem; font-weight: 600; margin-bottom: 8px;
  }
  .badge.done { background: #c6f6d5; color: #22543d; }
  .badge.failed { background: #fed7d7; color: #9b2c2c; }
</style>
</head>
<body>
<h1>School Scraper Results</h1>
<p class="summary" id="summary"></p>
<div class="cards" id="cards"></div>
<script>
const DATA = __DATA__;

document.getElementById("summary").textContent =
  DATA.length + " schools (" +
  DATA.filter(s => s.status === "done").length + " done, " +
  DATA.filter(s => s.status === "failed").length + " failed)";

const container = document.getElementById("cards");

DATA.forEach(s => {
  const card = document.createElement("div");
  card.className = "card" + (s.status === "failed" ? " failed" : "");

  const badge = '<span class="badge ' + s.status + '">' + s.status + '</span>';
  const name = s.school_name || "Unknown school";
  const url = s.school_url
    ? '<a href="' + s.school_url.replace(/"/g, "&quot;") + '" target="_blank">' +
      s.school_url.replace(/</g, "&lt;") + '</a>'
    : "";

  let fields = "";
  const add = (label, value) => {
    if (value) fields += '<div class="field"><span class="label">' + label + ':</span> ' +
      value.replace(/</g, "&lt;") + '</div>';
  };

  add("Head name", s.head_name);
  add("Head email", s.head_email);
  add("Safeguarding lead", s.safeguarding_lead_name);
  add("Safeguarding lead email", s.safeguarding_lead_email);
  add("Best contact email", s.best_contact_email);
  add("Age range", s.age_range);
  add("Address", s.address);
  add("SEN", s.is_sen);
  add("Gender", s.gender_type);
  if (s.status === "failed" && s.fail_reason) {
    fields += '<div class="field"><span class="label">Fail reason:</span> ' +
      s.fail_reason.replace(/</g, "&lt;") + '</div>';
  }

  card.innerHTML = badge +
    '<h2>' + name.replace(/</g, "&lt;") + '</h2>' +
    (url ? '<div class="field">' + url + '</div>' : "") +
    fields;

  container.appendChild(card);
});
</script>
</body>
</html>
"""


def main():
    conn = sqlite3.connect(str(DB_PATH))
    schools = _fetch_schools(conn)
    conn.close()

    html = HTML_TEMPLATE.replace("__DATA__", json.dumps(schools, ensure_ascii=False))
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(f"Wrote {len(schools)} schools to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
