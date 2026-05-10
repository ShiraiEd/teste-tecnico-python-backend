from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CategoriaEnum(str, Enum):
    coding = "coding"
    reuniao = "reuniao"
    estudo = "estudo"
    leitura = "leitura"
    planejamento = "planejamento"


class RegistroFocoRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nivel_foco: int = Field(..., ge=1, le=5, description="1 = muito distraído, 5 = estado de flow")
    tempo_minutos: int = Field(..., ge=1, description="Duração da sessão em minutos")
    comentario: str = Field(..., min_length=1, max_length=500)
    categoria: Optional[CategoriaEnum] = None
    tags: Optional[list[str]] = Field(default=None, max_length=10)
    data: Optional[datetime] = None


class RegistroFocoResponse(BaseModel):
    id: int
    nivel_foco: int
    tempo_minutos: int
    comentario: str
    categoria: Optional[CategoriaEnum] = None
    tags: list[str] = []
    data: datetime
    classificacao_foco: str
