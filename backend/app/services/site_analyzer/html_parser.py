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
    heading_levels: tuple[int, ...]
    visible_text: str
    meta_robots: str | None
    meta_description: str | None
    viewport: str | None
    canonical_href: str | None
    form_count: int
    link_hrefs: tuple[str, ...]
    interactive_texts: tuple[str, ...]
    image_count: int
    images_with_alt_attribute: int
    structured_types: tuple[str, ...]
    structured_names: tuple[str, ...]
    structured_addresses: tuple[str, ...]
    structured_data_documents: int


class _PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.headings: list[str] = []
        self.heading_levels: list[int] = []
        self.text_parts: list[str] = []
        self.meta_robots: str | None = None
        self.meta_description: str | None = None
        self.viewport: str | None = None
        self.canonical_href: str | None = None
        self.form_count = 0
        self.link_hrefs: list[str] = []
        self.interactive_texts: list[str] = []
        self.image_count = 0
        self.images_with_alt_attribute = 0
        self.jsonld_documents: list[str] = []
        self._jsonld_parts: list[str] = []
        self._in_title = False
        self._heading_tag: str | None = None
        self._heading_parts: list[str] = []
        self._interactive_tag: str | None = None
        self._interactive_parts: list[str] = []
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
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._heading_tag = tag
            self._heading_parts = []
        if tag in {"a", "button"}:
            self._interactive_tag = tag
            self._interactive_parts = []

        if tag == "a":
            href = (attr_map.get("href") or "").strip()
            if href:
                self.link_hrefs.append(href)
        elif tag == "form":
            self.form_count += 1
        elif tag == "img":
            self.image_count += 1
            if "alt" in attr_map:
                self.images_with_alt_attribute += 1
        elif tag == "link":
            rel = (attr_map.get("rel") or "").lower().split()
            href = (attr_map.get("href") or "").strip()
            if "canonical" in rel and href:
                self.canonical_href = href

        if tag == "meta":
            name = (attr_map.get("name") or "").lower()
            content = (attr_map.get("content") or "").strip() or None
            if name == "robots":
                self.meta_robots = content
            elif name == "description":
                self.meta_description = content
            elif name == "viewport":
                self.viewport = content

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
                self.heading_levels.append(int(tag[1]))
            self._heading_tag = None
            self._heading_parts = []
        if self._interactive_tag == tag:
            text = _clean_text(" ".join(self._interactive_parts))
            if text:
                self.interactive_texts.append(text)
            self._interactive_tag = None
            self._interactive_parts = []

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
        if self._interactive_tag:
            self._interactive_parts.append(data)
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
                structured_types.update(item for item in raw_type if isinstance(item, str))

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
        heading_levels=tuple(parser.heading_levels),
        visible_text=visible_text,
        meta_robots=parser.meta_robots,
        meta_description=parser.meta_description,
        viewport=parser.viewport,
        canonical_href=parser.canonical_href,
        form_count=parser.form_count,
        link_hrefs=tuple(parser.link_hrefs),
        interactive_texts=tuple(parser.interactive_texts),
        image_count=parser.image_count,
        images_with_alt_attribute=parser.images_with_alt_attribute,
        structured_types=tuple(sorted(structured_types)),
        structured_names=tuple(sorted(structured_names)),
        structured_addresses=tuple(sorted(structured_addresses)),
        structured_data_documents=documents,
    )
