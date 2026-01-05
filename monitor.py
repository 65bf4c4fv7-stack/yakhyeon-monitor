import os
import time
import hashlib
from playwright.sync_api import sync_playwright

URL = "https://www.yakhyeon.or.kr/app/guide/schedule.html"
STATE_FILE = "page_hash.txt"

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def load_prev():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def save_now(h: str):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        f.write(h)

def fetch_rendered_html() -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, timeout=60000)
        page.wait_for_timeout(5000)  # JS 렌더링 대기
        content = page.content()
        browser.close()
        return content

def send_telegram(msg: str):
    import requests
    api = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(api, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=20)

def main():
    html = fetch_rendered_html()
    h = sha256(" ".join(html.split()))
    prev = load_prev()

    if prev is None:
        save_now(h)
        return

    if h != prev:
        save_now(h)
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        send_telegram(
            f"[변경 감지]\n약현 혼배 예약 페이지에 변경이 발생했습니다.\n\n{URL}\n\n시간: {now}"
        )

if __name__ == "__main__":
    main()
