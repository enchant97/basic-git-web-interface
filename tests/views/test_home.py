import pytest
from quart import Quart


@pytest.mark.asyncio
async def test_index(app: Quart):
    test_client = app.test_client()
    response = await test_client.get("/")
    assert response.status_code == 200
    assert "A fast and minimal git web interface" in await response.get_data(as_text=True)


@pytest.mark.asyncio
async def test_index_authenticated(app: Quart):
    test_client = app.test_client()
    async with test_client.authenticated("1"):
        response = await test_client.get("/")
        assert response.status_code == 200
        assert "Log Out" in await response.get_data(as_text=True)
