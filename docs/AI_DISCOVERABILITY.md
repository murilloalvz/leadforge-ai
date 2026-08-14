# AI Discoverability

Além do score de oportunidade de automação, o LeadForge tem um segundo diagnóstico para sites: **prontidão para descoberta por mecanismos de busca e sistemas de IA**.

O nome é proposital. O sistema não promete que um site "será recomendado por IA". A ferramenta mede condições técnicas e de conteúdo que podem facilitar descoberta, entendimento e citação.

## Dois diagnósticos, dois problemas

1. **Automation Opportunity Score** — vale a pena abordar esse negócio com uma automação?
2. **AI Discoverability Score** — o site está bem preparado para ser entendido e descoberto por mecanismos de busca e experiências de IA?

Eles não são combinados em uma nota única.

## O que a v0.2 já faz

A v0.2 recebe uma URL pública e coleta sinais reais da página principal e do `robots.txt` do host final.

O analisador observa:

- resposta HTTP da página;
- redirects;
- `Content-Type`;
- `meta robots`;
- `X-Robots-Tag`;
- permissão de Googlebot no `robots.txt`;
- permissão de OAI-SearchBot no `robots.txt`;
- título e headings;
- quantidade aproximada de texto visível;
- indícios de seção de serviços;
- indícios de endereço/localização;
- JSON-LD;
- tipos Schema.org encontrados;
- nomes e endereços presentes nos dados estruturados.

Essas observações são transformadas nos sinais do score `ai-discoverability-v1`.

## Critérios do score v1

- página pública respondendo normalmente;
- conteúdo indexável;
- Googlebot permitido;
- OAI-SearchBot permitido;
- informações importantes disponíveis em texto;
- identidade do negócio clara;
- serviços descritos claramente;
- localização/área atendida clara;
- títulos de página descritivos;
- dados estruturados presentes;
- marcação `LocalBusiness` quando fizer sentido;
- dados estruturados coerentes com o conteúdo visível.

Bloqueios importantes, como página inacessível ou `noindex`, limitam a nota mesmo que outros sinais sejam positivos.

`confidence` representa quanto do conjunto de critérios foi realmente observado. Não é probabilidade de recomendação, ranking ou conversão.

## Heurísticas atuais

Alguns sinais não podem ser determinados perfeitamente olhando apenas uma homepage. Na v0.2, critérios como "serviços claramente descritos" e "localização clara" usam heurísticas simples e explicáveis.

Por isso o resultado guarda as evidências usadas, e os pesos deverão ser recalibrados com uso real.

## Segurança do fetch

Como o analisador faz requisições server-side para URLs recebidas pela API, existe risco de SSRF.

A implementação atual:

- aceita somente `http` e `https`;
- bloqueia credenciais embutidas na URL;
- bloqueia localhost e endereços IP não públicos;
- resolve o DNS antes de cada request;
- revalida cada redirect;
- limita redirects;
- limita tamanho de resposta;
- aplica timeout;
- desativa uso automático de proxies do ambiente;
- não executa JavaScript.

Ainda assim, essa proteção deve ser considerada **MVP**, não isolamento de rede completo. Uma versão exposta publicamente deverá endurecer a defesa contra DNS rebinding e outras diferenças entre resolução e conexão.

## O que não vira regra mágica

Não damos pontos simplesmente por ter `llms.txt`, "texto escrito para IA" ou algum markup inventado.

Os fundamentos técnicos e de conteúdo continuam sendo a base da análise. Para ChatGPT Search, a OpenAI orienta publishers que desejam ter conteúdo descoberto e citado a não bloquear o `OAI-SearchBot`.

## Referências oficiais

- Google Search Central — AI features and your website: https://developers.google.com/search/docs/appearance/ai-features
- Google Search Central — optimizing for generative AI features: https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
- OpenAI — Publishers and Developers FAQ: https://help.openai.com/en/articles/12627856-publishers-and-developers-faq
- Schema.org — LocalBusiness: https://schema.org/LocalBusiness

## Limitações atuais

A v0.2 ainda não:

- executa JavaScript;
- navega por múltiplas páginas do site;
- compara concorrentes;
- consulta Search Console ou analytics;
- mede presença real em respostas de modelos;
- encontra empresas automaticamente.

O próximo passo é ligar essas auditorias ao pipeline de prospects e depois adicionar discovery/enrichment por fontes públicas permitidas.
