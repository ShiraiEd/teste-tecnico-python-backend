PAYLOAD_VALIDO = {
    "nivel_foco": 4,
    "tempo_minutos": 50,
    "comentario": "Implementando a rota de diagnóstico",
    "categoria": "coding",
    "tags": ["fastapi", "python"],
}


# --- Happy path ---


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


def test_classificacao_foco_no_response(client):
    for nivel, esperado in [(1, "Muito Baixo"), (3, "Moderado"), (5, "Estado de Flow")]:
        payload = {**PAYLOAD_VALIDO, "nivel_foco": nivel}
        response = client.post("/registro-foco", json=payload)
        assert response.json()["classificacao_foco"] == esperado


# --- Boundary values: limites exatos válidos ---


def test_nivel_foco_minimo_valido(client):
    response = client.post("/registro-foco", json={**PAYLOAD_VALIDO, "nivel_foco": 1})
    assert response.status_code == 201


def test_nivel_foco_maximo_valido(client):
    response = client.post("/registro-foco", json={**PAYLOAD_VALIDO, "nivel_foco": 5})
    assert response.status_code == 201


def test_tempo_minutos_minimo_valido(client):
    response = client.post(
        "/registro-foco", json={**PAYLOAD_VALIDO, "tempo_minutos": 1}
    )
    assert response.status_code == 201


def test_comentario_tamanho_maximo_valido(client):
    response = client.post(
        "/registro-foco", json={**PAYLOAD_VALIDO, "comentario": "x" * 500}
    )
    assert response.status_code == 201


def test_tags_quantidade_maxima_valida(client):
    payload = {**PAYLOAD_VALIDO, "tags": [f"tag{i}" for i in range(10)]}
    response = client.post("/registro-foco", json=payload)
    assert response.status_code == 201


# --- Unhappy path: campos obrigatórios ---


def test_nivel_foco_abaixo_do_minimo(client):
    response = client.post("/registro-foco", json={**PAYLOAD_VALIDO, "nivel_foco": 0})
    assert response.status_code == 422


def test_nivel_foco_negativo(client):
    response = client.post("/registro-foco", json={**PAYLOAD_VALIDO, "nivel_foco": -1})
    assert response.status_code == 422


def test_nivel_foco_acima_do_maximo(client):
    response = client.post("/registro-foco", json={**PAYLOAD_VALIDO, "nivel_foco": 6})
    assert response.status_code == 422


def test_tempo_minutos_zero(client):
    response = client.post(
        "/registro-foco", json={**PAYLOAD_VALIDO, "tempo_minutos": 0}
    )
    assert response.status_code == 422


def test_tempo_minutos_negativo(client):
    response = client.post(
        "/registro-foco", json={**PAYLOAD_VALIDO, "tempo_minutos": -10}
    )
    assert response.status_code == 422


def test_comentario_vazio(client):
    response = client.post("/registro-foco", json={**PAYLOAD_VALIDO, "comentario": ""})
    assert response.status_code == 422


def test_comentario_apenas_espacos(client):
    response = client.post(
        "/registro-foco", json={**PAYLOAD_VALIDO, "comentario": "   "}
    )
    assert response.status_code == 422


def test_comentario_acima_do_tamanho_maximo(client):
    response = client.post(
        "/registro-foco", json={**PAYLOAD_VALIDO, "comentario": "x" * 501}
    )
    assert response.status_code == 422


def test_body_vazio(client):
    response = client.post("/registro-foco", json={})
    assert response.status_code == 422


# --- Unhappy path: campos opcionais com valores inválidos ---


def test_categoria_invalida(client):
    response = client.post(
        "/registro-foco", json={**PAYLOAD_VALIDO, "categoria": "invalida"}
    )
    assert response.status_code == 422


def test_tags_acima_do_limite(client):
    payload = {**PAYLOAD_VALIDO, "tags": [f"tag{i}" for i in range(11)]}
    response = client.post("/registro-foco", json=payload)
    assert response.status_code == 422
