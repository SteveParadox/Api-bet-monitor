from sqlalchemy import Column, String, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4

from app.db.session import Base

class SuspicionAlert(Base):
    __tablename__ = "suspicion_alerts"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    match_id = Column(String, ForeignKey("matches.match_id"), nullable=False)

    league = Column(String, nullable=False)
    home_team = Column(String, nullable=False)
    away_team = Column(String, nullable=False)
    commence_time = Column(DateTime, nullable=False)

    suspicious_draw = Column(Boolean, default=False)
    goal_line_shift = Column(Boolean, default=False)

    alert_sources = Column(JSON, default=list)  # Example: ['betfair', 'pinnacle']
    created_at = Column(DateTime, default=datetime.utcnow)

    match = relationship("Match")  # Optional: to backref full match info

    def to_dict(self):
        return {
            "match_id": self.match_id,
            "league": self.league,
            "home": self.home_team,
            "away": self.away_team,
            "commence_time": self.commence_time.isoformat(),
            "suspicious_draw": self.suspicious_draw,
            "goal_line_shift": self.goal_line_shift,
            "alert_sources": self.alert_sources,
            "created_at": self.created_at.isoformat()
        }

    def __repr__(self):
        return (
            f"<Alert {self.match_id} | draw_drop={self.suspicious_draw}, "
            f"goal_line_shift={self.goal_line_shift}>"
        )
