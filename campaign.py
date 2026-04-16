from __future__ import annotations

import argparse

from campaign.followup import run_followup
from campaign.sender import run_campaign
from db import get_connection


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ProspectaAí Campanhas")
    subparsers = parser.add_subparsers(dest="command", required=True)

    send_parser = subparsers.add_parser("send", help="Executa envio da campanha")
    send_parser.add_argument("--limit", type=int, default=30, help="Quantidade máxima de envios")
    send_parser.add_argument("--dry-run", action="store_true", help="Simula envios sem chamar a API")
    send_parser.set_defaults(handler=handle_send)

    followup_parser = subparsers.add_parser("followup", help="Executa follow-up da campanha")
    followup_parser.add_argument("--dry-run", action="store_true", help="Simula envios sem chamar a API")
    followup_parser.set_defaults(handler=handle_followup)

    stats_parser = subparsers.add_parser("stats", help="Mostra estatísticas de campanha")
    stats_parser.set_defaults(handler=handle_stats)

    return parser


def _fetch_campaign_stats() -> dict[str, int]:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN status_email = 'pendente' THEN 1 ELSE 0 END) AS pendentes,
                SUM(CASE WHEN status_email = 'enviado' THEN 1 ELSE 0 END) AS enviados,
                SUM(CASE WHEN status_email = 'erro' THEN 1 ELSE 0 END) AS erros,
                SUM(CASE WHEN respondeu = 1 THEN 1 ELSE 0 END) AS respondidos,
                SUM(CASE WHEN followup_count > 0 THEN 1 ELSE 0 END) AS followups
            FROM leads
            """
        ).fetchone()

    return {
        "total": int(row["total"] or 0),
        "pendentes": int(row["pendentes"] or 0),
        "enviados": int(row["enviados"] or 0),
        "erros": int(row["erros"] or 0),
        "respondidos": int(row["respondidos"] or 0),
        "followups": int(row["followups"] or 0),
    }


def handle_send(args: argparse.Namespace) -> None:
    run_campaign(daily_limit=args.limit, dry_run=args.dry_run)


def handle_followup(args: argparse.Namespace) -> None:
    run_followup(dry_run=args.dry_run)


def handle_stats(_: argparse.Namespace) -> None:
    stats = _fetch_campaign_stats()
    print("Estatísticas de campanha")
    print(f"Total: {stats['total']}")
    print(f"Pendentes: {stats['pendentes']}")
    print(f"Enviados: {stats['enviados']}")
    print(f"Erros: {stats['erros']}")
    print(f"Follow-ups: {stats['followups']}")
    print(f"Respondidos: {stats['respondidos']}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
