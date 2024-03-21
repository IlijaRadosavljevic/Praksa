import pytest
from app import models, schemas


def test_get_all_comments(authorized_client, test_comments):
    res = authorized_client.get("/comments/")

    def validate(comment):
        return schemas.Comment(**comment)

    comment_map = map(validate, res.json())
    comment_list = list(comment_map)
    assert len(res.json()) == len(test_comments)
    assert res.status_code == 200


def test_unauthorized_user_get_all_comments(client, test_comments):
    res = client.get("/comments/")
    assert res.status_code == 401


def test_unauthorized_user_get_one_comment(client, test_comments):
    res = client.get(f"/comments/{test_comments[3].comment_id}")
    assert res.status_code == 401


def test_get_one_comment_not_exist(authorized_client, test_comments):
    res = authorized_client.get(f"/comments/88888")
    assert res.status_code == 404


def test_get_one_comment(authorized_client, test_comments):
    res = authorized_client.get(f"/comments/{test_comments[0].comment_id}")
    comm = schemas.Comment(**res.json())
    assert comm.user_id == test_comments[0].user_id
    assert comm.content == test_comments[0].content


@pytest.mark.parametrize(
    "post_id, content",
    [
        (1, "awesome new content"),
        (2, "contentcontent"),
        (3, "content"),
    ],
)
def test_create_comment(
    authorized_client, test_user, test_posts, test_comments, post_id, content
):
    res = authorized_client.post(
        "/comments/", json={"post_id": post_id, "content": content}
    )
    res_json = res.json()

    created_comment = schemas.Comment(**res_json)
    created_comment.user_id = test_user["id"]

    assert res.status_code == 200
    assert created_comment.user_id == test_user["id"]
    assert created_comment.content == content


def test_unauthorized_user_create_comment(client, test_user, test_comments):
    res = client.post("/comments/", json={"post_id": 2, "content": "proba proba"})
    assert res.status_code == 401


def test_unauthorized_user_delete_comment(client, test_user, test_comments):
    res = client.delete(f"/comments/{test_comments[0].comment_id}")
    assert res.status_code == 401


def test_delete_comment_success(authorized_client, test_user, test_comments):
    res = authorized_client.delete(f"/comments/{test_comments[1].comment_id}")
    assert res.status_code == 204


def test_delete_comment_fail(authorized_client, test_user, test_comments):
    res = authorized_client.delete(f"/comments/99999")
    assert res.status_code == 404


def test_delete_other_user_comment(authorized_client, test_user, test_comments):
    res = authorized_client.delete(f"/comments/{test_comments[0].comment_id}")
    assert res.status_code == 403


def test_update_comment(authorized_client, test_user, test_comments):
    data = {
        "content": "firsto upgradedo content",
        "comment_id": test_comments[2].comment_id,
    }
    res = authorized_client.put(f"/comments/{test_comments[2].comment_id}", json=data)
    updated_comment = schemas.Comment(**res.json())

    assert res.status_code == 200
    assert updated_comment.content == data["content"]


def test_update_other_user_comment(
    authorized_client, test_user, test_user2, test_comments
):
    data = {
        "content": "firsto upgradedo content",
        "comment_id": test_comments[0].comment_id,
    }
    res = authorized_client.put(f"/comments/{test_comments[0].comment_id}", json=data)
    assert res.status_code == 403


def test_unauthorized_user_update_comments(client, test_user, test_comments):
    res = client.put(f"/comments/json={test_comments[0].comment_id}")
    assert res.status_code == 401


def test_update_comment_non_exist(authorized_client, test_user, test_comments):
    data = {
        "content": "firsto upgradedo content",
        "comment_id": len(test_comments) + 1,
    }
    res = authorized_client.put(f"/comments/{data['comment_id']}", json=data)
    assert res.status_code == 404
