# Plano: API de Log de Performance (FastAPI + Spec-Driven)

> Artefato gerado com auxílio do Claude Code (Anthropic) durante a fase de planejamento.

## Contexto
Teste técnico de backend Python. Construir uma API de "Log de Performance" com 2 endpoints usando spec-driven design: escrever o contrato OpenAPI primeiro, depois implementar o código que o satisfaz. Framework: FastAPI. Storage: SQLite puro (sqlite3, sem ORM).

---

## Estrutura de Pastas

```
teste-tecnico-python-backend/
├── openapi.yaml
├── requirements.txt
├── requirements-dev.txt
├── CLAUDE.md
├── .gitignore
├── docs/
│   └── plano.md
├── app/
│   ├── main.py
│   ├── models/
│   │   ├── registro.py
│   │   └── diagnostico.py
│   ├── routes/
│   │   ├── registro_foco.py
│   │   └── diagnostico.py
│   ├── services/
│   │   ├── registro_service.py
│   │   └── diagnostico_service.py
│   └── storage/
│       ├── database.py
│       └── registro_repository.py
└── tests/
    ├── conftest.py
    ├── test_registro_foco.py
    ├── test_diagnostico.py
    └── test_services.py
```

---

## Ordem de Implementação

```
Etapa 0 - Artefatos de planejamento
  1. docs/plano.md
  2. CLAUDE.md
  3. openapi.yaml           ← contrato da API (spec-first)
  4. requirements.txt
  5. requirements-dev.txt
  6. .gitignore

Etapa 1 - Infraestrutura de dados
  7. app/storage/database.py
  8. app/storage/registro_repository.py

Etapa 2 - Modelos Pydantic (derivados do openapi.yaml)
  9. app/models/registro.py
 10. app/models/diagnostico.py

Etapa 3 - Serviços (lógica pura, testável sem FastAPI)
 11. app/services/registro_service.py
 12. app/services/diagnostico_service.py

Etapa 4 - Rotas
 13. app/routes/registro_foco.py
 14. app/routes/diagnostico.py

Etapa 5 - Ponto de entrada
 15. app/main.py

Etapa 6 - Testes
 16. tests/conftest.py
 17. tests/test_services.py
 18. tests/test_registro_foco.py
 19. tests/test_diagnostico.py

Etapa 7 - Documentação
 20. README.md
```

---

## Campos da API

### POST /registro-foco — Request
| Campo | Tipo | Obrigatório | Detalhe |
|---|---|---|---|
| nivel_foco | int (1–5) | Sim | 1=distraído, 5=flow |
| tempo_minutos | int (≥1) | Sim | duração da sessão |
| comentario | str (1–500) | Sim | o que foi feito |
| categoria | enum | Não | coding, reuniao, estudo, leitura, planejamento |
| tags | list[str] | Não | max 10 |
| data | datetime | Não | preenchido automaticamente se omitido |

### POST /registro-foco — Response (201)
Mesmos campos + `id: int` + `classificacao_foco: str` (rótulo textual do nível)

### GET /diagnostico-produtividade — Response (200)
| Campo | Tipo | Descrição |
|---|---|---|
| total_registros | int | |
| media_foco | float | média aritmética |
| tempo_total_minutos | int | soma total |
| tempo_total_horas | float | calculado |
| nivel_predominante | str | nível mais frequente |
| distribuicao_categorias | dict[str, int] | contagem por categoria |
| top_tags | list[str] | top 5 tags |
| feedback | str | mensagem principal |
| sugestoes | list[str] | sugestões personalizadas |
| indice_consistencia | float (0–1) | 1.0 = estável, 0.0 = errático |
| tendencia | enum | melhora / piora / estavel / dados_insuficientes |

---

## Lógica de Diagnóstico

### Faixas de feedback
- `< 2.0` → "Foco fragmentado, precisa de atenção urgente."
- `2.0–3.0` → "Abaixo do ideal. Pequenas mudanças de ambiente ajudam."
- `3.0–3.5` → "Foco moderado. Há espaço para crescer."
- `3.5–4.0` → "Bom ritmo! Perto do seu melhor."
- `4.0–4.5` → "Alta performance!"
- `≥ 4.5` → "Maratona produtiva de alto nível! Estado de flow consistente."

### Sugestões dinâmicas (regras independentes)
- média < 3 → Pomodoro + modo Não Perturbe
- sessões > 90 min em média → pausas a cada 50 min
- foco alto mas inconsistente (média > 4, desvio > 1.2) → identificar padrão dos melhores dias
- reuniao > 40% do tempo → avaliar reuniões desnecessárias
- tendência de piora → revisar carga e sono
- tudo ótimo → documentar a rotina

### Índice de Consistência
```python
indice = round(max(0.0, 1.0 - (statistics.stdev(niveis) / 2.0)), 2)
```

### Tendência
Compara média da 1ª metade dos registros com a 2ª metade. delta > 0.3 = melhora, < -0.3 = piora.

---

## Segurança
| Camada | Proteção | Onde |
|---|---|---|
| Validação de input | Pydantic | automático |
| SQL Injection | Queries parametrizadas com `?` | registro_repository.py |
| Exposição de erros | Handler global 500 sem stack trace | main.py |
| Rate Limiting | slowapi: 30 POST/min por IP | routes/registro_foco.py |
| CORS | Origens específicas | main.py |

## Observabilidade
Middleware de logging em `main.py` — loga método, path, status e duração. Zero dependências extras.

## Testes
- Unitários: serviços testados sem HTTP
- Integração: TestClient do FastAPI com banco SQLite em memória isolado por fixture
