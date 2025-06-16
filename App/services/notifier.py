import os
import requests
import smtplib
from email.mime.text import MIMEText
from app.models.suspicion_alert import SuspicionAlert

# Load from environment or config
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

def send_telegram_alert(alert: SuspicionAlert):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram not configured.")
        return

    msg = f"""🚨 Suspicious Match Detected
🏟️ {alert.league}
⚽ {alert.home_team} vs {alert.away_team}
🕒 {alert.commence_time.strftime('%Y-%m-%d %H:%M')}
🔍 Flags: 
- Draw Drop: {"✅" if alert.suspicious_draw else "❌"}
- Goal Line Shift: {"✅" if alert.goal_line_shift else "❌"}
📡 Sources: {", ".join(alert.alert_sources)}
"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg})
    except Exception as e:
        print("Telegram alert failed:", e)

def send_email_alert(alert: SuspicionAlert):
    if not EMAIL_HOST or not EMAIL_USER or not EMAIL_PASS:
        print("Email not configured.")
        return

    subject = f"Suspicious Fixture Alert: {alert.home_team} vs {alert.away_team}"
    body = f"""
Suspicious match detected!

League: {alert.league}
Match: {alert.home_team} vs {alert.away_team}
Kickoff: {alert.commence_time}

Reasons:
- Draw odds drop: {"YES" if alert.suspicious_draw else "NO"}
- Goal line shift: {"YES" if alert.goal_line_shift else "NO"}

Source(s): {', '.join(alert.alert_sources)}
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, EMAIL_RECEIVER, msg.as_string())
    except Exception as e:
        print("Email alert failed:", e)

def notify_all(alert: SuspicionAlert):
    send_telegram_alert(alert)
    send_email_alert(alert)
