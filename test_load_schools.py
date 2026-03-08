import sqlite3
import pytest


def _make_db():
    conn = sqlite3.connect(":memory:")
    conn.executescript("""
        CREATE TABLE schools_queue (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            issc_id     TEXT,
            name        TEXT,
            url         TEXT NOT NULL UNIQUE,
            status      TEXT NOT NULL DEFAULT 'pending',
            fail_reason TEXT,
            queued_at   TEXT DEFAULT (datetime('now'))
        );
    """)
    return conn


def test_loads_schools_with_valid_urls(tmp_path):
    csv_file = tmp_path / "schools.csv"
    csv_file.write_text("name,school_url,issc_id\nSchool A,https://a.com,1\nSchool B,https://b.com,2\n")

    from load_schools import load_csv

    conn = _make_db()
    inserted, skipped = load_csv(conn, csv_file)

    assert inserted == 2
    assert skipped == 0
    rows = conn.execute("SELECT status FROM schools_queue").fetchall()
    assert all(r[0] == "pending" for r in rows)


def test_skips_rows_with_empty_urls(tmp_path):
    csv_file = tmp_path / "schools.csv"
    csv_file.write_text(
        "name,school_url,issc_id\n"
        "School A,,1\n"
        "School B,   ,2\n"
        "School C,https://c.com,3\n"
    )

    from load_schools import load_csv

    conn = _make_db()
    inserted, skipped = load_csv(conn, csv_file)

    assert inserted == 1
    assert skipped == 2


def test_second_run_inserts_nothing(tmp_path):
    csv_file = tmp_path / "schools.csv"
    csv_file.write_text("name,school_url,issc_id\nSchool A,https://a.com,1\n")

    from load_schools import load_csv

    conn = _make_db()
    load_csv(conn, csv_file)
    inserted, skipped = load_csv(conn, csv_file)

    assert inserted == 0
    assert skipped == 1
