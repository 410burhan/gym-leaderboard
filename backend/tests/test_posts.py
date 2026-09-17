def _setup_pair(client, other_user_client):
    client.post("/profiles", json={"username": "burhan", "display_name": "Burhan"})
    other_user_client.post("/profiles", json={"username": "friend", "display_name": "Friend"})


def test_create_post(client):
    client.post("/profiles", json={"username": "burhan", "display_name": "Burhan"})
    resp = client.post("/posts", json={"video_url": "https://x.supabase.co/v.mp4", "caption": "225 bench PR!"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["caption"] == "225 bench PR!"
    assert body["like_count"] == 0
    assert body["comment_count"] == 0
    assert body["liked_by_me"] is False


def test_post_can_link_to_own_workout(client):
    client.post("/profiles", json={"username": "burhan", "display_name": "Burhan"})
    workout = client.post("/workouts", json={"body_part": "push", "duration_minutes": 40}).json()

    resp = client.post("/posts", json={"video_url": "https://x.supabase.co/v.mp4", "workout_id": workout["id"]})
    assert resp.status_code == 201
    assert resp.json()["workout_id"] == workout["id"]


def test_post_cannot_link_to_someone_elses_workout(client, other_user_client):
    _setup_pair(client, other_user_client)
    workout = client.post("/workouts", json={"body_part": "push", "duration_minutes": 40}).json()

    resp = other_user_client.post(
        "/posts", json={"video_url": "https://x.supabase.co/v.mp4", "workout_id": workout["id"]}
    )
    assert resp.status_code == 400


def test_post_feed_only_shows_followed_users(client, other_user_client):
    _setup_pair(client, other_user_client)
    other_user_client.post("/posts", json={"video_url": "https://x.supabase.co/v.mp4", "caption": "PR"})

    resp = client.get("/posts/feed")
    assert resp.json() == []

    client.post("/follows/friend")
    resp = client.get("/posts/feed")
    assert len(resp.json()) == 1
    assert resp.json()[0]["username"] == "friend"


def test_owner_can_delete_post(client):
    client.post("/profiles", json={"username": "burhan", "display_name": "Burhan"})
    post = client.post("/posts", json={"video_url": "https://x.supabase.co/v.mp4"}).json()
    resp = client.delete(f"/posts/{post['id']}")
    assert resp.status_code == 204


def test_non_owner_cannot_delete_post(client, other_user_client):
    _setup_pair(client, other_user_client)
    post = client.post("/posts", json={"video_url": "https://x.supabase.co/v.mp4"}).json()
    resp = other_user_client.delete(f"/posts/{post['id']}")
    assert resp.status_code == 403
