from datetime import datetime, timezone
import pytest
from speed2audit.core.models import (
    AuditSession,
    AuditStatus,
    ConversationTurn,
    MessageRole,
    PersonaProfile,
    Scorecard,
)


def test_persona_profile_creation():
    persona = PersonaProfile(
        full_name="Sarah Jenkins",
        company_name="Acme Logistics",
        role="Operations Director",
        core_pain_point="Need immediate route optimization software for 50 vehicles",
        budget_range="$5,000 - $10,000/mo",
        urgency_level="High",
        extra_instructions="Request a demo and insist on a customized quote today.",
    )
    assert persona.full_name == "Sarah Jenkins"
    assert persona.urgency_level == "High"
    assert persona.company_name == "Acme Logistics"


def test_conversation_turn_and_metrics():
    now = datetime.now(timezone.utc)
    turn = ConversationTurn(
        turn_index=1,
        role=MessageRole.SHOPPER,
        content="Hello! Do you have fleet tracking pricing available?",
        timestamp=now,
        latency_seconds_since_last=None,
    )
    assert turn.turn_index == 1
    assert turn.role == MessageRole.SHOPPER
    assert turn.content == "Hello! Do you have fleet tracking pricing available?"


def test_scorecard_validation():
    scorecard = Scorecard(
        first_response_time_seconds=142.5,
        total_duration_seconds=1250.0,
        total_turns=6,
        clarity_score=8.5,
        objection_handling_score=7.0,
        proactivity_score=9.0,
        executive_summary="Attendant was polite, provided pricing within 20 minutes.",
        key_strengths=["Fast first response", "Clear pricing structure"],
        areas_for_improvement=["Failed to offer meeting time slots proactively"],
    )
    assert scorecard.clarity_score == 8.5
    assert scorecard.first_response_time_seconds == 142.5

    # Test score bounds validation (0 to 10)
    with pytest.raises(Exception):
        Scorecard(
            first_response_time_seconds=10.0,
            total_duration_seconds=100.0,
            total_turns=2,
            clarity_score=11.0,  # Invalid: > 10
            objection_handling_score=5.0,
            proactivity_score=5.0,
            executive_summary="Invalid test",
            key_strengths=[],
            areas_for_improvement=[],
        )


def test_audit_session_lifecycle():
    session = AuditSession(
        session_id="aud_12345",
        website_url="https://acme.com",
        target_phone="+15551234567",
        status=AuditStatus.INITIALIZING,
    )
    assert session.status == AuditStatus.INITIALIZING
    assert session.turns == []
    assert session.scorecard is None

    # Simulate transition to completed
    session.status = AuditStatus.COMPLETED_SUCCESS
    assert session.status == AuditStatus.COMPLETED_SUCCESS
