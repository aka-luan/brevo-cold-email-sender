"""Templates de email frio para campanhas ProspectaAí."""

from __future__ import annotations

import os
from typing import Any


UNSUBSCRIBE_FOOTER = "Para não receber mais emails: responda com REMOVER."

TEMPLATES: dict[str, dict[str, str]] = {
    "comercio": {
        "subject": "{nome} — vi que vocês ainda não têm site próprio",
        "body": (
            "Oi, tudo bem?\n\n"
            "Encontrei a {nome} no {fonte} procurando por {nicho} na região.\n"
            "Vi que vocês têm boa presença, mas não encontrei um site próprio — "
            "o que provavelmente está te custando clientes que pesquisam no Google antes de comprar.\n\n"
            "Crio sites para negócios como o seu: simples, rápidos e feitos para aparecer nas buscas locais. "
            "Entrego em até 10 dias, com domínio e hospedagem inclusos no primeiro ano.\n\n"
            "Posso te mandar 2 ou 3 exemplos do que já fiz?\n\n"
            "Abraço,\n"
            "{sender_name}\n"
            "{sender_whatsapp}\n"
            "{sender_website}\n\n"
            f"{UNSUBSCRIBE_FOOTER}"
        ),
    },
    "profissional": {
        "subject": "Clientes buscam {nicho} no Google — {nome} aparece?",
        "body": (
            "Olá, {nome}.\n\n"
            "Pesquisei por {nicho} no {fonte} e o você apareceu — ótimo sinal.\n"
            "Mas notei que não tem um site próprio ainda, só perfil em diretório. "
            "Isso significa que quando alguém pesquisa diretamente seu nome ou especialidade, "
            "provavelmente encontra um concorrente antes.\n\n"
            "Desenvolvo sites profissionais para {nicho} com foco em aparecer nas buscas do Google, "
            "transmitir credibilidade e receber contatos diretos — sem depender de plataformas de terceiros.\n\n"
            "Vale uma conversa de 15 minutos essa semana?\n\n"
            "Att,\n"
            "{sender_name}\n"
            "{sender_whatsapp}\n"
            "{sender_website}\n\n"
            f"{UNSUBSCRIBE_FOOTER}"
        ),
    },
    "restaurante": {
        "subject": "{nome} — seu cardápio está onde os clientes procuram?",
        "body": (
            "Oi! Tudo bem?\n\n"
            "Vi o {nome} no {fonte} e fiquei com vontade de conhecer.\n"
            "Uma coisa que percebi: não tem um site com cardápio, horários e localização. "
            "Muita gente pesquisa isso antes de sair de casa — e quem não aparece perde a mesa pra concorrência.\n\n"
            "Crio sites aqui na região: cardápio online, link direto pro WhatsApp, "
            "mapa e tudo que o cliente precisa antes de chegar. Rápido de fazer, fácil de atualizar.\n\n"
            "Valeu,\n"
            "{sender_name}\n"
            "{sender_whatsapp}\n"
            "{sender_website}\n\n"
            f"{UNSUBSCRIBE_FOOTER}"
        ),
    },
}


def get_template(nicho: str) -> dict[str, str]:
    """Retorna o template mais adequado para o nicho informado."""
    normalized = (nicho or "").strip().lower()

    if any(keyword in normalized for keyword in ("restaurante", "bar", "lanchonete")):
        return TEMPLATES["restaurante"]

    if any(
        keyword in normalized
        for keyword in ("advocacia", "contabilidade", "odonto", "psicolog", "fisio")
    ):
        return TEMPLATES["profissional"]

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