from __future__ import annotations

from app.conversion.html_to_markdown import html_to_markdown


def test_html_to_markdown_drops_libreoffice_style_metadata() -> None:
    html = """
    <html>
      <head>
        <style>
          @page { size: 8.5in 11in; margin: 0.79in }
          p { line-height: 115%; margin-bottom: 0.1in; background: transparent }
          pre.western { font-family: "Liberation Mono", monospace; font-size: 10pt }
        </style>
      </head>
      <body>
        <h1>Sample Document</h1>
        <p>This is a sample document.</p>
      </body>
    </html>
    """

    markdown, warnings = html_to_markdown(html)

    assert "@page" not in markdown
    assert "Liberation Mono" not in markdown
    assert "# Sample Document" in markdown
    assert "This is a sample document." in markdown
    assert warnings == []
