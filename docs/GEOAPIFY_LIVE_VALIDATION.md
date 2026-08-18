# Geoapify Live Validation

Este gate valida o provider Geoapify real com uma amostra deliberadamente pequena e manual. Ele fica separado da CI normal porque requer credencial externa e acesso de rede real.

## Credencial

Configure este repository secret no GitHub Actions:

```text
LEADFORGE_GEOAPIFY_API_KEY
```

Nunca coloque a chave em `.env.example`, inputs de workflow, código-fonte, logs, issues, comentários de PR ou artifacts.

## Workflow

Execute **Geoapify Live Validation** manualmente no GitHub Actions. O workflow:

1. instala o backend;
2. verifica que o secret existe sem imprimi-lo;
3. roda `python scripts/validate_geoapify.py`;
4. envia `geoapify-live-validation.json` como artifact temporário.

A amostra padrão continua limitada a três buscas com até quatro empresas cada:

- clínicas de estética — Campinas/SP;
- dentistas — Jundiaí/SP;
- academias — Sorocaba/SP.

## Baseline real da v0.3.6

O primeiro gate real, executado em 18/08/2026, teve:

- 3/3 queries concluídas;
- 0 falhas de provider;
- 12 empresas retornadas;
- cobertura de website: 66,7%;
- cobertura de telefone: 66,7%;
- latência média aproximada: 2960,5 ms;
- latência máxima aproximada: 4257,9 ms;
- 15 requests estimadas no fluxo antigo.

`provider_health_passed=true`, mas a revisão manual encontrou ruído de relevância: hospitais em estética e concentração de uma mesma rede em academias.

Esse artifact é o baseline de comparação da v0.3.7.

## Estratégia v0.3.7

Para os três nichos do gate, o provider usa:

```text
geocode da cidade
→ place_id da boundary
→ Places API por categoria dentro da boundary
→ filtro/dedup/diversidade
→ Place Details dos candidatos selecionados
```

Por isso o relatório agora usa schema `geoapify-live-validation-v2` e registra `discovery_mode` e estimativa de chamadas por query.

A estimativa para uma query categorizada é:

```text
1 city-geocode + 1 places-search + N place-details selecionados
```

O cache de boundary pode reduzir chamadas quando várias buscas reutilizam a mesma cidade durante a mesma instância do provider.

## Report

O relatório registra:

- quantidade de queries bem-sucedidas e falhas;
- total de empresas;
- cobertura de website e telefone;
- latência média e máxima;
- volume estimado de API requests;
- `discovery_mode` por query;
- nome público, categoria e external ID para revisão manual;
- falhas sanitizadas do provider.

Ele **não** exporta URL de website, número de telefone, API key ou payload bruto do provider.

## Semântica de aprovação

`provider_health_passed=true` continua significando apenas:

- todas as queries da amostra terminaram sem erro de provider; e
- pelo menos uma empresa foi retornada no conjunto.

Isso não basta sozinho para aprovar a v0.3.7.

A revisão manual também precisa confirmar:

- resultados materialmente compatíveis com o nicho;
- ausência do falso positivo conhecido de hospitais em estética;
- melhor diversidade quando houver marcas alternativas;
- nenhuma regressão grave de cobertura de website/telefone;
- latência e consumo compatíveis com uma busca interativa pequena.

Cobertura percentual não é gate rígido: quatro resultados por nicho formam um smoke sample, não uma medição de recall de produção.

Se o gate falhar, inspecione logs e artifact antes de alterar timeout, category mapping, dedup ou provider selection. Não esconda falha externa retornando conjunto vazio como se fosse sucesso.
