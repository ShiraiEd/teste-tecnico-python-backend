from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CategoriaEnum(str, Enum):
    """Categorias válidas para uma sessão de trabalho.

    Usado em: RegistroFocoRequest, RegistroFocoResponse,
    e na lógica de distribuicao_categorias do diagnostico_service.
    """

    coding = "coding"
    reuniao = "reuniao"
    estudo = "estudo"
    leitura = "leitura"
    planejamento = "planejamento"


class RegistroFocoRequest(BaseModel):
    """Schema de entrada do POST /registro-foco.

    str_strip_whitespace garante que comentarios com apenas espaços
    sejam rejeitados pelo min_length=1 após o strip.
    Usado por: routes/registro_foco.py.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    nivel_foco: int = Field(
        ..., ge=1, le=5, description="1 = muito distraído, 5 = estado de flow"
    )
    tempo_minutos: int = Field(..., ge=1, description="Duração da sessão em minutos")
    comentario: str = Field(..., min_length=1, max_length=500)
    categoria: Optional[CategoriaEnum] = None
    tags: Optional[list[str]] = Field(default=None, max_length=10)
    # Se omitido, preenchido automaticamente com datetime.now(UTC) em registro_service
    data: Optional[datetime] = None


class RegistroFocoResponse(BaseModel):
    """Schema de saída do POST /registro-foco.

    Inclui classificacao_foco, campo derivado de nivel_foco que não existe
    no banco — calculado em registro_service.classificar_foco() antes de retornar.
    Usado por: routes/registro_foco.py.
    """

    id: int
    nivel_foco: int
    tempo_minutos: int
    comentario: str
    categoria: Optional[CategoriaEnum] = None
    tags: list[str] = []
    data: datetime
    classificacao_foco: str  # ex: "Alto", "Estado de Flow"
