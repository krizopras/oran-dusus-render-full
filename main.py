import os
import time
import threading
import requests
from fastapi import FastAPI
import uvicorn

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("CHAT_ID")
DROP_THRESHOLD = float(os.getenv("DROP_THRESHOLD", "0.10"))

from fetch_odds import get_all_odds  # senin dosyadan geliyor

app = FastAPI()

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
                        msg = f"📉 Oran Düşüşü!\n\n🏷️ Market: {market} ({label})\n💰 {old} → {new} (%{int(drop_ratio * 100)})"
                        send_telegram_message(msg)

def bot_thread():
    while True:
        kontrol_et()
        time.sleep(900)  # 15 dakika

@app.get("/")
def root():
    return {"status": "Oran botu çalışıyor."}

# Arka plan thread'i başlat
threading.Thread(target=bot_thread, daemon=True).start()

# Lokal test için: uvicorn main:app --host 0.0.0.0 --port 10000
