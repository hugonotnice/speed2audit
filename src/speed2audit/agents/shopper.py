import asyncio
import random
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from speed2audit.channels.waha import WAHAClient
from speed2audit.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    MAX_HUMAN_DELAY_SECONDS,
    MIN_HUMAN_DELAY_SECONDS,
)
from speed2audit.core.models import AuditSession, ConversationTurn, MessageRole

SHOPPER_SYSTEM_PROMPT = """You are the Shopper Agent in the Speed2Audit platform.
You are playing the role of a realistic prospective buyer (mystery shopper) on WhatsApp.

Your objectives:
1. Stay strictly in character according to your assigned Persona Profile.
2. Communicate naturally, conversationally, and concisely as humans do on WhatsApp (avoid overly formal essay-length messages).
3. Push forward towards achieving the goal: getting a clear price quote/table, understanding conditions, or booking a demo/meeting.
4. Raise realistic objections if appropriate (e.g. price, implementation timeframe, competitor comparison) based on your persona.
5. Determine if the goal has been accomplished (e.g., received explicit pricing, checkout link, or scheduled meeting link).

Return a structured ShopperDecision.
"""


class ShopperDecision(BaseModel):
    reply_text: str = Field(description="The WhatsApp message to send as the shopper.")
    has_reached_goal: bool = Field(
        description="True if the seller provided a quote, pricing, checkout link, or scheduled a meeting."
    )
    goal_reason: str | None = Field(
        default=None,
        description="Explanation if goal was reached, or None.",
    )


class ShopperAgent:
    """Mystery Shopper Agent conducting the live sales conversation."""

    def __init__(
        self,
        api_key: str = GEMINI_API_KEY,
        model_name: str = GEMINI_MODEL,
        waha_client: WAHAClient | None = None,
    ):
        self.api_key = api_key
        self.model_name = model_name
        self.waha = waha_client

    async def _call_llm(
        self, session: AuditSession, last_seller_message: str | None
    ) -> ShopperDecision:
        """Call Gemini LLM to generate the next response in persona character."""
        llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=self.api_key,
            temperature=0.7,
        )
        structured_llm = llm.with_structured_output(ShopperDecision)

        persona_info = session.persona.model_dump_json(indent=2) if session.persona else "{}"

        # Format conversation history
        history_lines = []
        for t in session.turns:
            speaker = "Shopper (You)" if t.role == MessageRole.SHOPPER else "Seller (Target)"
            history_lines.append(f"[{speaker}]: {t.content}")

        history_str = "\n".join(history_lines) if history_lines else "(No previous turns yet - initiate the conversation)"

        prompt_content = f"""Assigned Persona Profile:
{persona_info}

Target Website: {session.website_url}
Target WhatsApp: {session.target_phone}

Conversation History:
{history_str}

Latest Seller Message:
{last_seller_message or '(Starting conversation now)'}
"""

        messages = [
            SystemMessage(content=SHOPPER_SYSTEM_PROMPT),
            HumanMessage(content=prompt_content),
        ]

        result = await structured_llm.ainvoke(messages)
        if isinstance(result, ShopperDecision):
            return result
        elif isinstance(result, dict):
            return ShopperDecision.model_validate(result)
        else:
            raise ValueError(f"Unexpected output type from LLM: {type(result)}")

    async def generate_next_message(
        self, session: AuditSession, last_seller_message: str | None = None
    ) -> ShopperDecision:
        """Generate next conversational turn."""
        return await self._call_llm(session, last_seller_message)

    async def dispatch_with_humanization(
        self,
        session: AuditSession,
        decision: ShopperDecision,
        skip_delay: bool = False,
    ) -> ConversationTurn:
        """Apply random 15-40s delay, typing simulation, and dispatch message via WAHA."""
        if not skip_delay:
            delay = random.uniform(MIN_HUMAN_DELAY_SECONDS, MAX_HUMAN_DELAY_SECONDS)
            # Wait part of delay, then show typing
            typing_start = max(0.0, delay - 5.0)
            await asyncio.sleep(typing_start)

            if self.waha:
                await self.waha.start_typing(session.target_phone)
                await asyncio.sleep(min(5.0, delay))
                await self.waha.stop_typing(session.target_phone)
            else:
                await asyncio.sleep(min(5.0, delay))

        # Send message
        if self.waha:
            await self.waha.send_text(session.target_phone, decision.reply_text)

        turn = ConversationTurn(
            turn_index=len(session.turns) + 1,
            role=MessageRole.SHOPPER,
            content=decision.reply_text,
        )
        return turn
