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

BRAZIL_STATE_CODES = (
    "ac",
    "al",
    "ap",
    "am",
    "ba",
    "ce",
    "df",
    "es",
    "go",
    "ma",
    "mt",
    "ms",
    "mg",
    "pa",
    "pb",
    "pr",
    "pe",
    "pi",
    "rj",
    "rn",
    "rs",
    "ro",
    "rr",
    "sc",
    "sp",
    "se",
    "to",
)
CITY_STATE_PATTERN = re.compile(
    rf"\b[a-z][a-z .'-]{{2,60}}\s*(?:/|-|,)\s*(?:{'|'.join(BRAZIL_STATE_CODES)})\b"
)

CTA_TERMS = (
    "agende",
    "agendar",
    "marque",
    "marcar",
    "fale conosco",
    "entre em contato",
    "contato",
    "orcamento",
    "orçamento",
    "solicitar",
    "whatsapp",
    "ligue",
    "saiba mais",
    "comece agora",
    "book",
    "contact",
    "get a quote",
    "learn more",
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
        location_haystack = f"{normalized_title} {normalized_text[:12000]}"
        location_clearly_described = (
            bool(page.structured_addresses)
            or bool(re.search(r"\b\d{5}-?\d{3}\b", page.visible_text))
            or _contains_any(location_haystack, LOCATION_TERMS)
            or _contains_brazilian_city_state(location_haystack)
        )
        descriptive_titles = (
            len(page.title or "") >= 10
            and normalized_title not in {_normalize(item) for item in GENERIC_TITLES}
        )
        structured_data_present = page.structured_data_documents > 0
        local_business_schema = any(
            schema_type in LOCAL_BUSINESS_TYPES for schema_type in page.structured_types
        )
        structured_data_matches_visible_content = self._structured_data_match(page)

        hrefs = tuple(href.strip().lower() for href in page.link_hrefs)
        whatsapp_link_present = any(
            href.startswith("whatsapp:")
            or "wa.me/" in href
            or "api.whatsapp.com/" in href
            for href in hrefs
        )
        telephone_link_present = any(href.startswith("tel:") for href in hrefs)
        email_link_present = any(href.startswith("mailto:") for href in hrefs)
        contact_page_link_present = any(
            "contato" in href or "contact" in href for href in hrefs
        )
        contact_channel_present = any(
            (
                whatsapp_link_present,
                telephone_link_present,
                email_link_present,
                contact_page_link_present,
            )
        )
        interactive_text = " ".join(page.interactive_texts)
        action_cta_present = contact_channel_present or _contains_any(
            interactive_text,
            CTA_TERMS,
        )
        form_present = page.form_count > 0
        lead_capture_path_present = form_present or contact_channel_present

        viewport = (page.viewport or "").lower().replace(" ", "")
        mobile_viewport_present = "width=device-width" in viewport
        images_alt_attributes_complete = (
            None
            if page.image_count == 0
            else page.images_with_alt_attribute == page.image_count
        )

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
            "https_enabled": urlsplit(response.final_url).scheme.lower() == "https",
            "mobile_viewport_present": mobile_viewport_present,
            "form_present": form_present,
            "whatsapp_link_present": whatsapp_link_present,
            "telephone_link_present": telephone_link_present,
            "contact_channel_present": contact_channel_present,
            "action_cta_present": action_cta_present,
            "lead_capture_path_present": lead_capture_path_present,
            "meta_description_present": bool(page.meta_description),
            "canonical_present": bool(page.canonical_href),
            "heading_structure_basic": _heading_structure_basic(page.heading_levels),
            "images_alt_attributes_complete": images_alt_attributes_complete,
            "redirect_chain_reasonable": len(response.redirects) <= 2,
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
            "headings": list(page.headings[:20]),
            "heading_levels": list(page.heading_levels[:20]),
            "word_count": len(page.visible_text.split()),
            "meta_robots": page.meta_robots,
            "meta_description": page.meta_description,
            "viewport": page.viewport,
            "canonical_href": page.canonical_href,
            "form_count": page.form_count,
            "link_count": len(page.link_hrefs),
            "interactive_texts": list(page.interactive_texts[:20]),
            "image_count": page.image_count,
            "images_with_alt_attribute": page.images_with_alt_attribute,
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
            "https_enabled": "Disponibilizar a versão principal do site em HTTPS.",
            "mobile_viewport_present": "Adicionar viewport adequado para dispositivos móveis.",
            "form_present": "Avaliar um formulário quando fizer sentido para captar contatos.",
            "whatsapp_link_present": "Avaliar um link direto para WhatsApp quando apropriado.",
            "telephone_link_present": "Avaliar um link de telefone clicável quando apropriado.",
            "contact_channel_present": "Expor um caminho claro de contato na página.",
            "action_cta_present": "Adicionar uma chamada para ação clara e acionável.",
            "lead_capture_path_present": "Criar um caminho claro para contato ou captação.",
            "meta_description_present": "Adicionar uma meta description descritiva.",
            "canonical_present": "Avaliar uma URL canônica explícita para a página.",
            "heading_structure_basic": "Revisar a hierarquia básica de headings da página.",
            "images_alt_attributes_complete": (
                "Adicionar atributo alt às imagens que ainda não o possuem."
            ),
            "redirect_chain_reasonable": "Reduzir cadeias longas de redirecionamento.",
        }
        return tuple(
            messages[key]
            for key, value in signals.items()
            if value is False and key in messages
        )


def _normalize(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    without_marks = "".join(char for char in normalized if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", without_marks).strip().lower()


def _contains_any(haystack: str, terms: tuple[str, ...]) -> bool:
    normalized_haystack = _normalize(haystack)
    normalized_terms = (_normalize(term) for term in terms)
    return any(term in normalized_haystack for term in normalized_terms)


def _contains_brazilian_city_state(value: str) -> bool:
    return bool(CITY_STATE_PATTERN.search(_normalize(value)))


def _heading_structure_basic(levels: tuple[int, ...]) -> bool:
    if not levels or levels.count(1) != 1 or levels[0] != 1:
        return False
    return all(
        current <= previous + 1
        for previous, current in zip(levels, levels[1:], strict=False)
    )
