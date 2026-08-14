# LeadForge AI

O LeadForge AI é um projeto para encontrar empresas que provavelmente têm espaço para automação, organizar essas oportunidades e transformar sinais públicos em uma abordagem comercial mais bem pensada.

A ideia é simples: em vez de sair mandando mensagem genérica para qualquer empresa, o sistema tenta entender o contexto do negócio, identificar possíveis gargalos e sugerir uma automação que realmente faça sentido para aquele caso.

> Status: projeto em fase inicial / MVP em desenvolvimento.

## Ideia do projeto

O fluxo que eu quero construir é mais ou menos este:

```text
Encontrar empresas
      ↓
Coletar informações públicas
      ↓
Identificar sinais de oportunidade
      ↓
Dar um score para os prospects
      ↓
Sugerir uma automação
      ↓
Gerar uma abordagem personalizada
      ↓
Montar uma demo da solução
      ↓
Revisão humana
      ↓
CRM / acompanhamento
```

O objetivo não é criar uma máquina de spam. No MVP, nenhuma mensagem deve ser enviada automaticamente sem revisão.

## Primeiro nicho

A primeira versão vai focar em clínicas e negócios de estética no Brasil.

Escolhi um nicho só para validar a ideia sem tentar resolver tudo de uma vez. Depois, a arquitetura deve permitir adaptar o projeto para outros tipos de negócio, como:

- imobiliárias;
- academias;
- clínicas odontológicas;
- escolas e cursos;
- oficinas;
- energia solar;
- prestadores de serviço;
- e-commerce.

## O que o sistema deve analisar

Para cada empresa, quero guardar os fatos encontrados e separar isso das interpretações.

Exemplo:

**Fato observado:** o site possui botão de WhatsApp.

**Hipótese:** o WhatsApp pode ser um canal importante de entrada de leads.

**Possível oportunidade:** automação de qualificação e follow-up.

Essa separação é importante para não inventar problemas ou métricas que não existem.

## Opportunity Score

Os prospects terão um score de 0 a 100.

Esse score não deve ser simplesmente um número inventado por um modelo de IA. A ideia é usar regras transparentes e ajustáveis.

Alguns sinais que podem entrar no cálculo:

- WhatsApp como canal visível de contato;
- presença digital ativa;
- vários serviços oferecidos;
- ausência de um sistema de agendamento visível;
- formulário de contato simples;
- sinais de demanda;
- automação já existente;
- quantidade insuficiente de informações;
- sinais de inatividade.

O resultado deve mostrar não só o score final, mas também o que aumentou ou diminuiu a pontuação.

## Roadmap

### v0.1 — Fundação

- estrutura do projeto;
- backend em FastAPI;
- banco de dados;
- modelos de prospects;
- dados fictícios para desenvolvimento;
- scoring inicial;
- API para listar e visualizar prospects;
- testes e lint.

### v0.2 — Coleta e evidências

- interfaces para diferentes fontes de dados;
- enriquecimento com dados públicos;
- histórico das evidências;
- confiança dos sinais;
- melhorias na deduplicação.

### v0.3 — Análise com IA

- análise estruturada dos prospects;
- separação entre fatos e hipóteses;
- sugestão de automações;
- respostas validadas com Pydantic;
- provider mock para rodar sem API externa.

### v0.4 — Oferta personalizada

- geração de abordagem baseada nas evidências;
- versões para WhatsApp e e-mail;
- fila de revisão humana;
- histórico de contato.

### v0.5 — Demo Generator

- templates de automação;
- demos personalizadas para cada prospect;
- dados de clientes totalmente fictícios;
- preview da solução antes do contato.

### v0.6 — CRM

- status dos prospects;
- notas;
- follow-ups;
- histórico de atividades;
- métricas do funil.

### v1.0 — Validação real

- uso com prospects reais em fontes permitidas;
- primeiras abordagens reais;
- acompanhamento de respostas;
- estudo de caso do projeto.

## Futuro

Depois que a parte de prospecção estiver funcionando, quero explorar duas extensões principais:

### Automation Engine

Templates reaproveitáveis das automações que forem vendidas aos clientes.

### AI Quality Monitor

Uma camada de acompanhamento das automações em produção, analisando coisas como:

- falhas;
- leads abandonados;
- respostas ruins do agente;
- conversas que deveriam ter ido para um humano;
- taxa de resolução;
- conversão;
- qualidade ao longo do tempo.

Essa parte pode acabar virando também um produto recorrente de manutenção.

## Stack planejada

### Backend

- Python 3.12+
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- SQLite no começo, com possibilidade de migrar para PostgreSQL

### Frontend

Provavelmente Next.js + TypeScript depois que o backend estiver mais estável.

### Qualidade

- pytest
- Ruff
- type checking
- logs estruturados

## Estrutura planejada

```text
leadforge-ai/
├── backend/
├── frontend/
├── docs/
├── sample_data/
├── scripts/
├── tests/
├── AGENTS.md
├── .env.example
├── .gitignore
└── README.md
```

## Segurança e privacidade

O projeto é voltado para prospecção B2B legítima.

Algumas regras do projeto:

- não coletar dados privados;
- não tentar burlar login ou CAPTCHA;
- não guardar senhas ou tokens no repositório;
- não enviar mensagens em massa automaticamente;
- não inventar métricas sobre empresas;
- não usar identidade falsa;
- demos devem usar dados fictícios;
- deve existir opção `do_not_contact` no CRM.

## Uso de IA no desenvolvimento

Esse projeto está sendo desenvolvido com bastante apoio de ferramentas de IA, principalmente Codex.

A IA pode escrever boa parte do código, mas a intenção é manter controle sobre arquitetura, regras de negócio, testes, segurança e decisões de produto. Também quero entender o que está sendo construído, e não só gerar código sem revisar.

## Documentação

As decisões de arquitetura ficam em [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

As instruções para agentes de código ficam em [`AGENTS.md`](AGENTS.md).

## Rodando localmente

A aplicação ainda não foi implementada. As instruções de instalação e execução serão adicionadas junto da v0.1.

## Objetivo inicial

O primeiro objetivo do LeadForge AI não é virar uma plataforma enorme.

É construir algo pequeno que consiga encontrar e priorizar boas oportunidades de automação e, depois, testar se essas oportunidades realmente ajudam a gerar conversas com empresas.
