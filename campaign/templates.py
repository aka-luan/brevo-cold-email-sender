"""Templates de email frio para campanhas ProspectaAí."""

from __future__ import annotations

import os
from typing import Any


UNSUBSCRIBE_FOOTER = "Para não receber mais emails: responda com REMOVER."

TEMPLATES: dict[str, dict[str, str]] = {
    "comercio": {
        "subject": "Fiz um rascunho de site pro negócio de vocês",
        "body": (
            "Olá, tudo bem?\n\n"
            "Conheci o trabalho de vocês e achei muito bacana. Como sou desenvolvedor, tomei a liberdade de montar um protótipo de site focado em vendas (com carregamento rápido, botão pro WhatsApp e otimizado pro Google).\n\n"
            "Fiz sem compromisso nenhum, apenas como um estudo de design. Posso mandar o link pra vocês verem como ficou?\n\n"
            "{sender_name}\n"
            "{sender_website}\n"
            "{sender_whatsapp}"
        ),
    },
    "restaurante": {
        "subject": "Ideia de cardápio digital/site pra vocês",
        "body": (
            "Oi, tudo bem?\n\n"
            "Gosto muito do espaço de vocês. Tomei a liberdade de desenhar um modelo de site com cardápio online, focado em facilitar pedidos pro delivery e WhatsApp. Tudo com um design bem moderno.\n\n"
            "Fiz sem compromisso, só pra mostrar como a marca ficaria na web. Posso enviar o link pra vocês darem uma olhada?\n\n"
            "{sender_name}\n"
            "{sender_website}\n"
            "{sender_whatsapp}"
        ),
    },
    "imovel": {
        "subject": "Projeto de site de alto padrão para os imóveis",
        "body": (
            "Olá, tudo bem?\n\n"
            "Tenho acompanhado os empreendimentos de vocês. Como trabalho com sites de alta performance, fiz um protótipo focado no mercado imobiliário: design premium e galerias de fotos que carregam super rápido.\n\n"
            "Criei sem compromisso nenhum, apenas para ilustrar. Querem que eu mande o link pra vocês verem?\n\n"
            "{sender_name}\n"
            "{sender_website}\n"
            "{sender_whatsapp}"
        ),
    },
    "arquitetura": {
        "subject": "Fiz um portfólio digital pro escritório",
        "body": (
            "Oi, tudo bem?\n\n"
            "Acho os projetos do escritório excelentes. Para valorizar ainda mais os trabalhos, montei um protótipo de portfólio online com um design bem minimalista e animações fluidas.\n\n"
            "Fiz de forma totalmente especulativa e sem compromisso. Posso mandar o link para vocês avaliarem o visual?\n\n"
            "{sender_name}\n"
            "{sender_website}\n"
            "{sender_whatsapp}"
        ),
    },
    "saude": {
        "subject": "Ideia de site profissional para a clínica",
        "body": (
            "Olá, tudo bem?\n\n"
            "Acompanho o trabalho da clínica de vocês. Tomei a iniciativa de desenhar um site focado em passar mais credibilidade e facilitar o agendamento de consultas pelo WhatsApp.\n\n"
            "É um modelo que fiz sem compromisso, apenas pra mostrar a estrutura. Posso compartilhar o link com vocês?\n\n"
            "{sender_name}\n"
            "{sender_website}\n"
            "{sender_whatsapp}"
        ),
    },
    "agencia": {
        "subject": "Protótipo de site de alta performance",
        "body": (
            "Oi, tudo bem?\n\n"
            "Acompanho o trabalho da agência e gosto muito do posicionamento de vocês. Como sou desenvolvedor front-end, montei um modelo de portfólio com código moderno, animações avançadas e foco em performance.\n\n"
            "Fiz sem compromisso nenhum, só para trocar uma ideia. Posso mandar o link pra vocês darem uma olhada?\n\n"
            "{sender_name}\n"
            "{sender_website}\n"
            "{sender_whatsapp}"
        ),
    },
    "consultoria": {
        "subject": "Nova estrutura de site para a consultoria",
        "body": (
            "Olá, tudo bem?\n\n"
            "Achei o escopo dos serviços de vocês muito interessante. Construí um rascunho de site focado em conversão B2B, ideal para destacar a metodologia e os cases de sucesso com um design mais premium.\n\n"
            "Foi feito sem compromisso, como um estudo. Querem que eu envie o link para visualizarem?\n\n"
            "{sender_name}\n"
            "{sender_website}\n"
            "{sender_whatsapp}"
        ),
    },
}


def get_template(nicho: str) -> dict[str, str]:
    """Retorna o template mais adequado para o nicho informado."""
    normalized = (nicho or "").strip().lower()

    # Imóvel: incorporadora, construtora, imobiliária
    if any(keyword in normalized for keyword in ("incorporadora", "construtora", "imobiliária", "imobiliario")):
        return TEMPLATES["imovel"]

    # Arquitetura & Engenharia: arquitetura, escritório de arquitetura, engenharia civil
    if any(keyword in normalized for keyword in ("arquitetura", "arquiteto", "engenharia civil", "engenheiro")):
        return TEMPLATES["arquitetura"]

    # Saúde: clínica médica, clínica de estética, odontologia, harmonização facial, cirurgião, dermatologista
    if any(
        keyword in normalized
        for keyword in (
            "clínica médica", "clínica de estética", "odontologia", "odonto",
            "harmonização facial", "harmonização", "cirurgião plástico", "cirurgião",
            "dermatologista", "dermatologia", "dentista", "psicolog", "fisio"
        )
    ):
        return TEMPLATES["saude"]

    # Agência: marketing, publicidade, assessoria de imprensa
    if any(keyword in normalized for keyword in ("agência", "agencia", "marketing", "publicidade", "assessoria de imprensa")):
        return TEMPLATES["agencia"]

    # Consultoria
    if any(keyword in normalized for keyword in ("consultoria", "consultor", "consultoria empresarial")):
        return TEMPLATES["consultoria"]

    # Restaurante
    if any(keyword in normalized for keyword in ("restaurante", "bar", "lanchonete")):
        return TEMPLATES["restaurante"]

    # Default
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
    return {
        "subject": template["subject"].format(**payload),
        "body": template["body"].format(**payload),
    }