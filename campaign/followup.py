"""Módulo de follow-up automático para campanhas ProspectaAí."""

from __future__ import annotations

import os
import random
import time

from campaign.brevo_client import send_transactional_email
from db import get_connection, get_followup_leads


FOLLOWUP_SUBJECT = "Re: {nome} — só confirmando se recebeu"

FOLLOWUP_BODY = (
    "Oi, {nome}!\n\n"
    "Só passando para ver se meu email anterior chegou bem.\n"
    "Se quiser dar uma olhada nos exemplos de sites que já fiz, "
    "é só responder aqui — te mando na hora.\n\n"
    "Abraço,\n"
    "{sender_name}\n"
    "{sender_whatsapp}\n"
    "{sender_website}\n\n"
    "Para não receber mais emails: responda com REMOVER."
)


def _sleep_interval() -> float:
    if os.getenv("PROSPECTAAI_FAST_SLEEP") == "1":
        return 1.0
    return random.uniform(45, 90)


def _mask_email(email: str) -> str:
    if "@" not in email:
        return "***"
    local, domain = email.split("@", 1)
    if len(local) <= 2:
        masked_local = local[0:1] + "*"
    else:
        masked_local = local[:2] + "***"
    return f"{masked_local}@{domain}"


def _update_followup_status(lead_id: int, status: str) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE leads
            SET status_email = ?,
                enviado_em = datetime('now'),
                followup_count = followup_count + 1
            WHERE id = ?
            """,
            (status, lead_id),
        )
        connection.commit()


def run_followup(dry_run: bool = False) -> None:
    """Executa follow-ups para leads que não responderam após 4 dias."""
    leads = get_followup_leads()
    enviados = 0
    erros = 0

    if not leads:
        print("Nenhum follow-up pendente.")
        return

    sender_name = os.getenv("SENDER_NAME", "")
    sender_whatsapp = os.getenv("SENDER_WHATSAPP", "")
    sender_website = os.getenv("SENDER_WEBSITE", "")

    for lead in leads:
        email = lead.get("email") or ""
        masked_email = _mask_email(email)
        nome = lead.get("nome") or "empresa"
        nicho = lead.get("nicho") or "seu negócio"

        subject = FOLLOWUP_SUBJECT.format(nome=nome)
        body = FOLLOWUP_BODY.format(
            nome=nome,
            nicho=nicho,
            sender_name=lead.get("sender_name") or sender_name,
            sender_whatsapp=lead.get("sender_whatsapp") or sender_whatsapp,
            sender_website=lead.get("sender_website") or sender_website,
        )

        if dry_run:
            print(f"[DRY RUN] Follow-up para: {masked_email} | Assunto: {subject}")
        else:
            ok = send_transactional_email(
                to_email=email,
                to_name=nome,
                subject=subject,
                body=body,
            )
            if ok:
                _update_followup_status(int(lead["id"]), "enviado")
                enviados += 1
            else:
                _update_followup_status(int(lead["id"]), "erro")
                erros += 1

        time.sleep(_sleep_interval())

    if dry_run:
        print(f"Follow-up: {len(leads)} simulados")
    else:
        print(f"Follow-up: {enviados} enviados | {erros} erros")