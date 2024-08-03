from fastapi.testclient import TestClient

from fastapi.testclient import TestClient
import pytest

from main import app


@pytest.fixture
def client():
    with TestClient(app) as client:
        client.post(
            "/users",
            json={
                "nickname": "test_user",
                "password": "Test_password",
            },
        )

        client.post(
            "/users/login",
            json={
                "nickname": "test_user",
                "password": "Test_password",
            },
        )

        # 명시해야 하나??
        # client.cookies = {
        #     "session_id": response.json()['session_id']
        # }

        # 미리 post 생성
        client.post(
            "/posts",
            json={
                "title": "test_title",
                "content": "test_content",
            },
        )
        yield client


@pytest.mark.create
def test_create_comment_ok(client: TestClient):
    response = client.post(
        "/comments/1",
        json={
            "content": "test_comment",
        },
    )
    assert response.status_code == 201
    assert response.json()["content"] == "test_comment"


@pytest.mark.create
def test_create_comment_invalid_params(client: TestClient):
    response = client.post(
        url="/comments/1",
        json={
            "content": None,
        },
    )
    assert response.status_code == 422


@pytest.mark.create
def test_create_comment_post_missing_field(client: TestClient):
    response = client.post(
        url="/comments/1",
        json={
            "content": None,
        },
    )
    assert response.status_code == 422


@pytest.mark.create
def test_create_comment_post_not_exists(client: TestClient):
    response = client.post(
        url="/comments/9999",
        json={
            "content": "test_comment",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "존재하지 않는 포스트입니다"


# 페이지네이션 해야함
@pytest.mark.comments
def test_comment_list_by_post_ok(client: TestClient):
    client.post(
        "/comments/1",
        json={
            "content": "test_comment_1",
        },
    )

    client.post(
        "/comments/1",
        json={
            "content": "test_comment_2",
        },
    )
    response = client.get("/comments/by_post/1")

    assert response.status_code == 200
    assert len(response.json()["comments"]) == 2


@pytest.mark.comments
def test_comment_list_by_post_empty_ok(client: TestClient):
    response = client.get("/comments/by_post/1")

    assert response.status_code == 200
    assert len(response.json()["comments"]) == 0


# 다른 유저가 넣은거 처리 해야함
@pytest.mark.comments
def test_comment_list_by_user_ok(client: TestClient):
    client.post(
        "/comments/1",
        json={
            "content": "test_comment_1",
        },
    )

    client.post(
        "/comments/1",
        json={
            "content": "test_comment_2",
        },
    )
    response = client.get("/comments/by_user/1")

    assert response.status_code == 200
    assert len(response.json()["comments"]) == 2


@pytest.mark.comments
def test_comment_list_by_user_empty_ok(client: TestClient):
    response = client.get("/comments/by_user/1")

    assert response.status_code == 200
    assert len(response.json()["comments"]) == 0


# 없는거 로직을 넣어야 하나?
# def test_comment_list_fail(client: TestClient):
#     response = client.get(
#         "/posts"
#     )
#     assert response.status_code == 500


@pytest.mark.patch
def test_comment_patch_ok(client: TestClient):
    client.post(
        url="/comments/1",
        json={
            "content": "test_comment_1",
        },
    )

    response = client.patch(url="/comments/1", json={"content": "test_comment_1_edit"})
    assert response.status_code == 204

    comment_response = client.get("/comments/by_post/1")
    assert comment_response.status_code == 200
    assert comment_response.json()["comments"][0]["content"] == "test_comment_1_edit"


@pytest.mark.patch
def test_comment_patch_not_exists(client: TestClient):
    response = client.patch(url="/comments/1", json={"content": "test_comment_1_edit"})

    assert response.status_code == 400
    assert response.json()["detail"] == "존재하지 않는 코멘트입니다"


@pytest.mark.patch
def test_comment_patch_invalid_author(client: TestClient):
    client.post(
        url="/comments/1",
        json={
            "content": "test_comment_1",
        },
    )

    # 다른 아이디로 수정 시도. 세션아이디 변경 됨
    client.post(
        "/users",
        json={
            "nickname": "test_user_2",
            "password": "Test_password",
        },
    )

    client.post(
        "/users/login",
        json={
            "nickname": "test_user_2",
            "password": "Test_password",
        },
    )

    # 쿠키에 이미 변경된 아이디가 들어있음. 명시로 다시 넣어주는게 좋은가?

    response = client.patch(url="/comments/1", json={"content": "test_content_1_edit"})

    assert response.status_code == 403
    assert response.json()["detail"] == "작성자만 수정할 수 있습니다"


@pytest.mark.patch
def test_comment_patch_admin_role(client: TestClient):
    client.post(
        url="/comments/1",
        json={
            "content": "test_comment_1",
        },
    )

    # admin role로 수정 시도. 세션아이디 변경 됨
    client.post(
        "/users",
        json={"nickname": "test_user_2", "password": "Test_password", "role": "admin"},
    )

    client.post(
        "/users/login",
        json={
            "nickname": "test_user_2",
            "password": "Test_password",
        },
    )

    response = client.patch(url="/comments/1", json={"content": "test_content_1_edit"})

    assert response.status_code == 204


@pytest.mark.delete
def test_comment_delete_ok(client: TestClient):
    client.post(
        url="/comments/1",
        json={
            "content": "test_comment_1",
        },
    )

    delete_response = client.delete(url="/comments/1")
    assert delete_response.status_code == 204

    comment_response = client.get("/comments/by_post/1")
    assert comment_response.status_code == 200
    assert comment_response.json()["comments"] == []


@pytest.mark.delete
def test_comment_delete_not_exists(client: TestClient):
    response = client.delete(url="/comments/1")

    assert response.status_code == 400
    assert response.json()["detail"] == "존재하지 않는 코멘트입니다"


@pytest.mark.delete
def test_comment_delete_invalid_author(client: TestClient):
    client.post(
        "/comments/1",
        json={
            "content": "test_comment_1",
        },
    )

    # 다른 아이디로 삭제 시도. 세션아이디 변경 됨
    client.post(
        "/users",
        json={
            "nickname": "test_user_2",
            "password": "Test_password",
        },
    )

    client.post(
        "/users/login",
        json={
            "nickname": "test_user_2",
            "password": "Test_password",
        },
    )

    # 쿠키에 이미 변경된 아이디가 들어있음. 명시로 다시 넣어주는게 좋은가?

    response = client.delete(url="/comments/1")

    assert response.status_code == 403
    assert response.json()["detail"] == "작성자만 삭제할 수 있습니다"


@pytest.mark.delete
def test_comment_delete_admin_role(client: TestClient):
    client.post(
        "/comments/1",
        json={
            "content": "test_comment_1",
        },
    )

    # 다른 아이디로 삭제 시도. 세션아이디 변경 됨
    client.post(
        "/users",
        json={"nickname": "test_user_2", "password": "Test_password", "role": "admin"},
    )

    client.post(
        "/users/login",
        json={
            "nickname": "test_user_2",
            "password": "Test_password",
        },
    )

    # 쿠키에 이미 변경된 아이디가 들어있음. 명시로 다시 넣어주는게 좋은가?

    response = client.delete(url="/comments/1")

    assert response.status_code == 204
