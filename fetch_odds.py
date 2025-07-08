import requests
import os

API_KEY = os.getenv("ODDS_API_KEY")
REGIONS = "eu"
MARKETS = "h2h,totals,spreads"
ODDS_URL = "https://api.the-odds-api.com/v4/sports"

def get_football_odds():
    try:
        sports_resp = requests.get(f"{ODDS_URL}?all=true&apiKey={API_KEY}")
        sports_resp.raise_for_status()
        sports_data = sports_resp.json()
        football_keys = [s["key"] for s in sports_data if s["group"] == "Soccer" and s["active"]]

        result = []
        for sport_key in football_keys:
            url = f"{ODDS_URL}/{sport_key}/odds/?apiKey={API_KEY}&regions={REGIONS}&markets={MARKETS}&oddsFormat=decimal"
            try:
                resp = requests.get(url, timeout=10)
                if resp.status_code != 200:
                    continue
                data = resp.json()
                for match in data:
                    match_name = match.get("home_team", "") + " vs " + match.get("away_team", "")
                    for bookmaker in match.get("bookmakers", []):
                        for market in bookmaker.get("markets", []):
                            for outcome in market.get("outcomes", []):
                                old_price = outcome.get("last_update_price", outcome.get("price"))
                                new_price = outcome.get("price")
                                if old_price and new_price and new_price < old_price:
                                    result.append({
                                        "match": match_name,
                                        "market_name": market["key"],
                                        "label": outcome["name"],
                                        "old_odds": old_price,
                                        "new_odds": new_price,
                                        "site": bookmaker["title"],
                                        "home_team": match.get("home_team"),
                                        "away_team": match.get("away_team")
                                    })
            except:
                continue
        return result
    except Exception as e:
        print("Ana API çağrısında hata:", e)
        return []
