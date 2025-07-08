import os
import requests
import logging

API_KEY = os.getenv("ODDS_API_KEY")

SOCCER_KEYS = [
    "soccer_epl", "soccer_germany_bundesliga", "soccer_italy_serie_a",
    "soccer_spain_la_liga", "soccer_france_ligue_one", "soccer_netherlands_eredivisie",
    "soccer_turkey_super_league", "soccer_portugal_primeira_liga", "soccer_belgium_first_div",
    "soccer_spl", "soccer_denmark_superliga", "soccer_norway_eliteserien",
    "soccer_sweden_allsvenskan", "soccer_switzerland_superleague"
]

BOOKMAKER_NAME = "bet365"

last_odds_cache = {}

def get_football_odds():
    matches_to_alert = []
    headers = {"Accept": "application/json"}

    for sport_key in SOCCER_KEYS:
        url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/?apiKey={API_KEY}&regions=eu&markets=h2h&oddsFormat=decimal"

        try:
            r = requests.get(url, headers=headers, timeout=10)
            r.raise_for_status()
            data = r.json()

            for game in data:
                match_name = f"{game['home_team']} vs {game['away_team']}"
                for bookmaker in game.get("bookmakers", []):
                    if bookmaker["key"] != BOOKMAKER_NAME:
                        continue
                    for market in bookmaker.get("markets", []):
                        if market["key"] != "h2h":
                            continue
                        for outcome in market.get("outcomes", []):
                            key = f"{match_name}-{market['key']}-{outcome['name']}"
                            new_odd = outcome["price"]
                            old_odd = last_odds_cache.get(key)
                            if old_odd and new_odd < old_odd:
                                matches_to_alert.append({
                                    "match": match_name,
                                    "bookmaker": bookmaker["title"],
                                    "market_name": market["key"].upper(),  # "H2H"
                                    "outcome_name": outcome["name"],  # "Draw" / "Team"
                                    "old_odds": old_odd,
                                    "new_odds": new_odd
                                })
                            last_odds_cache[key] = new_odd
        except Exception as e:
            logging.error(f"Ana API çağrısında hata: {e}")
    return matches_to_alert
