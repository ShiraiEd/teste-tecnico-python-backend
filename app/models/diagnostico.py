from enum import Enum

from pydantic import BaseModel


class TendenciaEnum(str, Enum):
    melhora = "melhora"
    piora = "piora"
    estavel = "estavel"
    dados_insuficientes = "dados_insuficientes"


class DiagnosticoResponse(BaseModel):
    total_registros: int
    media_foco: float
    tempo_total_minutos: int
    tempo_total_horas: float
    nivel_predominante: str
    distribuicao_categorias: dict[str, int]
    top_tags: list[str]
    feedback: str
    sugestoes: list[str]
    indice_consistencia: float
    tendencia: TendenciaEnum
