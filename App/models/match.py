from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from app.db.session import Base

class Match(Base):
    __tablename__ = "matches"

    match_id = Column(String, primary_key=True, index=True)
    home_team = Column(String, nullable=False)
    away_team = Column(String, nullable=False)
    league = Column(String, nullable=False)
    commence_time = Column(DateTime, nullable=False)
    source = Column(String, default="oddsapi")

    # Relationship to OddsSnapshot
    odds_snapshots = relationship("OddsSnapshot", back_populates="match")

    def __repr__(self):
        return f"<Match {self.home_team} vs {self.away_team} | {self.league} @ {self.commence_time}>"

ALL_MATCHES = []

def get_match_by_id(match_id: str):
    for match in ALL_MATCHES:
        if match.match_id == match_id:
            return match
    return None
