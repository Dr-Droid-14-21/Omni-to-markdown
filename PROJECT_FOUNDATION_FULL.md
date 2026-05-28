# DOCUMENT-TO-MARKDOWN CONVERTER + MD STITCHER PROJECT FOUNDATION

Generated: 2026-05-20 23:29 GMT+2


---

# 1. PRODUCT REQUIREMENTS DOCUMENT (PRD)

## Product title

Working title: **Document-to-Markdown Converter + MD Stitcher GUI**

Final brand name: to be selected after trademark clearance.

## Product vision

Build a fast, local-first desktop application that turns everyday document formats into clean Markdown and lets users merge Markdown files into one ordered, traceable master document. The product should feel like a document workbench: drop files in, preview the conversion plan, run safely, inspect output, and stitch final Markdown files together without command-line friction.

The north star is simple: **make document conversion and Markdown assembly boringly reliable**. The app is not trying to become Microsoft Word, Adobe Acrobat, Notion, Obsidian, or Pandoc with every flag exposed. It is a practical GUI layer over battle-tested conversion engines, with careful error handling, sensible defaults, and a file queue that behaves like a folder, archive, or batch export tray.

## Problem statement

Users who work with AI systems, documentation, legal files, research notes, product specs, books, archived Word documents, and LLM knowledge bases often need Markdown. The current workflow is scattered:

- `.doc`, `.docx`, `.pdf`, `.odt`, and `.odf` files require different tools.
- PDF conversion can collapse layout, lose headings, scramble tables, or silently produce nonsense.
- Old `.doc` files often need LibreOffice or Microsoft Word compatibility layers.
- Pandoc is powerful but intimidating for non-CLI users.
- Markdown stitching is usually manual copy/paste, which creates boundary confusion and version errors.
- When many files are joined, the user needs clear separators showing exactly where each source file begins or ends.

This app solves that by offering one conversion queue, one output location, one error model, and one dedicated MD Stitcher interface.

## Target users

### Primary users

**AI builders and prompt engineers**  
They convert source documents into Markdown for RAG pipelines, agent memory, coding-agent context, training notes, and long-term archives.

**Technical writers and documentation teams**  
They migrate Word/ODT documents into Markdown repositories, static-site docs, GitHub READMEs, and internal knowledge bases.

**Researchers, students, and analysts**  
They batch-convert papers, reports, and notes into Markdown for summarization, annotation, and searchable archives.

**Legal, compliance, and administrative teams**  
They convert correspondence, contracts, meeting notes, policies, and scanned records into a consistent text-first format.

**Founders and operators**  
They stitch fragmented Markdown plans, notes, SOPs, and product documents into one execution file for AI-assisted work.

### Secondary users

- Developers who want a GUI wrapper around Pandoc and related engines.
- Editors compiling book chapters or long-form writing from multiple Markdown pieces.
- Archivists migrating legacy `.doc` and OpenDocument files.

## Core product principles

1. **Local-first and private by default.** Files should be processed locally unless the user explicitly enables a cloud or AI add-on in a later version.
2. **Predictable beats magical.** The app must show what it will do before it does it.
3. **Never silently destroy structure.** If tables, images, footnotes, or metadata cannot be preserved, the app should warn clearly.
4. **Conversion should be inspectable.** Every output should have a small conversion report.
5. **Stitching must be reversible enough to audit.** Separator headers must preserve file boundaries.
6. **Batch workflows must be calm.** Large jobs need progress, cancel, retry, and partial success states.

## Core feature set

## A. Converter

### Supported input formats for V1

The GUI app converts these source formats into `.md`:

- `.doc`
- `.docx`, including Word 2007/2010-era files
- `.pdf`
- `.odt`
- `.odf`

### Output format

- `.md`, UTF-8 encoded.
- Default flavor: GitHub-flavored Markdown compatible where possible.
- Optional future profiles: Pandoc Markdown, CommonMark, Obsidian-friendly Markdown, RAG-clean Markdown.

### Conversion modes

**Single-file conversion**  
User selects one file and converts it into one Markdown file.

**Batch conversion**  
User selects multiple files or a folder and receives one Markdown file per source document.

**Folder import**  
User selects a folder and optionally includes subfolders. The app detects supported formats and builds a queue.

**Preview-only scan**  
The app analyzes file types, likely conversion engine, output path, and warnings before conversion.

**Conversion report**  
For each converted file, the app creates or displays:

- Input filename
- Input path
- Detected type
- Conversion engine used
- Output path
- Duration
- Warning count
- Error count
- Notes on dropped or approximated structures

### Recommended engine routing

| Source format | Primary route | Fallback route | Notes |
|---|---|---|---|
| `.docx` | Pandoc or Mammoth pipeline | LibreOffice to HTML then Markdown | Mammoth is useful for clean semantic output. Pandoc is useful for broad document structure. |
| `.doc` | LibreOffice headless to `.docx` or HTML, then Markdown | Antiword/catdoc optional legacy fallback | `.doc` is the nastiest old cupboard door. Treat as compatibility-first. |
| `.odt` | Pandoc to Markdown | LibreOffice to HTML then Markdown | Good candidate for reliable structure extraction. |
| `.odf` | LibreOffice headless conversion where possible | Text extraction fallback | `.odf` is ambiguous in practice, often OpenDocument Formula. Support should be explicit and guarded. |
| `.pdf` | PyMuPDF or pdfminer extraction, then Markdown normalization | Optional MarkItDown/PyMuPDF4LLM evaluation | PDF is a final-page format, not a semantic document source. Warn users accordingly. |

### Converter acceptance behavior

A converted Markdown file must:

- Preserve headings where the source exposes them.
- Preserve paragraphs and lists.
- Preserve links where possible.
- Preserve tables as Markdown tables where reasonable.
- Insert image references if image extraction is enabled.
- Preserve footnotes or endnotes when the engine supports them.
- Use stable output filenames.
- Avoid absolute local paths in generated Markdown unless explicitly requested.
- Include front matter only if enabled.

## B. MD Stitcher

### Purpose

The MD Stitcher combines multiple `.md` files into one Markdown file. It exists because large AI, documentation, and archive workflows often need a single long context file, while still preserving source boundaries.

### Required separator behavior

Between each file, the app automatically inserts a separator header using this exact visible format pattern:

```text
===========================PREVIOUS FILE NAME.md=================================
```

In implementation, `PREVIOUS FILE NAME.md` is replaced with the actual previous Markdown file name, including `.md`, without directory paths.

Example input order:

1. `intro.md`
2. `chapter-01.md`
3. `chapter-02.md`

Expected stitched output pattern:

```markdown
<contents of intro.md>

===========================intro.md=================================

<contents of chapter-01.md>

===========================chapter-01.md=================================

<contents of chapter-02.md>
```

No trailing separator is required after the final file unless the user enables “Add closing separator.”

### Stitcher interface model

The MD Stitcher should feel like adding files to a folder, zip archive, or playlist:

- Drag Markdown files into the Stitcher tray.
- Use `Add Files` from menu.
- Use `Add Folder` to import all Markdown files from a folder.
- Reorder using drag handles.
- Remove selected files.
- Clear all.
- Show duplicate filenames clearly.
- Show file size and modified date.
- Preview output order.
- Choose output filename and folder.
- Run stitch.
- Open output folder or open stitched Markdown after completion.

### Stitcher validation rules

- Only `.md` and `.markdown` accepted in V1.
- Missing files are marked red and cannot be stitched until removed or relinked.
- Duplicate file names are allowed but warned because separator names may repeat.
- The app must not mutate source files.
- Encoding should default to UTF-8, with detection and repair prompts where needed.
- If a file lacks a trailing newline, the stitcher inserts safe newline spacing before the separator.

### Stitcher output options

V1:

- Output filename.
- Output folder.
- Use exact separator format.
- Normalize line endings to LF.
- Preserve original file content.
- Add optional generated table of contents: off by default.

Future:

- Add YAML front matter.
- Add per-file metadata block.
- Add source path comments.
- Export stitch manifest JSON.
- Split existing stitched file back into parts.

## Functional requirements

### Conversion queue

The app must provide a queue table with:

- File name
- Source format
- Status
- Engine route
- Output filename
- Warnings
- Action buttons: preview, retry, remove

Statuses:

- Pending
- Scanning
- Ready
- Converting
- Converted
- Converted with warnings
- Failed
- Cancelled
- Skipped

### File detection

The app must validate file type by extension and magic/header where possible. A `.docx` is a ZIP-based Office document, while old `.doc` is binary. A mislabeled file should produce a warning instead of a crash.

### Output naming

Default output naming:

- `Input File.docx` → `Input File.md`
- `Input File.pdf` → `Input File.md`
- If conflict exists: `Input File (1).md`, `Input File (2).md`

Optional batch behavior:

- Mirror folder structure.
- Flatten into one output folder.
- Create one folder per batch run.

### Progress reporting

The app must show:

- Current file
- Per-file progress where possible
- Total queue progress
- Estimated remaining work only when reliable enough
- Cancel button
- Post-run summary

### Logs and reports

Every batch run should produce a run report in memory and optionally on disk:

- `conversion-report.json`
- `conversion-report.md`

Logs should avoid exposing full file contents.

### Settings

V1 settings:

- Default output directory
- Markdown flavor
- PDF extraction mode: plain text, layout-aware, Markdown-oriented
- Image extraction: off/on
- Table handling: simple, preserve raw HTML, fallback to text
- Engine preference for `.docx`: Pandoc-first or Mammoth-first
- External binary paths: Pandoc, LibreOffice
- Max file size warning threshold
- Concurrency limit

## Non-functional requirements

### Reliability

- A failure in one file must not stop the entire batch unless the user selects fail-fast mode.
- Temporary files must be cleaned after success or failure.
- Partial outputs should be marked `.partial.md` until complete.
- App must survive conversion subprocess crashes.
- The app must preserve source files untouched.

### Performance

Target performance for V1 on a modern Windows 11 laptop:

- App launch under 3 seconds after warm start.
- Queue scan of 100 local files under 10 seconds excluding deep file inspection.
- Typical `.docx` conversion under 5 seconds for ordinary documents.
- PDF conversion speed varies widely; show honest progress.

### Security

- Do not execute document macros.
- Run external converters with timeouts.
- Use isolated temporary directories.
- Sanitize output filenames.
- Avoid shell=True for subprocess calls.
- Do not follow symlinks without user consent in folder import.
- Never send files to network services by default.
- Treat malformed documents as untrusted input.
- Avoid embedding absolute source paths unless explicitly enabled.

### Privacy

- No telemetry in V1 unless explicitly opt-in.
- No cloud upload in V1.
- No AI model calls in V1.
- Logs must not include document text by default.

### Accessibility

- Keyboard navigation for all primary actions.
- Screen-reader labels for file queue and buttons.
- High-contrast mode.
- Clear progress labels, not only color.
- Scalable text.

### Internationalization

V1 language: English.  
Design should allow future translations by keeping UI strings centralized.

### Maintainability

