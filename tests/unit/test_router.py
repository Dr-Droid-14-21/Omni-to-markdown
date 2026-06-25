from pathlib import Path

from app.conversion.router import build_plan


def test_html_plan_uses_local_html_engine_with_pandoc_fallback() -> None:
    plan = build_plan(Path("page.html"), Path("page.md"))

    assert plan.detected_extension == ".html"
    assert plan.preferred_engine == "html"
    assert plan.fallback_engines == ["pandoc"]
    assert plan.requires_external_tools is False
    assert plan.estimated_risk_level == "low"


def test_rtf_plan_uses_libreoffice_route() -> None:
    plan = build_plan(Path("notes.rtf"), Path("notes.md"))

    assert plan.detected_extension == ".rtf"
    assert plan.preferred_engine == "libreoffice"
    assert plan.fallback_engines == []
    assert plan.requires_external_tools is True
    assert plan.estimated_risk_level == "medium"


def test_txt_plan_uses_local_text_engine() -> None:
    plan = build_plan(Path("notes.txt"), Path("notes.md"))

    assert plan.detected_extension == ".txt"
    assert plan.preferred_engine == "text"
    assert plan.fallback_engines == []
    assert plan.requires_external_tools is False
    assert plan.estimated_risk_level == "low"
