import socket

import httpx
import pytest

from app.services.site_analyzer.fetcher import (
    SafeHttpFetcher,
    SiteFetchError,
    UnsafeURL,
    validate_public_url,
)


def public_resolver(hostname: str, port: int) -> list[tuple]:
    return [
        (
            socket.AF_INET,
            socket.SOCK_STREAM,
            6,
            "",
            ("93.184.216.34", port),
        )
    ]


def test_rejects_loopback_and_private_literal_addresses() -> None:
    with pytest.raises(UnsafeURL):
        validate_public_url("http://127.0.0.1/admin")
    with pytest.raises(UnsafeURL):
        validate_public_url("http://10.0.0.4/internal")
    with pytest.raises(UnsafeURL):
        validate_public_url("http://[::1]/")


def test_rejects_domain_that_resolves_to_private_ip() -> None:
    def private_resolver(hostname: str, port: int) -> list[tuple]:
        return [
            (
                socket.AF_INET,
                socket.SOCK_STREAM,
                6,
                "",
                ("192.168.1.20", port),
            )
        ]

    with pytest.raises(UnsafeURL):
        validate_public_url("https://internal.example", private_resolver)


def test_redirect_to_private_target_is_blocked() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            302,
            headers={"location": "http://127.0.0.1/private"},
            request=request,
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    fetcher = SafeHttpFetcher(client=client, resolver=public_resolver)

    with pytest.raises(UnsafeURL):
        fetcher.fetch("https://example.com")


def test_response_size_limit_is_enforced() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"x" * 20, request=request)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    fetcher = SafeHttpFetcher(
        client=client,
        resolver=public_resolver,
        max_bytes=10,
    )

    with pytest.raises(SiteFetchError):
        fetcher.fetch("https://example.com")
