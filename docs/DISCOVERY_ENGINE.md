# Discovery Engine

O Discovery Engine é a camada do LeadForge responsável por transformar uma busca simples de nicho + cidade em uma lista de prospects com evidência e contexto suficiente para priorização.

Ele não é um "gerador de leads" isolado. O papel dele é alimentar os diagnósticos que já existem no projeto.

## Fluxo

```text
nicho + cidade + UF
        ↓
Discovery Provider
        ↓
normalização + deduplicação
        ↓
Prospect
        ├──────────────→ Automation Opportunity Score
        │
        └──────────────→ Site Analyzer (quando houver site e orçamento de auditoria)
                                ↓
                       AI Discoverability Score
        ↓
priority bucket
        ↓
ranking da execução
```

Os dois scores continuam independentes. O ranking não cria um terceiro score mágico.

## Providers

A camada de discovery usa um contrato próprio para que a fonte possa ser trocada sem reescrever o motor.

Providers atuais:

- `mock`: empresas fictícias para desenvolvimento/testes;
- `openstreetmap`: consulta pequena ao Overpass API para descoberta inicial de negócios públicos.

A implementação do OpenStreetMap é intencionalmente conservadora. Ela é apropriada para experimentação e uso interativo pequeno, não para montar uma base comercial em massa usando infraestrutura pública gratuita.

A fonte OSM também não deve ser tratada como cadastro completo. Se um negócio não tiver `website`, `phone` ou `contact:whatsapp` mapeado, o LeadForge mantém o dado como desconhecido. Ele não conclui que o canal não existe.

## Dados persistidos

Cada execução salva:

- nicho, cidade e UF;
- provider;
- limite solicitado;
- quantidade descoberta/criada/reutilizada;
- quantidade de sites auditados e falhas de auditoria;
- status e timestamps.

Cada candidato salva:

- prospect associado;
- identificador e URL da fonte;
- categoria pública;
- payload minimizado da fonte;
- Automation Opportunity Score + confidence;
- AI Discoverability Score + confidence, quando auditado;
- `priority_bucket`;
- posição no ranking;
- auditoria de site associada, quando houver.

O payload bruto do provider é reduzido a um conjunto pequeno de tags úteis. Campos não usados, como e-mails presentes no elemento OSM, não são armazenados automaticamente.

## Priority buckets

A v0.3 usa grupos explícitos:

- `dual_signal`: há sinal comercial e um site com oportunidade clara de melhoria;
- `automation_signal`: há sinais positivos para automação, mas não há gap forte/confirmado no site;
- `site_opportunity`: o principal gap observado está no site;
- `monitor`: há dados suficientes para observar, mas nenhum sinal forte na regra atual;
- `insufficient_evidence`: ainda falta evidência para priorizar com segurança.

Esses buckets servem apenas para ordenar trabalho. Eles não substituem os scores originais.

## API

Criar uma execução:

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

Para trabalhar sem rede externa, use `provider: "mock"` e, se quiser, `analyze_sites: false`.

## Limitações atuais

- a resolução de área do provider OSM usa o nome da cidade e níveis administrativos esperados; nomes ambíguos podem exigir um provider melhor no futuro;
- cobertura do OpenStreetMap varia bastante por cidade e categoria;
- discovery e auditorias rodam de forma síncrona no MVP;
- a execução audita apenas até `site_audit_limit` sites para evitar requests ilimitados;
- não há busca de decisores ou enriquecimento de pessoas;
- não há envio de mensagem;
- não há LLM nessa etapa.

## OpenStreetMap

Dados provenientes do OpenStreetMap devem manter atribuição e respeitar os termos/licença aplicáveis. O endpoint público do Overpass também é um recurso compartilhado e não deve ser usado como infraestrutura de bulk harvesting.

Referências:

- https://www.openstreetmap.org/copyright
- https://wiki.openstreetmap.org/wiki/Overpass_API
