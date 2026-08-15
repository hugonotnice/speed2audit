import httpx
import pytest
import respx

from speed2audit.channels.waha import WAHAClient, WAHASessionStatus


@pytest.mark.asyncio
async def test_waha_client_get_status():
    client = WAHAClient(base_url="http://localhost:3000", session_name="default")

    with respx.mock(base_url="http://localhost:3000") as respx_mock:
        respx_mock.get("/api/server/version").mock(
            return_value=httpx.Response(200, json={"version": "2026.1.0", "engine": "NOWEB"})
        )

        is_online = await client.check_server_online()
        assert is_online is True


@pytest.mark.asyncio
async def test_waha_client_get_session_status():
    client = WAHAClient(base_url="http://localhost:3000", session_name="default")

    with respx.mock(base_url="http://localhost:3000") as respx_mock:
        respx_mock.get("/api/sessions/default").mock(
            return_value=httpx.Response(200, json={"name": "default", "status": "WORKING"})
        )

        status = await client.get_session_status()
        assert status == WAHASessionStatus.WORKING


@pytest.mark.asyncio
async def test_waha_client_send_text_message():
    client = WAHAClient(base_url="http://localhost:3000", session_name="default")

    with respx.mock(base_url="http://localhost:3000") as respx_mock:
        route = respx_mock.post("/api/sendText").mock(
            return_value=httpx.Response(200, json={"id": "msg_123", "ack": 1})
        )

        resp = await client.send_text(
            chat_id="5511999998888@c.us", text="Hello, I need pricing information."
        )

        assert resp["id"] == "msg_123"
        assert route.called
        sent_body = route.calls.last.request.read().decode()
        assert "5511999998888@c.us" in sent_body
        assert "Hello, I need pricing information." in sent_body


@pytest.mark.asyncio
async def test_waha_client_typing_indicator():
    client = WAHAClient(base_url="http://localhost:3000", session_name="default")

    with respx.mock(base_url="http://localhost:3000") as respx_mock:
        start_route = respx_mock.post("/api/startTyping").mock(
            return_value=httpx.Response(200, json={"success": True})
        )
        stop_route = respx_mock.post("/api/stopTyping").mock(
            return_value=httpx.Response(200, json={"success": True})
        )

        ok_start = await client.start_typing("5511999998888@c.us")
        ok_stop = await client.stop_typing("5511999998888@c.us")

        assert ok_start is True
        assert ok_stop is True
        assert start_route.called
        assert stop_route.called
