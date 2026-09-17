def test_like_and_unlike(client, other_user_client):
    client.post("/profiles", json={"username": "burhan", "display_name": "Burhan"})
    other_user_client.post("/profiles", json={"username": "friend", "display_name": "Friend"})
    post = client.post("/posts", json={"video_url": "https://x.supabase.co/v.mp4"}).json()

    like_resp = other_user_client.post(f"/posts/{post['id']}/like")
    assert like_resp.status_code == 204

    fetched = other_user_client.get(f"/posts/{post['id']}").json()
    assert fetched["like_count"] == 1
    assert fetched["liked_by_me"] is True

    unlike_resp = other_user_client.delete(f"/posts/{post['id']}/like")
    assert unlike_resp.status_code == 204

    fetched = other_user_client.get(f"/posts/{post['id']}").json()
    assert fetched["like_count"] == 0
    assert fetched["liked_by_me"] is False


def test_liking_twice_is_idempotent(client):
    client.post("/profiles", json={"username": "burhan", "display_name": "Burhan"})
    post = client.post("/posts", json={"video_url": "https://x.supabase.co/v.mp4"}).json()

    client.post(f"/posts/{post['id']}/like")
    resp = client.post(f"/posts/{post['id']}/like")
    assert resp.status_code == 204

    fetched = client.get(f"/posts/{post['id']}").json()
    assert fetched["like_count"] == 1  # not 2 - the second like didn't double up


def test_like_nonexistent_post_404s(client):
    client.post("/profiles", json={"username": "burhan", "display_name": "Burhan"})
    resp = client.post("/posts/does-not-exist/like")
    assert resp.status_code == 404
