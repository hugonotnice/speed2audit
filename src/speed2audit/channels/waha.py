from enum import Enum
import httpx
from speed2audit.config import WAHA_API_KEY, WAHA_BASE_URL, WAHA_SESSION


class WAHASessionStatus(str, Enum):
    STOPPED = "STOPPED"
    STARTING = "STARTING"
    SCAN_QR_CODE = "SCAN_QR_CODE"
    WORKING = "WORKING"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


class WAHAClient:
    """Asynchronous client for interacting with the local-first WAHA WhatsApp HTTP API."""

    def __init__(
        self,
        base_url: str = WAHA_BASE_URL,
        session_name: str = WAHA_SESSION,
        api_key: str = WAHA_API_KEY,
        timeout: float = 10.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.session_name = session_name
        self.api_key = api_key
        self.timeout = timeout

    def _get_headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-Api-Key"] = self.api_key
        return headers

    async def check_server_online(self) -> bool:
        """Check if WAHA HTTP server is reachable."""
        url = f"{self.base_url}/api/server/version"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.get(url, headers=self._get_headers())
                return res.status_code == 200
        except Exception:
            return False

    async def get_session_status(self) -> WAHASessionStatus:
        """Retrieve the operational status of the current WhatsApp session."""
        url = f"{self.base_url}/api/sessions/{self.session_name}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.get(url, headers=self._get_headers())
                if res.status_code != 200:
                    return WAHASessionStatus.UNKNOWN
                data = res.json()
                raw_status = data.get("status", "").upper()
                return WAHASessionStatus(raw_status) if raw_status in WAHASessionStatus.__members__ else WAHASessionStatus.UNKNOWN
        except Exception:
            return WAHASessionStatus.UNKNOWN

    async def start_session(self) -> bool:
        """Start or initialize the WhatsApp session."""
        url = f"{self.base_url}/api/sessions/{self.session_name}/start"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(url, headers=self._get_headers())
                return res.status_code in (200, 201)
        except Exception:
            return False

    async def get_qr_code(self) -> str | None:
        """Get the QR code image base64 or raw string for pairing."""
        url = f"{self.base_url}/api/sessions/{self.session_name}/auth/qr"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.get(url, headers=self._get_headers())
                if res.status_code == 200:
                    data = res.json()
                    return data.get("qr") or data.get("raw")
                return None
        except Exception:
            return None

    async def send_text(self, chat_id: str, text: str) -> dict:
        """Send a plain text message to a WhatsApp recipient."""
        url = f"{self.base_url}/api/sendText"
        payload = {
            "session": self.session_name,
            "chatId": chat_id,
            "text": text,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            res = await client.post(url, json=payload, headers=self._get_headers())
            res.raise_for_status()
            return res.json()

    async def start_typing(self, chat_id: str) -> bool:
        """Send 'typing...' presence to the chat."""
        url = f"{self.base_url}/api/startTyping"
        payload = {
            "session": self.session_name,
            "chatId": chat_id,
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(url, json=payload, headers=self._get_headers())
                return res.status_code in (200, 201)
        except Exception:
            return False

    async def stop_typing(self, chat_id: str) -> bool:
        """Stop 'typing...' presence in the chat."""
        url = f"{self.base_url}/api/stopTyping"
        payload = {
            "session": self.session_name,
            "chatId": chat_id,
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(url, json=payload, headers=self._get_headers())
                return res.status_code in (200, 201)
        except Exception:
            return False
