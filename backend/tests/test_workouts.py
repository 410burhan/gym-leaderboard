def test_log_workout_requires_profile_first(client):
    resp = client.post("/workouts", json={"body_part": "push", "duration_minutes": 30})
    assert resp.status_code == 400


def test_log_workout_succeeds_with_profile(client):
    client.post("/profiles", json={"username": "burhan", "display_name": "Burhan"})
    resp = client.post("/workouts", json={"body_part": "legs", "duration_minutes": 50})
    assert resp.status_code == 201
    assert resp.json()["body_part"] == "legs"


def test_invalid_body_part_rejected(client):
    client.post("/profiles", json={"username": "burhan", "display_name": "Burhan"})
    resp = client.post("/workouts", json={"body_part": "biceps", "duration_minutes": 20})
    assert resp.status_code == 422


def test_user_can_delete_own_workout(client):
    client.post("/profiles", json={"username": "burhan", "display_name": "Burhan"})
    workout = client.post("/workouts", json={"body_part": "cardio", "duration_minutes": 20}).json()
    resp = client.delete(f"/workouts/{workout['id']}")
    assert resp.status_code == 204


def test_user_cannot_delete_someone_elses_workout(client, other_user_client):
    client.post("/profiles", json={"username": "burhan", "display_name": "Burhan"})
    other_user_client.post("/profiles", json={"username": "friend", "display_name": "Friend"})

    workout = client.post("/workouts", json={"body_part": "pull", "duration_minutes": 35}).json()
    resp = other_user_client.delete(f"/workouts/{workout['id']}")
    assert resp.status_code == 403
