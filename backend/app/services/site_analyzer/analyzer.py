from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlsplit, urlunsplit
from urllib.robotparser import RobotFileParser

from app.services.site_analyzer.fetcher import FetchResult, SafeHttpFetcher, SiteFetchError
from app.services.site_analyzer.html_parser import ParsedPage, parse_html
from app.services.site_readiness.engine import AIDiscoverabilityScorer

LOCAL_BUSINESS_TYPES = {
    "LocalBusiness",
    "MedicalBusiness",
    "HealthAndBeautyBusiness",
    "Dentist",
    "Store",
    "Restaurant",
    "BeautySalon",
    "DaySpa",
    "HairSalon",
    "NailSalon",
}

SERVICE_TERMS = (
    "servicos",
    "serviços",
    "tratamentos",
    "procedimentos",
    "especialidades",
    "o que fazemos",
    "services",
    "treatments",
    "solutions",
)

LOCATION_TERMS = (
    "endereco",
    "endereço",
    "localizacao",
    "localização",
    "onde estamos",
    "address",
    "location",
)

GENERIC_TITLES = {
    "home",
    "inicio",
    "início",
    "pagina inicial",
    "página inicial",
    "welcome",
}


@dataclass(frozen=True)
class SiteAnalysisResult:
    requested_url: str
    final_url: str
    http_status: int
    score: int
    confidence: float
    score_version: str
    signals: dict[str, bool | None]
    evidence: dict[str, Any]
    blockers: tuple[str, ...]
    recommendations: tuple[str, ...]


