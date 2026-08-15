import uuid
import chainlit as cl
from speed2audit.agents.auditor import AuditorAgent
from speed2audit.agents.persona import PersonaGenerator
from speed2audit.agents.scraper import ContextScraper, ScrapedContext
from speed2audit.agents.shopper import ShopperAgent, ShopperDecision
from speed2audit.channels.waha import WAHAClient, WAHASessionStatus
from speed2audit.core.database import AuditDatabase
from speed2audit.core.models import (
    AuditSession,
    AuditStatus,
    ConversationTurn,
    MessageRole,
    PersonaProfile,
    Scorecard,
)
from speed2audit.ui.health import HealthChecker

db = AuditDatabase()
waha_client = WAHAClient()
scraper = ContextScraper()
persona_generator = PersonaGenerator()
shopper = ShopperAgent(waha_client=waha_client)
auditor = AuditorAgent()


def format_scorecard_markdown(scorecard: Scorecard) -> str:
    strengths = "\n".join([f"- ✅ {s}" for s in scorecard.key_strengths]) or "- N/A"
    improvements = "\n".join([f"- ⚠️ {i}" for i in scorecard.areas_for_improvement]) or "- N/A"

    return f"""### 📊 Speed2Audit - Relatório de Auditoria

| Métrica | Resultado |
| :--- | :--- |
| ⏱️ **Primeira Resposta (FRT)** | **{scorecard.first_response_time_seconds:.1f}s** |
| ⏳ **Duração Total** | **{scorecard.total_duration_seconds:.1f}s** |
| 🔄 **Total de Turnos** | **{scorecard.total_turns}** |
| 🎯 **Clareza & Domínio** | **{scorecard.clarity_score:.1f} / 10** |
| 🛡️ **Quebra de Objeções** | **{scorecard.objection_handling_score:.1f} / 10** |
| 🚀 **Proatividade Comercial** | **{scorecard.proactivity_score:.1f} / 10** |

---

#### 📝 Diagnóstico Executivo
{scorecard.executive_summary}

---

#### 🌟 Pontos Fortes
{strengths}

---

#### 🔍 Oportunidades de Melhoria
{improvements}
"""


