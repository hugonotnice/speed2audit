from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from speed2audit.agents.scraper import ScrapedContext
from speed2audit.config import GEMINI_API_KEY, GEMINI_MODEL
from speed2audit.core.models import PersonaProfile

PERSONA_SYSTEM_PROMPT = """You are an expert customer intelligence architect for Speed2Audit.
Your mission is to generate a hyper-realistic, qualified prospective buyer persona (mystery shopper) for a business.

The persona MUST:
1. Match the Ideal Customer Profile (ICP) of the target business so they will NOT be disqualified.
2. Have a specific, realistic name, role, and company name (if B2B) or background (if B2C).
3. Have a tangible, concrete pain point or requirement that aligns with the business's offerings.
4. Have a realistic budget range and high urgency to make a decision or get a quote.
5. Incorporate any extra instructions provided by the user.

Return ONLY a structured PersonaProfile.
"""


class PersonaGenerator:
    """Generates a realistic mystery shopper persona based on scraped website context."""

    def __init__(self, api_key: str = GEMINI_API_KEY, model_name: str = GEMINI_MODEL):
        self.api_key = api_key
        self.model_name = model_name

    async def _call_llm_structured(
        self, context: ScrapedContext, extra_instructions: str | None = None
    ) -> PersonaProfile:
        """Call Gemini LLM with structured output binding."""
        llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=self.api_key,
            temperature=0.7,
        )
        structured_llm = llm.with_structured_output(PersonaProfile)

        prompt_content = f"""Target Website URL: {context.url}
Title: {context.title}
Description: {context.meta_description}

Extracted Website Content:
{context.extracted_text}

Extra User Directive/Behavior:
{extra_instructions or 'None. Create a high-intent standard qualified buyer.'}
"""

        messages = [
            SystemMessage(content=PERSONA_SYSTEM_PROMPT),
            HumanMessage(content=prompt_content),
        ]

        result = await structured_llm.ainvoke(messages)
        if isinstance(result, PersonaProfile):
            return result
        elif isinstance(result, dict):
            return PersonaProfile.model_validate(result)
        else:
            raise ValueError(f"Unexpected output type from LLM: {type(result)}")

    async def generate_persona(
        self, context: ScrapedContext, extra_instructions: str | None = None
    ) -> PersonaProfile:
        """Generate and return a qualified buyer persona."""
        profile = await self._call_llm_structured(context, extra_instructions)
        if extra_instructions and not profile.extra_instructions:
            profile.extra_instructions = extra_instructions
        return profile
