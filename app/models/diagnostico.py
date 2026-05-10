from enum import Enum

from pydantic import BaseModel


class TendenciaEnum(str, Enum):
    """Resultado da análise temporal de evolução do foco.

    Calculado em diagnostico_service._tendencia() comparando a média
    da primeira metade dos registros com a segunda metade.
    Usado em: DiagnosticoResponse, regras_diagnostico.TendenciaDePiora.
    """

    melhora = "melhora"
    piora = "piora"
    estavel = "estavel"
    dados_insuficientes = "dados_insuficientes"  # menos de 4 registros


class DiagnosticoResponse(BaseModel):
    """Schema de saída do GET /diagnostico-produtividade.

    Todos os campos são calculados em diagnostico_service.calcular()
    a partir da lista completa de registros.
    Usado por: routes/diagnostico.py.
    """

    total_registros: int
    media_foco: float  # média aritmética de nivel_foco
    tempo_total_minutos: int  # soma de tempo_minutos
    tempo_total_horas: float  # tempo_total_minutos / 60
    nivel_predominante: str  # nível com maior frequência, como string (ex: "Alto")
    distribuicao_categorias: dict[str, int]  # contagem de registros por categoria
    top_tags: list[str]  # até 5 tags mais usadas, por frequência
    feedback: str  # mensagem principal baseada na faixa de media_foco
    sugestoes: list[str]  # geradas pelo motor de regras (regras_diagnostico)
    indice_consistencia: float  # 0.0 = foco errático, 1.0 = foco estável
    tendencia: TendenciaEnum
    streak_dias: int  # maior sequência de dias consecutivos com registros
