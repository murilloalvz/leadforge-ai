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
