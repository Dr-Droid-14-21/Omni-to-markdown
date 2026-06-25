from pathlib import Path

from app.release_readiness import (
    CodeSignatureInspection,
    inspect_code_signature,
    inspect_release_readiness,
)


def _coverage(*, ok: bool = True, extensions: tuple[str, ...] = (".docx", ".pdf")):
    return type(
        "Coverage",
        (),
        {
            "ok": ok,
            "supported_extensions": extensions,
        },
    )()


def test_release_readiness_reports_missing_package(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.release_readiness.packaged_executable_path",
        lambda: type("FakePath", (), {"exists": lambda self: False})(),
    )
    monkeypatch.setattr(
        "app.release_readiness.explorer_integration_status",
        lambda: type("Status", (), {"installed": False, "sendto_installed": False})(),
    )
    monkeypatch.setattr(
        "app.release_readiness.inspect_context_menu_script_coverage",
        lambda: _coverage(),
    )

    readiness = inspect_release_readiness()

    assert readiness.packaged_app_exists is False
    assert readiness.explorer_menu_installed is False
    assert readiness.sendto_shortcut_installed is False
    assert readiness.context_menu_coverage_ok is True
    assert readiness.supported_extensions == (".docx", ".pdf")
    assert readiness.signing_required is False
    assert readiness.signature_status == "missing"
    assert "not built" in readiness.summary
    assert any("build_windows.ps1" in item for item in readiness.next_actions)


def test_release_readiness_reports_local_workflow_ready(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.release_readiness.packaged_executable_path",
        lambda: type("FakePath", (), {"exists": lambda self: True})(),
    )
    monkeypatch.setattr(
        "app.release_readiness.explorer_integration_status",
        lambda: type("Status", (), {"installed": True, "sendto_installed": True})(),
    )
    monkeypatch.setattr(
        "app.release_readiness.inspect_context_menu_script_coverage",
        lambda: _coverage(),
    )
    monkeypatch.setattr(
        "app.release_readiness.inspect_code_signature",
        lambda _: CodeSignatureInspection(status="NotSigned", detail="Not signed."),
    )

    readiness = inspect_release_readiness()

    assert readiness.packaged_app_exists is True
    assert readiness.explorer_menu_installed is True
    assert readiness.sendto_shortcut_installed is True
    assert readiness.context_menu_coverage_ok is True
    assert readiness.signing_required is False
    assert readiness.signature_status == "NotSigned"
    assert "Code signing is optional" in readiness.summary
    assert not any("Sign the packaged executable" in item for item in readiness.next_actions)


def test_release_readiness_reports_signed_distribution_ready(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.release_readiness.packaged_executable_path",
        lambda: type("FakePath", (), {"exists": lambda self: True})(),
    )
    monkeypatch.setattr(
        "app.release_readiness.explorer_integration_status",
        lambda: type("Status", (), {"installed": True, "sendto_installed": True})(),
    )
    monkeypatch.setattr(
        "app.release_readiness.inspect_context_menu_script_coverage",
        lambda: _coverage(),
    )
    monkeypatch.setattr(
        "app.release_readiness.inspect_code_signature",
        lambda _: CodeSignatureInspection(status="Valid", detail="Signature is valid."),
    )

    readiness = inspect_release_readiness()

    assert readiness.signing_required is False
    assert readiness.signature_status == "Valid"
    assert "code signing are ready" in readiness.summary
    assert not any("Sign the packaged executable" in item for item in readiness.next_actions)


def test_release_readiness_reports_context_menu_coverage_gap(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.release_readiness.packaged_executable_path",
        lambda: type("FakePath", (), {"exists": lambda self: True})(),
    )
    monkeypatch.setattr(
        "app.release_readiness.explorer_integration_status",
        lambda: type("Status", (), {"installed": True, "sendto_installed": True})(),
    )
    monkeypatch.setattr(
        "app.release_readiness.inspect_context_menu_script_coverage",
        lambda: _coverage(ok=False),
    )
    monkeypatch.setattr(
        "app.release_readiness.inspect_code_signature",
        lambda _: CodeSignatureInspection(status="Valid", detail="Signature is valid."),
    )

    readiness = inspect_release_readiness()

    assert readiness.context_menu_coverage_ok is False
    assert any("right-click coverage" in item for item in readiness.next_actions)


def test_code_signature_inspection_reports_unsigned_pe(tmp_path) -> None:
    executable = tmp_path / "unsigned.exe"
    _write_minimal_pe(executable, certificate_size=0)

    signature = inspect_code_signature(executable)

    assert signature.status == "NotSigned"
    assert "No Authenticode certificate table" in signature.detail


def test_code_signature_inspection_reports_certificate_table(tmp_path) -> None:
    executable = tmp_path / "signed.exe"
    _write_minimal_pe(executable, certificate_size=128)

    signature = inspect_code_signature(executable)

    assert signature.status == "Signed"
    assert "certificate table is present" in signature.detail


def _write_minimal_pe(path: Path, *, certificate_size: int) -> None:
    pe_offset = 0x80
    optional_header_size = 240
    content = bytearray(pe_offset + 24 + optional_header_size + certificate_size)
    content[0:2] = b"MZ"
    content[0x3C:0x40] = pe_offset.to_bytes(4, "little")
    content[pe_offset : pe_offset + 4] = b"PE\0\0"
    content[pe_offset + 20 : pe_offset + 22] = optional_header_size.to_bytes(2, "little")

    optional_header_offset = pe_offset + 24
    content[optional_header_offset : optional_header_offset + 2] = (0x20B).to_bytes(2, "little")
    security_directory_offset = optional_header_offset + 112 + (4 * 8)
    certificate_offset = len(content) - certificate_size if certificate_size else 0
    content[security_directory_offset : security_directory_offset + 4] = (
        certificate_offset.to_bytes(4, "little")
    )
    content[security_directory_offset + 4 : security_directory_offset + 8] = (
        certificate_size.to_bytes(4, "little")
    )
    path.write_bytes(content)
