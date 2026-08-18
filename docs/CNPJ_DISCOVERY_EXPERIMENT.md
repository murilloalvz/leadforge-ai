# Experimento de discovery com dados abertos do CNPJ

## Objetivo

Responder uma pergunta pequena antes de integrar uma nova fonte ao LeadForge:

> A base aberta do CNPJ encontra empresas ativas de odontologia em Jundiaí/SP onde o Geoapify retornou zero resultados úteis?

Este experimento não cria ainda um provider de produção. Ele serve apenas para medir cobertura com uma fonte oficial diferente.

## Por que testar separado

O Geoapify mostrou boa utilidade para alguns nichos, mas cobertura insuficiente para odontologia em Jundiaí. Em vez de afrouxar filtros e aceitar hospitais ou outros falsos leads, o LeadForge deve poder complementar o discovery com outra fonte.

A base aberta do CNPJ é interessante porque permite procurar estabelecimentos pela atividade econômica oficial (CNAE).

Para odontologia, o experimento usa o CNAE `8630504`.

## Dados necessários

Baixe os arquivos oficiais dos dados abertos do CNPJ da Receita Federal e mantenha-os fora do repositório.

O script precisa de:

- tabela `Municipios`;
- um ou mais arquivos `Estabelecimentos`.

Arquivos extraídos e arquivos `.zip` são aceitos. O script lê em streaming; ele não carrega a base inteira na memória.

A base não deve ser commitada no GitHub: ela é grande e é dado de entrada, não código-fonte do projeto.

## O que o script filtra

1. resolve o código de `Jundiaí` pela tabela de municípios;
2. mantém somente estabelecimentos de `SP`;
3. mantém somente situação cadastral ativa (`02`);
4. procura o CNAE `8630504` como atividade principal ou secundária;
5. gera uma contagem e uma pequena amostra em JSON.

Todos os componentes do CNPJ são tratados como texto. Isso evita assumir que o identificador é puramente numérico.

## Como rodar

A partir da pasta `backend`:

```bash
python scripts/experiment_cnpj_dentists.py \
  --municipalities /caminho/para/Municipios.zip \
  --establishments /caminho/para/Estabelecimentos0.zip /caminho/para/Estabelecimentos1.zip \
  --city "Jundiaí" \
  --state SP \
  --cnae 8630504 \
  --output artifacts/cnpj-dentists-jundiai.json
```

Para uma medição completa, passe todos os arquivos de estabelecimentos do lote baixado.

## Como interpretar

Se a contagem for claramente maior que zero e a amostra parecer coerente, teremos evidência de que CNPJ/CNAE pode complementar o Geoapify para descoberta de empresas.

Se a cobertura continuar ruim, não transformaremos a ideia em provider apenas porque já escrevemos código. O objetivo do experimento é reduzir incerteza antes de aumentar a arquitetura.

## Limites deste experimento

- não faz enriquecimento de website;
- não analisa oportunidade comercial;
- não consulta responsáveis ou quadro societário;
- não envia contato ou outreach;
- não une os resultados ao banco do LeadForge;
- não prova qualidade para outros CNAEs ou cidades.

## Fontes de referência

O experimento foi desenhado a partir da documentação oficial da Receita Federal sobre dados abertos do CNPJ e do layout cadastral, e da classificação oficial de CNAE da CONCLA/IBGE.
