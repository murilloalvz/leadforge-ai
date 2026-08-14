# LeadForge AI

O LeadForge é um projeto que estou construindo para transformar sinais públicos de empresas em informação útil para prospecção, automação e melhoria da presença digital.

A ideia começou com uma pergunta simples: em vez de sair oferecendo "IA e automação" para qualquer empresa, dá para encontrar negócios com sinais reais de processos manuais, organizar as evidências e priorizar onde uma solução provavelmente faz mais sentido?

Hoje o projeto trabalha com dois diagnósticos separados:

- **Automation Opportunity Score** — oportunidade comercial para automação;
- **AI Discoverability Score** — prontidão do site para ser encontrado e entendido por mecanismos de busca e experiências de IA.

## Estado atual

A branch de desenvolvimento da **v0.2** já tem:

- FastAPI;
- SQLAlchemy + SQLite;
- migrations com Alembic;
- prospects, evidências e CRM básico;
- Opportunity Scoring determinístico e versionado;
- deduplicação básica de prospects;
- 15 empresas fictícias para desenvolvimento;
- API de prospects com paginação;
- AI Discoverability Score determinístico;
- **Site Analyzer real por URL**;
- leitura de `robots.txt`, `noindex` e `X-Robots-Tag`;
- extração de título, headings, texto e JSON-LD;
- detecção de sinais de `LocalBusiness` e endereço;
- persistência das auditorias;
- proteção inicial contra SSRF, redirects para rede privada e respostas muito grandes;
- testes automatizados e CI.

Ainda **não** há descoberta automática de empresas, execução de JavaScript, análise por LLM, envio de mensagens ou demo personalizada.

## Fluxo atual

```text
URL pública
    ↓
Safe HTTP Fetcher
    ↓
HTML + robots.txt
    ↓
evidências observáveis
    ↓
AI Discoverability Score
    ↓
recomendações
    ↓
auditoria salva no banco
```

O princípio mais importante continua sendo: **fato observado e hipótese não são a mesma coisa**. O sistema não deve inventar perdas, receita ou processos internos que não consegue observar.

## Analisando um site

Com a API rodando, envie uma URL pública:

```http
POST /site-audits
Content-Type: application/json

{
  "url": "https://exemplo.com.br"
}
```

Também é possível ligar a auditoria a um prospect existente:

```json
{
  "url": "https://exemplo.com.br",
  "prospect_id": 3
}
```

A resposta inclui:

```json
{
  "score": 76,
  "confidence": 0.92,
  "score_version": "ai-discoverability-v1",
  "signals": {
    "indexable": true,
    "oai_searchbot_allowed": true,
    "services_clearly_described": false
  },
  "evidence": {
    "page_title": "...",
    "word_count": 640,
    "structured_types": ["LocalBusiness"]
  },
  "recommendations": [
    "Criar uma descrição explícita dos serviços."
  ]
}
```

Depois a auditoria pode ser consultada por:

```http
GET /site-audits/{id}
```

## Segurança do Site Analyzer

O endpoint recebe URLs informadas pelo usuário, então não pode fazer requests sem validação.

A v0.2 já:

- aceita apenas HTTP/HTTPS;
- bloqueia localhost e IPs não públicos;
- resolve DNS antes do fetch e rejeita destinos privados;
- revalida URLs de redirect;
- limita quantidade de redirects;
- limita o tamanho da resposta;
- usa timeout;
- não executa JavaScript.

Essa proteção é adequada ao MVP, mas o fetcher ainda não deve ser tratado como uma sandbox de rede de produção. Antes de expor o serviço publicamente, a camada contra SSRF deverá ser endurecida contra cenários como DNS rebinding e diferenças de infraestrutura/proxy.

## Score de oportunidade

O score comercial não vem de um LLM. Ele usa regras explícitas e auditáveis.

A revisão `automation-v1.1` corrigiu a escala para realmente ocupar 0–100 e melhorou o cálculo de `confidence` para representar cobertura de evidência.

Mais detalhes em [`docs/SCORING.md`](docs/SCORING.md).

## AI Discoverability

O segundo score não tenta prever "qual IA vai recomendar a empresa". Ele mede sinais que conseguimos observar e explicar, como:

- página pública e indexável;
- acesso de crawlers;
- informações importantes em texto;
- serviços e localização claros;
- identidade do negócio;
- títulos descritivos;
- dados estruturados.

Uma empresa pode ter um site excelente e processos comerciais manuais, ou o contrário. Por isso os dois scores continuam independentes.

Mais detalhes em [`docs/AI_DISCOVERABILITY.md`](docs/AI_DISCOVERABILITY.md).

## Primeiro caso de uso

O nicho inicial é **clínicas de estética e negócios locais de estética**.

A primeira oferta a ser validada é uma automação de **qualificação + follow-up de leads**: organizar novos contatos, registrar interesse, priorizar quem precisa de retorno e evitar que oportunidades fiquem esquecidas.

A especificação está em [`docs/FIRST_OFFER.md`](docs/FIRST_OFFER.md).

## Rodando localmente

Requisitos: Python 3.12+.

```bash
git clone https://github.com/murilloalvz/leadforge-ai.git
cd leadforge-ai/backend
python -m venv .venv
pip install -e ".[dev]"
alembic upgrade head
python -m app.db.seed
uvicorn app.main:app --reload
```

A documentação interativa fica em `/docs`.

## Testes e lint

Dentro de `backend/`:

```bash
ruff check .
pytest -q
```

O GitHub Actions repete lint, testes, migrations e seed em pushes e pull requests.

## Próximas etapas

- **v0.2:** concluir e validar Site Analyzer por URL;
- **v0.2.x:** conectar auditoria aos prospects e começar enrichment/discovery permitido;
- **v0.3:** análise estruturada por LLM, separando fatos e hipóteses;
- **v0.4:** rascunhos de abordagem personalizados com revisão humana;
- **v0.5:** demo personalizada com dados fictícios;
- **v0.6:** CRM mais completo;
- **v1.0:** validar o sistema com prospecção real.

Mais à frente quero experimentar um **Quality Monitor** para acompanhar automações implantadas e detectar falhas, conversas ruins, leads abandonados e regressões.

## Segurança e privacidade

O projeto é voltado a prospecção B2B legítima. A proposta não é coletar dados privados, contornar login/CAPTCHA, usar identidades falsas ou disparar spam em massa.

Demos usam dados fictícios e qualquer futura mensagem comercial deverá passar por revisão humana antes de ser enviada.

## Uso de IA no desenvolvimento

Uso IA/Codex bastante durante o desenvolvimento, principalmente para implementação, revisão e testes. As decisões de produto, arquitetura, critérios de avaliação e validação final continuam sendo dirigidas e revisadas por mim.

Uma parte do objetivo deste projeto também é aprender a trabalhar bem com desenvolvimento assistido por IA sem perder entendimento do sistema.
