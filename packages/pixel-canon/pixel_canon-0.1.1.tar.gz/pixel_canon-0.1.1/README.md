<div align="center">
  <a href="./README.md"><strong>English</strong></a> | <a href="./README.ru.md">Русский</a>
</div>
<hr>

# Pixel-Canon

> The canon for pixel data topology. A cross-language specification to define the logical layout of images (axis order, orientation, and memory order).

`Pixel-Canon` is a cross-language project aimed at solving a common and frustrating problem in computer vision, image processing, and machine learning: the ambiguity of image data layouts. When you receive an N-dimensional array, what do the axes mean? Is it `(Height, Width, Channels)` or `(Channels, Height, Width)`? Does the Y-axis point up or down? Are the data stored in C-style (row-major) or Fortran-style (column-major) order?

This project provides a simple, declarative specification and a set of tools to describe this information explicitly, eliminating guesswork and making data pipelines more robust and reliable.

## Core Concepts

The specification is built on a few core components:

*   **`ImageAxis`**: The name of an axis (e.g., `WIDTH`, `HEIGHT`, `CHANNELS`).
*   **`AxisDirection`**: The orientation of an axis (e.g., `UP`, `DOWN`, `LEFT`, `RIGHT`).
*   **`MemoryOrder`**: The physical layout in memory (`ROW_MAJOR` or `COLUMN_MAJOR`).
*   **`ChannelFormat`**: The semantic order of channels (`RGB`, `BGR`, `RGBA`).
*   **`ImageLayout`**: A composite object that combines all of the above to provide a complete, unambiguous description.

## The Specification

The formal specification, which all language-specific implementations must adhere to, can be found here:
*   **[Specification v1.0](./spec/v1.0.md)**

## Implementations

*   **[Python](./python/)** (In Progress)
*   *Other languages to be added.*

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
