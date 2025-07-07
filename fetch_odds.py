import requests

API_KEY = "8669c873a0ad07e5e2f38c6f52fb8e69"
REGIONS = "eu,us,uk,au,za"
MARKETS = "h2h,totals,btts,corners,cards"
ODDS_FORMAT = "decimal"

def get_all_odds():
    url = "https://api.the-odds-api.com/v4/sports/?all=true"
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)
    all_data = {}
    for sport in response.json():
        if not sport["key"].startswith("soccer_"):
            continue
        league = sport["key"]
        odds_url = f"https://api.the-odds-api.com/v4/sports/{league}/odds/"
        params = {
            "apiKey": API_KEY,
            "regions": REGIONS,
            "markets": MARKETS,
            "oddsFormat": ODDS_FORMAT
        }
        try:
            res = requests.get(odds_url, params=params)
            if res.status_code == 200:
                all_data[league] = parse_odds_data(res.json())
        except:
            continue
    return all_data

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
