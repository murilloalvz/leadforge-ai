# LeadForge AI

O LeadForge é um projeto que estou construindo para transformar sinais públicos de empresas em oportunidades de automação B2B mais fáceis de priorizar e explicar.

A ideia nasceu de uma pergunta simples: em vez de sair abordando qualquer empresa oferecendo “IA e automação”, dá para criar um sistema que encontre negócios com sinais reais de um processo manual, organize as evidências e ajude a decidir onde uma automação provavelmente faz sentido?

Esse repositório é a tentativa de responder isso construindo o produto de verdade, por etapas.

## Onde o projeto está

A **v0.1** já tem a fundação do backend:

- FastAPI;
- SQLAlchemy + SQLite;
- migrations com Alembic;
- modelo inicial de prospects, evidências e CRM;
- Opportunity Scoring determinístico;
- 15 empresas fictícias para desenvolvimento;
- API mínima de listagem/detalhe;
- testes automatizados.

Ainda **não** tem crawler real, análise por LLM, envio de mensagens ou demo personalizada. Essas partes entram depois que a base estiver validada.

## Como funciona a ideia

```text
empresa encontrada
       ↓
evidências públicas
       ↓
score de oportunidade
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

Um princípio importante: **fato observado e hipótese não são a mesma coisa**. O sistema não deve afirmar que uma empresa “perde 30 clientes por mês” sem ter dados para isso. Ausência também só conta quando houve uma checagem real.

## Score de oportunidade

O score principal não vem de um LLM. Ele é calculado por regras explícitas e auditáveis.

Alguns sinais da primeira versão:

- WhatsApp como canal de contato;
- presença de formulário;
- vários serviços;
- ausência de agendamento depois de uma checagem explícita;
- atividade pública/demanda;
- automação avançada já visível;
- sinais de inatividade.

Além da nota de 0 a 100, o resultado guarda os componentes e um nível de `confidence`, que representa cobertura de evidência — não a chance de fechar o cliente.

Os pesos atuais ainda são hipóteses. A ideia é recalibrar usando dados reais quando o projeto começar a ser usado em prospecção.

Mais detalhes em [`docs/SCORING.md`](docs/SCORING.md).

## Primeiro caso de uso

O nicho inicial é **clínicas de estética e negócios locais de estética**.

A primeira oferta que quero validar é uma automação de **qualificação + follow-up de leads**: organizar novos contatos, registrar interesse, priorizar quem precisa de retorno e evitar que oportunidades fiquem esquecidas.

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
│   │   └── services/scoring/
│   ├── alembic/
│   ├── tests/
│   ├── alembic.ini
│   └── pyproject.toml
├── docs/
├── sample_data/
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

## Testes

Dentro de `backend/`:

```bash
pytest -q
```

## Próximas etapas

- **v0.2:** evidências e enrichment por providers públicos permitidos;
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
