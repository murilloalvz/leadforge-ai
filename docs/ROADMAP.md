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

### v0.3.6 — Discovery Provider hardening — implementação atual

Objetivo: retirar o Overpass da posição de única fonte real sem acoplar o Discovery Engine a um fornecedor.

Decisões e implementação:

- Google Places foi avaliado e descartado para o caminho persistente por incompatibilidade entre suas restrições de caching/storage e a necessidade do LeadForge de persistir prospects/exports;
- Geoapify foi escolhido como provider persistente preferido porque documenta armazenamento/redistribuição dos resultados com attribution apropriada;
- Geoapify usa dados principalmente de OpenStreetMap;
- busca textual de amenities + Place Details para website/telefone quando disponíveis;
- limite externo de 20 candidatos por busca;
- API key apenas por ambiente/configuração;
- payload persistido minimizado;
- `provider="auto"`: Geoapify quando há chave, Overpass experimental caso contrário;
- provider mock mantido para testes determinísticos;
- testes Geoapify via `httpx.MockTransport`, sem segredo real;
- CI automática removida de pushes de feature branch; PR/main continuam gates automáticos;
- estratégia/attribution documentadas em `docs/DISCOVERY_PROVIDERS.md`.

Pendente para fechar a validação real:

- configurar `LEADFORGE_GEOAPIFY_API_KEY` fora do repositório;
- executar 2–3 buscas pequenas em nichos/cidades diferentes;
- medir latência, quantidade retornada, cobertura de website/telefone e falhas;
- validar Site Analyzer → OpportunityAssessment → export usando os resultados;
- registrar attribution e custo/consumo observado.

Nenhuma credencial deve ser commitada ou colocada na documentação.

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
