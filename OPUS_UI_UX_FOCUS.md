# OPUS_UI_UX_FOCUS.md

## Purpose

This file is the focused handoff brief for Claude Opus 4.7 UI/UX review work.
Use it with Hermes skill: `ui-ux-pro-max`.

## Project context

- App: **Omni to Markdown** (Windows 11 desktop app, PySide6).
- Two core workflows:
  - **Converter**: convert `.doc`, `.docx`, `.pdf`, `.odt`, `.odf` to Markdown.
  - **MD Stitcher**: combine multiple Markdown files into one output in exact order.
- Current status: backend + worker threading are solid; UI is functional and needs polish to reach MVP quality.

## Plain-language definitions

### What "converter usability" means

How easy it is for a normal user to:

1. add files/folders,
2. understand preflight warnings (missing tools, bad files),
3. choose output folder,
4. run/cancel/retry conversion,
5. understand final result without confusion.

### What "stitcher usability" means

How easy it is for a normal user to:

1. add/reorder Markdown files,
2. avoid mistakes (duplicates, missing files, wrong output path),
3. save/reload a stitch setup ("tray") and continue later,
4. run/cancel stitching and trust the result.

## Required skill mode

When Opus works on this project, explicitly apply:

- Hermes skill: `ui-ux-pro-max`
- Target: practical Windows desktop UX improvements (not generic web design advice)

## The 3 main things needed from Opus

1. **Prioritized UX audit**
   - List top usability problems by severity (`P0/P1/P2`) for Converter and Stitcher tabs.
   - Focus on friction, confusion points, and error-prone interactions.

2. **Concrete redesign guidance**
   - Give direct recommendations for:
     - control grouping,
     - button hierarchy (primary vs secondary),
     - label/copy rewrites,
     - warning/error phrasing,
     - progress/status communication.
   - Keep suggestions implementable in PySide6 with current architecture.

3. **Actionable implementation backlog**
   - Convert UX findings into a short engineering backlog:
     - item title,
     - exact UI file(s),
     - expected behavior,
     - acceptance criteria,
     - test/validation note.

## Specific areas Opus should take care of

- Converter:
  - Preflight clarity (what is blocking vs warning only).
  - Cancel/retry trust signals.
  - Better run-summary readability.
- Stitcher:
  - Tray workflow quality (save/load mental model, replacement confirmation, missing-file handling).
  - Reorder/disambiguation clarity when duplicate basenames appear.
  - Stronger status feedback before/during/after stitch.
- Global:
  - Consistent wording, spacing rhythm, and button intent across both tabs.
  - Windows-native interaction expectations (dialogs, confirmations, status language).

## Output format expected from Opus

Please return:

1. A short UX diagnosis summary.
2. A prioritized issue list (`P0/P1/P2`).
3. A concrete patch plan mapped to repository files.
4. Suggested microcopy replacements (old text -> new text).
5. MVP acceptance checklist for UX sign-off.
