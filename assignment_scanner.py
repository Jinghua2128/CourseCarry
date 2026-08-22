from urllib.parse import urljoin, urlparse, parse_qs

from playwright.sync_api import Page, Error as PlaywrightError

from coursecarry.utils.url_security import is_same_https_origin, require_same_https_origin


LMS_BASE = "https://nplms.polite.edu.sg"


def extract_query_value(url, key):
    parsed = urlparse(url)
    values = parse_qs(parsed.query).get(key)

    if values:
        return values[0]

    return None


def navigate_with_sso(page: Page, url: str):
    """
    Navigate to an NP Brightspace page.

    NP may redirect through Microsoft SSO during navigation.
    Playwright can interpret that redirect as an interrupted goto,
    so we allow the redirect and then inspect the resulting page.
    """

    require_same_https_origin(url, LMS_BASE)
    print("\nOpening the secure LMS page…")

    try:
        page.goto(
            url,
            wait_until="commit",
            timeout=60000,
        )

    except PlaywrightError as error:
        message = str(error)

        if "interrupted by another navigation" in message:
            print("SSO redirect detected...")
        else:
            raise

    # Give Microsoft / Brightspace redirects time to happen
    page.wait_for_timeout(3000)

    print(f"\nCurrent site: {urlparse(page.url).hostname or 'unknown'}")

    # Microsoft login detected
    if "login.microsoftonline.com" in page.url:
        print()
        print("=" * 60)
        print("Microsoft / NP login required")
        print("=" * 60)
        print()
        print("Complete the normal login in the Chrome window.")
        print("Complete MFA if requested.")

        input(
            "\nWhen login is complete, press Enter here..."
        )

        # After authentication, explicitly request the destination again.
        try:
            page.goto(
                url,
                wait_until="commit",
                timeout=60000,
            )

        except PlaywrightError as error:
            if "interrupted by another navigation" not in str(error):
                raise

        page.wait_for_timeout(3000)

    print(f"\nFinal site: {urlparse(page.url).hostname or 'unknown'}")

    return page


def scan_assignments(page: Page, course):
    course_id = course["id"]

    assignments_url = (
        f"{LMS_BASE}/d2l/lms/dropbox/user/"
        f"folders_list.d2l?ou={course_id}&isprv=0"
    )

    print()
    print("=" * 60)
    print(f"Scanning assignments: {course['name']}")
    print("=" * 60)

    navigate_with_sso(
        page,
        assignments_url,
    )

    # Make sure we actually arrived at Brightspace.
    if not is_same_https_origin(page.url, LMS_BASE):
        print()
        print("ERROR: Could not reach NP LMS.")
        return []

    page.wait_for_timeout(2000)

    links = page.locator(
        'a[href*="folders_history.d2l"]'
    )

    count = links.count()

    print()
    print(
        f"Submission-history links found: {count}"
    )

    assignments = []

    for i in range(count):
        link = links.nth(i)

        href = link.get_attribute("href")

        if not href:
            continue

        title = link.get_attribute("title") or ""
        text = link.inner_text().strip()

        assignment_id = extract_query_value(
            href,
            "db",
        )

        assignment_name = title

        prefix = "Submission history for "

        if assignment_name.startswith(prefix):
            assignment_name = assignment_name[
                len(prefix):
            ]

        history_url = urljoin(LMS_BASE, href)
        if not is_same_https_origin(history_url, LMS_BASE):
            continue

        assignments.append(
            {
                "name": assignment_name,
                "assignment_id": assignment_id,
                "course_id": course_id,
                "history_url": history_url,
                "summary": text,
            }
        )

    return assignments
