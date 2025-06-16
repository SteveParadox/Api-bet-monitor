
# ⚽ Automated Odds Monitoring System

A real-time suspicious betting pattern detector built with **Flask**, **SQLAlchemy**, and **odds APIs** (OddsAPI, Betfair, Pinnacle). It monitors targeted football leagues for odds anomalies and sends automated alerts via Telegram or other channels.

---

## 🧠 Features

- ⏱ Automated monitoring every X minutes (via cron or scheduler)
- 📉 Detect suspicious odds behavior:
  - Draw odds drop ≥ 20% within 30 minutes
  - Total goal line shift ≥ 1.0
  - Abnormal bookmaker imbalance (WIP)
- 📡 Multi-source odds aggregation (OddsAPI, Betfair, Pinnacle)
- 🧠 Historical odds timeline storage
- 📬 Notifications via Telegram or Webhooks
- 🌍 Targeted to leagues with suspicious betting history (Iran, Nigeria, Brazil Serie B/C, etc.)

---

## 🗂 Project Structure

```
app/
├── __init__.py
├── main.py              # FastAPI entry
├── models/              # SQLAlchemy models
│   ├── match.py
│   ├── odds.py
│   └── alert.py
├── services/            # API clients for OddsAPI, Betfair, Pinnacle
│   ├── odds_api.py
│   ├── betfair_api.py
│   └── pinnacle_api.py
├── analyzer/
│   └── analysis.py      # Core logic to detect suspicious matches
├── tasks/
│   └── monitor.py       # Scheduler to run monitoring
├── routes/
│   └── alerts.py        # API endpoints
├── notifier/
│   └── notifier.py      # Sends alerts
├── utils/
│   └── helpers.py       # Formatting and odds math
└── db/
    ├── session.py       # DB engine/session setup
    └── init_db.py
```

---

## 🛠️ Installation

### 1. Clone the repo
```bash
git clone https://github.com/SteveParadox/Api-bet-monitor.git
cd odds-monitor
```

### 2. Set up virtual environment
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create `.env` file
```ini
ODDS_API_KEY=your_oddsapi_key
BETFAIR_KEY=your_betfair_key
PINNACLE_USER=your_pinnacle_user
PINNACLE_PASS=your_pinnacle_pass
DATABASE_URL=sqlite:///./odds.db
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

---

## 🧪 Run Locally

### Start Flask server
```bash
export FLASK_APP=app
export FLASK_ENV=development
flask run


---

## 🔌 API Endpoints

| Method | Route                  | Description                          |
|--------|------------------------|--------------------------------------|
| GET    | `/suspicious`          | List latest suspicious alerts        |
| GET    | `/match/{match_id}`    | Full odds timeline for a match       |
| GET    | `/health`              | Healthcheck                          |
| POST   | `/recheck` (optional)  | Trigger manual analysis              |

---

## 🧠 Analysis Rules

- 🔻 **Draw Drop Rule**: Drop ≥ 20% from opening to latest odds.
- ⚽ **Goal Line Shift**: Movement ≥ 1.0 goal line.
- 📊 **Sources**: OddsAPI, Betfair (volume/odds), Pinnacle (sharp odds).

---

## 📦 Technologies Used

- **Flask** for backend API
- **SQLAlchemy** ORM
- **APScheduler / cron** for scheduled tasks
- **Requests** to fetch bookmaker APIs
- **Telegram Bot API** for notifications
- **PostgreSQL / SQLite** (pluggable)

---

## 🚀 Roadmap

- [x] Add Betfair volume anomaly detection
- [x] Integrate Pinnacle sharp money indicators
- [ ] Build frontend dashboard (React/Next.js)
- [ ] Dockerize project
- [ ] Add ML-based confidence scoring

---

## 🙏 Acknowledgments

- [OddsAPI](https://the-odds-api.com/)
- [Betfair Exchange API](https://docs.developer.betfair.com/)
- [Pinnacle API](https://www.pinnacle.com/en/api)

---

## 📄 License

MIT License. See `LICENSE`.
