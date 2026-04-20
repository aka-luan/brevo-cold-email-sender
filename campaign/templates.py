"""Templates de email frio para campanhas ProspectaAí."""

from __future__ import annotations

import html
import os
import re
from typing import Any


UNSUBSCRIBE_FOOTER = "Para não receber mais emails: responda com REMOVER."

TEMPLATES: dict[str, dict[str, str]] = {
    "comercio": {
        "subject": "Fiz um rascunho de site pro negócio de vocês",
        "body": (
            "Olá, tudo bem?\n\n"
            "Conheci o trabalho de vocês e achei muito bacana. Como sou desenvolvedor, tomei a liberdade de montar um protótipo de site focado em vendas, com carregamento rápido, botão para WhatsApp e estrutura otimizada para o Google.\n\n"
            "Fiz isso sem compromisso, apenas como um estudo de design aplicado ao negócio de vocês. Se fizer sentido, posso mandar o link para verem como ficou.\n\n"
            "{sender_name}\n"
            "Site: {sender_website}\n"
            "WhatsApp: {sender_whatsapp}"
        ),
    },
    "restaurante": {
        "subject": "Ideia de cardápio digital/site pra vocês",
        "body": (
            "Oi, tudo bem?\n\n"
            "Gosto muito do espaço de vocês. Tomei a liberdade de desenhar um modelo de site com cardápio online, focado em facilitar pedidos no delivery e no WhatsApp, com um visual mais moderno.\n\n"
            "Fiz isso sem compromisso, só para mostrar como a marca de vocês poderia ficar na web. Posso enviar o link para darem uma olhada?\n\n"
            "{sender_name}\n"
            "Site: {sender_website}\n"
            "WhatsApp: {sender_whatsapp}"
        ),
    },
    "imovel": {
        "subject": "Projeto de site de alto padrão para os imóveis",
        "body": (
            "Olá, tudo bem?\n\n"
            "Tenho acompanhado os empreendimentos de vocês. Como trabalho com sites de alta performance, montei um protótipo pensado para o mercado imobiliário, com visual premium e galerias de fotos que carregam rápido.\n\n"
            "Criei isso sem compromisso, apenas para ilustrar uma possibilidade de apresentação digital para a marca de vocês. Se quiserem, posso mandar o link para verem como ficou.\n\n"
            "{sender_name}\n"
            "Site: {sender_website}\n"
            "WhatsApp: {sender_whatsapp}"
        ),
    },
    "arquitetura": {
        "subject": "Fiz um portfólio digital pro escritório",
        "body": (
            "Oi, tudo bem?\n\n"
            "Acho os projetos do escritório excelentes. Para valorizar ainda mais os trabalhos, montei um protótipo de portfólio online com visual minimalista e animações fluidas.\n\n"
            "Fiz isso de forma totalmente especulativa e sem compromisso. Posso mandar o link para vocês avaliarem o visual?\n\n"
            "{sender_name}\n"
            "Site: {sender_website}\n"
            "WhatsApp: {sender_whatsapp}"
        ),
    },
    "saude": {
        "subject": "Ideia de site profissional para a clínica",
        "body": (
            "Olá, tudo bem?\n\n"
            "Acompanho o trabalho da clínica de vocês. Tomei a iniciativa de desenhar um site focado em transmitir mais credibilidade e facilitar o agendamento de consultas pelo WhatsApp.\n\n"
            "É um modelo que fiz sem compromisso, apenas para mostrar uma estrutura possível. Posso compartilhar o link com vocês?\n\n"
            "{sender_name}\n"
            "Site: {sender_website}\n"
            "WhatsApp: {sender_whatsapp}"
        ),
    },
    "agencia": {
        "subject": "Protótipo de site de alta performance",
        "body": (
            "Oi, tudo bem?\n\n"
            "Acompanho o trabalho da agência e gosto muito do posicionamento de vocês. Como sou desenvolvedor front-end, montei um modelo de portfólio com código moderno, animações avançadas e foco em performance.\n\n"
            "Fiz isso sem compromisso, só para trocar uma ideia. Posso mandar o link para vocês darem uma olhada?\n\n"
            "{sender_name}\n"
            "Site: {sender_website}\n"
            "WhatsApp: {sender_whatsapp}"
        ),
    },
    "consultoria": {
        "subject": "Nova estrutura de site para a consultoria",
        "body": (
            "Olá, tudo bem?\n\n"
            "Achei o escopo dos serviços de vocês muito interessante. Construí um rascunho de site focado em conversão B2B, ideal para destacar a metodologia e os cases de sucesso com um visual mais premium.\n\n"
            "Foi feito sem compromisso, como um estudo. Querem que eu envie o link para visualizarem?\n\n"
            "{sender_name}\n"
            "Site: {sender_website}\n"
            "WhatsApp: {sender_whatsapp}"
        ),
    },
}


