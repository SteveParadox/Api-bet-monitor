import os
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.match import Match
from app.models.odds import OddsSnapshot

PINNACLE_USERNAME = os.getenv("PINNACLE_USERNAME")
PINNACLE_PASSWORD = os.getenv("PINNACLE_PASSWORD")

BASE_URL = "https://api.pinnacle.com/v1/"
auth = HTTPBasicAuth(PINNACLE_USERNAME, PINNACLE_PASSWORD)

def get_leagues(sport_id=29):
    res = requests.get(f"{BASE_URL}leagues?sportId={sport_id}", auth=auth)
    res.raise_for_status()
    return res.json()

def get_fixtures(sport_id=29, league_ids=[]):
    league_param = ",".join(map(str, league_ids))
    url = f"{BASE_URL}fixtures?sportId={sport_id}&leagueIds={league_param}"
    res = requests.get(url, auth=auth)
    res.raise_for_status()
    return res.json()

def get_odds(sport_id=29, league_ids=[]):
    league_param = ",".join(map(str, league_ids))
    url = f"{BASE_URL}odds?sportId={sport_id}&leagueIds={league_param}&oddsFormat=DECIMAL"
    res = requests.get(url, auth=auth)
    res.raise_for_status()
    return res.json()

def fetch_pinnacle_data():
    db: Session = next(get_db())

    try:
        leagues = get_leagues()
        league_ids = [l["id"] for l in leagues if l["name"].lower() in {
            "brazil - serie b", "brazil - serie c",
            "argentina - primera b nacional",
            "iran - persian gulf pro league",
            "nigeria - pfl", "south africa - psl",
            "kenya - premier league", "ghana - premier league",
            "zimbabwe - premier league"
        }]

        fixtures = get_fixtures(league_ids=league_ids)
        odds_data = get_odds(league_ids=league_ids)

        fixture_map = {f["id"]: f for f in fixtures["league"] for f in f["events"]}
        for league in odds_data["league"]:
            for event in league["events"]:
                fixture = fixture_map.get(event["id"])
                if not fixture:
                    continue

                home = fixture["home"]
                away = fixture["away"]
                start_time = datetime.fromisoformat(fixture["starts"].replace("Z", "+00:00"))
                match_id = f"pinnacle_{event['id']}"

                # Add match
                match = db.query(Match).filter_by(match_id=match_id).first()
                if not match:
                    match = Match(
                        match_id=match_id,
                        home_team=home,
                        away_team=away,
                        commence_time=start_time,
                        league=league["name"]
                    )
                    db.add(match)
                    db.flush()

                # Add markets
                for market in event["periods"][0]["moneyline"], event["periods"][0].get("totals", []):
                    if isinstance(market, dict):  # moneyline
                        snapshot = OddsSnapshot(
                            id=str(uuid4()),
                            match_id=match.match_id,
                            timestamp=datetime.utcnow(),
                            bookmaker="Pinnacle",
                            market="1X2",
                            home=market.get("home"),
                            draw=market.get("draw"),
                            away=market.get("away")
                        )
                        db.add(snapshot)
                    elif isinstance(market, list):  # totals
                        for line in market:
                            snapshot = OddsSnapshot(
                                id=str(uuid4()),
                                match_id=match.match_id,
                                timestamp=datetime.utcnow(),
                                bookmaker="Pinnacle",
                                market="Over/Under",
                                total_line=line.get("points"),
                                over=line.get("over"),
                                under=line.get("under")
                            )
                            db.add(snapshot)

        db.commit()
        print("[✔] Pinnacle odds integrated.")

    except Exception as e:
        db.rollback()
        print(f"[!] Pinnacle API error: {e}")
