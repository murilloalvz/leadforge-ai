# LeadForge AI

O LeadForge é um **copiloto comercial para freelancers**.

> O freelancer informa o que sabe fazer, e o LeadForge encontra empresas que podem precisar dessas habilidades, explica por que cada empresa é uma oportunidade e ajuda a preparar a abordagem comercial.

O produto não é exclusivo para desenvolvimento web. `web_development` é apenas o primeiro módulo validado do MVP. Veja `docs/PRODUCT_VISION.md` e `docs/ROADMAP.md`.

## Estado atual — v0.3.7

A base inclui:

- FastAPI, SQLAlchemy, SQLite e Alembic;
- Prospect e Evidence com provenance/confiança;
- Discovery Engine por nicho + cidade + UF;
- providers substituíveis;
- `mock` determinístico;
- Geoapify como provider persistente preferido quando configurado;
- descoberta Geoapify por Places API + boundary da cidade para nichos mapeados;
- fallback textual conservador para nichos ainda não mapeados;
- deduplicação exata e diversidade de marca preservando filiais;
- OpenStreetMap/Overpass como fallback experimental;
- `provider="auto"`;
- deduplicação e reutilização de prospects;
- Site Analyzer com proteções SSRF de MVP;
- AI Discoverability separado;
- OpportunityAssessment genérico;
- módulo `web_development` / `web-development-v2`;
- calibração com sites públicos reais;
- export CSV/JSON determinístico;
- validação end-to-end do pipeline;
- CI, lint e testes.

Ainda não existem FreelancerProfile, Compatibility Engine, pricing, chat com IA, outreach, proposta ou demo.

## Discovery Providers

A API aceita:

- `auto` — usa Geoapify quando uma chave existe; sem chave, usa Overpass experimental;
- `geoapify` — discovery persistente baseado principalmente em dados OpenStreetMap;
- `openstreetmap` — Overpass experimental;
- `mock` — dados fictícios para testes.

```http
POST /discovery-runs
Content-Type: application/json

{
  "niche": "clínicas de estética",
  "city": "Campinas",
  "state": "SP",
  "provider": "auto",
  "limit": 10,
  "analyze_sites": true,
  "site_audit_limit": 5
}
```

### Geoapify

```env
LEADFORGE_GEOAPIFY_API_KEY=
LEADFORGE_GEOAPIFY_SEARCH_ENDPOINT=https://api.geoapify.com/v1/geocode/search
LEADFORGE_GEOAPIFY_PLACES_ENDPOINT=https://api.geoapify.com/v2/places
LEADFORGE_GEOAPIFY_DETAILS_ENDPOINT=https://api.geoapify.com/v2/place-details
LEADFORGE_GEOAPIFY_TIMEOUT_SECONDS=12
```

A chave não possui valor default e nunca deve ser commitada.

Na v0.3.7, nichos com categoria validada deixam de usar Forward Geocoding textual como busca principal. O provider resolve a boundary da cidade, consulta a Places API por categoria dentro dessa boundary, valida as categorias retornadas, remove duplicatas exatas e intercala marcas antes do limite final. Place Details é consultado somente para os candidatos selecionados.

Mapeamentos iniciais: clínicas de estética, dentistas/odontologia e academias/fitness. Nichos ainda não mapeados continuam no fallback textual até terem categoria validada. Veja `docs/DISCOVERY_PROVIDERS.md`.

Geoapify foi escolhido no lugar do Google Places para o caminho persistente porque o produto precisa armazenar prospects e exports. A política do Google Places restringe armazenamento/caching de conteúdo além das exceções permitidas, enquanto Geoapify documenta armazenamento/redistribuição de resultados com as atribuições exigidas.

OpenStreetMap attribution deve ser preservada; requisitos adicionais do plano Geoapify utilizado também devem ser respeitados.

### OpenStreetMap/Overpass

Continua disponível sem credencial, mas não é tratado como infraestrutura de produção. A v0.3.5 observou 502/timeouts em runners cloud, portanto sua disponibilidade não faz parte da CI normal.

## Opportunity Intelligence

O primeiro módulo ativo é `web_development`.

O Site Analyzer observa sinais objetivos como HTTPS, viewport, formulário, links de WhatsApp/telefone, CTA, identidade, serviços, localização, meta description, canonical, headings, imagens e redirects.

Findings distinguem `confirmed`, `strong_signal`, `inference` e `unknown`. Ausência de evidência não vira evidência de ausência.

## Export

Runs persistidos podem ser exportados sem repetir discovery/análise:

```http
GET /discovery-runs/1/export?format=csv
GET /discovery-runs/1/export?format=json
```

O JSON usa `discovery-export-v1`; o CSV possui proteção contra formula injection.

## Notificações e CI

A CI automática roda em pull requests e pushes na `main`. Feature branches não disparam CI em todo commit; execução manual continua disponível por `workflow_dispatch`. Isso reduz ruído de notificações sem remover o gate de integração.

## Rodando localmente

```bash
git clone https://github.com/murilloalvz/leadforge-ai.git
cd leadforge-ai/backend
python -m venv .venv
pip install -e ".[dev]"
alembic upgrade head
python -m app.db.seed
uvicorn app.main:app --reload
```

```bash
ruff check .
pytest -q
```

## Gate restante da v0.3.7

O gate técnico real da v0.3.6 passou, mas revelou ruído de relevância no discovery. A v0.3.7 corrige a estratégia de consulta. Depois da CI verde, é obrigatório repetir **Geoapify Live Validation** e comparar o novo artifact com o anterior, verificando relevância dos negócios, cobertura de website/telefone, latência, falhas e consumo estimado.

Somente depois desse gate o roadmap deve avançar para FreelancerProfile e Compatibility Engine.

## Uso de IA no desenvolvimento

Uso IA/Codex para implementação, revisão e testes. Arquitetura, decisões de produto, critérios de avaliação e validação final continuam dirigidos e revisados por mim.
