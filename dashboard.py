"""Live web dashboard for school scraper results."""

import sqlite3
from pathlib import Path

from flask import Flask, jsonify

from build_html import _fetch_schools

DB_PATH = Path(__file__).parent / "schools.db"

app = Flask(__name__)


def _get_conn():
    return sqlite3.connect(str(DB_PATH))


def _get_stats(conn):
    rows = conn.execute(
        "SELECT status, COUNT(*) FROM schools_queue GROUP BY status"
    ).fetchall()
    counts = {status: count for status, count in rows}
    return {
        "pending": counts.get("pending", 0) + counts.get("in_progress", 0),
        "done": counts.get("done", 0),
        "failed": counts.get("failed", 0),
        "total": sum(counts.values()),
    }


@app.route("/api/schools")
def api_schools():
    conn = _get_conn()
    schools = _fetch_schools(conn)
    conn.close()
    return jsonify(schools)


@app.route("/api/stats")
def api_stats():
    conn = _get_conn()
    stats = _get_stats(conn)
    conn.close()
    return jsonify(stats)


HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>School Scraper Dashboard</title>
<style>
  *, *::before, *::after { box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    margin: 0; padding: 24px; background: #f5f5f5; color: #1a1a1a;
  }
  header { display: flex; align-items: center; gap: 16px; margin-bottom: 16px; flex-wrap: wrap; }
  h1 { margin: 0; }
  .refresh-btn {
    padding: 8px 16px; border: 1px solid #2563eb; background: #2563eb; color: #fff;
    border-radius: 6px; cursor: pointer; font-size: 0.9rem;
  }
  .refresh-btn:hover { background: #1d4ed8; }
  .stats {
    display: flex; gap: 12px; margin-bottom: 24px; flex-wrap: wrap;
  }
  .stat {
    background: #fff; border: 1px solid #ddd; border-radius: 8px;
    padding: 12px 20px; text-align: center; min-width: 100px;
  }
  .stat .number { font-size: 1.6rem; font-weight: 700; }
  .stat .label { font-size: 0.8rem; color: #666; text-transform: uppercase; }
  .stat.done .number { color: #22543d; }
  .stat.failed .number { color: #9b2c2c; }
  .stat.pending .number { color: #744210; }
  .cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 16px; }
  .card {
    background: #fff; border: 1px solid #ddd; border-radius: 8px;
    padding: 16px; overflow-wrap: break-word;
  }
  .card.failed { background: #fff5f5; border-color: #e53e3e; }
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
<header>
  <h1>School Scraper Dashboard</h1>
  <button class="refresh-btn" onclick="loadAll()">Refresh</button>
</header>
<div class="stats" id="stats"></div>
<div class="cards" id="cards"></div>
<script>
function esc(s) { return s ? s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/"/g,"&quot;") : ""; }

function renderStats(data) {
  document.getElementById("stats").innerHTML =
    '<div class="stat"><div class="number">' + data.total + '</div><div class="label">Total</div></div>' +
    '<div class="stat done"><div class="number">' + data.done + '</div><div class="label">Done</div></div>' +
    '<div class="stat failed"><div class="number">' + data.failed + '</div><div class="label">Failed</div></div>' +
    '<div class="stat pending"><div class="number">' + data.pending + '</div><div class="label">Pending</div></div>';
}

function renderSchools(schools) {
  var container = document.getElementById("cards");
  container.innerHTML = "";
  schools.forEach(function(s) {
    var card = document.createElement("div");
    card.className = "card" + (s.status === "failed" ? " failed" : "");

    var badge = '<span class="badge ' + s.status + '">' + s.status + '</span>';
    var name = esc(s.school_name) || "Unknown school";
    var url = s.school_url
      ? '<a href="' + esc(s.school_url) + '" target="_blank">' + esc(s.school_url) + '</a>'
      : "";

    var fields = "";
    function add(label, value) {
      if (value) fields += '<div class="field"><span class="label">' + label + ':</span> ' + esc(value) + '</div>';
    }
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
      fields += '<div class="field"><span class="label">Fail reason:</span> ' + esc(s.fail_reason) + '</div>';
    }

    card.innerHTML = badge + '<h2>' + name + '</h2>' +
      (url ? '<div class="field">' + url + '</div>' : "") + fields;
    container.appendChild(card);
  });
}

function loadAll() {
  fetch("/api/stats").then(function(r) { return r.json(); }).then(renderStats);
  fetch("/api/schools").then(function(r) { return r.json(); }).then(renderSchools);
}

loadAll();
</script>
</body>
</html>
"""


@app.route("/")
def index():
    return HTML


if __name__ == "__main__":
    app.run(debug=False, port=5000)
