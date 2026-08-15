import pytest
from unittest.mock import AsyncMock, patch
from speed2audit.agents.auditor import AuditEvaluation
from speed2audit.agents.persona import PersonaGenerator
from speed2audit.agents.scraper import ScrapedContext
from speed2audit.agents.shopper import ShopperDecision
from speed2audit.core.models import (
    AuditSession,
    AuditStatus,
    ConversationTurn,
    MessageRole,
    PersonaProfile,
)
from speed2audit.graph import AuditState, create_audit_graph


@pytest.mark.asyncio
async def test_audit_graph_execution_flow():
    graph = create_audit_graph()

    initial_state: AuditState = {
        "session_id": "test_graph_01",
        "website_url": "https://acmefleet.com",
        "target_phone": "5511999998888@c.us",
        "extra_instructions": "Ask for demo",
        "scraped_context": None,
        "persona": None,
        "turns": [],
        "scorecard": None,
        "status": AuditStatus.INITIALIZING,
        "last_seller_message": None,
        "stop_reason": None,
    }

    mock_scraped = ScrapedContext(
        url="https://acmefleet.com",
        title="Acme Fleet",
        meta_description="Fleet tracking",
        extracted_text="We offer GPS tracking for vehicles.",
    )

    mock_persona = PersonaProfile(
        full_name="Lucas Andrade",
        role="Gerente de Logística",
        core_pain_point="Precisa de GPS para 40 carretas",
    )

    mock_decision = ShopperDecision(
        reply_text="Olá, vocês fazem rastreamento de frotas?",
        has_reached_goal=False,
    )

    with patch("speed2audit.graph.ContextScraper.scrape_url", new_callable=AsyncMock) as mock_scrape, \
         patch("speed2audit.graph.PersonaGenerator.generate_persona", new_callable=AsyncMock) as mock_gen_p, \
         patch("speed2audit.graph.ShopperAgent.generate_next_message", new_callable=AsyncMock) as mock_shop:

        mock_scrape.return_value = mock_scraped
        mock_gen_p.return_value = mock_persona
        mock_shop.return_value = mock_decision

        # Run scraper node
        state_after_scrape = await graph.nodes["scrape_node"].ainvoke(initial_state)
        assert state_after_scrape["scraped_context"].title == "Acme Fleet"

        # Run persona node
        state_after_persona = await graph.nodes["persona_node"].ainvoke({**initial_state, **state_after_scrape})
        assert state_after_persona["persona"].full_name == "Lucas Andrade"
