import pytest
from git_web.helpers import Config
from quart import Quart


@pytest.mark.asyncio
async def test_login_required(app: Quart):
    client = app.test_client()
    response = await client.get("/")
    assert response.status_code == 302


@pytest.mark.asyncio
async def test_get_login(app: Quart):
    client = app.test_client()
    response = await client.get("/auth/login")
    assert response.status_code == 200


class TestPostLogins:
    @pytest.mark.asyncio
    async def test_valid(self, app_config: Config, app: Quart):
        test_client = app.test_client()
        response = await test_client.post(
            "/auth/login",
            form = {
                "password": app_config.LOGIN_PASSWORD,
            },
        )
        assert response.status_code == 302

    @pytest.mark.asyncio
    async def test_invalid_form(self, app: Quart):
        test_client = app.test_client()
        response = await test_client.post(
            "/auth/login",
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_invalid_password(self, app: Quart):
        test_client = app.test_client()
        response = await test_client.post(
            "/auth/login",
            form = {
                "password": "wrong password 1234",
            },
        )
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_do_logout(app_config: Config, app: Quart):
    test_client = app.test_client()
    response = await test_client.post(
        "/auth/login",
        form = {
            "password": app_config.LOGIN_PASSWORD,
        },
    )
    assert response.status_code == 302
    async with test_client.authenticated("1"):
        response = await test_client.get("/auth/logout")
        assert response.status_code == 302
    response = await test_client.get("/")
    assert response.status_code == 302
