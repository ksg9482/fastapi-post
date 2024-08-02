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

        response = client.post(
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

        yield client


@pytest.mark.create
def test_create_post_ok(client: TestClient):
    response = client.post(
        "/posts",
        json={
            "title": "test_title",
            "content": "test_content",
        },
    )
    assert response.status_code == 201
    assert response.json()["id"]


@pytest.mark.create
def test_create_post_invalid_params(client: TestClient):

    response = client.post(
        "/posts",
        json={
            "title": None,
            "content": None,
        },
    )
    assert response.status_code == 422


@pytest.mark.posts
def test_post_list_ok(client: TestClient):
    client.post(
        "/posts",
        json={
            "title": "test_title_1",
            "content": "test_content_1",
        },
    )

    client.post(
        "/posts",
        json={
            "title": "test_title_2",
            "content": "test_content_2",
        },
    )

    response = client.get("/posts")

    assert response.status_code == 200
    assert len(response.json()["posts"]) == 2


@pytest.mark.posts
def test_post_list_empty_ok(client: TestClient):
    response = client.get("/posts")

    assert response.status_code == 200
    assert len(response.json()["posts"]) == 0


# 없는거 로직을 넣어야 하나?
# def test_post_list_fail(client: TestClient):
#     response = client.get(
#         "/posts"
#     )
#     assert response.status_code == 500


@pytest.mark.post
def test_post_find_one_ok(client: TestClient):
    client.post(
        "/posts",
        json={
            "title": "test_title_1",
            "content": "test_content_1",
        },
    )

    response = client.get("/posts/1")
    print(response.json())

    assert response.status_code == 200
    assert response.json()["title"] == "test_title_1"
    assert response.json()["content"] == "test_content_1"


@pytest.mark.post
def test_post_find_one_not_exists(client: TestClient):
    response = client.get("/posts/1")
    assert response.status_code == 400
    assert response.json()["detail"] == "존재하지 않는 포스트입니다"


@pytest.mark.patch
def test_post_patch_ok(client: TestClient):
    client.post(
        url="/posts",
        json={
            "title": "test_title_1",
            "content": "test_content_1",
        },
    )

    client.patch(url="/posts/1", json={"content": "test_content_1_edit"})

    response = client.get("/posts/1")
    assert response.status_code == 200
    assert response.json()["content"] == "test_content_1_edit"


@pytest.mark.patch
def test_post_patch_not_exists(client: TestClient):
    client.patch(url="/posts/1", json={"content": "test_content_1_edit"})

    response = client.get("/posts/1")
    assert response.status_code == 400
    assert response.json()["detail"] == "존재하지 않는 포스트입니다"


@pytest.mark.patch
def test_post_patch_invalid_author(client: TestClient):
    client.post(
        "/posts",
        json={
            "title": "test_title_1",
            "content": "test_content_1",
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

    response = client.patch(url="/posts/1", json={"content": "test_content_1_edit"})

    assert response.status_code == 403
    assert response.json()["detail"] == "작성자만 수정할 수 있습니다"


@pytest.mark.put
def test_post_put_ok(client: TestClient):
    client.post(
        url="/posts",
        json={
            "title": "test_title_1",
            "content": "test_content_1",
        },
    )

    client.put(
        url="/posts/1",
        json={"title": "test_title_1_edit", "content": "test_content_1_edit"},
    )

    response = client.get("/posts/1")
    assert response.status_code == 200
    assert response.json()["title"] == "test_title_1_edit"
    assert response.json()["content"] == "test_content_1_edit"


@pytest.mark.put
def test_post_put_not_exists(client: TestClient):
    response = client.put(
        url="/posts/1",
        json={"title": "test_title_1_edit", "content": "test_content_1_edit"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "존재하지 않는 포스트입니다"


@pytest.mark.put
def test_post_put_invalid_author(client: TestClient):
    client.post(
        "/posts",
        json={
            "title": "test_title_1",
            "content": "test_content_1",
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

    response = client.put(
        url="/posts/1",
        json={"title": "test_title_1_edit", "content": "test_content_1_edit"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "작성자만 수정할 수 있습니다"


@pytest.mark.put
def test_post_put_missing_field(client: TestClient):
    client.post(
        url="/posts",
        json={
            "title": "test_title_1",
            "content": "test_content_1",
        },
    )

    response = client.put(url="/posts/1", json={"content": "test_content_1_edit"})

    assert response.status_code == 422


@pytest.mark.delete
def test_post_delete_ok(client: TestClient):
    client.post(
        url="/posts",
        json={
            "title": "test_title_1",
            "content": "test_content_1",
        },
    )

    delete_response = client.delete(url="/posts/1")
    assert delete_response.status_code == 204

    # 삭제 포스트 검증
    post_response = client.get("/posts/1")
    assert post_response.status_code == 400
    assert post_response.json()["detail"] == "존재하지 않는 포스트입니다"


@pytest.mark.delete
def test_post_delete_invalid_author(client: TestClient):
    client.post(
        "/posts",
        json={
            "title": "test_title_1",
            "content": "test_content_1",
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

    response = client.delete(url="/posts/1")

    assert response.status_code == 403
    assert response.json()["detail"] == "작성자만 삭제할 수 있습니다"
