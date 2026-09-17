def test_get_user_workouts(client, other_user_client):
    client.post("/profiles", json={"username": "burhan", "display_name": "Burhan"})
    client.post("/workouts", json={"body_part": "push", "duration_minutes": 30})

    resp = other_user_client.get("/profiles/burhan/workouts")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["body_part"] == "push"


def test_get_workouts_for_nonexistent_profile_404s(client):
    resp = client.get("/profiles/nobody/workouts")
    assert resp.status_code == 404
