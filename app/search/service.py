from __future__ import annotations

import shutil
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from app.core.settings import AppSettings
from app.search.tika_locator import resolve_tika_app_path

SEARCHABLE_EXTENSIONS = {
    ".md",
    ".markdown",
    ".txt",
    ".doc",
    ".docx",
    ".htm",
    ".html",
    ".odt",
    ".odf",
    ".pdf",
    ".rtf",
}
PLAIN_TEXT_EXTENSIONS = {".md", ".markdown", ".txt"}
MAX_RESULT_LINE_LENGTH = 320


@dataclass(slots=True)
class SearchMatch:
    file_path: Path
    line_number: int
    line: str


@dataclass(slots=True)
class SearchFileResult:
    file_path: Path
    matches: list[SearchMatch] = field(default_factory=list)
    error: str = ""


@dataclass(slots=True)
class SearchSummary:
    query: str
    files_scanned: int
    total_matches: int
    results: list[SearchFileResult]
    warnings: list[str] = field(default_factory=list)

    @property
    def files_with_matches(self) -> int:
        return sum(1 for result in self.results if result.matches)


class KeywordSearchService:
    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings

    def search_files(
        self,
        paths: list[Path],
        query: str,
        *,
        case_sensitive: bool = False,
        progress_callback: Callable[[int, int, SearchFileResult], None] | None = None,
        should_cancel: Callable[[], bool] | None = None,
    ) -> SearchSummary:
        clean_query = query.strip()
        if not clean_query:
            raise ValueError("Search query is required.")

        results: list[SearchFileResult] = []
        warnings: list[str] = []
        total = len(paths)
        for index, path in enumerate(paths, start=1):
            if should_cancel is not None and should_cancel():
                warnings.append("Search cancelled before all files were scanned.")
                break

            result = self._search_one(path, clean_query, case_sensitive=case_sensitive)
            results.append(result)
            if progress_callback is not None:
                progress_callback(index, total, result)

        total_matches = sum(len(result.matches) for result in results)
        return SearchSummary(
            query=clean_query,
            files_scanned=len(results),
            total_matches=total_matches,
            results=results,
            warnings=warnings,
        )

    def _search_one(self, path: Path, query: str, *, case_sensitive: bool) -> SearchFileResult:
        resolved = path.resolve()
        suffix = resolved.suffix.lower()
        if suffix not in SEARCHABLE_EXTENSIONS:
            return SearchFileResult(
                file_path=resolved,
                error=f"Unsupported search file type: {suffix or '(none)'}",
            )
        if not resolved.exists() or not resolved.is_file():
            return SearchFileResult(file_path=resolved, error="File not found.")

        try:
            text = self._extract_text(resolved)
        except RuntimeError as exc:
            return SearchFileResult(file_path=resolved, error=str(exc))
        except OSError as exc:
            return SearchFileResult(file_path=resolved, error=f"Unable to read file: {exc}")

        needle = query if case_sensitive else query.lower()
        matches: list[SearchMatch] = []
        for line_number, line in enumerate(text.splitlines(), start=1):
            haystack = line if case_sensitive else line.lower()
            if needle in haystack:
                matches.append(
                    SearchMatch(
                        file_path=resolved,
                        line_number=line_number,
                        line=_compact_line(line),
                    )
                )

        return SearchFileResult(file_path=resolved, matches=matches)

    def _extract_text(self, path: Path) -> str:
        if path.suffix.lower() in PLAIN_TEXT_EXTENSIONS:
            return path.read_text(encoding="utf-8", errors="replace")
        return self._extract_with_tika(path)

    def _extract_with_tika(self, path: Path) -> str:
        java_path, java_error = self._resolve_java_path()
        if java_path is None:
            raise RuntimeError(java_error)

        tika_path, tika_error = resolve_tika_app_path(self._settings.tika_app_path)
        if tika_path is None:
            raise RuntimeError(tika_error)

        try:
            completed = subprocess.run(
                [java_path, "-jar", str(tika_path), "--text", str(path)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=45,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError("Tika text extraction timed out.") from exc
        except OSError as exc:
            raise RuntimeError(f"Unable to run Tika: {exc}") from exc

        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout or "No Tika error detail.").strip()
            raise RuntimeError(f"Tika extraction failed: {_compact_line(detail)}")

        return completed.stdout or ""

    def _resolve_java_path(self) -> tuple[str | None, str]:
        override = self._settings.java_binary_path.strip()
        if override:
            path = Path(override).expanduser()
            if path.exists() and path.is_file():
                return str(path), ""
            return None, f"Configured Java executable not found: {path}"

        found = shutil.which("java")
        if found:
            return found, ""
        return None, "Java executable was not found in PATH."


def format_search_summary(summary: SearchSummary) -> str:
    lines = [
        f"Query: {summary.query}",
        (
            f"Scanned {summary.files_scanned} file(s); "
            f"{summary.total_matches} match(es) in {summary.files_with_matches} file(s)."
        ),
    ]
    lines.extend(summary.warnings)

    for result in summary.results:
        if result.error:
            lines.append(f"{result.file_path}: ERROR: {result.error}")
            continue
        for match in result.matches:
            lines.append(f"{match.file_path}:{match.line_number}: {match.line}")

    if summary.total_matches == 0 and not any(result.error for result in summary.results):
        lines.append("No matches found.")

    return "\n".join(lines)


def _compact_line(value: str) -> str:
    compacted = " ".join(value.strip().split())
    if len(compacted) <= MAX_RESULT_LINE_LENGTH:
        return compacted
    return f"{compacted[: MAX_RESULT_LINE_LENGTH - 3]}..."
