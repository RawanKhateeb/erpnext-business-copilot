import os
import re
from playwright.sync_api import Page, expect


# -----------------------
# Helpers
# -----------------------

def get_base_url():
    return os.getenv("BASE_URL", "https://wiser-rosina-vaulted.ngrok-free.dev")


def click_mode(page: Page, mode_text: str):
    btn = page.get_by_role("button", name=mode_text)

    if btn.count() > 0:
        expect(btn.first).to_be_visible(timeout=20000)
        btn.first.click()
        return

    tab = page.get_by_text(mode_text, exact=False)
    expect(tab.first).to_be_visible(timeout=20000)
    tab.first.click()


def fill_query(page: Page, text: str):
    tb = page.get_by_role("textbox")

    if tb.count() > 0:
        expect(tb.first).to_be_visible(timeout=20000)
        tb.first.fill(text)
        return

    candidates = [
        page.locator('input[placeholder*="Show"]').first,
        page.locator("input").first,
        page.locator("textarea").first,
    ]

    for c in candidates:
        try:
            if c.count() > 0:
                expect(c).to_be_visible(timeout=20000)
                c.fill(text)
                return
        except Exception:
            continue

    page.screenshot(path="ui_debug_input.png", full_page=True)
    raise AssertionError("Could not find query input")


def click_ask(page: Page):
    ask_btn = page.get_by_role("button", name="Ask")
    expect(ask_btn).to_be_visible(timeout=20000)
    ask_btn.click()


# -----------------------
# Tests
# -----------------------

def test_e2e_data_mode_ask_question(page: Page):
    """
    E2E: Data -> Ask -> Results
    (Already working test)
    """
    page.goto(get_base_url(), wait_until="load")

    click_mode(page, "Data")
    fill_query(page, "Show purchase orders")
    click_ask(page)

    # Results visible
    expect(page.get_by_text("Displaying", exact=False)).to_be_visible(timeout=30000)


def test_export_pdf_download(page: Page):
    """
    Feature: Export PDF download works
    """
    page.goto(get_base_url(), wait_until="load")

    click_mode(page, "Data")
    fill_query(page, "Show purchase orders")
    click_ask(page)

    expect(page.get_by_text("Displaying", exact=False)).to_be_visible(timeout=30000)

    # ✅ Click specifically "Export as PDF"
    export_pdf_btn = page.get_by_role(
        "button",
        name=re.compile(r"export\s+as\s+pdf", re.I)
    )

    expect(export_pdf_btn).to_be_visible(timeout=20000)

    with page.expect_download(timeout=30000) as download_info:
        export_pdf_btn.click()

    download = download_info.value
    filename = download.suggested_filename.lower()
    assert filename.endswith(".pdf"), f"Expected PDF file, got: {filename}"
