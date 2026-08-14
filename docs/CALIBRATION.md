# Calibração do módulo web — v0.3.3

A calibração existe para responder uma pergunta simples: **os sinais automáticos do LeadForge batem com uma revisão humana do mesmo site?**

Ela não mede taxa de fechamento, qualidade comercial do lead ou retorno financeiro. O objetivo desta fase é validar a camada de evidências antes de construir etapas comerciais sobre ela.

## Método

A primeira amostra usa cinco homepages públicas de negócios locais, revisadas em 14/08/2026.

O arquivo versionado está em:

```text
sample_data/web_calibration_v0.3.3.json
```

Para cada página, a revisão humana rotulou apenas sinais que podiam ser verificados diretamente na homepage renderizada:

- `business_identity_clear`;
- `services_clearly_described`;
- `location_clearly_described`;
- `action_cta_present`;
- `lead_capture_path_present`.

Sinais que exigiriam outra fonte, inspeção mais ampla ou julgamento não verificável ficaram fora da amostra.

A amostra inicial contém:

- Clínica Estética Campinas;
- Praça Salão Bar;
- Laen Beauty & Spa;
- Hermas Beleza;
- CTF Clinic.

O repositório guarda URLs e rótulos derivados, não uma cópia do conteúdo dos sites.

## Métricas

A comparação diferencia:

- `matched`: previsão igual ao rótulo humano;
- `false_positive_gaps`: o LeadForge acusou ausência/problema que a revisão humana não confirmou;
- `false_negative_gaps`: o LeadForge considerou o critério presente quando a revisão humana indicou ausência;
- `unknown_predictions`: havia rótulo humano, mas o analisador não conseguiu concluir.

Um rótulo humano `null` não entra na métrica.

## Primeira execução

Antes de qualquer ajuste, o conjunto tinha 25 rótulos humanos.

Resultado:

```text
25 rótulos
22 matches
3 false-positive gaps
0 false-negative gaps
0 unknown
accuracy da amostra: 0.88
```

Os três erros estavam no mesmo sinal:

```text
location_clearly_described
2/5 matches
3 false-positive gaps
```

Os outros quatro sinais avaliados ficaram em 5/5.

## Diagnóstico

A regra de localização estava estreita demais. Ela reconhecia principalmente:

- endereço estruturado;
- CEP;
- palavras como "endereço" ou "localização".

Isso fazia o sistema marcar um gap mesmo quando a homepage informava claramente uma região em formatos como:

```text
Campinas/SP
Campinas - SP
Campinas, SP
```

Esse comportamento era especialmente ruim para negócios locais, porque informar cidade e UF já pode ser evidência suficiente de região atendida mesmo sem um endereço postal completo.

## Correção

O Site Analyzer passou a reconhecer pares brasileiros de cidade + UF no título e no texto visível analisado.

A mudança foi feita na regra de detecção, **não nos pesos do Opportunity Score**.

Essa ordem é intencional: quando a evidência está sendo interpretada incorretamente, reduzir o peso apenas esconderia o problema.

## Segunda execução

Depois da correção, os mesmos cinco sites foram analisados novamente.

Resultado:

```text
25 rótulos
25 matches
0 false-positive gaps
0 false-negative gaps
0 unknown
accuracy da amostra: 1.00
```

Todos os cinco sinais rotulados ficaram em 5/5 nesta amostra.

## O que esse resultado não significa

**25/25 nesta amostra não significa 100% de acurácia no mundo real.**

O conjunto é pequeno, usa apenas cinco homepages e possui predominância de exemplos positivos. Ele funciona como uma primeira calibração/smoke benchmark, não como benchmark estatisticamente representativo.

Antes de alterar pesos com confiança, a amostra precisa crescer com:

- páginas realmente sem CTA;
- páginas sem localização;
- páginas com localização ambígua;
- sites com conteúdo renderizado principalmente por JavaScript;
- sites quebrados ou parcialmente indisponíveis;
- exemplos de segmentos diferentes;
- casos onde a decisão humana também seja difícil.

Os pesos de `web-development-v2` permanecem inalterados após esta primeira calibração.

## Como executar

A partir de `backend/`:

```bash
python scripts/calibrate_web.py
```

Para outro dataset:

```bash
python scripts/calibrate_web.py --dataset ../sample_data/outro_dataset.json
```

Também existe um workflow `Live Calibration` no GitHub Actions. Ele é manual (`workflow_dispatch`) de propósito: sites externos mudam, podem bloquear requisições e não devem tornar a CI normal instável.

## Regra para futuras alterações

Não ajustar pesos apenas porque um resultado "parece errado".

A sequência preferida é:

```text
caso revisado por humano
→ reproduzir erro
→ identificar se a causa é coleta, regra ou peso
→ corrigir a causa mais específica
→ adicionar teste
→ executar novamente a calibração
→ só então considerar mudança de peso
```

A calibração deve continuar versionada e pequena o bastante para ser auditável manualmente.