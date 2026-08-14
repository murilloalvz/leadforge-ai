# LeadForge AI

O LeadForge é um projeto de **copiloto comercial para freelancers**.

A visão do produto é simples:

> O freelancer informa o que sabe fazer, e o LeadForge encontra empresas que podem precisar dessas habilidades, explica por que cada empresa é uma oportunidade e ajuda a preparar a abordagem comercial.

O produto final não será exclusivo para desenvolvimento web, automação ou SEO. Essas áreas entram como **módulos de oportunidade**. O primeiro módulo validado no MVP é `web_development`, focado inicialmente em negócios locais.

A visão completa está em [`docs/PRODUCT_VISION.md`](docs/PRODUCT_VISION.md) e o planejamento em [`docs/ROADMAP.md`](docs/ROADMAP.md).

## Estado atual — v0.3.2

A base já possui:

- FastAPI;
- SQLAlchemy + SQLite;
- migrations com Alembic;
- prospects e evidências com fonte/confiança;
- Discovery Engine por nicho + cidade + UF;
- provider mock;
- provider inicial OpenStreetMap/Overpass;
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
- CI, lint e testes.

Ainda **não** existem FreelancerProfile, precificação, chat com IA, abordagem automática, proposta ou demo. Essas fases foram mantidas fora do escopo de propósito.

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

Na v0.3.2, além dos sinais anteriores, o analisador observa:

- se a URL final usa HTTPS;
- declaração de viewport mobile;
- formulário na página analisada;
- links acionáveis de WhatsApp e telefone;
- caminho detectável de contato/captação;
- CTA em elementos interativos;
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

O GitHub Actions valida lint, testes, migrations e seed.

## Próximo recorte

A próxima etapa planejada é **v0.3.3 — Web opportunity calibration**: testar o analisador contra um pequeno conjunto de empresas reais revisadas manualmente, registrar falsos positivos/negativos e só então ajustar pesos e regras.

Ainda não é hora de adicionar perfil do freelancer, preço, chat, outreach ou demo.

Veja o plano completo em [`docs/ROADMAP.md`](docs/ROADMAP.md).

## Uso de IA no desenvolvimento

Uso IA/Codex como ferramenta de implementação, revisão e testes. Arquitetura, decisões de produto, critérios de avaliação e validação final continuam sendo dirigidas e revisadas por mim.
