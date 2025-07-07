import os
import time
import requests
from fetch_odds import get_all_odds
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Güvenli environment variable çekme
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
DROP_THRESHOLD = float(os.getenv("DROP_THRESHOLD", "0.10"))

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"🚨 Telegram mesaj hatası: {e}")

def kontrol_et():
    try:
        odds_data = get_all_odds()
        notifications = []

        for match_id, markets in odds_data.items():
            for market, entries in markets.items():
                for entry in entries:
                    old = entry.get("old")
                    new = entry.get("new")
                    label = entry.get("label")
                    
                    if old and new and old > 0 and new < old:
                        drop_ratio = (old - new) / old
                        if drop_ratio >= DROP_THRESHOLD:
                            notifications.append({
                                "market": market,
                                "label": label,
                                "old": old,
                                "new": new,
                                "drop_ratio": drop_ratio
                            })
        
        # Toplu bildirim gönderimi
        for notif in notifications:
            msg = f"""📉 Oran Düşüşü Bildirimi!
🏷️ Market: {notif['market']} ({notif['label']})
📊 {notif['old']} ➡ {notif['new']} (Düşüş: %{int(notif['drop_ratio']*100)})"""
            send_telegram_message(msg)
    
    except Exception as e:
        print(f"❌ Kontrol sırasında kritik hata: {e}")

def main():
    print("🚀 Odds Takip Botu Başlatıldı!")
    while True:
        try:
            print("⏳ Oranlar kontrol ediliyor...")
            kontrol_et()
            time.sleep(900)  # 15 dakikada bir kontrol
        except Exception as e:
            print(f"❌ Ana döngüde hata: {e}")
            time.sleep(300)  # Hata durumunda 5 dk bekle

if __name__ == "__main__":
    main()
