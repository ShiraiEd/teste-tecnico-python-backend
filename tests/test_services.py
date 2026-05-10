from app.services.registro_service import classificar_foco
from app.services.diagnostico_service import (
    _indice_consistencia,
    _tendencia,
    _feedback,
    _streak_dias,
    _distribuicao_categorias,
    _top_tags,
    _nivel_predominante,
)
from app.services.regras_diagnostico import (
    DadosDiagnostico,
    FocoBaixo,
    SessoesLongas,
    FocoAltoInconsistente,
    ReunioesDominantes,
    TendenciaDePiora,
    TudoOtimo,
    aplicar_regras,
)
from app.models.diagnostico import TendenciaEnum


# --- classificar_foco ---


def test_classificar_foco_limites():
    assert classificar_foco(1) == "Muito Baixo"
    assert classificar_foco(5) == "Estado de Flow"


def test_classificar_foco_intermediarios():
    assert classificar_foco(2) == "Baixo"
    assert classificar_foco(3) == "Moderado"
    assert classificar_foco(4) == "Alto"


# --- indice_consistencia ---


def test_indice_consistencia_perfeito():
    assert _indice_consistencia([5, 5, 5, 5]) == 1.0


def test_indice_consistencia_um_registro():
    assert _indice_consistencia([3]) == 1.0


def test_indice_consistencia_erratico():
    indice = _indice_consistencia([1, 5, 1, 5, 1, 5])
    assert 0.0 <= indice < 0.5


# --- tendencia ---


def test_tendencia_melhora():
    registros = [
        {"nivel_foco": 2},
        {"nivel_foco": 2},
        {"nivel_foco": 5},
        {"nivel_foco": 5},
    ]
    assert _tendencia(registros) == TendenciaEnum.melhora


def test_tendencia_piora():
    registros = [
        {"nivel_foco": 5},
        {"nivel_foco": 5},
        {"nivel_foco": 2},
        {"nivel_foco": 2},
    ]
    assert _tendencia(registros) == TendenciaEnum.piora


def test_tendencia_estavel():
    registros = [
        {"nivel_foco": 3},
        {"nivel_foco": 3},
        {"nivel_foco": 3},
        {"nivel_foco": 3},
    ]
    assert _tendencia(registros) == TendenciaEnum.estavel


def test_tendencia_dados_insuficientes():
    registros = [{"nivel_foco": 4}, {"nivel_foco": 3}]
    assert _tendencia(registros) == TendenciaEnum.dados_insuficientes


# --- feedback: todas as 6 faixas ---


def test_feedback_faixa_critica():
    assert "fragmentado" in _feedback(1.9).lower()


def test_feedback_faixa_abaixo_ideal():
    assert "abaixo do ideal" in _feedback(2.5).lower()


def test_feedback_faixa_moderado():
    assert "moderado" in _feedback(3.2).lower()


def test_feedback_faixa_bom_ritmo():
    assert "bom ritmo" in _feedback(3.7).lower()


def test_feedback_faixa_alta_performance():
    assert "alta performance" in _feedback(4.2).lower()


def test_feedback_faixa_flow():
    assert "flow" in _feedback(4.5).lower()


# --- nivel_predominante ---


def test_nivel_predominante_mais_frequente():
    niveis = [3, 3, 3, 5, 5]
    assert _nivel_predominante(niveis) == "Moderado"


def test_nivel_predominante_unico():
    assert _nivel_predominante([5]) == "Estado de Flow"


# --- distribuicao_categorias ---


def test_distribuicao_categorias_agrupa_corretamente():
    registros = [
        {"categoria": "coding"},
        {"categoria": "coding"},
        {"categoria": "reuniao"},
        {"categoria": None},
    ]
    dist = _distribuicao_categorias(registros)
    assert dist == {"coding": 2, "reuniao": 1}


def test_distribuicao_categorias_sem_categoria():
    registros = [{"categoria": None}, {"categoria": None}]
    assert _distribuicao_categorias(registros) == {}


# --- top_tags ---


def test_top_tags_ordena_por_frequencia():
    registros = [
        {"tags": ["python", "fastapi"]},
        {"tags": ["python", "sqlite"]},
        {"tags": ["python"]},
    ]
    tags = _top_tags(registros)
    assert tags[0] == "python"
    assert "fastapi" in tags
    assert "sqlite" in tags


