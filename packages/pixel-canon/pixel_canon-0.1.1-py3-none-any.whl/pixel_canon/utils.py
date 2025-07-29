"""
Utility functions for working with ImageLayout objects.
"""
from typing import List

from .core import ImageLayout, ImageAxis, MemoryOrder


def get_speed_order(layout: ImageLayout) -> List[ImageAxis]:
    """
    Calculates the order of axes from fastest to slowest based on memory layout.

    For ROW_MAJOR, the last axis in axis_order is fastest.
    For COLUMN_MAJOR, the first axis in axis_order is fastest.

    Args:
        layout: The ImageLayout to analyze.

    Returns:
        A list of ImageAxis enums, ordered from fastest-changing to slowest-changing.
    """
    if layout.memory_order == MemoryOrder.ROW_MAJOR:
        # The last axis is the fastest, so we reverse the list.
        return list(reversed(layout.axis_order))
    elif layout.memory_order == MemoryOrder.COLUMN_MAJOR:
        # The first axis is the fastest, so the order is as is.
        return list(layout.axis_order)
    # This line should be unreachable if all MemoryOrder cases are handled.
    raise ValueError(f"Unknown memory order: {layout.memory_order}")


def are_layouts_memory_equivalent(layout1: ImageLayout, layout2: ImageLayout) -> bool:
    """
    Checks if two layouts describe the exact same physical memory arrangement.

    Two layouts are memory-equivalent if their axes, when ordered from fastest
    to slowest, are identical. The semantic information (directions, channel names)
    does not affect physical memory layout and is ignored.

    Example:
        A (H, W, C) ROW_MAJOR layout is memory-equivalent to a
        (C, W, H) COLUMN_MAJOR layout.

    Args:
        layout1: The first ImageLayout.
        layout2: The second ImageLayout.

    Returns:
        True if the layouts are physically identical in memory, False otherwise.
    """
    if layout1 == layout2:
        return True

    # The number of axes must be the same.
    if len(layout1.axis_order) != len(layout2.axis_order):
        return False
        
    # The set of axes must be the same.
    if set(layout1.axis_order) != set(layout2.axis_order):
        return False

    # The order of axes from fastest to slowest must be identical.
    speed_order1 = get_speed_order(layout1)
    speed_order2 = get_speed_order(layout2)

    return speed_order1 == speed_order2

