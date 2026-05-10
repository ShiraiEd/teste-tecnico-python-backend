import json
import statistics
from collections import Counter

from app.models.diagnostico import DiagnosticoResponse, TendenciaEnum


def _feedback(media: float) -> str:
    if media < 2.0:
        return "Semana de turbulências. Seu foco está fragmentado e precisa de atenção urgente."
    if media < 3.0:
        return "Foco abaixo do ideal. Pequenas mudanças de ambiente podem fazer grande diferença."
    if media < 3.5:
        return "Foco moderado. Você está funcionando, mas há espaço para crescer."
    if media < 4.0:
        return "Bom ritmo! Você está produtivo e próximo do seu melhor."
    if media < 4.5:
        return "Excelente! Você está em modo de alta performance."
    return "Maratona produtiva de alto nível! Você atingiu estado de flow consistente."


def _sugestoes(media: float, media_tempo: float, desvio: float, tendencia: TendenciaEnum, pct_reuniao: float, indice: float) -> list[str]:
    result = []

    if media < 3.0:
        result.append("Experimente sessões mais curtas com a técnica Pomodoro (25 min).")
        result.append("Reduza notificações e use modo 'Não Perturbe' durante as sessões.")

    if media_tempo > 90:
        result.append("Sessões muito longas prejudicam o foco. Considere pausas a cada 50 minutos.")

    if media > 4.0 and desvio > 1.2:
        result.append("Seu foco é alto mas oscilante. Identifique o que diferencia seus melhores dias.")

    if pct_reuniao > 0.4:
        result.append("Reuniões dominam seu tempo. Avalie quais poderiam ser substituídas por e-mails.")

    if tendencia == TendenciaEnum.piora:
        result.append("Sua produtividade está caindo. Revise sua carga de trabalho e qualidade do sono.")

    if media >= 4.5 and indice > 0.7:
        result.append("Você está num ciclo virtuoso! Documente sua rotina para replicar esse resultado.")

    if not result:
        result.append("Continue registrando suas sessões para receber sugestões personalizadas.")

    return result


def _indice_consistencia(niveis: list[int]) -> float:
    if len(niveis) < 2:
        return 1.0
    desvio = statistics.stdev(niveis)
    return round(max(0.0, 1.0 - (desvio / 2.0)), 2)


def _tendencia(registros: list[dict]) -> TendenciaEnum:
    niveis = [r["nivel_foco"] for r in registros]
    if len(niveis) < 4:
        return TendenciaEnum.dados_insuficientes
    metade = len(niveis) // 2
    media_antiga = statistics.mean(niveis[:metade])
    media_recente = statistics.mean(niveis[metade:])
    delta = media_recente - media_antiga
    if delta > 0.3:
        return TendenciaEnum.melhora
    if delta < -0.3:
        return TendenciaEnum.piora
    return TendenciaEnum.estavel


def _distribuicao_categorias(registros: list[dict]) -> dict[str, int]:
    categorias = [r["categoria"] for r in registros if r.get("categoria")]
    return dict(Counter(categorias))


def _top_tags(registros: list[dict], top_n: int = 5) -> list[str]:
    todas = []
    for r in registros:
        tags = r.get("tags") or []
        if isinstance(tags, str):
            tags = json.loads(tags)
        todas.extend(tags)
    return [tag for tag, _ in Counter(todas).most_common(top_n)]


def _nivel_predominante(niveis: list[int]) -> str:
    from app.services.registro_service import classificar_foco
    nivel = Counter(niveis).most_common(1)[0][0]
    return classificar_foco(nivel)


def calcular(registros: list[dict]) -> DiagnosticoResponse:
    niveis = [r["nivel_foco"] for r in registros]
    tempos = [r["tempo_minutos"] for r in registros]

    media = round(statistics.mean(niveis), 2)
    desvio = statistics.stdev(niveis) if len(niveis) > 1 else 0.0
    total_minutos = sum(tempos)
    media_tempo = statistics.mean(tempos)
    indice = _indice_consistencia(niveis)
    tendencia = _tendencia(registros)
    dist_cat = _distribuicao_categorias(registros)

    tempo_total_reuniao = sum(
        r["tempo_minutos"] for r in registros if r.get("categoria") == "reuniao"
    )
    pct_reuniao = tempo_total_reuniao / total_minutos if total_minutos > 0 else 0.0

    return DiagnosticoResponse(
        total_registros=len(registros),
        media_foco=media,
        tempo_total_minutos=total_minutos,
        tempo_total_horas=round(total_minutos / 60, 2),
        nivel_predominante=_nivel_predominante(niveis),
        distribuicao_categorias=dist_cat,
        top_tags=_top_tags(registros),
        feedback=_feedback(media),
        sugestoes=_sugestoes(media, media_tempo, desvio, tendencia, pct_reuniao, indice),
        indice_consistencia=indice,
        tendencia=tendencia,
    )
