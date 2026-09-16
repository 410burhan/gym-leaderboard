def _make_group(client):
    resp = client.post("/groups", json={"name": "Gym Bros", "display_name": "Burhan"})
    return resp.json()["id"]


def test_log_workout_succeeds_for_member(client):
    group_id = _make_group(client)
    resp = client.post(
        f"/groups/{group_id}/workouts",
        json={"workout_type": "push", "duration_minutes": 45},
    )
    assert resp.status_code == 201
    assert resp.json()["workout_type"] == "push"


def test_non_member_cannot_log_workout(client, other_user_client):
    group_id = _make_group(client)  # created by `client`'s user, not `other_user_client`'s

    resp = other_user_client.post(
        f"/groups/{group_id}/workouts",
        json={"workout_type": "legs", "duration_minutes": 30},
    )
    assert resp.status_code == 403


def test_user_can_delete_own_workout(client):
    group_id = _make_group(client)
    workout = client.post(
        f"/groups/{group_id}/workouts",
        json={"workout_type": "cardio", "duration_minutes": 20},
    ).json()

    resp = client.delete(f"/groups/{group_id}/workouts/{workout['id']}")
    assert resp.status_code == 204


def test_user_cannot_delete_someone_elses_workout(client, other_user_client):
    group_id = _make_group(client)
    workout = client.post(
        f"/groups/{group_id}/workouts",
        json={"workout_type": "cardio", "duration_minutes": 20},
    ).json()

    # other_user_client joins the same group, then tries to delete client's log
    invite_code = client.get("/groups").json()[0]["invite_code"]
    other_user_client.post("/groups/join", json={"invite_code": invite_code, "display_name": "Friend"})

    resp = other_user_client.delete(f"/groups/{group_id}/workouts/{workout['id']}")
    assert resp.status_code == 403
