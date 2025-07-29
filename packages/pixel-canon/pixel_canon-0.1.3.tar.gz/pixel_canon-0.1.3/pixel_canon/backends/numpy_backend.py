"""
NumPy backend for converting image data arrays represented as np.ndarray.
"""
from typing import List
import numpy as np

from ..core import ImageLayout, ImageAxis, AxisDirection
from ..utils import are_layouts_memory_equivalent


def convert_numpy(data: np.ndarray, src: ImageLayout, dst: ImageLayout) -> np.ndarray:
    """
    Converts a NumPy array from a source to a destination ImageLayout.

    This function intelligently performs a series of transformations:
    1. Transposes axes to match the destination order.
    2. Flips axes to match the destination orientation.
    3. Reorders channels to match the destination format.

    It avoids unnecessary work by checking for memory layout equivalence first.

    Args:
        data: The input NumPy array.
        src: The ImageLayout describing the input `data`.
        dst: The target ImageLayout for the output.

    Returns:
        A new NumPy array conforming to the `dst` layout.
    
    Raises:
        ValueError: If the input data shape is incompatible with the source layout.
    """
    # Quick exit for fully identical layouts.
    if src == dst:
        return data.copy()
        
    if are_layouts_memory_equivalent(src, dst):
        # If memory layout is the same, we start with a copy and modify it.
        # This handles cases like changing only directions or channel order.
        converted_data = data.copy()
        current_layout = src
    else:
        # --- 1. Axis Transposition ---
        # This is the most significant change, affecting memory layout.
        src_axis_map = {axis: i for i, axis in enumerate(src.axis_order)}
        
        if not set(dst.axis_order).issubset(set(src.axis_order)):
             raise ValueError("Destination layout contains axes not present in source layout.")
        
        transpose_order = tuple(src_axis_map[axis] for axis in dst.axis_order)
        converted_data = np.transpose(data, axes=transpose_order)
        # After transpose, the data has a new layout, which is like dst but with src's other properties
        current_layout = ImageLayout(
            axis_order=dst.axis_order,
            memory_order=src.memory_order, # Transpose doesn't change C/F contiguity logic in this context
            channels=src.channels,
            directions=src.directions
        )

    # --- 2. Axis Flipping (Orientation) ---
    flip_axes: List[int] = []
    for i, axis in enumerate(current_layout.axis_order):
        src_dir = current_layout.directions.get(axis)
        dst_dir = dst.directions.get(axis)
        
        if src_dir and dst_dir and src_dir != dst_dir:
            # We only flip if the direction is explicitly different.
            if ( (src_dir == AxisDirection.UP and dst_dir == AxisDirection.DOWN) or
                 (src_dir == AxisDirection.DOWN and dst_dir == AxisDirection.UP) or
                 (src_dir == AxisDirection.LEFT and dst_dir == AxisDirection.RIGHT) or
                 (src_dir == AxisDirection.RIGHT and dst_dir == AxisDirection.LEFT) or
                 (src_dir == AxisDirection.FORWARD and dst_dir == AxisDirection.BACKWARD) or
                 (src_dir == AxisDirection.BACKWARD and dst_dir == AxisDirection.FORWARD) ):
                flip_axes.append(i)
    
    if flip_axes:
        converted_data = np.flip(converted_data, axis=tuple(flip_axes))

    # --- 3. Channel Reordering ---
    if current_layout.channels != dst.channels and ImageAxis.CHANNELS in dst.axis_order:
        try:
            channel_axis_index = dst.axis_order.index(ImageAxis.CHANNELS)
            src_channel_map = {char: i for i, char in enumerate(current_layout.channels)}
            
            # Check if all destination channels are present in the source
            if not all(c in src_channel_map for c in dst.channels):
                raise ValueError(f"Not all destination channels '{dst.channels}' are in source '{src.channels}'.")

            remap_indices = [src_channel_map[char] for char in dst.channels]
            converted_data = np.take(converted_data, remap_indices, axis=channel_axis_index)
        except (KeyError, ValueError) as e:
            raise ValueError(f"Cannot convert channels from '{src.channels}' to '{dst.channels}': {e}")

    return converted_data
