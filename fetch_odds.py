
import requests
import os
import logging

API_KEY = os.getenv("ODDS_API_KEY")
REGIONS = "eu,uk"
MARKETS = "h2h,totals,spreads"
ODDS_FORMAT = "decimal"

EUROPEAN_LEAGUES = [
    "soccer_uefa_champs_league", "soccer_uefa_europa_league", "soccer_uefa_euro_qualification",
    "soccer_uefa_nations_league", "soccer_uefa_conference_league", "soccer_europe_euro",
    "soccer_england_premier_league", "soccer_england_championship", "soccer_germany_bundesliga",
    "soccer_germany_bundesliga2", "soccer_spain_la_liga", "soccer_spain_segunda_division",
    "soccer_italy_serie_a", "soccer_italy_serie_b", "soccer_france_ligue_one",
    "soccer_france_ligue_two", "soccer_netherlands_eredivisie", "soccer_portugal_primeira_liga",
    "soccer_turkey_super_league", "soccer_sweden_allsvenskan", "soccer_norway_eliteserien",
    "soccer_denmark_superliga", "soccer_finland_veikkausliiga", "soccer_belgium_first_div",
    "soccer_switzerland_superleague", "soccer_austria_bundesliga", "soccer_czech_republic_first_league",
    "soccer_poland_ekstraklasa", "soccer_slovakia_superliga", "soccer_slovenia_prva_liga",
    "soccer_hungary_nb_i", "soccer_romania_liga_i", "soccer_croatia_1hnl",
    "soccer_serbia_super_liga", "soccer_bulgaria_first_league", "soccer_russia_premier_league",
    "soccer_ukraine_premier_league", "soccer_estonia_meistriliiga", "soccer_latvia_virsliga",
    "soccer_lithuania_a_lyga", "soccer_belarus_vysshaya_liga", "soccer_bosnia_premier_league",
    "soccer_montenegro_first_league", "soccer_macedonia_first_league", "soccer_albania_superliga",
    "soccer_georgia_eka_liga", "soccer_kazakhstan_premier_league", "soccer_azerbaijan_premier_league",
    "soccer_armenia_premier_league"
]

previous_odds = {}

def get_football_odds():
    result = []

    for sport_key in EUROPEAN_LEAGUES:
        try:
            url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"
            params = {
                "apiKey": API_KEY,
                "regions": REGIONS,
                "markets": MARKETS,
                "oddsFormat": ODDS_FORMAT
            }

            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            matches = response.json()

            for match in matches:
                match_name = f"{match['home_team']} vs {match['away_team']}"
                for bookmaker in match.get("bookmakers", []):
                    for market in bookmaker.get("markets", []):
                        for outcome in market.get("outcomes", []):
                            key = f"{match['id']}_{market['key']}_{outcome['name']}"
                            new_price = outcome.get("price")

                            if new_price is None:
                                continue

                            old_price = previous_odds.get(key)
                            previous_odds[key] = new_price

                            if old_price and new_price < old_price:
                                result.append({
                                    "match": match_name,
                                    "market_name": market["key"],
                                    "label": outcome["name"],
                                    "old_odds": old_price,
                                    "new_odds": new_price
                                })

        except Exception as e:
            logging.error(f"API ERROR ({sport_key}): {e}")

    return result
