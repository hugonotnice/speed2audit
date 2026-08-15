from datetime import datetime, timezone

from pydantic import BaseModel, Field


class WAHAInboundMessage(BaseModel):
    message_id: str
    from_phone: str
    to_phone: str | None = None
    body: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    from_me: bool = False


def parse_waha_webhook_payload(data: dict) -> WAHAInboundMessage | None:
    """Parse incoming WAHA webhook events and extract incoming text messages."""
    event = data.get("event")
    if event not in ("message", "message.any", "message.upsert"):
        return None

    payload = data.get("payload", {})
    from_me = payload.get("fromMe", False)
    if from_me:
        # Ignore messages sent by our own shopper bot
        return None

    msg_id = payload.get("id", "")
    from_phone = payload.get("from", "")
    to_phone = payload.get("to")
    body = payload.get("body", "")

    if not body or not from_phone:
        return None

    ts_raw = payload.get("timestamp")
    if isinstance(ts_raw, (int, float)):
        ts = datetime.fromtimestamp(ts_raw, tz=timezone.utc)
    else:
        ts = datetime.now(timezone.utc)

    return WAHAInboundMessage(
        message_id=str(msg_id),
        from_phone=str(from_phone),
        to_phone=str(to_phone) if to_phone else None,
        body=str(body),
        timestamp=ts,
        from_me=from_me,
    )
