from fastapi.testclient import TestClient

from fastapi.testclient import TestClient
import pytest

from main import app


@pytest.mark.create
def test_signup_user_ok():
    with TestClient(app) as client:
        response = client.post(
            "/users",
            json={
                "nickname": "test_user",
                "password": "Test_password",
            },
        )
        assert response.status_code == 201
        assert response.json() == {"id": 1, "nickname": "test_user"}


@pytest.mark.create
def test_signup_user_not_upper():
    with TestClient(app) as client:
        response = client.post(
            "/users",
            json={
                "nickname": "test_user",
                "password": "test_password",
            },
        )
        assert response.status_code == 400
        assert (
            response.json()["detail"] == "문자열에 대문자가 하나 이상 포함되어야 합니다"
        )


@pytest.mark.create
def test_signup_user_invalid_params():
    with TestClient(app) as client:
        response = client.post(
            "/users",
            json={
                "nickname": "",
                "password": "",
            },
        )
        assert response.status_code == 422
        # assert response.json()['detail'] == "문자열에 대문자가 하나 이상 포함되어야 합니다"


@pytest.mark.create
def test_signup_user_duplicate():
    with TestClient(app) as client:
        client.post(
            "/users",
            json={
                "nickname": "test_user",
                "password": "Test_password",
            },
        )

        response = client.post(
            "/users",
            json={
                "nickname": "test_user",
                "password": "Test_password",
            },
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "이미 가입한 유저입니다"


@pytest.mark.login
def test_login_ok():
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
        assert response.status_code == 200
        assert response.json()["session_id"]


@pytest.mark.login
def test_login_invalid_nikcname():
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
                "nickname": "invalid_user",
                "password": "Test_password",
            },
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "존재하지 않는 유저입니다"


@pytest.mark.login
def test_login_invalid_password():
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
                "password": "invalid_password",
            },
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "잘못된 비밀번호입니다"


@pytest.mark.logout
def test_logout_ok():
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

        response = client.post("/users/logout")

        assert response.status_code == 200


@pytest.mark.logout
def test_logout_invalid_session_id():
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

        client.cookies = {"session_id": "invalid_session_id"}
        response = client.post("/users/logout")

        assert response.status_code == 400
        assert response.json()["detail"] == "존재하지 않는 세션입니다"