- Clear separation between GUI, services, engines, domain models, and tests.
- Conversion engines should be plug-ins behind a stable interface.
- All workflows should be testable from CLI/service layer without launching GUI.
- All critical changes must update `ALL-FILES-CHANGELOG.md`.

## UI/UX requirements

## Main window layout

### Primary navigation

Two main tabs:

1. **Converter**
2. **MD Stitcher**

Optional third tab in later versions:

3. **Run History**

### Converter tab

Top area:

- Add Files
- Add Folder
- Remove
- Clear
- Output Folder
- Convert
- Settings

Middle:

- Queue table

Right side or bottom:

- File details and warnings panel

Bottom:

- Progress bar
- Status text
- Open Output Folder
- Export Report

### MD Stitcher tab

Top area:

- Add Markdown Files
- Add Folder
- Remove
- Clear
- Move Up
- Move Down
- Output File
- Stitch

Middle:

- Archive-style list with file cards or table rows
- Drag handles
- File order numbers

Side panel:

- Separator preview
- Output preview summary
- Duplicate filename warning
- Encoding warnings

Bottom:

- Progress
- Open stitched output

### Interaction tone

The application should feel like a quiet workshop, not a cockpit. Prefer clear labels over clever labels. Warnings should be plain-language and actionable.

Example warning:

> This PDF appears to contain scanned pages. Text extraction may produce little or no Markdown. OCR is not enabled in this version.

## File handling edge cases

### Document edge cases

- Password-protected Word files.
- Password-protected PDFs.
- Corrupt `.docx` ZIP containers.
- Old `.doc` files with unusual encodings.
- Documents with macros.
- Documents with embedded objects.
- Track changes and comments.
- Footnotes, endnotes, citations.
- Complex nested tables.
- Text boxes and floating shapes.
- Headers and footers.
- Page numbers.
- Equations and formulas.
- Right-to-left languages.
- CJK and vertical text.
- Very large documents.
- Duplicate filenames from different folders.
- Filename characters illegal on target OS.
- Cloud-synced placeholder files not downloaded locally.
- Symlinks, junctions, aliases.
- Network-drive latency and disconnections.
- Read-only output directories.
- Antivirus locking temporary outputs.

### PDF-specific edge cases

- Scanned/image-only PDFs.
- Multi-column academic papers.
- Tables spanning pages.
- Rotated pages.
- Mixed orientations.
- Embedded fonts with broken maps.
- OCR layers that disagree with visible text.
- Redacted PDFs.
- Forms and annotations.
- Digital signatures.
- Huge image-heavy PDFs.
- PDFs with no extractable text.

### Stitching edge cases

- Markdown file missing final newline.
- Different encodings across files.
- Duplicate file names.
- Empty files.
- Files over size limit.
- Markdown containing similar separator strings.
- Files moved after being added to queue.
- User reorders while stitch is running.
- Output file accidentally included in input list.
- Output path same as one of the source files.
- Read-only source or destination.
- User cancels during write.

## Error states

### Recoverable errors

- Unsupported file selected.
- External binary missing.
- Output directory unavailable.
- File locked by another process.
- Password required.
- Conversion warning with partial output.
- PDF text extraction produced empty output.

### Fatal per-file errors

- Corrupt file.
- Permission denied.
- Engine crash.
- Timeout.
- Unsupported encryption.
- Disk full during write.

### Fatal app errors

- Settings database unreadable and cannot be recreated.
- Temporary directory cannot be created.
- Required GUI resources missing.
- System lacks minimum OS support.

### Error UX

Each error must show:

- Human-readable message.
- Technical detail disclosure.
- Suggested fix.
- Retry action when possible.
- Copy diagnostic info action.

## Scope boundaries

## Explicitly in scope for V1

- Local desktop GUI.
- Convert `.doc`, `.docx`, `.pdf`, `.odt`, `.odf` to `.md`.
- Batch file queue.
- MD Stitcher with exact separator format.
- Basic settings.
- Conversion reports.
- Windows 11 first implementation.
- Linux compatibility target.
- macOS future target.

## Explicitly out of scope for V1

- Full WYSIWYG editing.
- Perfect PDF layout reconstruction.
- OCR as a default feature.
- Cloud processing.
- Built-in LLM summarization.
- RAG database ingestion.
- Collaborative editing.
- Mobile apps.
- Browser extension.
- Real-time watch folder automation.
- Round-trip Markdown back to Word with perfect fidelity.
- Macro execution.
- Direct editing of source documents.
- Legal-grade certified conversion guarantees.

## Success metrics

### Product metrics

- 90% of ordinary `.docx` and `.odt` documents convert without fatal error.
- 80% of text-based PDFs produce usable Markdown or a clear warning.
- 100% of batch failures are isolated per file.
- 100% of stitched outputs preserve requested file order.
- 100% of separators use the exact required format pattern.

### UX metrics

- First-time user can convert a document in under 60 seconds.
- First-time user can stitch three Markdown files in under 90 seconds.
- Error messages are understandable without developer knowledge.
- No source file is modified during normal operation.

## Release strategy

### V0.1 technical prototype

- CLI service layer only.
- Convert `.docx`, `.odt`, `.pdf`.
- Stitch Markdown files from a manifest.

### V0.2 Windows GUI MVP

- PySide6 GUI.
- File queue.
- External binary detection.
- Basic conversion.
- Stitcher tray.

### V0.3 Windows alpha

- Reports.
- Settings.
- Better errors.
- Packaging.

### V0.4 Linux beta

- Linux packaging.
- Dependency detection.
- File manager integration polish.

### V1.0 Windows + Linux release candidate

- Regression test corpus.
- Installer.
- Documentation.
- Basic update process.

### V1.1 macOS collaborative planning

- Q4 2026 to Q1 2027 target window.
- macOS signing and notarization path.
- Apple Silicon and Intel compatibility verification.


---

# 2. APP NAME CANDIDATES

Trademark status note: these are product-naming candidates, not legal trademark clearance. A proper launch requires checking USPTO, EUIPO, WIPO Global Brand Database, domain availability, app stores, GitHub, PyPI/npm/crates, and common-law usage. I checked for obvious major-product collisions and flag uncertainty where a visible collision or near-collision exists.

| # | Name | Tagline | Availability signal | Psychological breakdown |
|---:|---|---|---|---|
| 1 | **MarqFold** | “Fold documents into clean Markdown.” | No obvious major product found in quick search. Trademark uncertain. | Short, angular, and modern. “Marq” cues Markdown without looking too geeky, while “Fold” implies compression, organization, and document transformation. Good for a tool that converts and bundles. |
| 2 | **SlateMark** | “From document clutter to Markdown clarity.” | No obvious major software product found; minor unrelated name traces exist. Trademark uncertain. | “Slate” feels clean, writable, and calm. It positions the app as a blank, reliable surface for structured text. The name sounds professional enough for teams and memorable enough for solo creators. |
| 3 | **MarkLoom** | “Weave documents into Markdown.” | A Markloom IT/digital-marketing presence appears online; not a major document product. Trademark uncertain. | “Loom” suggests weaving many threads into one fabric, which fits both conversion and stitching. It has a warm craft feeling without losing technical credibility. |
| 4 | **MarkBinder** | “Bind every Markdown file into one source.” | Mostly unrelated personal/name references found. Trademark uncertain. | “Binder” is instantly understood: files go in, ordered output comes out. It has office-tool familiarity and is especially strong for the MD Stitcher part. |
| 5 | **BinderMD** | “A Markdown binder for serious document work.” | No obvious major app collision found in quick search. Trademark uncertain. | “MD” directly marks the Markdown audience. “Binder” gives users a mental model: collect, order, preserve. It is easy to spell and sounds utilitarian in a good way. |
| 6 | **ThreadMD** | “Thread your Markdown into one clean file.” | No obvious major document app found; scattered unrelated traces. Trademark uncertain. | “Thread” communicates sequence, continuity, and linked fragments. It works well for long-form files and AI context bundles. Slightly softer than “Binder,” more creative. |
| 7 | **PageSplice** | “Convert, combine, and keep the seams visible.” | Needs deeper search before launch. Trademark uncertain. | “Splice” is active and technical. It signals joining while preserving the idea of visible cuts, which matches separator headers. Good for power users, slightly less gentle for mainstream users. |
| 8 | **DocSplice** | “Documents in, stitched Markdown out.” | A small PyPI package named `docsplice` appears to exist, unrelated purpose. Use caution. | Very descriptive and easy to understand. The risk is that it leans more mechanical than premium, and the existing package means brand/legal diligence is necessary. |
| 9 | **FoldMark** | “The document converter that folds chaos into Markdown.” | Existing research/project usage around protein watermarking appears online. Use caution. | Compact and elegant. “Fold” has a satisfying transformation meaning, but the existing scientific usage makes it less clean as a brand. Strong fallback, not my first pick. |
| 10 | **VaultMark** | “Securely convert and archive Markdown-ready documents.” | A digital agency named Vault Mark appears online. Use caution. | “Vault” suggests safety, privacy, and archival seriousness. Excellent for legal/compliance positioning, but the agency collision means it should be checked carefully before adoption. |

## Recommended shortlist

1. **SlateMark** — best balance of professional, memorable, and clean.
2. **MarqFold** — most distinctive and conversion-oriented.
3. **BinderMD** — clearest for Markdown stitching and AI-context bundling.
4. **MarkLoom** — best metaphor for weaving many files into one.

## Naming decision rule

Choose **SlateMark** if the app should feel polished, Swiss-clean, and broad.  
Choose **BinderMD** if the app should feel like a direct utility for Markdown power users.  
Choose **MarqFold** if the brand should feel more startup-like and ownable.


---

# 3. CROSS-PLATFORM DIFFICULTY ASSESSMENT

## Unified macOS + Linux + Windows 11 codebase difficulty

**Rating: 8.0 / 10**

A unified codebase is realistic, but the project carries hidden complexity because the product is not just a GUI. It is a desktop shell around multiple document engines with different installation, licensing, path, crash, and formatting behavior.

### Why it is difficult

**1. Dependency complexity is the main dragon.**  
Pandoc, LibreOffice, PDF extractors, optional OCR, and GUI runtime packaging all behave differently per OS. Bundling everything creates large installers and licensing/upgrade concerns. Relying on system installs creates support burden.

**2. `.doc` support is old-format archaeology.**  
Modern `.docx` is easier because it is ZIP/XML-based. Old binary `.doc` files need LibreOffice or specialist legacy extractors. Some old documents open differently across LibreOffice versions.

**3. PDF parsing is probabilistic, not deterministic.**  
PDFs are page-description files. They often lack semantic headings, logical reading order, or table structure. A good app must set expectations and expose warnings.

**4. GUI toolkit choice is manageable but consequential.**  
PySide6 is strong for native desktop feel and Python integration. Tauri is elegant and smaller but adds Rust/frontend complexity. Electron is mature but heavy. For this project, Python + PySide6 wins because conversion libraries and subprocess orchestration are naturally Python-friendly.

**5. Packaging is three separate jobs wearing one coat.**  
Windows wants `.exe`/MSI/MSIX and signing. Linux wants AppImage/deb/rpm/Flatpak decisions. macOS wants `.app`/`.dmg`, hardened runtime, signing, notarization, and Apple Silicon/Intel verification.

