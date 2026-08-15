import logging
import phoenix as px
from speed2audit.config import PHOENIX_ENABLE

logger = logging.getLogger(__name__)

_phoenix_session = None


def init_local_telemetry() -> str | None:
    """Initialize local-first Arize Phoenix observability bound strictly to localhost."""
    global _phoenix_session

    if not PHOENIX_ENABLE:
        logger.info("Phoenix telemetry is disabled via configuration.")
        return None

    if _phoenix_session is not None:
        return "http://127.0.0.1:6006"

    try:
        # Launch local Phoenix in-process server bound strictly to localhost:6006
        _phoenix_session = px.launch_app(host="127.0.0.1", port=6006)
        logger.info("Arize Phoenix local observability initialized on http://127.0.0.1:6006")
        return "http://127.0.0.1:6006"
    except Exception as e:
        logger.warning(f"Could not launch Arize Phoenix locally: {e}")
        return None
