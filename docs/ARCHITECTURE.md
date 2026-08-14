# LeadForge AI — Arquitetura

## Objetivo

O LeadForge transforma sinais públicos de empresas em dois diagnósticos independentes:

1. **Automation Opportunity** — ajuda a priorizar empresas para uma oferta de automação;
2. **AI Discoverability** — avalia se o site está tecnicamente e semanticamente preparado para descoberta por busca e experiências de IA.

Os dois usam parte da mesma coleta de evidências, mas não compartilham um score único.

## Fluxo principal

```text
Discovery Provider
      ↓
normalização + deduplicação
      ↓
evidências / enrichment
      ├───────────────────────┐
      ↓                       ↓
Automation Opportunity    AI Discoverability
      ↓                       ↓
AI opportunity analyst    recomendações do site
      ↓
solution recommendation
      ↓
offer + demo
      ↓
human review
      ↓
CRM
```

## Discovery

Responsável por encontrar empresas a partir de fontes públicas permitidas. O restante do sistema não deve depender diretamente de um provider específico.

Na v0.1 existem apenas empresas fictícias. A v0.2 deve introduzir providers reais de forma controlada.

A identidade básica do prospect usa uma `dedup_key` normalizada. IDs estáveis de providers poderão melhorar essa deduplicação depois.

## Evidence / Enrichment

Armazena sinais observáveis com proveniência.

Exemplos comerciais:

- WhatsApp público;
- formulário;
- agendamento visível;
- catálogo de serviços;
- automação aparente;
- atividade pública.

Exemplos de site:

- status HTTP;
- indexabilidade;
- regras de crawler;
- conteúdo textual importante;
- títulos;
- descrição de serviços/localização;
- dados estruturados.

Um sinal externo deve, quando possível, guardar valor, fonte, timestamp e confiança.

## Automation Opportunity Scoring

O score comercial é determinístico, explicável e versionado.

O LLM não escolhe a nota canônica.

Saída conceitual:

```json
{
  "total": 78,
  "confidence": 0.82,
  "version": "automation-v1.1",
  "components": [],
  "explanation": "..."
}
```

`confidence` representa cobertura de evidência, não chance de venda.

Ausências só pontuam depois de uma checagem explícita.

## AI Discoverability

É um diagnóstico separado do score comercial.

O objetivo não é prever se uma IA vai recomendar a empresa. O objetivo é medir sinais verificáveis que favorecem descoberta e entendimento do site.

Saída conceitual:

```json
{
  "score": 84,
  "confidence": 0.91,
  "version": "ai-discoverability-v1",
  "components": [],
  "blockers": []
}
```

Critérios v1 incluem acessibilidade pública, indexabilidade, acesso de crawlers relevantes, conteúdo textual, clareza de identidade/serviços/localização e dados estruturados coerentes.

Bloqueadores técnicos podem limitar a nota mesmo quando o restante do site parece bom.

Detalhes em [`AI_DISCOVERABILITY.md`](AI_DISCOVERABILITY.md).

## AI Opportunity Analyst

Milestone futuro.

Recebe evidências e o score comercial e retorna estruturas separando:

- fatos observados;
- hipóteses;
- possíveis dores;
- oportunidades de automação;
- solução recomendada;
- informação faltante.

A saída do LLM deve ser validada por schema.

## Solution Recommender

Mapeia padrões de oportunidade para soluções reaproveitáveis.

Catálogo inicial planejado:

- qualificação de leads;
- follow-up;
- funil de agendamento;
- dashboard de leads.

## Outreach Generator

Milestone futuro. Produz rascunhos sustentados por evidências, mas não envia automaticamente.

Todo outreach começa com revisão humana.

## Demo Generator

Milestone futuro. Monta demos específicas a partir de templates reutilizáveis. Dados de clientes dentro das demos devem ser fictícios e identificados como tal.

## CRM

Pipeline inicial:

```text
discovered
→ analyzed
→ high_priority
→ offer_generated
→ demo_ready
→ ready_for_review
→ contacted
→ replied
→ meeting
→ proposal
→ won / lost / do_not_contact
```

## Quality Monitor

Produto recorrente futuro para automações implantadas em clientes.

Poderá acompanhar falhas, leads abandonados, respostas ruins, escalonamentos, resolução, conversão e regressões.

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
│   └── tests/
├── docs/
├── sample_data/
├── .github/workflows/
├── AGENTS.md
└── README.md
```

Só devem existir diretórios úteis para o milestone atual. Evitar arquitetura vazia apenas para parecer grande.

## Limites de segurança para a v0.2

Qualquer código que busque URLs deve:

- aceitar apenas `http`/`https`;
- rejeitar localhost, redes privadas, link-local e metadata services;
- validar DNS/IP para reduzir SSRF;
- usar timeouts;
- limitar tamanho de resposta;
- não executar JavaScript/código arbitrário de terceiros;
- respeitar termos e rate limits;
- não contornar autenticação, CAPTCHA ou anti-bot.

## Ordem de desenvolvimento

1. Fechar e testar a fundação v0.1.
2. Adicionar coleta real de evidências e análise de sites na v0.2.
3. Só então introduzir interpretação por LLM.
4. Gerar outreach apenas depois que a qualidade das evidências estiver confiável.
5. Validar com prospects reais antes de expandir para um SaaS genérico.
