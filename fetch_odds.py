import os
import requests
import logging
from datetime import datetime

# Logging ayarları
logging.basicConfig(level=logging.INFO)

THE_ODDS_API_KEY = os.environ.get("THE_ODDS_API_KEY")
BASE_URL = "https://api.the-odds-api.com/v4/sports/"
ENDPOINT = os.environ.get("ODDS_ENDPOINT", "soccer_uefa_champs_league/odds")

def get_odds_data():
    if not THE_ODDS_API_KEY:
        logging.error("❌ The Odds API Key eksik!")
        return []
    
    try:
        # Dinamik endpoint oluşturma
        url = f"{BASE_URL}{ENDPOINT}"
        
        params = {
            "apiKey": THE_ODDS_API_KEY,
            "regions": "eu",  # Avrupa bölgesi
            "markets": "h2h,spreads,totals",
            "oddsFormat": "decimal"
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        # Detaylı hata yakalama
        if response.status_code != 200:
            logging.error(f"API Çağrı Hatası: {response.status_code}")
            logging.error(f"Yanıt İçeriği: {response.text}")
            return []
        
        return parse_odds_data(response.json())
    
    except requests.RequestException as e:
        logging.error(f"API çağrısı hatası: {e}")
        return []

def parse_odds_data(raw_data):
    parsed_odds = []
    
    try:
        for match in raw_data:
            home_team = match.get('home_team', 'Bilinmeyen Takım')
            away_team = match.get('away_team', 'Bilinmeyen Takım')
            
            # Bookmaker'lar üzerinden odds'ları çekme
            for bookmaker in match.get('bookmakers', []):
                markets = bookmaker.get('markets', [])
                
                for market in markets:
                    market_name = market.get('key', 'Bilinmeyen Market')
                    
                    # Her bir sonuç için
                    for outcome in market.get('outcomes', []):
                        parsed_odds.append({
                            'match': f"{home_team} vs {away_team}",
                            'market_name': market_name,
                            'old_odds': outcome.get('price', 0) + 0.2,  # Simüle edilmiş eski oran
                            'new_odds': outcome.get('price', 0)
                        })
    
    except Exception as e:
        logging.error(f"Veriişleme hatası: {e}")
    
    return parsed_odds
