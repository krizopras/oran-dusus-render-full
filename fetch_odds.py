import os
import requests
import logging
from datetime import datetime, timedelta

# Logging ayarı
logging.basicConfig(level=logging.INFO)

SPORTMONKS_API_TOKEN = os.environ.get("SPORTMONKS_API_TOKEN")
BASE_URL = "https://api.sportmonks.com/v3"

def get_sportmonks_odds():
    if not SPORTMONKS_API_TOKEN:
        logging.error("❌ Sportmonks API Token eksik!")
        return []
    
    try:
        # Güncel ve yaklaşan maçlar için tarih aralığı
        today = datetime.now()
        next_week = today + timedelta(days=7)
        
        headers = {
            "Authorization": f"Bearer {SPORTMONKS_API_TOKEN}",
            "Accept": "application/json"
        }
        
        # Futbol maçları için endpoint
        url = f"{BASE_URL}/football/fixtures"
        
        params = {
            "filter[date_from]": today.strftime("%Y-%m-%d"),
            "filter[date_to]": next_week.strftime("%Y-%m-%d"),
            "include": "odds",
            "page": 1
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code != 200:
            logging.error(f"API Çağrı Hatası: {response.status_code}")
            return []
        
        return parse_odds_data(response.json())
    
    except requests.RequestException as e:
        logging.error(f"API çağrısı hatası: {e}")
        return []

def parse_odds_data(raw_data):
    parsed_odds = []
    
    try:
        fixtures = raw_data.get('data', [])
        
        for fixture in fixtures:
            # Maç bilgileri
            home_team = fixture.get('localTeam', {}).get('name', 'Bilinmeyen Takım')
            away_team = fixture.get('visitorTeam', {}).get('name', 'Bilinmeyen Takım')
            
            # Odds bilgileri
            odds = fixture.get('odds', [])
            
            for odd in odds:
                market_name = f"{home_team} vs {away_team}"
                
                parsed_odds.append({
                    'market_name': market_name,
                    'old_odds': odd.get('bookmaker', {}).get('probability', {}).get('home', 0),
                    'new_odds': odd.get('bookmaker', {}).get('probability', {}).get('away', 0)
                })
    
    except Exception as e:
        logging.error(f"Veri işleme hatası: {e}")
    
    return parsed_odds

# Test için mock veri
def mock_odds_data():
    return [
        {
            'market_name': 'Sample Match',
            'old_odds': 2.0,
            'new_odds': 1.8
        }
    ]
