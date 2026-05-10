import os
import sqlite3
from contextlib import contextmanager

# Caminho padrão do banco em produção. Nos testes é sobrescrito por ":memory:".
DB_PATH = os.getenv("DB_PATH", "performance.db")

# DDL executado no startup via create_tables(). CHECK constraints replicam as
# validações do Pydantic diretamente no banco, evitando dados inconsistentes
# caso o banco seja acessado fora da API.
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
    """Abre e retorna uma conexão SQLite com row_factory configurado.

    row_factory = sqlite3.Row permite acessar colunas por nome (row["campo"])
    em vez de por índice, tornando o código do repository mais legível.
    check_same_thread=False é necessário porque o FastAPI executa handlers
    em worker threads diferentes da thread principal.

    Usado por: db_session, create_tables, conftest.py (testes).
    """
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables(db_path: str = DB_PATH) -> None:
    """Cria as tabelas se ainda não existirem. Chamado no startup da aplicação.

    Usado por: app/main.py (lifespan).
    """
    with get_connection(db_path) as conn:
        conn.executescript(DDL)


@contextmanager
def db_session(db_path: str = DB_PATH):
    """Context manager que abre uma conexão, faz commit ao sair e rollback em erro.

    Garante que a conexão é sempre fechada, mesmo em caso de exceção.
    Usado por: get_conn() em app/routes/registro_foco.py e app/routes/diagnostico.py.
    """
    conn = get_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
