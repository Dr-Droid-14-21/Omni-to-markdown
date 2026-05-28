# Technical Concepts

## Separator Contract
- **Notation**: $S(f) = '='^{27} + f + '='^{60 - 27 - |f|}$
- **Definition**: A strictly defined string of 60 characters used to separate files in a stitched output, where $f$ is the basename of the previous file.
- **Boundary conditions**: Filename $|f|$ must not exceed a practical limit (typically 100+ chars) that would break the 60-char target; in practice, the implementation centers the name.
- **Related concepts**: MD Stitcher, Basename

## Engine Routing
- **Notation**: $R(e) \rightarrow \{E_1, E_2, \dots, E_n\}$
- **Definition**: The mapping of a file extension $e$ to an ordered set of conversion engines $\{E_n\}$, where $E_1$ is the preferred engine.
- **Boundary conditions**: Only applies to supported extensions; returns an empty set for unknown types.
- **Related concepts**: Fallback Route, Preflight Scan

## Normalization
- **Notation**: $N(m) \rightarrow m'$
- **Definition**: The process of cleaning raw engine output $m$ to ensure consistent line endings (LF), fenced code block integrity, and final newline presence.
- **Boundary conditions**: Must not alter the semantic content of the document.
- **Related concepts**: Markdown, Markdown Normalizer

## Preflight Scan
- **Notation**: $P(f, S) \rightarrow \{W, E\}$
- **Definition**: A static analysis of the input file $f$ and system settings $S$ before conversion, identifying missing dependencies, permission issues, or format mismatches.
- **Boundary conditions**: Does not perform actual conversion; relies on external binary detection.
- **Related concepts**: Engine Availability, Dependency Check

## Stitch Tray
- **Notation**: $T = \{f_1, f_2, \dots, f_n\}$
- **Definition**: A persistent archive (JSON) of file paths representing a reusable stitching queue.
- **Boundary conditions**: Paths must exist at load time; invalid paths are reported as warnings.
- **Related concepts**: MD Stitcher, Manifest
