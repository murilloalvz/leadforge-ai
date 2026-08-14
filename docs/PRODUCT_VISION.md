# Visão de Produto — LeadForge

## Definição canônica

**LeadForge é um copiloto comercial para freelancers.**

A proposta central é:

> O freelancer informa o que sabe fazer, e o LeadForge encontra empresas que podem precisar dessas habilidades, explica por que cada empresa é uma oportunidade e ajuda a preparar a abordagem comercial.

Essa é a visão de longo prazo do produto. Nenhuma implementação específica — desenvolvimento web, automação, SEO ou outra — deve ser confundida com o produto inteiro.

## Fluxo desejado no longo prazo

```text
habilidades do freelancer
        ↓
problemas detectáveis
        ↓
empresas compatíveis
        ↓
evidências + justificativa
        ↓
compatibilidade
        ↓
serviço sugerido
        ↓
preço sugerido
        ↓
abordagem
        ↓
proposta
        ↓
demonstração
```

## Público-alvo

Freelancers de áreas como:

- desenvolvimento web;
- design;
- social media;
- SEO;
- copywriting;
- edição de vídeo;
- gestão de tráfego;
- automação/RPA;
- análise de dados;
- suporte de TI.

A lista não é fechada. A arquitetura deve permitir novas categorias de serviço sem reconstruir discovery, evidências, persistência ou interface principal.

## Primeiro recorte de MVP

A visão é ampla, mas o MVP não é.

O primeiro módulo validado é:

- categoria de serviço: `web_development`;
- mercado inicial: negócios locais;
- objetivo: encontrar empresas, analisar sinais públicos do site e explicar oportunidades de melhoria web com evidência e confiança.

Desenvolvimento web é o **primeiro módulo**, não a identidade do LeadForge.

## Diferencial desejado

Ferramentas tradicionais de prospecção costumam responder:

```text
empresa + contato
```

O LeadForge deve evoluir para responder:

```text
empresa
+ problema detectado
+ evidência
+ nível de certeza
+ compatibilidade com o freelancer
+ serviço sugerido
+ preço
+ abordagem
+ proposta
+ demonstração
```

Nem todos esses itens pertencem ao MVP atual.

## Integridade das conclusões

O sistema deve diferenciar explicitamente:

- `confirmed`: evidência observável sustenta a conclusão;
- `strong_signal`: há um sinal forte, mas não confirmação direta;
- `inference`: interpretação plausível derivada de evidências;
- `unknown`: informação insuficiente.

Ausência de evidência não é evidência de ausência.

LLMs não podem inventar empresas, contatos, problemas, preços ou evidências. Quando o chat for introduzido, ele deve consultar dados reais do sistema e organizar respostas a partir deles.

## Perfil do freelancer — visão futura

O perfil poderá incluir:

- habilidades;
- serviços oferecidos;
- tecnologias e ferramentas;
- experiência;
- portfólio;
- localização;
- disponibilidade;
- tipos de projeto aceitos;
- complexidade máxima;
- preço mínimo;
- preferência por projeto, hora ou mensalidade.

O perfil servirá para evitar recomendações incompatíveis. Ele não pertence à fase atual até o núcleo de detecção de oportunidades estar validado.

## Precificação — princípio futuro

Preço não deve ser uma opinião solta de um LLM.

Um futuro Pricing Engine deverá usar dados com fonte, período, relevância e confiança, considerando escopo, complexidade, localização, experiência, prazo, revisões, integrações, custos e histórico do próprio freelancer.

O LLM poderá explicar a estimativa; não deverá fabricar a base da estimativa.

## Chat — princípio futuro

O chat será uma interface sobre dados reais:

```text
pergunta do usuário
        ↓
consulta ao perfil + prospects + evidências + assessments
        ↓
resposta organizada pelo LLM
```

Ele não deve substituir discovery, análise, scoring ou persistência por respostas inventadas.

## Demos — princípio futuro

Demonstrações devem ser adequadas ao serviço e sempre identificadas como conceituais e não oficiais.

Exemplos futuros:

- web: landing page baseada em template;
- design: conceito visual;
- social media: calendário e peças;
- copy: reescrita;
- SEO: mini auditoria;
- automação: fluxo/protótipo;
- dados: dashboard demonstrativo.

## Regra de desenvolvimento

A visão pode ser grande; cada versão deve continuar pequena.

Antes de adicionar uma nova fase, o núcleo anterior precisa estar funcional, testável e útil. Evitar diretórios, abstrações ou módulos vazios apenas para representar funcionalidades futuras.
