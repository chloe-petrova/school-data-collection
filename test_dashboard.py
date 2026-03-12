import sqlite3

import pytest

from db import init_db
from dashboard import app, DB_PATH


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Create a test client with an in-memory-like temp database."""
    db_file = tmp_path / "test.db"
    monkeypatch.setattr("dashboard.DB_PATH", db_file)

    conn = sqlite3.connect(str(db_file))
    init_db(conn)

    # Insert some test data
    conn.execute(
        "INSERT INTO schools_queue (id, name, url, status) VALUES (1, 'Good School', 'https://good.example.com', 'done')"
    )
    conn.execute(
        "INSERT INTO schools_queue (id, name, url, status, fail_reason) VALUES (2, 'Bad School', 'https://bad.example.com', 'failed', 'Site unreachable')"
    )
    conn.execute(
        "INSERT INTO schools_queue (id, name, url, status) VALUES (3, 'Pending School', 'https://pending.example.com', 'pending')"
    )
    conn.execute(
        """INSERT INTO results (school_url, head_name, head_email,
           safeguarding_lead_name, safeguarding_lead_email,
           best_contact_email, age_range, address, is_sen, gender_type)
           VALUES ('https://good.example.com', 'Jane Smith', 'jane@good.example.com',
           'Bob Jones', 'bob@good.example.com', 'office@good.example.com',
           '4-11', '1 School Lane', 'no', 'co-ed')"""
    )
    conn.commit()
    conn.close()

    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_api_schools_returns_done_and_failed(client):
    resp = client.get("/api/schools")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 2  # 1 done + 1 failed

    done = [s for s in data if s["status"] == "done"]
    failed = [s for s in data if s["status"] == "failed"]
    assert len(done) == 1
    assert len(failed) == 1

    assert done[0]["school_name"] == "Good School"
    assert done[0]["head_name"] == "Jane Smith"

    assert failed[0]["school_name"] == "Bad School"
    assert failed[0]["fail_reason"] == "Site unreachable"


def test_api_stats_returns_counts(client):
    resp = client.get("/api/stats")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["done"] == 1
    assert data["failed"] == 1
    assert data["pending"] == 1
    assert data["total"] == 3


def test_index_returns_html(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"School Scraper Dashboard" in resp.data
