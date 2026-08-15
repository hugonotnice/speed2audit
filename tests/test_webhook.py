from datetime import datetime, timezone
import pytest
from speed2audit.channels.webhook import parse_waha_webhook_payload, WAHAInboundMessage


def test_parse_valid_waha_message_payload():
    payload = {
        "event": "message",
        "session": "default",
        "payload": {
            "id": "msg_xyz_987",
            "timestamp": 1771171200,
            "from": "5511999998888@c.us",
            "to": "5511888887777@c.us",
            "body": "Olá! Temos condições especiais para empresas sim.",
            "fromMe": False,
            "hasMedia": False,
        },
    }

    parsed: WAHAInboundMessage | None = parse_waha_webhook_payload(payload)

    assert parsed is not None
    assert parsed.message_id == "msg_xyz_987"
    assert parsed.from_phone == "5511999998888@c.us"
    assert parsed.body == "Olá! Temos condições especiais para empresas sim."
    assert parsed.from_me is False


def test_parse_waha_outgoing_message_ignored():
    payload = {
        "event": "message",
        "session": "default",
        "payload": {
            "id": "msg_outgoing_111",
            "from": "5511888887777@c.us",
            "to": "5511999998888@c.us",
            "body": "Minha própria mensagem",
            "fromMe": True,
        },
    }

    parsed = parse_waha_webhook_payload(payload)
    assert parsed is None


def test_parse_non_message_event():
    payload = {
        "event": "session.status",
        "session": "default",
        "payload": {"status": "WORKING"},
    }

    parsed = parse_waha_webhook_payload(payload)
    assert parsed is None
