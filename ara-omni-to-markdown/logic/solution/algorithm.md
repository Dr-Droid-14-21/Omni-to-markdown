# Algorithm Specifications

## Separator Generation

### Mathematical Formulation
Given a filename $f$, the separator string $S$ is defined as:
$$S = L + f + R$$
Where:
- $TotalLength = 60$
- $LeftPadding = 27$
- $L = '=' \times LeftPadding$
- $Remaining = TotalLength - LeftPadding - |f|$
- $R = '=' \times \max(0, Remaining)$

### Step-by-Step Explanation
1. Determine the basename of the source file (e.g., "chapter1.docx" becomes "chapter1.docx").
2. Prepend 27 equal signs (`=`).
3. Append the basename.
4. Calculate the remaining characters to reach a total length of 60.
5. Append equal signs until the length is exactly 60.
6. Ensure no trailing newline is added by the generator itself.

## Engine Selection (Priority Routing)

### Pseudocode
```python
def select_engine(extension, settings):
    options = get_options_for_extension(extension)
    for engine_name in options:
        engine = get_engine(engine_name)
        if engine.is_available():
            return engine
    return None
```

### Complexity Analysis
- **Time Complexity**: $O(N)$ where $N$ is the number of fallback engines defined for an extension (typically $N \leq 3$).
- **Space Complexity**: $O(1)$ constant overhead for routing decisions.

## Markdown Normalization

### Logic
1. **Line Endings**: Replace all `\r\n` (Windows) and `\r` (Mac) with `\n` (Unix).
2. **Fenced Blocks**: Identify code blocks starting with ` ``` ` and skip them during character-level transformations (like blank-line compaction).
3. **HTML Sanitization**: If the source was HTML (from Mammoth or LibreOffice), use `markdownify` with GFM flavor to ensure semantic correctness.
4. **Trailing Newline**: Ensure exactly one `\n` at the end of the file.
