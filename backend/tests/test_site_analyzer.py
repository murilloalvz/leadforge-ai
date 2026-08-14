from app.services.site_analyzer.analyzer import SiteAnalyzer
from app.services.site_analyzer.fetcher import FetchResult


class FakeFetcher:
    def __init__(self, responses: dict[str, FetchResult]) -> None:
        self.responses = responses

    def fetch(self, url: str) -> FetchResult:
        return self.responses[url]


def html_response(url: str, html: str) -> FetchResult:
    return FetchResult(
        requested_url=url,
        final_url=url,
        status_code=200,
        headers={"content-type": "text/html; charset=utf-8"},
        body=html.encode(),
        redirects=(),
    )


def robots_response(url: str, text: str) -> FetchResult:
    return FetchResult(
        requested_url=url,
        final_url=url,
        status_code=200,
        headers={"content-type": "text/plain"},
        body=text.encode(),
        redirects=(),
    )


def rich_html(extra_head: str = "") -> str:
    body = " ".join(["tratamento estetico personalizado em Campinas"] * 35)
    return f"""
    <html>
      <head>
        <title>Clínica Aurora | Estética em Campinas</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta
          name="description"
          content="Clínica de estética em Campinas com tratamentos personalizados."
        >
        <link rel="canonical" href="https://clinic.example/">
        {extra_head}
        <script type="application/ld+json">
        {{
          "@context": "https://schema.org",
          "@type": "LocalBusiness",
          "name": "Clínica Aurora",
          "address": {{
            "@type": "PostalAddress",
            "streetAddress": "Rua das Flores, 10",
            "addressLocality": "Campinas",
            "addressRegion": "SP",
            "postalCode": "13000-000"
          }}
        }}
        </script>
      </head>
      <body>
        <h1>Clínica Aurora</h1>
        <h2>Serviços e tratamentos</h2>
        <p>Endereço: Rua das Flores, 10 - Campinas - CEP 13000-000.</p>
        <a href="https://wa.me/5519999999999">Agende pelo WhatsApp</a>
        <form action="/contato" method="post">
          <input name="nome">
        </form>
        <img src="clinica.jpg" alt="Recepção da Clínica Aurora">
        <p>{body}</p>
      </body>
    </html>
    """


def test_ready_public_site_scores_100() -> None:
    page_url = "https://clinic.example/"
    robots_url = "https://clinic.example/robots.txt"
    fetcher = FakeFetcher(
        {
            page_url: html_response(page_url, rich_html()),
            robots_url: robots_response(
                robots_url,
                "User-agent: Googlebot\nAllow: /\n"
                "User-agent: OAI-SearchBot\nAllow: /\n",
            ),
        }
    )

    result = SiteAnalyzer(fetcher=fetcher).analyze(page_url)

    assert result.score == 100
    assert result.confidence == 1.0
    assert result.signals["oai_searchbot_allowed"] is True
    assert result.signals["local_business_schema"] is True
    assert result.signals["https_enabled"] is True
    assert result.signals["mobile_viewport_present"] is True
    assert result.signals["form_present"] is True
    assert result.signals["whatsapp_link_present"] is True
    assert result.signals["contact_channel_present"] is True
    assert result.signals["action_cta_present"] is True
    assert result.signals["lead_capture_path_present"] is True
    assert result.signals["meta_description_present"] is True
    assert result.signals["canonical_present"] is True
    assert result.signals["heading_structure_basic"] is True
    assert result.signals["images_alt_attributes_complete"] is True
    assert result.evidence["form_count"] == 1
    assert result.evidence["image_count"] == 1
    assert result.evidence["word_count"] >= 120


def test_noindex_and_oai_block_are_reported() -> None:
    page_url = "https://clinic.example/"
    robots_url = "https://clinic.example/robots.txt"
    fetcher = FakeFetcher(
        {
            page_url: html_response(
                page_url,
                rich_html('<meta name="robots" content="noindex,follow">'),
            ),
            robots_url: robots_response(
                robots_url,
                "User-agent: OAI-SearchBot\nDisallow: /\n"
                "User-agent: Googlebot\nAllow: /\n",
            ),
        }
    )

    result = SiteAnalyzer(fetcher=fetcher).analyze(page_url)

    assert result.signals["indexable"] is False
    assert result.signals["oai_searchbot_allowed"] is False
    assert "indexable" in result.blockers
    assert result.score <= 25
    assert any("OAI-SearchBot" in item for item in result.recommendations)


def test_missing_robots_file_is_treated_as_allowed() -> None:
    page_url = "https://clinic.example/"
    robots_url = "https://clinic.example/robots.txt"
    missing_robots = FetchResult(
        requested_url=robots_url,
        final_url=robots_url,
        status_code=404,
        headers={"content-type": "text/plain"},
        body=b"not found",
        redirects=(),
    )
    fetcher = FakeFetcher(
        {
            page_url: html_response(page_url, rich_html()),
            robots_url: missing_robots,
        }
    )

    result = SiteAnalyzer(fetcher=fetcher).analyze(page_url)

    assert result.signals["googlebot_allowed"] is True
    assert result.signals["oai_searchbot_allowed"] is True


def test_sparse_page_exposes_web_gaps_without_inventing_performance() -> None:
    page_url = "https://clinic.example/"
    robots_url = "https://clinic.example/robots.txt"
    sparse_html = """
    <html>
      <head><title>Home</title></head>
      <body>
        <h2>Bem-vindo</h2>
        <img src="hero.jpg">
        <p>Clínica local.</p>
      </body>
    </html>
    """
    fetcher = FakeFetcher(
        {
            page_url: html_response(page_url, sparse_html),
            robots_url: robots_response(robots_url, "User-agent: *\nAllow: /\n"),
        }
    )

    result = SiteAnalyzer(fetcher=fetcher).analyze(page_url)

    assert result.signals["mobile_viewport_present"] is False
    assert result.signals["form_present"] is False
    assert result.signals["contact_channel_present"] is False
    assert result.signals["lead_capture_path_present"] is False
    assert result.signals["action_cta_present"] is False
    assert result.signals["meta_description_present"] is False
    assert result.signals["canonical_present"] is False
    assert result.signals["heading_structure_basic"] is False
    assert result.signals["images_alt_attributes_complete"] is False
    assert "core_web_vitals" not in result.signals
    assert "performance_score" not in result.signals


def test_brazilian_city_state_pair_counts_as_location_signal() -> None:
    page_url = "https://salon.example/"
    robots_url = "https://salon.example/robots.txt"
    html = """
    <html>
      <head><title>Laen Beauty & Spa | Campinas/SP</title></head>
      <body>
        <h1>Laen Beauty & Spa</h1>
        <p>Serviços de beleza e bem-estar.</p>
      </body>
    </html>
    """
    fetcher = FakeFetcher(
        {
            page_url: html_response(page_url, html),
            robots_url: robots_response(robots_url, "User-agent: *\nAllow: /\n"),
        }
    )

    result = SiteAnalyzer(fetcher=fetcher).analyze(page_url)

    assert result.signals["location_clearly_described"] is True
