# API de Log de Performance

Backend de um "Log de Performance" para registrar sessões de trabalho e obter um diagnóstico inteligente de produtividade.

## Tecnologias

- **Python 3.x** + **FastAPI**
- **SQLite** (via `sqlite3` puro, sem ORM)
- **Pydantic v2** para validação
- **slowapi** para rate limiting
- **python-dotenv** para variáveis de ambiente
- **ruff** para formatação e lint

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

# 4. Configurar variáveis de ambiente
cp .env.example .env  # ajuste os valores se necessário

# 5. Iniciar o servidor
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
  "tendencia": "melhora",
  "streak_dias": 3
}
```

## Estrutura do projeto

```
app/
├── main.py                     # Ponto de entrada (FastAPI, middlewares, routers)
├── models/
│   ├── registro.py             # Schemas Pydantic do registro
│   └── diagnostico.py          # Schema Pydantic do diagnóstico
├── routes/
│   ├── registro_foco.py        # POST /registro-foco
│   └── diagnostico.py          # GET /diagnostico-produtividade
├── services/
│   ├── registro_service.py     # Lógica de registro e classificação
│   ├── diagnostico_service.py  # Lógica de diagnóstico (média, tendência, consistência)
│   └── regras_diagnostico.py   # Specification Pattern para regras de sugestão
└── storage/
    ├── base_repository.py      # ABC AbstractRegistroRepository
    ├── database.py             # Conexão SQLite e DDL
    └── registro_repository.py  # Implementação concreta (SQLite)
