from flask import Blueprint, jsonify, request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.match import Match
from app.models.alert import SuspicionAlert
from app.analyzer.analysis import analyze_match
from app.tasks.monitor import run_monitoring

alerts_bp = Blueprint("alerts", __name__)

# Dependency-injected session for use in each route
def get_session():
    db = next(get_db())
    return db

@alerts_bp.route('/suspicious', methods=['GET'])
def suspicious_alerts():
    db: Session = get_session()
    alerts = db.query(SuspicionAlert).order_by(SuspicionAlert.created_at.desc()).limit(20).all()
    return jsonify({
        "count": len(alerts),
        "alerts": [alert.to_dict() for alert in alerts]
    })


@alerts_bp.route('/match/<match_id>', methods=['GET'])
def match_detail(match_id):
    db: Session = get_session()
    match = db.query(Match).filter(Match.match_id == match_id).first()
    if not match:
        return jsonify({"error": "Match not found"}), 404

    # Ensure match.odds_snapshots is loaded if needed
    analysis = analyze_match(match)
    return jsonify(analysis)


@alerts_bp.route('/recheck', methods=['POST'])
def manual_recheck():
    run_monitoring()
    return jsonify({"message": "Re-analysis complete"})


@alerts_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "OK", "message": "Backend running smoothly"})
