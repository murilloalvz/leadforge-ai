from __future__ import annotations

from dataclasses import dataclass

from app.services.opportunity.contracts import (
    FindingCertainty,
    OpportunityAssessmentResult,
    OpportunityContext,
    OpportunityFinding,
)

WEB_OPPORTUNITY_VERSION = "web-development-v1"


@dataclass(frozen=True)
class GapRule:
    signal: str
    weight: int
    title: str
    detail: str


RULES: tuple[GapRule, ...] = (
    GapRule(
        "public_http_ok",
        12,
        "Site com problema de disponibilidade",
        "A página principal não respondeu com sucesso durante a análise.",
    ),
    GapRule(
        "indexable",
        14,
        "Site com bloqueio de indexação",
        "A página analisada não está elegível para indexação.",
    ),
    GapRule(
        "important_content_textual",
        14,
        "Conteúdo principal pouco acessível em texto",
        "Informações importantes parecem insuficientes no HTML textual analisado.",
    ),
    GapRule(
        "business_identity_clear",
        12,
        "Identidade do negócio pouco clara",
        "O site não deixa nome e identidade do negócio claros pelos sinais atuais.",
    ),
    GapRule(
        "services_clearly_described",
        16,
        "Serviços pouco descritos",
        "Os serviços não aparecem descritos de forma explícita pelos sinais atuais.",
    ),
    GapRule(
        "location_clearly_described",
        10,
        "Localização pouco clara",
        "Endereço ou região atendida não ficaram claros na página analisada.",
    ),
    GapRule(
        "descriptive_titles",
        8,
        "Título de página pouco descritivo",
        "O título atual oferece pouco contexto sobre a página ou o negócio.",
    ),
    GapRule(
        "structured_data_present",
        6,
        "Dados estruturados ausentes",
        "Nenhum JSON-LD útil foi identificado na página analisada.",
    ),
    GapRule(
        "local_business_schema",
        8,
        "Marcação de negócio local ausente",
        "Não foi identificada marcação estruturada apropriada de negócio local.",
    ),
)

TOTAL_WEIGHT = sum(rule.weight for rule in RULES)


class WebDevelopmentOpportunityModule:
    service_category = "web_development"

    def assess(self, context: OpportunityContext) -> OpportunityAssessmentResult:
        observed = [rule for rule in RULES if context.signals.get(rule.signal) is not None]
        observed_weight = sum(rule.weight for rule in observed)
        gap_weight = sum(
            rule.weight
            for rule in observed
            if context.signals.get(rule.signal) is False
        )

        score = 0 if observed_weight == 0 else round(100 * gap_weight / observed_weight)
        confidence = 0.0 if TOTAL_WEIGHT == 0 else round(observed_weight / TOTAL_WEIGHT, 2)

        findings: list[OpportunityFinding] = []
        for rule in RULES:
            value = context.signals.get(rule.signal)
            if value is False:
                findings.append(
                    OpportunityFinding(
                        key=rule.signal,
                        title=rule.title,
                        certainty=FindingCertainty.CONFIRMED,
                        detail=rule.detail,
                        contribution=rule.weight,
                        evidence_keys=(rule.signal,),
                    )
                )
            elif value is None:
                findings.append(
                    OpportunityFinding(
                        key=rule.signal,
                        title=rule.title,
                        certainty=FindingCertainty.UNKNOWN,
                        detail="O analisador atual ainda não possui evidência suficiente para este ponto.",
                        contribution=0,
                        evidence_keys=(rule.signal,),
                    )
                )

        confirmed_count = sum(
            finding.certainty is FindingCertainty.CONFIRMED for finding in findings
        )
        if confidence == 0:
            summary = "Ainda não há evidência suficiente para avaliar a oportunidade web."
            recommended_service = None
        elif confirmed_count == 0:
            summary = "Nenhum gap web relevante foi confirmado pelos critérios atuais."
            recommended_service = "Auditoria e otimizações pontuais do site"
        else:
            summary = (
                f"Foram confirmados {confirmed_count} ponto(s) de melhoria web "
                "com base apenas em sinais observáveis do site."
            )
            recommended_service = (
                "Melhoria de site institucional"
                if score >= 35
                else "Otimizações pontuais de site"
            )

        return OpportunityAssessmentResult(
            service_category=self.service_category,
            score=score,
            confidence=confidence,
            version=WEB_OPPORTUNITY_VERSION,
            summary=summary,
            recommended_service=recommended_service,
            findings=tuple(findings),
        )