**6. Testing requires a document corpus.**  
Unit tests are not enough. The app needs real files: simple Word, complex Word, old `.doc`, ODT, formula-ish ODF, clean PDFs, scanned PDFs, multi-column PDFs, password-protected files, corrupt files, RTL/CJK examples, and huge files.

## Recommended unified approach

- Core language: Python 3.12 or 3.13.
- GUI: PySide6.
- Internal service architecture independent of GUI.
- Engines wrapped behind a `ConversionEngine` interface.
- External tools detected at runtime.
- Windows-first packaging, Linux second, macOS later.
- CI matrix for unit tests across OSes.
- Manual golden-file conversion QA before release.

## Windows 11 only difficulty

**Rating: 5.8 / 10**

Windows-only is much easier because you can freeze the environment, document known installation paths, and build around the most common target first.

### Specific rationale

- PySide6 works well on Windows.
- PyInstaller or pyside6-deploy can package the GUI.
- LibreOffice path detection can check common install directories.
- Pandoc installer availability is straightforward.
- Windows users expect installer prompts for dependencies.
- File locking and antivirus interference must be handled carefully.
- Old `.doc` compatibility is still hard, but at least the OS matrix is gone.

### Primary Windows risks

- Unsigned executables triggering SmartScreen.
- Antivirus quarantining bundled converters or temp-file behavior.
- Spaces and Unicode in paths.
- OneDrive placeholder files.
- Long path issues if Windows long-path support is disabled.
- LibreOffice headless failures when profile directory is locked.

## Linux only difficulty

**Rating: 6.6 / 10**

Linux has excellent command-line tooling, but distribution fragmentation increases support complexity.

### Specific rationale

- Pandoc and LibreOffice are often available through package managers.
- PySide6 works, but Wayland/X11 behavior can differ.
- AppImage/Flatpak/deb/rpm decisions matter.
- External binary availability is easier for technical users but harder for mainstream users.
- Sandbox packaging like Flatpak complicates file access and external converter calls.
- Font availability affects document conversion results.

### Primary Linux risks

- Different distro package versions.
- Missing system libraries for Qt.
- Sandboxed app permissions.
- Headless LibreOffice profile issues.
- AppImage compatibility across older distributions.
- Wayland drag/drop quirks.

## macOS future collaborative effort, Q4 2026 to Q1 2027

**Rating: 7.4 / 10**

macOS is very achievable but should be treated as a focused future track rather than casually promised in the first release.

### Framing

Target macOS as a collaborative Q4 2026 to Q1 2027 effort with a developer who can test on Apple Silicon and handle signing/notarization. The goal is not just “it runs on my Mac”; the goal is trusted distribution.

### Specific rationale

- PySide6 supports macOS, but packaging must be tested carefully.
- macOS app distribution requires signing and notarization for smooth user trust.
- Apple Silicon and Intel builds need deliberate handling.
- Bundling Pandoc/LibreOffice may be too large; detecting installed dependencies may be cleaner.
- Gatekeeper behavior can create user friction for unsigned apps.
- File permissions, sandboxing, and drag/drop need native testing.

### Primary macOS risks

- Code signing and notarization setup.
- Apple Developer Program requirement.
- Homebrew vs bundled dependencies decision.
- Apple Silicon/Intel binary differences.
- `.app` bundle resource paths.
- GUI polish expectations are higher on macOS.

## Bottom-line technical verdict

Build the first serious implementation for **Windows 11**, keep the service layer cross-platform from day one, validate on Linux during development, and plan macOS as a polished future release rather than a rushed checkbox. That avoids the classic cross-platform trap: building three unfinished apps instead of one dependable one.


---

# 4. PROJECT DOCUMENTATION FILES

The following sections contain the requested project documentation files in full, each opening with its filename as a top-level heading.

---

# SPECS_TECHSTACK.md

## Purpose

This document defines the recommended technical stack for a local-first desktop GUI application that converts `.doc`, `.docx`, `.pdf`, `.odt`, and `.odf` files to Markdown and stitches multiple Markdown files into one ordered output file.

## Product architecture stance

The product should be built as a modular desktop application, not as a monolithic GUI script. The GUI is only the surface. The core conversion, stitching, reporting, logging, and validation logic must run independently so it can be tested through CLI or service-level tests.

## Recommended stack summary

| Layer | Recommendation | Reason |
|---|---|---|
| Language | Python 3.12 or 3.13 | Best fit for document tooling, subprocess orchestration, PySide6 GUI, and fast development. |
| GUI | PySide6 / Qt for Python | Mature desktop widgets, drag/drop, native menus, accessibility potential, cross-platform path. |
| Packaging | PyInstaller first, pyside6-deploy evaluation second | PyInstaller is widely used; pyside6-deploy is Qt-aligned and should be evaluated. |
| DOCX conversion | Pandoc and Mammoth | Pandoc for broad structure; Mammoth for clean semantic HTML from `.docx`. |
| DOC conversion | LibreOffice headless pre-conversion | Old binary `.doc` needs compatibility conversion before Markdown normalization. |
| ODT conversion | Pandoc primary, LibreOffice fallback | ODT is Pandoc-friendly, LibreOffice is good fallback. |
| ODF conversion | LibreOffice guarded route | `.odf` is ambiguous; support must be explicitly validated. |
| PDF extraction | PyMuPDF + pdfminer.six | PyMuPDF for performance and extraction options; pdfminer.six for text analysis fallback. |
| Markdown normalization | custom service + markdownify/html2text where needed | Allows consistent heading, newline, table, and separator behavior. |
| Settings | platformdirs + JSON/TOML | Simple local config without database overhead. |
| Logging | Python logging or structlog/loguru | Structured logs without document body leakage. |
| Models | pydantic or dataclasses | Strong validation for queue items, reports, and settings. |
| Tests | pytest | Standard Python testing. |
| Lint/type | ruff + mypy/pyright | Fast code quality loop. |
| CI | GitHub Actions matrix | Windows-first, Linux, future macOS. |

## Runtime requirements

### Windows 11

Minimum:

- Windows 11 64-bit.
- 8 GB RAM.
- 500 MB app disk space without bundled LibreOffice/Pandoc.
- 2 GB+ if heavy external tools are bundled.
- Python not required for packaged release.
- Optional installed tools: LibreOffice, Pandoc.

Recommended:

- Windows 11 23H2 or newer.
- 16 GB RAM.
- SSD/NVMe.
- LibreOffice current stable.
- Pandoc current stable.

### Linux

Minimum:

- Modern 64-bit Linux distribution.
- glibc-compatible environment for packaged builds.
- Qt runtime compatibility depending on package format.
- LibreOffice and Pandoc available through system package manager or bundled path.

Recommended:

- Ubuntu LTS, Fedora, Debian stable, Arch, or Linux Mint.
- 8 GB RAM minimum, 16 GB preferred.
- Native package build plus AppImage/Flatpak evaluation.

### macOS

Future target:

- macOS current and one previous major release at the time of Q4 2026/Q1 2027 work.
- Apple Silicon required for test.
- Intel optional but preferred if support commitment exists.
- Apple Developer account for signing and notarization.
- DMG distribution.

## External tools

## Pandoc

Role:

- Convert `.docx`, `.odt`, and intermediate HTML into Markdown.
- Generate Markdown with stable structural rules.
- Preserve headings, lists, tables, links, footnotes, and metadata where supported.

Usage strategy:

- Detect `pandoc` binary at startup and from settings.
- Validate with `pandoc --version`.
- Prefer subprocess invocation over binding until stable.
- Use explicit `--from` and `--to` formats.
- Use `--wrap=none` where appropriate.
- Use temporary working directories.
- Capture stderr and exit codes.

Potential command patterns:

```bash
pandoc input.docx --from=docx --to=gfm --wrap=none --output=output.md
pandoc input.odt --from=odt --to=gfm --wrap=none --output=output.md
pandoc input.html --from=html --to=gfm --wrap=none --output=output.md
```

Risks:

- Complex tables may degrade.
- Exact styling is not preserved.
- Some embedded objects will be skipped.
- Requires installation or bundled binary.

## LibreOffice headless

Role:

- Pre-convert `.doc` and problematic ODT/ODF documents.
- Export to `.docx`, `.html`, `.txt`, or another intermediate.
- Provide legacy Office compatibility.

Usage strategy:

- Detect `soffice` or `libreoffice`.
- Use isolated user profile per run where possible.
- Always set timeout.
- Avoid macro execution.
- Run with a controlled temporary output directory.
- Do not run with shell interpolation.

Potential command patterns:

```bash
soffice --headless --convert-to docx --outdir /tmp/out input.doc
soffice --headless --convert-to html --outdir /tmp/out input.doc
soffice --headless --convert-to txt --outdir /tmp/out input.odf
```

Risks:

- Headless conversion can hang.
- Output filenames are controlled by LibreOffice.
- Filter behavior can vary by LibreOffice version.
- Requires write access to user profile.
- Bundling LibreOffice is heavy.

## Mammoth

Role:

- Convert `.docx` to clean semantic HTML.
- Useful when the goal is readable Markdown over layout fidelity.

Pipeline:

```text
docx -> Mammoth HTML -> Markdown normalizer -> .md
```

Strength:

- Clean semantic structure.
- Good for ordinary Word docs.
- Style-map customization.

Limitations:

- Not for old `.doc`.
- Not designed for exact visual reproduction.
- Complex layout and embedded objects may be ignored or simplified.

## PyMuPDF

Role:

- Extract text and layout information from PDF.
- Potentially generate Markdown-oriented output with custom logic.
- Detect image-heavy/scanned PDFs.

Strength:

- Fast.
- Useful for page-level extraction.
- Can inspect images and blocks.

Limitations:

- PDF logical structure may not exist.
- Tables and reading order need heuristics.
- OCR not included as default V1 feature.

## pdfminer.six

Role:

- Text extraction fallback.
- Useful for deeper text layout analysis.
- Handles many PDF internals.

Strength:

- Pure Python.
- Good text extraction tool.
- Supports encrypted PDFs where permitted and many font cases.

Limitations:

- Slower than PyMuPDF in many scenarios.
- Output may still be layout-scrambled.
- Not a semantic Markdown converter.

## Optional evaluation: Microsoft MarkItDown

Role:

- Optional plugin route for converting multiple formats to Markdown for LLM workflows.
- Useful benchmark against custom pipelines.

Caution:

- Use only as optional route until output quality and security posture are validated.
- Sanitize paths and permissions.
- Do not treat as magic perfect converter.

## Markdown normalization rules

The app must normalize output after any conversion engine.

Rules:

- Use UTF-8 output.
- Normalize line endings to LF.
- Trim excessive trailing whitespace.
- Preserve code blocks.
- Avoid rewriting content inside fenced code blocks.
- Ensure document ends with one newline.
- Convert image paths to relative paths if images are extracted.
- Avoid absolute input file paths in Markdown.
- Use safe filename slugs only when creating derived assets.
- Preserve Markdown headings generated by engine.
- Do not invent headings that are not detectable.

