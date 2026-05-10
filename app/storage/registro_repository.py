import json
import sqlite3


def inserir(conn: sqlite3.Connection, registro: dict) -> dict:
    cursor = conn.execute(
        """
        INSERT INTO registros (nivel_foco, tempo_minutos, comentario, categoria, tags, data)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            registro["nivel_foco"],
            registro["tempo_minutos"],
            registro["comentario"],
            registro.get("categoria"),
            json.dumps(registro["tags"]) if registro.get("tags") else None,
            registro["data"],
        ),
    )
    conn.commit()
    return {**registro, "id": cursor.lastrowid}


def listar_todos(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM registros ORDER BY data ASC"
    ).fetchall()
    result = []
    for row in rows:
        r = dict(row)
        r["tags"] = json.loads(r["tags"]) if r["tags"] else []
        result.append(r)
    return result


def contar(conn: sqlite3.Connection) -> int:
    return conn.execute("SELECT COUNT(*) FROM registros").fetchone()[0]
