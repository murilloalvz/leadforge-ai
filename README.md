# LeadForge AI

O LeadForge é um projeto que estou construindo para transformar sinais públicos de empresas em informação útil para prospecção e automação.

A ideia começou com uma pergunta simples: em vez de sair oferecendo "IA e automação" para qualquer empresa, dá para encontrar negócios com sinais reais de processos manuais, organizar as evidências e priorizar onde uma solução provavelmente faz mais sentido?

Com o tempo apareceu uma segunda frente que combina bastante com a primeira: se o sistema já está analisando o site de um prospect, ele também pode avaliar se esse site está bem preparado para ser encontrado e entendido por mecanismos de busca e experiências de IA.

Então o projeto passa a ter dois diagnósticos separados:

- **oportunidade de automação**;
- **prontidão do site para descoberta por IA/busca**.

## Estado atual

A branch de desenvolvimento da v0.1 já tem:

- FastAPI;
- SQLAlchemy + SQLite;
- migrations com Alembic;
- modelo inicial de prospects, evidências e CRM;
- Opportunity Scoring determinístico e versionado;
- deduplicação básica de prospects;
- 15 empresas fictícias para desenvolvimento;
- API mínima com paginação;
- motor inicial de AI Discoverability, ainda sem crawler real;
- testes automatizados;
- CI com lint, testes, migration e seed.

Ainda **não** tem coleta real de sites, análise por LLM, envio de mensagens ou demo personalizada. Essas partes entram depois que a fundação estiver validada.

## Fluxo que quero chegar

```text
empresa encontrada
       ↓
evidências públicas
       ├──────────────→ score de oportunidade de automação
       │
       └──────────────→ diagnóstico do site / AI Discoverability
                              ↓
                     problemas e melhorias

score comercial
       ↓
hipótese de problema
       ↓
automação recomendada
       ↓
oferta + demo
       ↓
revisão humana
       ↓
CRM
```

Um princípio importante do projeto: **fato observado e hipótese não são a mesma coisa**. O sistema não deve afirmar que uma empresa perde clientes ou dinheiro sem ter evidência para isso. Ausência também só conta quando houve uma checagem real.

## Score de oportunidade

O score comercial não vem de um LLM. Ele usa regras explícitas e auditáveis.

A revisão v1.1 corrigiu um problema da primeira implementação: os pesos positivos agora realmente ocupam a escala de 0 a 100, o algoritmo ganhou versionamento e a confiança passou a representar melhor a cobertura real das evidências.

Mais detalhes em [`docs/SCORING.md`](docs/SCORING.md).

## AI Discoverability

O segundo score não tenta prever "qual IA vai recomendar a empresa". Isso seria uma promessa que a ferramenta não consegue sustentar.

Ele mede sinais que podemos observar, como:

- site acessível e indexável;
- acesso de crawlers relevantes;
- informações importantes em texto;
- serviços e localização descritos claramente;
- identidade do negócio bem definida;
- dados estruturados coerentes.

Essa análise fica separada do score de automação. Uma empresa pode ter um ótimo site e ainda ter processos comerciais manuais; ou o contrário.

Mais detalhes em [`docs/AI_DISCOVERABILITY.md`](docs/AI_DISCOVERABILITY.md).

## Primeiro caso de uso

O nicho inicial é **clínicas de estética e negócios locais de estética**.

A primeira oferta a ser validada é uma automação de **qualificação + follow-up de leads**: organizar novos contatos, registrar interesse, priorizar quem precisa de retorno e evitar que oportunidades fiquem esquecidas.

A especificação está em [`docs/FIRST_OFFER.md`](docs/FIRST_OFFER.md).

## Estrutura atual

```text
leadforge-ai/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   │       ├── scoring/
│   │       └── site_readiness/
│   ├── alembic/
│   ├── tests/
│   ├── alembic.ini
│   └── pyproject.toml
├── docs/
├── sample_data/
├── .github/workflows/
├── AGENTS.md
└── README.md
```

## Rodando localmente

Requisitos: Python 3.12+.

```bash
git clone https://github.com/murilloalvz/leadforge-ai.git
cd leadforge-ai/backend
python -m venv .venv
```

Ative o ambiente virtual e instale o projeto:

```bash
pip install -e ".[dev]"
```

Crie o banco:

```bash
alembic upgrade head
```

Carregue os dados fictícios:

```bash
python -m app.db.seed
```

Suba a API:

```bash
uvicorn app.main:app --reload
```

A documentação interativa fica em `/docs`.

## Testes e lint

Dentro de `backend/`:

```bash
ruff check .
pytest -q
```

O GitHub Actions repete lint, testes, migration e seed em pushes e pull requests.

## Próximas etapas

- **v0.2:** coleta/enrichment por fontes públicas permitidas e análise real de sites;
- **v0.3:** análise estruturada por LLM, separando fatos e hipóteses;
- **v0.4:** rascunhos de abordagem personalizados, sempre com revisão humana;
- **v0.5:** demo personalizada com dados fictícios;
- **v0.6:** fluxo de CRM mais completo;
- **v1.0:** validar o sistema com prospecção real.

Mais à frente quero experimentar um **Quality Monitor** para acompanhar automações implantadas em clientes e detectar falhas, conversas ruins, leads abandonados e regressões.

## Segurança e privacidade

O projeto é voltado a prospecção B2B legítima. A proposta não é coletar dados privados, contornar login/CAPTCHA, usar identidades falsas ou disparar spam em massa.

Demos usam dados fictícios e qualquer futura mensagem comercial deverá passar por revisão humana antes de ser enviada.

## Uso de IA no desenvolvimento

Uso IA/Codex bastante durante o desenvolvimento, principalmente para implementação, revisão e testes. As decisões de produto, arquitetura, critérios de avaliação e validação final continuam sendo dirigidas e revisadas por mim.

Uma parte do objetivo deste projeto também é aprender a trabalhar bem com desenvolvimento assistido por IA sem perder entendimento do sistema.
