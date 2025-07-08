import os
import time
import logging
import requests
import threading
from fastapi import FastAPI
from fetch_odds import get_football_odds

app = FastAPI()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s: %(message)s"
)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DROP_THRESHOLD = float(os.getenv("DROP_THRESHOLD", "0.20"))

@app.get("/")
def root():
    return {"status": "Oran botu aktif!"}

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        r = requests.post(url, data=data, timeout=10)
        r.raise_for_status()
        logging.info("Telegram bildirimi gönderildi.")
    except Exception as e:
        logging.error(f"Telegram gönderim hatası: {e}")

def process_odds_changes(odds_data):
    for match in odds_data:
        try:
            match_name = match.get('match', 'Bilinmeyen Maç')
            bookmaker = match.get('bookmaker', 'Bilinmeyen')
            market_name = match.get('market_name', 'Bilinmeyen Market')
            outcome_name = match.get('outcome_name', 'Bilinmeyen Sonuç')
            old_odds = match.get('old_odds')
            new_odds = match.get('new_odds')

            if old_odds and new_odds and old_odds > new_odds:
                drop_ratio = (old_odds - new_odds) / old_odds
                if drop_ratio >= DROP_THRESHOLD:
                    msg = f"""📉 Oran Düşüşü!
🏟️ Maç: {match_name}
🏦 Site: {bookmaker}
🎯 Bahis Tipi: {market_name} - {outcome_name}
📊 Oran: {old_odds} ➡ {new_odds}
📉 Düşüş: %{int(drop_ratio*100)}"""
                    send_telegram_message(msg)
        except Exception as e:
            logging.error(f"İşleme hatası: {e}")

def background_worker():
    while True:
        try:
            logging.info("Oranlar kontrol ediliyor...")
            odds = get_football_odds()
            if odds:
                process_odds_changes(odds)
            time.sleep(5400)  # 90 dakika = 5400 saniye
        except Exception as e:
            logging.error(f"Arka plan hatası: {e}")
            time.sleep(300)

threading.Thread(target=background_worker, daemon=True).start()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
