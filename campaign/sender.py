"""Módulo de envio da campanha de email frio para ProspectaAí."""

from __future__ import annotations

import os
import random
import time

from apify_loader import load_apify_csv
from campaign.brevo_client import send_transactional_email
from campaign.templates import get_template, render_template
from db import get_pending_leads, sync_csv_leads, update_lead_status


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


def _normalize_csv_lead(lead: dict[str, str]) -> dict[str, str]:
    normalized = dict(lead)

    email = (normalized.get("email") or "").strip()
    normalized["email"] = email
    normalized["nicho"] = (
        normalized.get("nicho")
        or normalized.get("keyword")
        or "comercio"
    )
    normalized["nome"] = (
        normalized.get("nome")
        or normalized.get("title")
        or (email.split("@")[0] if email else "")
    )
    normalized["site"] = normalized.get("site") or normalized.get("url") or ""
    normalized["fonte"] = normalized.get("fonte") or "Apify CSV"

    return normalized


def run_campaign(daily_limit: int = 30, dry_run: bool = False) -> None:
    """Executa a campanha de email frio para leads pendentes."""
    csv_path = os.getenv("APIFY_CSV_PATH")
    if csv_path:
        leads = sync_csv_leads(
            [_normalize_csv_lead(lead) for lead in load_apify_csv(csv_path)],
            daily_limit,
        )
    else:
        leads = get_pending_leads(daily_limit)
    
    enviados = 0
    erros = 0

    if not leads:
        print("Nenhum lead pendente para envio.")
        return

    # Injeta sender vars em cada lead para render_template acessar
    sender_name = os.getenv("SENDER_NAME", "")
    sender_whatsapp = os.getenv("SENDER_WHATSAPP", "")
    sender_website = os.getenv("SENDER_WEBSITE", "")

    for lead in leads:
        lead.setdefault("sender_name", sender_name)
        lead.setdefault("sender_whatsapp", sender_whatsapp)
        lead.setdefault("sender_website", sender_website)

        template = get_template(lead.get("nicho", ""))
        rendered = render_template(template, lead)
        email = lead.get("email") or ""
        masked_email = _mask_email(email)

        if dry_run:
            print(f"[DRY RUN] Enviaria para: {masked_email} | Assunto: {rendered['subject']}")
        else:
            ok = send_transactional_email(
                to_email=email,
                to_name=lead.get("nome") or email,
                subject=rendered["subject"],
                body=rendered["body"],
            )
            if ok:
                update_lead_status(int(lead["id"]), "enviado")
                enviados += 1
            else:
                update_lead_status(int(lead["id"]), "erro")
                erros += 1

        time.sleep(_sleep_interval())

    if dry_run:
        print(f"Campanha: {len(leads)} simulados")
    else:
        print(f"Campanha: {enviados} enviados | {erros} erros")


def main() -> None:
    run_campaign()
