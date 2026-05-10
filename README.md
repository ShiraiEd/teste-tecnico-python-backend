# API de Log de Performance

Backend de um "Log de Performance" para registrar sessões de trabalho e obter um diagnóstico inteligente de produtividade.

## Tecnologias

- **Python 3.x** + **FastAPI**
- **SQLite** (via `sqlite3` puro, sem ORM)
- **Pydantic v2** para validação
- **slowapi** para rate limiting

## Como rodar

```bash
# 1. Clonar e entrar no diretório
git clone <url-do-repositorio>
cd teste-tecnico-python-backend

# 2. Criar e ativar o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\activate    # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Iniciar o servidor
uvicorn app.main:app --reload --port 8000
```

Acesse a documentação interativa em: http://localhost:8000/docs

## Como testar

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

## Endpoints

### `POST /registro-foco`

Registra uma sessão de trabalho.

**Body (JSON):**

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `nivel_foco` | int (1–5) | Sim | 1 = muito distraído, 5 = estado de flow |
| `tempo_minutos` | int (≥1) | Sim | Duração da sessão em minutos |
| `comentario` | string | Sim | O que foi feito ou o que causou distração |
| `categoria` | string | Não | `coding`, `reuniao`, `estudo`, `leitura`, `planejamento` |
| `tags` | list[string] | Não | Até 10 tags livres |
| `data` | datetime | Não | Preenchido automaticamente se omitido |

**Exemplo:**

```bash
curl -X POST http://localhost:8000/registro-foco \
  -H "Content-Type: application/json" \
  -d '{
    "nivel_foco": 4,
    "tempo_minutos": 50,
    "comentario": "Implementei a rota de diagnóstico sem interrupções",
    "categoria": "coding",
    "tags": ["fastapi", "python", "sqlite"]
  }'
```

**Response (201):**

```json
{
  "id": 1,
  "nivel_foco": 4,
  "tempo_minutos": 50,
  "comentario": "Implementei a rota de diagnóstico sem interrupções",
  "categoria": "coding",
  "tags": ["fastapi", "python", "sqlite"],
  "data": "2026-05-10T14:00:00Z",
  "classificacao_foco": "Alto"
}
```

---

### `GET /diagnostico-produtividade`

Retorna um resumo inteligente baseado em todos os registros.

**Exemplo:**

```bash
curl http://localhost:8000/diagnostico-produtividade
```

**Response (200):**

```json
{
  "total_registros": 10,
  "media_foco": 3.8,
  "tempo_total_minutos": 480,
  "tempo_total_horas": 8.0,
  "nivel_predominante": "Alto",
  "distribuicao_categorias": {"coding": 6, "reuniao": 3, "estudo": 1},
  "top_tags": ["python", "fastapi", "sqlite"],
  "feedback": "Bom ritmo! Você está produtivo e próximo do seu melhor.",
  "sugestoes": ["Reuniões dominam seu tempo. Avalie quais poderiam ser substituídas por e-mails."],
  "indice_consistencia": 0.75,
  "tendencia": "melhora"
}
```

## Estrutura do projeto

```
app/
├── main.py                  # Ponto de entrada (FastAPI, middlewares, routers)
├── models/
│   ├── registro.py          # Schemas Pydantic do registro
│   └── diagnostico.py       # Schema Pydantic do diagnóstico
├── routes/
│   ├── registro_foco.py     # POST /registro-foco
│   └── diagnostico.py       # GET /diagnostico-produtividade
├── services/
│   ├── registro_service.py  # Lógica de registro e classificação
│   └── diagnostico_service.py  # Lógica de diagnóstico (média, tendência, consistência)
└── storage/
    ├── database.py          # Conexão SQLite e DDL
    └── registro_repository.py  # Queries SQL
docs/
└── plano.md                 # Plano de arquitetura gerado com IA
tests/
├── conftest.py
├── test_services.py         # Testes unitários dos serviços
├── test_registro_foco.py    # Testes de integração do POST
└── test_diagnostico.py      # Testes de integração do GET
openapi.yaml                 # Contrato da API (spec-first)
CLAUDE.md                    # Instruções para Claude Code
```

## Segurança

- Validação automática de todos os campos via Pydantic (tipos, ranges, tamanhos)
- Rate limiting: 30 requisições/minuto por IP no endpoint de escrita
- Queries SQL sempre parametrizadas (sem interpolação de string)
- Erros internos não expõem stack traces

## Uso de IA

Este projeto foi desenvolvido com auxílio do **Claude Code** (Anthropic).

O fluxo utilizado foi **spec-driven design**:
1. Planejamento da arquitetura e contrato da API com IA (`docs/plano.md`)
2. Escrita do `openapi.yaml` como contrato antes do código
3. Implementação guiada pelo contrato
4. Geração e revisão dos testes

Os artefatos gerados estão incluídos no repositório conforme solicitado: `docs/plano.md`, `openapi.yaml` e `CLAUDE.md`.
