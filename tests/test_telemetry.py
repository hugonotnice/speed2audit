from unittest.mock import patch
import pytest
from speed2audit.telemetry import init_local_telemetry


def test_init_local_telemetry_disabled():
    with patch("speed2audit.telemetry.PHOENIX_ENABLE", False):
        session = init_local_telemetry()
        assert session is None


def test_init_local_telemetry_enabled():
    with patch("speed2audit.telemetry.PHOENIX_ENABLE", True), \
         patch("speed2audit.telemetry.px.launch_app") as mock_launch:

        mock_launch.return_value = "http://127.0.0.1:6006"
        session = init_local_telemetry()

        assert session == "http://127.0.0.1:6006"
        mock_launch.assert_called_once()
