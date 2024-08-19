from httpx import ASGITransport, AsyncClient
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from main import app
from src.database import get_session
from src.domains.user import User


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="session")
async def test_db_init():
    test_engine = create_async_engine(url=TEST_DATABASE_URL, future=True)
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

    yield test_engine

    await test_engine.dispose()


@pytest_asyncio.fixture
async def test_session(test_db_init: AsyncEngine) -> AsyncSession:
    AsyncSessionLocal = async_sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_db_init,
        class_=AsyncSession,
    )
    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture
def test_client(test_session: AsyncSession):
    async def override_get_session():
        yield test_session

    app.dependency_overrides[get_session] = override_get_session

    client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test/users")
    yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.create
async def test_signup_user_ok(test_client: AsyncClient, test_session: AsyncSession):

    # with test_client as client:
    response = await test_client.post(
        "/",
        json={
            "nickname": "test_user",
            "password": "Test_password",
        },
    )
    assert response.status_code == 201
    assert response.json() == {"id": 1, "nickname": "test_user"}

    result = await test_session.exec(select(User).where(User.nickname == "test_user"))
    user = result.first()
    assert user.nickname == "test_user"


# @pytest.mark.create
# def test_signup_user_not_upper():
#     with TestClient(app) as client:
#         response = client.post(
#             "/users",
#             json={
#                 "nickname": "test_user",
#                 "password": "test_password",
#             },
#         )
#         assert response.status_code == 400
#         assert (
#             response.json()["detail"] == "문자열에 대문자가 하나 이상 포함되어야 합니다"
#         )


# @pytest.mark.create
# def test_signup_user_invalid_params():
#     with TestClient(app) as client:
#         response = client.post(
#             "/users",
#             json={
#                 "nickname": "",
#                 "password": "",
#             },
#         )
#         assert response.status_code == 422


# @pytest.mark.create
# def test_signup_user_duplicate():
#     with TestClient(app) as client:
#         client.post(
#             "/users",
#             json={
#                 "nickname": "test_user",
#                 "password": "Test_password",
#             },
#         )

#         response = client.post(
#             "/users",
#             json={
#                 "nickname": "test_user",
#                 "password": "Test_password",
#             },
#         )
#         assert response.status_code == 409
#         assert response.json()["detail"] == "이미 가입한 유저입니다"


# @pytest.mark.login
# def test_login_ok():
#     with TestClient(app) as client:
#         client.post(
#             "/users",
#             json={
#                 "nickname": "test_user",
#                 "password": "Test_password",
#             },
#         )

#         response = client.post(
#             "/users/login",
#             json={
#                 "nickname": "test_user",
#                 "password": "Test_password",
#             },
#         )
#         assert response.status_code == 200
#         assert response.json()["session_id"]


# @pytest.mark.login
# def test_login_invalid_nikcname():
#     with TestClient(app) as client:
#         client.post(
#             "/users",
#             json={
#                 "nickname": "test_user",
#                 "password": "Test_password",
#             },
#         )

#         response = client.post(
#             "/users/login",
#             json={
#                 "nickname": "invalid_user",
#                 "password": "Test_password",
#             },
#         )
#         assert response.status_code == 401
#         assert response.json()["detail"] == "존재하지 않는 유저입니다"


# @pytest.mark.login
# def test_login_invalid_password():
#     with TestClient(app) as client:
#         client.post(
#             "/users",
#             json={
#                 "nickname": "test_user",
#                 "password": "Test_password",
#             },
#         )

#         response = client.post(
#             "/users/login",
#             json={
#                 "nickname": "test_user",
#                 "password": "invalid_password",
#             },
#         )
#         assert response.status_code == 401
#         assert response.json()["detail"] == "잘못된 비밀번호입니다"


# @pytest.mark.logout
# def test_logout_ok():
#     with TestClient(app) as client:
#         client.post(
#             "/users",
#             json={
#                 "nickname": "test_user",
#                 "password": "Test_password",
#             },
#         )

#         response = client.post(
#             "/users/login",
#             json={
#                 "nickname": "test_user",
#                 "password": "Test_password",
#             },
#         )

#         response = client.post("/users/logout")

#         assert response.status_code == 200


# @pytest.mark.logout
# def test_logout_invalid_session_id():
#     with TestClient(app) as client:
#         client.post(
#             "/users",
#             json={
#                 "nickname": "test_user",
#                 "password": "Test_password",
#             },
#         )

#         response = client.post(
#             "/users/login",
#             json={
#                 "nickname": "test_user",
#                 "password": "Test_password",
#             },
#         )

#         client.cookies = {"session_id": "invalid_session_id"}
#         response = client.post("/users/logout")

#         assert response.status_code == 400
#         assert response.json()["detail"] == "존재하지 않는 세션입니다"
