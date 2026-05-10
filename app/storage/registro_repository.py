import json
import sqlite3

from app.storage.base_repository import AbstractRegistroRepository


class SQLiteRegistroRepository(AbstractRegistroRepository):
    """Implementação SQLite de AbstractRegistroRepository.

    Todas as queries usam parâmetros posicionais (?) para prevenir SQL injection.
    tags é serializado como JSON em coluna TEXT por ser uma lista variável
    sem necessidade de tabela pivot para esse volume de dados.

    Usado por: registro_service.processar_registro, diagnostico_service.calcular
    (via instância singleton `registro_repository` ao final deste módulo).
    """

    def inserir(self, conn: sqlite3.Connection, registro: dict) -> dict:
        """Insere um registro e retorna o dict original com o id gerado pelo banco."""
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
                # Serializa lista como JSON; None se tags não informado
                json.dumps(registro["tags"]) if registro.get("tags") else None,
                registro["data"],
            ),
        )
        return {**registro, "id": cursor.lastrowid}

    def listar_todos(self, conn: sqlite3.Connection) -> list[dict]:
        """Retorna todos os registros ordenados por data ASC (mais antigo primeiro).

        Ordem crescente é necessária para que _tendencia() e _streak_dias()
        calculem corretamente a evolução temporal sem precisar reordenar.
        Deserializa a coluna tags de JSON para list[str].
        """
        rows = conn.execute("SELECT * FROM registros ORDER BY data ASC").fetchall()
        result = []
        for row in rows:
            r = dict(row)
            r["tags"] = json.loads(r["tags"]) if r["tags"] else []
            result.append(r)
        return result

    def contar(self, conn: sqlite3.Connection) -> int:
        """Retorna o total de registros. Usado para verificações rápidas sem carregar dados."""
        return conn.execute("SELECT COUNT(*) FROM registros").fetchone()[0]


# Singleton compartilhado por todas as rotas e serviços.
# Não instanciar diretamente nas rotas — importar esta instância.
registro_repository = SQLiteRegistroRepository()