@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("step", "HEALTH_CHECK")
    cl.user_session.set("session_id", str(uuid.uuid4())[:8])

    await cl.Message(
        content="## 🕵️‍♂️ Bem-vindo ao **Speed2Audit Cockpit**\n*Auditoria autônoma de atendimento e vendas no WhatsApp.*"
    ).send()

    # Módulo A: Health Check
    health_checker = HealthChecker(waha_client=waha_client)
    status = await health_checker.run_health_check()

    if not status.gemini_configured:
        await cl.Message(
            content="⚠️ **Atenção:** `GEMINI_API_KEY` não está configurada no arquivo `.env`. Configure a chave para habilitar a inteligência dos agentes."
        ).send()

    if not status.waha_online:
        await cl.Message(
            content="ℹ️ **WhatsApp Gateway (WAHA) offline:** Você pode executar simulações ou iniciar o contêiner WAHA via Docker quando for auditar no WhatsApp real:\n```bash\ndocker run -d --name waha -p 3000:3000 devlikeapro/waha\n```"
        ).send()
    elif status.qr_code_needed:
        await cl.Message(
            content=f"📱 **Conecte o WhatsApp:** Escaneie o QR Code abaixo no seu WhatsApp para autenticar a sessão `{waha_client.session_name}`."
        ).send()
    else:
        await cl.Message(
            content=f"🟢 **Canais Prontos:** WhatsApp conectado ({status.waha_session_status.value}) e Gemini configurado!"
        ).send()

    cl.user_session.set("step", "AWAITING_URL")
    await cl.Message(
        content="👉 **Para iniciar uma auditoria:** Por favor, informe a **URL do site da empresa** que vamos avaliar:"
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    step = cl.user_session.get("step")
    session_id = cl.user_session.get("session_id")
    text = message.content.strip()

    if step == "AWAITING_URL":
        if not text.startswith("http://") and not text.startswith("https://"):
            text = "https://" + text

        cl.user_session.set("website_url", text)
        msg_loading = await cl.Message(content=f"🔍 Analisando o site `{text}` e extraindo catálogo e ICP...").send()

        try:
            context: ScrapedContext = await scraper.scrape_url(text)
            cl.user_session.set("scraped_context", context)

            await msg_loading.update()
            await cl.Message(content=f"✅ Site analisado: **{context.title or text}**\n\n🤖 Gerando Persona ideal de Lead qualificado...").send()

            persona: PersonaProfile = await persona_generator.generate_persona(context)
            cl.user_session.set("persona", persona)

            persona_card = f"""### 👤 Persona Gerada para a Auditoria

- **Nome:** {persona.full_name}
- **Cargo / Empresa:** {persona.role} @ {persona.company_name or 'N/A'}
- **Dor / Demanda Principal:** {persona.core_pain_point}
- **Faixa de Orçamento:** {persona.budget_range or 'Sob consulta'}
- **Nível de Urgência:** {persona.urgency_level}
"""
            await cl.Message(content=persona_card).send()

            res = await cl.AskActionMessage(
                content="Deseja aprovar esta persona ou fazer ajustes?",
                actions=[
                    cl.Action(name="approve_persona", payload={"value": "approve"}, label="✅ Aprovar Persona"),
                    cl.Action(name="edit_persona", payload={"value": "edit"}, label="✏️ Ajustar Instruções"),
                ],
            ).send()

            if res and res.get("payload", {}).get("value") == "edit":
                cl.user_session.set("step", "AWAITING_PERSONA_EDIT")
                await cl.Message(content="✍️ Digite quais ajustes ou instruções extras você quer incluir para este Lead:").send()
            else:
                cl.user_session.set("step", "AWAITING_PHONE")
                await cl.Message(content="📱 Informe o **número de WhatsApp do alvo** a ser auditado (com DDI e DDD, ex: `+55 11 99999-8888`):").send()

        except Exception as e:
            await cl.Message(content=f"❌ Erro ao analisar o site: `{str(e)}`. Por favor, verifique a URL e tente novamente.").send()

    elif step == "AWAITING_PERSONA_EDIT":
        persona: PersonaProfile = cl.user_session.get("persona")
        persona.extra_instructions = text
        cl.user_session.set("persona", persona)

        await cl.Message(content=f"✅ Instruções atualizadas: *\"{text}\"*").send()
        cl.user_session.set("step", "AWAITING_PHONE")
        await cl.Message(content="📱 Agora informe o **número de WhatsApp do alvo** a ser auditado (ex: `+55 11 99999-8888`):").send()

    elif step == "AWAITING_PHONE":
        clean_phone = "".join(c for c in text if c.isdigit())
        if not clean_phone.endswith("@c.us"):
            target_jid = f"{clean_phone}@c.us"
        else:
            target_jid = clean_phone

        website_url = cl.user_session.get("website_url")
        persona = cl.user_session.get("persona")

        audit_session = AuditSession(
            session_id=session_id,
            website_url=website_url,
            target_phone=target_jid,
            persona=persona,
            status=AuditStatus.AUDITING,
        )
        cl.user_session.set("audit_session", audit_session)
        cl.user_session.set("step", "AUDITING")

        await cl.Message(
            content=f"🚀 **Iniciando Auditoria com {persona.full_name}!**\nEnviando primeira abordagem para `{target_jid}`..."
        ).send()

        # Generate first message
        decision: ShopperDecision = await shopper.generate_next_message(audit_session)
        turn = await shopper.dispatch_with_humanization(audit_session, decision, skip_delay=True)
        audit_session.turns.append(turn)
        db.save_session(audit_session)

        await cl.Message(
            content=f"💬 **[Shopper ({persona.full_name}) ➔ Alvo]:**\n> {decision.reply_text}"
        ).send()

        await cl.Message(
            content="ℹ️ *O Shopper está aguardando respostas. Você pode digitar mensagens aqui a qualquer momento para intervir e direcionar a conversa.*"
        ).send()

    elif step == "AUDITING":
        # User intervention during live chat
        audit_session: AuditSession = cl.user_session.get("audit_session")
        if audit_session and audit_session.persona:
            audit_session.persona.extra_instructions = (
                f"{audit_session.persona.extra_instructions or ''} [Intervenção ao vivo: {text}]".strip()
            )
            await cl.Message(content=f"🧭 **Diretriz injetada no Shopper:** \"{text}\"").send()
