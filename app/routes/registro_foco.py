import os

from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.models.registro import RegistroFocoRequest, RegistroFocoResponse
from app.services import registro_service
from app.storage.database import db_session

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(tags=["Registro"])

_rate_limit = f"{os.getenv('RATE_LIMIT', '30')}/minute"


def get_conn():
    with db_session() as conn:
        yield conn


@router.post("/registro-foco", response_model=RegistroFocoResponse, status_code=201)
@limiter.limit(_rate_limit)
def criar_registro(
    request: Request, payload: RegistroFocoRequest, conn=Depends(get_conn)
):
    return registro_service.processar_registro(payload, conn)