def get_template(nicho: str) -> dict[str, str]:
    """Retorna o template mais adequado para o nicho informado."""
    normalized = (nicho or "").strip().lower()

    if any(keyword in normalized for keyword in ("incorporadora", "construtora", "imobiliária", "imobiliario")):
        return TEMPLATES["imovel"]

    if any(keyword in normalized for keyword in ("arquitetura", "arquiteto", "engenharia civil", "engenheiro")):
        return TEMPLATES["arquitetura"]

    if any(
        keyword in normalized
        for keyword in (
            "clínica médica",
            "clínica de estética",
            "odontologia",
            "odonto",
            "harmonização facial",
            "harmonização",
            "cirurgião plástico",
            "cirurgião",
            "dermatologista",
            "dermatologia",
            "dentista",
            "psicolog",
            "fisio",
        )
    ):
        return TEMPLATES["saude"]

    if any(keyword in normalized for keyword in ("agência", "agencia", "marketing", "publicidade", "assessoria de imprensa")):
        return TEMPLATES["agencia"]

    if any(keyword in normalized for keyword in ("consultoria", "consultor", "consultoria empresarial")):
        return TEMPLATES["consultoria"]

    if any(keyword in normalized for keyword in ("restaurante", "bar", "lanchonete")):
        return TEMPLATES["restaurante"]

    return TEMPLATES["comercio"]


def render_template(template: dict[str, str], lead: dict[str, Any]) -> dict[str, str]:
    """Renderiza um template substituindo as variáveis com os dados do lead e do sender."""
    payload = {
        "nome": lead.get("nome") or "empresa",
        "nicho": lead.get("nicho") or "seu negócio",
        "fonte": lead.get("fonte") or "uma listagem online",
        "sender_name": lead.get("sender_name") or os.getenv("SENDER_NAME", ""),
        "sender_whatsapp": lead.get("sender_whatsapp") or os.getenv("SENDER_WHATSAPP", ""),
        "sender_website": lead.get("sender_website") or os.getenv("SENDER_WEBSITE", ""),
    }
    body = template["body"].format(**payload)
    return {
        "subject": template["subject"].format(**payload),
        "body": body,
        "html_body": _render_html_email(body, payload),
    }


def _normalize_url(url: str) -> str:
    normalized = url.strip()
    if not normalized:
        return ""
    if normalized.startswith(("http://", "https://")):
        return normalized
    return f"https://{normalized}"


def _extract_digits(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def _build_whatsapp_url(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        return ""
    if normalized.startswith(("http://", "https://")):
        return normalized

    digits = _extract_digits(normalized)
    if not digits:
        return ""
    return f"https://wa.me/{digits}"


def _render_signature_html(payload: dict[str, str]) -> str:
    signature_lines = [f"<strong>{html.escape(payload['sender_name'])}</strong>"]

    website = payload.get("sender_website", "").strip()
    if website:
        website_href = _normalize_url(website)
        signature_lines.append(
            f'Site: <a href="{html.escape(website_href)}">{html.escape(website)}</a>'
        )

    whatsapp = payload.get("sender_whatsapp", "").strip()
    if whatsapp:
        whatsapp_href = _build_whatsapp_url(whatsapp)
        whatsapp_label = html.escape(whatsapp)
        if whatsapp_href:
            signature_lines.append(
                f'WhatsApp: <a href="{html.escape(whatsapp_href)}">{whatsapp_label}</a>'
            )
        else:
            signature_lines.append(f"WhatsApp: {whatsapp_label}")

    return "<br>".join(signature_lines)


def _render_html_email(body: str, payload: dict[str, str]) -> str:
    paragraphs = [part.strip() for part in body.split("\n\n") if part.strip()]
    content_paragraphs = paragraphs[:-1]
    html_parts = [
        (
            "<div style=\"font-family: Arial, sans-serif; font-size: 16px; "
            "line-height: 1.6; color: #1f2937;\">"
        )
    ]

    for paragraph in content_paragraphs:
        html_parts.append(f"<p>{html.escape(paragraph)}</p>")

    html_parts.append(f"<p>{_render_signature_html(payload)}</p>")
    html_parts.append("</div>")
    return "".join(html_parts)
