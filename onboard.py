from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
import os
import sqlite3


load_dotenv()

CLIENTS_DIR = Path("clients")
DEFAULT_NICHOS = [
    "clínicas odontológicas",
    "escritórios de advocacia",
    "restaurantes",
    "pousadas",
    "pet shops",
]
DEFAULT_CIDADES = ["Belém-PA"]
DEFAULT_PLANO = "starter"
DEFAULT_LIMITE_DIARIO = 30
DEFAULT_PORTFOLIO = "https://exemplo.com/portfolio"

SCHEMA = """
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    nicho TEXT NOT NULL,
    telefone TEXT,
    email TEXT,
    site TEXT,
    instagram TEXT,
    fonte TEXT NOT NULL,
    cidade TEXT DEFAULT 'Belém',
    status_email TEXT DEFAULT 'pendente',
    enviado_em TEXT,
    followup_count INTEGER DEFAULT 0,
    respondeu INTEGER DEFAULT 0,
    coletado_em TEXT DEFAULT (datetime('now'))
);
"""


def _slugify(value: str) -> str:
    normalized = value.strip().lower()
    normalized = (
        normalized.replace("ã", "a")
        .replace("á", "a")
        .replace("à", "a")
        .replace("â", "a")
        .replace("é", "e")
        .replace("ê", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ô", "o")
        .replace("õ", "o")
        .replace("ú", "u")
        .replace("ç", "c")
    )
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    return normalized.strip("-") or "cliente"


def _init_client_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as connection:
        connection.execute(SCHEMA)
        connection.commit()


def _write_config(client_dir: Path, payload: dict[str, Any]) -> Path:
    config_path = client_dir / "config.json"
    with config_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    return config_path


def _write_templates(client_dir: Path, client_name: str, portfolio: str) -> Path:
    template_path = client_dir / "templates.json"
    templates = {
        "comercio": {
            "subject": f"{client_name} - oportunidade para {{nicho}}",
            "body": (
                f"Olá, {{nome}}.\n\n"
                f"Sou da {client_name} e vi seu negócio em {{fonte}}.\n"
                f"Temos um portfólio com resultados em negócios locais: {portfolio}\n\n"
                "Se fizer sentido, posso enviar um diagnóstico rápido.\n\n"
                "Para não receber mais emails: responda com REMOVER."
            ),
        },
        "profissional": {
            "subject": f"{client_name} - proposta para {{nicho}}",
            "body": (
                f"Olá, {{nome}}.\n\n"
                f"Sou da {client_name} e vi sua presença em {{fonte}}.\n"
                f"Aqui está nosso portfólio: {portfolio}\n\n"
                "Posso te enviar uma sugestão objetiva de próximos passos.\n\n"
                "Para não receber mais emails: responda com REMOVER."
            ),
        },
        "restaurante": {
            "subject": f"{client_name} - mais reservas para {{nicho}}",
            "body": (
                f"Olá, {{nome}}.\n\n"
                f"Sou da {client_name} e encontrei seu perfil em {{fonte}}.\n"
                f"Portfólio com resultados: {portfolio}\n\n"
                "Se quiser, posso te mandar uma ideia prática aplicada ao seu contexto.\n\n"
                "Para não receber mais emails: responda com REMOVER."
            ),
        },
    }
    with template_path.open("w", encoding="utf-8") as handle:
        json.dump(templates, handle, ensure_ascii=False, indent=2)
    return template_path


def onboard_client(client_name: str) -> Path:
    slug = _slugify(client_name)
    client_dir = CLIENTS_DIR / slug
    client_dir.mkdir(parents=True, exist_ok=True)

    db_path = client_dir / "leads.db"
    _init_client_db(db_path)

    sender_email = os.getenv("SENDER_EMAIL", "contato@exemplo.com")
    config_payload = {
        "nome": client_name,
        "plano": DEFAULT_PLANO,
        "cidades": DEFAULT_CIDADES,
        "nichos": DEFAULT_NICHOS,
        "sender_email": sender_email,
        "limite_diario": DEFAULT_LIMITE_DIARIO,
        "portfolio": DEFAULT_PORTFOLIO,
        "criado_em": datetime.now().isoformat(timespec="seconds"),
    }
    _write_config(client_dir, config_payload)
    _write_templates(client_dir, client_name, DEFAULT_PORTFOLIO)

    print(f"Cliente criado em: {client_dir}")
    print("Checklist de próximos passos:")
    print("- Configurar subdomínio DNS do cliente")
    print("- Validar sender no Brevo")
    print("- Revisar termos de uso e compliance LGPD com jurídico")
    print("- Confirmar nichos e cidades prioritárias")

    return client_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Onboarding de cliente ProspectaAí")
    parser.add_argument("--client", required=True, help="Nome do cliente")
    args = parser.parse_args()

    onboard_client(args.client)


if __name__ == "__main__":
    main()
