from pathlib import Path

from app.conversion.markdown_normalizer import (
    normalize_markdown_text,
    rewrite_markdown_image_paths,
    rewrite_markdown_image_paths_for_output,
)


def test_normalizer_converts_line_endings_and_final_newline() -> None:
    src = "line1\r\nline2\rline3"
    out = normalize_markdown_text(src)
    assert out == "line1\nline2\nline3\n"


def test_normalizer_trims_trailing_whitespace_outside_fences() -> None:
    src = "text with spaces   \n\nmore text\t \n"
    out = normalize_markdown_text(src)
    assert out == "text with spaces\n\nmore text\n"


def test_normalizer_preserves_fenced_content_as_is() -> None:
    src = "before  \n```python\nx = 1    \n```\nafter   \n"
    out = normalize_markdown_text(src)
    assert out == "before\n```python\nx = 1    \n```\nafter\n"


def test_normalizer_limits_blank_runs() -> None:
    src = "a\n\n\n\nb\n"
    out = normalize_markdown_text(src)
    assert out == "a\n\nb\n"


def test_rewrite_markdown_image_paths_updates_relative_targets() -> None:
    src = '![Logo](images/logo.png "Brand")\n![Remote](https://example.test/logo.png)\n'

    out = rewrite_markdown_image_paths(src, lambda target: f"assets/{target}")

    assert out == '![Logo](assets/images/logo.png "Brand")\n![Remote](https://example.test/logo.png)\n'


def test_rewrite_markdown_image_paths_preserves_fenced_code() -> None:
    src = "before ![A](a.png)\n```md\n![B](b.png)\n```\nafter ![C](c.png)\n"

    out = rewrite_markdown_image_paths(src, lambda target: f"assets/{target}")

    assert out == "before ![A](assets/a.png)\n```md\n![B](b.png)\n```\nafter ![C](assets/c.png)\n"


def test_rewrite_image_paths_for_output_uses_output_relative_paths(tmp_path: Path) -> None:
    source_base = tmp_path / "source"
    output_base = tmp_path / "out"

    out = rewrite_markdown_image_paths_for_output(
        "![Logo](<media/logo one.png>)\n",
        source_base=source_base,
        output_base=output_base,
    )

    assert out == "![Logo](<../source/media/logo one.png>)\n"
