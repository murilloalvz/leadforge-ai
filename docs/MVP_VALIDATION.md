# Validação end-to-end do MVP — v0.3.5

## Objetivo

A v0.3.5 foi usada como gate antes de integrar o núcleo atual do LeadForge. O objetivo não era adicionar funcionalidades, e sim verificar se o fluxo já construído funciona de ponta a ponta com empresas e sites públicos reais.

Fluxo validado:

```text
empresas públicas conhecidas
→ Discovery Provider normalizado
→ Prospect + deduplicação
→ fetch real do site
→ Site Analyzer
→ OpportunityAssessment web_development
→ ranking
→ export CSV/JSON
```

## Amostra

Foram usadas quatro empresas públicas, em dois grupos distintos:

- clínicas de estética em Belo Horizonte/MG:
  - Clin Clin — `https://www.clinclin.com.br/`
  - Beauty S.A. — `https://beautysa.com.br/`
- barbearias em Campinas/SP:
  - A Barbearia — `https://www.abarbearia.net/`
  - Estação Campinas — `https://www.estacaocampinas.com.br/`

A lista é fixa no script de validação apenas para tornar o gate reproduzível. O HTML não é copiado para o repositório: as páginas continuam sendo acessadas ao vivo pelo Site Analyzer.

## O que o gate verifica

O script `backend/scripts/validate_mvp.py` verifica:

- conclusão do Discovery Run;
- ranking contíguo;
- ausência de prospects duplicados no mesmo run;
- criação de OpportunityAssessment para candidatos auditados;
- auditoria real das URLs públicas;
- consistência entre o run persistido e os exports CSV/JSON;
- contrato JSON `discovery-export-v1`.

O workflow `MVP Live Validation` é manual. Ele não faz parte da CI normal porque depende de sites de terceiros que podem mudar ou ficar indisponíveis.

## Resultado do gate

Na execução final usada para fechar a v0.3.5:

- 4 empresas entraram no pipeline;
- 4 sites foram auditados;
- 0 auditorias falharam;
- 4 OpportunityAssessments foram criados;
- os dois runs mantiveram ranking válido;
- CSV e JSON permaneceram consistentes com os runs persistidos.

Os quatro casos receberam `low_opportunity`. Isso não é tratado como falha: o sistema deve ser capaz de concluir que um site observado tem poucos gaps, em vez de fabricar leads quentes.

## Bug encontrado durante a revisão manual

A revisão dos resultados encontrou um falso positivo em `descriptive_titles`.

A regra anterior tratava qualquer `<title>` acima de 75 caracteres como "pouco descritivo". Isso misturava comprimento do título com capacidade de descrever o negócio.

A regra foi corrigida para considerar um título suficientemente específico como descritivo mesmo quando é longo. Foi adicionado um teste de regressão para impedir que esse erro volte.

Os pesos de `web-development-v2` não foram alterados, porque o problema estava no detector, não na ponderação.

## Discovery via OpenStreetMap/Overpass

Também foi tentada uma validação usando diretamente o provider OpenStreetMap/Overpass a partir do GitHub Actions.

Essa parte não se mostrou confiável no ambiente de runner cloud: ocorreram respostas 502 e timeouts mesmo com uma consulta menor e com endpoint alternativo. Por isso:

- o provider Overpass continua configurável e disponível para experimentação;
- a query foi reduzida e os erros de timeout/HTTP ficaram mais explícitos;
- o provider possui testes determinísticos para query, payload e tratamento de erro;
- disponibilidade do Overpass em GitHub Actions **não** é usada como gate de merge;
- a cobertura/recall real do provider ainda precisa ser avaliada de uma rede adequada ou com um provider de produção posterior.

A validação v0.3.5 portanto prova o pipeline após a entrada normalizada de empresas e a análise real dos sites. Ela **não prova** cobertura, disponibilidade ou qualidade de recall do provider Overpass.

## Limitações

Esta validação não prova que o LeadForge está pronto para produção.

Principais limites:

- amostra pequena, com quatro empresas;
- empresas escolhidas, não descobertas pelo provider ao vivo no gate final;
- sites externos são mutáveis;
- o módulo ativo continua sendo apenas `web_development`;
- não há FreelancerProfile nem Compatibility Engine;
- não há precificação, chat, proposta, outreach ou demo;
- não há medição real de responsividade, performance ou Core Web Vitals;
- o fetcher SSRF ainda é proteção de MVP, não uma sandbox de rede de produção.

## Conclusão

O núcleo atual é coerente e utilizável como base do Opportunity Intelligence MVP:

```text
Prospect
→ Evidence
→ Site Analyzer
→ OpportunityAssessment
→ ranking
→ export
```

A v0.3.5 fecha a Fase 1 técnica deste recorte sem ampliar prematuramente a superfície do produto. A próxima evolução deve continuar respeitando a visão canônica do LeadForge como copiloto comercial para freelancers.