import re

import db
from fastmcp import FastMCP
from playwright.async_api import async_playwright

mcp = FastMCP("school-scraper")


# ---------------------------------------------------------------------------
# Helper functions (accept conn so they can be tested with in-memory SQLite)
# ---------------------------------------------------------------------------

def _get_next_school(conn):
    row = conn.execute(
        "SELECT id, name, url FROM schools_queue WHERE status = 'pending' ORDER BY id LIMIT 1"
    ).fetchone()
    if row is None:
        return {"id": None, "name": None, "url": None}
    school_id, name, url = row
    conn.execute(
        "UPDATE schools_queue SET status = 'in_progress' WHERE id = ?", (school_id,)
    )
    conn.commit()
    return {"id": school_id, "name": name, "url": url}


def _save_result(
    conn,
    queue_id,
    school_url,
    head_name,
    head_email,
    safeguarding_lead_name,
    safeguarding_lead_email,
    best_contact_email,
    age_range,
    address,
    is_sen,
    gender_type,
):
    try:
        with conn:
            conn.execute(
                """INSERT INTO results (
                    school_url, head_name, head_email,
                    safeguarding_lead_name, safeguarding_lead_email,
                    best_contact_email, age_range, address, is_sen, gender_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    school_url, head_name, head_email,
                    safeguarding_lead_name, safeguarding_lead_email,
                    best_contact_email, age_range, address, is_sen, gender_type,
                ),
            )
            conn.execute(
                "UPDATE schools_queue SET status = 'done' WHERE id = ?", (queue_id,)
            )
        return "saved"
    except Exception as e:
        return f"ERROR: {type(e).__name__}: {e}"


async def _fetch_page(url):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            )
            await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            text = await page.inner_text("body")
            await browser.close()
        text = re.sub(r"\n{3,}", "\n\n", text)
        if len(text) > 15000:
            text = text[:15000] + "\n[TRUNCATED — page was longer]"
        return text
    except Exception as e:
        return f"ERROR: {type(e).__name__}: {e}"


def _mark_failed(conn, queue_id, reason):
    conn.execute(
        "UPDATE schools_queue SET status = 'failed', fail_reason = ? WHERE id = ?",
        (reason, queue_id),
    )
    conn.commit()
    return "marked_failed"


# ---------------------------------------------------------------------------
# MCP tools
# ---------------------------------------------------------------------------

@mcp.tool()
def get_next_school() -> dict:
    return _get_next_school(db.get_conn())


@mcp.tool()
def save_result(
    queue_id: int,
    school_url: str,
    head_name: str,
    head_email: str,
    safeguarding_lead_name: str,
    safeguarding_lead_email: str,
    best_contact_email: str,
    age_range: str,
    address: str,
    is_sen: str,
    gender_type: str,
) -> str:
    return _save_result(
        db.get_conn(),
        queue_id, school_url, head_name, head_email,
        safeguarding_lead_name, safeguarding_lead_email,
        best_contact_email, age_range, address, is_sen, gender_type,
    )


@mcp.tool()
def mark_failed(queue_id: int, reason: str) -> str:
    return _mark_failed(db.get_conn(), queue_id, reason)


@mcp.tool()
async def fetch_page(url: str) -> str:
    return await _fetch_page(url)


if __name__ == "__main__":
    mcp.run()
