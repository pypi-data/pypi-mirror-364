import unittest
import numpy as np
from pixel_canon.core import ImageLayout, ImageAxis, AxisDirection, MemoryOrder, ChannelFormat
from pixel_canon.common import CommonLayouts
from pixel_canon.backends.numpy_backend import convert_numpy

class TestNumpyBackend(unittest.TestCase):

    def setUp(self):
        """Create a sample HWC RGB image for testing."""
        self.h, self.w, self.c = 4, 6, 3
        # Create a predictable image:
        # R channel = height index
        # G channel = width index
        # B channel = constant 99
        self.img_hwc_rgb = np.zeros((self.h, self.w, self.c), dtype=np.uint8)
        self.img_hwc_rgb[..., 0] = np.arange(self.h).reshape(-1, 1)
        self.img_hwc_rgb[..., 1] = np.arange(self.w)
        self.img_hwc_rgb[..., 2] = 99
    
    def test_transpose_hwc_to_chw(self):
        """Test transposition from (H, W, C) to (C, H, W)."""
        src = CommonLayouts.HWC_ROW_MAJOR_RGB
        dst = CommonLayouts.CHW_ROW_MAJOR_RGB
        
        converted = convert_numpy(self.img_hwc_rgb, src, dst)
        
        self.assertEqual(converted.shape, (self.c, self.h, self.w))
        # Check if channels were transposed correctly
        # R channel (now at index 0) should match height indices
        self.assertTrue(np.array_equal(converted[0, :, :], self.img_hwc_rgb[:, :, 0]))
        # G channel (now at index 1) should match width indices
        self.assertTrue(np.array_equal(converted[1, :, :], self.img_hwc_rgb[:, :, 1]))
        
    def test_flip_vertical(self):
        """Test vertical flip (DOWN to UP)."""
        src = CommonLayouts.HWC_ROW_MAJOR_RGB # directions={H: DOWN, ...}
        dst_opengl = CommonLayouts.HWC_ROW_MAJOR_RGBA_OPENGL # directions={H: UP, ...}
        
        # Create a layout that only differs in direction
        dst_mod = ImageLayout(
            axis_order=src.axis_order, memory_order=src.memory_order,
            channels=src.channels, directions=dst_opengl.directions
        )
        
        converted = convert_numpy(self.img_hwc_rgb, src, dst_mod)
        
        self.assertEqual(converted.shape, self.img_hwc_rgb.shape)
        # The first row of the converted image should be the last row of the original
        self.assertTrue(np.array_equal(converted[0, :, :], self.img_hwc_rgb[-1, :, :]))
        # The last row of converted should be the first of original
        self.assertTrue(np.array_equal(converted[-1, :, :], self.img_hwc_rgb[0, :, :]))

    def test_reorder_channels_rgb_to_bgr(self):
        """Test channel reordering from RGB to BGR."""
        src = CommonLayouts.HWC_ROW_MAJOR_RGB
        dst = ImageLayout(
            axis_order=src.axis_order, memory_order=src.memory_order,
            channels=ChannelFormat.BGR, # The only change
            directions=src.directions
        )
        
        converted = convert_numpy(self.img_hwc_rgb, src, dst)
        
        self.assertEqual(converted.shape, self.img_hwc_rgb.shape)
        # Original R (index 0) is now at converted B (index 2)
        self.assertTrue(np.array_equal(converted[:, :, 2], self.img_hwc_rgb[:, :, 0]))
        # Original B (index 2) is now at converted R (index 0)
        self.assertTrue(np.array_equal(converted[:, :, 0], self.img_hwc_rgb[:, :, 2]))
        # Green channel should remain in the middle
        self.assertTrue(np.array_equal(converted[:, :, 1], self.img_hwc_rgb[:, :, 1]))

    def test_no_op_conversion(self):
        """Test conversion between identical layouts, should be a copy."""
        converted = convert_numpy(self.img_hwc_rgb, CommonLayouts.HWC_ROW_MAJOR_RGB, CommonLayouts.HWC_ROW_MAJOR_RGB)
        self.assertTrue(np.array_equal(converted, self.img_hwc_rgb))
        # Check that it's a copy, not the same object
        self.assertFalse(np.shares_memory(converted, self.img_hwc_rgb))

    def test_memory_equivalent_conversion(self):
        """Test conversion between memory-equivalent layouts (e.g., C vs Fortran)."""
        # This conversion should NOT trigger a transpose.
        src = CommonLayouts.HWC_ROW_MAJOR_RGB
        dst = CommonLayouts.CWH_COLUMN_MAJOR_RGB
        
        converted = convert_numpy(self.img_hwc_rgb, src, dst)
        # Since nothing else changes, it should just be a copy.
        self.assertTrue(np.array_equal(converted, self.img_hwc_rgb))
        
    def test_complex_conversion(self):
        """Test a conversion involving transpose, flip, and channel reorder."""
        # From NumPy-like (HWC_RGB, DOWN) to a custom layout (CHW_BGR, UP)
        src = CommonLayouts.HWC_ROW_MAJOR_RGB
        dst = ImageLayout(
            axis_order=(ImageAxis.CHANNELS, ImageAxis.HEIGHT, ImageAxis.WIDTH),
            memory_order=MemoryOrder.ROW_MAJOR,
            channels=ChannelFormat.BGR,
            directions={ImageAxis.HEIGHT: AxisDirection.UP, ImageAxis.WIDTH: AxisDirection.RIGHT}
        )

        converted = convert_numpy(self.img_hwc_rgb, src, dst)
        
        # 1. Check shape (transposed to CHW)
        self.assertEqual(converted.shape, (self.c, self.h, self.w))

        # 2. Check channels (reordered to BGR) and flip (UP)
        # Original R channel (value = height index) is now at converted channel 2
        # Original B channel (value = 99) is now at converted channel 0
        original_r_flipped = np.flipud(self.img_hwc_rgb[..., 0])
        original_g_flipped = np.flipud(self.img_hwc_rgb[..., 1])
        original_b_flipped = np.flipud(self.img_hwc_rgb[..., 2])
        
        self.assertTrue(np.array_equal(converted[0], original_b_flipped)) # B
        self.assertTrue(np.array_equal(converted[1], original_g_flipped)) # G
        self.assertTrue(np.array_equal(converted[2], original_r_flipped)) # R

        # 3. Check a specific value to be sure
        # Original image at (h-1, 0, R) has value h-1.
        # After conversion, it should be at (C=2, H=0, W=0)
        self.assertEqual(converted[2, 0, 0], self.h - 1)


if __name__ == '__main__':
    unittest.main()
