# Pixel-Canon

**PyPI Homepage** | [**GitHub Repository**](https://github.com/GolonChenroppi/pixel-canon) | [**Specification**](https://github.com/GolonChenroppi/pixel-canon/blob/main/spec/v1.0.md)

---

> The canon for pixel data topology. A cross-language specification to define the logical layout of images (axis order, orientation, and memory order).

`Pixel-Canon` is a cross-language project aimed at solving a common and frustrating problem in computer vision, image processing, and machine learning: the ambiguity of image data layouts. When you receive an N-dimensional array, what do the axes mean? Is it `(Height, Width, Channels)` or `(Channels, Height, Width)`? Does the Y-axis point up or down?

This project provides a simple, declarative specification and a set of tools to describe this information explicitly, eliminating guesswork and making data pipelines more robust and reliable.

## Python Implementation

This package contains the Python implementation of the Pixel-Canon spec.

### Installation

```bash
pip install pixel-canon
```

To include support for `numpy` arrays:
```bash
pip install "pixel-canon[numpy]"
```

### Quick Example

```python
import numpy as np
from pixel_canon import CommonLayouts
from pixel_canon.backends.numpy_backend import convert_numpy

# Your image from a source like OpenCV
image_from_opencv = np.zeros((480, 640, 3), dtype=np.uint8)
layout_from_opencv = CommonLayouts.HWC_ROW_MAJOR_RGB

# The layout required by a library like PyTorch
layout_for_pytorch = CommonLayouts.CHW_ROW_MAJOR_RGB

# Convert the image layout safely and explicitly
prepared_image = convert_numpy(
    image_from_opencv,
    src=layout_from_opencv,
    dst=layout_for_pytorch
)

print(f"Original shape: {image_from_opencv.shape}")
print(f"Converted shape: {prepared_image.shape}")
# Original shape: (480, 640, 3)
# Converted shape: (3, 480, 640)
```

For full documentation, source code for other languages, and to contribute, please visit our main [**GitHub Repository**](https://github.com/GolonChenroppi/pixel-canon).
