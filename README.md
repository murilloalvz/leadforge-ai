# LeadForge AI

O LeadForge é um **copiloto comercial para freelancers**.

> O freelancer informa o que sabe fazer, e o LeadForge encontra empresas que podem precisar dessas habilidades, explica por que cada empresa é uma oportunidade e ajuda a preparar a abordagem comercial.

O produto não é exclusivo para desenvolvimento web. `web_development` é apenas o primeiro módulo validado do MVP. A visão completa está em `docs/PRODUCT_VISION.md` e o roadmap em `docs/ROADMAP.md`.

## Estado atual — v0.3.6

A base atual inclui:

- FastAPI, SQLAlchemy, SQLite e Alembic;
- Prospect e Evidence com provenance/confiança;
- Discovery Engine por nicho + cidade + UF;
- providers substituíveis;
- provider `mock` determinístico;
- provider Google Places API (New);
- provider OpenStreetMap/Overpass mantido como experimental;
- seleção `provider="auto"`;
- deduplicação e reutilização de prospects;
- Site Analyzer por URL com proteções SSRF de MVP;
- AI Discoverability como diagnóstico separado;
- contrato genérico de OpportunityModule;
- OpportunityAssessment persistido;
- módulo `web_development` / `web-development-v2`;
- calibração com sites públicos reais;
- export CSV/JSON determinístico;
- validação end-to-end do pipeline;
- CI, lint e testes.

Ainda não existem FreelancerProfile, Compatibility Engine, pricing, chat com IA, outreach, proposta ou demo.

## Arquitetura

```text
Discovery Providers
        ↓
     Prospect
        ↓
     Evidence
        ↓
 Site Analyzer / outras fontes
        ↓
Opportunity Modules
        ↓
OpportunityAssessment
        ↓
priorização
        ↓
   CSV / JSON
```

## Discovery Providers

A API aceita:

- `auto` — default; usa Google Places quando uma chave está configurada, senão cai no Overpass experimental;
- `google_places` — Google Places API (New) / Text Search;
- `openstreetmap` — Overpass experimental;
- `mock` — dados fictícios para testes.

Exemplo:

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

### Google Places

Configuração:

```env
LEADFORGE_GOOGLE_PLACES_API_KEY=
LEADFORGE_GOOGLE_PLACES_ENDPOINT=https://places.googleapis.com/v1/places:searchText
LEADFORGE_GOOGLE_PLACES_TIMEOUT_SECONDS=12
```

A chave nunca possui valor default e não deve ser commitada.

O provider usa FieldMask explícita e pede apenas ID, nome, endereço, tipo primário, website, telefone comercial e URL do Google Maps. Não pede reviews, fotos, rating, horários ou dados de atmosfera.

O `pageSize` é limitado a 20 por chamada. A cobrança do Google depende dos campos solicitados; `websiteUri` e telefone elevam o SKU, portanto qualquer expansão da FieldMask deve ser tratada como decisão de produto/custo.

Mais detalhes em `docs/DISCOVERY_PROVIDERS.md`.

### OpenStreetMap/Overpass

O provider continua disponível para experimentação e fallback sem credencial. Ele não é tratado como infraestrutura de produção. Na v0.3.5 houve 502/timeouts em runners cloud; sua disponibilidade não faz parte da CI normal.

## Opportunity Intelligence

O primeiro módulo ativo é `web_development`.

O Site Analyzer observa sinais como:

- HTTPS;
- viewport mobile;
- formulário;
- links de WhatsApp e telefone;
- caminho de contato/captação;
- CTA;
- identidade, serviços e localização;
- meta description;
- canonical;
- headings;
- cobertura de `alt` em imagens;
- redirects.

O LeadForge diferencia:

- `confirmed`;
- `strong_signal`;
- `inference`;
- `unknown`.

Ausência de evidência não vira evidência de ausência.

## Diagnósticos separados

### Web Development Opportunity

Responde se existem problemas observáveis no site que tornam a empresa uma oportunidade plausível para desenvolvimento web.

### AI Discoverability

Responde se o site possui sinais observáveis de prontidão para busca/experiências de IA.

Os scores permanecem separados.

## Export

Um Discovery Run persistido pode ser exportado sem repetir a busca ou o Site Analyzer:

```http
GET /discovery-runs/1/export?format=csv
GET /discovery-runs/1/export?format=json
```

O JSON usa `discovery-export-v1`; o CSV possui proteção contra formula injection.

## Notificações e CI

A partir da v0.3.6, a CI automática roda em:

- pull requests;
- pushes na `main`.

Feature branches não disparam CI em todo commit. O workflow continua disponível via `workflow_dispatch` para execução manual. Isso reduz ruído de notificações durante desenvolvimento sem remover o gate de integração.

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

Testes:

```bash
ruff check .
pytest -q
```

## Próximo gate

A integração Google Places está implementada e pode ser testada deterministicamente sem segredo. Para fechar a validação real da v0.3.6 falta configurar a API key fora do repositório e executar 2–3 buscas pequenas, medindo:

- latência;
- número de empresas retornadas;
- cobertura de website;
- cobertura de telefone comercial;
- falhas;
- funcionamento do pipeline Site Analyzer → OpportunityAssessment → export.

Somente depois desse gate o roadmap deve avançar para FreelancerProfile e Compatibility Engine.

## Uso de IA no desenvolvimento

Uso IA/Codex para implementação, revisão e testes. Arquitetura, decisões de produto, critérios de avaliação e validação final continuam dirigidos e revisados por mim.
