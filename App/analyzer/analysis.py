from typing import List
from app.models.match import Match
from app.models.odds import OddsSnapshot
from app.models.suspicion_alert import SuspicionAlert

DRAW_DROP_THRESHOLD = 0.20  # 20% drop
GOAL_LINE_SHIFT_THRESHOLD = 1.0  # 1.0 goal change


def detect_suspicious_draw(match: Match, source_filter=None) -> bool:
    draw_odds = [
        snap.draw for snap in match.odds_snapshots 
        if snap.market == "1X2" and snap.draw is not None and 
           (source_filter is None or snap.bookmaker == source_filter)
    ]
    if len(draw_odds) < 2:
        return False

    opening = draw_odds[0]
    latest = draw_odds[-1]

    if opening == 0 or latest >= opening:
        return False

    drop_ratio = (opening - latest) / opening
    return drop_ratio >= DRAW_DROP_THRESHOLD


def detect_goal_line_shift(match: Match, source_filter=None) -> bool:
    goal_lines = [
        snap.total_line for snap in match.odds_snapshots 
        if snap.market == "Over/Under" and snap.total_line is not None and 
           (source_filter is None or snap.bookmaker == source_filter)
    ]
    if len(goal_lines) < 2:
        return False

    shift = abs(goal_lines[-1] - goal_lines[0])
    return shift >= GOAL_LINE_SHIFT_THRESHOLD


def analyze_match(match: Match) -> SuspicionAlert | None:
    """
    Returns a SuspicionAlert object if any suspicious behavior is found.
    Checks source attribution: odds_api, betfair, pinnacle.
    """
    sources = []

    # General suspicion flags
    general_draw_flag = detect_suspicious_draw(match)
    general_goal_flag = detect_goal_line_shift(match)

    if not general_draw_flag and not general_goal_flag:
        return None

    # Source-specific checks
    if detect_suspicious_draw(match, source_filter="OddsAPI"):
        sources.append("odds_api")
    if detect_suspicious_draw(match, source_filter="Betfair"):
        sources.append("betfair")
    if detect_suspicious_draw(match, source_filter="Pinnacle"):
        sources.append("pinnacle")

    if detect_goal_line_shift(match, source_filter="OddsAPI") and "odds_api" not in sources:
        sources.append("odds_api")
    if detect_goal_line_shift(match, source_filter="Betfair") and "betfair" not in sources:
        sources.append("betfair")
    if detect_goal_line_shift(match, source_filter="Pinnacle") and "pinnacle" not in sources:
        sources.append("pinnacle")

    alert = SuspicionAlert(
        match_id=match.match_id,
        league=match.league,
        home_team=match.home_team,
        away_team=match.away_team,
        commence_time=match.commence_time,
        suspicious_draw=general_draw_flag,
        goal_line_shift=general_goal_flag,
        alert_sources=sources or ["unknown"]
    )
    return alert


def analyze_matches(matches: List[Match]) -> List[SuspicionAlert]:
    """
    Analyze all matches and return list of SuspicionAlert objects.
    """
    return [alert for match in matches if (alert := analyze_match(match))]
