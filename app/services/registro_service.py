from datetime import datetime, timezone

from app.models.registro import RegistroFocoRequest, RegistroFocoResponse
from app.storage import registro_repository


_CLASSIFICACOES = {
    1: "Muito Baixo",
    2: "Baixo",
    3: "Moderado",
    4: "Alto",
    5: "Estado de Flow",
}


def classificar_foco(nivel: int) -> str:
    return _CLASSIFICACOES.get(nivel, "Desconhecido")


def processar_registro(payload: RegistroFocoRequest, conn) -> RegistroFocoResponse:
    data = payload.data or datetime.now(timezone.utc)

    registro = {
        "nivel_foco": payload.nivel_foco,
        "tempo_minutos": payload.tempo_minutos,
        "comentario": payload.comentario,
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
        classificacao_foco=classificar_foco(salvo["nivel_foco"]),
    )
