def test_create_group_returns_invite_code(client):
    resp = client.post("/groups", json={"name": "Gym Bros", "display_name": "Burhan"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "Gym Bros"
    assert len(body["invite_code"]) == 6


def test_join_group_with_valid_code(client, other_user_client):
    create_resp = client.post("/groups", json={"name": "Gym Bros", "display_name": "Burhan"})
    invite_code = create_resp.json()["invite_code"]

    join_resp = other_user_client.post(
        "/groups/join", json={"invite_code": invite_code, "display_name": "Friend"}
    )
    assert join_resp.status_code == 200
    assert join_resp.json()["invite_code"] == invite_code


def test_join_group_with_invalid_code_returns_404(client):
    resp = client.post("/groups/join", json={"invite_code": "ZZZZZZ", "display_name": "Nobody"})
    assert resp.status_code == 404


def test_joining_twice_is_idempotent(client):
    create_resp = client.post("/groups", json={"name": "Gym Bros", "display_name": "Burhan"})
    invite_code = create_resp.json()["invite_code"]

    resp = client.post("/groups/join", json={"invite_code": invite_code, "display_name": "Burhan"})
    assert resp.status_code == 200  # doesn't error on re-joining your own group
