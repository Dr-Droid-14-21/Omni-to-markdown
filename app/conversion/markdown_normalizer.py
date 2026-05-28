from __future__ import annotations

import os
import re
from collections.abc import Callable
from pathlib import Path

_IMAGE_PATTERN = re.compile(r"!\[(?P<alt>[^\]\n]*)\]\((?P<target>[^)\n]+)\)")
_SCHEME_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")


def normalize_markdown_text(content: str) -> str:
    text = content.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")
    normalized: list[str] = []
    in_fenced_block = False
    fence_marker = ""

    for line in lines:
        stripped = line.lstrip()
        marker = _fence_marker(stripped)
        if marker and not in_fenced_block:
            in_fenced_block = True
            fence_marker = marker
            normalized.append(line.rstrip())
            continue
        if marker and in_fenced_block and marker == fence_marker:
            in_fenced_block = False
            fence_marker = ""
            normalized.append(line.rstrip())
            continue

        if in_fenced_block:
            normalized.append(line)
        else:
            normalized.append(line.rstrip())

    compact = _collapse_excess_blank_lines(normalized)
    result = "\n".join(compact).strip("\n")
    return f"{result}\n" if result else "\n"


def normalize_markdown_file(path: Path) -> None:
    current = path.read_text(encoding="utf-8")
    path.write_text(normalize_markdown_text(current), encoding="utf-8", newline="\n")


def rewrite_markdown_image_paths(
    content: str,
    rewriter: Callable[[str], str],
) -> str:
    lines = content.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    rewritten: list[str] = []
    in_fenced_block = False
    fence_marker = ""

    for line in lines:
        stripped = line.lstrip()
        marker = _fence_marker(stripped)
        if marker and not in_fenced_block:
            in_fenced_block = True
            fence_marker = marker
            rewritten.append(line)
            continue
        if marker and in_fenced_block and marker == fence_marker:
            in_fenced_block = False
            fence_marker = ""
            rewritten.append(line)
            continue

        rewritten.append(line if in_fenced_block else _rewrite_images_in_line(line, rewriter))

    return "\n".join(rewritten)


def rewrite_markdown_image_paths_for_output(
    content: str,
    *,
    source_base: Path,
    output_base: Path,
) -> str:
    source_root = source_base.resolve()
    output_root = output_base.resolve()

    def rewriter(target: str) -> str:
        if _is_external_image_target(target):
            return target
        target_path = Path(target)
        if target_path.is_absolute():
            return target
        absolute_target = (source_root / target_path).resolve()
        return Path(os.path.relpath(absolute_target, output_root)).as_posix()

    return rewrite_markdown_image_paths(content, rewriter)


def _fence_marker(stripped_line: str) -> str:
    for marker in ("```", "~~~"):
        if stripped_line.startswith(marker):
            return marker
    return ""


def _collapse_excess_blank_lines(lines: list[str], max_consecutive: int = 1) -> list[str]:
    output: list[str] = []
    blank_run = 0
    for line in lines:
        if line == "":
            blank_run += 1
            if blank_run > max_consecutive:
                continue
        else:
            blank_run = 0
        output.append(line)
    return output


def _rewrite_images_in_line(line: str, rewriter: Callable[[str], str]) -> str:
    def replace(match: re.Match[str]) -> str:
        payload = match.group("target").strip()
        parsed = _split_image_payload(payload)
        if parsed is None:
            return match.group(0)

        target, title, used_angle_target = parsed
        if not target or _is_external_image_target(target):
            rewritten_target = target
        else:
            rewritten_target = rewriter(target)

        target_text = _format_image_target(rewritten_target, used_angle_target)
        return f"![{match.group('alt')}]({target_text}{title})"

    return _IMAGE_PATTERN.sub(replace, line)


def _split_image_payload(payload: str) -> tuple[str, str, bool] | None:
    if payload.startswith("<"):
        closing = payload.find(">")
        if closing < 0:
            return None
        return payload[1:closing], payload[closing + 1 :], True

    parts = payload.split(maxsplit=1)
    if not parts:
        return None
    title = f" {parts[1]}" if len(parts) == 2 else ""
    return parts[0], title, False


def _format_image_target(target: str, force_angle_target: bool) -> str:
    if force_angle_target or any(char.isspace() for char in target):
        return f"<{target}>"
    return target


def _is_external_image_target(target: str) -> bool:
    stripped = target.strip()
    return stripped.startswith("#") or bool(_SCHEME_PATTERN.match(stripped))
