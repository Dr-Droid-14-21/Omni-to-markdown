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
