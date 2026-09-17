def test_create_profile(client):
    resp = client.post("/profiles", json={"username": "burhan", "display_name": "Burhan"})
    assert resp.status_code == 201
    assert resp.json()["username"] == "burhan"


def test_cannot_create_profile_twice(client):
    client.post("/profiles", json={"username": "burhan", "display_name": "Burhan"})
    resp = client.post("/profiles", json={"username": "burhan2", "display_name": "Burhan"})
    assert resp.status_code == 400


def test_duplicate_username_rejected(client, other_user_client):
    client.post("/profiles", json={"username": "burhan", "display_name": "Burhan"})
    resp = other_user_client.post("/profiles", json={"username": "burhan", "display_name": "Someone Else"})
    assert resp.status_code == 409


def test_invalid_username_rejected(client):
    resp = client.post("/profiles", json={"username": "no spaces!", "display_name": "Burhan"})
    assert resp.status_code == 422


def test_public_profile_shows_counts(client, other_user_client):
    client.post("/profiles", json={"username": "burhan", "display_name": "Burhan"})
    other_user_client.post("/profiles", json={"username": "friend", "display_name": "Friend"})

    other_user_client.post("/follows/burhan")
    client.post("/workouts", json={"body_part": "push", "duration_minutes": 40})

    resp = other_user_client.get("/profiles/burhan")
    assert resp.status_code == 200
    body = resp.json()
    assert body["follower_count"] == 1
    assert body["workout_count"] == 1
    assert body["is_following"] is True
