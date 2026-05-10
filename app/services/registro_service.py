from datetime import datetime, timezone

from app.models.registro import RegistroFocoRequest, RegistroFocoResponse
from app.storage.registro_repository import registro_repository

# Mapeamento fixo de nivel_foco (1-5) para rótulo textual.
# Centralizado aqui para que classificar_foco() e _nivel_predominante()
# em diagnostico_service usem a mesma fonte.
_CLASSIFICACOES = {
    1: "Muito Baixo",
    2: "Baixo",
    3: "Moderado",
    4: "Alto",
    5: "Estado de Flow",
}


def classificar_foco(nivel: int) -> str:
    """Converte nivel_foco (int 1-5) em rótulo textual.

    Usado por: processar_registro (campo classificacao_foco no response)
    e diagnostico_service._nivel_predominante.
    """
    return _CLASSIFICACOES.get(nivel, "Desconhecido")


def processar_registro(payload: RegistroFocoRequest, conn) -> RegistroFocoResponse:
    """Converte o payload validado em dict, persiste e retorna o response completo.

    Preenche data automaticamente com UTC se não informada pelo cliente.
    Converte CategoriaEnum para string antes de persistir (SQLite não armazena enums).
    Usado por: routes/registro_foco.py.
    """
    data = payload.data or datetime.now(timezone.utc)

    registro = {
        "nivel_foco": payload.nivel_foco,
        "tempo_minutos": payload.tempo_minutos,
        "comentario": payload.comentario,
        # .value extrai a string do enum; None se categoria não informada
        "categoria": payload.categoria.value if payload.categoria else None,
        "tags": payload.tags or [],
        "data": data.isoformat(),
    }

    salvo = registro_repository.inserir(conn, registro)

    return RegistroFocoResponse(
        id=salvo["id"],
        nivel_foco=salvo["nivel_foco"],
        tempo_minutos=salvo["tempo_minutos"],
        comentario=salvo["comentario"],
        categoria=salvo.get("categoria"),
        tags=salvo.get("tags") or [],
        data=data,
        # classificacao_foco é derivado, não existe no banco
        classificacao_foco=classificar_foco(salvo["nivel_foco"]),
    )
