import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.storage.database import create_tables, get_connection, db_session

TEST_DB = ":memory:"


@pytest.fixture
def client(monkeypatch):
    conn = get_connection(TEST_DB)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS registros (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            nivel_foco    INTEGER NOT NULL CHECK(nivel_foco BETWEEN 1 AND 5),
            tempo_minutos INTEGER NOT NULL CHECK(tempo_minutos > 0),
            comentario    TEXT    NOT NULL,
            categoria     TEXT,
            tags          TEXT,
            data          TEXT    NOT NULL
        );
    """)
    conn.commit()

    from contextlib import contextmanager

    @contextmanager
    def mock_db_session(db_path=TEST_DB):
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    monkeypatch.setattr("app.routes.registro_foco.db_session", mock_db_session)
    monkeypatch.setattr("app.routes.diagnostico.db_session", mock_db_session)

    with TestClient(app) as c:
        yield c

    conn.close()
