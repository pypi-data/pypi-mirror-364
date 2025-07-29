"""
A collection of pre-defined, commonly used ImageLayouts for popular libraries.
"""
from .core import ImageLayout, ImageAxis, AxisDirection, MemoryOrder, ChannelFormat

class CommonLayouts:
    """
    A namespace for standard, pre-configured ImageLayout instances.
    These constants represent the default layouts used by major libraries.
    """
    # --- Typical for NumPy, OpenCV, Pillow, TensorFlow ---
    # Shape: (Height, Width, Channels), Memory: C-contiguous (Row-Major)
    HWC_ROW_MAJOR_RGB = ImageLayout(
        axis_order=(ImageAxis.HEIGHT, ImageAxis.WIDTH, ImageAxis.CHANNELS),
        memory_order=MemoryOrder.ROW_MAJOR,
        channels=ChannelFormat.RGB,
        directions={
            ImageAxis.HEIGHT: AxisDirection.DOWN,
            ImageAxis.WIDTH: AxisDirection.RIGHT,
        }
    )

    # --- Typical for PyTorch, TorchVision ---
    # Shape: (Channels, Height, Width), Memory: C-contiguous (Row-Major)
    CHW_ROW_MAJOR_RGB = ImageLayout(
        axis_order=(ImageAxis.CHANNELS, ImageAxis.HEIGHT, ImageAxis.WIDTH),
        memory_order=MemoryOrder.ROW_MAJOR,
        channels=ChannelFormat.RGB,
        directions={
            ImageAxis.HEIGHT: AxisDirection.DOWN,
            ImageAxis.WIDTH: AxisDirection.RIGHT,
        }
    )

    # --- Typical for OpenGL textures ---
    # Shape: (Height, Width, Channels), Y-axis is inverted
    HWC_ROW_MAJOR_RGBA_OPENGL = ImageLayout(
        axis_order=(ImageAxis.HEIGHT, ImageAxis.WIDTH, ImageAxis.CHANNELS),
        memory_order=MemoryOrder.ROW_MAJOR,
        channels=ChannelFormat.RGBA,
        directions={
            ImageAxis.HEIGHT: AxisDirection.UP, # Y=0 is at the bottom
            ImageAxis.WIDTH: AxisDirection.RIGHT,
        }
    )

    # --- Fortran / MATLAB equivalent of the NumPy layout ---
    # This layout is physically identical in memory to HWC_ROW_MAJOR_RGB
    CWH_COLUMN_MAJOR_RGB = ImageLayout(
        axis_order=(ImageAxis.CHANNELS, ImageAxis.WIDTH, ImageAxis.HEIGHT), # Reversed
        memory_order=MemoryOrder.COLUMN_MAJOR, # Different memory order
        channels=ChannelFormat.RGB,
        directions={
            ImageAxis.HEIGHT: AxisDirection.DOWN,
            ImageAxis.WIDTH: AxisDirection.RIGHT,
        }
    )
