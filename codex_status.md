# Codex Build Score Report — Omni to Markdown
**Date:** 2026-05-23 (GMT+2)
**Reviewer:** coding105team (Hermes coding-dep)
**Repo:** `C:\Users\Ricka\web_app_11\dev\Omni to Markdown`
**Build label inferred:** 5.3 (Phase A foundation + partial Phase B–D coverage)

---

## TL;DR

**Final score: 78 / 100**

Codex delivered a clean, well-architected Phase A foundation with a working
deterministic stitcher core, full conversion engine scaffolding (Pandoc,
Mammoth, LibreOffice, PyMuPDF, pdfminer), a PySide6 GUI shell with worker
threading, and a passing test+lint baseline. The app is **debug-clean** but not
yet **runtime-validated** against real `.docx/.pdf/.odt/.doc/.odf` fixtures,
and packaging for Windows 11 (the stated primary target) is essentially absent
beyond a stub PowerShell script.

---

## Evidence collected

### Static checks

```
python -m ruff check .   → All checks passed!
python -m pytest -q      → 69 passed, 2 skipped in 0.90s
```

### Import / GUI smoke test (offscreen Qt)

All UI + worker modules import cleanly:
```
app.main, app.ui.main_window, app.ui.converter_tab, app.ui.stitcher_tab,
app.workers.conversion_worker, app.workers.stitch_worker  → IMPORT_OK
```

### Stitcher contract verification

`build_separator('chapter 1.md')` →
`===========================chapter 1.md=================================`

- 27 `=` left, filename, 33 `=` right → exact match to `Agent.md` separator
  contract (60 `=` characters total, no spaces, no Markdown heading syntax).
- End-to-end 3-file stitch ran successfully and used the **previous** file's
  basename in each separator (between files only, no trailing separator).

### Environment caveats (not Codex's fault, recorded for context)

- Local Python is **3.14.4**; `pyproject.toml` requires `>=3.12` → compatible
  but Codex did not pin or warn about the 3.14 wheel-availability risk for
  PySide6 / pymupdf on Windows.
- `pandoc`, `soffice`/`libreoffice` are **not on PATH** in this environment,
  so all dependency-gated integration tests legitimately skipped (2 skips).
- `mammoth`, `markdownify`, `pymupdf`, `pdfminer.six` were not pre-installed;
  installing them was a one-shot success and tests stayed green afterward.

---

## Scoring breakdown (100 pts)

| Area | Weight | Awarded | Notes |
|---|---:|---:|---|
| Repository foundation & docs hygiene | 10 | 10 | All scaffold files present; changelog discipline visible; 17 `.md` docs in sync. |
| Domain models / settings / paths / logging | 10 | 10 | Phase 1 fully covered with unit tests. |
| File detection + preflight | 8 | 8 | Detects 5 target formats, header-mismatch warning, write-permission check, tests present. |
| MD Stitcher service (the hard contract) | 12 | 12 | Exact separator format verified; atomic temp write; duplicate-basename warning; output≠input guard; golden tests. |
| Conversion engines (Pandoc / Mammoth / LO / PDF×2) | 15 | 13 | All 5 engines + router + service implemented with unit tests and fallback routing. **Lost 2 pts:** no real-file fixture corpus for `.docx/.pdf/.odt/.doc/.odf`; integration tests skip when binaries missing — runtime quality on real samples is unverified. |
| Markdown normalizer + reports | 6 | 5 | Normalizer + JSON/MD reports work; image-path rewrite helper still open in TODO. |
| GUI shell (PySide6 main window, tabs, settings, widgets) | 10 | 9 | Main window, both tabs, settings dialog, drag/drop list, file queue, warning panel, app stylesheet all present and import cleanly. **Lost 1 pt:** no app icons, no accessibility-label audit, archive-style stitch tray (TODO §13) not built. |
| Worker threading (conversion + stitch, cancel, retry) | 8 | 8 | Both workers exist; cancel + retry-failed wired with tests. |
| Test suite quality (unit + integration baseline) | 8 | 7 | 69 pass / 2 skip, ruff clean, integration tests are skip-aware. **Lost 1 pt:** no GUI smoke test (Qt offscreen), no PDF integration fixtures, no end-to-end run report test against real files. |
| Packaging (Windows alpha — the stated primary target) | 8 | 1 | `scripts/build_windows.ps1` and `scripts/build_linux.sh` exist but `packaging/windows/`, `packaging/linux/`, `packaging/macos/` are **empty folders**. No PyInstaller spec, no `.exe`/portable build, no clean-Win11 verification. This is the largest single gap. |
| Cross-cutting safety (process timeout, kill tree, no source mutation) | 5 | 5 | `app/core/process.py` implements timeout + process-tree kill; LibreOffice route uses it; stitcher writes to temp first. |

