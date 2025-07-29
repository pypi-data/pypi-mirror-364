"""
Core components of the Pixel-Canon specification.

This module contains the fundamental building blocks for describing image layouts,
including Enums for axes and their properties, and the main ImageLayout dataclass.
"""
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Tuple, Dict, Final, Mapping
from types import MappingProxyType

class ImageAxis(Enum):
    """Represents a named, logical axis of the image data."""
    HEIGHT = auto()
    WIDTH = auto()
    CHANNELS = auto()
    DEPTH = auto()

class AxisDirection(Enum):
    """Represents the semantic direction of a spatial axis."""
    DOWN = auto()
    UP = auto()
    RIGHT = auto()
    LEFT = auto()
    FORWARD = auto()
    BACKWARD = auto()
    SYMMETRIC = auto()

class ChannelFormat:
    """
    Represents the semantic meaning and order of channels.
    Using a class with constants instead of an Enum for easy string representation.
    """
    RGB: Final[str] = "RGB"
    RGBA: Final[str] = "RGBA"
    BGR: Final[str] = "BGR"
    BGRA: Final[str] = "BGRA"
    LUMINANCE: Final[str] = "LUMINANCE" # Using a full word for clarity
    ALPHA: Final[str] = "ALPHA"

class MemoryOrder(Enum):
    """Defines how logical axes map to linear memory."""
    ROW_MAJOR = auto()    # C-style: last axis is fastest
    COLUMN_MAJOR = auto() # Fortran-style: first axis is fastest

@dataclass(frozen=True, eq=True)
class ImageLayout:
    """
    A complete, unambiguous description of an image's logical layout.
    
    This object is immutable and hashable, so it can be used as a dictionary key.
    The 'directions' dictionary is internally converted to a read-only MappingProxyType
    to ensure hashability.
    """
    axis_order: Tuple[ImageAxis, ...]
    memory_order: MemoryOrder
    channels: str # Using str type hint for compatibility with ChannelFormat constants
    
    # We use a mutable default for initialization, then make it immutable.
    # The type hint remains Mapping for external users.
    directions: Mapping[ImageAxis, AxisDirection] = field(hash=False)

    def __post_init__(self):
        """
        Ensure immutability for the directions dictionary after initialization.
        This is a standard pattern for making dataclasses with mutable collections
        truly immutable and hashable.
        """
        # The `frozen=True` dataclass will raise an error if we try to assign
        # to self.directions directly. We use object.__setattr__ to bypass this
        # check just for this setup phase.
        object.__setattr__(self, 'directions', MappingProxyType(dict(self.directions)))

    def __hash__(self):
        """
        Provide an explicit hash implementation that includes all fields.
        We must manually hash the frozendict-like 'directions'.
        """
        # We create a frozenset of the items for a hashable representation of the mapping.
        directions_hashable = frozenset(self.directions.items())
        return hash((
            self.axis_order,
            self.memory_order,
            self.channels,
            directions_hashable
        ))

