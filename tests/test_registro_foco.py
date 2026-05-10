PAYLOAD_VALIDO = {
    "nivel_foco": 4,
    "tempo_minutos": 50,
    "comentario": "Implementando a rota de diagnóstico",
    "categoria": "coding",
    "tags": ["fastapi", "python"],
}


def test_criar_registro_valido(client):
    response = client.post("/registro-foco", json=PAYLOAD_VALIDO)
    assert response.status_code == 201
    data = response.json()
    assert data["nivel_foco"] == 4
    assert data["classificacao_foco"] == "Alto"
    assert "id" in data


def test_criar_registro_sem_opcionais(client):
    payload = {
        "nivel_foco": 3,
        "tempo_minutos": 30,
        "comentario": "Sessão básica",
    }
    response = client.post("/registro-foco", json=payload)
    assert response.status_code == 201


def test_nivel_foco_abaixo_do_minimo(client):
    payload = {**PAYLOAD_VALIDO, "nivel_foco": 0}
    response = client.post("/registro-foco", json=payload)
    assert response.status_code == 422


def test_nivel_foco_acima_do_maximo(client):
    payload = {**PAYLOAD_VALIDO, "nivel_foco": 6}
    response = client.post("/registro-foco", json=payload)
    assert response.status_code == 422


def test_tempo_minutos_zero(client):
    payload = {**PAYLOAD_VALIDO, "tempo_minutos": 0}
    response = client.post("/registro-foco", json=payload)
    assert response.status_code == 422


def test_tempo_minutos_negativo(client):
    payload = {**PAYLOAD_VALIDO, "tempo_minutos": -10}
    response = client.post("/registro-foco", json=payload)
    assert response.status_code == 422


def test_comentario_vazio(client):
    payload = {**PAYLOAD_VALIDO, "comentario": ""}
    response = client.post("/registro-foco", json=payload)
    assert response.status_code == 422


def test_classificacao_foco_no_response(client):
    for nivel, esperado in [(1, "Muito Baixo"), (3, "Moderado"), (5, "Estado de Flow")]:
        payload = {**PAYLOAD_VALIDO, "nivel_foco": nivel}
        response = client.post("/registro-foco", json=payload)
        assert response.json()["classificacao_foco"] == esperado