class SiteAnalyzer:
    def __init__(self, fetcher: SafeHttpFetcher | None = None) -> None:
        self.fetcher = fetcher or SafeHttpFetcher()
        self.scorer = AIDiscoverabilityScorer()

    def analyze(self, url: str) -> SiteAnalysisResult:
        page_response = self.fetcher.fetch(url)
        self._validate_html_response(page_response)
        html = self._decode_body(page_response)
        page = parse_html(html)

        robots_url = self._robots_url(page_response.final_url)
        robots_response = self._fetch_robots(robots_url)
        googlebot_allowed = self._robots_permission(
            robots_response,
            "Googlebot",
            page_response.final_url,
        )
        oai_searchbot_allowed = self._robots_permission(
            robots_response,
            "OAI-SearchBot",
            page_response.final_url,
        )

        signals = self._signals(
            page_response,
            page,
            googlebot_allowed,
            oai_searchbot_allowed,
        )
        readiness = self.scorer.score(signals)
        evidence = self._evidence(page_response, page, robots_url, robots_response)
        recommendations = self._recommendations(signals)

        return SiteAnalysisResult(
            requested_url=page_response.requested_url,
            final_url=page_response.final_url,
            http_status=page_response.status_code,
            score=readiness.score,
            confidence=readiness.confidence,
            score_version=readiness.version,
            signals=signals,
            evidence=evidence,
            blockers=readiness.blockers,
            recommendations=recommendations,
        )

    @staticmethod
    def _validate_html_response(response: FetchResult) -> None:
        content_type = response.headers.get("content-type", "").lower()
        if content_type and "html" not in content_type:
            raise SiteFetchError(
                f"A URL não retornou HTML analisável: {content_type.split(';')[0]}"
            )

    @staticmethod
    def _decode_body(response: FetchResult) -> str:
        content_type = response.headers.get("content-type", "")
        match = re.search(r"charset=([\w.-]+)", content_type, flags=re.IGNORECASE)
        encoding = match.group(1) if match else "utf-8"
        try:
            return response.body.decode(encoding, errors="replace")
        except LookupError:
            return response.body.decode("utf-8", errors="replace")

    @staticmethod
    def _robots_url(url: str) -> str:
        parsed = urlsplit(url)
        return urlunsplit((parsed.scheme, parsed.netloc, "/robots.txt", "", ""))

    def _fetch_robots(self, robots_url: str) -> FetchResult | None:
        try:
            return self.fetcher.fetch(robots_url)
        except SiteFetchError:
            return None

    @staticmethod
    def _robots_permission(
        robots_response: FetchResult | None,
        user_agent: str,
        target_url: str,
    ) -> bool | None:
        if robots_response is None:
            return None
        status = robots_response.status_code
        if status in {401, 403}:
            return False
        if 400 <= status < 500:
            return True
        if status >= 500:
            return None
        if status < 200 or status >= 300:
            return None

        text = robots_response.body.decode("utf-8", errors="replace")
        parser = RobotFileParser()
        parser.parse(text.splitlines())
        return parser.can_fetch(user_agent, target_url)

    def _signals(
        self,
        response: FetchResult,
        page: ParsedPage,
        googlebot_allowed: bool | None,
        oai_searchbot_allowed: bool | None,
    ) -> dict[str, bool | None]:
        public_http_ok = 200 <= response.status_code < 300
        robot_directives = " ".join(
            part
            for part in (
                page.meta_robots or "",
                response.headers.get("x-robots-tag", ""),
            )
            if part
        ).lower()
        indexable = public_http_ok and "noindex" not in robot_directives

        normalized_title = _normalize(page.title or "")
        normalized_headings = " ".join(_normalize(item) for item in page.headings)
        normalized_text = _normalize(page.visible_text)
        word_count = len(page.visible_text.split())

        business_identity_clear = bool(page.title) and (
            bool(page.headings) or bool(page.structured_names)
        )
        services_clearly_described = _contains_any(
            f"{normalized_headings} {normalized_text[:8000]}",
            SERVICE_TERMS,
        )
        location_clearly_described = bool(page.structured_addresses) or bool(
            re.search(r"\b\d{5}-?\d{3}\b", page.visible_text)
        ) or _contains_any(normalized_text[:8000], LOCATION_TERMS)
        descriptive_titles = (
            10 <= len(page.title or "") <= 75
            and normalized_title not in {_normalize(item) for item in GENERIC_TITLES}
        )
        structured_data_present = page.structured_data_documents > 0
        local_business_schema = any(
            schema_type in LOCAL_BUSINESS_TYPES for schema_type in page.structured_types
        )
        structured_data_matches_visible_content = self._structured_data_match(page)

        return {
            "public_http_ok": public_http_ok,
            "indexable": indexable,
            "googlebot_allowed": googlebot_allowed,
            "oai_searchbot_allowed": oai_searchbot_allowed,
            "important_content_textual": word_count >= 120,
            "business_identity_clear": business_identity_clear,
            "services_clearly_described": services_clearly_described,
            "location_clearly_described": location_clearly_described,
            "descriptive_titles": descriptive_titles,
            "structured_data_present": structured_data_present,
            "local_business_schema": local_business_schema,
            "structured_data_matches_visible_content": structured_data_matches_visible_content,
        }

    @staticmethod
    def _structured_data_match(page: ParsedPage) -> bool | None:
        if not page.structured_names:
            return None
        haystack = _normalize(f"{page.title or ''} {page.visible_text[:12000]}")
        return any(_normalize(name) in haystack for name in page.structured_names)

    @staticmethod
    def _evidence(
        response: FetchResult,
        page: ParsedPage,
        robots_url: str,
        robots_response: FetchResult | None,
    ) -> dict[str, Any]:
        return {
            "page_title": page.title,
            "headings": list(page.headings[:12]),
            "word_count": len(page.visible_text.split()),
            "meta_robots": page.meta_robots,
            "x_robots_tag": response.headers.get("x-robots-tag"),
            "structured_data_documents": page.structured_data_documents,
            "structured_types": list(page.structured_types),
            "structured_names": list(page.structured_names),
            "structured_addresses": list(page.structured_addresses),
            "content_type": response.headers.get("content-type"),
            "redirects": list(response.redirects),
            "robots_url": robots_url,
            "robots_status": robots_response.status_code if robots_response else None,
        }

    @staticmethod
    def _recommendations(signals: dict[str, bool | None]) -> tuple[str, ...]:
        messages = {
            "public_http_ok": "Corrigir disponibilidade HTTP da página principal.",
            "indexable": "Remover bloqueios de indexação quando forem não intencionais.",
            "googlebot_allowed": "Revisar robots.txt para acesso do Googlebot.",
            "oai_searchbot_allowed": "Revisar robots.txt para acesso do OAI-SearchBot.",
            "important_content_textual": (
                "Colocar informações importantes em texto HTML acessível."
            ),
            "business_identity_clear": "Deixar nome e proposta do negócio claros no site.",
            "services_clearly_described": "Criar uma descrição explícita dos serviços.",
            "location_clearly_described": "Informar endereço ou região atendida claramente.",
            "descriptive_titles": "Usar títulos de página mais descritivos.",
            "structured_data_present": "Adicionar dados estruturados JSON-LD quando úteis.",
            "local_business_schema": "Avaliar marcação Schema.org adequada ao negócio local.",
            "structured_data_matches_visible_content": (
                "Alinhar dados estruturados com o conteúdo visível da página."
            ),
        }
        return tuple(messages[key] for key, value in signals.items() if value is False)


def _normalize(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    without_marks = "".join(char for char in normalized if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", without_marks).strip().lower()


def _contains_any(haystack: str, terms: tuple[str, ...]) -> bool:
    normalized_terms = (_normalize(term) for term in terms)
    return any(term in haystack for term in normalized_terms)
