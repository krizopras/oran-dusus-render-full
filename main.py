import os
import time
import logging
import requests
import threading
from fetch_odds import get_all_odds

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
        logging.info(f"Telegram bildirimi gönderildi: {message[:50]}...")
    except Exception as e:
        logging.error(f"Telegram mesaj hatası: {e}")

def ping_self():
    try:
        render_url = os.environ.get("RENDER_EXTERNAL_URL", "https://example.com")
        while True:
            try:
                requests.get(render_url, timeout=10)
                logging.info("🌐 Self ping başarılı")
            except Exception as e:
                logging.error(f"Ping hatası: {e}")
            time.sleep(300)  # 5 dakikada bir ping
    except Exception as e:
        logging.error(f"Ping mekanizması hatası: {e}")

def background_worker():
    while True:
        try:
            logging.info("⏳ Oranlar kontrol ediliyor...")
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
📊 {old} ➡ {new} (Düşüş: %{int(drop_ratio*100)})"""
                                send_telegram_message(msg)
            
            time.sleep(900)  # 15 dakikada bir kontrol
        
        except Exception as e:
            logging.error(f"Background worker hatası: {e}")
            time.sleep(300)  # Hata durumunda 5 dk bekle

def main():
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logging.error("❌ Telegram credentials eksik!")
        return
    
    # Ping thread'i
    ping_thread = threading.Thread(target=ping_self, daemon=True)
    ping_thread.start()
    
    # Background worker thread'i
    worker_thread = threading.Thread(target=background_worker, daemon=True)
    worker_thread.start()
    
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        logging.info("Uygulama kapatılıyor...")

if __name__ == "__main__":
    logging.info("🚀 Bot başlatıldı!")
    main()
