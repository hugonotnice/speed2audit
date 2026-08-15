from pathlib import Path

from speed2audit.core.models import AuditSession, MessageRole


def export_session_to_markdown(session: AuditSession, output_dir: str = "reports") -> Path:
    """Generate a comprehensive Markdown report file for an audit session."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    file_name = f"audit_report_{session.session_id}.md"
    target_file = out_path / file_name

    scorecard = session.scorecard
    frt_str = f"{scorecard.first_response_time_seconds:.1f}s" if scorecard else "N/A"
    duration_str = f"{scorecard.total_duration_seconds:.1f}s" if scorecard else "N/A"
    turns_str = str(scorecard.total_turns) if scorecard else str(len(session.turns))

    clarity_str = f"{scorecard.clarity_score:.1f} / 10" if scorecard else "N/A"
    objection_str = f"{scorecard.objection_handling_score:.1f} / 10" if scorecard else "N/A"
    proactivity_str = f"{scorecard.proactivity_score:.1f} / 10" if scorecard else "N/A"

    persona = session.persona
    persona_name = persona.full_name if persona else "N/A"
    persona_role = f"{persona.role} @ {persona.company_name or 'N/A'}" if persona else "N/A"
    persona_pain = persona.core_pain_point if persona else "N/A"
    persona_budget = persona.budget_range or "Sob consulta" if persona else "N/A"

    strengths = (
        "\n".join([f"- ✅ {s}" for s in scorecard.key_strengths])
        if scorecard and scorecard.key_strengths
        else "- N/A"
    )
    improvements = (
        "\n".join([f"- ⚠️ {i}" for i in scorecard.areas_for_improvement])
        if scorecard and scorecard.areas_for_improvement
        else "- N/A"
    )
    summary = scorecard.executive_summary if scorecard else "N/A"

    # Build transcript section
    transcript_lines = []
    for t in session.turns:
        speaker = "Shopper" if t.role == MessageRole.SHOPPER else "Atendente"
        latency = (
            f" *(Latência: {t.latency_seconds_since_last:.1f}s)*"
            if t.latency_seconds_since_last
            else ""
        )
        transcript_lines.append(f"**[{speaker}]**{latency}: {t.content}\n")

    transcript_str = (
        "\n".join(transcript_lines) if transcript_lines else "*(Nenhuma mensagem registrada)*"
    )

    markdown_content = f"""# 📊 Speed2Audit - Relatório de Auditoria
*Gerado em: {session.created_at.strftime("%d/%m/%Y %H:%M:%S UTC")}*
*ID da Sessão: `{session.session_id}`*

---

## 🎯 Dados da Auditoria
- **Empresa / URL:** [{session.website_url}]({session.website_url})
- **WhatsApp Alvo:** `{session.target_phone}`
- **Status Final:** `{session.status.value}`

### 👤 Perfil da Persona (Cliente Oculto)
- **Nome:** {persona_name}
- **Cargo:** {persona_role}
- **Demanda / Dor Principal:** {persona_pain}
- **Orçamento Previsto:** {persona_budget}

---

## 📈 Scorecard & Benchmarks de Performance

| Métrica | Valor | Benchmark / Meta |
| :--- | :--- | :--- |
| ⏱️ **Primeira Resposta (FRT)** | **{frt_str}** | < 120s |
| ⏳ **Duração Total da Sessão** | **{duration_str}** | - |
| 🔄 **Total de Turnos** | **{turns_str}** | < 10 turnos |
| 🎯 **Clareza & Domínio de Produto** | **{clarity_str}** | >= 8.0 |
| 🛡️ **Tratamento de Objeções** | **{objection_str}** | >= 8.0 |
| 🚀 **Proatividade Comercial** | **{proactivity_str}** | >= 8.0 |

---

## 📝 Diagnóstico Executivo
{summary}

### 🌟 Pontos Fortes
{strengths}

### 🔍 Oportunidades de Melhoria
{improvements}

---

## 💬 Transcrição Comentada da Conversa
{transcript_str}

---
*Relatório emitido automaticamente pela plataforma Speed2Audit (AGPLv3).*
"""

    target_file.write_text(markdown_content, encoding="utf-8")
    return target_file
