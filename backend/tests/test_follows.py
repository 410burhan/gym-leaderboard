def test_follow_and_unfollow(client, other_user_client):
    client.post("/profiles", json={"username": "burhan", "display_name": "Burhan"})
    other_user_client.post("/profiles", json={"username": "friend", "display_name": "Friend"})

    follow_resp = other_user_client.post("/follows/burhan")
    assert follow_resp.status_code == 204

    profile = other_user_client.get("/profiles/burhan").json()
    assert profile["is_following"] is True

    unfollow_resp = other_user_client.delete("/follows/burhan")
    assert unfollow_resp.status_code == 204

    profile = other_user_client.get("/profiles/burhan").json()
    assert profile["is_following"] is False


def test_cannot_follow_self(client):
    client.post("/profiles", json={"username": "burhan", "display_name": "Burhan"})
    resp = client.post("/follows/burhan")
    assert resp.status_code == 400


def test_follow_nonexistent_user_404s(client):
    client.post("/profiles", json={"username": "burhan", "display_name": "Burhan"})
    resp = client.post("/follows/nobody")
    assert resp.status_code == 404


def test_following_twice_is_idempotent(client, other_user_client):
    client.post("/profiles", json={"username": "burhan", "display_name": "Burhan"})
    other_user_client.post("/profiles", json={"username": "friend", "display_name": "Friend"})

    other_user_client.post("/follows/burhan")
    resp = other_user_client.post("/follows/burhan")
    assert resp.status_code == 204  # no error re-following
