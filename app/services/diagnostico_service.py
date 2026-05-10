import json
import statistics
from collections import Counter
from datetime import date

from app.models.diagnostico import DiagnosticoResponse, TendenciaEnum
from app.services.regras_diagnostico import DadosDiagnostico, aplicar_regras
from app.services.registro_service import classificar_foco


def _feedback(media: float) -> str:
    """Retorna a mensagem principal de diagnóstico baseada na faixa de media_foco.

    6 faixas com limites no intervalo [1.0, 5.0].
    Usado por: calcular().
    """
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


def _indice_consistencia(niveis: list[int]) -> float:
    """Mede a previsibilidade do foco via desvio padrão invertido.

    Fórmula: 1 - (stdev / 2.0), limitado ao intervalo [0.0, 1.0].
    O divisor 2.0 normaliza o desvio máximo possível no range 1-5.
    Retorna 1.0 com menos de 2 registros (sem variação mensurável).
    Usado por: calcular().
    """
    if len(niveis) < 2:
        return 1.0
    desvio = statistics.stdev(niveis)
    return round(max(0.0, 1.0 - (desvio / 2.0)), 2)


def _tendencia(registros: list[dict]) -> TendenciaEnum:
    """Compara a média da primeira metade dos registros com a segunda metade.

    delta > 0.3 → melhora, delta < -0.3 → piora, senão → estável.
    Requer mínimo de 4 registros para uma comparação significativa.
    Registros devem estar ordenados por data ASC (garantido por listar_todos).
    Usado por: calcular().
    """
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
    """Conta registros por categoria, ignorando os sem categoria.

    Usado por: calcular() para o campo distribuicao_categorias.
    """
    categorias = [r["categoria"] for r in registros if r.get("categoria")]
    return dict(Counter(categorias))


def _top_tags(registros: list[dict], top_n: int = 5) -> list[str]:
    """Retorna as top_n tags mais frequentes entre todos os registros.

    tags pode chegar como list (após deserialização pelo repository) ou
    como string JSON (fallback defensivo caso venha direto do banco).
    Usado por: calcular().
    """
    todas = []
    for r in registros:
        tags = r.get("tags") or []
        if isinstance(tags, str):
            tags = json.loads(tags)
        todas.extend(tags)
    return [tag for tag, _ in Counter(todas).most_common(top_n)]


def _nivel_predominante(niveis: list[int]) -> str:
    """Retorna o rótulo textual do nível de foco mais frequente.

    Usado por: calcular().
    """
    nivel = Counter(niveis).most_common(1)[0][0]
    return classificar_foco(nivel)


def _streak_dias(registros: list[dict]) -> int:
    """Calcula a maior sequência de dias consecutivos com pelo menos um registro.

    Deduplica datas (múltiplos registros no mesmo dia contam como 1 dia).
    Percorre as datas ordenadas e reinicia o contador quando há lacuna > 1 dia.
    Usado por: calcular().
    """
    datas = sorted(set(date.fromisoformat(r["data"][:10]) for r in registros))
    if not datas:
        return 0
    max_streak = streak = 1
    for i in range(1, len(datas)):
        if (datas[i] - datas[i - 1]).days == 1:
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 1  # lacuna encontrada — reinicia contador
    return max_streak


def calcular(registros: list[dict]) -> DiagnosticoResponse:
    """Orquestra todos os cálculos e retorna o diagnóstico completo.

    Ponto de entrada chamado por routes/diagnostico.py após listar_todos().
    Monta DadosDiagnostico para passar ao motor de regras (aplicar_regras),
    que avalia cada EspecificacaoSugestao de forma independente.
    """
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
    # Proporção do tempo total gasta em reuniões (0.0 a 1.0)
    pct_reuniao = tempo_total_reuniao / total_minutos if total_minutos > 0 else 0.0

    dados = DadosDiagnostico(
        media=media,
        media_tempo=media_tempo,
        desvio=desvio,
        tendencia=tendencia,
        pct_reuniao=pct_reuniao,
        indice_consistencia=indice,
    )

    return DiagnosticoResponse(
        total_registros=len(registros),
        media_foco=media,
        tempo_total_minutos=total_minutos,
        tempo_total_horas=round(total_minutos / 60, 2),
        nivel_predominante=_nivel_predominante(niveis),
        distribuicao_categorias=dist_cat,
        top_tags=_top_tags(registros),
        feedback=_feedback(media),
        sugestoes=aplicar_regras(dados),
        indice_consistencia=indice,
        tendencia=tendencia,
        streak_dias=_streak_dias(registros),
    )
