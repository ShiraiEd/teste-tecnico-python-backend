# CLAUDE.md

## Como rodar
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # ajuste os valores se necessário
uvicorn app.main:app --reload --port 8000
```

## Como testar
```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

## Estrutura
- `openapi.yaml` — contrato da API (fonte da verdade, escrito antes do código)
- `app/models/` — schemas Pydantic derivados do contrato
- `app/routes/` — handlers HTTP (sem lógica de negócio)
- `app/services/` — lógica de negócio pura (sem FastAPI)
  - `registro_service.py` — classificação e persistência de registros
  - `diagnostico_service.py` — cálculos (média, tendência, consistência, streak)
  - `regras_diagnostico.py` — Specification Pattern para regras de sugestão
- `app/storage/` — SQLite com sqlite3 puro
  - `base_repository.py` — ABC `AbstractRegistroRepository`
  - `registro_repository.py` — `SQLiteRegistroRepository` (implementação concreta)
  - `database.py` — conexão, DDL e context manager
- `tests/` — unitários (lógica pura) e integração (HTTP + banco em memória)

## Variáveis de ambiente
Copie `.env.example` para `.env` antes de rodar. Carregadas via `python-dotenv` no startup de `app/main.py`.

| Variável | Padrão | Onde é usada |
|---|---|---|
| `DB_PATH` | `performance.db` | `app/storage/database.py` |
| `LOG_LEVEL` | `INFO` | `app/main.py` |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:5173` | `app/main.py` |
| `RATE_LIMIT` | `30` | `app/routes/registro_foco.py` |

## Convenções
- Lógica de negócio fica em `services/`, nunca em `routes/`
- Queries SQLite sempre parametrizadas com `?` — nunca f-string com input do usuário
- `tags` armazenado como JSON serializado em coluna TEXT
- `data` armazenado como ISO 8601 em coluna TEXT
- Novas regras de sugestão = nova classe em `regras_diagnostico.py` implementando `EspecificacaoSugestao` + inclusão em `REGRAS` — sem modificar código existente
- Repository acessado sempre via instância `registro_repository` (singleton), nunca instanciado diretamente nas rotas
