import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    API_KEYS = {
        "oddsapi": os.getenv("ODDS_API_KEY"),
        "betfair": os.getenv("BETFAIR_API_KEY"),
        "pinnacle": os.getenv("PINNACLE_API_KEY"),
    }
    ALERT_THRESHOLD = {
        "draw_drop_percent": 20,
        "goal_line_shift": 1.0,
    }
