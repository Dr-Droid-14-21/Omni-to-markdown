from __future__ import annotations
from pathlib import Path

def build_separator(previous_filename: str) -> str:
    """
    Generates a byte-for-byte deterministic separator for MD Stitching.
    
    Args:
        previous_filename: The basename of the file that precedes this separator.
        
    Returns:
        A 60-character string of '=' with the filename centered/padded.
    """
    TOTAL_LENGTH = 60
    LEFT_PAD = 27
    
    line = "=" * LEFT_PAD
    line += previous_filename
    
    remaining = TOTAL_LENGTH - len(line)
    if remaining > 0:
        line += "=" * remaining
    
    # Strictly truncate or pad to exactly 60
    return line[:TOTAL_LENGTH]
