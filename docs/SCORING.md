# Opportunity Scoring v1.1

O score de oportunidade do LeadForge é determinístico. O LLM não escolhe a nota.

A versão atual do algoritmo é `automation-v1.1`.

## O que mudou na revisão

A primeira versão tinha um problema simples: os sinais positivos somavam no máximo 85 pontos, então o intervalo prometido de 0 a 100 não era realmente utilizável. Na v1.1 os pesos positivos somam 100.

Também foram ajustados dois pontos:

- `confidence` agora pode chegar a 1.0 quando a cobertura de evidências é completa;
- valores dependentes de uma checagem só contam para a cobertura quando a checagem realmente aconteceu.

Exemplo: `booking_system_present=false` não melhora o score e nem a confiança se `booking_system_checked` não for `true`.

## Pesos atuais

| Sinal | Peso |
|---|---:|
| WhatsApp presente | +12 |
| Site próprio | +5 |
| Formulário de contato | +6 |
| Vários serviços | +8 |
| Sem agendamento visível após checagem | +16 |
| Sem automação de chat visível após checagem | +10 |
| Sinal forte de demanda | +14 |
| Presença social ativa | +8 |
| Nicho de ticket médio/alto | +12 |
| Múltiplos canais de contato | +9 |
| Empresa grande | -20 |
| Automação avançada já visível | -18 |
| Possível inatividade | -25 |

Os pesos ainda são hipóteses. Eles só devem ser tratados como bons depois de serem comparados com resultado real de prospecção: respostas, reuniões, propostas e vendas.

## Score x confidence

São coisas diferentes.

- `score`: quão interessante o prospect parece para a oferta de automação atual;
- `confidence`: quanta evidência relevante foi realmente verificada.

Um prospect pode ter score alto e confidence baixa. Nesse caso o sistema deve interpretar como "promissor, mas ainda pouco verificado", e não como certeza.

## Versionamento

Cada prospect armazena a versão do algoritmo usada no cálculo. Isso permite recalibrar pesos no futuro sem fingir que notas produzidas por versões diferentes são diretamente comparáveis.
