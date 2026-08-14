# Export de Discovery Runs — v0.3.4

A v0.3.4 permite exportar um `DiscoveryRun` já persistido sem executar uma nova busca ou uma nova análise de site.

O export é uma **fotografia do estado daquele run**. Isso é importante porque sites e fontes públicas mudam com o tempo; exportar não deve recalcular resultados silenciosamente.

## Endpoint

```http
GET /discovery-runs/{run_id}/export?format=csv
```

ou:

```http
GET /discovery-runs/{run_id}/export?format=json
```

Formatos aceitos:

- `csv`;
- `json`.

O padrão é `csv`.

## JSON

O JSON usa o schema versionado:

```text
discovery-export-v1
```

Estrutura principal:

```json
{
  "schema_version": "discovery-export-v1",
  "run": {},
  "candidates": []
}
```

Cada candidato preserva:

- rank e priority bucket;
- dados comerciais públicos do prospect;
- URL/categoria da fonte;
- OpportunityAssessment atual;
- findings com certainty e evidence keys;
- Site Audit quando existir;
- signals e evidence do Site Analyzer;
- AI Discoverability como diagnóstico separado.

Campos antigos de Automation Opportunity não fazem parte do novo contrato de export. Eles continuam existentes apenas por compatibilidade interna com versões antigas.

## CSV

O CSV é voltado para uso manual em Excel, Google Sheets, LibreOffice ou ferramentas de análise.

Ele contém colunas como:

- `run_id`;
- `rank`;
- `prospect_id`;
- `name`;
- `niche`;
- `city`;
- `state`;
- `website`;
- `phone`;
- `source_url`;
- `source_category`;
- `priority_bucket`;
- `service_category`;
- `opportunity_score`;
- `opportunity_confidence`;
- `opportunity_version`;
- `opportunity_summary`;
- `recommended_service`;
- `confirmed_findings_count`;
- `unknown_findings_count`;
- `confirmed_findings`;
- `findings_json`;
- `site_audit_id`;
- `site_signals_json`;
- `site_evidence_json`;
- `ai_discoverability_score`;
- `ai_discoverability_confidence`.

Estruturas aninhadas são serializadas como JSON compacto dentro da célula para não perder informação.

## Segurança do CSV

Dados públicos podem conter texto começando com caracteres interpretados como fórmulas por planilhas, por exemplo:

```text
=HYPERLINK(...)
+SUM(...)
@...
```

Por isso, valores textuais que começam com `=`, `+`, `-` ou `@` são neutralizados no CSV com um prefixo textual antes da escrita.

Essa proteção vale apenas para o CSV. O JSON mantém o valor original porque não é interpretado como uma planilha.

## Determinismo

Para o mesmo estado persistido do mesmo run:

- candidatos são ordenados pelo `rank`;
- JSON usa ordenação estável de chaves;
- estruturas aninhadas no CSV usam serialização JSON estável;
- o export não chama provider externo;
- o export não reexecuta o Site Analyzer;
- o export não recalcula OpportunityAssessment.

Isso permite comparar arquivos e reproduzir resultados com menos ambiguidade.

## Limitações atuais

O export não é ainda uma camada de relatório visual.

Ele também não:

- gera PDF;
- gera proposta comercial;
- calcula preço;
- cria abordagem;
- adiciona dados que não estavam persistidos no run;
- busca informações novas durante a exportação.

Essas responsabilidades pertencem a fases posteriores do produto.
