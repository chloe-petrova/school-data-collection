"""
Scrape ISSC school directory to get school names and their own website URLs.
Outputs: schools.csv with columns: name, school_url, issc_id
"""
import csv
import time
import re
import urllib.request

BASE = "https://www.issc.co.uk/schools/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
}


def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode("utf-8", errors="replace")


def get_school_ids_from_page(html):
    """Extract unique (name, id) pairs from a listing page."""
    seen = set()
    schools = []
    # Each school has two links (logo + name). The name link contains meaningful text.
    for m in re.finditer(r'<a href="details\.asp\?id=(\d+)"[^>]*>\s*([^<]{4,}?)\s*</a>', html):
        school_id = m.group(1)
        name = m.group(2).strip()
        # Skip logo links (short/empty text) and duplicates
        if school_id not in seen and len(name) > 3 and not name.startswith('<'):
            schools.append((name, school_id))
            seen.add(school_id)
    return schools


def get_website_from_detail(html):
    """Extract the school's own website URL from its detail page.
    The website appears as plain text: Website:</span> www.example.com
    """
    m = re.search(r'Website:</span>\s*([^\s<]{4,})', html)
    if m:
        url = m.group(1).strip().rstrip('.,;')
        # Normalise: add https:// if missing
        if not url.startswith('http'):
            url = 'https://' + url
        return url
    return ""


def main():
    print("Fetching page 1 to find total count...")
    html = fetch(BASE + "default.asp?page=1&pagesize=100&keywords=&gradesEn=primary&regionEn=&genderEn=&residencyEn=&scholarshipsEn=&religionEn=")

    total_match = re.search(r'Total\s+([\d,]+)\s+Schools', html, re.IGNORECASE)
    total = int(total_match.group(1).replace(",", "")) if total_match else 1155
    total_pages = (total + 99) // 100
    print(f"Total schools: {total}, pages (at 100/page): {total_pages}")

    all_schools = []

    # Step 1: collect all school IDs from listing pages
    schools = get_school_ids_from_page(html)
    all_schools.extend(schools)
    print(f"  Page 1/{total_pages}: {len(schools)} schools")

    for page in range(2, total_pages + 1):
        url = BASE + f"default.asp?page={page}&pagesize=100&keywords=&gradesEn=primary&regionEn=&genderEn=&residencyEn=&scholarshipsEn=&religionEn="
        html = fetch(url)
        schools = get_school_ids_from_page(html)
        all_schools.extend(schools)
        print(f"  Page {page}/{total_pages}: {len(schools)} schools (total: {len(all_schools)})")
        time.sleep(0.3)

    print(f"\nCollected {len(all_schools)} schools. Fetching detail pages for website URLs...")

    # Step 2: fetch each detail page to get the school's own website URL
    results = []
    for i, (name, school_id) in enumerate(all_schools, 1):
        detail_url = BASE + f"details.asp?id={school_id}"
        try:
            detail_html = fetch(detail_url)
            website = get_website_from_detail(detail_html)
        except Exception as e:
            website = ""
            print(f"  Error id={school_id} ({name}): {e}")

        results.append({"name": name, "school_url": website, "issc_id": school_id})

        if i % 50 == 0 or i == len(all_schools):
            found = sum(1 for r in results if r["school_url"])
            print(f"  {i}/{len(all_schools)} done — {found} website URLs found so far")

        time.sleep(0.2)

    # Save to CSV
    out_path = "schools.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "school_url", "issc_id"])
        writer.writeheader()
        writer.writerows(results)

    found = sum(1 for r in results if r["school_url"])
    print(f"\nDone. Saved {len(results)} schools to {out_path}")
    print(f"Website URLs found: {found}/{len(results)}")
    print(f"Missing URLs: {len(results) - found}")


if __name__ == "__main__":
    main()
