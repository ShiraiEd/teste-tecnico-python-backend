import sqlite3
from contextlib import contextmanager

DB_PATH = "performance.db"

DDL = """
CREATE TABLE IF NOT EXISTS registros (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nivel_foco    INTEGER NOT NULL CHECK(nivel_foco BETWEEN 1 AND 5),
    tempo_minutos INTEGER NOT NULL CHECK(tempo_minutos > 0),
    comentario    TEXT    NOT NULL,
    categoria     TEXT,
    tags          TEXT,
    data          TEXT    NOT NULL
);
"""


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables(db_path: str = DB_PATH) -> None:
    with get_connection(db_path) as conn:
        conn.executescript(DDL)


@contextmanager
def db_session(db_path: str = DB_PATH):
    conn = get_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
