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

## Validação real leve — 18/08/2026

Antes de baixar o dump nacional completo, fizemos uma validação leve para responder apenas se a hipótese de cobertura era plausível.

A Fundação Seade, órgão oficial do Estado de São Paulo, publica o conjunto **Seade Empresa**, derivado do Cadastro Nacional de Pessoas Jurídicas da Receita Federal. O recurso de empresas estava atualizado em 10/08/2026 e possui cerca de 6 MiB, o que confirmou que existe um caminho estadual muito menor para análises agregadas do que baixar imediatamente o dump nacional completo.

Além disso, consultas públicas baseadas em dados cadastrais da Receita mostraram múltiplos estabelecimentos **ativos**, localizados em **Jundiaí/SP**, com CNAE principal `8630504 — Atividade odontológica`. Entre os exemplos observados estão:

- Clínicas Odontológicas Viva Sorrindo Jundiaí Ltda;
- Rigo & Cardoso Odontologia Ltda;
- ERM - Serviços Odontológicos Ltda (Odonto Company);
- F Scurissa Melchert Odontologia;
- Clínica Dentária Jundiaí Ltda;
- S C Lopes Zanutel Odontologia;
- Elev Odontologia e Estética Ltda;
- Instituto Excellence Clínica Odontológica Ltda;
- M.V.L. Consultório Odontológico;
- CM Clínica Odontológica Ltda (CM Odontologia Digital).

### Conclusão desta validação

A hipótese mínima foi **confirmada**: dados cadastrais baseados em CNPJ/CNAE enxergam estabelecimentos odontológicos ativos em Jundiaí que não apareceram na validação do Geoapify.

Isso ainda **não é uma contagem completa** da base oficial e não mede todos os estabelecimentos existentes. O dump integral continua sendo a forma correta de obter uma medição exata e reproduzível com o script deste PR.

Portanto, a decisão nesta fase é:

- considerar CNPJ/CNAE uma fonte promissora para complementar o discovery;
- não transformar ainda o experimento em provider de produção;
- evitar baixar vários GB apenas para provar que a cobertura é maior que zero;
- numa próxima fase de implementação, decidir a estratégia operacional de ingestão/recorte dos dados oficiais.

## Como interpretar

Se a contagem completa for claramente maior que zero e a amostra parecer coerente, teremos evidência quantitativa reproduzível de que CNPJ/CNAE pode complementar o Geoapify para descoberta de empresas.

A validação leve já reduziu a principal incerteza: sabemos que existem empresas odontológicas ativas no recorte cadastral. A medição completa passa a servir para dimensionar cobertura, não mais para provar existência.

Se uma futura medição completa mostrar limitações inesperadas, não transformaremos a ideia em provider apenas porque já escrevemos código.

## Limites deste experimento

- a validação leve não representa uma contagem exaustiva;
- não faz enriquecimento de website;
- não analisa oportunidade comercial;
- não consulta responsáveis ou quadro societário;
- não envia contato ou outreach;
- não une os resultados ao banco do LeadForge;
- não prova qualidade para outros CNAEs ou cidades.

## Fontes de referência

O experimento foi desenhado a partir da documentação oficial da Receita Federal sobre dados abertos do CNPJ e do layout cadastral, da classificação oficial de CNAE da CONCLA/IBGE e, para a validação leve, do conjunto Seade Empresa e de consultas públicas que reproduzem dados cadastrais da Receita.
