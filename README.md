# LeadForge AI

O LeadForge é um projeto de **copiloto comercial para freelancers**.

A ideia é simples:

> O freelancer informa o que sabe fazer, e o LeadForge encontra empresas que podem precisar dessas habilidades, explica por que cada empresa é uma oportunidade e ajuda a preparar a abordagem comercial.

O produto final não será exclusivo para desenvolvimento web, automação ou SEO. Essas áreas entram como **módulos de oportunidade**. O primeiro módulo validado no MVP é `web_development`, focado inicialmente em negócios locais.

A visão completa está em [`docs/PRODUCT_VISION.md`](docs/PRODUCT_VISION.md) e o planejamento em [`docs/ROADMAP.md`](docs/ROADMAP.md).

## Estado atual — v0.3.5

A base já possui:

- FastAPI;
- SQLAlchemy + SQLite;
- migrations com Alembic;
- prospects e evidências com fonte/confiança;
- Discovery Engine por nicho + cidade + UF;
- provider mock;
- provider experimental OpenStreetMap/Overpass;
- deduplicação e reutilização de prospects;
- Site Analyzer por URL;
- leitura de HTML, `robots.txt`, `noindex`, `X-Robots-Tag` e JSON-LD;
- AI Discoverability como diagnóstico separado;
- proteção inicial contra SSRF;
- contrato genérico de `OpportunityModule`;
- persistência de `OpportunityAssessment`;
- primeiro módulo de oportunidade: `web_development`;
- Web Development Opportunity `web-development-v2`;
- sinais objetivos de viewport, formulário, contato, CTA, HTTPS, headings, canonical, meta description e imagens;
- conjunto inicial de calibração com sites públicos reais revisados manualmente;
- métricas de falsos positivos, falsos negativos e unknowns;
- script e workflow manual de calibração;
- export de Discovery Runs em CSV e JSON;
- contrato de export JSON versionado;
- proteção contra CSV formula injection;
- validação end-to-end com quatro sites públicos reais;
- workflow manual de validação ao vivo;
- CI, lint e testes.

Ainda **não** existem FreelancerProfile, precificação, chat com IA, abordagem automática, proposta ou demo. Essas fases continuam fora do escopo de propósito.

## Arquitetura mental

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

Hoje existe apenas:

```text
Opportunity Modules
└── web_development
```

No futuro poderão existir módulos como SEO, design, social media, automação ou dados sem transformar essas categorias no núcleo do produto.

## Integridade das conclusões

O LeadForge não deve transformar hipótese em fato.

Os findings usam uma taxonomia explícita:

- `confirmed` — sustentado por evidência observável;
- `strong_signal` — sinal forte, mas sem confirmação direta;
- `inference` — interpretação plausível;
- `unknown` — informação insuficiente.

No MVP atual o módulo web continua deliberadamente conservador e trabalha principalmente com `confirmed` e `unknown`.

Uma regra importante é o **escopo da evidência**. Por exemplo:

> Nenhum formulário foi encontrado na página analisada.

é diferente de afirmar:

> A empresa não possui formulário.

O segundo enunciado exigiria analisar mais do que a página atual.

## Discovery

Exemplo:

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

Quando um site é auditado, o candidato pode retornar uma avaliação como:

```json
{
  "name": "Empresa Exemplo",
  "priority_bucket": "medium_opportunity",
  "opportunity": {
    "service_category": "web_development",
    "score": 43,
    "confidence": 1.0,
    "version": "web-development-v2",
    "summary": "Foram confirmados pontos de melhoria web com base em sinais observáveis.",
    "recommended_service": "Melhoria de site institucional",
    "findings": []
  }
}
```

Os campos antigos de Automation Opportunity continuam persistidos temporariamente por compatibilidade com versões anteriores, mas **não são mais o conceito principal nem determinam o ranking atual**.

### Estado do provider OpenStreetMap/Overpass

O provider inicial continua disponível como fonte experimental e configurável. Durante a validação v0.3.5, chamadas feitas a partir de runners cloud do GitHub Actions sofreram 502/timeouts mesmo com consultas pequenas e endpoint alternativo.

Por isso a disponibilidade do Overpass **não é usada como gate de CI**. O provider possui testes determinísticos para query, payload e tratamento de erro, mas ainda não deve ser tratado como a fonte definitiva do MVP.

O próximo milestone é justamente escolher/endurecer um caminho de discovery suficientemente confiável para uso real.

## Exportando um run

Depois que um Discovery Run foi concluído, ele pode ser exportado sem repetir a busca ou reanalisar os sites.

CSV:

```http
GET /discovery-runs/1/export?format=csv
```

JSON:

```http
GET /discovery-runs/1/export?format=json
```

O JSON usa o contrato:

```text
discovery-export-v1
```

Ele preserva de forma estruturada:

- dados do run;
- empresa e fonte;
- rank e priority bucket;
- OpportunityAssessment;
- score e confidence;
- serviço sugerido;
- findings e certainty;
- Site Audit, signals e evidence quando disponíveis;
- AI Discoverability separadamente.

O CSV achata os campos mais úteis para abrir em planilha. Findings e evidências complexas continuam disponíveis em colunas JSON para não perder informação.

O export é determinístico para o mesmo estado persistido e **não faz novas chamadas de rede**.

Também existe proteção contra CSV formula injection: textos públicos começando com caracteres que planilhas poderiam interpretar como fórmula são neutralizados antes da escrita no CSV.

Mais detalhes em [`docs/EXPORT.md`](docs/EXPORT.md).

## Site Analyzer

Também é possível analisar uma URL diretamente:

```http
POST /site-audits
Content-Type: application/json

{
  "url": "https://exemplo.com.br"
}
```

