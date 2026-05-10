from app.services.registro_service import classificar_foco
from app.services.diagnostico_service import (
    _indice_consistencia,
    _tendencia,
    _feedback,
)
from app.models.diagnostico import TendenciaEnum


def test_classificar_foco_limites():
    assert classificar_foco(1) == "Muito Baixo"
    assert classificar_foco(5) == "Estado de Flow"


def test_classificar_foco_intermediarios():
    assert classificar_foco(2) == "Baixo"
    assert classificar_foco(3) == "Moderado"
    assert classificar_foco(4) == "Alto"


def test_indice_consistencia_perfeito():
    assert _indice_consistencia([5, 5, 5, 5]) == 1.0


def test_indice_consistencia_um_registro():
    assert _indice_consistencia([3]) == 1.0


def test_indice_consistencia_erratico():
    indice = _indice_consistencia([1, 5, 1, 5, 1, 5])
    assert 0.0 <= indice < 0.5


def test_tendencia_melhora():
    registros = [
        {"nivel_foco": 2}, {"nivel_foco": 2},
        {"nivel_foco": 5}, {"nivel_foco": 5},
    ]
    assert _tendencia(registros) == TendenciaEnum.melhora


def test_tendencia_piora():
    registros = [
        {"nivel_foco": 5}, {"nivel_foco": 5},
        {"nivel_foco": 2}, {"nivel_foco": 2},
    ]
    assert _tendencia(registros) == TendenciaEnum.piora


def test_tendencia_estavel():
    registros = [
        {"nivel_foco": 3}, {"nivel_foco": 3},
        {"nivel_foco": 3}, {"nivel_foco": 3},
    ]
    assert _tendencia(registros) == TendenciaEnum.estavel


def test_tendencia_dados_insuficientes():
    registros = [{"nivel_foco": 4}, {"nivel_foco": 3}]
    assert _tendencia(registros) == TendenciaEnum.dados_insuficientes


def test_feedback_faixas():
    assert "fragmentado" in _feedback(1.5).lower()
    assert "moderado" in _feedback(3.2).lower()
    assert "flow" in _feedback(5.0).lower()
