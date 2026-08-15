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
from speed2audit.core.report_exporter import export_session_to_markdown


@pytest.fixture
def completed_session():
    now = datetime.now(timezone.utc)
    return AuditSession(
        session_id="aud_export_99",
        website_url="https://acmefleet.com",
        target_phone="+5511999998888",
        status=AuditStatus.COMPLETED_SUCCESS,
        persona=PersonaProfile(
            full_name="Lucas Andrade",
            role="Gerente de Logística",
            company_name="TransLog",
            core_pain_point="Rastreamento para 40 caminhões",
            budget_range="R$ 5.000/mês",
            urgency_level="Alta",
        ),
        turns=[
            ConversationTurn(
                turn_index=1,
                role=MessageRole.SHOPPER,
                content="Olá! Gostaria de um orçamento para rastreamento.",
                timestamp=now,
            ),
            ConversationTurn(
                turn_index=2,
                role=MessageRole.TARGET_SELLER,
                content="Olá Lucas! O valor fica R$ 69 por veículo.",
                timestamp=now,
                latency_seconds_since_last=32.5,
            ),
        ],
        scorecard=Scorecard(
            first_response_time_seconds=32.5,
            total_duration_seconds=32.5,
            total_turns=2,
            clarity_score=9.5,
            objection_handling_score=8.5,
            proactivity_score=9.0,
            executive_summary="Atendimento ágil e objetivo com envio de preço imediato.",
            key_strengths=["Resposta rápida em 32.5s", "Preço claro"],
            areas_for_improvement=["Oferecer agendamento de call"],
        ),
    )


def test_export_session_to_markdown(completed_session, tmp_path):
    output_dir = tmp_path / "reports"
    file_path = export_session_to_markdown(completed_session, output_dir=str(output_dir))

    assert file_path.exists()
    content = file_path.read_text(encoding="utf-8")

    assert "Speed2Audit - Relatório de Auditoria" in content
    assert "Lucas Andrade" in content
    assert "https://acmefleet.com" in content
    assert "32.5s" in content
    assert "9.5 / 10" in content
    assert "Transcrição Comentada" in content
    assert "**[Shopper]**: Olá! Gostaria de um orçamento" in content
    assert "**[Atendente]** *(Latência: 32.5s)*: Olá Lucas! O valor fica" in content
