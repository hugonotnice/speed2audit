from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from speed2audit.config import GEMINI_API_KEY, GEMINI_MODEL
from speed2audit.core.models import (
    AuditSession,
    MessageRole,
    Scorecard,
)

AUDITOR_SYSTEM_PROMPT = """You are the Senior Customer Service & Sales Auditor in Speed2Audit.
Your job is to objectively evaluate a recorded WhatsApp sales conversation conducted by our mystery shopper.

You must grade the seller on:
1. Clarity & Product Knowledge (0-10): Did they explain the offering clearly, accurately, and without ambiguity?
2. Objection Handling & Negotiation (0-10): How well did they handle pricing, competitor comparisons, or timeline friction?
3. Commercial Proactivity & Velocity (0-10): Did they drive the sale forward, offer demos, schedule meetings, or send pricing promptly?

Provide an executive summary, list top strengths, and list actionable areas for improvement.
Return ONLY a structured AuditEvaluation.
"""


class AuditEvaluation(BaseModel):
    clarity_score: float = Field(
        ge=0, le=10, description="Clarity and product knowledge score (0 to 10)"
    )
    objection_handling_score: float = Field(
        ge=0, le=10, description="Objection handling score (0 to 10)"
    )
    proactivity_score: float = Field(
        ge=0, le=10, description="Commercial proactivity score (0 to 10)"
    )
    executive_summary: str = Field(description="High-level diagnostic summary of the interaction.")
    key_strengths: list[str] = Field(default_factory=list, description="Top positive highlights.")
    areas_for_improvement: list[str] = Field(
        default_factory=list, description="Actionable points to improve."
    )


class AuditorAgent:
    """Evaluates full conversation transcripts and generates audit scorecards."""

    def __init__(self, api_key: str = GEMINI_API_KEY, model_name: str = GEMINI_MODEL):
        self.api_key = api_key
        self.model_name = model_name

    async def _call_llm_evaluation(self, session: AuditSession) -> AuditEvaluation:
        """Call Gemini LLM to analyze the full audit transcript."""
        llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=self.api_key,
            temperature=0.2,
        )
        structured_llm = llm.with_structured_output(AuditEvaluation)

        persona_info = session.persona.model_dump_json(indent=2) if session.persona else "N/A"

        transcript_lines = []
        for t in session.turns:
            speaker = "Mystery Shopper" if t.role == MessageRole.SHOPPER else "Sales Attendant"
            latency_info = (
                f" (latency: {t.latency_seconds_since_last:.1f}s)"
                if t.latency_seconds_since_last
                else ""
            )
            transcript_lines.append(
                f"[{speaker} @ {t.timestamp.isoformat()}]{latency_info}: {t.content}"
            )

        transcript_str = "\n".join(transcript_lines)

        prompt_content = f"""Target Company URL: {session.website_url}
Target Phone: {session.target_phone}

Assigned Mystery Shopper Persona:
{persona_info}

Full Conversation Transcript:
{transcript_str}
"""

        messages = [
            SystemMessage(content=AUDITOR_SYSTEM_PROMPT),
            HumanMessage(content=prompt_content),
        ]

        result = await structured_llm.ainvoke(messages)
        if isinstance(result, AuditEvaluation):
            return result
        elif isinstance(result, dict):
            return AuditEvaluation.model_validate(result)
        else:
            raise ValueError(f"Unexpected output type from LLM: {type(result)}")

    async def evaluate_session(self, session: AuditSession) -> Scorecard:
        """Compute latency telemetry, total turns, and generate final Scorecard."""
        first_response_time = 0.0
        total_duration = 0.0
        turns = session.turns

        # Calculate FRT (latency between turn 1 and first seller response)
        first_seller_turn = next((t for t in turns if t.role == MessageRole.TARGET_SELLER), None)
        if first_seller_turn and turns:
            first_shopper_turn = turns[0]
            first_response_time = max(
                0.0,
                (first_seller_turn.timestamp - first_shopper_turn.timestamp).total_seconds(),
            )

        # Calculate total duration
        if len(turns) >= 2:
            total_duration = max(
                0.0,
                (turns[-1].timestamp - turns[0].timestamp).total_seconds(),
            )

        # Get LLM evaluation scores
        eval_result = await self._call_llm_evaluation(session)

        scorecard = Scorecard(
            first_response_time_seconds=first_response_time,
            total_duration_seconds=total_duration,
            total_turns=len(turns),
            clarity_score=eval_result.clarity_score,
            objection_handling_score=eval_result.objection_handling_score,
            proactivity_score=eval_result.proactivity_score,
            executive_summary=eval_result.executive_summary,
            key_strengths=eval_result.key_strengths,
            areas_for_improvement=eval_result.areas_for_improvement,
        )
        return scorecard
