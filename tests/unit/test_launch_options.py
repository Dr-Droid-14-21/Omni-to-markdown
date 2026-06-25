from pathlib import Path

from app.launch_options import parse_launch_options


def test_parse_launch_options_collects_paths_and_flags() -> None:
    options = parse_launch_options(
        [
            "--convert-now",
            "--no-splash",
            "--self-check",
            r"C:\docs\sample.docx",
            r"C:\docs\batch",
        ]
    )

    assert options.auto_convert is True
    assert options.suppress_splash is True
    assert options.self_check is True
    assert options.selected_paths == [
        Path(r"C:\docs\sample.docx"),
        Path(r"C:\docs\batch"),
    ]


def test_parse_launch_options_ignores_unknown_flags() -> None:
    options = parse_launch_options(
        [
            "--future-flag",
            r"C:\docs\sample.pdf",
        ]
    )

    assert options.auto_convert is False
    assert options.selected_paths == [Path(r"C:\docs\sample.pdf")]
