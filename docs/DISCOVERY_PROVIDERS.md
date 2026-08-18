# Discovery Providers — v0.3.7

O Discovery Engine não depende de uma única fonte. Providers transformam uma busca `nicho + cidade + UF` no contrato comum `DiscoveredBusiness`.

## Estratégia atual

- `auto` — usa Geoapify quando uma chave está configurada; senão usa OpenStreetMap/Overpass como fallback experimental;
- `geoapify` — provider preferido para discovery persistente;
- `openstreetmap` — Overpass experimental/fallback;
- `mock` — dados fictícios e determinísticos para testes.

## Por que Geoapify

Google Places foi descartado como provider persistente porque suas políticas de Places restringem caching/storage de conteúdo além das exceções permitidas. Isso não combina com o LeadForge, que precisa persistir prospects, evidências e exports.

Geoapify documenta armazenamento/redistribuição de resultados com as atribuições exigidas. A fonte principal dos dados de Places é OpenStreetMap.

Referências oficiais relevantes:

- Geoapify Places API;
- Geoapify Geocoding API;
- Geoapify Terms and Conditions;
- OpenStreetMap copyright/attribution;
- Google Places policies para a decisão de não usar Google no caminho persistente.

## Configuração

```env
LEADFORGE_GEOAPIFY_API_KEY=
LEADFORGE_GEOAPIFY_SEARCH_ENDPOINT=https://api.geoapify.com/v1/geocode/search
LEADFORGE_GEOAPIFY_PLACES_ENDPOINT=https://api.geoapify.com/v2/places
LEADFORGE_GEOAPIFY_DETAILS_ENDPOINT=https://api.geoapify.com/v2/place-details
LEADFORGE_GEOAPIFY_TIMEOUT_SECONDS=12
```

Nenhuma chave possui valor default ou deve ser commitada.

## Problema observado no gate real da v0.3.6

O smoke test real confirmou saúde do provider, mas mostrou que Forward Geocoding textual com `type=amenity` não é uma busca de negócios suficientemente precisa para ser a estratégia principal.

Exemplos observados:

- busca por clínicas de estética retornou hospitais;
- busca por academias retornou várias unidades da mesma rede nas primeiras posições.

Isso não invalida o Geoapify como fonte. O problema estava na forma como o LeadForge consultava a fonte.

## Fluxo Geoapify v0.3.7

Para nichos com mapeamento de categoria de alta confiança:

```text
nicho + cidade + UF
→ resolver categoria Geoapify conhecida
→ geocodificar somente a cidade
→ obter place_id da boundary
→ Places API com categories + filter=place:<place_id>
→ pós-validar categorias retornadas
→ remover duplicata exata por place_id ou nome+endereço
→ diversificar marcas sem apagar filiais legítimas
→ selecionar até o limite solicitado
→ Place Details somente dos candidatos selecionados
→ DiscoveredBusiness
```

A Places API é a primitiva apropriada para POIs por categoria e aceita filtro espacial por boundary retornada pelas APIs Geoapify.

### Categorias mapeadas inicialmente

O resolver começa pequeno e explícito:

- clínicas de estética: `commercial.health_and_beauty`, `service.beauty.spa`;
- dentistas/odontologia: `healthcare.dentist`;
- academias/fitness: `sport.fitness.fitness_centre`.

Novos nichos devem entrar somente com categoria documentada e teste. Não inferir categoria ampla apenas para aumentar recall.

### Nichos ainda não mapeados

Se não existe mapeamento confiável, o provider preserva o fallback textual da v0.3.6. Isso mantém a interface geral do LeadForge sem fingir precisão que ainda não foi validada.

O fallback deve ser tratado como menor confiança operacional e é candidato a evolução por novos mapeamentos de categoria.

## Relevância e deduplicação

A v0.3.7 separa três conceitos:

1. **relevância de nicho** — categoria retornada precisa corresponder à categoria solicitada;
2. **duplicata exata** — mesmo `place_id`, ou mesmo nome normalizado + mesmo endereço formatado;
3. **filial legítima** — mesma marca em endereço diferente não é apagada.

Filiais legítimas são preservadas, mas o provider intercala grupos de marca antes de aplicar o limite final. Assim uma rede pode aparecer mais de uma vez sem dominar todas as primeiras posições quando existem alternativas.

## Custo e volume

Para um nicho categorizado, uma busca pode envolver:

- uma chamada de geocoding da cidade, com cache em memória por `cidade + UF` durante a vida do provider;
- uma chamada Places API limitada e com over-fetch pequeno para permitir filtragem/diversidade;
- uma chamada Place Details apenas para cada candidato finalmente selecionado.

O over-fetch é limitado a `4 × limit`, com teto de 40 resultados. O limite público do Discovery continua pequeno e interativo; não existe coleta em massa.

## Payload persistido

O provider persiste apenas campos necessários ao LeadForge:

- place ID;
- nome;
- categorias;
- cidade/UF;
- endereço formatado;
- website e telefone comercial quando disponíveis;
- provenance reduzida;
- `discovery_mode`, indicando `places_category_boundary` ou o fallback textual existente.

Não persistimos o payload inteiro de Place Details.

## Attribution

Dados Geoapify/OSM devem manter atribuição adequada. OpenStreetMap attribution é obrigatória; requisitos adicionais do plano Geoapify utilizado também devem ser respeitados.

Exports e futura interface que exponham esses dados devem preservar provenance suficiente para atribuição.

## OpenStreetMap/Overpass

Overpass continua disponível sem credencial, mas experimental. Na v0.3.5 runners cloud observaram 502/timeouts mesmo com consultas pequenas.

Regras:

- consultas pequenas e user-triggered;
- sem paralelismo para aumentar throughput;
- sem bulk harvesting de infraestrutura pública compartilhada;
- missing fields permanecem unknown;
- disponibilidade do Overpass não é gate da CI normal.

## Testes

Geoapify continua testado sem segredo real com `httpx.MockTransport`.

A v0.3.7 adiciona regressões para:

- resolução explícita de nichos conhecidos;
- city boundary antes da busca de POIs;
- uso de `categories` + `filter=place:<place_id>`;
- descarte de categoria fora do nicho;
- deduplicação exata;
- diversidade de marca preservando filiais;
- fallback textual para nicho ainda não mapeado.

## Gate de saída da v0.3.7

Depois de CI verde, repetir **Geoapify Live Validation** com a chave já configurada e comparar com o artifact da v0.3.6.

O objetivo do novo gate não é apenas `provider_health_passed=true`. A revisão manual precisa confirmar melhora de relevância para os três nichos do smoke sample, sem regressão grave de cobertura, latência ou consumo.
