from __future__ import annotations

import importlib.util
import shutil
import subprocess
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from app.core.settings import AppSettings
from app.search.tika_locator import resolve_tika_app_path


@dataclass(slots=True)
class DependencyStatus:
    name: str
    available: bool
    path: str = ""
    detail: str = ""


def detect_pandoc(settings: AppSettings) -> DependencyStatus:
    return _detect_executable(
        name="pandoc",
        override=settings.pandoc_binary_path.strip(),
        candidates=["pandoc"],
    )


def detect_libreoffice(settings: AppSettings) -> DependencyStatus:
    return _detect_executable(
        name="libreoffice",
        override=settings.libreoffice_binary_path.strip(),
        candidates=["soffice", "libreoffice"],
    )


def detect_java(settings: AppSettings) -> DependencyStatus:
    return _detect_executable(
        name="java",
        override=settings.java_binary_path.strip(),
        candidates=["java"],
    )


def detect_tika_app(settings: AppSettings) -> DependencyStatus:
    tika_path, detail = resolve_tika_app_path(settings.tika_app_path)
    if tika_path is None:
        return DependencyStatus(name="tika", available=False, detail=detail)
    return DependencyStatus(name="tika", available=True, path=str(tika_path))


def detect_mammoth_package(_: AppSettings) -> DependencyStatus:
    return _detect_python_package(name="mammoth", module_name="mammoth")


def detect_pymupdf_package(_: AppSettings) -> DependencyStatus:
    return _detect_python_package(name="pymupdf", module_name="fitz")


def detect_pdfminer_package(_: AppSettings) -> DependencyStatus:
    return _detect_python_package(name="pdfminer", module_name="pdfminer")


def detect_all_dependencies(settings: AppSettings) -> dict[str, DependencyStatus]:
    pandoc = detect_pandoc(settings)
    libreoffice = detect_libreoffice(settings)
    java = detect_java(settings)
    tika = detect_tika_app(settings)
    mammoth = detect_mammoth_package(settings)
    pymupdf = detect_pymupdf_package(settings)
    pdfminer = detect_pdfminer_package(settings)
    return {
        "pandoc": pandoc,
        "libreoffice": libreoffice,
        "java": java,
        "tika": tika,
        "mammoth": mammoth,
        "pymupdf": pymupdf,
        "pdfminer": pdfminer,
    }


def detect_engine_versions(settings: AppSettings) -> dict[str, str]:
    statuses = detect_all_dependencies(settings)
    versions: dict[str, str] = {}
    for name, status in statuses.items():
        if not status.available:
            versions[name] = "unavailable"
            continue
        if name in {"mammoth", "pymupdf", "pdfminer"}:
            versions[name] = _probe_python_package_version(_package_name_for_dependency(name))
            continue
        if name == "tika":
            versions[name] = Path(status.path).name
            continue
        executable = status.path or name
        versions[name] = _probe_version_line(executable)
    return versions


def required_dependencies_for_extension(extension: str) -> set[str]:
    options = dependency_route_options_for_extension(extension)
    if not options:
        return set()
    return set(options[0])


def dependency_route_options_for_extension(extension: str) -> list[set[str]]:
    ext = extension.lower()
    if ext == ".doc":
        return [{"libreoffice"}]
    if ext == ".docx":
        return [{"pandoc"}, {"mammoth"}, {"libreoffice"}]
    if ext == ".odt":
        return [{"pandoc"}, {"libreoffice"}]
    if ext == ".odf":
        return [{"libreoffice"}]
    if ext == ".pdf":
        return [{"pymupdf"}, {"pdfminer"}]
    return [set()]


def _detect_executable(name: str, override: str, candidates: list[str]) -> DependencyStatus:
    if override:
        path = Path(override).expanduser()
        if path.exists() and path.is_file():
            return DependencyStatus(name=name, available=True, path=str(path))
        return DependencyStatus(
            name=name,
            available=False,
            path=str(path),
            detail=f"Configured path not found: {path}",
        )

    for candidate in candidates:
        found = shutil.which(candidate)
        if found:
            return DependencyStatus(name=name, available=True, path=found)

    return DependencyStatus(
        name=name,
        available=False,
        detail=f"{name} executable was not found in PATH.",
    )


def _detect_python_package(name: str, module_name: str) -> DependencyStatus:
    if importlib.util.find_spec(module_name) is None:
        return DependencyStatus(
            name=name,
            available=False,
            detail=f"Python package `{name}` is not installed.",
        )
    return DependencyStatus(
        name=name,
        available=True,
        path=module_name,
    )


def _probe_version_line(executable: str) -> str:
    try:
        completed = subprocess.run(
            [executable, "--version"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "version-probe-failed"

    output = (completed.stdout or completed.stderr or "").splitlines()
    if not output:
        return "unknown-version"
    return output[0].strip()


def _probe_python_package_version(package_name: str) -> str:
    try:
        return version(package_name)
    except PackageNotFoundError:
        return "unknown-version"


def _package_name_for_dependency(dependency_name: str) -> str:
    mapping = {
        "mammoth": "mammoth",
        "pymupdf": "PyMuPDF",
        "pdfminer": "pdfminer.six",
    }
    return mapping.get(dependency_name, dependency_name)
