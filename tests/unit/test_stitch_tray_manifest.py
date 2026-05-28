from pathlib import Path

import pytest

from app.stitcher.tray_manifest import (
    StitchTrayError,
    load_stitch_tray,
    save_stitch_tray,
)


def test_save_and_load_tray_roundtrip(tmp_path: Path) -> None:
    first = tmp_path / "first.md"
    second = tmp_path / "second.md"
    first.write_text("a", encoding="utf-8")
    second.write_text("b", encoding="utf-8")
    output = tmp_path / "merged.md"
    tray_file = tmp_path / "bundle.omni-tray.json"

    save_stitch_tray(
        tray_file,
        input_files=[first, second],
        output_path=output,
    )
    tray = load_stitch_tray(tray_file)

    assert tray.input_files == [first, second]
    assert tray.output_path == output


def test_save_tray_rejects_empty_input(tmp_path: Path) -> None:
    tray_file = tmp_path / "empty.omni-tray.json"
    with pytest.raises(StitchTrayError):
        save_stitch_tray(tray_file, input_files=[])


def test_load_tray_rejects_wrong_kind(tmp_path: Path) -> None:
    tray_file = tmp_path / "bad.omni-tray.json"
    tray_file.write_text(
        '{"kind":"other","version":1,"items":[{"path":"a.md"}]}',
        encoding="utf-8",
    )

    with pytest.raises(StitchTrayError):
        load_stitch_tray(tray_file)


def test_load_tray_rejects_missing_items(tmp_path: Path) -> None:
    tray_file = tmp_path / "bad-items.omni-tray.json"
    tray_file.write_text(
        '{"kind":"omni-stitch-tray","version":1,"items":[]}',
        encoding="utf-8",
    )

    with pytest.raises(StitchTrayError):
        load_stitch_tray(tray_file)
