import os
import time
import logging
import requests
import threading
from fastapi import FastAPI
from fetch_odds import get_football_odds

app = FastAPI()

# Logging yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s'
)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
DROP_THRESHOLD = float(os.getenv("DROP_THRESHOLD", "0.20"))

@app.get("/")
def root():
    return {"status": "Oran botu çalışıyor."}

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
        logging.info(f"Telegram bildirimi: {message[:50]}...")
    except Exception as e:
        logging.error(f"Telegram mesaj hatası: {e}")

def process_odds_changes(odds_data):
    for match in odds_data:
        try:
            old_odds = match.get('old_odds')
            new_odds = match.get('new_odds')
            match_name = match.get('match', 'Bilinmeyen Maç')
            market_key = match.get('market_name', 'unknown')
            label_raw = match.get('label', 'Seçim')
            bookmaker_name = match.get('site', 'Bilinmeyen Site')
            home_team = match.get("home_team", "")
            away_team = match.get("away_team", "")

            if old_odds and new_odds and old_odds > 0 and new_odds < old_odds:
                drop_ratio = (old_odds - new_odds) / old_odds
                if drop_ratio >= DROP_THRESHOLD:
                    # Bahis tipi belirleme
                    if market_key == "h2h":
                        market_name = "MS"
                        if label_raw == home_team:
                            label = "MS 1"
                        elif label_raw == away_team:
                            label = "MS 2"
                        else:
                            label = "MS 0"
                    elif market_key == "totals":
                        market_name = "Alt/Üst"
                        label = label_raw
                    elif market_key == "spreads":
                        market_name = "Handikap"
                        label = label_raw
                    else:
                        market_name = market_key
                        label = label_raw

                    msg = f"""📉 Oran Düşüşü Tespit Edildi!
🏢 Site: {bookmaker_name}
⚽ Maç: {match_name}
🎯 Bahis Tipi: {market_name}
🏷️ Seçenek: {label}
📊 Oran: {old_odds} ➡ {new_odds}
📉 Düşüş: %{int(drop_ratio * 100)}"""
                    send_telegram_message(msg)
        except Exception as e:
            logging.error(f"Odds işleme hatası: {e}")

def background_worker():
    while True:
        try:
            logging.info("⏳ Oranlar kontrol ediliyor...")
            odds_data = get_football_odds()
            if odds_data:
                process_odds_changes(odds_data)
            time.sleep(900)  # 15 dk
        except Exception as e:
            logging.error(f"Background worker hatası: {e}")
            time.sleep(300)

threading.Thread(target=background_worker, daemon=True).start()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
