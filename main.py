import os
import time
import logging
import requests
import threading
from fetch_odds import get_football_odds

# Logging yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s'
)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
DROP_THRESHOLD = float(os.getenv("DROP_THRESHOLD", "0.10"))

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
            market_name = match.get('market_name', 'Bilinmeyen Market')
            
            if old_odds and new_odds and old_odds > 0 and new_odds < old_odds:
                drop_ratio = (old_odds - new_odds) / old_odds
                
                if drop_ratio >= DROP_THRESHOLD:
                    msg = f"""📉 Futbol Oran Düşüşü!
⚽ Maç: {match_name}
🏆 Market: {market_name}
📊 {old_odds} ➡ {new_odds} 
📉 Düşüş: %{int(drop_ratio*100)}"""
                    
                    send_telegram_message(msg)
        except Exception as e:
            logging.error(f"Odds işleme hatası: {e}")

def background_worker():
    while True:
        try:
            logging.info("⏳ Futbol oranları kontrol ediliyor...")
            odds_data = get_football_odds()
            
            if odds_data:
                process_odds_changes(odds_data)
            
            time.sleep(900)  # 15 dakikada bir kontrol
        
        except Exception as e:
            logging.error(f"Background worker hatası: {e}")
            time.sleep(300)  # Hata durumunda 5 dk bekle

def main():
    # Gerekli credential kontrolü
    if not all([TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID]):
        logging.error("❌ Eksik credentials!")
        return
    
    worker_thread = threading.Thread(target=background_worker, daemon=True)
    worker_thread.start()
    
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        logging.info("Uygulama kapatılıyor...")

if __name__ == "__main__":
    logging.info("🚀 Futbol Odds Takip Botu Başlatıldı!")
    main()
