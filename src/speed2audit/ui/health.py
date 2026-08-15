from pydantic import BaseModel

from speed2audit.channels.waha import WAHAClient, WAHASessionStatus
from speed2audit.config import GEMINI_API_KEY


class HealthStatus(BaseModel):
    gemini_configured: bool
    waha_online: bool
    waha_session_status: WAHASessionStatus
    qr_code_needed: bool = False
    qr_code_data: str | None = None
    is_ready: bool


class HealthChecker:
    """Module A: Evaluates global health and readiness of external channels and AI keys."""

    def __init__(self, waha_client: WAHAClient | None = None):
        self.waha = waha_client or WAHAClient()

    async def run_health_check(self, gemini_key: str = GEMINI_API_KEY) -> HealthStatus:
        """Run connectivity checks for WAHA container, WhatsApp session, and Gemini key."""
        gemini_ok = bool(gemini_key and len(gemini_key.strip()) > 5)

        waha_online = await self.waha.check_server_online()
        waha_status = WAHASessionStatus.UNKNOWN
        qr_needed = False
        qr_data = None

        if waha_online:
            waha_status = await self.waha.get_session_status()
            if waha_status == WAHASessionStatus.SCAN_QR_CODE:
                qr_needed = True
                qr_data = await self.waha.get_qr_code()
            elif waha_status == WAHASessionStatus.STOPPED:
                # Attempt to auto-start session
                await self.waha.start_session()
                waha_status = await self.waha.get_session_status()
                if waha_status == WAHASessionStatus.SCAN_QR_CODE:
                    qr_needed = True
                    qr_data = await self.waha.get_qr_code()

        is_ready = gemini_ok and waha_online and (waha_status == WAHASessionStatus.WORKING)

        return HealthStatus(
            gemini_configured=gemini_ok,
            waha_online=waha_online,
            waha_session_status=waha_status,
            qr_code_needed=qr_needed,
            qr_code_data=qr_data,
            is_ready=is_ready,
        )
