import re
import sys
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

FORM_URL = "https://forms.cloud.microsoft/pages/responsepage.aspx?id=fRx5_rdAYEikL8P16a9_7BIKWu-Aw7ZCq8KaGdT4awZUMFJLNEswR0tFS1MzV1ZYVVJXOTRDN1hFRi4u&route=shorturl"

DEBUG_DIR = Path("debug_screenshots")


def parse_chat_call_line(line):
    parts = [p.strip() for p in line.strip().split("=")]
    if len(parts) < 2:
        return None
    remarks = parts[1].strip()
    m = re.search(r"(\d{6,7})\s*$", parts[-1])
    if not m:
        return None
    return {"cx_id": m.group(1), "remarks": remarks}


def parse_ticket_line(line):
    parts = [p.strip() for p in line.strip().split("=")]
    if len(parts) < 2:
        return None
    remarks = parts[0].strip()
    m = re.search(r"(\d{6,7})\s*$", parts[-1])
    if not m:
        return None
    return {"cx_id": m.group(1), "remarks": remarks}


def snap(page, name):
    """Save a screenshot for debugging. Never raises."""
    try:
        DEBUG_DIR.mkdir(exist_ok=True)
        page.screenshot(path=str(DEBUG_DIR / f"{name}.png"), full_page=True)
    except Exception:
        pass


def choose_dropdown(page, label_text, option_text):
    """
    Opens a dropdown by its label and selects an option, primarily via
    Playwright's get_by_role name matching (substring, case-insensitive),
    which correctly resolves the option's real accessible name. Falls back
    to a raw inner_text scan only to build a helpful error message.
    """
    page.get_by_label(label_text).click(timeout=10000)
    page.wait_for_timeout(300)

    option = page.get_by_role("option", name=option_text)
    try:
        expect(option.first).to_be_visible(timeout=8000)
        option.first.click(timeout=10000)
        return
    except Exception:
        pass

    all_option_texts = page.get_by_role("option").all_inner_texts()
    raise RuntimeError(
        f"Could not find option containing {option_text!r} in dropdown {label_text!r}. "
        f"Raw inner texts on the options found: {all_option_texts}"
    )


def choose_radio(page, option_text):
    """
    Selects a radio button by accessible name, using Playwright's own
    get_by_role name-matching (substring, case-insensitive by default).
    This correctly resolves labels linked via aria-labelledby / <label for=...>,
    which a manual aria-label/inner_text read on the radio element itself
    misses (that's why a hand-rolled version returned blank names).
    """
    radio = page.get_by_role("radio", name=option_text)
    try:
        expect(radio.first).to_be_visible(timeout=10000)
        radio.first.click(timeout=10000)
        return
    except Exception:
        pass

    # Fallback: click the visible label text directly, then locate the
    # radio physically nearest it (handles cases where the label text
    # isn't wired into the accessible name at all).
    try:
        label = page.get_by_text(option_text, exact=True)
        expect(label.first).to_be_visible(timeout=5000)
        label.first.click(timeout=10000)
        return
    except Exception as e:
        all_radio_names = page.get_by_role("radio").all_inner_texts()
        raise RuntimeError(
            f"Could not find or click radio option {option_text!r}. "
            f"Raw inner texts on the radios found: {all_radio_names}. "
            f"Original error: {e}"
        )


def wait_branch_ready(page, mode):
    if mode in ("chats", "calls"):
        expect(page.get_by_label("Chat/Call Status")).to_be_visible(timeout=15000)
    elif mode == "tickets":
        expect(page.get_by_label("Ticket Dept")).to_be_visible(timeout=15000)


def fill_common(page, record):
    choose_dropdown(page, "WL STAFF", "Suresh")
    page.get_by_label("CX ID").fill(record["cx_id"])


def submit_chat(page, record):
    page.goto(FORM_URL, wait_until="domcontentloaded")
    page.wait_for_load_state("networkidle")
    fill_common(page, record)
    choose_radio(page, "Chat")  # confirmed exact label: "Chat"
    wait_branch_ready(page, "chats")
    choose_dropdown(page, "Chat/Call Status", "Resolved: Self")
    page.get_by_label("Remarks (Support Requested for)").fill(record["remarks"])
    page.get_by_role("button", name="Submit").click(timeout=10000)
    page.wait_for_timeout(1500)


def submit_call(page, record):
    page.goto(FORM_URL, wait_until="domcontentloaded")
    page.wait_for_load_state("networkidle")
    fill_common(page, record)
    choose_radio(page, "Call")  # confirmed exact label: "Call" (not "Calls")
    wait_branch_ready(page, "calls")
    choose_dropdown(page, "Chat/Call Status", "Resolved: Self")
    page.get_by_label("Remarks (Support Requested for)").fill(record["remarks"])
    page.get_by_role("button", name="Submit").click(timeout=10000)
    page.wait_for_timeout(1500)


def submit_ticket(page, record):
    page.goto(FORM_URL, wait_until="domcontentloaded")
    page.wait_for_load_state("networkidle")
    fill_common(page, record)
    choose_radio(page, "Ticket")  # confirmed exact label: "Ticket" (not "Tickets")
    wait_branch_ready(page, "tickets")
    choose_dropdown(page, "Ticket Dept", "Windows")
    # Match loosely on "On Hold" + "Resolved" so a spelling variant
    # ("Awaiting" vs "Awating") in the live form doesn't break this.
    choose_dropdown(page, "Ticket Status", "On Hold")
    page.get_by_label("Remarks (Support Requested for)").fill(record["remarks"])
    page.get_by_role("button", name="Submit").click(timeout=10000)
    page.wait_for_timeout(1500)


def load_records(mode):
    p = Path(f"{mode}.txt")
    if not p.exists():
        return []
    records = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        if mode in ("chats", "calls"):
            rec = parse_chat_call_line(line)
        else:
            rec = parse_ticket_line(line)
        if rec:
            records.append(rec)
    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["chats", "calls", "tickets"])
    parser.add_argument("--headed", action="store_true", help="Show the browser window")
    parser.add_argument("--slowmo", type=int, default=0, help="Slow down actions by N ms")
    args = parser.parse_args()

    records = load_records(args.mode)
    if not records:
        print(f"No valid records found in {args.mode}.txt")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.headed, slow_mo=args.slowmo)
        page = browser.new_page(viewport={"width": 1400, "height": 1200})

        failures = 0
        for i, record in enumerate(records, 1):
            try:
                if args.mode == "chats":
                    submit_chat(page, record)
                elif args.mode == "calls":
                    submit_call(page, record)
                else:
                    submit_ticket(page, record)
                print(f"Submitted {i}/{len(records)}: {args.mode} {record['cx_id']}")
            except Exception as e:
                failures += 1
                snap(page, f"{args.mode}_fail_{i}_{record.get('cx_id', 'unknown')}")
                print(f"Failed record {i}: {record} -> {e}", file=sys.stderr)

        browser.close()

        if failures:
            print(
                f"\n{failures} record(s) failed. Screenshots saved in "
                f"'{DEBUG_DIR}/' — open them to see exactly what the page "
                f"looked like at the moment of failure."
            )


if __name__ == "__main__":
    main()
