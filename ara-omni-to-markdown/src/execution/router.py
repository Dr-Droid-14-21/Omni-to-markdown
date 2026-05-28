from __future__ import annotations
from pathlib import Path

def get_fallback_sequence(extension: str) -> list[str]:
    """
    Returns the ordered list of engines to try for a given extension.
    
    Args:
        extension: The file extension (including dot).
        
    Returns:
        List of engine identifiers.
    """
    sequences = {
        ".docx": ["pandoc", "mammoth", "libreoffice"],
        ".odt": ["pandoc", "libreoffice"],
        ".doc": ["libreoffice", "pandoc"],
        ".pdf": ["pymupdf", "pdfminer"],
        ".odf": ["libreoffice"]
    }
    return sequences.get(extension.lower(), [])
