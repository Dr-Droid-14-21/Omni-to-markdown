from pathlib import Path

import pytest

from app.core.models import ConversionPlan, FileStatus, QueueItem, StitchManifest


def test_conversion_plan_rejects_non_markdown_output() -> None:
    with pytest.raises(ValueError):
        ConversionPlan(
            source_path=Path("example.docx"),
            output_path=Path("example.txt"),
            detected_extension=".docx",
            preferred_engine="pandoc",
        )


def test_queue_item_validates_progress() -> None:
    with pytest.raises(ValueError):
        QueueItem(
            id="q1",
            source_path=Path("example.docx"),
            display_name="example.docx",
            detected_type=".docx",
            status=FileStatus.PENDING,
            progress=101.0,
        )


def test_stitch_manifest_requires_files() -> None:
    with pytest.raises(ValueError):
        StitchManifest(input_files=[], output_path=Path("out.md"))
