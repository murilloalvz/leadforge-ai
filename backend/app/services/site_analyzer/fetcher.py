from __future__ import annotations

import ipaddress
import socket
from collections.abc import Callable
from dataclasses import dataclass
from urllib.parse import urljoin, urlsplit

import httpx

Resolver = Callable[[str, int], list[tuple]]


class UnsafeURL(ValueError):
    """Raised when a URL is not safe to fetch from the server."""


class SiteFetchError(RuntimeError):
    """Raised when a public URL cannot be fetched safely."""


@dataclass(frozen=True)
class FetchResult:
    requested_url: str
    final_url: str
    status_code: int
    headers: dict[str, str]
    body: bytes
    redirects: tuple[str, ...]


def _default_resolver(hostname: str, port: int) -> list[tuple]:
    return socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)


def _resolved_ips(hostname: str, port: int, resolver: Resolver) -> set[ipaddress.IPv4Address | ipaddress.IPv6Address]:
    try:
        literal = ipaddress.ip_address(hostname)
    except ValueError:
        try:
            records = resolver(hostname, port)
        except OSError as exc:
            raise UnsafeURL(f"Não foi possível resolver o host: {hostname}") from exc
        addresses = {record[4][0] for record in records}
        if not addresses:
            raise UnsafeURL(f"O host não possui endereço resolvível: {hostname}")
        return {ipaddress.ip_address(address) for address in addresses}
    return {literal}


def validate_public_url(url: str, resolver: Resolver = _default_resolver) -> str:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"}:
        raise UnsafeURL("Apenas URLs http:// e https:// são permitidas")
    if parsed.username or parsed.password:
        raise UnsafeURL("URLs com credenciais embutidas não são permitidas")
    if not parsed.hostname:
        raise UnsafeURL("URL sem hostname")

    hostname = parsed.hostname.rstrip(".").lower()
    if hostname == "localhost" or hostname.endswith(".localhost"):
        raise UnsafeURL("Hosts locais não são permitidos")

    try:
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
    except ValueError as exc:
        raise UnsafeURL("Porta inválida") from exc

    for address in _resolved_ips(hostname, port, resolver):
        if not address.is_global:
            raise UnsafeURL(f"Destino não público bloqueado: {address}")

    return url


class SafeHttpFetcher:
    def __init__(
        self,
        *,
        timeout_seconds: float = 6.0,
        max_bytes: int = 1_500_000,
        max_redirects: int = 5,
        resolver: Resolver = _default_resolver,
        client: httpx.Client | None = None,
    ) -> None:
        self.timeout_seconds = timeout_seconds
        self.max_bytes = max_bytes
        self.max_redirects = max_redirects
        self.resolver = resolver
        self.client = client or httpx.Client(
            timeout=timeout_seconds,
            follow_redirects=False,
            trust_env=False,
            headers={
                "User-Agent": (
                    "LeadForgeBot/0.2 (+https://github.com/murilloalvz/leadforge-ai)"
                )
            },
        )

    def fetch(self, url: str) -> FetchResult:
        requested_url = validate_public_url(url, self.resolver)
        current_url = requested_url
        redirects: list[str] = []

        for redirect_count in range(self.max_redirects + 1):
            validate_public_url(current_url, self.resolver)
            try:
                with self.client.stream("GET", current_url) as response:
                    status_code = response.status_code
                    headers = {key.lower(): value for key, value in response.headers.items()}

                    if status_code in {301, 302, 303, 307, 308}:
                        location = response.headers.get("location")
                        if not location:
                            raise SiteFetchError("Redirect sem cabeçalho Location")
                        if redirect_count >= self.max_redirects:
                            raise SiteFetchError("Limite de redirects excedido")
                        next_url = urljoin(current_url, location)
                        validate_public_url(next_url, self.resolver)
                        redirects.append(next_url)
                        current_url = next_url
                        continue

                    body = self._read_limited(response)
                    return FetchResult(
                        requested_url=requested_url,
                        final_url=str(response.url),
                        status_code=status_code,
                        headers=headers,
                        body=body,
                        redirects=tuple(redirects),
                    )
            except UnsafeURL:
                raise
            except httpx.HTTPError as exc:
                raise SiteFetchError(f"Falha HTTP ao acessar {current_url}") from exc

        raise SiteFetchError("Limite de redirects excedido")

    def _read_limited(self, response: httpx.Response) -> bytes:
        chunks: list[bytes] = []
        total = 0
        for chunk in response.iter_bytes():
            total += len(chunk)
            if total > self.max_bytes:
                raise SiteFetchError(
                    f"Resposta excedeu o limite de {self.max_bytes} bytes"
                )
            chunks.append(chunk)
        return b"".join(chunks)
