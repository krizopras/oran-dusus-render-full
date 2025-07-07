import os
import requests
import logging
from datetime import datetime

# Logging ayarları
logging.basicConfig(level=logging.INFO)

THE_ODDS_API_KEY = os.environ.get("THE_ODDS_API_KEY")
BASE_URL = "https://api.the-odds-api.com/v4/sports/"

def get_football_odds():
    if not THE_ODDS_API_KEY:
        logging.error("❌ The Odds API Key eksik!")
        return []
    
    # Futbol ligi endpoint'leri
    football_leagues = [
        "soccer_uefa_champs_league",
        "soccer_epl",
        "soccer_uefa_europa_league",
        "soccer_spain_la_liga"
    ]
    
    all_parsed_odds = []
    
    for league in football_leagues:
        try:
            url = f"{BASE_URL}{league}/odds"
            
            params = {
                "apiKey": THE_ODDS_API_KEY,
                "regions": "eu",  # Avrupa bölgesi
                "markets": "h2h,spreads,totals",
                "oddsFormat": "decimal"
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            # Detaylı hata yakalama
            if response.status_code != 200:
                logging.error(f"{league} için API Çağrı Hatası: {response.status_code}")
                continue
            
            # Her bir lig için odds'ları parse et
            league_odds = parse_football_odds(response.json(), league)
            all_parsed_odds.extend(league_odds)
        
        except requests.RequestException as e:
            logging.error(f"{league} için API çağrısı hatası: {e}")
    
    return all_parsed_odds

def parse_football_odds(raw_data, league):
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
                            'league': league,
                            'market_name': market_name,
                            'old_odds': outcome.get('price', 0) + 0.2,  # Simüle edilmiş eski oran
                            'new_odds': outcome.get('price', 0)
                        })
    
    except Exception as e:
        logging.error(f"{league} için veri işleme hatası: {e}")
    
    return parsed_odds
