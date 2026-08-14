# LeadForge AI

O LeadForge é um projeto que estou construindo para transformar sinais públicos de empresas em informação útil para prospecção, automação e melhoria da presença digital.

A ideia é simples: em vez de sair oferecendo "IA e automação" para qualquer empresa, o sistema tenta encontrar negócios, organizar o que realmente consegue observar e mostrar onde existe uma oportunidade mais interessante.

Hoje o projeto trabalha com dois diagnósticos separados:

- **Automation Opportunity Score** — sinais de oportunidade para automação;
- **AI Discoverability Score** — prontidão do site para ser encontrado e entendido por mecanismos de busca e experiências de IA.

Não existe um score único misturando os dois. Eles medem problemas diferentes.

## Estado atual

A branch de desenvolvimento da **v0.3** já tem:

- FastAPI;
- SQLAlchemy + SQLite;
- migrations com Alembic;
- prospects, evidências e CRM básico;
- Opportunity Scoring determinístico e versionado;
- deduplicação de prospects;
- 15 empresas fictícias para desenvolvimento;
- API de prospects;
- Site Analyzer real por URL;
- leitura de `robots.txt`, `noindex`, `X-Robots-Tag`, HTML e JSON-LD;
- AI Discoverability Score;
- proteção inicial contra SSRF;
- **Discovery Engine por nicho + cidade + UF**;
- provider mock para trabalhar sem rede externa;
- provider inicial usando OpenStreetMap/Overpass;
- criação/reutilização automática de prospects;
- auditoria opcional dos sites encontrados;
- ranking por buckets explícitos, sem inventar um terceiro score;
- testes automatizados e CI.

Ainda **não** há análise por LLM, busca de decisores, envio de mensagens, demo personalizada ou execução em massa.

## Fluxo atual

```text
nicho + cidade + UF
        ↓
Discovery Engine
        ↓
empresas públicas encontradas
        ↓
deduplicação + evidências
        ↓
Prospect
   ├────────────→ Automation Opportunity
   │
   └────────────→ Site Analyzer
                         ↓
                AI Discoverability
        ↓
priorização
```

O princípio mais importante continua sendo: **fato observado e hipótese não são a mesma coisa**.

Se uma fonte não informa WhatsApp, por exemplo, isso não significa que a empresa não usa WhatsApp. O dado continua desconhecido até existir uma checagem melhor.

## Descobrindo prospects

Com a API rodando:

```http
POST /discovery-runs
Content-Type: application/json

{
  "niche": "clínicas de estética",
  "city": "Campinas",
  "state": "SP",
  "provider": "openstreetmap",
  "limit": 10,
  "analyze_sites": true,
  "site_audit_limit": 5
}
```

A execução salva os prospects encontrados, reaproveita empresas já existentes e pode analisar uma quantidade limitada de sites na mesma rodada.

Cada candidato retorna os dois diagnósticos separadamente:

```json
{
  "name": "Exemplo Clínica",
  "automation_score": 38,
  "automation_confidence": 0.24,
  "ai_discoverability_score": 44,
  "ai_discoverability_confidence": 0.91,
  "priority_bucket": "dual_signal"
}
```

O `automation_confidence` pode ser baixo no discovery inicial — e isso é esperado. Nessa fase normalmente temos poucas evidências comerciais. O sistema não tenta esconder essa incerteza.

Para testar sem depender de nenhuma fonte externa:

```json
{
  "niche": "clínicas de estética",
  "city": "Campinas",
  "state": "SP",
  "provider": "mock",
  "analyze_sites": false
}
```

Mais detalhes em [`docs/DISCOVERY_ENGINE.md`](docs/DISCOVERY_ENGINE.md).

## Analisando um site diretamente

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

Depois:

```http
GET /site-audits/{id}
```

## Segurança do Site Analyzer

O endpoint recebe URLs informadas pelo usuário, então essa parte do backend é tratada como sensível.

O MVP já:

- aceita apenas HTTP/HTTPS;
- bloqueia localhost e IPs não públicos;
- resolve DNS antes do fetch;
- revalida redirects;
- limita redirects e tamanho da resposta;
- usa timeout;
- não executa JavaScript.

Ainda não considero essa camada uma sandbox de rede pronta para exposição pública. Antes disso, quero endurecer proteção contra DNS rebinding/TOCTOU e detalhes de infraestrutura/proxy.

## OpenStreetMap no Discovery Engine

O provider inicial usa OpenStreetMap/Overpass porque permite testar o fluxo de discovery sem depender de uma chave paga.

Isso não transforma o Overpass público numa base comercial para coleta em massa. As consultas são pequenas e disparadas pelo usuário, e o provider fica isolado justamente para poder ser substituído depois.

Também reduzo o payload armazenado aos campos necessários para o LeadForge em vez de salvar todas as tags devolvidas pela fonte.

A cobertura do OpenStreetMap varia bastante conforme cidade e nicho, então o provider atual deve ser visto como uma primeira fonte de descoberta, não como fonte definitiva.

## Score de oportunidade

O score comercial não vem de um LLM. Ele usa regras explícitas e auditáveis.

A versão atual é `automation-v1.1`. O `confidence` representa cobertura de evidência, não chance de fechar venda.

Mais detalhes em [`docs/SCORING.md`](docs/SCORING.md).

## AI Discoverability

Esse score não tenta prever "qual IA vai recomendar a empresa".

Ele mede coisas observáveis como:

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

- **v0.3:** validar o Discovery Engine e melhorar os providers;
- **v0.4:** análise estruturada por LLM, separando fatos e hipóteses;
- **v0.5:** rascunhos de abordagem personalizados com revisão humana;
- **v0.6:** demo personalizada com dados fictícios;
- **v0.7:** CRM mais completo;
- **v1.0:** validar o sistema com prospecção real.

Mais à frente quero experimentar um **Quality Monitor** para acompanhar automações implantadas e detectar falhas, conversas ruins, leads abandonados e regressões.

## Segurança e privacidade

O projeto é voltado a prospecção B2B legítima. A proposta não é coletar dados privados, contornar login/CAPTCHA, usar identidades falsas ou disparar spam em massa.

Demos usam dados fictícios e qualquer futura mensagem comercial deverá passar por revisão humana antes de ser enviada.

## Uso de IA no desenvolvimento

Uso IA/Codex bastante durante o desenvolvimento, principalmente para implementação, revisão e testes. As decisões de produto, arquitetura, critérios de avaliação e validação final continuam sendo dirigidas e revisadas por mim.

Uma parte do objetivo deste projeto também é aprender a trabalhar bem com desenvolvimento assistido por IA sem perder entendimento do sistema.
