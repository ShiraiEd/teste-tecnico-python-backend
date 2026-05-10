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

## Decisões de arquitetura

### Spec-driven design
O `openapi.yaml` foi escrito antes de qualquer linha de código Python. Isso inverte o fluxo comum: em vez de documentar o que foi feito, o contrato define o que será feito. O benefício prático é que todas as decisões de nomes de campos, tipos, validações e respostas de erro foram tomadas e revisadas antes da implementação — evitando retrabalho e garantindo que a documentação nunca fique desatualizada em relação ao código.

### FastAPI em vez de Flask ou Django
FastAPI foi escolhido porque integra validação (Pydantic), serialização e documentação automática em uma única camada, sem bibliotecas extras. Para uma API que exige validação rigorosa de campos (`nivel_foco` entre 1 e 5, `tempo_minutos` positivo), isso elimina código de validação manual e entrega respostas de erro 422 com mensagens descritivas automaticamente. Flask exigiria essas validações escritas à mão. Django, por sua vez, traria um ecossistema completo (ORM, admin, autenticação, migrations) pensado para aplicações web maiores — tudo isso seria overhead desnecessário para dois endpoints, além de exigir mais tempo de configuração inicial sem agregar valor ao escopo do projeto.

### SQLite com `sqlite3` puro em vez de ORM
SQLAlchemy ou SQLModel adicionariam abstração útil em projetos maiores, mas para dois endpoints com uma tabela simples o custo de configuração supera o benefício. Usar `sqlite3` puro com queries parametrizadas demonstra domínio direto de SQL, torna o código mais fácil de auditar por segurança (sem mágica de ORM) e mantém o número de dependências no mínimo. A troca de banco de dados no futuro exigiria mudar apenas `storage/database.py`.

### Separação em camadas (routes / services / storage)
A lógica de negócio foi isolada em `services/` sem nenhuma dependência do FastAPI. Isso tem uma consequência direta: os testes unitários em `test_services.py` testam a lógica de diagnóstico (médias, tendência, consistência) sem subir servidor, sem fazer requisições HTTP e sem banco de dados — são instantâneos e determinísticos. Se a lógica estivesse nas rotas, qualquer teste exigiria infraestrutura HTTP completa.

### Middleware de logging
Em vez de adicionar `print()` ou logs espalhados pelo código, um middleware centraliza o registro de todas as requisições com método, path, status code e tempo de resposta. Isso cobre 100% dos endpoints automaticamente e é o padrão de observabilidade mínima em qualquer API em produção — o desenvolvedor vê no terminal exatamente o que está acontecendo sem instrumentar cada rota.

### Rate limiting com slowapi
O endpoint de escrita (`POST /registro-foco`) está sujeito a abuso — um loop simples poderia inserir milhares de registros e degradar o diagnóstico ou encher o disco. O rate limiting por IP (30 req/min) é a camada mais simples de proteção contra isso e exige apenas um decorator na rota, sem infraestrutura adicional.

### Testes em dois níveis
Os testes unitários (`test_services.py`) cobrem a lógica pura com casos de borda precisos — faixas de média, desvio padrão, tendência com dados insuficientes. Os testes de integração (`test_registro_foco.py`, `test_diagnostico.py`) usam o `TestClient` do FastAPI com um banco SQLite em memória isolado por fixture, garantindo que cada teste começa do zero sem interferência entre casos. Essa separação permite identificar rapidamente se um erro é de lógica ou de infraestrutura HTTP.

---

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
