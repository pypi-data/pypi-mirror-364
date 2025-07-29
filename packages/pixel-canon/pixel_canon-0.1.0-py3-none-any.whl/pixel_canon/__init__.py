"""
Pixel-Canon: A universal specification for describing image memory layouts.
"""
from .core import (
    ImageAxis,
    AxisDirection,
    ChannelFormat,
    MemoryOrder,
    ImageLayout
)
from .common import CommonLayouts
from .utils import are_layouts_memory_equivalent, get_speed_order


__version__ = "0.1.0"

__all__ = [
    "ImageAxis",
    "AxisDirection",
    "ChannelFormat",
    "MemoryOrder",
    "ImageLayout",
    "CommonLayouts",
    "are_layouts_memory_equivalent",
    "get_speed_order",
    "__version__",
]

