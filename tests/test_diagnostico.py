PAYLOAD_BASE = {
    "nivel_foco": 4,
    "tempo_minutos": 60,
    "comentario": "Sessão de teste",
    "categoria": "coding",
}


def test_diagnostico_sem_registros(client):
    response = client.get("/diagnostico-produtividade")
    assert response.status_code == 404


def test_diagnostico_com_registros(client):
    client.post("/registro-foco", json=PAYLOAD_BASE)
    response = client.get("/diagnostico-produtividade")
    assert response.status_code == 200
    data = response.json()
    assert "media_foco" in data
    assert "feedback" in data
    assert "sugestoes" in data
    assert "tendencia" in data


def test_media_foco_calculada_corretamente(client):
    client.post("/registro-foco", json={**PAYLOAD_BASE, "nivel_foco": 2})
    client.post("/registro-foco", json={**PAYLOAD_BASE, "nivel_foco": 4})
    response = client.get("/diagnostico-produtividade")
    assert response.json()["media_foco"] == 3.0


def test_tempo_total_calculado(client):
    client.post("/registro-foco", json={**PAYLOAD_BASE, "tempo_minutos": 30})
    client.post("/registro-foco", json={**PAYLOAD_BASE, "tempo_minutos": 90})
    data = client.get("/diagnostico-produtividade").json()
    assert data["tempo_total_minutos"] == 120
    assert data["tempo_total_horas"] == 2.0


def test_tendencia_dados_insuficientes(client):
    client.post("/registro-foco", json=PAYLOAD_BASE)
    data = client.get("/diagnostico-produtividade").json()
    assert data["tendencia"] == "dados_insuficientes"


def test_campos_obrigatorios_no_response(client):
    client.post("/registro-foco", json=PAYLOAD_BASE)
    data = client.get("/diagnostico-produtividade").json()
    campos = [
        "total_registros",
        "media_foco",
        "tempo_total_minutos",
        "tempo_total_horas",
        "nivel_predominante",
        "distribuicao_categorias",
        "top_tags",
        "feedback",
        "sugestoes",
        "indice_consistencia",
        "tendencia",
        "streak_dias",
    ]
    for campo in campos:
        assert campo in data, f"Campo ausente: {campo}"


def test_streak_dias_presente_no_response(client):
    client.post("/registro-foco", json=PAYLOAD_BASE)
    data = client.get("/diagnostico-produtividade").json()
    assert isinstance(data["streak_dias"], int)
    assert data["streak_dias"] >= 1
