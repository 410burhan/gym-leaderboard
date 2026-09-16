from datetime import date, timedelta

from app.routers.leaderboard import _current_streak


def test_streak_counts_consecutive_days_ending_today():
    today = date.today()
    dates = {today, today - timedelta(days=1), today - timedelta(days=2)}
    assert _current_streak(dates) == 3


def test_streak_still_counts_if_not_logged_yet_today():
    today = date.today()
    dates = {today - timedelta(days=1), today - timedelta(days=2)}
    assert _current_streak(dates) == 2


def test_streak_breaks_on_gap():
    today = date.today()
    dates = {today, today - timedelta(days=3)}  # gap at day -1 and -2
    assert _current_streak(dates) == 1


def test_streak_zero_when_no_logs():
    assert _current_streak(set()) == 0


def test_leaderboard_aggregates_across_group(client):
    group_resp = client.post("/groups", json={"name": "Gym Bros", "display_name": "Burhan"})
    group_id = group_resp.json()["id"]

    client.post(f"/groups/{group_id}/workouts", json={"workout_type": "push", "duration_minutes": 30})
    client.post(f"/groups/{group_id}/workouts", json={"workout_type": "legs", "duration_minutes": 50})

    resp = client.get(f"/groups/{group_id}/leaderboard")
    assert resp.status_code == 200
    entry = resp.json()[0]
    assert entry["workout_count"] == 2
    assert entry["total_minutes"] == 80
