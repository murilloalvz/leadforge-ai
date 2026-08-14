# Roadmap — LeadForge

Este roadmap preserva o que já foi construído e separa a visão ampla do escopo imediato.

## Fundação concluída

### v0.1 — Backend foundation

- FastAPI;
- SQLAlchemy + Alembic;
- prospects e evidências;
- scoring determinístico inicial;
- seed e testes;
- CI.

### v0.2 — Site Analyzer

- análise de URL pública;
- fetcher com proteções SSRF de MVP;
- HTML, robots.txt, indexabilidade e JSON-LD;
- AI Discoverability;
- auditorias persistidas.

### v0.3 — Discovery Engine

- descoberta por nicho + cidade + UF;
- provider mock;
- provider inicial OpenStreetMap/Overpass;
- deduplicação;
- criação/reuso de prospects;
- auditoria limitada de sites;
- ranking persistido.

## Fase 1 — Opportunity Intelligence MVP

O produto é para freelancers em geral, mas o **único módulo ativo do MVP inicial é `web_development`**.

### v0.3.1 — Opportunity Modules foundation

- contrato genérico de `OpportunityModule`;
- `OpportunityAssessment` independente do prospect;
- taxonomia de certeza: confirmed / strong_signal / inference / unknown;
- primeiro módulo `web_development`;
- ranking do Discovery Engine baseado na oportunidade do módulo ativo;
- manter diagnósticos antigos apenas por compatibilidade durante a transição.

### v0.3.2 — Web evidence expansion

Adicionar sinais objetivos úteis para freelancers web, por exemplo:

- viewport mobile;
- presença de formulário;
- CTA principal;
- WhatsApp/link de contato;
- HTTPS e redirects relevantes;
- estrutura básica da página;
- sinais de responsividade detectáveis sem executar JavaScript.

Não afirmar performance ou Core Web Vitals sem uma fonte própria para isso.

### v0.3.3 — Web opportunity calibration

- revisar pesos;
- explicar contribuição de cada finding;
- validar contra empresas reais;
- registrar falsos positivos/negativos;
- separar melhor problema confirmado de recomendação.

### v0.3.4 — Export

- exportar resultados em CSV/JSON;
- manter fonte, score, confidence e findings no export;
- permitir uso manual pelo freelancer.

### v1.0 — MVP útil

Fluxo mínimo validado:

```text
buscar negócios locais
→ analisar site
→ detectar problemas objetivos
→ criar OpportunityAssessment web
→ explicar evidências e confiança
→ priorizar
→ exportar
```

## Fase 2 — Perfil e venda assistida

Somente depois do núcleo acima estar validado.

- FreelancerProfile;
- habilidades e serviços;
- experiência e limites de complexidade;
- disponibilidade e localização;
- Compatibility Engine;
- sugestão de serviço/escopo;
- Pricing Engine inicial com fontes e data;
- rascunho de abordagem com revisão humana;
- proposta revisável.

## Fase 3 — Chat com IA

- linguagem natural como interface principal;
- respostas grounded nos dados persistidos;
- comparação de oportunidades;
- ajuste de escopo e preço;
- edição de abordagem/proposta;
- preferências e histórico somente com autorização.

O chat não substitui fontes, regras e assessments por invenção do modelo.

## Fase 4 — Demos

- templates por categoria/segmento;
- primeira implementação para web development;
- dados públicos da empresa apenas quando apropriados;
- dados de clientes sempre fictícios;
- revisão manual;
- link temporário claramente marcado como demonstração não oficial.

## Fase 5 — Generalização

Adicionar módulos reais, um por vez, quando houver critérios e dados suficientes:

- SEO;
- design;
- social media;
- copywriting;
- edição de vídeo;
- gestão de tráfego;
- automação/RPA;
- análise de dados;
- suporte de TI.

Cada módulo poderá ter seus próprios:

- sinais;
- regras de findings;
- scoring;
- requisitos de compatibilidade;
- catálogo de serviços;
- inputs de precificação;
- tipo de demonstração.

Discovery, Prospect, Evidence e OpportunityAssessment permanecem infraestrutura compartilhada.

## Fora do escopo atual

Não implementar agora:

- FreelancerProfile;
- Compatibility Engine;
- Pricing Engine;
- LLM/chat;
- outreach automático;
- propostas;
- demos;
- múltiplos módulos de serviço;
- coleta em massa.
