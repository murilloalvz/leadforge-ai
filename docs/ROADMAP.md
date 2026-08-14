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

### v0.3.1 — Opportunity Modules foundation — concluída

- contrato genérico de `OpportunityModule`;
- `OpportunityAssessment` independente do prospect;
- taxonomia de certeza: confirmed / strong_signal / inference / unknown;
- primeiro módulo `web_development`;
- ranking baseado na oportunidade do módulo ativo.

### v0.3.2 — Web evidence expansion — concluída

- viewport, formulário, contato, CTA e HTTPS;
- meta description, canonical, headings e imagens;
- Web Development Opportunity `web-development-v2`;
- limitações dos sinais documentadas.

### v0.3.3 — Web opportunity calibration — concluída

- cinco homepages públicas e 25 rótulos revisados;
- comparador de falsos positivos/falsos negativos;
- correção de localização brasileira com teste de regressão;
- pesos mantidos quando o problema estava no detector.

### v0.3.4 — Export — concluída

- CSV e JSON de Discovery Runs persistidos;
- contrato `discovery-export-v1`;
- proteção contra CSV formula injection;
- export determinístico e sem novas chamadas de rede.

### v0.3.5 — Validação end-to-end do MVP — concluída

- quatro empresas públicas reais em dois grupos;
- 4/4 sites auditados na execução final;
- ranking, deduplicação e exports validados;
- falso positivo de título longo corrigido;
- limitação do Overpass em runners cloud documentada.

Detalhes em `docs/MVP_VALIDATION.md`.

### v0.3.6 — Discovery Provider hardening — integração implementada

Objetivo: retirar o Overpass da posição de única fonte real e preservar a arquitetura substituível de providers.

Implementado:

- Google Places API (New) / Text Search como segundo provider;
- FieldMask explícita e limitada aos dados necessários;
- `pageSize` limitado a 20 por chamada;
- API key somente por configuração/ambiente;
- timeout e erros externos classificados;
- payload persistido minimizado;
- provider `auto`: Google Places quando há chave, Overpass como fallback experimental;
- provider mock preservado para testes determinísticos;
- Overpass explicitamente mantido como experimental;
- testes do Google Places via `httpx.MockTransport`, sem segredo real;
- documentação de custo, proveniência e limitações em `docs/DISCOVERY_PROVIDERS.md`;
- CI automática removida de pushes de feature branch para reduzir ruído de notificações; PR/main continuam como gates automáticos.

Pendente para fechar a validação real do provider Google:

- configurar uma API key habilitada fora do repositório;
- rodar pequenas buscas reais em pelo menos dois nichos/cidades;
- medir latência, quantidade retornada, cobertura de website/telefone e falhas;
- registrar custo observado e comparar qualidade com o fallback.

Nenhuma credencial deve ser commitada no repositório ou colada em documentação.

### Próximo gate — validação live do Google Places

Depois que a credencial estiver disponível via ambiente/secret:

```text
Google Places real
→ 2–3 buscas pequenas
→ cobertura de website/telefone
→ latência/falhas
→ Site Analyzer
→ OpportunityAssessment
→ export
```

Esse gate deve ser pequeno e controlado. Não adicionar FreelancerProfile, preço, chat ou novos módulos durante a validação.

### v1.0 — Opportunity Intelligence MVP útil

Fluxo mínimo desejado:

```text
buscar negócios locais com uma fonte confiável
→ analisar site
→ detectar problemas objetivos
→ criar OpportunityAssessment web
→ explicar evidências e confiança
→ priorizar
→ exportar
```

## Fase 2 — Perfil e venda assistida

Somente depois do núcleo acima estar validado com um caminho de discovery suficientemente confiável.

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
- revisão manual;
- link temporário claramente marcado como demonstração não oficial.

## Fase 5 — Generalização

Adicionar módulos reais, um por vez:

- SEO;
- design;
- social media;
- copywriting;
- edição de vídeo;
- gestão de tráfego;
- automação/RPA;
- análise de dados;
- suporte de TI.

Cada módulo poderá ter seus próprios sinais, findings, scoring, compatibilidade, catálogo de serviços, inputs de preço e tipo de demonstração.

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