## MD Stitcher technical specification

Input:

- Ordered list of Markdown file paths.
- Output file path.
- Separator configuration locked to required format in V1.
- Optional line-ending normalization.

Separator constants:

```python
SEPARATOR_PREFIX = "==========================="
SEPARATOR_SUFFIX = "================================="
```

Separator function:

```text
separator(previous_file_name) = SEPARATOR_PREFIX + previous_file_name + SEPARATOR_SUFFIX
```

Implementation rules:

- Use basename only, not full path.
- Preserve `.md` extension in separator display.
- If input file is `.markdown`, display original basename including `.markdown` unless user chooses normalize-to-md display.
- Insert separator between files only.
- Default: no separator before first file and no separator after final file.
- Ensure blank line before and after separator.
- Do not mutate source files.
- Write to temporary file first, then atomic rename if possible.

## Python package dependencies

Recommended `pyproject.toml` groups:

### Core

- `PySide6`
- `pydantic`
- `platformdirs`
- `charset-normalizer`
- `python-magic` or platform-specific filetype alternative
- `markdownify`
- `beautifulsoup4`
- `pypandoc`
- `mammoth`
- `pymupdf`
- `pdfminer.six`
- `loguru` or `structlog`

### Development

- `pytest`
- `pytest-qt`
- `ruff`
- `mypy` or `pyright`
- `coverage`
- `pre-commit`

### Packaging

- `pyinstaller`
- optional: `nuitka`
- optional: `briefcase`
- optional: `cx_Freeze`

## Proposed repository structure

```text
doc-to-md-stitcher/
  app/
    __init__.py
    main.py
    ui/
      main_window.py
      converter_tab.py
      stitcher_tab.py
      settings_dialog.py
      widgets/
        file_queue_table.py
        drag_drop_list.py
        warning_panel.py
    core/
      models.py
      settings.py
      paths.py
      logging_config.py
      file_detection.py
      temp_manager.py
    conversion/
      base.py
      router.py
      pandoc_engine.py
      libreoffice_engine.py
      mammoth_engine.py
      pdf_pymupdf_engine.py
      pdf_pdfminer_engine.py
      markdown_normalizer.py
      reports.py
    stitcher/
      stitcher_service.py
      separator.py
      manifest.py
    workers/
      conversion_worker.py
      stitch_worker.py
    resources/
      icons/
      styles/
  tests/
    unit/
    integration/
    fixtures/
  docs/
    SPECS_TECHSTACK.md
    WORKFLOWS_ARCHITECTURE.md
    CODING_PIPELINE_CODING_PROGRESS.md
    Agent.md
    GEMINI.md
    PLAN.md
    TODO.md
    ALL-FILES-CHANGELOG.md
  scripts/
    detect_dependencies.py
    build_windows.ps1
    build_linux.sh
    run_tests.ps1
    run_tests.sh
  pyproject.toml
  README.md
  LICENSE
```

## Conversion engine interface

Each engine should implement:

```python
class ConversionEngine:
    name: str
    supported_extensions: set[str]

    def is_available(self) -> EngineAvailability:
        ...

    def can_convert(self, source: Path, context: ConversionContext) -> bool:
        ...

    def convert(self, source: Path, output: Path, context: ConversionContext) -> ConversionResult:
        ...
```

## Conversion result model

Fields:

- `source_path`
- `output_path`
- `engine_name`
- `status`
- `warnings`
- `errors`
- `duration_ms`
- `intermediate_files`
- `metadata`
- `report_path`

## Security requirements

- Never execute macros.
- Never use `shell=True` for converter calls.
- Sanitize file paths displayed in reports if privacy mode is on.
- Use per-run temp directories.
- Delete temp directories by default.
- Keep debug temp files only if user enables diagnostics.
- Timebox external converters.
- Validate outputs before marking success.
- Treat all input documents as untrusted.

## Version strategy

Application version:

```text
0.1.0 CLI prototype
0.2.0 GUI MVP
0.3.0 Windows alpha
0.4.0 Linux beta
1.0.0 Windows/Linux release candidate
1.1.0 macOS collaboration track
```

## Final recommendation

Use **Python + PySide6 + Pandoc/LibreOffice/Mammoth/PyMuPDF/pdfminer.six**. Avoid Tauri/Electron for V1 unless a web UI is strategically required. The conversion problem is already a hydra; do not give it a second head by adding a complex frontend/backend bridge before the engine layer is stable.


---

# WORKFLOWS_ARCHITECTURE.md

## Purpose

This document describes the system architecture, data flow, MD Stitcher workflow, queue management, and error-handling flow for the Document-to-Markdown Converter + MD Stitcher GUI application.

## Architecture principles

1. GUI must not contain conversion logic.
2. Conversion and stitching must be callable without GUI.
3. All external tools must be wrapped behind engine interfaces.
4. Every job must produce a result object.
5. Errors must be data, not surprise popups only.
6. Source files must never be modified.
7. Temporary outputs must become final outputs only after validation.

## Component diagram

```text
+--------------------------------------------------------------------------------+
|                                   Desktop App                                  |
|                                                                                |
|  +-----------------------------+       +-------------------------------------+ |
|  |           PySide6 UI         |       |          Settings + Profiles        | |
|  |-----------------------------|       |-------------------------------------| |
|  | Main Window                 |<----->| User settings JSON/TOML             | |
|  | Converter Tab               |       | Engine paths                        | |
|  | MD Stitcher Tab             |       | Output preferences                  | |
|  | Settings Dialog             |       | Privacy + diagnostics flags          | |
|  +--------------+--------------+       +------------------+------------------+ |
|                 |                                     |                        |
|                 v                                     v                        |
|  +-----------------------------+       +-------------------------------------+ |
|  |        Job Controller        |<----->|             Logger/Reporter         | |
|  |-----------------------------|       |-------------------------------------| |
|  | Queue state                  |       | Run report                          | |
|  | Worker lifecycle             |       | Per-file report                     | |
|  | Cancel/retry                 |       | User-visible diagnostics             | |
|  +--------------+--------------+       +------------------+------------------+ |
|                 |                                     ^                        |
|                 v                                     |                        |
|  +-----------------------------+       +-------------------------------------+ |
|  |       Conversion Router      |------>|         Conversion Engines          | |
|  |-----------------------------|       |-------------------------------------| |
|  | File type detection          |       | Pandoc Engine                       | |
|  | Engine selection             |       | LibreOffice Engine                  | |
|  | Fallback planning            |       | Mammoth Engine                      | |
|  | Warning generation           |       | PyMuPDF Engine                      | |
|  +--------------+--------------+       | pdfminer.six Engine                 | |
|                 |                      +------------------+------------------+ |
|                 v                                         |                    |
|  +-----------------------------+                          v                    |
|  |     Markdown Normalizer      |<------------------ External Tools           |
|  |-----------------------------|        pandoc / soffice / optional plugins   |
|  | LF line endings              |                                               |
|  | Markdown cleanup             |                                               |
|  | Asset path rewrite           |                                               |
|  +--------------+--------------+                                               |
|                 |                                                              |
|                 v                                                              |
|  +-----------------------------+                                               |
|  |      Output Writer           |                                               |
|  |-----------------------------|                                               |
|  | Temp output                  |                                               |
|  | Validate                     |                                               |
|  | Atomic move                  |                                               |
|  +-----------------------------+                                               |
|                                                                                |
|  +-----------------------------+                                               |
|  |       MD Stitcher Service    |                                               |
|  |-----------------------------|                                               |
|  | Ordered Markdown manifest    |                                               |
|  | Separator insertion          |                                               |
|  | Encoding normalization       |                                               |
|  | Atomic stitched output       |                                               |
|  +-----------------------------+                                               |
+--------------------------------------------------------------------------------+
```

## Primary modules

## UI layer

Responsibilities:

- File selection.
- Drag/drop.
- Queue display.
- User settings.
- Progress display.
- Human-readable errors.
- Dispatch work to controllers.

Non-responsibilities:

- Direct document conversion.
- Parsing Markdown.
- Calling external binaries directly.
- Writing output files directly except via services.

## Job controller

Responsibilities:

- Maintain queue state.
- Create jobs from UI requests.
- Start, pause, cancel, retry jobs.
- Route results back to UI.
- Prevent destructive operations.
- Keep UI responsive via workers/threads.

## Conversion router

Responsibilities:

- Detect input format.
- Select engine route.
- Build fallback plan.
- Validate engine availability.
- Produce preflight warnings.

Example route:

```text
source.doc
  -> LibreOfficeEngine converts to intermediate.docx
  -> PandocEngine converts intermediate.docx to output.md
  -> MarkdownNormalizer cleans output.md
  -> ReportWriter records route
```

## Conversion engines

Each engine is narrow and replaceable.

### Pandoc Engine

- Handles `.docx`, `.odt`, `.html`.
- Invokes Pandoc safely.
- Captures stderr.
- Produces raw Markdown.

### LibreOffice Engine

- Handles `.doc` and fallback conversions.
- Converts legacy formats into safer intermediate formats.
- Uses isolated profiles when possible.
- Applies timeout and crash handling.

### Mammoth Engine

- Handles `.docx` to semantic HTML.
- Good for clean prose.
- Passes HTML to Markdown normalizer.

### PyMuPDF Engine

- Handles PDF extraction.
- Detects image-heavy/scanned pages.
- Produces text/Markdown-like output.

### pdfminer.six Engine

- Fallback for PDF text extraction.
- Can be slower but useful when PyMuPDF output is poor.

## Markdown Normalizer

Responsibilities:

- Normalize line endings.
- Ensure final newline.
- Clean excessive blank lines conservatively.
- Convert HTML fragments to Markdown where required.
- Rewrite asset paths.
- Preserve code blocks.
- Generate warnings for unsupported structures.

## Output Writer

Responsibilities:

- Write to temporary file.
- Validate output exists and has expected encoding.
- Rename/move to final output.
- Prevent overwriting unless user confirms.
- Handle filename conflicts.

## Data flow: conversion pipeline

```text
User adds files
  -> FileDetector scans extension and magic/header
  -> QueueItem created
  -> Router creates ConversionPlan
  -> UI displays engine route and warnings
  -> User clicks Convert
  -> JobController starts worker
  -> Engine converts to temp output
  -> MarkdownNormalizer processes temp output
  -> OutputWriter commits final .md
  -> Reporter records result
  -> UI shows success/warnings/errors
```

## Conversion plan object

Fields:

- `source_path`
- `detected_extension`
- `detected_mime`
- `preferred_engine`
- `fallback_engines`
- `intermediate_format`
- `output_path`
- `warnings`
- `requires_external_tools`
- `estimated_risk_level`

Risk levels:

- Low: normal `.docx`/`.odt`.
- Medium: PDF with extractable text.
- High: old `.doc`, `.odf`, complex PDF.
- Critical: encrypted, corrupt, scanned without OCR.

## MD Stitcher workflow

