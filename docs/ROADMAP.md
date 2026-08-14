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
- ranking do Discovery Engine baseado na oportunidade do módulo ativo;
- diagnósticos antigos mantidos apenas por compatibilidade durante a transição.

### v0.3.2 — Web evidence expansion — concluída

- declaração de viewport mobile;
- presença de formulário;
- links acionáveis de WhatsApp e telefone;
- caminho de contato/captação composto;
- CTA detectável em elementos interativos;
- HTTPS da URL final;
- cadeia de redirects observada;
- meta description;
- canonical;
- hierarquia básica de headings;
- cobertura de atributo `alt` em imagens;
- Web Development Opportunity `web-development-v2`;
- documentação explícita das limitações de cada sinal.

A versão continua sem afirmar performance, Core Web Vitals ou responsividade real sem uma fonte própria para isso.

### v0.3.3 — Web opportunity calibration — concluída

- conjunto inicial de cinco homepages públicas com revisão humana;
- 25 rótulos sobre identidade, serviços, localização, CTA e caminho de contato;
- comparador determinístico de falsos positivos, falsos negativos e unknowns;
- script reproduzível de calibração ao vivo;
- workflow manual de calibração no GitHub Actions;
- primeira execução: 22/25 matches, com três falsos positivos concentrados em localização;
- correção da detecção de cidade + UF brasileira;
- segunda execução no mesmo conjunto: 25/25 matches;
- teste de regressão para a correção;
- pesos de `web-development-v2` mantidos inalterados porque o erro estava na detecção, não na ponderação;
- limitações da pequena amostra documentadas em `docs/CALIBRATION.md`.

O resultado 25/25 vale somente para essa amostra inicial e não deve ser apresentado como 100% de acurácia real do produto.

### v0.3.4 — Export — concluída

- export de `DiscoveryRun` persistido em CSV e JSON;
- endpoint `GET /discovery-runs/{run_id}/export`;
- contrato JSON versionado como `discovery-export-v1`;
- empresa, fonte, ranking, score, confidence, serviço sugerido e findings preservados;
- Site Audit, signals e evidence preservados quando disponíveis;
- AI Discoverability mantido como diagnóstico separado;
- CSV achatado para uso manual, mantendo estruturas complexas em JSON compacto;
- proteção contra CSV formula injection em dados textuais públicos;
- export determinístico e sem novas chamadas a providers ou sites externos;
- testes de conteúdo, determinismo, endpoint e segurança do CSV;
- documentação em `docs/EXPORT.md`.

### v0.3.5 — Validação end-to-end do MVP — concluída

- gate reproduzível com quatro empresas públicas reais, em dois nichos/cidades;
- 4/4 sites auditados ao vivo na execução final;
- 0 falhas de auditoria nessa amostra;
- OpportunityAssessment criado para todos os sites auditados;
- ranking, deduplicação e exports CSV/JSON verificados de ponta a ponta;
- revisão manual dos candidatos priorizados;
- falso positivo em títulos longos detectado, corrigido e coberto por teste de regressão;
- query Overpass reduzida e erros externos mais observáveis;
- limitação do Overpass em runners cloud documentada;
- workflow de validação ao vivo mantido manual-only para não tornar a CI normal dependente de terceiros;
- detalhes em `docs/MVP_VALIDATION.md`.

A validação confirma o pipeline após a entrada normalizada de empresas e o fetch real dos sites. Ela **não confirma cobertura ou disponibilidade de produção do provider Overpass**.

### v0.3.6 — Discovery Provider hardening — próximo passo

Antes de abrir a Fase 2, fortalecer a parte do produto que realmente encontra empresas:

- definir critérios de provider de produção: cobertura, latência, custo, termos de uso, proveniência e estabilidade;
- avaliar fontes/API permitidas sem acoplar o Discovery Engine ao fornecedor;
- manter o provider mock para testes determinísticos;
- manter Overpass como provider experimental enquanto sua disponibilidade não for adequada ao uso pretendido;
- implementar somente um provider adicional quando houver uma escolha justificada;
- testar pequenas buscas reais em mais de um nicho/cidade;
- medir quantidade retornada, cobertura de website/contato comercial e falhas;
- documentar custo e limitações da fonte escolhida.

Não adicionar FreelancerProfile, preço, chat ou novos módulos de serviço durante esse milestone.

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
