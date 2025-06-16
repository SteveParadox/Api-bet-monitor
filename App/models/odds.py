from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base

class OddsSnapshot(Base):
    __tablename__ = "odds_snapshots"

    id = Column(String, primary_key=True)
    match_id = Column(String, ForeignKey("matches.match_id"), nullable=False)

    timestamp = Column(DateTime, default=datetime.utcnow)
    bookmaker = Column(String, nullable=False)
    market = Column(String, nullable=False)  # "1X2", "Over/Under"

    # 1X2 market
    home = Column(Float)
    draw = Column(Float)
    away = Column(Float)

    # Over/Under market
    total_line = Column(Float)
    over = Column(Float)
    under = Column(Float)

    # Relationship back to Match
    match = relationship("Match", back_populates="odds_snapshots")

    def __repr__(self):
        return f"<OddsSnapshot {self.market} by {self.bookmaker} @ {self.timestamp}>"
