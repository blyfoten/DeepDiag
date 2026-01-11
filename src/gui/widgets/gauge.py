"""
Gauge widget for dashboard.
TODO: Implement in Phase 6
"""

import dearpygui.dearpygui as dpg


class Gauge:
    """Circular gauge widget."""

    def __init__(self, label: str, min_val: float, max_val: float, unit: str = ""):
        """Initialize gauge."""
        self.label = label
        self.min_val = min_val
        self.max_val = max_val
        self.unit = unit
        # TODO: Implementation

    def update(self, value: float):
        """Update gauge value."""
        pass