O Site Analyzer produz sinais e evidências reutilizáveis por diferentes diagnósticos. AI Discoverability continua separado da OpportunityAssessment.

Entre os sinais observados estão:

- se a URL final usa HTTPS;
- declaração de viewport mobile;
- formulário na página analisada;
- links acionáveis de WhatsApp e telefone;
- caminho detectável de contato/captação;
- CTA em elementos interativos;
- identidade, serviços e localização;
- meta description;
- canonical;
- hierarquia básica de headings;
- cobertura de atributo `alt` nas imagens;
- cadeia de redirects observada.

Mais detalhes e limitações estão em [`docs/WEB_EVIDENCE.md`](docs/WEB_EVIDENCE.md).

## O que esses sinais não provam

`mobile_viewport_present=true` significa apenas que a página declara um viewport adequado. **Não prova que o layout inteiro é responsivo.**

Da mesma forma, o LeadForge ainda não afirma:

- Core Web Vitals;
- Lighthouse/PageSpeed score;
- performance real;
- taxa de conversão;
- qualidade do atendimento;
- orçamento da empresa;
- dor operacional interna.

Esses itens permanecem desconhecidos até existir uma fonte adequada.

## Web Development Opportunity v2

O score atual é determinístico e versionado como `web-development-v2`.

Ele usa sinais compostos quando isso evita conclusões ruins. Exemplo: a ausência de um `<form>` não é pontuada como problema por si só se a página já possui um caminho de contato acionável, como WhatsApp.

`score` e `confidence` continuam separados:

- `score` representa a proporção ponderada de gaps confirmados entre os critérios observados;
- `confidence` representa quanto da matriz relevante foi de fato verificada.

## Calibração v0.3.3

A v0.3.3 adicionou uma primeira camada de validação contra sites públicos reais revisados manualmente.

O conjunto inicial contém cinco homepages e 25 rótulos sobre identidade, serviços, localização, CTA e caminho de contato/captação.

Na primeira execução, o analisador acertou 22 de 25 rótulos. Os três erros eram falsos positivos concentrados em `location_clearly_described`.

A análise mostrou que o detector não reconhecia bem informações explícitas em formatos como `Campinas/SP`. A regra foi corrigida e ganhou teste de regressão. Os pesos do Opportunity Score **não foram alterados**.

Executando novamente o mesmo conjunto, os 25 rótulos bateram com a revisão humana.

Isso **não significa 100% de acurácia no mundo real**: é uma amostra pequena, com cinco sites e predominância de exemplos positivos. Ela serve como smoke benchmark auditável e como prova de que o processo de calibração consegue encontrar e corrigir erros concretos.

Detalhes em [`docs/CALIBRATION.md`](docs/CALIBRATION.md).

## Validação end-to-end v0.3.5

A v0.3.5 executou o pipeline completo com quatro empresas públicas reais em dois grupos: clínicas de estética em Belo Horizonte/MG e barbearias em Campinas/SP.

Na execução final:

- 4 empresas entraram no pipeline;
- 4 sites foram auditados ao vivo;
- nenhuma auditoria falhou;
- todos os candidatos auditados receberam OpportunityAssessment;
- ranking e deduplicação permaneceram consistentes;
- exports CSV/JSON bateram com os runs persistidos.

A revisão manual também encontrou um falso positivo: títulos de página longos eram marcados como "pouco descritivos" apenas por ultrapassarem 75 caracteres. A regra foi corrigida e ganhou teste de regressão, sem alterar os pesos do score.

Os quatro sites da amostra final receberam `low_opportunity`. Isso é aceitável e desejável: o LeadForge não deve fabricar uma oportunidade forte quando os gaps observados são pequenos.

A amostra não valida cobertura/recall do provider Overpass. Detalhes e limitações estão em [`docs/MVP_VALIDATION.md`](docs/MVP_VALIDATION.md).

## Diagnósticos separados

### Web Development Opportunity

Responde:

> Existem problemas observáveis neste site que tornam a empresa uma oportunidade plausível para um freelancer de desenvolvimento web?

### AI Discoverability

Responde:

> O site está preparado para ser encontrado e entendido por mecanismos de busca e experiências de IA?

São perguntas diferentes e continuam com scores separados.

## Segurança e privacidade

O projeto trabalha com prospecção B2B legítima e informações comerciais públicas.

Não é objetivo:

- coletar dados privados desnecessários;
- contornar login, CAPTCHA ou paywall;
- montar coleta em massa sobre infraestrutura pública;
- usar identidades falsas;
- disparar spam;
- apresentar inferências como fatos.

O fetcher de URLs possui proteções SSRF adequadas ao MVP, mas ainda não deve ser considerado uma sandbox de rede pronta para exposição pública irrestrita.

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

A documentação interativa da API fica em `/docs`.

## Testes

Dentro de `backend/`:

```bash
ruff check .
pytest -q
```

O GitHub Actions valida lint, testes, migrations e seed. Workflows que dependem de sites reais permanecem manuais para evitar CI flaky por indisponibilidade de terceiros.

## Próximo recorte

A próxima etapa planejada é **v0.3.6 — Discovery Provider hardening**.

Antes de iniciar FreelancerProfile e Compatibility Engine, precisamos tornar a descoberta de empresas mais confiável: avaliar uma fonte/API permitida com cobertura, latência, custo, proveniência e estabilidade adequados e então implementar apenas um provider adicional atrás da interface já existente.

Ainda não é hora de adicionar preço, chat, outreach, demo ou novos módulos de serviço.

Veja o plano completo em [`docs/ROADMAP.md`](docs/ROADMAP.md).

## Uso de IA no desenvolvimento

Uso IA/Codex como ferramenta de implementação, revisão e testes. Arquitetura, decisões de produto, critérios de avaliação e validação final continuam sendo dirigidas e revisadas por mim.
