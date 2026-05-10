from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.models.diagnostico import TendenciaEnum


@dataclass
class DadosDiagnostico:
    media: float
    media_tempo: float
    desvio: float
    tendencia: TendenciaEnum
    pct_reuniao: float
    indice_consistencia: float


class EspecificacaoSugestao(ABC):
    """Specification Pattern para regras de sugestão de diagnóstico.

    Cada regra avalia suas condições de forma independente. Todas as
    especificações satisfeitas contribuem para a lista final de sugestões
    — ao contrário do Strategy, onde apenas uma estratégia é selecionada.
    Adicionar uma nova regra significa criar uma nova classe e incluí-la
    em REGRAS, sem modificar nenhum código existente (Open/Closed Principle).
    """

    @abstractmethod
    def satisfeita(self, dados: DadosDiagnostico) -> bool: ...

    @abstractmethod
    def sugestao(self) -> str: ...


class FocoBaixo(EspecificacaoSugestao):
    def satisfeita(self, dados: DadosDiagnostico) -> bool:
        return dados.media < 3.0

    def sugestao(self) -> str:
        return "Experimente sessões mais curtas com a técnica Pomodoro (25 min) e use modo 'Não Perturbe' durante as sessões."


class SessoesLongas(EspecificacaoSugestao):
    def satisfeita(self, dados: DadosDiagnostico) -> bool:
        return dados.media_tempo > 90

    def sugestao(self) -> str:
        return "Sessões muito longas prejudicam o foco. Considere pausas a cada 50 minutos."


class FocoAltoInconsistente(EspecificacaoSugestao):
    def satisfeita(self, dados: DadosDiagnostico) -> bool:
        return dados.media > 4.0 and dados.desvio > 1.2

    def sugestao(self) -> str:
        return "Seu foco é alto mas oscilante. Identifique o que diferencia seus melhores dias."


class ReunioesDominantes(EspecificacaoSugestao):
    def satisfeita(self, dados: DadosDiagnostico) -> bool:
        return dados.pct_reuniao > 0.4

    def sugestao(self) -> str:
        return "Reuniões dominam seu tempo. Avalie quais poderiam ser substituídas por e-mails."


class TendenciaDePiora(EspecificacaoSugestao):
    def satisfeita(self, dados: DadosDiagnostico) -> bool:
        return dados.tendencia == TendenciaEnum.piora

    def sugestao(self) -> str:
        return "Sua produtividade está caindo. Revise sua carga de trabalho e qualidade do sono."


class TudoOtimo(EspecificacaoSugestao):
    def satisfeita(self, dados: DadosDiagnostico) -> bool:
        return dados.media >= 4.5 and dados.indice_consistencia > 0.7

    def sugestao(self) -> str:
        return "Você está num ciclo virtuoso! Documente sua rotina para replicar esse resultado."


REGRAS: list[EspecificacaoSugestao] = [
    FocoBaixo(),
    SessoesLongas(),
    FocoAltoInconsistente(),
    ReunioesDominantes(),
    TendenciaDePiora(),
    TudoOtimo(),
]


def aplicar_regras(dados: DadosDiagnostico) -> list[str]:
    resultado = [r.sugestao() for r in REGRAS if r.satisfeita(dados)]
    return resultado or [
        "Continue registrando suas sessões para receber sugestões personalizadas."
    ]
