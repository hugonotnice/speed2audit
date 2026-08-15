from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest

from speed2audit.agents.auditor import AuditEvaluation, AuditorAgent
from speed2audit.core.models import (
    AuditSession,
    AuditStatus,
    ConversationTurn,
    MessageRole,
    PersonaProfile,
    Scorecard,
)


@pytest.fixture
def audit_session_with_transcript():
    start_time = datetime.now(timezone.utc)
    turn1_time = start_time
    turn2_time = start_time + timedelta(seconds=75)
    turn3_time = start_time + timedelta(seconds=120)
    turn4_time = start_time + timedelta(seconds=210)

    turns = [
        ConversationTurn(
            turn_index=1,
            role=MessageRole.SHOPPER,
            content="Olá, gostaria de um orçamento para rastreamento de 40 carretas.",
            timestamp=turn1_time,
        ),
        ConversationTurn(
            turn_index=2,
            role=MessageRole.TARGET_SELLER,
            content="Olá! Claro, nosso plano empresarial sai por R$ 79/veículo.",
            timestamp=turn2_time,
            latency_seconds_since_last=75.0,
        ),
        ConversationTurn(
            turn_index=3,
            role=MessageRole.SHOPPER,
            content="Tem desconto para pagamento anual ou taxa de instalação?",
            timestamp=turn3_time,
        ),
        ConversationTurn(
            turn_index=4,
            role=MessageRole.TARGET_SELLER,
            content="No anual damos 15% e a instalação é 100% gratuita!",
            timestamp=turn4_time,
            latency_seconds_since_last=90.0,
        ),
    ]

    return AuditSession(
        session_id="aud_eval_01",
        website_url="https://acmefleet.com",
        target_phone="5511999998888@c.us",
        status=AuditStatus.AUDITING,
        persona=PersonaProfile(
            full_name="Lucas Andrade",
            role="Gerente de Logística",
            core_pain_point="Rastreamento para 40 veículos",
        ),
        turns=turns,
    )


@pytest.mark.asyncio
async def test_auditor_calculates_telemetry_and_scorecard(audit_session_with_transcript):
    auditor = AuditorAgent()

    mock_eval = AuditEvaluation(
        clarity_score=9.5,
        objection_handling_score=9.0,
        proactivity_score=8.5,
        executive_summary="Atendimento excelente, rápido (75s no 1º contato) e ofereceu desconto estruturado.",
        key_strengths=["Velocidade de resposta", "Negociação transparente de descontos"],
        areas_for_improvement=["Poderia ter convidado para reunião de onboarding"],
    )

    with patch.object(auditor, "_call_llm_evaluation", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = mock_eval

        scorecard: Scorecard = await auditor.evaluate_session(audit_session_with_transcript)

        assert scorecard.first_response_time_seconds == 75.0
        assert scorecard.total_turns == 4
        assert scorecard.clarity_score == 9.5
        assert scorecard.objection_handling_score == 9.0
        assert len(scorecard.key_strengths) == 2
