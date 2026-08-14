# Discovery Providers — v0.3.6

O Discovery Engine não deve depender de uma única fonte. Providers transformam uma busca `nicho + cidade + UF` no contrato comum `DiscoveredBusiness`.

## Estratégia atual

Providers suportados:

- `auto` — usa Google Places quando uma chave está configurada; caso contrário usa OpenStreetMap/Overpass como fallback experimental;
- `google_places` — Google Places API (New), provider preferido para uso real quando configurado;
- `openstreetmap` — OpenStreetMap/Overpass, útil para experimentação e fallback, mas não tratado como infraestrutura de produção;
- `mock` — dados fictícios e determinísticos para testes e desenvolvimento sem rede.

## Google Places API (New)

Implementação: Text Search (New), por HTTP POST.

Configuração:

```env
LEADFORGE_GOOGLE_PLACES_API_KEY=
LEADFORGE_GOOGLE_PLACES_ENDPOINT=https://places.googleapis.com/v1/places:searchText
LEADFORGE_GOOGLE_PLACES_TIMEOUT_SECONDS=12
```

O provider não contém chave default e falha explicitamente quando `google_places` é solicitado sem credencial.

### Query

Uma busca como:

```text
niche=barbearia
city=Campinas
state=SP
```

é enviada como uma consulta textual equivalente a:

```text
barbearia em Campinas, SP, Brasil
```

O `pageSize` é limitado a no máximo 20 por chamada, mesmo que o contrato do LeadForge permita um `limit` maior.

### Field mask

O provider solicita somente:

```text
places.id
places.displayName
places.formattedAddress
places.primaryType
places.websiteUri
places.nationalPhoneNumber
places.googleMapsUri
```

Não solicita reviews, fotos, horários, rating, atmosfera ou outros campos que não são necessários para o MVP.

Essa lista é propositalmente explícita. Google Places exige FieldMask e a cobrança depende dos campos solicitados; portanto adicionar um campo novo é também uma decisão de custo/produto e deve ser revisado.

### Dados persistidos

O contrato normalizado recebe:

- ID externo do Google;
- nome;
- categoria/primary type;
- cidade e UF da query;
- website, quando retornado;
- telefone comercial, quando retornado;
- URL do Google Maps como provenance/source URL;
- payload reduzido com place ID, endereço formatado e primary type.

Não persistimos o objeto inteiro retornado pelo Google.

## Custo

A tabela oficial de preços deve ser consultada antes de aumentar volume ou campos.

Em agosto de 2026, os campos `websiteUri` e `nationalPhoneNumber` colocam Text Search na faixa Enterprise. A tabela oficial vigente informa uma franquia mensal e preço por mil eventos após a franquia. Esses valores podem mudar, portanto a documentação do Google é a fonte de verdade, não valores hardcoded no LeadForge.

Referências oficiais:

- https://developers.google.com/maps/documentation/places/web-service/text-search
- https://developers.google.com/maps/documentation/places/web-service/data-fields
- https://developers.google.com/maps/billing-and-pricing/pricing

## OpenStreetMap/Overpass

O provider Overpass permanece disponível, mas é experimental.

Durante a v0.3.5, runners cloud do GitHub Actions observaram 502 e timeouts mesmo com consultas pequenas. A query foi reduzida e os erros são classificados como timeout, HTTP externo ou resposta inválida.

Regras:

- consultas pequenas e user-triggered;
- sem paralelismo para aumentar throughput;
- sem coleta em massa usando infraestrutura pública compartilhada;
- cobertura ausente não vira evidência de ausência;
- disponibilidade do Overpass não é gate de CI.

## `auto`

`provider="auto"` é o default da API.

Com `LEADFORGE_GOOGLE_PLACES_API_KEY` configurada:

```text
auto → google_places
```

Sem chave:

```text
auto → openstreetmap
```

O `DiscoveryRun.provider` persiste o nome real do provider usado, não a palavra `auto`.

## Testes

Google Places é testado sem credencial real usando `httpx.MockTransport`.

Os testes verificam:

- API key no header correto;
- FieldMask sem campos desnecessários;
- query e limite;
- normalização para `DiscoveredBusiness`;
- minimização do payload persistido;
- erro explícito sem API key;
- tratamento seguro de HTTP 429.

Overpass continua com testes determinísticos de query, payload, HTTP externo e timeout.

## Limitação da v0.3.6

A integração Google Places pode ser validada deterministicamente sem segredo, mas uma validação real de cobertura/latência depende de uma API key habilitada e billing configurado. Nenhuma credencial deve ser commitada no repositório.
