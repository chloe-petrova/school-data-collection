import sqlite3

_conn = None


def init_db(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS schools_queue (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            issc_id     TEXT,
            name        TEXT,
            url         TEXT NOT NULL,
            status      TEXT NOT NULL DEFAULT 'pending',
            fail_reason TEXT,
            queued_at   TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS results (
            id                      INTEGER PRIMARY KEY AUTOINCREMENT,
            school_name             TEXT,
            school_url              TEXT NOT NULL,
            head_name               TEXT,
            head_email              TEXT,
            safeguarding_lead_name  TEXT,
            safeguarding_lead_email TEXT,
            best_contact_email      TEXT,
            age_range               TEXT,
            address                 TEXT,
            is_sen                  TEXT,
            gender_type             TEXT,
            collected_at            TEXT DEFAULT (datetime('now'))
        );
    """)
    conn.commit()


def get_conn():
    global _conn
    if _conn is None:
        _conn = sqlite3.connect("schools.db", check_same_thread=False)
        init_db(_conn)
    return _conn


if __name__ == "__main__":
    get_conn()
    print("schools.db created with tables: schools_queue, results")