```text
User opens MD Stitcher tab
  -> User drags .md files into tray or uses menu
  -> Stitcher validates files
  -> UI shows ordered archive-style list
  -> User reorders/removes files
  -> User chooses output path
  -> User clicks Stitch
  -> StitcherService reads files in order
  -> Writes first file content
  -> Inserts separator named after previous file
  -> Writes next file content
  -> Repeats until final file
  -> OutputWriter commits stitched output
  -> UI displays summary
```

## MD Stitcher separator rule

Required exact visible pattern:

```text
===========================PREVIOUS FILE NAME.md=================================
```

Implementation interpretation:

```text
===========================actual_previous_file_name.md=================================
```

The previous file name is the basename only. Directory paths are excluded.

## Stitcher output flow

For input order:

```text
a.md
b.md
c.md
```

The output is:

```text
<content of a.md>

===========================a.md=================================

<content of b.md>

===========================b.md=================================

<content of c.md>
```

## Queue management

## Queue item model

Fields:

- `id`
- `source_path`
- `display_name`
- `detected_type`
- `status`
- `engine_route`
- `output_path`
- `warnings`
- `errors`
- `progress`
- `created_at`
- `updated_at`
- `result`

## Queue operations

- Add files.
- Add folder.
- Remove selected.
- Clear finished.
- Clear all.
- Retry failed.
- Open source location.
- Open output location.
- Export queue report.

## Queue concurrency

Recommended V1:

- Default concurrency: 1.
- Optional concurrency: 2 for documents.
- PDF extraction may run separately if stable.
- LibreOffice conversions should usually run one at a time because headless profile contention can cause unpredictable behavior.

## Error handling flow

```text
Operation starts
  -> Validate inputs
  -> Validate output path
  -> Validate engine availability
  -> Create temp workspace
  -> Run engine with timeout
      -> success: normalize and commit
      -> warning: normalize, commit, mark warning
      -> failure: capture stderr, remove partial, mark failed
      -> timeout: kill process tree, clean temp, mark failed
  -> Write report entry
  -> Update queue status
```

## Error object

Fields:

- `code`
- `severity`
- `title`
- `message`
- `technical_details`
- `suggested_fix`
- `retryable`
- `source_path`
- `engine_name`

Example:

```json
{
  "code": "PDF_NO_TEXT_LAYER",
  "severity": "warning",
  "title": "No extractable text found",
  "message": "This PDF appears to contain scanned pages. Markdown output may be empty.",
  "technical_details": "PyMuPDF extracted 0 text characters across 12 pages.",
  "suggested_fix": "Use an OCR tool first or enable OCR in a future version.",
  "retryable": false
}
```

## Cancellation flow

- User clicks Cancel.
- JobController requests cancellation.
- Worker stops before next file.
- If an external process is running, it is terminated after grace period.
- Temp output is deleted or marked `.cancelled`.
- Source file remains unchanged.
- Queue marks current file cancelled and pending files unchanged.

## Reporting flow

For every run:

```text
run_id/
  conversion-report.json
  conversion-report.md
  logs/
    app.log
  outputs/
    converted files
```

Report should include:

- App version.
- OS.
- Engine versions.
- Source file names.
- Output file names.
- Status per item.
- Warnings/errors.
- Runtime duration.
- Settings profile.

## Data persistence

V1 should persist only:

- User settings.
- Recent output folders.
- Optional recent project/session files.
- App logs.

It should not persist document content.

## Future architecture extension points

- OCR plugin.
- AI cleanup plugin.
- RAG export plugin.
- Watch folder automation.
- CLI binary.
- Split stitched Markdown back into source files.
- Cloud sync integration.
- Conversion quality scoring.


---

# CODING_PIPELINE_CODING_PROGRESS.md

## Purpose

This file tracks the phased engineering build plan for the Document-to-Markdown Converter + MD Stitcher GUI application. Each phase includes objectives, files to create or modify, acceptance criteria, and estimated complexity.

## Complexity scale

| Score | Meaning |
|---:|---|
| 1 | Tiny task |
| 3 | Small implementation |
| 5 | Moderate feature |
| 7 | Hard feature with integration risk |
| 9 | High-risk subsystem |
| 10 | Research-heavy or release-blocking |

## Phase 0: Repository foundation

### Objectives

- Create repository structure.
- Add Python project configuration.
- Add documentation files.
- Add test/lint baseline.
- Add changelog discipline.

### Files to create/modify

- `pyproject.toml`
- `README.md`
- `.gitignore`
- `.editorconfig`
- `docs/SPECS_TECHSTACK.md`
- `docs/WORKFLOWS_ARCHITECTURE.md`
- `docs/CODING_PIPELINE_CODING_PROGRESS.md`
- `docs/Agent.md`
- `docs/GEMINI.md`
- `docs/PLAN.md`
- `docs/TODO.md`
- `docs/ALL-FILES-CHANGELOG.md`
- `app/__init__.py`
- `tests/__init__.py`

### Acceptance criteria

- `python -m pytest` runs successfully with placeholder tests.
- `ruff check .` runs.
- Project imports without GUI launch.
- Documentation files exist.
- Changelog has initial entry.

### Estimated complexity

**3 / 10**

## Phase 1: Core domain models and settings

### Objectives

- Define data models for files, jobs, conversion plans, results, warnings, and errors.
- Implement settings loader/saver.
- Implement platform-aware app directories.
- Implement logging configuration.

### Files to create/modify

- `app/core/models.py`
- `app/core/settings.py`
- `app/core/paths.py`
- `app/core/logging_config.py`
- `tests/unit/test_models.py`
- `tests/unit/test_settings.py`

### Acceptance criteria

- Models validate required fields.
- Settings load defaults if no config exists.
- Settings save to correct platform config path.
- Logs avoid document body content.
- Unit tests pass.

### Estimated complexity

**4 / 10**

## Phase 2: File detection and queue preflight

### Objectives

- Detect supported file types.
- Validate paths, permissions, extensions, and likely MIME/magic.
- Generate preflight warnings.
- Create conversion plans without converting yet.

### Files to create/modify

- `app/core/file_detection.py`
- `app/conversion/router.py`
- `app/conversion/base.py`
- `tests/unit/test_file_detection.py`
- `tests/unit/test_router.py`

### Acceptance criteria

- `.doc`, `.docx`, `.pdf`, `.odt`, `.odf` recognized.
- Unsupported files rejected with useful error.
- Mislabeled files produce warnings.
- Missing external dependencies produce preflight warnings.
- No source file is modified.

### Estimated complexity

**5 / 10**

## Phase 3: MD Stitcher service

### Objectives

- Implement standalone stitching service.
- Preserve file order.
- Insert exact separator format.
- Handle encoding and newline normalization.
- Write atomically.

### Files to create/modify

- `app/stitcher/separator.py`
- `app/stitcher/manifest.py`
- `app/stitcher/stitcher_service.py`
- `tests/unit/test_separator.py`
- `tests/unit/test_stitcher_service.py`
- `tests/fixtures/markdown/`

### Acceptance criteria

- Three-file stitch produces exact expected separator sequence.
- No trailing separator by default.
- Source files remain unchanged.
- Missing file produces structured error.
- Output file cannot overwrite an input file.
- Duplicate basenames warn but do not fail.
- Encoding errors are reported.

### Estimated complexity

**5 / 10**

## Phase 4: Pandoc engine

### Objectives

- Implement Pandoc availability detection.
- Convert `.docx` and `.odt` to `.md`.
- Capture stderr, exit codes, and durations.
- Normalize output.

### Files to create/modify

- `app/conversion/pandoc_engine.py`
- `app/conversion/markdown_normalizer.py`
- `app/conversion/reports.py`
- `tests/integration/test_pandoc_engine.py`

### Acceptance criteria

- Engine returns unavailable if Pandoc missing.
- `.docx` fixture converts to Markdown.
- `.odt` fixture converts to Markdown.
- Engine failure returns structured error.
- Output is UTF-8 and LF-normalized.

### Estimated complexity

**6 / 10**

## Phase 5: Mammoth engine

### Objectives

- Implement `.docx` to semantic HTML conversion.
- Convert HTML to Markdown.
- Add style-map hooks for headings.
- Compare Mammoth output with Pandoc output.

### Files to create/modify

- `app/conversion/mammoth_engine.py`
- `app/conversion/html_to_markdown.py`
- `tests/integration/test_mammoth_engine.py`

### Acceptance criteria

- Simple `.docx` converts cleanly.
- Heading/list/link fixture passes.
- Embedded unsupported content creates warning.
- Output does not include full HTML wrapper unless intended.

### Estimated complexity

**5 / 10**

## Phase 6: LibreOffice engine

### Objectives

- Detect LibreOffice/soffice.
- Implement `.doc` pre-conversion route.
- Support fallback conversion to HTML/text.
- Use isolated temp profile where possible.
- Add process timeout and cleanup.

### Files to create/modify

- `app/conversion/libreoffice_engine.py`
- `app/core/process.py`
- `tests/integration/test_libreoffice_engine.py`

### Acceptance criteria

- Missing LibreOffice produces actionable error.
- `.doc` fixture converts through intermediate route.
- Timeout kills process tree.
- Temp profile is cleaned.
- Output path is detected even if LibreOffice changes filename capitalization.

### Estimated complexity

**8 / 10**

## Phase 7: PDF engines

### Objectives

- Implement PyMuPDF extraction.
- Implement pdfminer.six fallback.
- Detect likely scanned/image-only PDFs.
- Produce warnings for low-confidence extraction.

### Files to create/modify

- `app/conversion/pdf_pymupdf_engine.py`
- `app/conversion/pdf_pdfminer_engine.py`
- `tests/integration/test_pdf_engines.py`
- `tests/fixtures/pdf/`

### Acceptance criteria

- Text PDF converts to Markdown.
- Empty/scanned PDF creates warning.
- Password-protected PDF creates structured error.
- Multi-page PDF preserves page order.
- Engine reports character count and page count.

### Estimated complexity

**7 / 10**

## Phase 8: GUI shell

### Objectives

- Build PySide6 main window.
- Add Converter and MD Stitcher tabs.
- Add menu bar and app actions.
- Implement drag/drop shell.

### Files to create/modify

- `app/main.py`
- `app/ui/main_window.py`
- `app/ui/converter_tab.py`
- `app/ui/stitcher_tab.py`
- `app/ui/widgets/file_queue_table.py`
- `app/ui/widgets/drag_drop_list.py`
- `app/ui/widgets/warning_panel.py`
- `app/resources/styles/app.qss`

### Acceptance criteria

- App launches.
- User can add/remove files in Converter.
- User can add/reorder/remove Markdown files in Stitcher.
- UI remains responsive during placeholder jobs.
- Basic accessibility labels exist.

### Estimated complexity

**7 / 10**

## Phase 9: Worker integration

### Objectives

- Connect GUI to conversion services.
- Implement background workers.
- Display progress and status.
- Support cancel/retry.

### Files to create/modify

- `app/workers/conversion_worker.py`
- `app/workers/stitch_worker.py`
- `app/ui/converter_tab.py`
- `app/ui/stitcher_tab.py`
- `app/core/job_controller.py`

### Acceptance criteria

- Batch conversion runs without blocking UI.
- Stitching runs without blocking UI.
- Cancel stops before next job.
- Retry works for failed jobs.
- UI status matches result objects.

