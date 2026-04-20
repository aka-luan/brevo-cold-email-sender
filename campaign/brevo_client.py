from __future__ import annotations

from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from sib_api_v3_sdk import (
    ApiClient,
    Configuration,
    SendSmtpEmail,
    TransactionalEmailsApi,
)
from sib_api_v3_sdk.rest import ApiException
import os


load_dotenv()

LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "campaign.log"
BREVO_API_KEY = os.getenv("BREVO_API_KEY", "")
SENDER_NAME = os.getenv("SENDER_NAME", "")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
REPLY_TO_EMAIL = os.getenv("REPLY_TO_EMAIL", "luan.alves.developer@gmail.com")
REPLY_TO_NAME = os.getenv("REPLY_TO_NAME", SENDER_NAME or SENDER_EMAIL)


def _ensure_log_dir() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def _write_log(to_email: str, subject: str, result: str) -> None:
    _ensure_log_dir()
    timestamp = datetime.now().isoformat(timespec="seconds")
    with LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(f"[{timestamp}] | [{to_email}] | [{subject}] | [{result}]\n")


def send_transactional_email(to_email: str, to_name: str, subject: str, body: str) -> bool:
    _ensure_log_dir()

    if not BREVO_API_KEY or not SENDER_EMAIL:
        _write_log(to_email, subject, "erro: credenciais Brevo ausentes")
        return False

    configuration = Configuration()
    configuration.api_key["api-key"] = BREVO_API_KEY

    try:
        api_instance = TransactionalEmailsApi(ApiClient(configuration))
        payload_kwargs = {
            "to": [{"email": to_email, "name": to_name or to_email}],
            "sender": {"email": SENDER_EMAIL, "name": SENDER_NAME or SENDER_EMAIL},
            "subject": subject,
            "text_content": body,
        }
        if REPLY_TO_EMAIL:
            payload_kwargs["reply_to"] = {
                "email": REPLY_TO_EMAIL,
                "name": REPLY_TO_NAME or REPLY_TO_EMAIL,
            }
        payload = SendSmtpEmail(
            **payload_kwargs
        )
        api_instance.send_transac_email(payload)
        _write_log(to_email, subject, "enviado")
        return True
    except ApiException as exc:
        _write_log(to_email, subject, f"erro: {exc}")
        return False
    except Exception as exc:
        _write_log(to_email, subject, f"erro: {exc}")
        return False
