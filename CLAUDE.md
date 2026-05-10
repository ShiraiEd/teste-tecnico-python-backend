# CLAUDE.md

## Como rodar
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Como testar
```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

## Estrutura
- `openapi.yaml` — contrato da API (fonte da verdade)
- `app/models/` — schemas Pydantic derivados do contrato
- `app/services/` — lógica de negócio pura (sem FastAPI)
- `app/routes/` — handlers HTTP (sem lógica de negócio)
- `app/storage/` — SQLite com sqlite3 puro (repository pattern)

## Convenções
- Lógica de negócio fica em `services/`, nunca em `routes/`
- Queries SQLite sempre parametrizadas com `?` — nunca f-string com input do usuário
- `tags` armazenado como JSON serializado em coluna TEXT
- `data` armazenado como ISO 8601 em coluna TEXT