### Estimated complexity

**8 / 10**

## Phase 10: Reports and diagnostics

### Objectives

- Implement JSON and Markdown reports.
- Show run summary.
- Add copy diagnostics.
- Add privacy-safe logs.

### Files to create/modify

- `app/conversion/reports.py`
- `app/core/diagnostics.py`
- `app/ui/run_summary_dialog.py`
- `tests/unit/test_reports.py`

### Acceptance criteria

- Report generated for each run.
- Failed jobs include technical detail.
- Report does not include document body content.
- User can open output folder.

### Estimated complexity

**5 / 10**

## Phase 11: Packaging Windows alpha

### Objectives

- Build Windows `.exe`.
- Include icons and resources.
- Detect external dependencies.
- Create installer or portable package.

### Files to create/modify

- `scripts/build_windows.ps1`
- `packaging/windows/`
- `app/resources/icons/`
- `README.md`

### Acceptance criteria

- App runs on clean Windows 11 test machine.
- Missing Pandoc/LibreOffice warnings work.
- Conversion works when dependencies installed.
- No console window appears in GUI release build unless debug mode.

### Estimated complexity

**7 / 10**

## Phase 12: Linux beta

### Objectives

- Validate Linux runtime.
- Package AppImage or deb.
- Test drag/drop and file permissions.
- Document dependency installation.

### Files to create/modify

- `scripts/build_linux.sh`
- `packaging/linux/`
- `README.md`
- `docs/linux-install.md`

### Acceptance criteria

- App launches on target distro.
- Pandoc/LibreOffice detection works.
- File dialogs and drag/drop work.
- Markdown stitcher works identically to Windows.

### Estimated complexity

**7 / 10**

## Phase 13: macOS collaborative track

### Objectives

- Start Q4 2026/Q1 2027 macOS effort.
- Validate PySide6 app bundle.
- Handle signing/notarization path.
- Test Apple Silicon.

### Files to create/modify

- `scripts/build_macos.sh`
- `packaging/macos/`
- `docs/macos-release.md`
- CI macOS workflow

### Acceptance criteria

- App launches as `.app`.
- DMG generated.
- Signed/notarized release path documented.
- Dependency strategy chosen.

### Estimated complexity

**8 / 10**

## Current progress snapshot

| Phase | Status | Notes |
|---|---|---|
| 0 | Ready to start | Documentation foundation generated. |
| 1 | Not started | Models/settings next. |
| 2 | Not started | Required before engines. |
| 3 | Not started | Good early win. |
| 4 | Not started | Needs Pandoc install. |
| 5 | Not started | Optional but useful for DOCX quality. |
| 6 | Not started | High-risk legacy support. |
| 7 | Not started | Needs fixture corpus. |
| 8 | Not started | UI after service skeleton. |
| 9 | Not started | Depends on UI and services. |
| 10 | Not started | Can begin after first engines. |
| 11 | Not started | Windows alpha target. |
| 12 | Not started | Linux beta target. |
| 13 | Future | Q4 2026/Q1 2027. |


---

# Agent.md

## Purpose

This file gives instructions to any AI coding agent assisting the Document-to-Markdown Converter + MD Stitcher GUI project.

## Agent mission

Help build a reliable, local-first desktop application that converts documents to Markdown and stitches Markdown files into one ordered output file. Prioritize correctness, safety, maintainability, and honest error handling over flashy features.

## Behavioral rules

1. **Do not guess file behavior.** If a format, engine, or OS-specific behavior is uncertain, create a small test or mark the uncertainty clearly.
2. **Never modify source documents.** All conversion work must happen in temp directories and output paths.
3. **Do not hide failures.** Every failed conversion must return a structured error.
4. **Do not silently drop user content.** If content may be lost, create a warning.
5. **Prefer small commits.** Each change should have a clear scope.
6. **Update tests when behavior changes.**
7. **Update `ALL-FILES-CHANGELOG.md` for every meaningful file change.**
8. **Keep GUI and core logic separate.**
9. **Do not add cloud calls, telemetry, or AI APIs unless explicitly approved.**
10. **Do not execute document macros.**

## Autonomy rules

## The agent may do autonomously

- Create missing project folders.
- Add tests for documented behavior.
- Refactor internal code without changing public behavior.
- Add type hints.
- Improve error messages.
- Add dependency detection.
- Add safe logging.
- Add fixtures that contain no private data.
- Update documentation to reflect implemented behavior.
- Run tests and lint commands.

## The agent must not do autonomously

- Delete major files.
- Change required stitcher separator format.
- Add network/cloud processing.
- Add telemetry.
- Change license.
- Add paid third-party services.
- Bundle large binaries without approval.
- Commit private user documents as fixtures.
- Replace the chosen GUI framework.
- Change scope from desktop app to web app.
- Disable safety checks to make tests pass.

## Ambiguity handling

When requirements are ambiguous, follow this order:

1. Preserve source files.
2. Preserve user-visible content.
3. Preserve exact separator behavior.
4. Prefer local processing.
5. Prefer testable service-layer implementation.
6. Ask for clarification only if the ambiguity blocks safe progress.

If a single reasonable interpretation exists, proceed and document the assumption.

## Escalation protocol

Escalate when:

- A dependency license may conflict with distribution.
- A conversion route requires bundled external binaries.
- A feature would send files to a network service.
- A test fixture may contain private or copyrighted content.
- An implementation changes output semantics.
- A packaging choice affects signing/notarization.
- The separator format requirement conflicts with another request.

Escalation note format:

```text
ESCALATION REQUIRED
Area:
Decision needed:
Risk:
Recommended option:
Alternatives:
```

## Required engineering standards

### Code style

- Use Python type hints.
- Use small modules.
- Keep functions focused.
- Use descriptive names.
- Avoid global mutable state.
- Avoid `shell=True`.
- Avoid broad `except Exception` unless wrapping into structured error with diagnostics.

### Testing

Required test categories:

- Unit tests for separator generation.
- Unit tests for output path naming.
- Unit tests for file detection.
- Unit tests for settings load/save.
- Integration tests for engines when dependencies exist.
- GUI smoke tests.
- Regression tests for known conversion edge cases.

### Logging

Logs may include:

- Engine name.
- File extension.
- Basename if privacy mode allows.
- Error codes.
- Duration.
- Dependency versions.

Logs must not include:

- Full document text.
- Secrets.
- Private file paths when privacy mode is enabled.
- Environment variables wholesale.

## Changelog discipline

Every meaningful change must append an entry to `ALL-FILES-CHANGELOG.md` using the required timestamp format.

Example:

```text
[2026-W21 | 2026-05-20 23:29 GMT+2] | app/stitcher/separator.py | ADD | Implemented required separator format for MD Stitcher.
```

Never delete changelog entries. If correcting, use strikethrough and append an update marker.

## Separator rule: do not break

The stitcher separator format is a hard requirement:

```text
===========================PREVIOUS FILE NAME.md=================================
```

Implementation must replace `PREVIOUS FILE NAME.md` with the actual previous file basename.

Do not add spaces.  
Do not localize it.  
Do not convert it into Markdown heading syntax.  
Do not change the number of `=` characters.

## Security baseline

- Treat every input file as untrusted.
- Run external tools with explicit argument lists.
- Use timeouts.
- Kill process trees on timeout.
- Use temp directories.
- Do not execute macros.
- Do not open converted output automatically unless user requested it.
- Do not follow symlinks in folder import without approval.
- Reject output path if it equals an input source path.

## Final instruction

Be boringly reliable. This app is a paper mill with guardrails, not a fireworks factory.


---

# GEMINI-ORCHESTRATION-ROLE_PLAN_TODO.md

## Purpose

This document defines Gemini's orchestration role for coordinating AI coding agents and implementation work on the Document-to-Markdown Converter + MD Stitcher GUI application.

## Gemini orchestration role

Gemini acts as the project conductor. It should break down work, assign tasks to suitable agents, review outputs, enforce scope, and keep documentation synchronized.

Gemini should not behave like a single mega-coder trying to do everything at once. It should operate like a systems architect with a clipboard, a laser pointer, and a refusal to let chaos wear a fake moustache.

## Primary responsibilities

- Maintain the project plan.
- Translate PRD requirements into implementation tickets.
- Keep build phases in order.
- Detect conflicts between requirements and code.
- Delegate implementation tasks.
- Review diffs for safety and correctness.
- Ensure tests exist before declaring a feature complete.
- Ensure changelog entries are appended.
- Escalate unclear product decisions.

## Delegation logic

### Architecture agent

Assign:

- Repository structure.
- Service boundaries.
- Core models.
- Engine interfaces.
- Error model.
- Settings architecture.

### Conversion agent

Assign:

- Pandoc engine.
- LibreOffice engine.
- Mammoth engine.
- PDF engines.
- Markdown normalizer.
- Conversion reports.

### GUI agent

Assign:

- PySide6 main window.
- Converter tab.
- Stitcher tab.
- Settings dialog.
- Progress UI.
- Drag/drop behavior.

### QA agent

Assign:

- Test fixtures.
- Unit tests.
- Integration tests.
- Edge-case matrix.
- Regression tests.
- Golden output comparison.

### Packaging agent

Assign:

- Windows packaging.
- Linux packaging.
- Future macOS packaging.
- Dependency detection scripts.
- Installer documentation.

### Documentation agent

Assign:

- README.
- User guide.
- Troubleshooting.
- Changelog enforcement.
- Developer setup docs.

## Current high-level plan

1. Create repository skeleton.
2. Implement models and settings.
3. Implement MD Stitcher service first because it is deterministic and high-value.
4. Implement file detection and conversion router.
5. Implement Pandoc and Mammoth conversion for `.docx`/`.odt`.
6. Implement LibreOffice route for `.doc`.
7. Implement PDF extraction engines.
8. Build GUI shell.
9. Connect workers and progress.
10. Add reports and diagnostics.
11. Package Windows alpha.
12. Validate Linux beta.
13. Prepare macOS collaborative release track.

## Current TODO list

## Priority 0: Foundation

- [ ] Create repository structure.
- [ ] Add `pyproject.toml`.
- [ ] Add `README.md`.
- [ ] Add docs folder and generated docs.
- [ ] Add initial test runner.
- [ ] Add `ALL-FILES-CHANGELOG.md` initial entry.

## Priority 1: Deterministic core

- [ ] Implement `separator.py`.
- [ ] Implement `stitcher_service.py`.
- [ ] Implement unit tests for exact separator behavior.
- [ ] Implement path safety checks.
- [ ] Implement atomic output writer.

## Priority 2: Conversion planning

- [ ] Implement file detection.
- [ ] Implement dependency detection for Pandoc and LibreOffice.
- [ ] Implement conversion plan model.
- [ ] Implement router.
- [ ] Add preflight warnings.

## Priority 3: Engines

- [ ] Implement Pandoc engine.
- [ ] Implement Mammoth engine.
- [ ] Implement LibreOffice engine.
- [ ] Implement PyMuPDF engine.
- [ ] Implement pdfminer.six engine.
- [ ] Implement Markdown normalizer.

