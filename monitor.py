import os
import time
import hashlib
import requests

URL = "https://www.yakhyeon.or.kr/app/guide/schedule.html"
STATE_FILE = "page_hash.txt"

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

def normalize(text: str) -> str:
    return " ".join(text.split())

def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def load_prev():
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        v = f.read().strip()
        return v or None

def save_now(h: str):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        f.write(h)

def fetch_html() -> str:
    headers = {"User-Agent": "Mozilla/5.0 (page-change-monitor)"}
    r = requests.get(URL, headers=headers, timeout=20)
    r.raise_for_status()
    r.encoding = r.encoding or "utf-8"
    return r.text

def send_telegram(msg: str):
    api = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(
        api,
        data={"chat_id": TELEGRAM_CHAT_ID, "text": msg},
        timeout=20
    ).raise_for_status()

def main():
    html = fetch_html()
    h = sha256(normalize(html))
    prev = load_prev()

    if prev is None:
        save_now(h)
        print("초기 기준 저장 (알림 없음)")
        return

    if h != prev:
        save_now(h)
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        send_telegram(
            f"[변경 감지]\n약현 혼배 예약 페이지에 변경이 발생했습니다.\n\nURL:\n{URL}\n\n시간: {now}"
        )
        print("변경 감지 → 텔레그램 알림 전송")
    else:
        print("변경 없음")

if __name__ == "__main__":
    main()
