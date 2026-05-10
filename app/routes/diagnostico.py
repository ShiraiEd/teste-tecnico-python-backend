from fastapi import APIRouter, Depends, HTTPException

from app.models.diagnostico import DiagnosticoResponse
from app.services import diagnostico_service
from app.storage import registro_repository
from app.storage.database import db_session

router = APIRouter(tags=["Diagnóstico"])


def get_conn():
    with db_session() as conn:
        yield conn


@router.get("/diagnostico-produtividade", response_model=DiagnosticoResponse)
def obter_diagnostico(conn=Depends(get_conn)):
    registros = registro_repository.listar_todos(conn)
    if not registros:
        raise HTTPException(
            status_code=404,
            detail="Nenhum registro encontrado. Comece registrando sua primeira sessão.",
        )
    return diagnostico_service.calcular(registros)
