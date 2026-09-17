def test_add_and_list_comments(client, other_user_client):
    client.post("/profiles", json={"username": "burhan", "display_name": "Burhan"})
    other_user_client.post("/profiles", json={"username": "friend", "display_name": "Friend"})
    post = client.post("/posts", json={"video_url": "https://x.supabase.co/v.mp4"}).json()

    resp = other_user_client.post(f"/posts/{post['id']}/comments", json={"body": "Let's gooo"})
    assert resp.status_code == 201
    assert resp.json()["body"] == "Let's gooo"
    assert resp.json()["username"] == "friend"

    listed = client.get(f"/posts/{post['id']}/comments").json()
    assert len(listed) == 1

    fetched_post = client.get(f"/posts/{post['id']}").json()
    assert fetched_post["comment_count"] == 1


def test_owner_can_delete_comment(client):
    client.post("/profiles", json={"username": "burhan", "display_name": "Burhan"})
    post = client.post("/posts", json={"video_url": "https://x.supabase.co/v.mp4"}).json()
    comment = client.post(f"/posts/{post['id']}/comments", json={"body": "nice"}).json()

    resp = client.delete(f"/comments/{comment['id']}")
    assert resp.status_code == 204


def test_non_owner_cannot_delete_comment(client, other_user_client):
    client.post("/profiles", json={"username": "burhan", "display_name": "Burhan"})
    other_user_client.post("/profiles", json={"username": "friend", "display_name": "Friend"})
    post = client.post("/posts", json={"video_url": "https://x.supabase.co/v.mp4"}).json()
    comment = client.post(f"/posts/{post['id']}/comments", json={"body": "nice"}).json()

    resp = other_user_client.delete(f"/comments/{comment['id']}")
    assert resp.status_code == 403
