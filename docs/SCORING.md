# Opportunity Scoring v1

O score canônico do LeadForge é determinístico: o LLM não escolhe a nota.

## Regras importantes

- O score é limitado entre 0 e 100.
- Cada contribuição aparece separadamente e tem uma justificativa.
- `confidence` mede cobertura de evidência, não “certeza de fechar venda”.
- Ausência só conta quando houve uma checagem explícita. Ex.: `booking_system_present=false` sozinho não prova ausência; também precisamos de `booking_system_checked=true`.

## Sinais v1

| Sinal | Peso |
|---|---:|
| WhatsApp presente | +12 |
| Site próprio | +5 |
| Formulário de contato | +6 |
| Vários serviços | +7 |
| Sem agendamento visível após checagem | +14 |
| Sem automação de chat visível após checagem | +8 |
| Sinal forte de demanda | +12 |
| Presença social ativa | +7 |
| Nicho de ticket médio/alto | +9 |
| Múltiplos canais de contato | +5 |
| Empresa grande | -20 |
| Automação avançada já visível | -18 |
| Possível inatividade | -25 |

Esses pesos são uma hipótese de produto e deverão ser recalibrados usando resultados reais de prospecção.
