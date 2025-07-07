import os
import time
import logging
import requests
import functools

def cached(expire_after=300):
    def decorator(func):
        cache = {}
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            current_time = time.time()
            
            if key in cache:
                result, timestamp = cache[key]
                if current_time - timestamp < expire_after:
                    return result
            
            result = func(*args, **kwargs)
            cache[key] = (result, current_time)
            return result
        return wrapper
    return decorator

API_KEY = os.environ.get("ODDS_API_KEY")
REGIONS = "eu,us,uk,au,za"
MARKETS = "h2h,totals,btts,corners,cards"
ODDS_FORMAT = "decimal"

@cached(expire_after=300)
def get_all_odds():
    if not API_KEY:
        logging.error("❌ ODDS_API_KEY eksik!")
        return {}
    
    try:
        url = "https://api.the-odds-api.com/v4/sports/?all=true"
        headers = {"Accept": "application/json"}
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        all_data = {}
        for sport in response.json():
            if not sport["key"].startswith("soccer_"):
                continue
            
            try:
                league = sport["key"]
                odds_url = f"https://api.the-odds-api.com/v4/sports/{league}/odds/"
                params = {
                    "apiKey": API_KEY,
                    "regions": REGIONS,
                    "markets": MARKETS,
                    "oddsFormat": ODDS_FORMAT
                }
                
                res = requests.get(odds_url, params=params, timeout=10)
                res.raise_for_status()
                
                if res.status_code == 200:
                    all_data[league] = parse_odds_data(res.json())
            
            except requests.RequestException as e:
                logging.error(f"League {league} odds fetch hatası: {e}")
                continue
        
        return all_data
    
    except requests.RequestException as e:
        logging.error(f"Ana API çağrısında hata: {e}")
        return {}

def parse_odds_data(matches):
    parsed = {}
    for m in matches:
        match_id = m.get("id")
        markets = m.get("bookmakers", [])
        market_data = {}
        for bm in markets:
            for market in bm.get("markets", []):
                key = market.get("key")
                outcomes = market.get("outcomes", [])
                market_data.setdefault(key, [])
                for o in outcomes:
                    market_data[key].append({
                        "label": o.get("name"),
                        "old": o.get("price") + 0.2,  # Simüle edilmiş düşüş
                        "new": o.get("price")
                    })
        parsed[match_id] = market_data
    return parsed
