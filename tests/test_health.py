from unittest.mock import AsyncMock, patch

import pytest

from speed2audit.channels.waha import WAHASessionStatus
from speed2audit.ui.health import HealthChecker, HealthStatus


@pytest.mark.asyncio
async def test_health_checker_all_ok():
    checker = HealthChecker()

    with (
        patch(
            "speed2audit.ui.health.WAHAClient.check_server_online", new_callable=AsyncMock
        ) as mock_online,
        patch(
            "speed2audit.ui.health.WAHAClient.get_session_status", new_callable=AsyncMock
        ) as mock_status,
    ):
        mock_online.return_value = True
        mock_status.return_value = WAHASessionStatus.WORKING

        status: HealthStatus = await checker.run_health_check(gemini_key="AIzaSyDummyKey")

        assert status.gemini_configured is True
        assert status.waha_online is True
        assert status.waha_session_status == WAHASessionStatus.WORKING
        assert status.is_ready is True


@pytest.mark.asyncio
async def test_health_checker_waha_offline():
    checker = HealthChecker()

    with (
        patch(
            "speed2audit.ui.health.WAHAClient.check_server_online", new_callable=AsyncMock
        ) as mock_online,
        patch(
            "speed2audit.ui.health.WAHAClient.get_session_status", new_callable=AsyncMock
        ) as mock_status,
    ):
        mock_online.return_value = False
        mock_status.return_value = WAHASessionStatus.UNKNOWN

        status: HealthStatus = await checker.run_health_check(gemini_key="AIzaSyDummyKey")

        assert status.gemini_configured is True
        assert status.waha_online is False
        assert status.is_ready is False
