from __future__ import annotations

from PySide6.QtCore import QRectF
from PySide6.QtGui import QPainterPath


def create_stepped_bevel_path(rect: QRectF, cut: float) -> QPainterPath:
    """
    Creates a 'two-part' cut corner (stepped bevel) for futuristic sci-fi panels.
    Instead of a single diagonal chamfer, the corner has a double notch.
    """
    path = QPainterPath()
    step = cut * 0.45  # Slightly less than half to make the angle pop

    # Start at top-left, moving right
    path.moveTo(rect.left() + cut, rect.top())
    
    # Top edge
    path.lineTo(rect.right() - cut, rect.top())
    
    # Top-Right corner (stepped)
    path.lineTo(rect.right() - step, rect.top())
    path.lineTo(rect.right(), rect.top() + step)
    path.lineTo(rect.right(), rect.top() + cut)
    
    # Right edge
    path.lineTo(rect.right(), rect.bottom() - cut)
    
    # Bottom-Right corner (stepped)
    path.lineTo(rect.right(), rect.bottom() - step)
    path.lineTo(rect.right() - step, rect.bottom())
    path.lineTo(rect.right() - cut, rect.bottom())
    
    # Bottom edge
    path.lineTo(rect.left() + cut, rect.bottom())
    
    # Bottom-Left corner (stepped)
    path.lineTo(rect.left() + step, rect.bottom())
    path.lineTo(rect.left(), rect.bottom() - step)
    path.lineTo(rect.left(), rect.bottom() - cut)
    
    # Left edge
    path.lineTo(rect.left(), rect.top() + cut)
    
    # Top-Left corner (stepped)
    path.lineTo(rect.left(), rect.top() + step)
    path.lineTo(rect.left() + step, rect.top())
    
    path.closeSubpath()
    return path
