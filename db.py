from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd


DB_PATH = Path("leads.db")
TABLE_NAME = "leads"
SOCIAL_ONLY_DOMAINS = (
    "instagram.com",
    "facebook.com",
    "linktr.ee",
    "bio.link",
    "wa.me",
    "whatsapp.com",
)
SCHEMA = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
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
COLUMN_DEFINITIONS = {
    "nome": "TEXT NOT NULL",
    "nicho": "TEXT NOT NULL",
    "telefone": "TEXT",
    "email": "TEXT",
    "site": "TEXT",
    "instagram": "TEXT",
    "fonte": "TEXT NOT NULL",
    "cidade": "TEXT DEFAULT 'Belém'",
    "status_email": "TEXT DEFAULT 'pendente'",
    "enviado_em": "TEXT",
    "followup_count": "INTEGER DEFAULT 0",
    "respondeu": "INTEGER DEFAULT 0",
    "coletado_em": "TEXT DEFAULT (datetime('now'))",
}
DEFAULT_STATS = {
    "total": 0,
    "pendentes": 0,
    "enviados": 0,
    "erros": 0,
    "respondidos": 0,
    "quentes": 0,
}


def get_connection() -> sqlite3.Connection:
    DB_PATH.touch(exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with get_connection() as connection:
        connection.execute(SCHEMA)
        connection.commit()

    migrate()


def migrate() -> None:
    with get_connection() as connection:
        for column_name, definition in COLUMN_DEFINITIONS.items():
            try:
                connection.execute(
                    f"ALTER TABLE {TABLE_NAME} ADD COLUMN {column_name} {definition}"
                )
            except sqlite3.OperationalError:
                continue

        connection.commit()


def _row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None

    return dict(row)


def _rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]


def _is_social_only(site: str | None) -> bool:
    if site is None:
        return True

    normalized_site = site.strip().lower()
    if not normalized_site:
        return True

    return any(domain in normalized_site for domain in SOCIAL_ONLY_DOMAINS)


def insert_lead(lead: dict[str, Any]) -> bool:
    init_db()

    nome = (lead.get("nome") or "").strip()
    nicho = (lead.get("nicho") or "").strip()
    fonte = (lead.get("fonte") or "").strip()

    if not nome or not nicho or not fonte:
        raise ValueError("Lead precisa conter nome, nicho e fonte.")

    telefone = lead.get("telefone")
    with get_connection() as connection:
        duplicate = connection.execute(
            f"""
            SELECT id
            FROM {TABLE_NAME}
            WHERE nome = ?
              AND (
                    (telefone = ?)
                    OR (telefone IS NULL AND ? IS NULL)
                  )
            LIMIT 1
            """,
            (nome, telefone, telefone),
        ).fetchone()
        if duplicate is not None:
            return False

        connection.execute(
            f"""
            INSERT INTO {TABLE_NAME} (
                nome, nicho, telefone, email, site, instagram, fonte,
                cidade, status_email, enviado_em, followup_count, respondeu
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                nome,
                nicho,
                telefone,
                lead.get("email"),
                lead.get("site"),
                lead.get("instagram"),
                fonte,
                lead.get("cidade", "Belém"),
                lead.get("status_email", "pendente"),
                lead.get("enviado_em"),
                int(lead.get("followup_count", 0) or 0),
                int(lead.get("respondeu", 0) or 0),
            ),
        )
        connection.commit()
        return True


def _normalize_text(value: Any) -> str | None:
    if value is None:
        return None

    normalized = str(value).strip()
    return normalized or None


def _find_existing_lead_row(
    connection: sqlite3.Connection, lead: dict[str, Any]
) -> sqlite3.Row | None:
    email = _normalize_text(lead.get("email"))
    nome = _normalize_text(lead.get("nome"))
    telefone = _normalize_text(lead.get("telefone"))

    if email is not None:
        row = connection.execute(
            f"""
            SELECT *
            FROM {TABLE_NAME}
            WHERE LOWER(TRIM(COALESCE(email, ''))) = LOWER(?)
            ORDER BY id DESC
            LIMIT 1
            """,
            (email,),
        ).fetchone()
        if row is not None:
            return row

    if nome is None:
        return None

    return connection.execute(
        f"""
        SELECT *
        FROM {TABLE_NAME}
        WHERE nome = ?
          AND (
                (telefone = ?)
                OR (telefone IS NULL AND ? IS NULL)
              )
        ORDER BY id DESC
        LIMIT 1
        """,
        (nome, telefone, telefone),
    ).fetchone()


def upsert_lead(lead: dict[str, Any]) -> dict[str, Any]:
    """Insere ou atualiza um lead e devolve a linha persistida."""
    init_db()

    nome = _normalize_text(lead.get("nome"))
    nicho = _normalize_text(lead.get("nicho"))
    fonte = _normalize_text(lead.get("fonte"))

    if not nome or not nicho or not fonte:
        raise ValueError("Lead precisa conter nome, nicho e fonte.")

    payload = {
        "nome": nome,
        "nicho": nicho,
        "telefone": _normalize_text(lead.get("telefone")),
        "email": _normalize_text(lead.get("email")),
        "site": _normalize_text(lead.get("site")),
        "instagram": _normalize_text(lead.get("instagram")),
        "fonte": fonte,
        "cidade": _normalize_text(lead.get("cidade")) or "Belém",
    }

    with get_connection() as connection:
        existing = _find_existing_lead_row(connection, payload)

        if existing is None:
            cursor = connection.execute(
                f"""
                INSERT INTO {TABLE_NAME} (
                    nome, nicho, telefone, email, site, instagram, fonte, cidade
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["nome"],
                    payload["nicho"],
                    payload["telefone"],
                    payload["email"],
                    payload["site"],
                    payload["instagram"],
                    payload["fonte"],
                    payload["cidade"],
                ),
            )
            lead_id = int(cursor.lastrowid)
        else:
            lead_id = int(existing["id"])
            connection.execute(
                f"""
                UPDATE {TABLE_NAME}
                SET nome = ?,
                    nicho = ?,
                    telefone = ?,
                    email = ?,
                    site = ?,
                    instagram = ?,
                    fonte = ?,
                    cidade = ?
                WHERE id = ?
                """,
                (
                    payload["nome"],
                    payload["nicho"],
                    payload["telefone"],
                    payload["email"],
                    payload["site"],
                    payload["instagram"],
                    payload["fonte"],
                    payload["cidade"],
                    lead_id,
                ),
            )

        connection.commit()
        row = connection.execute(
            f"""
            SELECT *
            FROM {TABLE_NAME}
            WHERE id = ?
            """,
            (lead_id,),
        ).fetchone()

    persisted = _row_to_dict(row)
    if persisted is None:
        raise RuntimeError("Falha ao persistir lead no banco.")
    return persisted


