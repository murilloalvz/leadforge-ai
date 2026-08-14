# LeadForge AI — Arquitetura

## Objetivo arquitetural

LeadForge é um copiloto comercial para freelancers. A arquitetura deve separar:

- descoberta de empresas;
- coleta de evidências;
- análise técnica;
- avaliação de oportunidade por categoria de serviço;
- persistência e export dos resultados;
- futuras etapas de compatibilidade, preço e venda assistida.

Nenhuma categoria específica deve ser o núcleo do sistema.

## Fluxo atual

```text
Discovery Provider
      ↓
normalização + deduplicação
      ↓
Prospect
      ↓
Evidence
      ↓
Site Analyzer
      ├──────────────→ AI Discoverability
      │
      ↓
Opportunity Module
      ↓
OpportunityAssessment
      ↓
ranking da execução
      ↓
DiscoveryRun persistido
      ↓
CSV / JSON export
```

Na v0.3.4 existe apenas o módulo de oportunidade `web_development`.

## Núcleo compartilhado

### Prospect

Representa a empresa identificada. Não deve carregar a identidade de um tipo de serviço específico.

Os campos legados `score`, `score_confidence`, `score_version` e `score_explanation` ainda existem por compatibilidade com o antigo Automation Opportunity, mas novos scores de oportunidade devem ser persistidos em `OpportunityAssessment`.

### Evidence

Representa informação observável com proveniência.

Quando possível, cada evidência deve preservar:

- valor;
- fonte;
- timestamp;
- confiança.

Ausência de evidência não é evidência de ausência.

### Discovery Provider

Encontra negócios em fontes públicas permitidas e devolve um formato normalizado.

O restante do sistema não depende do formato específico de OpenStreetMap, Google Places ou qualquer provider futuro.

### Site Analyzer

Coleta sinais objetivos de uma URL pública e produz dados reutilizáveis por múltiplos módulos.

AI Discoverability é um consumidor desses sinais, não o único objetivo do Site Analyzer.

## Opportunity Modules

Um `OpportunityModule` responde a uma pergunta específica de categoria:

> As evidências observadas indicam uma oportunidade plausível para este tipo de serviço?

Contrato conceitual:

```text
OpportunityContext
    signals
    evidence
        ↓
OpportunityModule
        ↓
OpportunityAssessmentResult
    service_category
    score
    confidence
    version
    summary
    recommended_service
    findings
```

Cada módulo pode ter regras próprias, mas deve produzir a mesma estrutura de saída.

Estrutura atual:

```text
services/
└── opportunity/
    ├── contracts.py
    └── web_development/
        └── module.py
```

Novos diretórios só devem ser criados quando um novo módulo for realmente implementado.

## OpportunityAssessment

É a entidade canônica para scores de oportunidade novos.

Ela pode estar ligada a:

- Prospect;
- DiscoveryRun;
- SiteAudit;
- categoria de serviço.

Isso permite que a mesma empresa tenha avaliações independentes no futuro:

```text
Prospect
├── web_development assessment
├── seo assessment
├── design assessment
└── automation assessment
```

Sem colocar vários scores diretamente na tabela `prospects`.

## Findings e certeza

Os módulos devem distinguir:

- `confirmed` — evidência observável confirma o ponto;
- `strong_signal` — sinal forte sem confirmação direta;
- `inference` — interpretação plausível;
- `unknown` — evidência insuficiente.

No MVP atual o módulo web trabalha principalmente com `confirmed` e `unknown`.

Isso é intencional: não há necessidade de inferências antes de o núcleo objetivo estar validado.

## Módulo web_development

É o primeiro módulo de oportunidade do MVP, não o produto inteiro.

Ele reaproveita os sinais do Site Analyzer e mede gaps objetivos relacionados ao site.

A versão atual não afirma responsividade real, performance ou Core Web Vitals porque ainda não existe coleta suficiente para sustentar essas conclusões.

## Export de Discovery Runs

O export é uma camada de leitura sobre resultados persistidos.

Ele não deve ter efeitos colaterais nem alterar a conclusão original do run.

```text
DiscoveryRun persistido
        ↓
Discovery Exporter
   ├── CSV
   └── JSON
```

Regras arquiteturais:

- não reexecutar providers durante export;
- não refazer Site Audit;
- não recalcular OpportunityAssessment;
- ordenar candidatos pelo `rank` persistido;
- preservar findings, certainty e evidências relevantes;
- manter AI Discoverability separado do Opportunity Score;
- versionar o contrato público JSON;
- proteger células CSV contra formula injection;
- não ressuscitar campos legados de automação como contrato principal.

O contrato atual é `discovery-export-v1`.

Detalhes em [`EXPORT.md`](EXPORT.md).

## AI Discoverability

Continua como diagnóstico independente.

Ele mede readiness para descoberta e entendimento por busca/IA, não oportunidade comercial para um freelancer.

Uma empresa pode ter:

- alta oportunidade web e boa discoverability;
- baixa oportunidade web e baixa discoverability;
- qualquer outra combinação.

Não misturar os scores.

## Automation Opportunity legado

O scorer `automation-v1.1` permanece temporariamente para preservar trabalho anterior e compatibilidade com dados/API existentes.

Ele não é mais o modelo canônico de oportunidade nem deve orientar a arquitetura futura.

Quando automação voltar como categoria de produto, deverá ser adaptada para um `OpportunityModule` próprio em uma fase posterior.

## Compatibilidade com freelancer — futuro

`OpportunityAssessment` responde se há uma oportunidade de determinado serviço.

Um futuro `CompatibilityAssessment` responderá outra pergunta:

> Esta oportunidade combina com este freelancer específico?

Não misturar essas duas notas.

Exemplo futuro:

```text
Web Opportunity: 82/100
Freelancer Compatibility: 47/100
```

## Pricing — futuro

Preço deverá ser produzido por um motor separado e sustentado por dados com fonte/frescor/confiança.

O LLM poderá explicar preço e escopo, mas não será a fonte canônica do valor.

## Chat — futuro

O chat será uma interface sobre dados reais persistidos:

```text
FreelancerProfile
Prospect
Evidence
OpportunityAssessment
CompatibilityAssessment
PricingAssessment
        ↓
       LLM
        ↓
resposta em linguagem natural
```

O modelo não deve inventar dados ausentes.

## Demos — futuro

Demos serão específicas por categoria de serviço e claramente identificadas como conceituais/não oficiais.

Não implementar antes das fases anteriores estarem validadas.

## Segurança

Qualquer fetch server-side controlado por URL do usuário deve:

- aceitar apenas HTTP/HTTPS;
- rejeitar localhost, redes privadas, link-local, reserved e metadata services;
- validar DNS/IP;
- revalidar redirects;
- usar timeout;
- limitar redirects e tamanho da resposta;
- não executar JavaScript arbitrário no milestone atual.

Exports CSV também devem tratar texto externo como dado, nunca como fórmula executável.

## Ordem de desenvolvimento

1. Preservar Discovery + Evidence + Site Analyzer.
2. Validar `OpportunityModule` com `web_development`.
3. Expandir evidências objetivas do site.
4. Calibrar oportunidades reais.
5. Exportar resultados persistidos de forma segura e determinística.
6. Validar o fluxo end-to-end em uso real controlado.
7. Só então introduzir FreelancerProfile e Compatibility.
8. Pricing, outreach e proposta vêm depois.
9. Chat vem quando houver dados estruturados suficientes para ser uma boa interface.
10. Novas categorias entram uma por vez.

Veja [`PRODUCT_VISION.md`](PRODUCT_VISION.md) e [`ROADMAP.md`](ROADMAP.md).