docs/
└── plano.md                    # Plano de arquitetura gerado com IA
tests/
├── conftest.py
├── test_services.py            # Testes unitários dos serviços
├── test_registro_foco.py       # Testes de integração do POST
└── test_diagnostico.py         # Testes de integração do GET
.env.example                    # Variáveis de ambiente (copiar para .env)
openapi.yaml                    # Contrato da API (spec-first)
CLAUDE.md                       # Instruções para Claude Code
```

## Decisões de arquitetura

### Spec-driven design
O `openapi.yaml` foi escrito antes de qualquer linha de código Python. Isso inverte o fluxo comum: em vez de documentar o que foi feito, o contrato define o que será feito. O benefício prático é que todas as decisões de nomes de campos, tipos, validações e respostas de erro foram tomadas e revisadas antes da implementação — evitando retrabalho e garantindo que a documentação nunca fique desatualizada em relação ao código.

### FastAPI em vez de Flask ou Django
FastAPI foi escolhido porque integra validação (Pydantic), serialização e documentação automática em uma única camada, sem bibliotecas extras. Para uma API que exige validação rigorosa de campos (`nivel_foco` entre 1 e 5, `tempo_minutos` positivo), isso elimina código de validação manual e entrega respostas de erro 422 com mensagens descritivas automaticamente. Flask exigiria essas validações escritas à mão. Django, por sua vez, traria um ecossistema completo (ORM, admin, autenticação, migrations) pensado para aplicações web maiores — tudo isso seria overhead desnecessário para dois endpoints, além de exigir mais tempo de configuração inicial sem agregar valor ao escopo do projeto.

### SQLite com `sqlite3` puro em vez de ORM
SQLAlchemy ou SQLModel adicionariam abstração útil em projetos maiores, mas para dois endpoints com uma tabela simples o custo de configuração supera o benefício. Usar `sqlite3` puro com queries parametrizadas demonstra domínio direto de SQL, torna o código mais fácil de auditar por segurança (sem mágica de ORM) e mantém o número de dependências no mínimo. A troca de banco de dados no futuro exigiria mudar apenas `storage/database.py`.

### Specification Pattern para as regras de diagnóstico

As sugestões do diagnóstico são geradas por regras independentes definidas em `app/services/regras_diagnostico.py`. Cada regra é uma classe que implementa `EspecificacaoSugestao`, uma ABC com dois métodos: `satisfeita(dados)` e `sugestao()`. O motor de regras avalia todas e coleta os resultados de cada uma que foi satisfeita — múltiplas regras podem disparar simultaneamente e todas contribuem para a lista final.

O benefício prático é o **Open/Closed Principle**: adicionar uma nova regra significa criar uma nova classe e incluí-la na lista `REGRAS`, sem modificar nenhum código existente. Remover uma regra também não afeta as demais.

### Separação em camadas (routes / services / storage)
A lógica de negócio foi isolada em `services/` sem nenhuma dependência do FastAPI. Isso tem uma consequência direta: os testes unitários em `test_services.py` testam a lógica de diagnóstico (médias, tendência, consistência) sem subir servidor, sem fazer requisições HTTP e sem banco de dados — são instantâneos e determinísticos. Se a lógica estivesse nas rotas, qualquer teste exigiria infraestrutura HTTP completa.

### Middleware de logging
Em vez de adicionar `print()` ou logs espalhados pelo código, um middleware centraliza o registro de todas as requisições com método, path, status code e tempo de resposta. Isso cobre 100% dos endpoints automaticamente e é o padrão de observabilidade mínima em qualquer API em produção — o desenvolvedor vê no terminal exatamente o que está acontecendo sem instrumentar cada rota.

### Rate limiting com slowapi
O endpoint de escrita (`POST /registro-foco`) está sujeito a abuso — um loop simples poderia inserir milhares de registros e degradar o diagnóstico ou encher o disco. O rate limiting por IP (30 req/min) é a camada mais simples de proteção contra isso e exige apenas um decorator na rota, sem infraestrutura adicional.

### Abstract Base Class no Repository

`app/storage/base_repository.py` define `AbstractRegistroRepository`, uma ABC com os três métodos de acesso a dados (`inserir`, `listar_todos`, `contar`). A implementação concreta `SQLiteRegistroRepository` em `registro_repository.py` satisfaz esse contrato. As rotas e serviços dependem apenas da instância — não do SQLite diretamente. Trocar o banco de dados exigiria apenas uma nova classe implementando a mesma ABC, sem tocar em nenhuma outra camada.

### `streak_dias` — sequência de dias consecutivos

O campo `streak_dias` no diagnóstico mede a maior sequência de dias consecutivos em que o usuário registrou pelo menos uma sessão. É calculado a partir das datas já persistidas no banco, sem campo extra na tabela. Uma sequência longa indica consistência de hábito — informação diferente da média de foco, que mede qualidade mas não regularidade.

### Testes em dois níveis

Os testes unitários (`test_services.py`) cobrem a lógica pura sem subir servidor ou banco. Os testes de integração (`test_registro_foco.py`, `test_diagnostico.py`) usam o `TestClient` do FastAPI com banco SQLite em memória isolado por fixture — cada teste começa do zero sem interferência entre casos. Essa separação permite identificar rapidamente se um erro é de lógica ou de infraestrutura HTTP.

**O que é coberto:**

`test_registro_foco.py` — 18 casos:
- Happy path: POST válido, POST sem campos opcionais, `classificacao_foco` para os 5 níveis
- Boundary values: `nivel_foco` 1 e 5 (limites válidos), `tempo_minutos` 1, `comentario` com 500 chars, `tags` com 10 itens
- Unhappy path obrigatórios: `nivel_foco` 0, -1 e 6 (→ 422), `tempo_minutos` 0 e negativo (→ 422), `comentario` vazio, só espaços e com 501 chars (→ 422), body vazio (→ 422)
- Unhappy path opcionais: `categoria` inválida (→ 422), `tags` com 11 itens (→ 422)

`test_diagnostico.py` — 7 casos:
- GET sem registros (→ 404), GET com registros (→ 200)
- Cálculo correto de `media_foco` e `tempo_total`
- `tendencia` = `dados_insuficientes` com poucos registros
- Presença de todos os campos no response, incluindo `streak_dias`

`test_services.py` — 39 casos:
- `classificar_foco`: todos os 5 níveis
- `_indice_consistencia`: foco perfeito, único registro, errático
- `_tendencia`: melhora, piora, estável, dados insuficientes
- `_feedback`: todas as 6 faixas de média individualmente
- `_nivel_predominante`: nível mais frequente e caso único
- `_distribuicao_categorias`: agrupamento correto, registros sem categoria
- `_top_tags`: ordenação por frequência, lista vazia, limite top_n
- `_streak_dias`: sequência contínua, com lacuna, único registro, múltiplos no mesmo dia
- Specification Pattern: cada regra satisfeita e não satisfeita nos limites exatos, motor de regras sem disparo e com múltiplos disparos simultâneos

---

## Variáveis de ambiente

Copie `.env.example` para `.env` e ajuste conforme necessário. O `.env` nunca é commitado.

| Variável | Padrão | Descrição |
|---|---|---|
| `DB_PATH` | `performance.db` | Caminho do arquivo SQLite |
| `LOG_LEVEL` | `INFO` | Nível de log (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:5173` | Origens permitidas (separadas por vírgula) |
| `RATE_LIMIT` | `30` | Requisições por minuto por IP no POST |

## Segurança

- Validação automática de todos os campos via Pydantic (tipos, ranges, tamanhos)
- Rate limiting por IP no endpoint de escrita (padrão: 30 req/min, configurável via `RATE_LIMIT`)
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

## Retrospectiva do processo

O fluxo foi incremental: comecei com o contrato e a implementação, e fui adicionando camadas — middlewares, variáveis de ambiente, design pattern, testes — conforme o escopo ficava mais claro. Funcionou, mas exigiu várias iterações que poderiam ter sido planejadas no início se eu tivesse listado os requisitos não-funcionais antes de escrever código.

A IA foi mais útil como par de código do que como gerador — ela propôs o Specification Pattern, apontou o commit duplo no repository e inconsistências entre o `openapi.yaml` e os models. As decisões de aceitar ou rejeitar cada sugestão foram minhas.

O que faria diferente: definir requisitos não-funcionais (segurança, observabilidade, configuração, qualidade de código) antes de começar a implementar, em vez de adicioná-los incrementalmente.