def sync_csv_leads(leads: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    """
    Persiste leads vindos de CSV e devolve apenas os pendentes para envio.
    """
    pending_leads: list[dict[str, Any]] = []

    for lead in leads:
        persisted = upsert_lead(lead)
        email = _normalize_text(persisted.get("email"))
        if persisted.get("status_email") != "pendente" or email is None:
            continue

        pending_leads.append(persisted)
        if len(pending_leads) >= limit:
            break

    return pending_leads


def get_hot_leads() -> list[dict[str, Any]]:
    init_db()

    conditions = " OR ".join(["LOWER(COALESCE(site, '')) LIKE ?" for _ in SOCIAL_ONLY_DOMAINS])
    params = [f"%{domain}%" for domain in SOCIAL_ONLY_DOMAINS]

    with get_connection() as connection:
        rows = connection.execute(
            f"""
            SELECT *
            FROM {TABLE_NAME}
            WHERE site IS NULL
               OR TRIM(COALESCE(site, '')) = ''
               OR ({conditions})
            ORDER BY coletado_em DESC, id DESC
            """,
            params,
        ).fetchall()

    return _rows_to_dicts(rows)


def get_pending_leads(limit: int) -> list[dict[str, Any]]:
    init_db()

    with get_connection() as connection:
        rows = connection.execute(
            f"""
            SELECT *
            FROM {TABLE_NAME}
            WHERE status_email = 'pendente'
              AND email IS NOT NULL
              AND TRIM(email) <> ''
            ORDER BY coletado_em ASC, id ASC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return _rows_to_dicts(rows)


def get_followup_leads() -> list[dict[str, Any]]:
    init_db()

    with get_connection() as connection:
        rows = connection.execute(
            f"""
            SELECT *
            FROM {TABLE_NAME}
            WHERE status_email = 'enviado'
              AND respondeu = 0
              AND followup_count < 2
              AND enviado_em IS NOT NULL
              AND enviado_em <= datetime('now', '-4 days')
            ORDER BY enviado_em ASC, id ASC
            """
        ).fetchall()

    return _rows_to_dicts(rows)


def update_lead_status(id: int, status: str) -> None:
    init_db()

    with get_connection() as connection:
        connection.execute(
            f"""
            UPDATE {TABLE_NAME}
            SET status_email = ?,
                enviado_em = CASE
                    WHEN ? = 'enviado' THEN datetime('now')
                    ELSE enviado_em
                END
            WHERE id = ?
            """,
            (status, status, id),
        )
        connection.commit()


def export_to_csv(filepath: str) -> None:
    init_db()

    with get_connection() as connection:
        dataframe = pd.read_sql_query(
            f"SELECT * FROM {TABLE_NAME} ORDER BY id ASC", connection
        )

    output_path = Path(filepath)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(output_path, index=False)


def get_stats() -> dict[str, int]:
    init_db()

    conditions = " OR ".join(["LOWER(COALESCE(site, '')) LIKE ?" for _ in SOCIAL_ONLY_DOMAINS])
    params = [f"%{domain}%" for domain in SOCIAL_ONLY_DOMAINS]

    with get_connection() as connection:
        row = connection.execute(
            f"""
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN status_email = 'pendente' THEN 1 ELSE 0 END) AS pendentes,
                SUM(CASE WHEN status_email = 'enviado' THEN 1 ELSE 0 END) AS enviados,
                SUM(CASE WHEN status_email = 'erro' THEN 1 ELSE 0 END) AS erros,
                SUM(CASE WHEN respondeu = 1 THEN 1 ELSE 0 END) AS respondidos,
                SUM(
                    CASE
                        WHEN site IS NULL
                             OR TRIM(COALESCE(site, '')) = ''
                             OR ({conditions})
                        THEN 1 ELSE 0
                    END
                ) AS quentes
            FROM {TABLE_NAME}
            """,
            params,
        ).fetchone()

    if row is None:
        return DEFAULT_STATS.copy()

    return {
        key: int(row[key] or 0)
        for key in DEFAULT_STATS
    }


init_db()
