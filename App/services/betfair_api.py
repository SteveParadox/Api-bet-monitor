import requests
import os
from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.match import Match
from app.models.odds import OddsSnapshot

BETFAIR_APP_KEY = os.getenv("BETFAIR_APP_KEY")
BETFAIR_SESSION_TOKEN = os.getenv("BETFAIR_SESSION_TOKEN")

BASE_URL = "https://api.betfair.com/exchange/betting/rest/v1.0"

HEADERS = {
    "X-Application": BETFAIR_APP_KEY,
    "X-Authentication": BETFAIR_SESSION_TOKEN,
    "Content-Type": "application/json"
}

def list_market_catalogue(competition_ids=[], market_type="MATCH_ODDS", event_type_id="1", max_results=100):
    payload = {
        "filter": {
            "eventTypeIds": [event_type_id],
            "competitionIds": competition_ids,
            "marketTypeCodes": [market_type],
        },
        "marketProjection": ["RUNNER_METADATA", "MARKET_START_TIME", "EVENT"],
        "maxResults": str(max_results)
    }

    res = requests.post(f"{BASE_URL}/listMarketCatalogue/", json=payload, headers=HEADERS)
    res.raise_for_status()
    return res.json()

def list_market_book(market_ids):
    payload = {
        "marketIds": market_ids,
        "priceProjection": {
            "priceData": ["EX_BEST_OFFERS", "EX_TRADED"]
        }
    }

    res = requests.post(f"{BASE_URL}/listMarketBook/", json=payload, headers=HEADERS)
    res.raise_for_status()
    return res.json()

def fetch_betfair_data():
    db: Session = next(get_db())

    try:
        catalogue = list_market_catalogue()
        market_ids = [m["marketId"] for m in catalogue]
        books = list_market_book(market_ids)
        market_lookup = {m["marketId"]: m for m in catalogue}

        for book in books:
            market_id = book["marketId"]
            market_info = market_lookup.get(market_id)
            if not market_info:
                continue

            event = market_info["event"]
            start_time = datetime.fromisoformat(event["openDate"].replace("Z", "+00:00"))
            home = event["name"].split(" v ")[0].strip()
            away = event["name"].split(" v ")[1].strip()
            league = event.get("countryCode", "Unknown")

            match_id = f"betfair_{event['id']}"

            # Store or get match
            match = db.query(Match).filter_by(match_id=match_id).first()
            if not match:
                match = Match(
                    match_id=match_id,
                    home_team=home,
                    away_team=away,
                    commence_time=start_time,
                    league=league
                )
                db.add(match)
                db.flush()

            runners = book["runners"]
            prices = {r["runnerName"]: r["ex"]["availableToBack"][0]["price"] if r["ex"]["availableToBack"] else None
                      for r in runners}

            snapshot = OddsSnapshot(
                id=str(uuid4()),
                match_id=match.match_id,
                timestamp=datetime.utcnow(),
                bookmaker="Betfair",
                market="1X2",
                home=prices.get(home),
                draw=prices.get("The Draw"),
                away=prices.get(away)
            )
            db.add(snapshot)

        db.commit()
        print(f"[✔] Betfair data integrated.")
    except Exception as e:
        db.rollback()
        print(f"[!] Betfair API error: {e}")
