from pathlib import Path

from app.core.file_detection import check_output_directory_writable, detect_file


def _write_bytes(path: Path, content: bytes) -> None:
    path.write_bytes(content)


def test_detect_pdf_header_ok(tmp_path: Path) -> None:
    pdf = tmp_path / "sample.pdf"
    _write_bytes(pdf, b"%PDF-1.7\ncontent")

    preflight = detect_file(pdf)

    assert preflight.error == ""
    assert preflight.supported is True
    assert preflight.detected_kind == "pdf"
    assert preflight.warnings == []


def test_detect_unsupported_extension(tmp_path: Path) -> None:
    txt = tmp_path / "notes.txt"
    _write_bytes(txt, b"hello")

    preflight = detect_file(txt)

    assert preflight.supported is False
    assert "Unsupported file extension" in preflight.error


def test_detect_header_mismatch_warning(tmp_path: Path) -> None:
    docx = tmp_path / "bad.docx"
    _write_bytes(docx, b"not-a-zip")

    preflight = detect_file(docx)

    assert preflight.error == ""
    assert preflight.supported is True
    assert len(preflight.warnings) == 1
    assert preflight.warnings[0].code == "HEADER_MISMATCH"


def test_detect_odf_adds_ambiguity_warning(tmp_path: Path) -> None:
    odf = tmp_path / "formula.odf"
    _write_bytes(odf, b"anything")

    preflight = detect_file(odf)

    assert preflight.error == ""
    assert len(preflight.warnings) == 1
    assert preflight.warnings[0].code == "ODF_AMBIGUOUS"


def test_detect_missing_file(tmp_path: Path) -> None:
    missing = tmp_path / "missing.docx"

    preflight = detect_file(missing)

    assert preflight.error == "File does not exist."


def test_output_directory_writable(tmp_path: Path) -> None:
    ok, reason = check_output_directory_writable(tmp_path / "out")
    assert ok is True
    assert reason == ""
