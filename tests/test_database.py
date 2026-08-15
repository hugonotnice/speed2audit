import pytest
from speed2audit.core.database import AuditDatabase
from speed2audit.core.models import (
    AuditSession,
    AuditStatus,
    ConversationTurn,
    MessageRole,
    PersonaProfile,
    Scorecard,
)


@pytest.fixture
def db(tmp_path):
    db_file = tmp_path / "test_audit.db"
    return AuditDatabase(db_path=str(db_file))


def test_database_save_and_get_session(db):
    session = AuditSession(
        session_id="session_abc_001",
        website_url="https://saascompany.com",
        target_phone="+5511999998888",
        status=AuditStatus.INITIALIZING,
        persona=PersonaProfile(
            full_name="Carlos Silva",
            role="Tech Lead",
            core_pain_point="Preciso de integracao via API rapida",
        ),
    )

    db.save_session(session)
    retrieved = db.get_session("session_abc_001")

    assert retrieved is not None
    assert retrieved.session_id == "session_abc_001"
    assert retrieved.website_url == "https://saascompany.com"
    assert retrieved.target_phone == "+5511999998888"
    assert retrieved.persona.full_name == "Carlos Silva"
    assert retrieved.status == AuditStatus.INITIALIZING


def test_database_update_turns_and_scorecard(db):
    session = AuditSession(
        session_id="session_abc_002",
        website_url="https://logistics.com",
        target_phone="+15559876543",
        status=AuditStatus.AUDITING,
    )
    db.save_session(session)

    # Add turns
    turn1 = ConversationTurn(
        turn_index=1,
        role=MessageRole.SHOPPER,
        content="Oi, quanto custa a mensalidade?",
    )
    turn2 = ConversationTurn(
        turn_index=2,
        role=MessageRole.TARGET_SELLER,
        content="Olá! Custa R$ 500/mês.",
        latency_seconds_since_last=45.0,
    )
    session.turns.extend([turn1, turn2])
    session.status = AuditStatus.COMPLETED_SUCCESS
    session.scorecard = Scorecard(
        first_response_time_seconds=45.0,
        total_duration_seconds=45.0,
        total_turns=2,
        clarity_score=10.0,
        objection_handling_score=8.0,
        proactivity_score=8.5,
        executive_summary="Vendedor respondeu rápido e deu o preço direto.",
        key_strengths=["Velocidade recorde"],
        areas_for_improvement=["Poderia ter oferecido demonstração"],
    )

    db.save_session(session)
    updated = db.get_session("session_abc_002")

    assert len(updated.turns) == 2
    assert updated.turns[1].role == MessageRole.TARGET_SELLER
    assert updated.scorecard.clarity_score == 10.0
    assert updated.status == AuditStatus.COMPLETED_SUCCESS


def test_database_list_sessions(db):
    s1 = AuditSession(
        session_id="sess_1",
        website_url="https://site1.com",
        target_phone="+111",
        status=AuditStatus.COMPLETED_SUCCESS,
    )
    s2 = AuditSession(
        session_id="sess_2",
        website_url="https://site2.com",
        target_phone="+222",
        status=AuditStatus.COMPLETED_TIMEOUT,
    )
    db.save_session(s1)
    db.save_session(s2)

    sessions = db.list_sessions()
    assert len(sessions) == 2
    session_ids = [s.session_id for s in sessions]
    assert "sess_1" in session_ids
    assert "sess_2" in session_ids
