# Roadmap — LeadForge

Este roadmap preserva o que já foi construído e separa a visão ampla do escopo imediato.

## Fundação concluída

### v0.1 — Backend foundation

FastAPI, SQLAlchemy/Alembic, prospects, evidências, scoring inicial, seed, testes e CI.

### v0.2 — Site Analyzer

URL pública, fetcher com proteções SSRF de MVP, HTML/robots/indexabilidade/JSON-LD, AI Discoverability e auditorias persistidas.

### v0.3 — Discovery Engine

Descoberta por nicho + cidade + UF, provider mock, Overpass inicial, deduplicação, prospects, auditoria limitada e ranking persistido.

## Fase 1 — Opportunity Intelligence MVP

O produto é para freelancers em geral; o único módulo ativo do MVP inicial é `web_development`.

### v0.3.1 — Opportunity Modules foundation — concluída

Contrato genérico de OpportunityModule, OpportunityAssessment persistido, taxonomia de certeza e primeiro módulo web.

### v0.3.2 — Web evidence expansion — concluída

Viewport, formulário, contatos, CTA, HTTPS, meta description, canonical, headings, imagens e `web-development-v2`.

### v0.3.3 — Web opportunity calibration — concluída

Cinco homepages públicas, 25 rótulos, comparador de erros e regressão da detecção de localização brasileira.

### v0.3.4 — Export — concluída

CSV/JSON de Discovery Runs, `discovery-export-v1`, determinismo e proteção contra CSV formula injection.

### v0.3.5 — Validação end-to-end — concluída

Quatro sites públicos reais, ranking/dedup/export validados e regressão para falso positivo de título longo. Overpass mostrou 502/timeouts em runners cloud e permaneceu experimental.

### v0.3.6 — Discovery Provider hardening — concluída

- Google Places avaliado e descartado para o caminho persistente por restrições de storage/caching incompatíveis com Prospect/Evidence/export;
- Geoapify adicionado como provider persistente preferido;
- chave apenas por ambiente/GitHub secret;
- workflow manual `Geoapify Live Validation`;
- gate real executado em 18/08/2026: 3/3 queries concluídas, 12 empresas, zero falhas de provider, cobertura aproximada de 66,7% para website e telefone.

O gate confirmou saúde técnica do provider, mas revelou ruído de relevância: hospitais em busca de estética e concentração de várias unidades da mesma rede em academias.

### v0.3.7 — Discovery Relevance Hardening — em implementação

Objetivo: corrigir a consulta, não mascarar ruído com heurísticas pós-hoc frágeis.

Para nichos com mapeamento de categoria validado:

```text
cidade → place_id da boundary
→ Places API por categoria dentro da cidade
→ validação de categoria
→ deduplicação exata
→ diversidade de marca preservando filiais
→ detalhes somente dos candidatos selecionados
```

Mapeamentos iniciais:

- clínicas de estética;
- dentistas/odontologia;
- academias/fitness.

Nichos ainda não mapeados continuam no fallback textual existente até terem categoria validada.

Gate de saída:

- CI verde;
- repetir `Geoapify Live Validation`;
- revisão manual comprovar melhora de relevância sem regressão grave de cobertura/latência/consumo.

### v1.0 — Opportunity Intelligence MVP útil

```text
buscar negócios locais com uma fonte confiável
→ analisar site
→ detectar problemas objetivos
→ criar OpportunityAssessment
→ explicar evidências/confiança
→ priorizar
→ exportar
```

## Fase 2 — Perfil e venda assistida

Somente depois do discovery real estar suficientemente validado:

- FreelancerProfile;
- habilidades, serviços, experiência e restrições;
- Compatibility Engine;
- sugestão de serviço/escopo;
- Pricing Engine inicial com fontes/data;
- rascunho de abordagem e proposta revisável.

## Fase 3 — Chat com IA

Interface em linguagem natural grounded em Prospect, Evidence, OpportunityAssessment e dados futuros de perfil/compatibilidade/preço. O modelo não substitui fatos por invenção.

## Fase 4 — Demos

Templates por categoria, primeira implementação web, revisão manual e link temporário claramente marcado como demonstração não oficial.

## Fase 5 — Generalização

Adicionar módulos reais, um por vez: SEO, design, social media, copywriting, vídeo, tráfego, automação/RPA, dados e suporte de TI.

Cada módulo poderá ter sinais, findings, scoring, compatibilidade, catálogo de serviços, inputs de preço e tipo de demo próprios. Discovery, Prospect, Evidence e OpportunityAssessment continuam compartilhados.

## Fora do escopo atual

Não implementar agora FreelancerProfile, Compatibility Engine, Pricing Engine, LLM/chat, outreach automático, propostas, demos, múltiplos módulos ou coleta em massa.
