import pytest

from app.stitcher.separator import (
    SEPARATOR_PREFIX,
    SEPARATOR_SUFFIX,
    build_separator,
)


def test_build_separator_has_exact_shape() -> None:
    assert (
        build_separator("chapter-01.md")
        == f"{SEPARATOR_PREFIX}chapter-01.md{SEPARATOR_SUFFIX}"
    )


def test_build_separator_rejects_empty_name() -> None:
    with pytest.raises(ValueError):
        build_separator("  ")