def test_top_tags_sem_tags():
    registros = [{"tags": []}, {"tags": None}]
    assert _top_tags(registros) == []


def test_top_tags_limita_ao_top_n():
    registros = [{"tags": [f"tag{i}" for i in range(10)]}]
    assert len(_top_tags(registros, top_n=5)) == 5


# --- streak_dias ---


def _reg(data: str) -> dict:
    return {"nivel_foco": 3, "tempo_minutos": 30, "comentario": "x", "data": data}


def test_streak_dias_consecutivos():
    registros = [
        _reg("2026-05-01T10:00:00"),
        _reg("2026-05-02T10:00:00"),
        _reg("2026-05-03T10:00:00"),
    ]
    assert _streak_dias(registros) == 3


def test_streak_dias_com_lacuna():
    registros = [
        _reg("2026-05-01T10:00:00"),
        _reg("2026-05-03T10:00:00"),
        _reg("2026-05-04T10:00:00"),
    ]
    assert _streak_dias(registros) == 2


def test_streak_dias_unico_registro():
    assert _streak_dias([_reg("2026-05-01T10:00:00")]) == 1


def test_streak_dias_duplicados_mesmo_dia():
    registros = [
        _reg("2026-05-01T09:00:00"),
        _reg("2026-05-01T14:00:00"),
        _reg("2026-05-02T10:00:00"),
    ]
    assert _streak_dias(registros) == 2


# --- Specification Pattern: regras individuais ---


def _dados(**kwargs) -> DadosDiagnostico:
    defaults = dict(
        media=3.5,
        media_tempo=50,
        desvio=0.5,
        tendencia=TendenciaEnum.estavel,
        pct_reuniao=0.1,
        indice_consistencia=0.8,
    )
    return DadosDiagnostico(**{**defaults, **kwargs})


def test_regra_foco_baixo_satisfeita():
    assert FocoBaixo().satisfeita(_dados(media=2.9))


def test_regra_foco_baixo_nao_satisfeita():
    assert not FocoBaixo().satisfeita(_dados(media=3.0))


def test_regra_sessoes_longas_satisfeita():
    assert SessoesLongas().satisfeita(_dados(media_tempo=91))


def test_regra_sessoes_longas_nao_satisfeita():
    assert not SessoesLongas().satisfeita(_dados(media_tempo=90))


def test_regra_foco_alto_inconsistente_satisfeita():
    assert FocoAltoInconsistente().satisfeita(_dados(media=4.5, desvio=1.3))


def test_regra_foco_alto_inconsistente_nao_satisfeita_desvio():
    assert not FocoAltoInconsistente().satisfeita(_dados(media=4.5, desvio=1.0))


def test_regra_reunioes_dominantes_satisfeita():
    assert ReunioesDominantes().satisfeita(_dados(pct_reuniao=0.41))


def test_regra_tendencia_piora_satisfeita():
    assert TendenciaDePiora().satisfeita(_dados(tendencia=TendenciaEnum.piora))


def test_regra_tudo_otimo_satisfeita():
    assert TudoOtimo().satisfeita(_dados(media=4.5, indice_consistencia=0.8))


def test_regra_tudo_otimo_nao_satisfeita_indice():
    assert not TudoOtimo().satisfeita(_dados(media=4.5, indice_consistencia=0.6))


# --- aplicar_regras ---


def test_aplicar_regras_sem_disparo_retorna_padrao():
    dados = _dados(
        media=3.5,
        media_tempo=50,
        desvio=0.5,
        tendencia=TendenciaEnum.estavel,
        pct_reuniao=0.1,
        indice_consistencia=0.5,
    )
    resultado = aplicar_regras(dados)
    assert len(resultado) == 1
    assert "registrando" in resultado[0].lower()


def test_aplicar_regras_multiplas_disparam():
    dados = _dados(
        media=2.5,
        media_tempo=95,
        desvio=0.3,
        tendencia=TendenciaEnum.piora,
        pct_reuniao=0.1,
        indice_consistencia=0.5,
    )
    resultado = aplicar_regras(dados)
    assert len(resultado) >= 3
