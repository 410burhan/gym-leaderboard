def test_feed_only_shows_followed_users(client, other_user_client):
    client.post("/profiles", json={"username": "burhan", "display_name": "Burhan"})
    other_user_client.post("/profiles", json={"username": "friend", "display_name": "Friend"})

    # A third, unfollowed user's workout should never appear.
    other_user_client.post("/workouts", json={"body_part": "push", "duration_minutes": 40})

    resp = client.get("/feed")
    assert resp.status_code == 200
    assert resp.json() == []  # burhan doesn't follow friend yet

    client.post("/follows/friend")
    resp = client.get("/feed")
    assert resp.status_code == 200
    entries = resp.json()
    assert len(entries) == 1
    assert entries[0]["username"] == "friend"
    assert entries[0]["workout"]["body_part"] == "push"


def test_feed_excludes_own_workouts(client, other_user_client):
    client.post("/profiles", json={"username": "burhan", "display_name": "Burhan"})
    other_user_client.post("/profiles", json={"username": "friend", "display_name": "Friend"})
    client.post("/follows/friend")

    client.post("/workouts", json={"body_part": "legs", "duration_minutes": 45})  # burhan's own

    resp = client.get("/feed")
    assert resp.json() == []  # only friend's workouts should show, and friend hasn't logged any
