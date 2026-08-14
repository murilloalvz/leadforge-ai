from __future__ import annotations

import json
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Any


@dataclass(frozen=True)
class ParsedPage:
    title: str | None
    headings: tuple[str, ...]
    visible_text: str
    meta_robots: str | None
    structured_types: tuple[str, ...]
    structured_names: tuple[str, ...]
    structured_addresses: tuple[str, ...]
    structured_data_documents: int


class _PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.headings: list[str] = []
        self.text_parts: list[str] = []
        self.meta_robots: str | None = None
        self.jsonld_documents: list[str] = []
        self._jsonld_parts: list[str] = []
        self._in_title = False
        self._heading_tag: str | None = None
        self._heading_parts: list[str] = []
        self._skip_depth = 0
        self._in_jsonld = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attr_map = {key.lower(): value for key, value in attrs}

        if tag in {"style", "noscript", "svg"}:
            self._skip_depth += 1
            return

        if tag == "script":
            script_type = (attr_map.get("type") or "").lower()
            if script_type == "application/ld+json":
                self._in_jsonld = True
                self._jsonld_parts = []
            else:
                self._skip_depth += 1
            return

        if tag == "title":
            self._in_title = True
        if tag in {"h1", "h2", "h3"}:
            self._heading_tag = tag
            self._heading_parts = []

        if tag == "meta":
            name = (attr_map.get("name") or "").lower()
            if name == "robots":
                self.meta_robots = attr_map.get("content")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"style", "noscript", "svg"}:
            self._skip_depth = max(0, self._skip_depth - 1)
            return
        if tag == "script":
            if self._in_jsonld:
                document = "".join(self._jsonld_parts).strip()
                if document:
                    self.jsonld_documents.append(document)
                self._jsonld_parts = []
                self._in_jsonld = False
            else:
                self._skip_depth = max(0, self._skip_depth - 1)
            return
        if tag == "title":
            self._in_title = False
        if self._heading_tag == tag:
            heading = _clean_text(" ".join(self._heading_parts))
            if heading:
                self.headings.append(heading)
            self._heading_tag = None
            self._heading_parts = []

    def handle_data(self, data: str) -> None:
        if self._in_jsonld:
            self._jsonld_parts.append(data)
            return
        if self._skip_depth:
            return
        if self._in_title:
            self.title_parts.append(data)
        if self._heading_tag:
            self._heading_parts.append(data)
        cleaned = _clean_text(data)
        if cleaned:
            self.text_parts.append(cleaned)


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _iter_jsonld_objects(value: Any):
    if isinstance(value, dict):
        yield value
        graph = value.get("@graph")
        if graph is not None:
            yield from _iter_jsonld_objects(graph)
        for nested in value.values():
            if isinstance(nested, (dict, list)):
                yield from _iter_jsonld_objects(nested)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_jsonld_objects(item)


def _extract_address(value: Any) -> str | None:
    if isinstance(value, str):
        return _clean_text(value)
    if not isinstance(value, dict):
        return None
    parts = [
        value.get("streetAddress"),
        value.get("addressLocality"),
        value.get("addressRegion"),
        value.get("postalCode"),
        value.get("addressCountry"),
    ]
    text = ", ".join(str(part) for part in parts if part)
    return _clean_text(text) or None


def parse_html(html: str) -> ParsedPage:
    parser = _PageParser()
    parser.feed(html)

    structured_types: set[str] = set()
    structured_names: set[str] = set()
    structured_addresses: set[str] = set()
    documents = 0

    for candidate in parser.jsonld_documents:
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        documents += 1
        for obj in _iter_jsonld_objects(payload):
            raw_type = obj.get("@type")
            if isinstance(raw_type, str):
                structured_types.add(raw_type)
            elif isinstance(raw_type, list):
                structured_types.update(
                    item for item in raw_type if isinstance(item, str)
                )

            name = obj.get("name")
            if isinstance(name, str) and _clean_text(name):
                structured_names.add(_clean_text(name))

            address = _extract_address(obj.get("address"))
            if address:
                structured_addresses.add(address)

    title = _clean_text(" ".join(parser.title_parts)) or None
    visible_text = _clean_text(" ".join(parser.text_parts))
    return ParsedPage(
        title=title,
        headings=tuple(parser.headings),
        visible_text=visible_text,
        meta_robots=parser.meta_robots,
        structured_types=tuple(sorted(structured_types)),
        structured_names=tuple(sorted(structured_names)),
        structured_addresses=tuple(sorted(structured_addresses)),
        structured_data_documents=documents,
    )
