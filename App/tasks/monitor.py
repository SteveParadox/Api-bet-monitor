import time
from sqlalchemy.orm import Session
from uuid import uuid4

from app.services.odds_api import fetch_all_odds
from app.services.betfair_api import fetch_betfair_data
from app.services.pinnacle_api import fetch_pinnacle_data
from app.analyzer.analysis import analyze_matches
from app.models.match import Match
from app.models.alert import SuspicionAlert
from app.services.notifier import notify_all
from app.db.session import get_db

def run_monitoring():
    print("🕵️‍♂️ Starting monitoring task...")

    db: Session = next(get_db())

    # 1. Fetch matches and odds
    matches: list[Match] = fetch_all_odds()

    # 2. Optional: enrich data with Betfair, Pinnacle
    betfair_info = fetch_betfair_data()
    pinnacle_info = fetch_pinnacle_data()

    # Enrich odds_snapshots (assumes odds_snapshots already include bookmaker field)
    for match in matches:
        for snapshot in match.odds_snapshots:
            if snapshot.bookmaker.lower() in ["betfair", "pinnacle"]:
                continue  # Already attributed
            if snapshot.bookmaker in betfair_info:
                snapshot.bookmaker = "Betfair"
            elif snapshot.bookmaker in pinnacle_info:
                snapshot.bookmaker = "Pinnacle"

    # 3. Analyze suspicious patterns
    alerts = analyze_matches(matches)

    if alerts:
        print(f"🚨 Found {len(alerts)} suspicious fixtures")
    else:
        print("✅ No suspicious activity detected.")

    for alert in alerts:
        # Avoid duplicates
        existing = db.query(SuspicionAlert).filter_by(match_id=alert.match_id).first()
        if existing:
            continue

        db_alert = SuspicionAlert(
            id=str(uuid4()),
            match_id=alert.match_id,
            league=alert.league,
            home_team=alert.home_team,
            away_team=alert.away_team,
            commence_time=alert.commence_time,
            suspicious_draw=alert.suspicious_draw,
            goal_line_shift=alert.goal_line_shift,
            alert_sources=alert.alert_sources  
        )

        db.add(db_alert)
        notify_all(db_alert)

    db.commit()
