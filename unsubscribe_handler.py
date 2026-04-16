from __future__ import annotations

import argparse
from pathlib import Path

from db import get_connection


def _load_emails(path: Path) -> list[str]:
    raw = path.read_text(encoding="utf-8")
    emails: list[str] = []
    for chunk in raw.replace(",", "\n").splitlines():
        cleaned = chunk.strip()
        if cleaned:
            emails.append(cleaned)
    return emails


def _mask_email(email: str) -> str:
    if "@" not in email:
        return "***"
    local, domain = email.split("@", 1)
    if len(local) <= 2:
        masked_local = local[0:1] + "*"
    else:
        masked_local = local[:2] + "***"
    return f"{masked_local}@{domain}"


def unsubscribe_emails(emails: list[str]) -> int:
    if not emails:
        return 0

    placeholders = ",".join(["?"] * len(emails))
    with get_connection() as connection:
        result = connection.execute(
            f"""
            UPDATE leads
            SET status_email = 'descadastrado'
            WHERE email IN ({placeholders})
            """,
            emails,
        )
        connection.commit()
        return result.rowcount


def main() -> None:
    parser = argparse.ArgumentParser(description="Processa descadastramentos")
    parser.add_argument("--input", required=True, help="Arquivo com emails (um por linha ou separados por vírgula)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(str(input_path))

    emails = _load_emails(input_path)
    updated = unsubscribe_emails(emails)
    print(f"Descadastramentos aplicados: {updated} de {len(emails)}")
    if emails:
        print(f"Exemplo (mascarado): {_mask_email(emails[0])}")


if __name__ == "__main__":
    main()