## Priority 4: GUI

- [ ] Create PySide6 main window.
- [ ] Create Converter tab.
- [ ] Create MD Stitcher tab.
- [ ] Add drag/drop.
- [ ] Add queue table.
- [ ] Add run summary dialog.
- [ ] Add settings dialog.

## Priority 5: Release

- [ ] Build Windows portable package.
- [ ] Create Windows installer.
- [ ] Test on clean Windows 11.
- [ ] Build Linux package.
- [ ] Write user guide.
- [ ] Write troubleshooting guide.

## Review checklist for every agent output

- [ ] Does it preserve source files?
- [ ] Does it keep GUI and core logic separate?
- [ ] Does it return structured errors?
- [ ] Does it add/update tests?
- [ ] Does it update changelog?
- [ ] Does it avoid network calls?
- [ ] Does it avoid hidden destructive behavior?
- [ ] Does it preserve exact separator format?

## Conflict handling

If two agents produce conflicting implementations, Gemini must:

1. Compare against PRD.
2. Compare against `SPECS_TECHSTACK.md`.
3. Keep the safer implementation.
4. Preserve tests from both if useful.
5. Append changelog entry explaining the decision.
6. Escalate only if product behavior changes.

## Completion definition

A task is complete only when:

- Code is implemented.
- Tests pass.
- Docs are updated if behavior changed.
- Changelog is appended.
- No source-file mutation risk exists.
- Errors are structured and user-readable.


---

# GEMINI.md

## Persona

You are Gemini, the orchestration agent for the Document-to-Markdown Converter + MD Stitcher GUI project. You are a calm technical conductor: architectural, skeptical, precise, and allergic to vague “done” claims.

You coordinate implementation across agents and components. Your job is not just to generate code. Your job is to keep the project coherent.

## Project mission

Build a local-first desktop app that converts `.doc`, `.docx`, `.pdf`, `.odt`, and `.odf` documents into Markdown, then lets users stitch multiple Markdown files into one output with exact separator headers.

## Hard requirement

The MD Stitcher separator format must remain exactly:

```text
===========================PREVIOUS FILE NAME.md=================================
```

The implementation replaces `PREVIOUS FILE NAME.md` with the actual previous file basename. No extra spaces. No Markdown heading prefix. No decorative changes.

## Priority order

When instructions conflict, follow this order:

1. User’s explicit product requirements.
2. `ALL-FILES-CHANGELOG.md` standing rules.
3. `SPECS_TECHSTACK.md`.
4. `WORKFLOWS_ARCHITECTURE.md`.
5. `PLAN.md`.
6. `TODO.md`.
7. Existing code behavior and tests.
8. Agent suggestions.

## Capabilities

You may:

- Analyze the codebase.
- Create implementation plans.
- Delegate tasks.
- Review diffs.
- Write code when needed.
- Write tests.
- Update docs.
- Add changelog entries.
- Propose architecture improvements.
- Identify risks.

You may not:

- Add telemetry.
- Send user files to cloud services.
- Execute macros.
- Change separator format.
- Delete changelog history.
- Replace PySide6 without explicit approval.
- Make macOS release promises before packaging proof.
- Commit private documents as fixtures.
- Disable tests to pass CI.

## Project file interaction rules

Before editing:

1. Read the relevant file.
2. Check `ALL-FILES-CHANGELOG.md`.
3. Identify whether the change affects behavior, docs, tests, or packaging.

After editing:

1. Run or specify tests.
2. Update changelog.
3. Summarize what changed.
4. Note risks and follow-up tasks.

## Required output format for implementation tasks

When reporting work, use:

```text
Summary:
Files changed:
Tests:
Changelog:
Risks:
Next step:
```

## Ambiguity protocol

If a decision is ambiguous but safe progress is possible, proceed with the conservative option and document the assumption.

If ambiguity risks source file modification, data loss, cloud upload, license conflict, or separator behavior, stop and escalate.

Escalation format:

```text
ESCALATION REQUIRED
Decision:
Why it matters:
Recommended path:
Blocked tasks:
```

## Conversion engine rules

- Treat all documents as untrusted.
- Use subprocess calls with argument lists, not shell strings.
- Capture stdout/stderr.
- Use timeouts.
- Kill child processes on timeout.
- Write intermediate files into temp directories.
- Convert partial failures into structured errors.
- Do not mark success until output exists and is readable.

## PDF rules

- Do not promise perfect PDF conversion.
- Detect scanned/image-only PDFs when possible.
- Warn about multi-column or low-confidence extraction.
- Keep OCR out of default V1 unless explicitly added.

## GUI rules

- Keep UI responsive.
- Use workers for long-running tasks.
- UI should display human-readable errors and technical details behind disclosure.
- All primary actions must be keyboard reachable.
- Drag/drop must not bypass validation.

## Testing policy

Minimum required tests before feature completion:

- Unit tests for pure logic.
- Integration tests for engine wrappers when dependencies exist.
- GUI smoke tests for main windows.
- Golden output tests for stitcher behavior.

If an external dependency is missing in CI, tests should skip with a clear reason, not fail mysteriously.

## Changelog rules

Every meaningful update must append to `ALL-FILES-CHANGELOG.md` using:

```text
[YYYY-W## | YYYY-MM-DD HH:MM GMT+2] | FILE AFFECTED | TYPE: ADD/UPDATE/FIX/NOTE | Description
```

Never delete prior entries. Correct by strikethrough plus `### UPDATE`.

## Quality bar

A feature is not complete because code exists. It is complete when:

- It is tested.
- It fails safely.
- It reports clearly.
- It preserves source files.
- It is documented.
- It respects the architecture.


---

# PLAN.md

## Purpose

This is the master project plan for the Document-to-Markdown Converter + MD Stitcher GUI application.

## Planning horizon

The plan starts from the current foundation phase and aligns release maturity with Q4 2026 and Q1 2027 milestones, especially for the macOS collaborative effort.

## Project objectives

1. Build a reliable Windows 11-first local desktop GUI.
2. Keep Linux compatibility active from early development.
3. Keep macOS architecture-compatible but schedule polished macOS work for Q4 2026 to Q1 2027.
4. Convert `.doc`, `.docx`, `.pdf`, `.odt`, `.odf` to Markdown.
5. Provide a deterministic MD Stitcher with exact separator behavior.
6. Maintain safe, testable, documented implementation.

## Roles

| Role | Owner | Responsibility |
|---|---|---|
| Product Owner | Project lead | Defines scope, approves UX, prioritizes features. |
| Systems Architect | Engineering lead | Architecture, stack, dependency strategy. |
| Conversion Engineer | Developer/agent | Conversion engines and normalization. |
| GUI Engineer | Developer/agent | PySide6 interface and workers. |
| QA Engineer | Developer/agent | Fixtures, regression tests, edge cases. |
| Packaging Engineer | Developer/agent | Windows/Linux/macOS packaging. |
| Documentation Lead | Developer/agent | User/developer docs and changelog discipline. |
| Gemini Orchestrator | AI conductor | Delegation, review, conflict control. |

## Phase roadmap

## Phase A: Foundation and deterministic core

Target: May to June 2026

Deliverables:

- Repository skeleton.
- Documentation foundation.
- Models and settings.
- File detection.
- MD Stitcher service.
- Stitcher unit tests.

Exit criteria:

- Stitching works from service layer.
- Exact separator behavior is covered by tests.
- Source files remain untouched.
- Changelog process is active.

## Phase B: Conversion engine prototype

Target: June to July 2026

Deliverables:

- Pandoc engine.
- Mammoth engine.
- Markdown normalizer.
- Initial PDF extraction with PyMuPDF.
- Reports model.
- Engine availability detection.

Exit criteria:

- `.docx` converts through at least one route.
- `.odt` converts through Pandoc route.
- Text PDF converts with warnings where needed.
- Missing dependencies are reported clearly.

## Phase C: Legacy and fallback conversion

Target: July to August 2026

Deliverables:

- LibreOffice engine.
- `.doc` route.
- `.odf` guarded route.
- pdfminer.six fallback.
- Timeout and crash handling.
- Expanded test corpus.

Exit criteria:

- `.doc` conversion path works on Windows test machine with LibreOffice installed.
- Encrypted/corrupt files fail safely.
- PDF failures are user-readable.
- Conversion reports are useful.

## Phase D: Windows GUI MVP

Target: August to September 2026

Deliverables:

- PySide6 main window.
- Converter tab.
- MD Stitcher tab.
- Drag/drop.
- Queue table.
- Settings dialog.
- Background workers.

Exit criteria:

- User can convert files from GUI.
- User can stitch Markdown files from GUI.
- UI does not freeze during work.
- Cancel/retry flows work.
- Output folder actions work.

## Phase E: Windows alpha packaging

Target: September to October 2026

Deliverables:

- Windows portable build.
- Windows installer candidate.
- Dependency detection screen.
- User guide draft.
- Troubleshooting guide.

Exit criteria:

- Runs on clean Windows 11.
- Handles missing Pandoc/LibreOffice gracefully.
- Installer or portable package is testable.
- Basic regression test suite passes.

## Phase F: Linux beta

Target: Q4 2026

Deliverables:

- Linux package strategy.
- AppImage or deb proof.
- Linux dependency guide.
- Linux drag/drop validation.
- Cross-platform path fixes.

Exit criteria:

- Runs on at least one Ubuntu LTS target.
- Runs on one non-Ubuntu distro if feasible.
- Stitcher output identical to Windows.
- Conversion behavior documented per distro limitations.

## Phase G: Windows/Linux release candidate

Target: Q4 2026

Deliverables:

- V1 release candidate.
- Regression corpus.
- Signed Windows build if certificate available.
- Linux package candidate.
- Documentation complete.

Exit criteria:

- No known source-file mutation risk.
- All priority tests pass.
- Critical errors are structured.
- Changelog complete.

## Phase H: macOS collaborative track

Target: Q4 2026 to Q1 2027

Deliverables:

- macOS build investigation.
- `.app` bundle.
- DMG packaging.
- Apple Silicon validation.
- Signing and notarization plan.
- Dependency strategy: Homebrew-detected vs bundled.

Exit criteria:

- App launches on Apple Silicon.
- File dialogs and drag/drop work.
- Converter dependencies are detected.
- Notarized build path is documented or implemented.
- macOS limitations documented honestly.

## Milestone table

| Milestone | Target | Deliverable |
|---|---|---|
| M0 | 2026-05 | Project docs and foundation generated |
| M1 | 2026-06 | Core models + stitcher service |
| M2 | 2026-07 | Conversion prototype |
| M3 | 2026-08 | Legacy and PDF fallback routes |
| M4 | 2026-09 | Windows GUI MVP |
| M5 | 2026-10 | Windows alpha package |
| M6 | Q4 2026 | Linux beta and Windows/Linux RC |
| M7 | Q4 2026 | macOS collaboration starts |
| M8 | Q1 2027 | macOS signed/notarized release candidate if feasible |

## Scope control

Do not add these until V1 is stable:

- OCR.
- Cloud conversion.
- AI summarization.
- RAG database export.
- Real-time folder watcher.
- Markdown editor.
- Obsidian plugin.
- Browser extension.
- Mobile apps.

