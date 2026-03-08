import csv
from pathlib import Path

import db


def load_csv(conn, csv_path):
    """Read schools from csv_path and insert pending rows into schools_queue.

    Returns (inserted, skipped) where skipped counts rows with no URL plus
    rows whose URL is already in the queue.
    """
    inserted = 0
    skipped = 0

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = row.get("school_url", "").strip()
            if not url:
                skipped += 1
                continue

            cursor = conn.execute(
                "INSERT OR IGNORE INTO schools_queue (issc_id, name, url) VALUES (?, ?, ?)",
                (row.get("issc_id"), row.get("name"), url),
            )
            if cursor.rowcount == 1:
                inserted += 1
            else:
                skipped += 1

    conn.commit()
    return inserted, skipped


if __name__ == "__main__":
    csv_path = Path(__file__).parent / "data_collection" / "schools.csv"
    conn = db.get_conn()
    inserted, skipped = load_csv(conn, csv_path)
    print(f"Done: {inserted} inserted, {skipped} skipped.")
