from unittest.mock import AsyncMock, patch

import pytest

from speed2audit.agents.persona import PersonaGenerator
from speed2audit.agents.scraper import ScrapedContext
from speed2audit.core.models import PersonaProfile


@pytest.mark.asyncio
async def test_persona_generator_creates_profile():
    scraped = ScrapedContext(
        url="https://acmefleet.com",
        title="Acme Fleet Tracking Software",
        meta_description="Real-time GPS tracking and route optimization for logistics companies.",
        extracted_text="Our SaaS platform helps logistics managers reduce fuel costs by 20% and track over 500+ vehicles simultaneously.",
    )

    mock_profile = PersonaProfile(
        full_name="Lucas Andrade",
        company_name="TransLog Express",
        role="Gerente de Logística e Frotas",
        core_pain_point="Precisa monitorar 40 caminhões e diminuir custos com combustível",
        budget_range="R$ 3.000 a R$ 6.000/mês",
        urgency_level="High",
        extra_instructions="Pedir tabela de preços e perguntar sobre prazo de instalação.",
    )

    generator = PersonaGenerator()

    with patch.object(generator, "_call_llm_structured", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = mock_profile

        profile = await generator.generate_persona(
            context=scraped,
            extra_instructions="Pedir tabela de preços e perguntar sobre prazo de instalação.",
        )

        assert profile.full_name == "Lucas Andrade"
        assert profile.role == "Gerente de Logística e Frotas"
        assert "40 caminhões" in profile.core_pain_point
        assert profile.extra_instructions is not None
