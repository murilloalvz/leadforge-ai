# AI Discoverability

Além do score de oportunidade de automação, o LeadForge terá um segundo diagnóstico para sites: **prontidão para descoberta por mecanismos de busca e sistemas de IA**.

O nome é proposital. O sistema não deve prometer que um site "será recomendado por IA". Nenhuma análise externa consegue garantir isso. A ideia é medir se o site tem condições técnicas e de conteúdo que facilitam descoberta, entendimento e citação.

## Por que isso combina com o LeadForge

Quando o sistema encontra um prospect, muitas vezes já vai visitar o site para coletar evidências. A mesma coleta pode gerar dois resultados separados:

1. **Automation Opportunity Score** — vale a pena abordar esse negócio com uma automação?
2. **AI Discoverability Score** — o site está bem preparado para ser entendido e descoberto por mecanismos de busca e experiências de IA?

Isso abre uma segunda linha de serviço sem misturar os dois problemas.

## O que o score v1 observa

O motor já existe de forma determinística, mas ainda não há crawler real na v0.1.

Critérios iniciais:

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

Bloqueios técnicos importantes, como página não pública ou `noindex`, limitam a nota mesmo que o restante do conteúdo seja bom.

## O que NÃO deve virar regra mágica

Não vamos dar pontos simplesmente por ter `llms.txt`, "texto escrito para IA" ou algum markup inventado. As orientações atuais do Google dizem que os fundamentos de SEO continuam válidos para os recursos generativos e que não existe markup especial obrigatório para aparecer nesses recursos.

Para ChatGPT Search, a OpenAI orienta que sites que desejam ter conteúdo descoberto e citado não bloqueiem o `OAI-SearchBot`.

Por isso, o score deve continuar baseado em sinais verificáveis e explicáveis.

## Referências oficiais

- Google Search Central — AI features and your website: https://developers.google.com/search/docs/appearance/ai-features
- Google Search Central — optimizing for generative AI features: https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
- OpenAI — Publishers and Developers FAQ: https://help.openai.com/en/articles/12627856-publishers-and-developers-faq
- Schema.org — LocalBusiness: https://schema.org/LocalBusiness

## Próximo passo técnico

Na v0.2 o crawler/enrichment poderá transformar observações do site nesses sinais. O resultado deve ser armazenado separadamente do score comercial, com versão, componentes, evidências e confidence.
