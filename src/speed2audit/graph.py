from typing import NotRequired, TypedDict
from langgraph.graph import END, StateGraph
from speed2audit.agents.auditor import AuditorAgent
from speed2audit.agents.persona import PersonaGenerator
from speed2audit.agents.scraper import ContextScraper, ScrapedContext
from speed2audit.agents.shopper import ShopperAgent, ShopperDecision
from speed2audit.channels.waha import WAHAClient
from speed2audit.config import (
    ABANDONMENT_TIMEOUT_MINUTES,
    MAX_CONVERSATION_TURNS,
)
from speed2audit.core.models import (
    AuditSession,
    AuditStatus,
    ConversationTurn,
    MessageRole,
    PersonaProfile,
    Scorecard,
)


class AuditState(TypedDict):
    website_url: str
    target_phone: NotRequired[str]
    session_id: NotRequired[str]
    extra_instructions: NotRequired[str | None]
    scraped_context: NotRequired[ScrapedContext | None]
    persona: NotRequired[PersonaProfile | None]
    turns: NotRequired[list[ConversationTurn]]
    scorecard: NotRequired[Scorecard | None]
    status: NotRequired[AuditStatus]
    last_seller_message: NotRequired[str | None]
    stop_reason: NotRequired[str | None]


async def scrape_node(state: AuditState) -> dict:
    """Node 1: Extract company offerings and ICP context from website."""
    scraper = ContextScraper()
    context = await scraper.scrape_url(state["website_url"])
    return {
        "scraped_context": context,
        "status": AuditStatus.SCRAPING,
    }


async def persona_node(state: AuditState) -> dict:
    """Node 2: Generate realistic buyer persona matching ICP."""
    if not state.get("scraped_context"):
        raise ValueError("Cannot generate persona without scraped context.")
    generator = PersonaGenerator()
    persona = await generator.generate_persona(
        context=state["scraped_context"],
        extra_instructions=state.get("extra_instructions"),
    )
    return {
        "persona": persona,
        "status": AuditStatus.PERSONA_REVIEW,
    }


async def shopper_node(state: AuditState) -> dict:
    """Node 3: Execute next dialogue turn as the shopper."""
    shopper = ShopperAgent()
    temp_session = AuditSession(
        session_id=state.get("session_id") or "studio_demo",
        website_url=state["website_url"],
        target_phone=state.get("target_phone") or "5511999999999@c.us",
        persona=state.get("persona"),
        turns=state.get("turns") or [],
        status=AuditStatus.AUDITING,
    )
    decision: ShopperDecision = await shopper.generate_next_message(
        session=temp_session,
        last_seller_message=state.get("last_seller_message"),
    )

    new_turns = list(state.get("turns") or [])
    turn = ConversationTurn(
        turn_index=len(new_turns) + 1,
        role=MessageRole.SHOPPER,
        content=decision.reply_text,
    )
    new_turns.append(turn)

    stop_reason = None
    if decision.has_reached_goal:
        stop_reason = f"Goal reached: {decision.goal_reason or 'Quote/Meeting received'}"
    elif len(new_turns) >= MAX_CONVERSATION_TURNS:
        stop_reason = f"Safety turn limit reached ({MAX_CONVERSATION_TURNS} turns)"

    return {
        "turns": new_turns,
        "stop_reason": stop_reason,
        "status": AuditStatus.AUDITING,
    }


async def auditor_node(state: AuditState) -> dict:
    """Node 4: Analyze full transcript and compute final Scorecard."""
    auditor = AuditorAgent()
    temp_session = AuditSession(
        session_id=state.get("session_id") or "studio_demo",
        website_url=state["website_url"],
        target_phone=state.get("target_phone") or "5511999999999@c.us",
        persona=state.get("persona"),
        turns=state.get("turns") or [],
        status=AuditStatus.COMPLETED_SUCCESS if not state.get("stop_reason") or "limit" not in state.get("stop_reason", "").lower() else AuditStatus.COMPLETED_LIMIT_REACHED,
    )
    scorecard: Scorecard = await auditor.evaluate_session(temp_session)
    return {
        "scorecard": scorecard,
        "status": temp_session.status,
    }


def create_audit_graph() -> StateGraph:
    """Assemble the 4-agent LangGraph topology."""
    workflow = StateGraph(AuditState)

    workflow.add_node("scrape_node", scrape_node)
    workflow.add_node("persona_node", persona_node)
    workflow.add_node("shopper_node", shopper_node)
    workflow.add_node("auditor_node", auditor_node)

    workflow.set_entry_point("scrape_node")
    workflow.add_edge("scrape_node", "persona_node")

    return workflow.compile()
