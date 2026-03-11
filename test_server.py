import sqlite3
import pytest
import db
from server import _get_next_school, _save_result, _mark_failed, _fetch_page


def _make_db():
    conn = sqlite3.connect(":memory:")
    db.init_db(conn)
    return conn


def _seed(conn, schools):
    """Insert schools as pending rows. schools: list of (name, url) tuples."""
    for name, url in schools:
        conn.execute(
            "INSERT INTO schools_queue (name, url) VALUES (?, ?)", (name, url)
        )
    conn.commit()


# ---------------------------------------------------------------------------
# get_next_school
# ---------------------------------------------------------------------------

def test_get_next_school_returns_first_pending():
    conn = _make_db()
    _seed(conn, [("School A", "https://a.com"), ("School B", "https://b.com")])

    result = _get_next_school(conn)

    assert result["name"] == "School A"
    assert result["url"] == "https://a.com"
    assert isinstance(result["id"], int)


def test_get_next_school_marks_school_in_progress():
    conn = _make_db()
    _seed(conn, [("School A", "https://a.com")])

    result = _get_next_school(conn)

    status = conn.execute(
        "SELECT status FROM schools_queue WHERE id = ?", (result["id"],)
    ).fetchone()[0]
    assert status == "in_progress"


def test_get_next_school_second_call_returns_different_school():
    conn = _make_db()
    _seed(conn, [("School A", "https://a.com"), ("School B", "https://b.com")])

    first = _get_next_school(conn)
    second = _get_next_school(conn)

    assert first["id"] != second["id"]


def test_get_next_school_returns_nulls_when_queue_empty():
    conn = _make_db()

    result = _get_next_school(conn)

    assert result == {"id": None, "name": None, "url": None}


# ---------------------------------------------------------------------------
# save_result
# ---------------------------------------------------------------------------

def test_save_result_marks_queue_done():
    conn = _make_db()
    _seed(conn, [("School A", "https://a.com")])
    school = _get_next_school(conn)

    _save_result(
        conn,
        queue_id=school["id"],
        school_url=school["url"],
        head_name="Jane Smith",
        head_email="j.smith@a.com",
        safeguarding_lead_name="Bob Jones",
        safeguarding_lead_email="b.jones@a.com",
        best_contact_email="office@a.com",
        age_range="11-18",
        address="1 School Lane",
        is_sen="no",
        gender_type="co-ed",
    )

    status = conn.execute(
        "SELECT status FROM schools_queue WHERE id = ?", (school["id"],)
    ).fetchone()[0]
    assert status == "done"


def test_save_result_inserts_results_row():
    conn = _make_db()
    _seed(conn, [("School A", "https://a.com")])
    school = _get_next_school(conn)

    _save_result(
        conn,
        queue_id=school["id"],
        school_url=school["url"],
        head_name="Jane Smith",
        head_email="",
        safeguarding_lead_name="",
        safeguarding_lead_email="",
        best_contact_email="office@a.com",
        age_range="",
        address="",
        is_sen="unknown",
        gender_type="unknown",
    )

    row = conn.execute(
        "SELECT school_url, head_name FROM results WHERE school_url = ?",
        (school["url"],),
    ).fetchone()
    assert row is not None
    assert row[0] == "https://a.com"
    assert row[1] == "Jane Smith"


def test_save_result_returns_saved():
    conn = _make_db()
    _seed(conn, [("School A", "https://a.com")])
    school = _get_next_school(conn)

    result = _save_result(
        conn,
        queue_id=school["id"],
        school_url=school["url"],
        head_name="",
        head_email="",
        safeguarding_lead_name="",
        safeguarding_lead_email="",
        best_contact_email="",
        age_range="",
        address="",
        is_sen="unknown",
        gender_type="unknown",
    )

    assert result == "saved"


# ---------------------------------------------------------------------------
# mark_failed
# ---------------------------------------------------------------------------

def test_mark_failed_sets_status_and_reason():
    conn = _make_db()
    _seed(conn, [("School A", "https://a.com")])
    school = _get_next_school(conn)

    _mark_failed(conn, queue_id=school["id"], reason="Could not load page")

    row = conn.execute(
        "SELECT status, fail_reason FROM schools_queue WHERE id = ?", (school["id"],)
    ).fetchone()
    assert row[0] == "failed"
    assert row[1] == "Could not load page"


def test_mark_failed_returns_marked_failed():
    conn = _make_db()
    _seed(conn, [("School A", "https://a.com")])
    school = _get_next_school(conn)

    result = _mark_failed(conn, queue_id=school["id"], reason="Timeout")

    assert result == "marked_failed"


# ---------------------------------------------------------------------------
# fetch_page
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_fetch_page_returns_readable_text():
    result = await _fetch_page("https://example.com")

    assert "Example Domain" in result
    assert "<" not in result  # no HTML tags


@pytest.mark.asyncio
async def test_fetch_page_returns_error_for_bad_url():
    result = await _fetch_page("https://nonexistent.invalid")

    assert result.startswith("ERROR:")