## Risk register

| Risk | Severity | Mitigation |
|---|---:|---|
| LibreOffice headless hangs | High | Timeouts, isolated profile, single concurrency. |
| PDF extraction quality varies | High | Warnings, fallback engines, no perfection promise. |
| Packaging size grows too large | Medium | Detect external tools instead of bundling initially. |
| macOS signing complexity | High | Schedule collaborative future track. |
| Duplicate filenames in stitcher | Medium | Warn and use basename exactly as required. |
| User expects OCR | Medium | Clear out-of-scope messaging. |
| Source files accidentally modified | Critical | Read-only design, tests, temp output, no in-place operations. |

## Definition of done

The project is release-ready when:

- Converter supports required formats with safe fallbacks.
- MD Stitcher separator behavior is exact and tested.
- GUI is responsive.
- Errors are structured.
- Reports exist.
- Windows package is tested.
- Linux package is validated.
- Docs are complete.
- Changelog allows contributor resume from last line.


---

# TODO.md

## Purpose

This is the immediate actionable task list for the Document-to-Markdown Converter + MD Stitcher GUI application.

## Priority 0: Start here

- [ ] Create repository root.
- [ ] Create `app/`, `tests/`, `docs/`, `scripts/`, and `packaging/` folders.
- [ ] Add all generated documentation files into `docs/`.
- [ ] Add `pyproject.toml`.
- [ ] Add `.gitignore`.
- [ ] Add `.editorconfig`.
- [ ] Add initial `README.md`.
- [ ] Add initial changelog entry in `ALL-FILES-CHANGELOG.md`.
- [ ] Run initial `pytest` placeholder.

## Priority 1: Core safety and models

- [ ] Create `app/core/models.py`.
- [ ] Define `FileStatus`.
- [ ] Define `ConversionWarning`.
- [ ] Define `ConversionError`.
- [ ] Define `ConversionPlan`.
- [ ] Define `ConversionResult`.
- [ ] Define `QueueItem`.
- [ ] Define `StitchManifest`.
- [ ] Add unit tests for model validation.
- [ ] Create `app/core/paths.py`.
- [ ] Add platform-specific config/cache/temp directories.
- [ ] Create `app/core/settings.py`.
- [ ] Add default settings.
- [ ] Add settings load/save tests.
- [ ] Create `app/core/logging_config.py`.
- [ ] Ensure logs do not capture document body text.

## Priority 2: MD Stitcher first implementation

- [ ] Create `app/stitcher/separator.py`.
- [ ] Add exact separator constants.
- [ ] Add separator generation tests.
- [ ] Create `app/stitcher/stitcher_service.py`.
- [ ] Implement ordered file read.
- [ ] Implement basename-only separator naming.
- [ ] Insert separator between files only.
- [ ] Normalize line endings to LF.
- [ ] Preserve source content.
- [ ] Write to temp output first.
- [ ] Prevent output path from matching an input path.
- [ ] Add duplicate basename warning.
- [ ] Add empty file handling.
- [ ] Add encoding error handling.
- [ ] Add golden output test.

## Priority 3: File detection and preflight

- [ ] Create `app/core/file_detection.py`.
- [ ] Detect `.doc`.
- [ ] Detect `.docx`.
- [ ] Detect `.pdf`.
- [ ] Detect `.odt`.
- [ ] Detect `.odf`.
- [ ] Reject unsupported files.
- [ ] Warn on mismatched extension/header.
- [ ] Detect cloud placeholder/unavailable file where possible.
- [ ] Detect read permission issues.
- [ ] Detect output directory write permission.
- [ ] Add unit tests.

## Priority 4: Engine availability

- [ ] Create `app/conversion/base.py`.
- [ ] Define `ConversionEngine` interface.
- [ ] Create `app/conversion/router.py`.
- [ ] Add engine availability model.
- [ ] Detect Pandoc.
- [ ] Detect LibreOffice/soffice.
- [ ] Detect Python package engines.
- [ ] Add settings overrides for binary paths.
- [ ] Add preflight dependency warnings.

## Priority 5: Markdown normalizer

- [ ] Create `app/conversion/markdown_normalizer.py`.
- [ ] Normalize LF line endings.
- [ ] Ensure final newline.
- [ ] Avoid modifying fenced code blocks.
- [ ] Convert HTML fragments to Markdown.
- [ ] Add image path rewrite helpers.
- [ ] Add table fallback warnings.
- [ ] Add unit tests.

## Priority 6: Pandoc conversion

- [ ] Create `app/conversion/pandoc_engine.py`.
- [ ] Implement `.docx` conversion.
- [ ] Implement `.odt` conversion.
- [ ] Implement HTML intermediate conversion.
- [ ] Capture stderr.
- [ ] Handle non-zero exit codes.
- [ ] Add timeout.
- [ ] Add integration tests skipped if Pandoc unavailable.

## Priority 7: Mammoth conversion

- [ ] Create `app/conversion/mammoth_engine.py`.
- [ ] Convert `.docx` to HTML.
- [ ] Convert HTML to Markdown.
- [ ] Add style map option.
- [ ] Warn on unsupported embedded content.
- [ ] Add tests.

## Priority 8: LibreOffice conversion

- [ ] Create `app/conversion/libreoffice_engine.py`.
- [ ] Detect `soffice`.
- [ ] Convert `.doc` to `.docx`.
- [ ] Convert fallback to HTML.
- [ ] Convert `.odf` cautiously.
- [ ] Use isolated temp profile.
- [ ] Add process timeout.
- [ ] Kill process tree on timeout.
- [ ] Clean temp profile.
- [ ] Add integration tests skipped if LibreOffice unavailable.

## Priority 9: PDF conversion

- [ ] Create `app/conversion/pdf_pymupdf_engine.py`.
- [ ] Extract text by pages.
- [ ] Detect image-heavy pages.
- [ ] Warn if no text layer.
- [ ] Create `app/conversion/pdf_pdfminer_engine.py`.
- [ ] Add fallback extraction.
- [ ] Add password-protected PDF handling.
- [ ] Add tests with safe fixtures.

## Priority 10: Reports

- [ ] Create `app/conversion/reports.py`.
- [ ] Generate JSON report.
- [ ] Generate Markdown report.
- [ ] Include engine versions.
- [ ] Include warnings/errors.
- [ ] Avoid document body text.
- [ ] Add tests.

## Priority 11: GUI shell

- [ ] Create `app/main.py`.
- [ ] Create `app/ui/main_window.py`.
- [ ] Add menu bar.
- [ ] Add Converter tab.
- [ ] Add MD Stitcher tab.
- [ ] Add Settings dialog.
- [ ] Add status bar.
- [ ] Add icons later.
- [ ] Add app stylesheet.

## Priority 12: Converter GUI

- [ ] Add file queue table.
- [ ] Add Add Files action.
- [ ] Add Add Folder action.
- [ ] Add Remove action.
- [ ] Add Clear action.
- [ ] Add output folder selector.
- [ ] Add Convert button.
- [ ] Add progress bar.
- [ ] Add warning/error panel.
- [ ] Connect to preflight scan.

## Priority 13: MD Stitcher GUI

- [ ] Add archive-style Markdown tray.
- [ ] Add drag/drop.
- [ ] Add reorder controls.
- [ ] Add remove/clear.
- [ ] Add output file selector.
- [ ] Add separator preview.
- [ ] Add duplicate warning display.
- [ ] Connect to StitcherService.
- [ ] Add completion summary.

## Priority 14: Workers

- [ ] Create `app/workers/conversion_worker.py`.
- [ ] Create `app/workers/stitch_worker.py`.
- [ ] Ensure UI stays responsive.
- [ ] Add cancel behavior.
- [ ] Add retry failed behavior.
- [ ] Add worker tests where practical.

## Priority 15: Packaging

- [ ] Create `scripts/build_windows.ps1`.
- [ ] Create Windows PyInstaller spec.
- [ ] Test on clean Windows 11.
- [ ] Create `scripts/build_linux.sh`.
- [ ] Evaluate AppImage/deb.
- [ ] Document dependency installation.
- [ ] Plan macOS Q4 2026/Q1 2027 track.

## Priority 16: Documentation

- [ ] Write `README.md`.
- [ ] Write `docs/user-guide.md`.
- [ ] Write `docs/troubleshooting.md`.
- [ ] Write `docs/developer-setup.md`.
- [ ] Write `docs/conversion-quality.md`.
- [ ] Update all docs after implementation changes.

## Immediate next three tasks

1. Implement `separator.py` and tests.
2. Implement `stitcher_service.py` and golden output test.
3. Implement `models.py` and `settings.py`.

These are deterministic, safe, and create momentum before wrestling the PDF goblin.


---

# ALL-FILES-CHANGELOG.md

## Standing instructions

- Every entry uses **GMT+2 timestamp** + **ISO week number** in this format: `[YYYY-W## | YYYY-MM-DD HH:MM GMT+2]`.
- Entries are **append-only**. Never delete or replace unless absolutely unavoidable.
- When a prior entry needs correction, use `~~strikethrough~~` on the old text and append the correction below it with a `### UPDATE` marker.
- The purpose of this file is to allow any contributor to **resume from the last log line** without reading entire files from the beginning.
- Format: `[timestamp] | FILE AFFECTED | TYPE: (ADD/UPDATE/FIX/NOTE) | Description`.

## Entry types

- `ADD`: new file, new feature, new section, or new dependency.
- `UPDATE`: intentional change to existing content or behavior.
- `FIX`: correction to broken, unsafe, or incorrect behavior.
- `NOTE`: context, decision record, caveat, or known issue.

## Changelog

[2026-W21 | 2026-05-20 23:29 GMT+2] | PROJECT FOUNDATION | ADD | Created initial PRD, app naming candidates, cross-platform difficulty assessment, and documentation set: `SPECS_TECHSTACK.md`, `WORKFLOWS_ARCHITECTURE.md`, `CODING_PIPELINE_CODING_PROGRESS.md`, `Agent.md`, `GEMINI-ORCHESTRATION-ROLE_PLAN_TODO.md`, `GEMINI.md`, `PLAN.md`, `TODO.md`, and `ALL-FILES-CHANGELOG.md`.


---

# Research Source Notes

This project foundation was informed by the following public documentation and ecosystem references checked on 2026-05-20:

- Pandoc User Guide: https://pandoc.org/MANUAL.html
- LibreOffice command-line parameters help: https://help.libreoffice.org/latest/en-US/text/shared/guide/start_parameters.html
- pdfminer.six documentation: https://pdfminersix.readthedocs.io/
- PyMuPDF documentation: https://pymupdf.readthedocs.io/
- Qt for Python / PySide6 deployment documentation: https://doc.qt.io/qtforpython-6/deployment/index.html
- Tauri distribution documentation: https://v2.tauri.app/distribute/
- Electron code signing documentation: https://www.electronjs.org/docs/latest/tutorial/code-signing
- Microsoft MarkItDown repository: https://github.com/microsoft/markitdown

These are notes, not a dependency lock file. Pin exact versions during implementation.
