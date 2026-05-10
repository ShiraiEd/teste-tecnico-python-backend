from abc import ABC, abstractmethod
import sqlite3


class AbstractRegistroRepository(ABC):
    """Contrato de acesso a dados para registros de foco.

    Define os métodos que qualquer implementação de storage deve satisfazer.
    Usado por: SQLiteRegistroRepository (implementação concreta).
    Depende de: nada — camada mais interna, sem dependência de framework.
    """

    @abstractmethod
    def inserir(self, conn: sqlite3.Connection, registro: dict) -> dict:
        """Persiste um novo registro e retorna o dict com o id gerado."""
        ...

    @abstractmethod
    def listar_todos(self, conn: sqlite3.Connection) -> list[dict]:
        """Retorna todos os registros ordenados por data crescente."""
        ...

    @abstractmethod
    def contar(self, conn: sqlite3.Connection) -> int:
        """Retorna o total de registros no banco."""
        ...
