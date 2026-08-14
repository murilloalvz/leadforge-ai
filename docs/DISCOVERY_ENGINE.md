# Discovery Engine

O Discovery Engine transforma uma busca de nicho + cidade + UF em prospects normalizados e evidências que podem ser avaliadas por módulos de oportunidade.

Ele não é um gerador de lista isolado e não pertence a uma categoria específica de freelancer.

## Fluxo atual

```text
nicho + cidade + UF
        ↓
Discovery Provider
        ↓
normalização + deduplicação
        ↓
Prospect
        ↓
Site Analyzer (quando houver site e orçamento de auditoria)
        ↓
OpportunityModule ativo
        ↓
OpportunityAssessment
        ↓
priority bucket
        ↓
ranking
```

Na v0.3.1 o módulo ativo é `web_development`.

AI Discoverability continua sendo produzido separadamente pelo Site Analyzer. O antigo Automation Opportunity também continua persistido temporariamente para compatibilidade, mas não determina mais o ranking principal.

## Providers

Providers atuais:

- `mock`: empresas fictícias para testes/desenvolvimento;
- `openstreetmap`: consulta pequena ao Overpass API para descoberta inicial.

Providers permanecem atrás de contrato próprio. O restante do sistema não depende do formato específico da fonte.

OpenStreetMap/Overpass é usado de forma conservadora e interativa, não como infraestrutura de bulk harvesting.

Campos ausentes na fonte permanecem desconhecidos. Falta de `website`, `phone` ou WhatsApp no provider não significa que esses canais não existem.

## Dados persistidos

Cada execução salva nicho, cidade, UF, provider, limites, contadores, status e timestamps.

Cada candidato pode referenciar:

- Prospect;
- SiteAudit;
- OpportunityAssessment;
- fonte/categoria pública;
- payload minimizado;
- posição no ranking.

## Priority buckets v0.3.1

- `high_opportunity`;
- `medium_opportunity`;
- `low_opportunity`;
- `insufficient_evidence`.

Os buckets são derivados do OpportunityAssessment ativo e servem apenas para ordenar o trabalho. Score e confidence continuam visíveis separadamente.

## API

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

Consultar depois:

```http
GET /discovery-runs/{id}
```

Sem rede externa, use `provider: "mock"` e `analyze_sites: false`.

## Limitações atuais

- cobertura do OpenStreetMap varia por cidade/categoria;
- discovery e auditoria ainda são síncronos;
- apenas até `site_audit_limit` sites são analisados por execução;
- o único OpportunityModule ativo é web development;
- não há perfil do freelancer, preço, chat, outreach ou demo;
- não há busca de decisores/pessoas.

## Referências do provider inicial

- https://www.openstreetmap.org/copyright
- https://wiki.openstreetmap.org/wiki/Overpass_API
