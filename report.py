from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter

from campaign.brevo_client import send_transactional_email
from db import get_connection


REPORT_DIR = Path("reports")
OPERATOR_EMAIL = "luan.alves.developer@gmail.com"
OPERATOR_NAME = "Luan Alves | Web"


def _fetch_weekly_leads() -> pd.DataFrame:
    since = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as connection:
        dataframe = pd.read_sql_query(
            """
            SELECT *
            FROM leads
            WHERE coletado_em >= ?
            ORDER BY coletado_em ASC
            """,
            connection,
            params=(since,),
        )
    return dataframe


def _format_worksheet(writer: pd.ExcelWriter, sheet_name: str = "Leads") -> None:
    worksheet = writer.sheets[sheet_name]
    header_font = Font(bold=True)

    for cell in worksheet[1]:
        cell.font = header_font

    for column_cells in worksheet.columns:
        max_length = max(len(str(cell.value)) if cell.value is not None else 0 for cell in column_cells)
        column_letter = get_column_letter(column_cells[0].column)
        worksheet.column_dimensions[column_letter].width = min(max_length + 2, 40)


def generate_weekly_report() -> str:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    date_suffix = datetime.now().strftime("%Y-%m-%d")
    filepath = REPORT_DIR / f"relatorio_{date_suffix}.xlsx"

    dataframe = _fetch_weekly_leads()
    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        dataframe.to_excel(writer, index=False, sheet_name="Leads")
        _format_worksheet(writer, "Leads")

    return str(filepath)


def _fetch_weekly_metrics() -> dict[str, int]:
    since = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                SUM(CASE WHEN status_email = 'enviado' THEN 1 ELSE 0 END) AS enviados,
                SUM(CASE WHEN respondeu = 1 THEN 1 ELSE 0 END) AS respondidos,
                SUM(CASE
                        WHEN site IS NULL
                             OR TRIM(COALESCE(site, '')) = ''
                             OR LOWER(COALESCE(site, '')) LIKE '%instagram.com%'
                             OR LOWER(COALESCE(site, '')) LIKE '%facebook.com%'
                             OR LOWER(COALESCE(site, '')) LIKE '%linktr.ee%'
                             OR LOWER(COALESCE(site, '')) LIKE '%bio.link%'
                             OR LOWER(COALESCE(site, '')) LIKE '%wa.me%'
                             OR LOWER(COALESCE(site, '')) LIKE '%whatsapp.com%'
                    THEN 1 ELSE 0
                END) AS quentes
            FROM leads
            WHERE coletado_em >= ?
            """,
            (since,),
        ).fetchone()

    return {
        "enviados": int(row["enviados"] or 0),
        "respondidos": int(row["respondidos"] or 0),
        "quentes": int(row["quentes"] or 0),
    }


def send_report_email(filepath: str) -> bool:
    metrics = _fetch_weekly_metrics()
    subject = "Relatório semanal ProspectaAí"
    body = (
        "Olá.\n\n"
        "Segue o relatório semanal em anexo.\n\n"
        f"Enviados: {metrics['enviados']}\n"
        "Abertos: (indisponível)\n"
        f"Respondidos: {metrics['respondidos']}\n"
        f"Leads quentes novos: {metrics['quentes']}\n\n"
        "Qualquer ajuste, me avise."
    )

    attachment_path = Path(filepath)
    if not attachment_path.exists():
        raise FileNotFoundError(filepath)

    return send_transactional_email(
        to_email=OPERATOR_EMAIL,
        to_name=OPERATOR_NAME,
        subject=subject,
        body=body,
    )


def main() -> None:
    filepath = generate_weekly_report()
    print(f"Relatório gerado em: {filepath}")
    # Envio real do email deve ser aprovado manualmente antes da execução.


if __name__ == "__main__":
    main()
