# Discovery Providers — v0.3.6

O Discovery Engine não deve depender de uma única fonte. Providers transformam uma busca `nicho + cidade + UF` no contrato comum `DiscoveredBusiness`.

## Estratégia atual

- `auto` — usa Geoapify quando uma chave está configurada; senão usa OpenStreetMap/Overpass como fallback experimental;
- `geoapify` — provider preferido para discovery persistente;
- `openstreetmap` — Overpass experimental/fallback;
- `mock` — dados fictícios e determinísticos para testes.

## Por que Geoapify

Na pesquisa da v0.3.6, Google Places foi descartado como provider persistente porque suas políticas restringem caching/storage do conteúdo de Places além das exceções permitidas. Isso não combina com o fluxo do LeadForge, que precisa persistir prospects, evidências e exports.

Geoapify documenta explicitamente que resultados do Places API podem ser armazenados e redistribuídos, desde que as atribuições exigidas sejam respeitadas. A fonte principal dos dados de Places é OpenStreetMap.

Referências:

- https://www.geoapify.com/places-api/
- https://www.geoapify.com/terms-and-conditions/
- https://www.openstreetmap.org/copyright
- https://developers.google.com/maps/documentation/places/web-service/policies

## Configuração

```env
LEADFORGE_GEOAPIFY_API_KEY=
LEADFORGE_GEOAPIFY_SEARCH_ENDPOINT=https://api.geoapify.com/v1/geocode/search
LEADFORGE_GEOAPIFY_DETAILS_ENDPOINT=https://api.geoapify.com/v2/place-details
LEADFORGE_GEOAPIFY_TIMEOUT_SECONDS=12
```

Nenhuma chave possui valor default ou deve ser commitada.

## Fluxo Geoapify

Para preservar a busca livre `nicho + cidade + UF`, o provider usa duas etapas pequenas:

1. Forward Geocoding com `type=amenity`, query textual e filtro Brasil;
2. Place Details por `place_id` para obter website/telefone quando disponíveis.

A busca é limitada a no máximo 20 candidatos por chamada. O provider normaliza somente os campos usados pelo LeadForge:

- place ID;
- nome;
- categoria;
- cidade/UF;
- endereço formatado;
- website e telefone comercial quando disponíveis;
- provenance do provider.

Não persistimos o payload inteiro de Place Details.

## Attribution

Dados Geoapify/OSM devem manter atribuição adequada. OpenStreetMap attribution é obrigatória; no plano gratuito do Geoapify, Geoapify attribution também é exigida.

Exports ou futura interface que exponham esses dados devem carregar a informação de provenance necessária para permitir essa atribuição.

## Custo e volume

Geoapify usa modelo por créditos/requisições. A versão atual faz uma busca e, para cada candidato normalizado, uma chamada pequena de Place Details. Portanto aumentar `limit` aumenta também o consumo de API.

A v0.3.6 limita discovery externo a pequenas buscas interativas e não implementa coleta em massa.

## OpenStreetMap/Overpass

Overpass continua disponível sem credencial, mas experimental. Na v0.3.5 runners cloud observaram 502/timeouts mesmo com consultas pequenas.

Regras:

- consultas pequenas e user-triggered;
- sem paralelismo para aumentar throughput;
- sem bulk harvesting de infraestrutura pública compartilhada;
- missing fields permanecem unknown;
- disponibilidade do Overpass não é gate da CI normal.

## `auto`

Com `LEADFORGE_GEOAPIFY_API_KEY`:

```text
auto → geoapify
```

Sem chave:

```text
auto → openstreetmap
```

`DiscoveryRun.provider` registra o provider real utilizado.

## Testes

Geoapify é testado sem segredo real via `httpx.MockTransport`. Os testes cobrem query, filtro Brasil, limite, Place Details, normalização, payload minimizado, chave ausente e erros externos.

Overpass mantém testes determinísticos de query, payload, HTTP externo e timeout.

## Gate restante

Para validar o provider real ainda falta configurar uma chave Geoapify fora do repositório e executar 2–3 buscas pequenas, medindo latência, quantidade de empresas, cobertura de website/telefone e falhas.
