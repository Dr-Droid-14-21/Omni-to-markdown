from pathlib import Path

import pytest

from app.core.models import StitchManifest
from app.stitcher.stitcher_service import (
    StitchCancelledError,
    StitcherService,
    StitcherValidationError,
)


def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def test_stitcher_produces_expected_separator_flow(tmp_path: Path) -> None:
    a = tmp_path / "a.md"
    b = tmp_path / "b.md"
    c = tmp_path / "c.md"
    output = tmp_path / "stitched.md"

    _write(a, "alpha")
    _write(b, "beta\n")
    _write(c, "gamma")

    service = StitcherService()
    manifest = StitchManifest(input_files=[a, b, c], output_path=output)

    result = service.stitch(manifest)

    assert result.file_count == 3
    assert output.exists()
    assert (
        output.read_text(encoding="utf-8")
        == "alpha\n\n===========================a.md=================================\n\n"
        "beta\n\n===========================b.md=================================\n\n"
        "gamma\n"
    )


def test_stitcher_rejects_output_path_equal_to_input(tmp_path: Path) -> None:
    source = tmp_path / "a.md"
    _write(source, "alpha")

    service = StitcherService()
    manifest = StitchManifest(input_files=[source], output_path=source)

    with pytest.raises(StitcherValidationError):
        service.stitch(manifest)


def test_stitcher_reports_duplicate_basenames(tmp_path: Path) -> None:
    left_dir = tmp_path / "left"
    right_dir = tmp_path / "right"
    left_dir.mkdir()
    right_dir.mkdir()

    left = left_dir / "dup.md"
    right = right_dir / "dup.md"
    _write(left, "one")
    _write(right, "two")

    service = StitcherService()
    output = tmp_path / "out.md"
    result = service.stitch(StitchManifest(input_files=[left, right], output_path=output))

    assert len(result.warnings) == 1
    assert result.warnings[0].code == "DUPLICATE_BASENAME"


def test_stitcher_rejects_missing_input(tmp_path: Path) -> None:
    service = StitcherService()
    missing = tmp_path / "missing.md"
    output = tmp_path / "out.md"

    manifest = StitchManifest(input_files=[missing], output_path=output)
    with pytest.raises(StitcherValidationError):
        service.stitch(manifest)


def test_stitcher_cancellation_cleans_temp_output(tmp_path: Path) -> None:
    a = tmp_path / "a.md"
    b = tmp_path / "b.md"
    output = tmp_path / "stitched.md"
    _write(a, "alpha")
    _write(b, "beta")

    service = StitcherService()
    manifest = StitchManifest(input_files=[a, b], output_path=output)

    with pytest.raises(StitchCancelledError):
        service.stitch(manifest, should_cancel=lambda: True)

    assert output.exists() is False
    assert list(tmp_path.glob("*.tmp.md")) == []
