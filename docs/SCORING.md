# Scoring — estado atual

## Modelo canônico

A partir da v0.3.1, novos scores de oportunidade pertencem a `OpportunityAssessment` e são produzidos por um `OpportunityModule` específico de categoria.

O primeiro módulo ativo é `web_development` (`web-development-v1`).

Cada avaliação nova deve expor:

- categoria de serviço;
- score;
- confidence;
- versão;
- findings;
- resumo;
- serviço sugerido, quando aplicável.

`confidence` representa cobertura/qualidade da evidência observada, não chance de venda.

## Automation Opportunity — legado

O algoritmo `automation-v1.1` foi construído nas primeiras versões do projeto e continua no repositório para preservar trabalho, testes e compatibilidade com dados existentes.

Ele não é mais o scorer canônico do LeadForge e não determina o ranking principal da v0.3.1.

Quando automação/RPA voltar como categoria suportada para freelancers, deverá ser adaptada para um `OpportunityModule` próprio em vez de voltar a ser um score global do Prospect.

## Princípios obrigatórios

- scores devem ser determinísticos quando forem canônicos;
- pesos/regras devem ser versionados;
- ausência de evidência não pode virar evidência de ausência;
- findings devem distinguir `confirmed`, `strong_signal`, `inference` e `unknown`;
- módulos diferentes não devem ser misturados em um score opaco único;
- compatibilidade com um freelancer específico será um score futuro e separado da oportunidade do serviço.

Veja [`ARCHITECTURE.md`](ARCHITECTURE.md) e [`ROADMAP.md`](ROADMAP.md).
