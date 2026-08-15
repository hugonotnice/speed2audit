from unittest.mock import AsyncMock, patch

import pytest

from speed2audit.agents.shopper import ShopperAgent, ShopperDecision
from speed2audit.core.models import (
    AuditSession,
    AuditStatus,
    PersonaProfile,
)


@pytest.fixture
def sample_session():
    return AuditSession(
        session_id="aud_test_99",
        website_url="https://acmefleet.com",
        target_phone="5511999998888@c.us",
        status=AuditStatus.AUDITING,
        persona=PersonaProfile(
            full_name="Lucas Andrade",
            role="Gerente de Logística",
            company_name="TransLog",
            core_pain_point="Precisa de rastreamento para 40 carretas",
            budget_range="R$ 4.000/mês",
            urgency_level="High",
        ),
    )


@pytest.mark.asyncio
async def test_shopper_agent_first_message(sample_session):
    agent = ShopperAgent()

    with patch.object(agent, "_call_llm", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = ShopperDecision(
            reply_text="Olá! Vocês atendem frotas de caminhões?",
            has_reached_goal=False,
            goal_reason=None,
        )

        decision = await agent.generate_next_message(
            session=sample_session,
            last_seller_message=None,
        )

        assert "Olá" in decision.reply_text
        assert decision.has_reached_goal is False


@pytest.mark.asyncio
async def test_shopper_agent_detects_goal_reached(sample_session):
    agent = ShopperAgent()

    with patch.object(agent, "_call_llm", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = ShopperDecision(
            reply_text="Perfeito, vou avaliar a proposta enviada com a diretoria. Obrigado!",
            has_reached_goal=True,
            goal_reason="Quote / proposal table was provided by seller.",
        )

        decision = await agent.generate_next_message(
            session=sample_session,
            last_seller_message="Aqui está nossa tabela: R$ 89/mês por caminhão com instalação grátis.",
        )

        assert decision.has_reached_goal is True
        assert "Quote" in decision.goal_reason
