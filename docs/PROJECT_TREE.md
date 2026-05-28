# PROJECT_TREE.md

## Repository tree snapshot (2026-05-23)

```text
Omni to Markdown/
  app/
    main.py
    conversion/
      base.py
      dependency_check.py
      html_to_markdown.py
      libreoffice_engine.py
      mammoth_engine.py
      markdown_normalizer.py
      pandoc_engine.py
      pdf_pdfminer_engine.py
      pdf_pymupdf_engine.py
      reports.py
      router.py
      service.py
    core/
      file_detection.py
      logging_config.py
      models.py
      paths.py
      process.py
      settings.py
    resources/
      icons/
      styles/
        app.qss
    stitcher/
      manifest.py
      separator.py
      stitcher_service.py
      tray_manifest.py
    ui/
      converter_tab.py
      main_window.py
      neon_effects.py
      settings_dialog.py
      stitcher_tab.py
      widgets/
        drag_drop_list.py
        file_queue_table.py
        warning_panel.py
    workers/
      conversion_worker.py
      stitch_worker.py
  docs/
    conversion-quality.md
    dependency-installation.md
    developer-setup.md
    PROJECT_TREE.md
    troubleshooting.md
    user-guide.md
  packaging/
    linux/
    macos/
    windows/
      OmniToMarkdown.spec
  scripts/
    build_linux.sh
    build_windows.ps1
    run_tests.ps1
    run_tests.sh
  tests/
    fixtures/
      sample.pdf
    integration/
      test_libreoffice_engine_integration.py
      test_pandoc_engine_integration.py
      test_pdf_fixture_integration.py
    unit/
      test_conversion_service.py
      test_conversion_worker.py
      test_dependency_check.py
      test_libreoffice_engine.py
      test_file_detection.py
      test_mammoth_engine.py
      test_markdown_normalizer.py
      test_models.py
      test_pandoc_engine.py
      test_pdf_pdfminer_engine.py
      test_pdf_pymupdf_engine.py
      test_process.py
      test_reports.py
      test_separator.py
      test_settings.py
      test_stitcher_service.py
      test_stitch_tray_manifest.py
      test_stitch_worker.py
      test_ui_accessibility.py
  .editorconfig
  .gitignore
  ALL-FILES-CHANGELOG.md
  CODING_PIPELINE_CODING_PROGRESS.md
  OPUS_UI_UX_FOCUS.md
  PLAN.md
  TODO.md
  pyproject.toml
  README.md
```

## Notes

- Modular layout now includes working conversion service + worker threading baseline.
- Stitcher UX now includes tray archive save/load support with manifest validation tests.
- UI coverage now includes offscreen smoke/accessibility tests.
- PDF conversion now has a safe fixture integration test.
- Windows packaging now includes a PyInstaller spec.
- Root planning markdown files are still authoritative and updated alongside code changes.
