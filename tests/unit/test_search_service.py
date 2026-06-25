from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from app.core.settings import AppSettings
from app.search.service import KeywordSearchService, format_search_summary


def _settings() -> AppSettings:
    return AppSettings.default()


def test_markdown_keyword_search_returns_line_matches(tmp_path: Path) -> None:
    source = tmp_path / "notes.md"
    source.write_text("Alpha\nneedle is here\nBeta\n", encoding="utf-8")

    summary = KeywordSearchService(_settings()).search_files([source], "needle")

    assert summary.total_matches == 1
    assert summary.results[0].matches[0].line_number == 2
    assert "needle is here" in format_search_summary(summary)


def test_search_is_case_insensitive_by_default(tmp_path: Path) -> None:
    source = tmp_path / "notes.md"
    source.write_text("Mixed Keyword\n", encoding="utf-8")

    summary = KeywordSearchService(_settings()).search_files([source], "keyword")

    assert summary.total_matches == 1


def test_case_sensitive_search_respects_case(tmp_path: Path) -> None:
    source = tmp_path / "notes.md"
    source.write_text("Mixed Keyword\n", encoding="utf-8")

    summary = KeywordSearchService(_settings()).search_files(
        [source],
        "keyword",
        case_sensitive=True,
    )

    assert summary.total_matches == 0


def test_binary_document_search_uses_tika(monkeypatch: object, tmp_path: Path) -> None:
    source = tmp_path / "source.odt"
    source.write_bytes(b"fake")
    tika = tmp_path / "tika-app.jar"
    tika.write_text("", encoding="utf-8")
    java = tmp_path / "java.exe"
    java.write_text("", encoding="utf-8")
    settings = _settings()
    settings.tika_app_path = str(tika)
    settings.java_binary_path = str(java)

    def fake_run(*_: object, **__: object) -> SimpleNamespace:
        return SimpleNamespace(returncode=0, stdout="Extracted target text\n", stderr="")

    monkeypatch.setattr("subprocess.run", fake_run)

    summary = KeywordSearchService(settings).search_files([source], "target")

    assert summary.total_matches == 1
    assert summary.results[0].matches[0].line == "Extracted target text"


def test_rtf_search_uses_tika(monkeypatch: object, tmp_path: Path) -> None:
    source = tmp_path / "source.rtf"
    source.write_text(r"{\rtf1 target}", encoding="utf-8")
    tika = tmp_path / "tika-app.jar"
    tika.write_text("", encoding="utf-8")
    java = tmp_path / "java.exe"
    java.write_text("", encoding="utf-8")
    settings = _settings()
    settings.tika_app_path = str(tika)
    settings.java_binary_path = str(java)

    def fake_run(*_: object, **__: object) -> SimpleNamespace:
        return SimpleNamespace(returncode=0, stdout="target in rtf\n", stderr="")

    monkeypatch.setattr("subprocess.run", fake_run)

    summary = KeywordSearchService(settings).search_files([source], "target")

    assert summary.total_matches == 1
    assert summary.results[0].matches[0].line == "target in rtf"


def test_binary_document_search_reports_missing_tika(tmp_path: Path) -> None:
    source = tmp_path / "source.docx"
    source.write_bytes(b"fake")
    java = tmp_path / "java.exe"
    java.write_text("", encoding="utf-8")
    settings = _settings()
    settings.java_binary_path = str(java)
    settings.tika_app_path = str(tmp_path / "missing.jar")

    summary = KeywordSearchService(settings).search_files([source], "target")

    assert summary.total_matches == 0
    assert "Configured Tika jar not found" in summary.results[0].error
