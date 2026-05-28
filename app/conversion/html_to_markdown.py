from __future__ import annotations

import re
from collections.abc import Callable
from html import unescape
from importlib import import_module

from app.core.models import ConversionWarning


def html_to_markdown(html: str) -> tuple[str, list[ConversionWarning]]:
    warnings: list[ConversionWarning] = []
    lowered = html.lower()

    if "<table" in lowered:
        warnings.append(
            ConversionWarning(
                code="TABLE_LAYOUT_SIMPLIFIED",
                message="HTML table formatting may not be preserved in Markdown output.",
            )
        )
    if "<img" in lowered:
        warnings.append(
            ConversionWarning(
                code="IMAGE_EXPORT_LIMITED",
                message=(
                    "Embedded images were detected. Verify image references in generated markdown."
                ),
            )
        )

    markdownify = _load_markdownify()
    if markdownify is None:
        warnings.append(
            ConversionWarning(
                code="HTML_MARKDOWN_FALLBACK",
                message=(
                    "markdownify package is unavailable. Falling back to basic "
                    "HTML text conversion."
                ),
            )
        )
        return _basic_html_to_markdown(html), warnings

    converted = markdownify(
        html,
        heading_style="ATX",
        bullets="-",
        strip=["script", "style"],
        autolinks=False,
    )
    return converted.strip(), warnings


def _load_markdownify() -> Callable[..., str] | None:
    try:
        module = import_module("markdownify")
    except ImportError:
        return None
    converter = getattr(module, "markdownify", None)
    if callable(converter):
        return converter
    return None


def _basic_html_to_markdown(html: str) -> str:
    text = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", "", html)
    text = re.sub(
        r"(?is)<a\s+[^>]*href=['\"]([^'\"]+)['\"][^>]*>(.*?)</a>",
        lambda match: _render_link(match.group(2), match.group(1)),
        text,
    )

    for level in range(1, 7):
        text = re.sub(
            rf"(?is)<h{level}[^>]*>(.*?)</h{level}>",
            lambda match, current_level=level: _render_heading(current_level, match.group(1)),
            text,
        )

    block_tags = (
        "p",
        "div",
        "section",
        "article",
        "header",
        "footer",
        "aside",
        "li",
        "ul",
        "ol",
        "blockquote",
        "pre",
        "table",
        "tr",
    )
    for tag in block_tags:
        text = re.sub(rf"(?is)</?{tag}[^>]*>", "\n", text)

    text = re.sub(r"(?is)<br\s*/?>", "\n", text)
    text = re.sub(r"(?is)<[^>]+>", "", text)
    text = unescape(text)

    lines = [line.strip() for line in text.splitlines()]
    compact_lines: list[str] = []
    blank_run = 0
    for line in lines:
        if line == "":
            blank_run += 1
            if blank_run > 1:
                continue
        else:
            blank_run = 0
        compact_lines.append(line)
    return "\n".join(compact_lines).strip()


def _render_heading(level: int, inner_html: str) -> str:
    text = _strip_inline_tags(inner_html).strip()
    return f"\n{'#' * level} {text}\n"


def _render_link(inner_html: str, href: str) -> str:
    label = _strip_inline_tags(inner_html).strip()
    if not label:
        label = href
    return f"[{label}]({href})"


def _strip_inline_tags(value: str) -> str:
    return re.sub(r"(?is)<[^>]+>", "", unescape(value))