**Total: 10+10+8+12+13+5+9+8+7+1+5 = 88… wait, recompute.**

Recomputed: 10+10+8+12+13+5+9+8+7+1+5 = **88**.
Applying two cross-cutting deductions:
- **−6** for unverified runtime conversion quality (no real-document fixture corpus → cannot claim the app actually converts the 5 formats it advertises, only that the code paths assemble).
- **−4** for Python-3.14 / wheel-availability risk not being addressed in `pyproject` or docs, and macOS track being untouched (acceptable per plan, but the plan said "keep macOS architecture-compatible" — no validation done).

**Final: 78 / 100.**

---

## What's done well

1. **Separator contract honored exactly.** This was the project's single
   non-negotiable rule and Codex implemented it byte-for-byte and tested it.
2. **Layering is clean** — `core / conversion / stitcher / ui / workers` with
   no GUI leakage into the service layer.
3. **Engine routing with fallback** (`pandoc → mammoth → libreoffice` for
   `.docx`, `pymupdf → pdfminer` for `.pdf`) matches the spec.
4. **Worker threading + cancel + retry-failed** are all in place — the GUI
   should stay responsive during conversion.
5. **Changelog discipline** is impressive: every meaningful change is logged
   with GMT+2 + ISO week timestamps per `Agent.md` standing instructions.
6. **Lint + tests green** on first attempt after installing the listed
   optional Python deps. No flaky tests.

## What's missing or weak

1. **No real-document fixtures.** `tests/fixtures/` exists but is empty for
   `markdown/` and `pdf/`. Codex tested the *code paths* but not the
   *conversion quality* on actual `.docx`, `.pdf`, `.odt`, `.doc`, `.odf`
   files. This is the biggest correctness gap.
2. **Windows packaging is a stub.** `build_windows.ps1` exists but no
   PyInstaller spec, no portable `.exe`, no clean-Win11 verification. The
   project's stated primary deliverable cannot yet ship.
3. **Open TODO items not done:**
   - Image-path rewrite helpers in the markdown normalizer.
   - Archive-style Markdown tray UX in the stitcher tab.
   - PDF integration tests with safe fixtures.
   - App icons.
4. **No GUI smoke test** under `QT_QPA_PLATFORM=offscreen` — easy to add and
   would catch widget-construction regressions.
5. **No diagnostics dialog** (`app/ui/run_summary_dialog.py` is referenced
   in the progress doc but does not exist in the tree).
6. **`app/core/job_controller.py`** referenced in Phase 9 docs — not present.

## Recommended next 3 actions (matches TODO.md "Immediate next three tasks")

1. **Drop 1-2 small real fixtures per format** into `tests/fixtures/` (no
   private content; synthetic Lorem-ipsum `.docx` etc.) and run real
   conversions through the service end-to-end on this Windows 11 machine
   with Pandoc + LibreOffice installed.
2. **Write a PyInstaller spec** + run `build_windows.ps1` and ship a
   portable folder build. Verify on a clean VM.
3. **Add the archive-style stitch tray** UX so the Stitcher tab feels
   finished, then add a GUI smoke test gated on `QT_QPA_PLATFORM=offscreen`.

---

## Phase coverage map (from CODING_PIPELINE_CODING_PROGRESS.md, verified)

| Phase | Doc claims | Verified |
|---|---|---|
| 0 Foundation | Completed | ✅ |
| 1 Models/settings | Completed | ✅ |
| 2 File detection | In progress | ✅ done in practice |
| 3 Stitcher | Completed | ✅ |
| 4 Pandoc engine | In progress | ✅ code complete, runtime unverified |
| 5 Mammoth engine | Completed | ✅ |
| 6 LibreOffice engine | In progress | ✅ code complete + process-tree kill |
| 7 PDF engines | In progress | ⚠️ code complete, no fixture coverage |
| 8 GUI shell | In progress | ✅ imports clean, no icons |
| 9 Workers | In progress | ✅ cancel+retry wired |
| 10 Reports | In progress | ✅ JSON+MD reports with engine metadata |
| 11 Windows packaging | Not started | ❌ stub only |
| 12 Linux beta | Not started | ❌ stub only |
| 13 macOS | Future | — |

---

## Verdict

This is a **solid B+ build**. The architecture, safety rails, and stitcher
contract are production-quality. The conversion code is in place but not
runtime-proven on real documents, and the Windows 11 packaging path — the
project's primary deliverable — is unfinished. Codex earned **78/100** for
Build 5.3.
