import os
import time
import requests
from fetch_odds import get_all_odds

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
DROP_THRESHOLD = float(os.getenv("DROP_THRESHOLD", "0.10"))

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Telegram mesaj hatası:", e)

def kontrol_et():
    odds_data = get_all_odds()
    for match_id, markets in odds_data.items():
        for market, entries in markets.items():
            for entry in entries:
                old = entry.get("old")
                new = entry.get("new")
                label = entry.get("label")
                if old and new and old > 0 and new < old:
                    drop_ratio = (old - new) / old
                    if drop_ratio >= DROP_THRESHOLD:
                        msg = f"""📉 Oran Düşüşü!
🏷️ Market: {market} ({label})
📊 {old} ➡ {new} (%{int(drop_ratio*100)})"""
                        send_telegram_message(msg)

if __name__ == "__main__":
    while True:
        print("⏳ Oranlar kontrol ediliyor...")
        kontrol_et()
        time.sleep(900)
