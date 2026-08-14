# Evidências Web — v0.3.2

Este documento descreve os sinais objetivos coletados pelo Site Analyzer para o módulo `web_development`.

A regra principal é simples: **o LeadForge deve afirmar apenas o que a coleta realmente consegue observar**.

A análise atual trabalha principalmente sobre a página HTML solicitada e seu `robots.txt`. Portanto, ausência na página analisada não significa ausência em todo o site ou em todo o negócio.

## Sinais do Site Analyzer

| Sinal | O que confirma | O que não confirma |
|---|---|---|
| `https_enabled` | a URL final analisada usa HTTPS | qualidade da configuração TLS ou segurança geral do site |
| `mobile_viewport_present` | existe viewport com `width=device-width` | que o layout é realmente responsivo em todos os breakpoints |
| `form_present` | existe ao menos um elemento `<form>` na página | que o formulário funciona, converte ou existe em outras páginas |
| `whatsapp_link_present` | existe link acionável de WhatsApp detectável | que o canal é atendido ou responde rápido |
| `telephone_link_present` | existe link `tel:` detectável | qualidade do atendimento telefônico |
| `contact_channel_present` | existe canal acionável ou link de contato detectável | que todos os canais da empresa foram encontrados |
| `action_cta_present` | existe CTA textual/interativo compatível com regras atuais | qualidade visual, persuasão ou taxa de conversão do CTA |
| `lead_capture_path_present` | existe formulário ou caminho acionável de contato | qualidade do funil ou taxa de conversão |
| `meta_description_present` | existe meta description | que o texto está otimizado ou será exibido por buscadores |
| `canonical_present` | existe declaração de URL canônica | que a canonical está semanticamente correta para toda a arquitetura do site |
| `heading_structure_basic` | a página tem um único H1 inicial e não pula níveis na sequência analisada | conformidade completa de acessibilidade/semântica |
| `images_alt_attributes_complete` | todas as tags `<img>` da página possuem atributo `alt` | qualidade textual do alt; `alt=""` pode ser correto para imagem decorativa |
| `redirect_chain_reasonable` | a coleta observou no máximo dois redirects | performance de navegação ou qualidade geral da infraestrutura |

Os sinais anteriores de identidade, serviços, localização, indexabilidade, conteúdo textual e dados estruturados continuam disponíveis.

## Sinais compostos

Nem todo dado bruto deve virar um problema comercial sozinho.

Exemplo: `form_present=false` não é automaticamente um problema. Uma empresa pode usar corretamente um botão de WhatsApp como principal caminho de contato.

Por isso o score de oportunidade usa sinais compostos quando isso é mais defensável. Hoje o principal exemplo é:

```text
lead_capture_path_present
    = formulário presente
      OU canal de contato acionável presente
```

Assim, o LeadForge evita recomendar um formulário apenas porque não encontrou uma tag `<form>`.

## Escopo da conclusão

Preferir:

> Nenhum formulário foi encontrado na página analisada.

Evitar:

> A empresa não possui formulário.

Preferir:

> Não foi identificado um caminho acionável de contato na página analisada.

Evitar:

> A empresa perde clientes porque não tem canal de contato.

A segunda frase exigiria dados que o LeadForge ainda não possui.

## O que a v0.3.2 não mede

A versão atual **não mede**:

- Core Web Vitals;
- Lighthouse/PageSpeed score;
- tempo real de carregamento;
- comportamento responsivo real em diferentes telas;
- JavaScript renderizado em navegador;
- taxa de conversão;
- analytics;
- broken links do site inteiro;
- conformidade WCAG completa;
- receita, orçamento ou capacidade de pagamento da empresa;
- dor operacional interna.

Esses itens devem permanecer `unknown` até existir um coletor apropriado.

## Opportunity Score web v2

A versão `web-development-v2` usa uma matriz determinística de 100 pontos possíveis de evidência. Quanto maior a proporção de gaps confirmados entre os critérios efetivamente observados, maior o score de oportunidade.

`score` e `confidence` continuam separados:

- `score`: proporção ponderada de problemas confirmados entre os critérios observados;
- `confidence`: quanto da matriz de evidências o sistema conseguiu verificar.

Um score alto com confidence baixa deve ser interpretado como uma oportunidade potencial que ainda precisa de mais verificação, não como certeza de venda.
