import requests
import os
from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session
from app.models.match import Match
from app.models.odds import OddsSnapshot
from app.db.session import get_db

# Load your OddsAPI key from environment
ODDS_API_KEY = os.getenv("ODDS_API_KEY")

BASE_URL = "https://api.the-odds-api.com/v4/sports"
REGIONS = "eu,uk"
MARKETS = "h2h,totals"

LEAGUE_KEYS = [
    "soccer_brazil_serieb",
    "soccer_brazil_seriec",
    "soccer_argentina_primera_b_nacional",
    "soccer_iran_persian_gulf_pro_league",
    "soccer_nigeria_pfl",
    "soccer_south_africa_psl",
    "soccer_kenya_premier_league",
    "soccer_ghana_premier_league",
    "soccer_zimbabwe_premier_league"
]

def fetch_odds_for_all_target_leagues():
    db: Session = next(get_db())
    all_matches = []

    for league_key in LEAGUE_KEYS:
        print(f"[+] Fetching league: {league_key}")
        matches = fetch_odds_for_league(league_key, db)
        all_matches.extend(matches)

    db.commit()
    return all_matches

def fetch_odds_for_league(league_key, db: Session):
    url = f"{BASE_URL}/{league_key}/odds"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": REGIONS,
        "markets": MARKETS,
        "oddsFormat": "decimal"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[!] Request failed for {league_key}: {e}")
        return []

    raw_data = response.json()
    parsed_matches = []

    for match_data in raw_data:
        match_id = match_data.get("id")
        commence_time = datetime.fromisoformat(match_data["commence_time"].replace("Z", "+00:00"))
        home_team = match_data.get("home_team")
        away_team = [team for team in match_data["teams"] if team != home_team][0]
        league = match_data.get("sport_key")

        # Check if match already exists
        match = db.query(Match).filter_by(match_id=match_id).first()
        if not match:
            match = Match(
                match_id=match_id,
                home_team=home_team,
                away_team=away_team,
                league=league,
                commence_time=commence_time
            )
            db.add(match)
            db.flush()  # ensure match_id is available

        for bookmaker in match_data.get("bookmakers", []):
            bk_title = bookmaker.get("title")
            timestamp = datetime.utcnow()

            for market in bookmaker.get("markets", []):
                market_type = market.get("key")

                if market_type == "h2h":
                    h, d, a = None, None, None
                    for outcome in market.get("outcomes", []):
                        name = outcome.get("name").lower()
                        price = outcome.get("price")
                        if name == home_team.lower():
                            h = price
                        elif name == away_team.lower():
                            a = price
                        elif name == "draw":
                            d = price

                    snapshot = OddsSnapshot(
                        id=str(uuid4()),
                        match_id=match.match_id,
                        timestamp=timestamp,
                        bookmaker=bk_title,
                        market="1X2",
                        home=h,
                        draw=d,
                        away=a
                    )
                    db.add(snapshot)

                elif market_type == "totals":
                    over = under = total_line = None
                    for outcome in market.get("outcomes", []):
                        if "over" in outcome["name"].lower():
                            over = outcome["price"]
                            total_line = outcome["point"]
                        elif "under" in outcome["name"].lower():
                            under = outcome["price"]
                            total_line = outcome["point"]

                    snapshot = OddsSnapshot(
                        id=str(uuid4()),
                        match_id=match.match_id,
                        timestamp=timestamp,
                        bookmaker=bk_title,
                        market="Over/Under",
                        total_line=total_line,
                        over=over,
                        under=under
                    )
                    db.add(snapshot)

        parsed_matches.append(match)

    return parsed_matches
