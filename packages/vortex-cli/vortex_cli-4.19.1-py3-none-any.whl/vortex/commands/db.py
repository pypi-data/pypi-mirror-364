from __future__ import annotations

import logging
import os
import subprocess
import sys
import tempfile
from typing import Any

import tabulate

from vortex.models import DatabaseConnection
from vortex.models import PuakmaServer
from vortex.workspace import Workspace

logger = logging.getLogger("vortex")

GET_SCHEMA_SQL = """\
SELECT DISTINCT
    CASE
        WHEN isprimarykey = '1'
        THEN 'PK'
        ELSE ''
    END AS "PK"
    , attributename AS "Attribute"
    , CASE WHEN ref.tableid > 0
        THEN UPPER(ref.tablename)
        ELSE ''
    END AS "References"
    , CASE WHEN type IN ('VARCHAR', 'CHAR')
        THEN CONCAT(type, ' (', typesize, ')')
        ELSE type
    END AS "Type"
    , CASE
        WHEN isunique = '1'
        THEN 'Yes'
        ELSE 'No'
    END AS "Unique"
    , CASE
        WHEN allownull = '1'
        THEN 'Yes'
        ELSE 'No'
    END AS "Allow Null"
FROM attribute a
INNER JOIN pmatable t
ON t.tableid = a.tableid
INNER JOIN dbconnection db
ON db.dbconnectionid = t.dbconnectionid
LEFT JOIN pmatable ref
ON ref.tableid::VARCHAR = a.reftable
WHERE LOWER(db.dbname) = '%s'
    AND LOWER(t.tablename) = '%s'
ORDER BY attributename
"""

LIST_TABLES_SQL = """\
SELECT DISTINCT tablename
    , description
FROM dbconnection db
INNER JOIN pmatable t
ON db.dbconnectionid = t.dbconnectionid
WHERE LOWER(db.dbname)='%s'
"""


def _truncate_cols(result: tuple[dict[str, Any], ...]) -> tuple[dict[str, Any], ...]:
    number_of_cols = len(result[0])
    max_cols = 6
    if number_of_cols <= max_cols:
        return result

    left_cols = max_cols // 2
    right_cols = max_cols - left_cols
    truncated_result = []
    placeholder = "..."
    for row in result:
        truncated_row = dict(list(row.items())[:left_cols])
        truncated_row[placeholder] = placeholder
        truncated_row.update(dict(list(row.items())[-right_cols:]))
        truncated_result.append(truncated_row)
    logger.debug("Output has been truncated. Use --all-cols and --limit to control.")
    return tuple(truncated_result)


def _output_result(
    server: PuakmaServer,
    conn_id: int,
    sql: str,
    update: bool,
    truncate_cols: bool = False,
    db_name: str | None = None,
    schema_table: str | None = None,
    list_tables: bool = False,
) -> int:
    with server:
        result = tuple(server.database_designer.execute_query(conn_id, sql, update))
        if schema_table and not result:
            logger.error(f"Table '{schema_table}' not found in database '{db_name}'")
            return 1
        if list_tables and not result:
            logger.error(f"No tables found in database '{db_name}'.")
            return 1
        if result:
            if truncate_cols:
                result = _truncate_cols(result)
            print(
                tabulate.tabulate(
                    result,
                    headers="keys",
                    maxcolwidths=50,
                    tablefmt="psql",
                    showindex=True,
                )
            )
        else:
            logger.info("Query returned nil results.")
    return 0


def _is_connection_cloned(workspace: Workspace, conn_id: int) -> bool:
    """Returns True if the given conn_id exists in a locally cloned Application."""
    conns: list[DatabaseConnection] = []
    for app in workspace.listapps():
        if app.db_connections:
            conns.extend(app.db_connections)
    return any(conn.id == conn_id for conn in conns)


def _read_from_editor() -> str:
    fd, tmp_sql_file = tempfile.mkstemp(suffix=".sql")
    os.close(fd)
    try:
        subprocess.call(["nano", tmp_sql_file])
        with open(tmp_sql_file) as f:
            return f.read().strip()
    finally:
        os.remove(tmp_sql_file)


def db(
    workspace: Workspace,
    server: PuakmaServer,
    database: int | str,
    sql: str | None,
    update: bool = False,
    limit_n_results: int = 5,
    schema_table: str | None = None,
    list_tables: bool = False,
    truncate_cols: bool = False,
) -> int:
    if sql is not None:
        if sql.strip() == "":
            sql = None if sys.platform == "win32" else _read_from_editor()
        db_name = None
        conn_id = int(database)
        # If we're modifying a database, lets check that its locally
        # cloned to ensure intent
        if update and not _is_connection_cloned(workspace, conn_id):
            logger.error(f"No cloned applications with DB Connection ID '{conn_id}'")
            return 1
        if sql and not update:
            sql = sql + f" LIMIT {limit_n_results}"
    else:
        db_name = str(database).lower()
        update = False
        truncate_cols = False
        conn_id = server.puakma_db_conn_id
        if schema_table is not None:
            sql = GET_SCHEMA_SQL % (db_name, schema_table)
        elif list_tables:
            sql = LIST_TABLES_SQL % db_name

    if not sql:
        logger.error("No Query to execute.")
        return 1

    return _output_result(
        server, conn_id, sql, update, truncate_cols, db_name, schema_table, list_tables
    )
