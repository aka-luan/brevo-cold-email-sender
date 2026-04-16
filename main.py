from __future__ import annotations

import argparse

from db import export_to_csv, get_connection, get_stats


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ProspectaAí CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    stats_parser = subparsers.add_parser("stats", help="Mostra estatísticas atuais dos leads")
    stats_parser.set_defaults(handler=handle_stats)

    export_parser = subparsers.add_parser("export", help="Exporta os leads para CSV")
    export_parser.add_argument("--output", required=True, help="Arquivo CSV de saída")
    export_parser.set_defaults(handler=handle_export)

    return parser


def _print_table(title: str, rows: list[tuple[str, int]]) -> None:
    print(title)
    if not rows:
        print("  (sem dados)")
        return

    label_width = max(len(label) for label, _ in rows)
    value_width = max(len(str(value)) for _, value in rows)

    for label, value in rows:
        print(f"  {label.ljust(label_width)} | {str(value).rjust(value_width)}")


def _fetch_grouped_counts(column: str) -> list[tuple[str, int]]:
    with get_connection() as connection:
        rows = connection.execute(
            f"""
            SELECT COALESCE(NULLIF(TRIM({column}), ''), '(não informado)') AS label,
                   COUNT(*) AS total
            FROM leads
            GROUP BY label
            ORDER BY total DESC, label ASC
            """
        ).fetchall()

    return [(str(row["label"]), int(row["total"])) for row in rows]


def print_stats() -> None:
    stats = get_stats()
    print("Estatísticas ProspectaAí")
    print("=" * 24)
    _print_table(
        "Resumo",
        [
            ("Total", stats["total"]),
            ("Quentes", stats["quentes"]),
            ("Pendentes", stats["pendentes"]),
            ("Enviados", stats["enviados"]),
            ("Erros", stats["erros"]),
            ("Respondidos", stats["respondidos"]),
        ],
    )
    print()
    _print_table("Por nicho", _fetch_grouped_counts("nicho"))
    print()
    _print_table("Por status", _fetch_grouped_counts("status_email"))


def handle_stats(_: argparse.Namespace) -> None:
    print_stats()


def handle_export(args: argparse.Namespace) -> None:
    export_to_csv(args.output)
    print(f"Exportação concluída: {args.output}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
