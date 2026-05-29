from pathlib import Path

from app.conversion.dependency_check import (
    DependencyStatus,
    dependency_route_options_for_extension,
    detect_all_dependencies,
    detect_engine_versions,
    detect_java,
    detect_libreoffice,
    detect_mammoth_package,
    detect_pandoc,
    detect_pdfminer_package,
    detect_pymupdf_package,
    detect_tika_app,
    required_dependencies_for_extension,
)
from app.core.settings import AppSettings


def _settings() -> AppSettings:
    return AppSettings.default()


def test_required_dependencies_mapping() -> None:
    assert required_dependencies_for_extension(".doc") == {"libreoffice"}
    assert required_dependencies_for_extension(".odf") == {"libreoffice"}
    assert required_dependencies_for_extension(".docx") == {"pandoc"}
    assert required_dependencies_for_extension(".odt") == {"pandoc"}
    assert required_dependencies_for_extension(".pdf") == {"pymupdf"}


def test_dependency_route_options_mapping() -> None:
    assert dependency_route_options_for_extension(".docx") == [
        {"pandoc"},
        {"mammoth"},
        {"libreoffice"},
    ]
    assert dependency_route_options_for_extension(".odt") == [{"pandoc"}, {"libreoffice"}]
    assert dependency_route_options_for_extension(".pdf") == [{"pymupdf"}, {"pdfminer"}]


def test_override_path_missing_marks_unavailable(tmp_path: Path) -> None:
    settings = _settings()
    settings.pandoc_binary_path = str(tmp_path / "missing-pandoc.exe")
    status = detect_pandoc(settings)

    assert status.available is False
    assert "Configured path not found" in status.detail


def test_override_path_existing_file_marks_available(tmp_path: Path) -> None:
    fake_binary = tmp_path / "pandoc.exe"
    fake_binary.write_text("", encoding="utf-8")
    settings = _settings()
    settings.pandoc_binary_path = str(fake_binary)
    status = detect_pandoc(settings)

    assert status.available is True
    assert status.path == str(fake_binary)


def test_detect_all_dependencies_uses_which(monkeypatch: object) -> None:
    import shutil

    def fake_which(name: str) -> str | None:
        mapping = {
            "pandoc": r"C:\Tools\pandoc.exe",
            "java": r"C:\Tools\java.exe",
            "soffice": None,
            "libreoffice": r"C:\Tools\soffice.exe",
        }
        return mapping.get(name)

    monkeypatch.setattr(shutil, "which", fake_which)
    monkeypatch.setattr("importlib.util.find_spec", lambda _: object())
    monkeypatch.setattr(
        "app.conversion.dependency_check.resolve_tika_app_path",
        lambda _: (Path(r"C:\Tools\tika-app.jar"), ""),
    )
    settings = _settings()
    settings.pandoc_binary_path = ""
    settings.libreoffice_binary_path = ""

    statuses = detect_all_dependencies(settings)
    assert statuses["pandoc"].available is True
    assert statuses["libreoffice"].available is True
    assert statuses["java"].available is True
    assert statuses["tika"].available is True
    assert statuses["mammoth"].available is True
    assert statuses["pymupdf"].available is True
    assert statuses["pdfminer"].available is True


def test_detect_libreoffice_missing_when_not_found(monkeypatch: object) -> None:
    import shutil

    monkeypatch.setattr(shutil, "which", lambda _: None)
    settings = _settings()
    settings.libreoffice_binary_path = ""
    status = detect_libreoffice(settings)

    assert status.available is False
    assert "not found in PATH" in status.detail


def test_detect_java_missing_when_not_found(monkeypatch: object) -> None:
    import shutil

    monkeypatch.setattr(shutil, "which", lambda _: None)
    settings = _settings()
    settings.java_binary_path = ""
    status = detect_java(settings)

    assert status.available is False
    assert "not found in PATH" in status.detail


def test_detect_tika_app_uses_configured_path(tmp_path: Path) -> None:
    tika = tmp_path / "tika-app.jar"
    tika.write_text("", encoding="utf-8")
    settings = _settings()
    settings.tika_app_path = str(tika)

    status = detect_tika_app(settings)

    assert status.available is True
    assert status.path == str(tika)


def test_detect_engine_versions_collects_first_line(monkeypatch: object) -> None:
    from types import SimpleNamespace

    def fake_statuses(_: AppSettings) -> dict[str, DependencyStatus]:
        return {
            "pandoc": DependencyStatus(name="pandoc", available=True, path="pandoc"),
            "libreoffice": DependencyStatus(name="libreoffice", available=False),
            "java": DependencyStatus(name="java", available=True, path="java"),
            "tika": DependencyStatus(name="tika", available=True, path="tika-app-3.2.3.jar"),
            "mammoth": DependencyStatus(name="mammoth", available=True, path="mammoth"),
            "pymupdf": DependencyStatus(name="pymupdf", available=True, path="pymupdf"),
            "pdfminer": DependencyStatus(name="pdfminer", available=True, path="pdfminer"),
        }

    def fake_run(*_: object, **__: object) -> SimpleNamespace:
        return SimpleNamespace(returncode=0, stdout="pandoc 3.0.0\nextra", stderr="")

    monkeypatch.setattr("app.conversion.dependency_check.detect_all_dependencies", fake_statuses)
    monkeypatch.setattr("subprocess.run", fake_run)
    monkeypatch.setattr("app.conversion.dependency_check.version", lambda _: "1.0.0")

    versions = detect_engine_versions(_settings())
    assert versions["pandoc"] == "pandoc 3.0.0"
    assert versions["libreoffice"] == "unavailable"
    assert versions["java"] == "pandoc 3.0.0"
    assert versions["tika"] == "tika-app-3.2.3.jar"
    assert versions["mammoth"] == "1.0.0"
    assert versions["pymupdf"] == "1.0.0"
    assert versions["pdfminer"] == "1.0.0"


def test_detect_mammoth_package_missing(monkeypatch: object) -> None:
    monkeypatch.setattr("importlib.util.find_spec", lambda _: None)
    status = detect_mammoth_package(_settings())

    assert status.available is False
    assert "not installed" in status.detail


def test_detect_pdf_packages_missing(monkeypatch: object) -> None:
    monkeypatch.setattr("importlib.util.find_spec", lambda _: None)

    pymupdf_status = detect_pymupdf_package(_settings())
    pdfminer_status = detect_pdfminer_package(_settings())

    assert pymupdf_status.available is False
    assert pdfminer_status.available is False
